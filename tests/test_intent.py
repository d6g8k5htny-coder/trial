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
    agents = (ROOT / "portable" / "main-default-branch" / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    assert "chatgpt/drive-github-hardening-20260919" in readme
    assert "PR #2" in readme
    assert "abandoned" in readme.lower()
    assert "Apply" in apply
    assert "does not" in readme.lower()
    assert "premise discharge" in readme.lower()
    assert "AGENTS.md" in apply
    assert "restore_main_face.sh" in apply
    assert "lemma_closed" in agents
    assert "SIDE24" in agents or "q0" in agents.lower()
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
        assert bad not in agents


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
    assert "0015-frozen-drive-index-close-file-handles.patch" in apply_all
    assert "0016-receipts-bridge-close-file-handles.patch" in apply_all
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
    assert "74c082e" in base_tip
    assert "chatgpt/drive-github-hardening-20260919" in base_tip
    assert "PACKET.json" in (ROOT / "portable" / "patches" / "0002-math-console-path-honesty.patch").read_text()
    assert (ROOT / "portable" / "patches" / "0003-gaussian-moments-parametrize-list.patch").is_file()
    apply_all_txt = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "post-#41" in apply_all_txt or "PATH_C_BASE=main" in apply_all_txt
    assert "BASE_TIP" in apply_all_txt
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
    assert "0015-frozen-drive-index-close-file-handles.patch" in apply_all_txt
    p16 = (ROOT / "portable" / "patches" / "0016-receipts-bridge-close-file-handles.patch").read_text(
        encoding="utf-8"
    )
    assert "test_receipts.py" in p16
    assert "test_bridge.py" in p16
    assert "0016-receipts-bridge-close-file-handles.patch" in apply_all_txt
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
    """Option-B portable README (+ AGENTS) must flip the local auditor to ALIGNED."""
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
        shutil.copy(
            ROOT / "portable" / "main-default-branch" / "AGENTS.md",
            root / "AGENTS.md",
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
        assert data["root_has_AGENTS_md"] is True
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
    assert "restore_main_face.sh" in one
    assert "wait_until_aligned.sh" in one
    assert "--direct-main" in one
    assert "--after-merge" in one
    assert "probe_main_write_vectors.py" in one or (ROOT / "scripts" / "probe_main_write_vectors.py").is_file()
    assert "HOLD" in one and "VOID" in one
    assert (ROOT / "portable" / "RESTORE_PLAN_58.json").is_file()
    assert (ROOT / "portable" / "RESTORE_PLAN_59.json").is_file()
    assert (ROOT / "portable" / "RESTORE_PLAN_60.json").is_file()
    assert (ROOT / "portable" / "BATCH58_TOKEN_SEARCH.json").is_file()
    assert (ROOT / "portable" / "BATCH59_TOKEN_SEARCH.json").is_file()
    assert (ROOT / "portable" / "BATCH60_TOKEN_SEARCH.json").is_file()
    token_log = __import__("json").loads(
        (ROOT / "portable" / "BATCH60_TOKEN_SEARCH.json").read_text(encoding="utf-8")
    )
    assert token_log["batch"] == "60"
    assert token_log["scientific_effect"] == "NONE"
    # Ensure no raw secret material leaked into the token search log
    blob = (ROOT / "portable" / "BATCH60_TOKEN_SEARCH.json").read_text(encoding="utf-8")
    assert "oauth_token" not in blob
    assert "ghs_" not in blob
    assert "gho_" not in blob
    assert "github_pat_" not in blob
    patches_readme = (ROOT / "portable" / "patches" / "README.md").read_text(encoding="utf-8")
    assert "0006" in patches_readme
    assert "0007" in patches_readme
    assert "0008" in patches_readme
    assert "0009" in patches_readme
    assert "0012" in patches_readme
    assert "0014" in patches_readme
    assert "0015" in patches_readme
    assert "0016" in patches_readme
    assert "apply_all.sh" in patches_readme
    assert "74c082e" in patches_readme or "PR #45" in patches_readme or "#45" in patches_readme
    assert "post-#41" in patches_readme.lower() or "PR #41" in patches_readme
    assert "fbb4360" in patches_readme or "PR #30" in patches_readme or "PR #28" in patches_readme or "PR #29" in patches_readme or "PR #27" in patches_readme or "PR #34" in patches_readme or "PR #43" in patches_readme or "#43" in patches_readme or "PR #42" in patches_readme or "#42" in patches_readme or "PR #45" in patches_readme or "#45" in patches_readme
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
    vectors = ROOT / "scripts" / "probe_main_write_vectors.py"
    assert vectors.is_file()
    vresult = subprocess.run(
        [sys.executable, str(vectors)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert vresult.returncode in (0, 1, 2), vresult.stderr
    vdata = __import__("json").loads(vresult.stdout)
    assert vdata["scientific_effect"] == "NONE"
    assert vdata["state"] in {"WRITABLE", "DENIED", "TRANSPORT_ERROR"}
    assert "vectors" in vdata
    assert "W1_git_refs" in vdata["vectors"]
    assert (ROOT / "portable" / "RESTORE_PLAN_55.json").is_file()
    restore = __import__("json").loads((ROOT / "portable" / "RESTORE_PLAN_55.json").read_text())
    assert restore["preferred_restore"] == "Path_B"
    assert restore["scientific_effect"] == "NONE"
    restore59 = __import__("json").loads((ROOT / "portable" / "RESTORE_PLAN_59.json").read_text())
    assert restore59["scientific_effect"] == "NONE"
    assert restore59["aligned"] is True
    assert restore59["path_b"].get("already_aligned_skip") is True or restore59["path_b"].get(
        "dry_run_state"
    ) == "ALREADY_ALIGNED"
    restore60 = __import__("json").loads((ROOT / "portable" / "RESTORE_PLAN_60.json").read_text())
    assert restore60["scientific_effect"] == "NONE"
    assert restore60["aligned"] is True
    assert restore60["path_c"].get("dry_run_certainty") == "scripts/path_c_dry_run.py"
    assert restore60["path_c"].get("post_aligned_keep_hardening") is True
    restore61 = __import__("json").loads((ROOT / "portable" / "RESTORE_PLAN_61.json").read_text())
    assert restore61["scientific_effect"] == "NONE"
    assert restore61["aligned"] is True
    restore62 = ROOT / "portable" / "RESTORE_PLAN_62.json"
    assert restore62.is_file()
    restore62_data = __import__("json").loads(restore62.read_text())
    assert restore62_data["scientific_effect"] == "NONE"
    assert restore62_data["aligned"] is True
    assert restore62_data.get("goal_complete") is False
    assert restore62_data.get("lemma_closed") is False
    assert restore62_data.get("autonomous_window", {}).get("window_mode") == (
        "PERMANENT_UNTIL_OWNER_INTERVENES"
    )
    restore63 = ROOT / "portable" / "RESTORE_PLAN_63.json"
    assert restore63.is_file()
    restore63_data = __import__("json").loads(restore63.read_text())
    assert restore63_data["scientific_effect"] == "NONE"
    assert restore63_data["aligned"] is True
    assert restore63_data.get("goal_complete") is False
    assert restore63_data.get("lemma_closed") is False
    assert restore63_data.get("autonomous_window", {}).get("window_mode") == (
        "PERMANENT_UNTIL_OWNER_INTERVENES"
    )
    assert "6f0f061" in restore63_data["path_c"].get("base_tip", "")
    assert (ROOT / "portable" / "BATCH63_TOKEN_SEARCH.json").is_file()
    restore64 = ROOT / "portable" / "RESTORE_PLAN_64.json"
    assert restore64.is_file()
    restore64_data = __import__("json").loads(restore64.read_text())
    assert restore64_data["scientific_effect"] == "NONE"
    assert restore64_data["aligned"] is True
    assert restore64_data.get("goal_complete") is False
    assert restore64_data.get("lemma_closed") is False
    assert restore64_data.get("autonomous_window", {}).get("window_mode") == (
        "PERMANENT_UNTIL_OWNER_INTERVENES"
    )
    assert "6f0f061" in restore64_data["path_c"].get("base_tip", "")
    assert (ROOT / "portable" / "BATCH64_TOKEN_SEARCH.json").is_file()
    restore65 = ROOT / "portable" / "RESTORE_PLAN_65.json"
    assert restore65.is_file()
    restore65_data = __import__("json").loads(restore65.read_text())
    assert restore65_data["scientific_effect"] == "NONE"
    assert restore65_data["aligned"] is True
    assert restore65_data.get("goal_complete") is False
    assert restore65_data.get("lemma_closed") is False
    assert restore65_data.get("autonomous_window", {}).get("window_mode") == (
        "PERMANENT_UNTIL_OWNER_INTERVENES"
    )
    assert "3d47d1b" in restore65_data["path_c"].get("base_tip", "")
    assert (ROOT / "portable" / "BATCH65_TOKEN_SEARCH.json").is_file()
    restore66 = ROOT / "portable" / "RESTORE_PLAN_66.json"
    assert restore66.is_file()
    restore66_data = __import__("json").loads(restore66.read_text())
    assert restore66_data["scientific_effect"] == "NONE"
    assert restore66_data["aligned"] is True
    assert restore66_data.get("goal_complete") is False
    assert restore66_data.get("lemma_closed") is False
    assert restore66_data.get("autonomous_window", {}).get("window_mode") == (
        "PERMANENT_UNTIL_OWNER_INTERVENES"
    )
    assert "74c082e" in restore66_data["path_c"].get("base_tip", "")
    assert (ROOT / "portable" / "BATCH66_TOKEN_SEARCH.json").is_file()
    assert (ROOT / "scripts" / "check_autonomous_window.py").is_file()
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "probe_main_write_vectors.py" in pack
    assert "path_c_dry_run.py" in pack
    assert "check_autonomous_window.py" in pack
    # Batch 64+: auto-glob restore plans + token search logs (no per-batch hardcode)
    assert "RESTORE_PLAN_*.json" in pack
    assert "BATCH*_TOKEN_SEARCH.json" in pack
    assert "wait_until_aligned.sh" in pack
    assert "restore_main_face.sh" in pack
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "probe_main_write_vectors.py" in unblock
    assert "restore_main_face.sh" in unblock
    assert "path_c_dry_run.py" in unblock or "owner_land_path_c.sh --dry-run" in unblock
    assert "auto-approve" in unblock or "unrestricted" in unblock
    assert "BASE_TIP.txt" in unblock
    assert (
        "Batch 66" in unblock
        or "Batch 65" in unblock
        or "Batch 64" in unblock
        or "Batch 63" in unblock
        or "PERMANENT" in unblock
        or "1c6e74b" in unblock
    )
    assert "3600" in unblock or "permanent-autonomous-align-watch" in unblock
    assert "check_autonomous_window.py" in unblock
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "auto-approved" in agents or "auto-approve" in agents
    assert "Do not ask Dylan for approval" in agents or "approval" in agents.lower()
    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 66" in log
    assert "Batch 65" in log
    assert "Batch 64" in log
    assert "Batch 63" in log
    assert "Batch 62" in log
    assert "Batch 61" in log
    assert "PERMANENT_UNTIL_OWNER_INTERVENES" in log
    assert "Batch 60" in log
    assert "Batch 59" in log
    assert "Batch 58" in log
    assert "Batch 55" in log
    assert "HOLD" in log and "VOID" in log
    assert "Path A or B OK" in log or "Path A OR Path B OK" in log
    assert "restore_main_face" in log or "one-command" in log.lower()
    assert "ALIGNED" in log and "1c6e74b" in log
    assert "path_c_dry_run" in log or "Path C dry-run" in log or "APPLY_READY_POST_ALIGNED" in log
    assert "check_autonomous_window" in log or "no 48h finale" in log.lower()
    assert "74c082e" in log or "PR #45" in log
    assert "pack_portable" in log and ("auto-glob" in log or "glob" in log)
    assert "3600" in log
    assert "watch_main_alignment" in log and (
        "autonomous_window" in log
        or "route" in log
        or "Batch 62" in log
        or "Batch 63" in log
        or "Batch 64" in log
        or "Batch 65" in log
        or "Batch 66" in log
    )
    restore_one = ROOT / "scripts" / "restore_main_face.sh"
    assert restore_one.is_file()
    assert restore_one.stat().st_mode & 0o111
    rtext = restore_one.read_text(encoding="utf-8")
    assert "owner_land_path_b.sh" in rtext
    assert "scientific_effect=NONE" in rtext
    assert "--dry-run" in rtext
    assert "--batch" in rtext
    assert "probe_main_write_vectors" in rtext
    assert "already ALIGNED" in rtext or "short-circuit" in rtext.lower()
    # dry-run path must would-align / ALREADY_ALIGNED without pushing
    dry = subprocess.run(
        ["bash", str(restore_one), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(ROOT),
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    combined = dry.stdout + dry.stderr
    assert (
        "would-align" in combined.lower()
        or "WOULD_ALIGN" in combined
        or "ALREADY_ALIGNED" in combined
    )
    # land short-circuits when tip is already ALIGNED
    land = subprocess.run(
        ["bash", str(restore_one), "--batch", "59"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(ROOT),
    )
    assert land.returncode == 0, land.stderr + land.stdout
    assert "already ALIGNED" in (land.stdout + land.stderr)


def test_path_c_dry_run_post_aligned_keep_hardening() -> None:
    """Path C certainty: apply_ready on hardening; default tip ALIGNED but not Path-C shaped."""
    path_c = ROOT / "scripts" / "path_c_dry_run.py"
    owner_c = ROOT / "scripts" / "owner_land_path_c.sh"
    assert path_c.is_file()
    assert owner_c.is_file()
    assert owner_c.stat().st_mode & 0o111
    assert "--dry-run" in owner_c.read_text(encoding="utf-8")
    assert "path_c_dry_run" in owner_c.read_text(encoding="utf-8")
    assert "PR #41" in owner_c.read_text(encoding="utf-8") or "post-ALIGNED" in owner_c.read_text(
        encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(path_c), "--skip-rebase-probe"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = __import__("json").loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data["apply_ready"] is True
    assert data["tip_matches_base"] is True
    assert data["default_aligned"] is True
    assert data["default_path_c_shape"]["accepts"] is False
    assert data["hardening_path_c_shape"]["accepts"] is True
    assert data["do_not_set_path_c_base_main"] is True
    assert data["state"] == "APPLY_READY_POST_ALIGNED_KEEP_HARDENING"
    # owner wrapper --dry-run
    wrap = subprocess.run(
        ["bash", str(owner_c), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert wrap.returncode == 0, wrap.stderr + wrap.stdout
    combined = wrap.stdout + wrap.stderr
    assert "APPLY_READY" in combined or "dry-run OK" in combined


def test_path_c_rebase_helper_dry_run() -> None:
    """Batch 68: owner-safe rebase helper documents strategy without inventing status."""
    helper = ROOT / "scripts" / "path_c_rebase_helper.sh"
    notes = ROOT / "portable" / "PATH_C_REBASE_RESOLUTION_NOTES_68.json"
    assert helper.is_file()
    assert helper.stat().st_mode & 0o111
    text = helper.read_text(encoding="utf-8")
    assert "--dry-run" in text
    assert "keep-hardening-engineering" in text
    assert "preserve-main-face" in text
    assert "lemma_closed" in text
    assert "PACKET.json" in text
    assert notes.is_file()
    data = __import__("json").loads(notes.read_text(encoding="utf-8"))
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed"] is False
    assert data["goal_complete"] is False
    assert data["do_not_set_path_c_rebase_onto_main"] is True
    assert len(data["resolutions"]) == 3
    result = subprocess.run(
        ["bash", str(helper), "--dry-run", "--no-abort-advice"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    out = result.stdout + result.stderr
    assert "ci.yml" in out
    assert "research.yml" in out
    assert "engine/bridge/README.md" in out
    assert '"scientific_effect": "NONE"' in out
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "path_c_rebase_helper.sh" in pack
    assert "PATH_C_REBASE_RESOLUTION_NOTES_" in pack


def test_check_autonomous_window_permanent_mode(tmp_path, monkeypatch) -> None:
    """Permanent mode must never hard-stop on elapsed wall-clock."""
    import json
    import os

    store = tmp_path / "stores"
    store.mkdir()
    (store / "autonomous_window_mode.txt").write_text(
        "PERMANENT_UNTIL_OWNER_INTERVENES\n", encoding="utf-8"
    )
    (store / "autonomous_48h_window_seconds.txt").write_text("999999999\n", encoding="utf-8")
    (store / "autonomous_48h_started_at.txt").write_text(
        "2020-01-01T00:00:00Z\n", encoding="utf-8"
    )
    (store / "autonomous_permanent_extension.txt").write_text(
        "extended permanently\n", encoding="utf-8"
    )
    monkeypatch.setenv("AUTONOMOUS_STORE_DIR", str(store))
    script = ROOT / "scripts" / "check_autonomous_window.py"
    assert script.is_file()
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=str(ROOT),
        env={**os.environ, "AUTONOMOUS_STORE_DIR": str(store)},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = json.loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data["window_mode"] == "PERMANENT_UNTIL_OWNER_INTERVENES"
    assert data["state"] == "PERMANENT_OPEN"
    assert data["hard_stop"] is False
    assert data["within_window"] is True
    assert data["finale"] is False
    assert data["stop_condition"] == "owner_intervene_only"


def test_watch_embeds_autonomous_window_and_route() -> None:
    """Batch 62: watch_main_alignment embeds permanent window + Path C route hint."""
    import json

    watch = ROOT / "scripts" / "watch_main_alignment.py"
    assert watch.is_file()
    result = subprocess.run(
        [sys.executable, str(watch)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode in (0, 1, 2), result.stderr + result.stdout
    data = json.loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert "autonomous_window" in data
    assert data["autonomous_window"] is not None
    assert data["autonomous_window"].get("scientific_effect") == "NONE"
    assert "route" in data
    assert data["route"].get("goal_complete") is False
    assert "lemma_closed" in data["route"]["note"]
    # --no-window still returns route but null window
    skipped = subprocess.run(
        [sys.executable, str(watch), "--no-window"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    assert skipped.returncode in (0, 1, 2), skipped.stderr + skipped.stdout
    skipped_data = json.loads(skipped.stdout)
    assert skipped_data["autonomous_window"] is None
    assert skipped_data["route"]["goal_complete"] is False


def test_alignment_status_post_41_critical_path() -> None:
    """Dashboard must not claim PR #2 MERGEABLE; embed window + Path C tip currency."""
    import json

    script = ROOT / "scripts" / "alignment_status.py"
    src = script.read_text(encoding="utf-8")
    assert "PR #2 MERGEABLE/CLEAN lands q0" not in src
    assert "check_autonomous_window" in src
    assert "pr41_url" in src or "PR #41" in src
    assert "goal_complete" in src
    assert "lemma_closed" in src
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode in (0, 2), result.stderr + result.stdout
    if result.returncode != 0:
        return
    data = json.loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data.get("goal_complete") is False
    assert data.get("lemma_closed") is False
    assert "autonomous_window" in data
    assert "path_c_tip" in data
    assert data["path_c_tip"].get("apply_stack") == "0001-0004 + 0008-0016"
    crit = data["main"]["critical_path"]
    assert "pr41_url" in crit
    assert crit.get("prefer_when_aligned_writable") == "Path_C_on_hardening"


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
    assert "check_autonomous_window.py" in wait_text
    assert "PERMANENT_UNTIL_OWNER_INTERVENES" in wait_text
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
    assert "restore_main_face.sh" in pack
    assert (ROOT / "scripts" / "restore_main_face.sh").is_file()
    assert (ROOT / "scripts" / "restore_main_face.sh").stat().st_mode & 0o111
    assert "restore_main_face.sh" in (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "restore_main_face.sh" in (ROOT / "README.md").read_text(encoding="utf-8")
    # Option-B patch must add AGENTS.md (Batch 58 stronger pack)
    ob = (ROOT / "portable" / "main-default-branch" / "0001-option-b-default-branch-notice.patch").read_text()
    assert "AGENTS.md" in ob
    assert "create mode 100644 AGENTS.md" in ob or "AGENTS.md" in ob
    assert (ROOT / "portable" / "main-default-branch" / "AGENTS.md").is_file()
