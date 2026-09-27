"""Offline tests for the needs_attention inbox tooling.

Coordination/engineering only. A green run here is not research evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import needs_attention_check as nac  # noqa: E402
import needs_attention_scan as nas  # noqa: E402

NOW = datetime(2026, 9, 27, 19, 0, 0, tzinfo=timezone.utc)


def _card(**over: object) -> dict:
    card = {
        "schema": "needs_attention/v1",
        "id": "NA-0042",
        "title": "example",
        "status": "OPEN",
        "opened_at": "2026-09-27T18:00:00Z",
        "opened_by": {"provider": "cursor"},
        "repo": "d6g8k5htny-coder/trial",
        "refs": {"pr": 1},
        "blocker": "stuck",
        "ask": "help",
        "scientific_effect": "NONE",
    }
    card.update(over)
    return card


def test_inbox_layout_and_readme() -> None:
    base = ROOT / "needs_attention"
    assert (base / "README.md").is_file()
    text = (base / "README.md").read_text(encoding="utf-8")
    assert "Scientific effect: NONE" in text
    assert "needs_attention_check.py" in text
    assert "needs_attention_scan.py" in text
    assert (base / "cards").is_dir()
    assert (base / "resolved").is_dir()


def test_committed_cards_validate() -> None:
    code, problems, report = nac.check_tree(ROOT)
    assert code == 0, problems
    assert report["scientific_effect"] == "NONE"
    assert all(c["errors"] == [] for c in report["cards"])


def test_validator_rejects_bad_cards() -> None:
    ok = nac.validate_card(_card(), resolved_dir=False, filename="NA-0042-example.json")
    assert ok == []
    bad_status = nac.validate_card(_card(status="DONE"), resolved_dir=False, filename="NA-0042-x.json")
    assert any("bad status" in e for e in bad_status)
    closed_in_cards = nac.validate_card(
        _card(status="RESOLVED", resolution="fixed", resolved_at="2026-09-27T18:30:00Z", resolved_by="x"),
        resolved_dir=False,
        filename="NA-0042-x.json",
    )
    assert any("git mv to resolved/" in e for e in closed_in_cards)
    unresolved = nac.validate_card(_card(status="RESOLVED"), resolved_dir=True, filename="NA-0042-x.json")
    assert any("resolution" in e for e in unresolved)
    sci = nac.validate_card(_card(scientific_effect="MINOR"), resolved_dir=False, filename="NA-0042-x.json")
    assert any("scientific_effect" in e for e in sci)
    forbidden = nac.validate_card(
        _card(refs={"pr": 1, "lemma_closed": True}), resolved_dir=False, filename="NA-0042-x.json"
    )
    assert any("forbidden" in e for e in forbidden)
    name = nac.validate_card(_card(), resolved_dir=False, filename="NA-0099-other.json")
    assert any("filename" in e for e in name)


def test_validator_cli_detects_duplicate_ids(tmp_path: Path) -> None:
    cards = tmp_path / "needs_attention" / "cards"
    cards.mkdir(parents=True)
    (tmp_path / "needs_attention" / "resolved").mkdir()
    (cards / "NA-0001-a.json").write_text(json.dumps(_card(id="NA-0001")), encoding="utf-8")
    (cards / "NA-0001-b.json").write_text(json.dumps(_card(id="NA-0001")), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "needs_attention_check.py"), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "duplicate id NA-0001" in result.stderr


def test_classify_pr_findings() -> None:
    pr = {
        "number": 7,
        "title": "t",
        "html_url": "https://github.com/o/r/pull/7",
        "user": {"login": "bot"},
        "head": {"ref": "cursor/x", "sha": "abc"},
        "draft": True,
        "mergeable_state": "dirty",
        "mergeable": False,
        "updated_at": "2026-09-24T00:00:00Z",
    }
    runs = [
        {"name": "sanity", "conclusion": "failure", "html_url": "u1"},
        {"name": "ok", "conclusion": "success"},
        {"name": "pending", "conclusion": None},
    ]
    reviews = [
        {"user": {"login": "r1"}, "state": "CHANGES_REQUESTED", "submitted_at": "2026-09-25T00:00:00Z"},
        {"user": {"login": "r1"}, "state": "APPROVED", "submitted_at": "2026-09-26T00:00:00Z"},
        {"user": {"login": "r2"}, "state": "CHANGES_REQUESTED", "submitted_at": "2026-09-26T00:00:00Z"},
    ]
    findings = nas.classify_pr(pr, runs, reviews, now=NOW, stale_hours=48, repo="o/r")
    kinds = {f["kind"] for f in findings}
    assert kinds == {"PR_CHECKS_FAILING", "PR_CONFLICTING", "PR_CHANGES_REQUESTED", "PR_STALE_DRAFT"}
    failing = next(f for f in findings if f["kind"] == "PR_CHECKS_FAILING")
    assert [d["name"] for d in failing["detail"]] == ["sanity"]
    changes = next(f for f in findings if f["kind"] == "PR_CHANGES_REQUESTED")
    assert changes["detail"]["reviewers"] == ["r2"]  # r1's later APPROVED supersedes
    assert all(f["severity"] in ("high", "medium", "low", "info") for f in findings)

    clean = {**pr, "mergeable_state": "clean", "mergeable": True, "draft": False}
    assert nas.classify_pr(clean, [{"name": "ok", "conclusion": "success"}], [], now=NOW, stale_hours=48, repo="o/r") == []

    # A superseded red attempt must not mask a newer green run of the same check.
    reruns = [
        {"id": 1, "name": "verify", "conclusion": "failure", "completed_at": "2026-09-27T19:18:00Z"},
        {"id": 2, "name": "verify", "conclusion": "success", "completed_at": "2026-09-27T19:40:00Z"},
    ]
    assert nas.classify_pr(clean, reruns, [], now=NOW, stale_hours=48, repo="o/r") == []
    assert [f["kind"] for f in nas.classify_pr(clean, list(reversed(reruns)), [], now=NOW, stale_hours=48, repo="o/r")] == []


def test_expired_leases_only_active_or_offered_past_expiry() -> None:
    ledger = {
        "leases": [
            {"work_id": "a", "state": "ACTIVE", "expires_at": "2026-09-27T18:00:00Z", "source": {"repo": "x", "pr": 1}},
            {"work_id": "b", "state": "OFFERED", "expires_at": "2026-09-28T00:00:00Z"},
            {"work_id": "c", "state": "RELEASED", "expires_at": "2026-09-01T00:00:00Z"},
            {"work_id": "d", "state": "ACTIVE", "expires_at": None},
        ]
    }
    out = nas.expired_leases(ledger, now=NOW)
    assert [l["work_id"] for l in out] == ["a"]
    assert out[0]["overdue_hours"] == 1.0
    assert out[0]["kind"] == "LEASE_EXPIRED"


def test_render_triage_mentions_every_kind() -> None:
    snap = {
        "generated_at": "2026-09-27T19:00:00Z",
        "repos_scanned": 1,
        "open_prs": 0,
        "api_calls": 1,
        "findings": [],
        "transport_errors": ["HTTP 403 /x"],
    }
    text = nas.render_triage(snap)
    for kind in ("CARD_OPEN", "PR_CHECKS_FAILING", "PR_CONFLICTING", "PR_CHANGES_REQUESTED", "LEASE_EXPIRED", "PR_STALE_DRAFT"):
        assert f"## {kind} (0)" in text
    assert "scientific effect NONE" in text
    assert "HTTP 403 /x" in text


def test_committed_snapshot_is_none_effect_if_present() -> None:
    snap = ROOT / "needs_attention" / "SNAPSHOT.json"
    if not snap.is_file():
        return
    data = json.loads(snap.read_text(encoding="utf-8"))
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed_flipped"] is False
    assert isinstance(data["findings"], list)


# ---------------------------------------------------------------- one shared tip gate (NA-0007)


def test_ci_uses_exactly_one_tip_drift_gate() -> None:
    """NA-0007: four agents shipped four gate scripts within 25 minutes; ci.yml must
    reference exactly one so the next fix does not race the last one."""
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    gates = sorted({name for name in ("tip_drift_class.py", "tip_drift_gate.py", "path_c_tip_gate.py", "path_c_tip_drift_tolerance.sh") if f"scripts/{name}" in ci})
    assert gates == ["tip_drift_class.py"], gates
    for stale in ("tip_drift_gate.py", "path_c_tip_gate.py", "path_c_tip_drift_tolerance.sh"):
        assert not (ROOT / "scripts" / stale).exists(), f"duplicate gate left in tree: {stale}"
    # a mismatch must route to the classifier, never straight to ::error
    assert "DESCENDANT" in ci and "path_c_landed" in ci
    # lemma_closed gates on the live tip are untouched by the gate change
    assert "lemma_closed=false" in ci


def test_ci_sanity_validates_needs_attention_cards() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "scripts/needs_attention_check.py" in ci
