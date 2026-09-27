"""Offline tests for the needs_attention inbox tooling and the tip-drift gate.

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
import tip_drift_gate as tdg  # noqa: E402

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


# ---------------------------------------------------------------- tip-drift gate


def test_tip_gate_exact_match_ok_without_network() -> None:
    sha = "2f7a5a9f10c9ed5f5b7792a8f2521318d9208532"
    rep = tdg.evaluate(live=sha, base=sha, landed=False, repo_dir=None, use_api=False)
    assert rep["ok"] is True and rep["mode"] == "EXACT"
    rep7 = tdg.evaluate(live=sha, base=sha[:7], landed=False, repo_dir=None, use_api=False)
    assert rep7["ok"] is True


def test_tip_gate_fails_closed_when_unresolvable_or_not_landed(tmp_path: Path) -> None:
    live = "e7652a130398e88b2119884498af0987eef135c0"
    base = "2f7a5a9f10c9ed5f5b7792a8f2521318d9208532"
    rep = tdg.evaluate(live=live, base=base, landed=True, repo_dir=None, use_api=False, use_temp_fetch=False)
    assert rep["ok"] is False and rep["mode"] == "DRIFT"
    assert "unresolvable" in rep["reason"]
    assert rep["scientific_effect"] == "NONE" and rep["lemma_closed_flipped"] is False


def _two_commit_repo(repo: Path) -> tuple[str, str]:
    repo.mkdir()

    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()

    git("init", "-q", "-b", tdg.HARDENING_REF)
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (repo / "a").write_text("1", encoding="utf-8")
    git("add", "a")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (repo / "a").write_text("2", encoding="utf-8")
    git("commit", "-q", "-am", "next")
    live = git("rev-parse", "HEAD")
    return base, live


def test_tip_gate_ancestor_via_local_git(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    base, live = _two_commit_repo(repo)

    landed = tdg.evaluate(live=live, base=base, landed=True, repo_dir=repo, use_api=False)
    assert landed["ok"] is True and landed["mode"] == "ANCESTOR"
    assert landed["ancestry_via"] == "git" and landed["ahead_by"] == 1

    not_landed = tdg.evaluate(live=live, base=base, landed=False, repo_dir=repo, use_api=False)
    assert not_landed["ok"] is False and "not landed" in not_landed["reason"]

    reversed_ = tdg.evaluate(live=base, base=live, landed=True, repo_dir=repo, use_api=False)
    assert reversed_["ok"] is False and reversed_["base_is_ancestor_of_live"] is False


def test_tip_gate_temp_fetch_fallback_needs_no_api(tmp_path: Path, monkeypatch) -> None:
    """No --repo-dir and no usable API token: ancestry still resolves via a cached treeless fetch."""
    remote = tmp_path / "remote"
    base, live = _two_commit_repo(remote)
    cache = tmp_path / "cache"
    monkeypatch.setenv("TIP_DRIFT_REMOTE_URL", str(remote))
    monkeypatch.setenv("TIP_DRIFT_CACHE_DIR", str(cache))
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_stale_token_that_would_401")

    rep = tdg.evaluate(live=live, base=base, landed=True, repo_dir=None, use_api=False)
    assert rep["ok"] is True and rep["mode"] == "ANCESTOR"
    assert rep["ancestry_via"] == "git_temp_fetch" and rep["ahead_by"] == 1
    assert (cache / "HEAD").exists()

    # second call reuses the cache (no re-init) and a reversed pair fails closed
    again = tdg.evaluate(live=live, base=base, landed=True, repo_dir=None, use_api=False)
    assert again["ok"] is True
    reversed_ = tdg.evaluate(live=base, base=live, landed=True, repo_dir=None, use_api=False)
    assert reversed_["ok"] is False and reversed_["base_is_ancestor_of_live"] is False

    # unknown live SHA is unresolvable → DRIFT, never silently OK
    unknown = tdg.evaluate(live="a" * 40, base=base, landed=True, repo_dir=None, use_api=False)
    assert unknown["ok"] is False and "unresolvable" in unknown["reason"]


def test_tip_gate_requires_landed_commit_in_live_history(tmp_path: Path) -> None:
    """BASE_TIP ancestry alone is not enough: the recorded landed commit must be in history too."""
    repo = tmp_path / "r"
    base, live = _two_commit_repo(repo)
    common = dict(live=live, base=base, landed=True, repo_dir=repo, use_api=False, use_temp_fetch=False)

    ok = tdg.evaluate(**common, landed_sha=base)  # landed commit == BASE_TIP → in history
    assert ok["ok"] is True and ok["landed_sha_is_ancestor_of_live"] is True

    live_is_landed = tdg.evaluate(**common, landed_sha=live)
    assert live_is_landed["ok"] is True

    gone = tdg.evaluate(**common, landed_sha="b" * 40)  # not an object in the repo → unresolvable
    assert gone["ok"] is False and gone["mode"] == "DRIFT" and "landed Path C commit" in gone["reason"]

    # a side branch commit that is NOT in live history → DRIFT
    side = subprocess.run(
        ["git", "commit-tree", f"{base}^{{tree}}", "-p", base, "-m", "side"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    rewritten = tdg.evaluate(**common, landed_sha=side)
    assert rewritten["ok"] is False and rewritten["landed_sha_is_ancestor_of_live"] is False
    assert "rewritten/reverted" in rewritten["reason"]


def test_tip_gate_landed_args_from_verify(tmp_path: Path) -> None:
    v = tmp_path / "VERIFY.json"
    v.write_text(json.dumps({"path_c_landed": True, "path_c_0019_merge_commit_sha": "c" * 40}), encoding="utf-8")
    assert tdg.landed_args(v) == {"landed": True, "landed_sha": "c" * 40}
    v.write_text(json.dumps({"path_c_landed": False, "merge_commit_sha": "d" * 40}), encoding="utf-8")
    assert tdg.landed_args(v) == {"landed": False, "landed_sha": None}
    assert tdg.landed_args(tmp_path / "missing.json") == {"landed": False, "landed_sha": None}
    # the committed VERIFY records the 0019 merge commit
    real = tdg.landed_args(ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json")
    assert real["landed"] is True and real["landed_sha"] and len(real["landed_sha"]) == 40


def test_ci_uses_shared_tip_gate() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("scripts/tip_drift_gate.py") >= 2
    assert 'if [[ "$TIP" != "$BASE_SHA" ]]' not in ci
    # lemma_closed gates on the live tip are untouched
    assert "lemma_closed is not false after path-c-applied-bundle" in ci
    assert "grep -q 'lemma_closed=false' /tmp/math_status_landed.out" in ci
    for script in ("refresh_path_c_bundle.sh", "assert_path_c_ready.sh", "path_c_dry_run.py", "write_path_c_status.py"):
        assert "tip_drift_gate" in (ROOT / "scripts" / script).read_text(encoding="utf-8"), script
