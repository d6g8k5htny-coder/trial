"""Offline checks for scripts/tip_drift_class.py and the DESCENDANT_OK gates.

Sidecar b3c6 (2026-09-27): hardening merges land several times per hour, so a
strict ``live == BASE_TIP`` gate reds every trial-ci run between an upstream
merge and the next tip-sync pulse. With Path C landed, a live tip that
*descends* from BASE_TIP still carries the stack; BEHIND / DIVERGED stay red.

Repository-intent only. Not evidence about any claim; scientific effect NONE.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tip_drift_class as tdc  # noqa: E402

BASE = "e7652a130398e88b2119884498af0987eef135c0"
LIVE = "d4ad3bbe9dc3eb9e7c6c61a3fe57dbdf3027e10b"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Never hit the compare API in unit tests; each test sets the answer."""
    monkeypatch.setattr(tdc, "_compare_status", lambda *a, **k: pytest.fail("network"))
    tdc._CACHE.clear()


def _status(monkeypatch, value: str):
    monkeypatch.setattr(tdc, "_compare_status", lambda base, live, repo=None, timeout=30: value)


def test_match_is_local_and_prefix_tolerant():
    assert tdc.classify(BASE, BASE) == "MATCH"
    assert tdc.classify(BASE[:7], BASE) == "MATCH"
    assert tdc.classify(BASE, BASE[:12]) == "MATCH"
    assert tdc.classify(BASE.upper(), BASE) == "MATCH"


def test_bad_input_is_unknown_without_network():
    assert tdc.classify("", LIVE) == "UNKNOWN"
    assert tdc.classify(None, LIVE) == "UNKNOWN"
    assert tdc.classify("not-a-sha", LIVE) == "UNKNOWN"
    assert tdc.classify(BASE, "abc") == "UNKNOWN"  # < 7 hex


@pytest.mark.parametrize(
    "status,expected",
    [
        ("ahead", "DESCENDANT"),
        ("behind", "BEHIND"),
        ("diverged", "DIVERGED"),
        ("identical", "MATCH"),
        ("", "UNKNOWN"),
        ("garbage", "UNKNOWN"),
    ],
)
def test_compare_status_maps_to_class(monkeypatch, status, expected):
    _status(monkeypatch, status)
    assert tdc.classify(BASE, LIVE) == expected


def test_acceptable_policy():
    assert tdc.acceptable("MATCH", landed=False) is True
    assert tdc.acceptable("MATCH", landed=True) is True
    assert tdc.acceptable("DESCENDANT", landed=True) is True
    # Not landed → a moved tip still needs a real refresh before landing.
    assert tdc.acceptable("DESCENDANT", landed=False) is False
    for cls in ("BEHIND", "DIVERGED", "UNKNOWN"):
        assert tdc.acceptable(cls, landed=True) is False
        assert tdc.acceptable(cls, landed=False) is False


def test_path_c_landed_reads_verify(tmp_path):
    good = tmp_path / "VERIFY.json"
    good.write_text(json.dumps({"path_c_landed": True}), encoding="utf-8")
    assert tdc.path_c_landed(good) is True
    bad = tmp_path / "VERIFY2.json"
    bad.write_text(json.dumps({"path_c_landed": "true"}), encoding="utf-8")
    assert tdc.path_c_landed(bad) is False
    assert tdc.path_c_landed(tmp_path / "missing.json") is False


def test_main_exit_codes(monkeypatch, capsys):
    _status(monkeypatch, "ahead")
    assert tdc.main([BASE, LIVE, "--landed"]) == 0
    assert capsys.readouterr().out.strip() == "DESCENDANT"

    monkeypatch.setattr(tdc, "path_c_landed", lambda *a, **k: False)
    assert tdc.main([BASE, LIVE]) == 1

    _status(monkeypatch, "behind")
    assert tdc.main([BASE, LIVE, "--landed"]) == 1

    _status(monkeypatch, "")
    assert tdc.main([BASE, LIVE, "--landed"]) == 2

    assert tdc.main([BASE, BASE]) == 0


def test_main_json_never_flips_research(monkeypatch, capsys):
    _status(monkeypatch, "ahead")
    assert tdc.main([BASE, LIVE, "--landed", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["class"] == "DESCENDANT"
    assert data["acceptable"] is True
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed"] is False


def test_cli_rejects_bad_input_with_exit_2():
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tip_drift_class.py"), "nope", "alsonope"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 2
    assert p.stdout.strip() == "UNKNOWN"


def test_gates_carry_descendant_ok_and_keep_hard_fail():
    """Each wired gate mentions DESCENDANT_OK and still exits 1 on other drift."""
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("tip_drift_class.py") == 2
    assert "DESCENDANT_OK" in ci
    assert "::error::tip-drift: live hardening SHA" in ci

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "TIP_DRIFT_DESCENDANT_OK" in refresh
    assert 'echo "refresh_path_c_bundle: dry-run TIP_DRIFT ${PRIOR_SHORT} -> ${LIVE_SHORT}' in refresh

    for rel in (
        "scripts/assert_path_c_ready.sh",
        "scripts/owner_open_path_c_pr.sh",
        "scripts/owner_land_path_c.sh",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "tip_drift_class.py" in text, rel
        assert "DESCENDANT" in text, rel

    for rel in (
        "scripts/path_c_dry_run.py",
        "scripts/write_path_c_status.py",
        "scripts/when_writable_land.py",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "tip_drift_class" in text, rel
        assert "tip_exact_match" in text, rel


def test_apply_all_0017_semantic_guard_present():
    text = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert '"$bn" == 0017-*' in text
    assert "already-applied (semantic)" in text
