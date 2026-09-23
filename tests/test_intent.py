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
    # Must satisfy audit_main_alignment Q0_MARKERS and clear COMPLEXITY_MARKERS.
    for marker in (
        "q0 Research Program",
        "SIDE24",
        "chatgpt/drive-github-hardening-20260919",
        "PR #2",
    ):
        assert marker in readme
    for bad in (
        "Multiscale Retrodiction Complexity",
        "complexity-physics-framework",
        "δC = 0",
    ):
        assert bad not in readme


def test_audit_script_reports_misalignment_or_ok() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_main_alignment.py")],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    # 0=aligned, 1=misaligned, 2=transport (e.g. API rate limit on CI)
    assert result.returncode in (0, 1, 2), result.stderr
    if result.returncode == 2:
        assert "transport" in result.stderr.lower()
        return
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
    # Audit/watch steps must export the runner token (avoids unauthenticated API 403s).
    assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in ci
    land_wf = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text()
    assert "MAIN_PUSH_TOKEN" in land_wf
    assert "option-b" in land_wf
    assert "dry_run" in land_wf
    assert "0001-option-b-default-branch-notice.patch" in land_wf
    assert "Locate Option-B patch" in land_wf or "PATCH_PATH" in land_wf
    assert "audit_local_tree.py" in land_wf
    assert "would-align" in land_wf
    apply_all = (ROOT / "portable" / "patches" / "apply_all.sh").read_text()
    assert "--check" in apply_all
    assert "CHECK_ONLY" in apply_all
    # Ordered apply; --check uses a disposable worktree
    assert "worktree" in apply_all
    assert "apply_series" in apply_all
    assert "0008-carriers-math-status-close-file-handles.patch" in apply_all
    assert "0012-inventable-negative-tests-close-file-handles.patch" in apply_all
    assert "0014-collision-close-file-handles.patch" in apply_all
    # Post-#27: tip-cut 0005/0006/0007 dropped from apply_all (kept on disk for history)
    assert "0005-inventable-probes-restore-receipts-after-test.patch" not in apply_all
    assert "0006-instrumentation-status-restore-receipts-after-test.patch" not in apply_all
    assert "0007-inventable-tests-close-file-handles.patch" not in apply_all


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
    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text()
    assert "8510874" in base_tip
    assert "chatgpt/drive-github-hardening-20260919" in base_tip
    assert "PACKET.json" in (ROOT / "portable" / "patches" / "0002-math-console-path-honesty.patch").read_text()
    assert (ROOT / "portable" / "patches" / "0003-gaussian-moments-parametrize-list.patch").is_file()
    apply_all_txt = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    # Historical tip-cut 0005/0006/0007 kept on disk; dropped from apply_all after PR #27
    p5 = (ROOT / "portable" / "patches" / "0005-inventable-probes-restore-receipts-after-test.patch").read_text(
        encoding="utf-8"
    )
    assert "test_inventable_jetmod_probes.py" in p5
    assert "INVENTABLE_PROBES_INDEX.json" in p5
    assert "finally:" in p5
    assert "SHORTCUTS" in p5 or "freeze" in p5
    assert "0005-inventable-probes-restore-receipts-after-test.patch" not in apply_all_txt
    p6 = (ROOT / "portable" / "patches" / "0006-instrumentation-status-restore-receipts-after-test.patch").read_text(
        encoding="utf-8"
    )
    assert "test_inventable_jetmod_instrumentation_status.py" in p6
    assert "INVENTABLE_INSTRUMENTATION_STATUS_INDEX.json" in p6
    assert "0006-instrumentation-status-restore-receipts-after-test.patch" not in apply_all_txt
    p7 = (ROOT / "portable" / "patches" / "0007-inventable-tests-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "test_inventable_jetmod_probes.py" in p7
    assert "test_inventable_jetmod_instrumentation_status.py" in p7
    assert "Path(path).read_bytes()" in p7 or "read_bytes()" in p7
    assert "0007-inventable-tests-close-file-handles.patch" not in apply_all_txt
    p8 = (ROOT / "portable" / "patches" / "0008-carriers-math-status-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "test_carriers.py" in p8
    assert "test_math_status.py" in p8
    assert "carriers_verify.py" in p8
    assert "0008-carriers-math-status-close-file-handles.patch" in apply_all_txt
    p9 = (ROOT / "portable" / "patches" / "0009-claims-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "test_claims.py" in p9
    assert "review_queue.json" in p9 or "operator_decisions.json" in p9
    assert "0009-claims-close-file-handles.patch" in apply_all_txt
    p12 = (ROOT / "portable" / "patches" / "0012-inventable-negative-tests-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "test_inventable_jetmod_probes.py" in p12
    assert "test_inventable_jetmod_instrumentation_status.py" in p12
    assert "0012-inventable-negative-tests-close-file-handles.patch" in apply_all_txt
    p14 = (ROOT / "portable" / "patches" / "0014-collision-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "collision_proposal_check.py" in p14
    assert "test_collision_proposal.py" in p14
    assert "0014-collision-close-file-handles.patch" in apply_all_txt
    assert "0013-verify-quarantine-close-file-handles.patch" in apply_all_txt
    assert (ROOT / "scripts" / "print_owner_unblock.sh").is_file()
    land_wf = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text(encoding="utf-8")
    assert "gh pr create" in land_wf
    assert "option-b-notice-from-trial" in land_wf
    assert (ROOT / "portable" / "patches" / "0005-pre17-inventable-probes-restore-receipts-after-test.patch").is_file()
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
    assert "#27" in text
    assert "0001–0004 + 0008" in text or "0001-0004 + 0008" in text
    compat = (ROOT / "portable" / "patches" / "COMPATIBILITY.md").read_text(encoding="utf-8")
    assert "PR #27" in compat
    assert "20e31a1" in compat
    assert "obsolete" in compat.lower()
    assert "0001–0004 + 0008" in compat or "0001-0004 + 0008" in compat
    assert "tmp_path" in compat


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
    assert "#18" in text and "340d98a" in text


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


def test_audit_local_tree_option_b_would_align() -> None:
    """Option-B portable README alone must flip the local auditor to ALIGNED."""
    import json
    import shutil
    import subprocess
    import tempfile

    script = ROOT / "scripts" / "audit_local_tree.py"
    assert script.is_file()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shutil.copy(
            ROOT / "portable" / "main-default-branch" / "README.md",
            root / "README.md",
        )
        # Simulate post-am quarantine (body moved off root).
        (root / "quarantine").mkdir()
        result = subprocess.run(
            [sys.executable, str(script), str(root)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["state"] == "ALIGNED"
        assert data["scientific_effect"] == "NONE"
        assert data["complexity_markers_present"] == []
        assert "q0 Research Program" in data["q0_or_notice_markers_present"]


def test_owner_one_liners_and_probe_main_write() -> None:
    one = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Path A" in one and "Path B" in one and "Path C" in one
    assert "gh pr ready 2" in one
    assert "gh pr merge 2" in one
    assert "MAIN_PUSH_TOKEN" in one
    assert "apply_all.sh" in one
    assert "Scientific effect: NONE" in one
    assert "owner_land_path_a.sh" in one
    assert "owner_land_path_b.sh" in one
    assert "wait_until_aligned.sh" in one
    assert "--direct-main" in one
    assert "--after-merge" in one
    patches_readme = (ROOT / "portable" / "patches" / "README.md").read_text(encoding="utf-8")
    assert "0006" in patches_readme
    assert "0007" in patches_readme
    assert "0008" in patches_readme
    assert "0009" in patches_readme
    assert "0012" in patches_readme
    assert "0014" in patches_readme
    assert "apply_all.sh" in patches_readme
    assert "8510874" in patches_readme or "PR #29" in patches_readme or "PR #27" in patches_readme
    probe = ROOT / "scripts" / "probe_main_write.py"
    assert probe.is_file()
    result = subprocess.run(
        [sys.executable, str(probe)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode in (0, 1, 2), result.stderr
    data = __import__("json").loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data["state"] in {"WRITABLE", "DENIED", "TRANSPORT_ERROR"}
    if result.returncode == 1:
        assert data["state"] == "DENIED"


def test_owner_land_scripts_exist_and_fail_closed() -> None:
    """Owner Path A/B land scripts must be executable and mention fail-closed gates."""
    path_a = ROOT / "scripts" / "owner_land_path_a.sh"
    path_b = ROOT / "scripts" / "owner_land_path_b.sh"
    wait_aligned = ROOT / "scripts" / "wait_until_aligned.sh"
    assert path_a.is_file() and path_b.is_file()
    assert wait_aligned.is_file()
    assert path_a.stat().st_mode & 0o111
    assert path_b.stat().st_mode & 0o111
    assert wait_aligned.stat().st_mode & 0o111
    a_text = path_a.read_text(encoding="utf-8")
    b_text = path_b.read_text(encoding="utf-8")
    wait_text = wait_aligned.read_text(encoding="utf-8")
    assert "gh pr ready" in a_text and "gh pr merge" in a_text
    assert "watch_main_alignment.py" in a_text
    assert "ALIGNED" in a_text
    assert "Scientific effect" in a_text
    assert "0001-option-b-default-branch-notice.patch" in b_text
    assert "audit_local_tree.py" in b_text
    assert "--direct-main" in b_text
    assert "--after-merge" in b_text
    assert "gh pr create" in b_text
    assert "Scientific effect" in b_text
    assert "watch_main_alignment.py" in wait_text
    assert "ALIGNED" in wait_text
    assert "--verify" in wait_text
    assert "VERIFY_AFTER_MERGE.sh" in wait_text
    assert "scientific_effect=NONE" in wait_text or "Scientific effect: NONE" in wait_text
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "owner_land_path_a.sh" in unblock
    assert "owner_land_path_b.sh" in unblock
    assert "wait_until_aligned.sh" in unblock
    # --after-merge: fail-closed while MISALIGNED; succeed once default tip is ALIGNED (PR #2).
    result = subprocess.run(
        ["bash", str(path_b), "--after-merge"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    watch = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "watch_main_alignment.py")],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    watch_state = __import__("json").loads(watch.stdout).get("state") if watch.returncode in (0, 1) else None
    if watch_state == "ALIGNED":
        assert result.returncode == 0
        assert "ALIGNED" in (result.stderr + result.stdout)
    else:
        assert result.returncode != 0
        assert "ERROR" in (result.stderr + result.stdout)
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "owner_land_path_a.sh" in pack
    assert "owner_land_path_b.sh" in pack
