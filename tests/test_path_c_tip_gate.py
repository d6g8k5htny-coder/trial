"""Offline contract tests for scripts/path_c_tip_gate.py.

Own module (not tests/test_intent.py) so wake-loop appends never conflict.
Ancestry is stubbed: no network, no clone. These tests encode the engineering
gate contract only; they are not research evidence. Scientific effect: NONE.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import path_c_tip_gate as tg  # noqa: E402

BASE = "2f7a5a9f10c9ed5f5b7792a8f2521318d9208532"
MERGE = "542e6ec2f462d6202f5bc5b3a044e71ae7a1a96c"
LIVE = "d4ad3bbe9dc3eb9e7c6c61a3fe57dbdf3027e10b"
OTHER = "2cce7bf4c9d2381d95e532186bcc7aae67726d8a"


def _stub_ancestry(monkeypatch, table: dict[tuple[str, str], bool | None]) -> None:
    def fake(ancestor: str, descendant: str, repo_dir, token=""):
        if tg._sha_prefix_eq(ancestor, descendant):
            return True, "identical"
        got = table.get((ancestor, descendant))
        return got, ("stub" if got is not None else "none")

    monkeypatch.setattr(tg, "is_ancestor", fake)


def test_parse_base_tip_sha_variants() -> None:
    assert tg.parse_base_tip_sha(f"chatgpt/drive-github-hardening-20260919 {BASE}") == BASE
    assert tg.parse_base_tip_sha(f"chatgpt/drive-github-hardening-20260919 {BASE}  # tip") == BASE
    assert tg.parse_base_tip_sha("ref 2f7a5a9") == "2f7a5a9"
    assert tg.parse_base_tip_sha("") == ""
    assert tg.parse_base_tip_sha("no sha here") == ""


def test_tip_match_is_ok_without_ancestry(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {})
    res = tg.evaluate(BASE, BASE, path_c_landed=False)
    assert res["tip_state"] == "TIP_MATCH"
    assert res["tip_ok"] is True
    assert res["tip_matches_base"] is True
    short = tg.evaluate(BASE[:7], BASE, path_c_landed=False)
    assert short["tip_state"] == "TIP_MATCH" and short["tip_matches_base"] is True


def test_landed_ancestor_requires_base_and_merge_in_history(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {(BASE, LIVE): True, (MERGE, LIVE): True})
    res = tg.evaluate(LIVE, BASE, path_c_landed=True, landed_merge_sha=MERGE)
    assert res["tip_state"] == "LANDED_ANCESTOR"
    assert res["tip_ok"] is True
    assert res["tip_matches_base"] is False, "literal equality must stay honest"
    assert res["base_is_ancestor_of_live"] is True
    assert res["landed_merge_is_ancestor_of_live"] is True


def test_drift_when_base_not_in_live_history(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {(BASE, OTHER): False})
    res = tg.evaluate(OTHER, BASE, path_c_landed=True, landed_merge_sha=MERGE)
    assert res["tip_state"] == "TIP_DRIFT"
    assert res["tip_ok"] is False
    assert "not in live hardening history" in res["reason"]


def test_drift_when_merge_missing_even_if_base_is_ancestor(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {(BASE, LIVE): True, (MERGE, LIVE): False})
    res = tg.evaluate(LIVE, BASE, path_c_landed=True, landed_merge_sha=MERGE)
    assert res["tip_state"] == "TIP_DRIFT"
    assert res["tip_ok"] is False
    assert "0019 merge" in res["reason"]


def test_drift_when_path_c_not_landed(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {(BASE, LIVE): True, (MERGE, LIVE): True})
    res = tg.evaluate(LIVE, BASE, path_c_landed=False, landed_merge_sha=MERGE)
    assert res["tip_state"] == "TIP_DRIFT"
    assert res["tip_ok"] is False
    assert res["base_is_ancestor_of_live"] is None, "no ancestry work when not landed"


def test_unknown_when_ancestry_unavailable(monkeypatch) -> None:
    _stub_ancestry(monkeypatch, {})
    res = tg.evaluate(LIVE, BASE, path_c_landed=True, landed_merge_sha=MERGE)
    assert res["tip_state"] == "UNKNOWN"
    assert res["tip_ok"] is False
    missing = tg.evaluate("", BASE, path_c_landed=True)
    assert missing["tip_state"] == "UNKNOWN" and missing["tip_ok"] is False


def test_never_carries_research_status() -> None:
    res = tg.evaluate(BASE, BASE, path_c_landed=True)
    assert res["scientific_effect"] == "NONE"
    for key in res:
        assert "lemma" not in key and "prize" not in key and "premise" not in key


def test_cli_sh_and_exit_codes(monkeypatch, tmp_path: Path, capsys) -> None:
    trial = tmp_path / "trial"
    (trial / "portable" / "patches").mkdir(parents=True)
    (trial / "portable" / "path-c-applied-bundle").mkdir(parents=True)
    (trial / "portable" / "patches" / "BASE_TIP.txt").write_text(
        f"chatgpt/drive-github-hardening-20260919 {BASE}\n", encoding="utf-8"
    )
    (trial / "portable" / "path-c-applied-bundle" / "VERIFY.json").write_text(
        json.dumps({"path_c_landed": True, "path_c_0019_merge_commit_sha": MERGE}), encoding="utf-8"
    )
    _stub_ancestry(monkeypatch, {(BASE, LIVE): True, (MERGE, LIVE): True, (BASE, OTHER): False})

    assert tg.main(["--live", LIVE, "--trial-root", str(trial), "--sh"]) == 0
    out = capsys.readouterr().out
    assert "TIP_GATE_TIP_STATE='LANDED_ANCESTOR'" in out
    assert "TIP_GATE_TIP_OK='true'" in out
    assert "TIP_GATE_TIP_MATCHES_BASE='false'" in out
    assert f"TIP_GATE_LANDED_MERGE_SHA='{MERGE}'" in out

    assert tg.main(["--live", OTHER, "--trial-root", str(trial), "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data["tip_state"] == "TIP_DRIFT"

    assert tg.main(["--live", BASE, "--trial-root", str(trial), "--sh"]) == 0
    assert "TIP_GATE_TIP_STATE='TIP_MATCH'" in capsys.readouterr().out


def test_cli_unknown_exit_2(monkeypatch, tmp_path: Path) -> None:
    trial = tmp_path / "trial"
    (trial / "portable" / "patches").mkdir(parents=True)
    (trial / "portable" / "path-c-applied-bundle").mkdir(parents=True)
    (trial / "portable" / "patches" / "BASE_TIP.txt").write_text(f"ref {BASE}\n", encoding="utf-8")
    (trial / "portable" / "path-c-applied-bundle" / "VERIFY.json").write_text(
        json.dumps({"path_c_landed": True}), encoding="utf-8"
    )
    _stub_ancestry(monkeypatch, {})
    assert tg.main(["--live", LIVE, "--trial-root", str(trial), "--json"]) == 2


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (BASE, BASE, True),
        (BASE[:7], BASE, True),
        (BASE, BASE[:12], True),
        (BASE, OTHER, False),
        ("2f7a5a", BASE, False),
        ("", BASE, False),
    ],
)
def test_sha_prefix_eq(a: str, b: str, expected: bool) -> None:
    assert tg._sha_prefix_eq(a, b) is expected
