"""Sanity checks for the trial sandbox.

These tests encode repository intent only. They do not validate research claims
from d6g8k5htny-coder/main and must never be cited as scientific evidence.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_states_sandbox_boundary() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "research repository" in text.lower()
    assert "**Not**" in text
    assert "d6g8k5htny-coder/main" in text
    assert "No scientific authority" in text


def test_audit_and_owner_actions_exist() -> None:
    assert (ROOT / "docs" / "PROJECT_INTENT_AUDIT.md").is_file()
    assert (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").is_file()
    audit = (ROOT / "docs" / "PROJECT_INTENT_AUDIT.md").read_text(encoding="utf-8")
    assert "Scientific effect: NONE" in audit
    assert "OBL-H5-JETMOD" in audit
    assert "D3-LEMMA-RN-UNIF" in audit
    assert "lemma_closed" in audit


def test_license_is_cc0() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "CC0 1.0 Universal" in license_text


def test_no_research_registers_tree() -> None:
    """trial must not grow a shadow registers/ that could be mistaken for authority."""
    assert not (ROOT / "registers").exists()
    assert not (ROOT / "claims").exists()


def test_portable_default_branch_pack() -> None:
    readme = (ROOT / "portable" / "main-default-branch" / "README.md").read_text(
        encoding="utf-8"
    )
    apply = (ROOT / "portable" / "main-default-branch" / "APPLY.md").read_text(
        encoding="utf-8"
    )
    assert "chatgpt/drive-github-hardening-20260919" in readme
    assert "PR #2" in readme
    assert "abandoned" in readme.lower()
    assert "Apply" in apply
    assert "does not" in readme.lower()
    assert "premise discharge" in readme.lower()


def test_audit_script_reports_misalignment_or_ok() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_main_alignment.py")],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode in (0, 1), result.stderr
    assert '"scientific_effect": "NONE"' in result.stdout
    if result.returncode == 1:
        assert "MISALIGNED" in result.stderr


def test_autonomous_log_and_ci_exist() -> None:
    text = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "status promotion" in text
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "portable-patches-on-main" in ci
    assert "apply_all.sh" in ci
    assert "apply_all.sh --check" in ci or "apply_all.sh --check" in ci.replace("\n", " ")
    land_wf = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text()
    assert "MAIN_PUSH_TOKEN" in land_wf
    assert "option-b" in land_wf
    apply_all = (ROOT / "portable" / "patches" / "apply_all.sh").read_text()
    assert "--check" in apply_all
    assert "CHECK_ONLY" in apply_all


def test_portable_patches_exist() -> None:
    root = ROOT / "portable" / "patches"
    assert (root / "README.md").is_file()
    p1 = (root / "0001-carriers-verify-ignore-bytecode-caches.patch").read_text(encoding="utf-8")
    p2 = (root / "0002-math-console-path-honesty.patch").read_text(encoding="utf-8")
    assert "carriers_verify.py" in p1
    assert "__pycache__" in p1
    assert "math_console.py" in p2
    assert "docs/math_status/math_console.py" in p2
    assert (ROOT / "portable" / "pr2-landing" / "CHECKLIST.md").is_file()
    assert (ROOT / "portable" / "patches" / "apply_all.sh").is_file()
    assert (ROOT / "portable" / "patches" / "BASE_TIP.txt").is_file()
    assert "1ea0ae8" in (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text()
    assert "PACKET.json" in (ROOT / "portable" / "patches" / "0002-math-console-path-honesty.patch").read_text()
    assert (ROOT / "portable" / "patches" / "0003-gaussian-moments-parametrize-list.patch").is_file()
    assert (ROOT / "portable" / "main-default-branch" / "0001-option-b-default-branch-notice.patch").is_file()
    ob = (ROOT / "portable" / "main-default-branch" / "0001-option-b-default-branch-notice.patch").read_text()
    assert "chatgpt/drive-github-hardening-20260919" in ob
    assert "quarantine/pre-q0-scaffolding" in ob
    checklist = (ROOT / "portable" / "pr2-landing" / "CHECKLIST.md").read_text(encoding="utf-8")
    assert "MERGEABLE" in checklist
    assert "Scientific effect: NONE" in checklist


def test_alignment_status_script() -> None:
    import subprocess, sys, json
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "alignment_status.py")],
        capture_output=True, text=True, timeout=90, check=False,
    )
    assert result.returncode in (0, 2), result.stderr
    if result.returncode == 0:
        data = json.loads(result.stdout)
        assert data["scientific_effect"] == "NONE"
        assert "main" in data and "trial" in data
        assert data["main"]["alignment"]["audit_exit"] in (0, 1)


def test_land_sheet() -> None:
    text = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "Path A" in text and "Path B" in text and "Path C" in text
    assert "PR #2" in text
    assert "Scientific effect: NONE" in text
    assert "403" in text


def test_watch_main_alignment_and_expected_fixture() -> None:
    import json, subprocess, sys
    assert (ROOT / "portable" / "EXPECTED_POST_ALIGNMENT.json").is_file()
    expected = json.loads((ROOT / "portable" / "EXPECTED_POST_ALIGNMENT.json").read_text())
    assert expected["scientific_effect"] == "NONE"
    assert (ROOT / "portable" / "patches" / "0004-git-fixture-timeout-60s.patch").is_file()
    assert (ROOT / "portable" / "patches" / "COMPATIBILITY.md").is_file()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "watch_main_alignment.py")],
        capture_output=True, text=True, timeout=90, check=False,
    )
    assert result.returncode in (0, 1, 2)
    data = json.loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data["state"] in {"ALIGNED", "MISALIGNED", "TRANSPORT_ERROR"}


def test_conflicting_pr_notes() -> None:
    text = (ROOT / "portable" / "CONFLICTING_PR_NOTES.md").read_text(encoding="utf-8")
    assert "PR #12" in text and "PR #3" in text
    assert "math_console.py" in text
    assert "OPEN_PROBLEMS.md" in text
    assert "Scientific effect: NONE" in text


def test_verify_after_merge_script() -> None:
    path = ROOT / "portable" / "pr2-landing" / "VERIFY_AFTER_MERGE.sh"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "watch_main_alignment.py" in text
    assert "ALIGNED" in text


def test_pack_portable_script() -> None:
    import subprocess, tempfile, os
    script = ROOT / "scripts" / "pack_portable.sh"
    assert script.is_file()
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "pack.tgz")
        subprocess.run([str(script), out], check=True, timeout=60)
        assert os.path.getsize(out) > 1000
