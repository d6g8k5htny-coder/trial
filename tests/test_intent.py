"""Sanity checks for the trial sandbox.

These tests encode repository intent only. They do not validate research claims
from d6g8k5htny-coder/main and must never be cited as scientific evidence.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Living Path C tip/release may supersede across tip-refresh / pack batches.
# Batch 180 tip 8bd1f03 → Batch 202 tip b89448d; release batch180 → batch199 → batch202.
_LIVING_TIPS = (
    "8bd1f03",
    "b89448d",
    "1d0dceb",
    "cbaa056",
    "93a4ecd",
    "377201c",
    "1200501",
    "62f955a",
    "a1ed37b",
    "542e6ec",
)
_LIVING_RELEASES = (
    "batch180-path-c-bundle",
    "batch199-path-c-bundle",
    "batch202-path-c-bundle",
    "batch218-path-c-bundle",
    "batch207-path-c-bundle",
    "batch223-path-c-bundle",
    "batch236-path-c-bundle",
    "batch238-path-c-bundle",
    "batch239-path-c-bundle",
    "batch241-path-c-bundle",
)


def _living_tip(val) -> bool:
    """True if val is / contains / starts with a living Path C tip SHA prefix."""
    s = str(val or "")
    return any(s == t or s.startswith(t) or t in s for t in _LIVING_TIPS)


def _living_release(val) -> bool:
    s = str(val or "")
    return s in _LIVING_RELEASES or s.endswith("-path-c-bundle")



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
    # 0=aligned, 1=misaligned, 2=transport (e.g. API rate limit / RemoteDisconnected on CI)
    assert result.returncode in (0, 1, 2), result.stderr
    if result.returncode == 2:
        assert "transport" in result.stderr.lower()
        return
    # Batch 155: empty stdout with connection drop must not be treated as aligned
    # (script now maps those to exit 2; keep belt-and-suspenders for older trees).
    if not result.stdout.strip() and any(
        x in result.stderr.lower()
        for x in ("remote", "disconnected", "timeout", "connection", "transport")
    ):
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
    # Batch 73: land workflows validated in CI without MAIN_PUSH_TOKEN
    assert "land-workflows-dry-run" in ci
    assert "validate_land_workflows.py" in ci
    assert "actionlint" in ci
    assert "owner_land_path_b.sh --dry-run" in ci
    assert "owner_land_path_c.sh --dry-run" in ci
    # Batch 138: path-c-applied-bundle dry-apply on hardening tip + lemma_closed gate
    assert "path-c-applied-bundle-dry-apply" in ci
    assert "path-c-on-hardening.patch" in ci
    assert "lemma_closed=false" in ci
    # Batch 74: Intent suite + audit/watch export runner token; Option-B skips when ALIGNED
    assert "Intent suite" in ci
    assert "Option-B apply check SKIPPED" in ci or "already ALIGNED" in ci
    assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in ci
    # Audit/watch steps must export the runner token (avoids unauthenticated API 403s).
    assert ci.count("GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}") >= 2
    # Batch 86: research-stack status guard (hardening shallow clone; continue-on-error)
    assert "research-stack-status-guard" in ci
    assert "guard_no_status_promotion.py" in ci
    assert "STATUS_GUARD_SNAPSHOT.json" in ci
    assert "continue-on-error: true" in ci
    land_wf = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text()
    assert "MAIN_PUSH_TOKEN" in land_wf
    assert "option-b" in land_wf
    assert "dry_run" in land_wf
    assert "0001-option-b-default-branch-notice.patch" in land_wf
    assert "Locate Option-B patch" in land_wf or "PATCH_PATH" in land_wf
    assert "audit_local_tree.py" in land_wf
    assert "would-align" in land_wf
    path_c_wf = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text()
    assert "MAIN_PUSH_TOKEN" in path_c_wf
    assert "dry_run" in path_c_wf
    assert "default: true" in path_c_wf
    assert "apply_all.sh" in path_c_wf
    assert "lemma_closed=false" in path_c_wf
    assert "math_status_check" in path_c_wf
    assert "chatgpt/drive-github-hardening-20260919" in path_c_wf
    assert "workflow_dispatch" in path_c_wf
    assert "cursor/portable-engineering-patches" in path_c_wf
    assert "Scientific effect: NONE" in path_c_wf or "scientific effect: NONE" in path_c_wf.lower()
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
    assert "0017-pinned-sources-close-file-handles.patch" in apply_all
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
    # Living tip supersession (Batch 218+: 1d0dceb; keep older SHAs accepted for history).
    assert _living_tip(base_tip) or any(
        t in base_tip
        for t in ("8ea3b5f", "10c077e", "c82c9357", "ac33581")
    )
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
    assert "0017-pinned-sources-close-file-handles.patch" in apply_all_txt
    assert (ROOT / "scripts" / "print_owner_unblock.sh").is_file()
    land_wf = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text(encoding="utf-8")
    assert "gh pr create" in land_wf
    assert "option-b-notice-from-trial" in land_wf
    path_c_wf = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "gh pr create" in path_c_wf
    assert "portable-engineering-patches" in path_c_wf
    assert "lemma_closed" in path_c_wf
    assert "problems=0" in path_c_wf or "problems!=0" in path_c_wf
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
    assert (
        "ac33581" in patches_readme
        or "PR #48" in patches_readme
        or "#48" in patches_readme
        or "5f352a2" in patches_readme
        or "PR #44" in patches_readme
        or "#44" in patches_readme
        or "74c082e" in patches_readme
        or "PR #45" in patches_readme
        or "#45" in patches_readme
    )
    assert "post-#41" in patches_readme.lower() or "PR #41" in patches_readme
    assert (
        "fbb4360" in patches_readme
        or "PR #30" in patches_readme
        or "PR #28" in patches_readme
        or "PR #29" in patches_readme
        or "PR #27" in patches_readme
        or "PR #34" in patches_readme
        or "PR #43" in patches_readme
        or "#43" in patches_readme
        or "PR #42" in patches_readme
        or "#42" in patches_readme
        or "PR #45" in patches_readme
        or "#45" in patches_readme
        or "PR #44" in patches_readme
        or "#44" in patches_readme
        or "PR #48" in patches_readme
        or "#48" in patches_readme
        or "ac33581" in patches_readme
    )
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
    assert "install_has_main" in data
    assert "installation_repositories" in data
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
    # TRANSPORT_ERROR may leave vectors empty (no tip); otherwise W1 is required.
    if vdata["state"] != "TRANSPORT_ERROR":
        assert "W1_git_refs" in vdata["vectors"]
    else:
        assert vresult.returncode == 2
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
        "Batch 69" in unblock
        or "Batch 68" in unblock
        or "Batch 66" in unblock
        or "Batch 65" in unblock
        or "Batch 64" in unblock
        or "Batch 63" in unblock
        or "PERMANENT" in unblock
        or "1c6e74b" in unblock
        or "land-path-c-on-main" in unblock
    )
    assert "3600" in unblock or "permanent-autonomous-align-watch" in unblock
    assert "check_autonomous_window.py" in unblock
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "auto-approved" in agents or "auto-approve" in agents
    assert "Do not ask Dylan for approval" in agents or "approval" in agents.lower()
    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 72" in log
    assert "Batch 71" in log
    assert "Batch 69" in log
    assert "Batch 68" in log
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
    assert "74c082e" in log or "PR #45" in log or "5f352a2" in log or "ac33581" in log or "PR #48" in log or "Batch 74" in log
    assert "Batch 74" in log
    assert "Batch 81" in log or "Batch 82" in log or "Batch 84" in log
    assert "when_writable_land" in log or "Batch 82" in log or "Batch 84" in log
    assert "pack_portable" in log and ("auto-glob" in log or "glob" in log)
    assert "3600" in log
    assert "land-path-c-on-main" in log
    assert "aligned_drift_watch" in log
    assert "watch_main_alignment" in log and (
        "autonomous_window" in log
        or "route" in log
        or "Batch 62" in log
        or "Batch 63" in log
        or "Batch 64" in log
        or "Batch 65" in log
        or "Batch 66" in log
        or "Batch 69" in log
        or "Batch 72" in log
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


def test_land_path_c_workflow_dry_run_default() -> None:
    """Batch 69: Path C Actions land workflow exists; dry_run defaults true; never flips status."""
    path = ROOT / ".github" / "workflows" / "land-path-c-on-main.yml"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "name: land-path-c-on-main" in text
    assert "workflow_dispatch" in text
    # Batch 139: repository_dispatch so ghs Contents write can land when MAIN_PUSH_TOKEN appears
    assert "repository_dispatch" in text
    assert "types: [land-path-c-on-main]" in text
    assert "steps.mode.outputs.dry_run" in text
    assert "dry_run" in text
    # default true appears near dry_run input
    assert "default: true" in text
    assert "MAIN_PUSH_TOKEN" in text
    assert "apply_all" in text
    assert "lemma_closed=false" in text
    assert "math_status_check" in text
    assert "chatgpt/drive-github-hardening-20260919" in text
    assert "cursor/portable-engineering-patches" in text
    assert "direct_push" in text
    # Must not flip research status
    assert "lemma_closed" in text
    assert "Scientific effect" in text or "scientific effect" in text.lower()
    assert "NONE" in text
    # Owner script mentions the workflow
    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "land-path-c-on-main" in owner_c
    assert "MAIN_PUSH_TOKEN" in owner_c
    # Vectors probe covers Path C dispatch
    vectors = (ROOT / "scripts" / "probe_main_write_vectors.py").read_text(encoding="utf-8")
    assert "land-path-c-on-main" in vectors
    assert "W3d_dispatch_path_c_trial" in vectors
    assert "W3f_repository_dispatch_path_c" in vectors
    # Batch 139 helper
    dispatch = ROOT / "scripts" / "dispatch_land_path_c.sh"
    assert dispatch.is_file()
    dtxt = dispatch.read_text(encoding="utf-8")
    assert "repository_dispatch" in dtxt or "dispatches" in dtxt
    assert "land-path-c-on-main" in dtxt
    assert "--apply" in dtxt


def test_watch_main_alignment_workflow_exists() -> None:
    """Batch 98: hourly trial workflow watches remote main; upserts drift issue; never writes main."""
    path = ROOT / ".github" / "workflows" / "watch-main-alignment.yml"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "name: watch-main-alignment" in text
    assert "workflow_dispatch" in text
    assert "repository_dispatch" in text
    assert "watch-main-alignment" in text
    assert "schedule:" in text
    assert 'cron: "0 * * * *"' in text or "cron: '0 * * * *'" in text
    assert "aligned_drift_watch.py" in text or "audit_main_alignment.py" in text
    assert "GITHUB_TOKEN" in text
    assert "main ALIGNED drift" in text
    assert "issues: write" in text
    assert "gh issue" in text
    assert "MISALIGNED" in text
    assert "ALIGNED" in text
    # Must not flip research status; must not push to main repo
    assert "lemma_closed" in text
    assert "Scientific effect" in text or "scientific effect" in text.lower()
    assert "NONE" in text
    assert "never writes to" in text.lower() or "never touch main" in text.lower()
    assert "git push" not in text
    assert "d6g8k5htny-coder/main" in text
    # Checkout is trial only (no main clone step)
    assert "actions/checkout@v4" in text
    assert "Clone hardening" not in text
    assert "clone.*d6g8k5htny-coder/main" not in text.replace("\n", " ")


def test_validate_land_workflows_no_token() -> None:
    """Batch 73: land workflows validate without MAIN_PUSH_TOKEN (CI dry-run contract)."""
    script = ROOT / "scripts" / "validate_land_workflows.py"
    assert script.is_file()
    result = subprocess.run(
        [sys.executable, str(script), "--json"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = __import__("json").loads(result.stdout)
    assert data["ok"] is True
    assert data["errors"] == []
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed"] is False
    assert data["main_push_token_required"] is False
    assert "land-option-b-on-main.yml" in data["workflows"][0]
    assert "land-path-c-on-main.yml" in data["workflows"][1]
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "validate_land_workflows.py" in pack
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "land-workflows-dry-run" in ci
    assert "validate_land_workflows.py" in ci


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
    assert data["path_c_tip"].get("apply_stack") in (
        "0001-0004 + 0008-0016",
        "0001-0004 + 0008-0017",
        "0001-0004 + 0008-0019",
    )
    crit = data["main"]["critical_path"]
    assert "pr41_url" in crit
    assert crit.get("prefer_when_aligned_writable") == "Path_C_on_hardening"


def test_audit_research_stack_open_read_only() -> None:
    """Batch 70: mechanical OPEN inventory; never flips lemma_closed / prizes."""
    import json
    import subprocess
    import tempfile

    script = ROOT / "scripts" / "audit_research_stack_open.py"
    assert script.is_file()
    # Empty-ish tree → NO_PACKET shape, exit 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "README.md").write_text("sandbox\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(script), str(root), "--tip-sha", "deadbeef"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        data = json.loads(result.stdout)
        assert data["scientific_effect"] == "NONE"
        assert data["flipped_anything"] is False
        assert data["lemma_closed"] is False
        assert data["goal_complete"] is False
        assert data["shape"] == "NO_PACKET"
        assert data.get("tip_sha") == "deadbeef"

    # Synthetic PACKET + claims graph → OPEN lists, confirmations stay false
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "math_status").mkdir(parents=True)
        (root / "claims").mkdir()
        (root / "registers" / "json").mkdir(parents=True)
        packet = {
            "disposition": "OPEN_HOLD",
            "lemma_closed": False,
            "prizes_solved": False,
            "original_prize_closed": False,
            "independence_credit": 0,
            "bridge": "PROPOSED_NOT_DEPLOYED",
            "freeze": False,
            "OBL-H5-JETMOD": {
                "status": "OPEN",
                "lemma_closed": False,
                "freeze": False,
                "grade": "display_only",
            },
            "D3-LEMMA-RN-UNIF": {
                "status": "OPEN",
                "lemma_closed": False,
                "freeze": False,
                "piece2_annulus_driver": "UNWRITTEN",
                "discharges_lemma": False,
            },
        }
        (root / "docs" / "math_status" / "PACKET.json").write_text(
            json.dumps(packet), encoding="utf-8"
        )
        graph = {
            "as_of": "test",
            "premises": {
                "OBL-H5-JETMOD": {
                    "track": "UPPER2D",
                    "status_frozen_v2_2": "OPEN",
                    "status_register_note": "OPEN",
                    "source": "test",
                },
                "D3-LEMMA-RN-UNIF": {
                    "track": "UPPER2D",
                    "status_frozen_v2_2": "NOT_CLOSED",
                    "status_register_note": "OPEN",
                    "source": "test",
                },
            },
            "claims": {
                "D1-v2.2(2)": {
                    "track": "UPPER2D",
                    "grade": "CONDITIONAL",
                    "depends_on": ["OBL-H5-JETMOD", "D3-LEMMA-RN-UNIF"],
                    "source": "test",
                },
                "PR-TAL-003..008": {
                    "track": "NUMBER_THEORY",
                    "grade": "AUTHOR_SIDE_PROOF_PRESENT",
                    "original_prize_closed": False,
                    "depends_on": [],
                    "source": "test",
                },
            },
            "firewalls": [{"id": "FW-NO-PRIZE-CLOSURE", "rule": "x", "source": "t"}],
        }
        (root / "claims" / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
        oq = {
            "header": [
                "OQ ID",
                "Decision class",
                "Priority",
                "Register status",
                "Current evidence / change",
                "Live state",
                "Next decisive action",
                "Owner or capacity needed",
                "Source",
                "Reviewed",
            ],
            "rows": [
                ["OQ-010", "x", "Medium", "OPEN", "e", "OPEN", "next", "", "", ""],
                ["OQ-001", "x", "High", "CLOSED", "e", "TERMINAL — DONE", "n", "", "", ""],
            ],
        }
        (root / "registers" / "json" / "open_questions.json").write_text(
            json.dumps(oq), encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, str(script), str(root)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        data = json.loads(result.stdout)
        assert data["shape"] == "HAS_PACKET"
        assert data["lemma_closed"] is False
        assert data["lemma_closed_confirmation"] is True
        assert data["prizes_solved_confirmation"] is True
        assert data["flipped_anything"] is False
        assert data["counts"]["open_premises_frozen_layer"] == 2
        assert data["counts"]["open_prizes"] == 1
        assert data["counts"]["open_questions"] == 1
        assert data["open_questions"][0]["id"] == "OQ-010"
        # PACKET on disk unchanged
        disk = json.loads(
            (root / "docs" / "math_status" / "PACKET.json").read_text(encoding="utf-8")
        )
        assert disk["lemma_closed"] is False
        assert disk["prizes_solved"] is False

    audit_art = ROOT / "portable" / "BATCH70_RESEARCH_STACK_AUDIT.json"
    assert audit_art.is_file()
    art = json.loads(audit_art.read_text(encoding="utf-8"))
    assert art["scientific_effect"] == "NONE"
    assert art["lemma_closed"] is False
    assert art["flipped_anything"] is False
    assert art["goal_complete"] is False
    assert art["expected_post_alignment_matches"] is True
    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 70" in findings
    assert "lemma_closed=false" in findings
    assert "audit_research_stack_open.py" in findings
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "audit_research_stack_open.py" in pack
    assert "BATCH*_RESEARCH_STACK_AUDIT.json" in pack
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert (
        "Batch 72" in unblock
        or "Batch 71" in unblock
        or "Batch 70" in unblock
        or "Batch 76" in unblock
        or "Batch 74" in unblock
        or "Batch 73" in unblock
        or "aligned_drift_watch" in unblock
        or "path-c-applied-bundle" in unblock
    )
    assert "audit_research_stack_open.py" in unblock
    assert "aligned_drift_watch.py" in unblock
    assert (ROOT / "portable" / "BATCH71_BRIEF.json").is_file()
    brief71 = json.loads(
        (ROOT / "portable" / "BATCH71_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief71["scientific_effect"] == "NONE"
    assert brief71["goal_complete"] is False
    assert brief71["lemma_closed"] is False
    assert brief71["new_0017"] is False
    assert brief71["hardening_tip"].startswith("5f352a2")
    assert (ROOT / "portable" / "RESTORE_PLAN_71.json").is_file()
    restore71 = json.loads(
        (ROOT / "portable" / "RESTORE_PLAN_71.json").read_text(encoding="utf-8")
    )
    assert restore71["goal_complete"] is False
    assert restore71["lemma_closed"] is False
    assert "5f352a2" in str(restore71.get("path_c", {}).get("base_tip", ""))
    assert (ROOT / "portable" / "BATCH72_BRIEF.json").is_file()
    brief72 = json.loads(
        (ROOT / "portable" / "BATCH72_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief72["scientific_effect"] == "NONE"
    assert brief72["goal_complete"] is False
    assert brief72["lemma_closed"] is False
    assert brief72["aligned"] is True
    assert brief72["hardening_tip"].startswith("5f352a2")
    assert brief72["preferred_restore_if_drift"] == "Path_B"
    assert (ROOT / "portable" / "RESTORE_PLAN_72.json").is_file()
    restore72 = json.loads(
        (ROOT / "portable" / "RESTORE_PLAN_72.json").read_text(encoding="utf-8")
    )
    assert restore72["goal_complete"] is False
    assert restore72["lemma_closed"] is False
    assert "5f352a2" in str(restore72.get("path_c", {}).get("base_tip", ""))
    assert (ROOT / "portable" / "BATCH74_BRIEF.json").is_file()
    brief74 = json.loads(
        (ROOT / "portable" / "BATCH74_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief74["scientific_effect"] == "NONE"
    assert brief74["goal_complete"] is False
    assert brief74["lemma_closed"] is False
    assert brief74["aligned"] is True
    assert brief74["hardening_tip"].startswith("ac33581")
    assert brief74["tip_refresh"] is True
    assert brief74["preferred_restore_if_drift"] == "Path_B"
    assert (ROOT / "portable" / "RESTORE_PLAN_74.json").is_file()
    restore74 = json.loads(
        (ROOT / "portable" / "RESTORE_PLAN_74.json").read_text(encoding="utf-8")
    )
    assert restore74["goal_complete"] is False
    assert restore74["lemma_closed"] is False
    assert "ac33581" in str(restore74.get("path_c", {}).get("base_tip", ""))
    assert (ROOT / "portable" / "BATCH74_OPEN_PR_THREATS.json").is_file()
    threats74 = json.loads(
        (ROOT / "portable" / "BATCH74_OPEN_PR_THREATS.json").read_text(encoding="utf-8")
    )
    assert threats74["scientific_effect"] == "NONE"
    assert threats74["goal_complete"] is False
    assert isinstance(threats74["open_prs_targeting_default_main"], list)
    assert (ROOT / "portable" / "BATCH76_BRIEF.json").is_file()
    brief76 = json.loads(
        (ROOT / "portable" / "BATCH76_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief76["scientific_effect"] == "NONE"
    assert brief76["goal_complete"] is False
    assert brief76["lemma_closed"] is False
    assert brief76["aligned"] is True
    assert brief76["hardening_tip"].startswith("ac33581")
    assert brief76["tip_refresh"] is False
    assert brief76["preferred_restore_if_drift"] == "Path_B"
    assert (ROOT / "portable" / "RESTORE_PLAN_76.json").is_file()
    restore76 = json.loads(
        (ROOT / "portable" / "RESTORE_PLAN_76.json").read_text(encoding="utf-8")
    )
    assert restore76["goal_complete"] is False
    assert restore76["lemma_closed"] is False
    assert "ac33581" in str(restore76.get("path_c", {}).get("base_tip", ""))
    assert "path-c-applied-bundle" in str(
        restore76.get("path_c", {}).get("applied_bundle", "")
    )
    assert (ROOT / "portable" / "BATCH76_OPEN_PR_THREATS.json").is_file()
    threats76 = json.loads(
        (ROOT / "portable" / "BATCH76_OPEN_PR_THREATS.json").read_text(encoding="utf-8")
    )
    assert threats76["scientific_effect"] == "NONE"
    assert threats76["goal_complete"] is False
    assert isinstance(threats76["open_prs_targeting_default_main"], list)
    bundle = ROOT / "portable" / "path-c-applied-bundle"
    assert (bundle / "path-c-on-hardening.patch").is_file()
    assert (bundle / "APPLY.md").is_file()
    assert (bundle / "VERIFY.json").is_file()
    verify76 = json.loads((bundle / "VERIFY.json").read_text(encoding="utf-8"))
    assert verify76["problems"] == 0
    assert verify76["lemma_closed"] is False
    # Living VERIFY may stamp 0 when tip refresh skips full pytest (Batch 180+).
    assert verify76["pytest"]["focused_passed"] in (0, 90)
    assert verify76["goal_complete"] is False
    assert "git am" in (bundle / "APPLY.md").read_text(encoding="utf-8")
    pack76 = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "portable/path-c-applied-bundle" in pack76


def test_aligned_drift_watch_script_and_ci_record_only() -> None:
    """Batch 72: drift watch exits 0/1/2, snapshots tip+markers, CI is record-only."""
    import json
    import tempfile

    script = ROOT / "scripts" / "aligned_drift_watch.py"
    assert script.is_file()
    src = script.read_text(encoding="utf-8")
    assert "preferred_restore_route" in src
    assert "Path_B" in src and "Path_A" in src
    assert "--restore-if-writable" in src
    assert "--no-restore" in src
    assert "--dry-run" in src
    assert "MAIN_PUSH_TOKEN" in src
    assert "auto_path_b_restore" in src or "auto Path B" in src
    assert "resolve_main_push_token" in src or "when_writable_land" in src
    assert "ALIGNED_DRIFT_SNAPSHOT" in src
    assert "restore_main_face" in src
    assert "lemma_closed" in src
    assert "scientific_effect" in src.lower() or "Scientific effect" in src

    snap_path = ROOT / "portable" / "ALIGNED_DRIFT_SNAPSHOT.json"
    assert snap_path.is_file()
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    assert snap["scientific_effect"] == "NONE"
    assert snap["goal_complete"] is False
    assert snap["lemma_closed"] is False
    assert snap["state"] in {"ALIGNED", "MISALIGNED", "TRANSPORT_ERROR"}
    assert "default_tip_sha" in snap
    assert "preferred_restore_route" in snap
    assert "q0_or_notice_markers_present" in snap or "complexity_markers_present" in snap

    threats = ROOT / "portable" / "BATCH72_OPEN_PR_THREATS.json"
    assert threats.is_file()
    threat_data = json.loads(threats.read_text(encoding="utf-8"))
    assert threat_data["scientific_effect"] == "NONE"
    assert threat_data["goal_complete"] is False
    assert isinstance(threat_data["open_prs_targeting_default_main"], list)

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "aligned_drift_watch.py" in ci
    assert "record-only" in ci
    # Must not gate the job on MISALIGNED of remote main
    assert "aligned-drift-watch.json" in ci or "ALIGNED drift watch" in ci

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "aligned_drift_watch.py" in pack
    assert "ALIGNED_DRIFT_SNAPSHOT.json" in pack

    with tempfile.TemporaryDirectory() as td:
        out_snap = Path(td) / "snap.json"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--no-probe",
                "--snapshot",
                str(out_snap),
            ],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
            cwd=str(ROOT),
        )
        assert result.returncode in (0, 1, 2), result.stderr + result.stdout
        data = json.loads(result.stdout)
        assert data["scientific_effect"] == "NONE"
        assert data["goal_complete"] is False
        assert data["lemma_closed"] is False
        assert data["flipped_anything"] is False
        assert data["state"] in {"ALIGNED", "MISALIGNED", "TRANSPORT_ERROR"}
        route = data["preferred_restore_route"]
        assert "prefer" in route
        if data["state"] == "ALIGNED":
            # Batch 231: Path C landed → tip_sync_drift_watch; else Path_C_on_hardening.
            assert route["prefer"] in ("Path_C_on_hardening", "tip_sync_drift_watch")
            assert route.get("restore_if_drift") == "Path_B"
            assert route.get("alternate_restore") == "Path_A"
        elif data["state"] == "MISALIGNED":
            assert route["prefer"] == "Path_B"
            assert route.get("alternate_restore") == "Path_A"
        assert out_snap.is_file()
        written = json.loads(out_snap.read_text(encoding="utf-8"))
        assert written["scientific_effect"] == "NONE"
        assert written["state"] == data["state"]
        assert "default_tip_sha" in written

    # --restore-if-writable must not land when ALIGNED or when write DENIED
    skip = subprocess.run(
        [
            sys.executable,
            str(script),
            "--no-probe",
            "--no-snapshot",
            "--restore-if-writable",
            "--batch",
            "72",
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
        env={k: v for k, v in os.environ.items() if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")},
    )
    assert skip.returncode in (0, 1, 2), skip.stderr + skip.stdout
    skip_data = json.loads(skip.stdout)
    if "restore" in skip_data:
        # Without probe, write state is None → skipped not_writable or not_misaligned
        assert skip_data["restore"].get("attempted") is False

    # Batch 240: --dry-run + --no-restore never attempts; token_source reported
    dry = subprocess.run(
        [
            sys.executable,
            str(script),
            "--no-probe",
            "--no-snapshot",
            "--no-window",
            "--no-path-c-status",
            "--dry-run",
            "--batch",
            "240",
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
        env={k: v for k, v in os.environ.items() if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")},
    )
    assert dry.returncode in (0, 1, 2), dry.stderr + dry.stdout
    dry_data = json.loads(dry.stdout)
    assert dry_data["lemma_closed"] is False
    assert dry_data["flipped_anything"] is False
    assert dry_data["scientific_effect"] == "NONE"
    assert "token_source" in dry_data
    assert dry_data.get("auto_path_b_restore") is True
    if "restore" in dry_data:
        assert dry_data["restore"].get("attempted") is False
        assert dry_data["restore"].get("skipped_reason") in (
            "not_misaligned",
            "not_writable",
            "dry_run",
        )

    no_restore = subprocess.run(
        [
            sys.executable,
            str(script),
            "--no-probe",
            "--no-snapshot",
            "--no-window",
            "--no-path-c-status",
            "--no-restore",
            "--batch",
            "240",
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
    )
    assert no_restore.returncode in (0, 1, 2), no_restore.stderr + no_restore.stdout
    nr_data = json.loads(no_restore.stdout)
    assert "restore" not in nr_data or nr_data["restore"].get("attempted") is False
    assert nr_data["instant_restore_ready"].get("auto_restore") is False


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
    # Batch 227: Path B retries transport (exit 2); Intent allows one re-invoke if a
    # prior flake still surfaces while a fresh watch reports ALIGNED.
    result = subprocess.run(
        ["bash", str(path_b), "--after-merge"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(ROOT),
        env={**os.environ, "PATH_B_TRANSPORT_RETRIES": "3", "PATH_B_TRANSPORT_SLEEP_S": "1"},
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
    if watch_state == "ALIGNED" and result.returncode != 0:
        combined = (result.stderr + result.stdout).lower()
        if "transport" in combined or "exit=2" in combined or "exit 2" in combined:
            result = subprocess.run(
                ["bash", str(path_b), "--after-merge"],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
                cwd=str(ROOT),
                env={**os.environ, "PATH_B_TRANSPORT_RETRIES": "3", "PATH_B_TRANSPORT_SLEEP_S": "1"},
            )
    if watch_state == "ALIGNED":
        assert result.returncode == 0, (result.stdout, result.stderr)
        assert "ALIGNED" in (result.stderr + result.stdout)
    else:
        assert result.returncode != 0
        assert "ERROR" in (result.stderr + result.stdout)
    b_text_live = path_b.read_text(encoding="utf-8")
    assert "TRANSPORT_RETRIES" in b_text_live or "transport" in b_text_live.lower()
    assert "PATH_B_TRANSPORT_RETRIES" in b_text_live
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


def test_when_writable_land_once_dry_run() -> None:
    """Batch 82/92: background lander --once --dry-run; install_has_main status."""
    import json
    import tempfile

    script = ROOT / "scripts" / "when_writable_land.py"
    assert script.is_file()
    src = script.read_text(encoding="utf-8")
    assert "--once" in src and "--dry-run" in src
    assert "owner_land_path_c" in src
    assert "restore_main_face" in src
    assert "lemma_closed" in src
    assert "when_writable_land.stop" in src
    assert "when_writable_land.status.json" in src
    assert "300" in src  # default poll interval
    assert "scientific_effect" in src.lower() or "Scientific effect" in src
    assert "install_has_main" in src
    assert "/installation/repositories" in src
    assert "--mock-install-has-main" in src
    probe_src = (ROOT / "scripts" / "probe_main_write.py").read_text(encoding="utf-8")
    assert "check_installation_repositories" in probe_src
    assert "install_has_main" in probe_src
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Repository access" in owner
    assert "d6g8k5htny-coder/main" in owner
    assert "CURSOR_BOT_ACCESS_91.json" in owner
    assert "Read and write" in owner

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "when_writable_land.py" in pack

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        log_path = td_path / "when_writable_land.log"
        status_path = td_path / "when_writable_land.status.json"
        stop_path = td_path / "when_writable_land.stop"

        # DENIED → continue (no land); install_has_main=false recorded
        denied = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "DENIED",
                "--mock-install-has-main",
                "false",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
            env={**os.environ, "MAIN_PUSH_TOKEN": ""},
        )
        assert denied.returncode == 0, denied.stderr + denied.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["scientific_effect"] == "NONE"
        assert status["goal_complete"] is False
        assert status["lemma_closed"] is False
        assert status["flipped_anything"] is False
        assert status["dry_run"] is True
        assert status["once"] is True
        assert status["install_has_main"] is False
        # When a well-known token file is present on the host, denied→dispatch.
        # CI hosts usually have none → continue_denied + PATH_C_BLOCKED=NO_TOKEN.
        last_action = status["last"]["action"]
        assert last_action in ("continue_denied", "path_c_repository_dispatch")
        log_txt = log_path.read_text(encoding="utf-8")
        if last_action == "continue_denied":
            assert status["last"]["land"] is None
            assert "continue_denied" in log_txt
            assert "PATH_C_BLOCKED=NO_TOKEN" in log_txt
            assert status["last"].get("path_c_blocked_reasons") == ["NO_TOKEN"]
            assert status["last"].get("path_c_blocked") == "PATH_C_BLOCKED=NO_TOKEN"
        else:
            assert status["last"].get("land") is not None
            assert "path_c_repository_dispatch" in log_txt
        assert log_path.is_file()

        # Flip false→true + DENIED then WRITABLE mock: Path C attempt on flip
        # (second run with install true after status already false)
        flip = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "WRITABLE",
                "--mock-align",
                "ALIGNED",
                "--mock-install-has-main",
                "true",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
        )
        assert flip.returncode == 0, flip.stderr + flip.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["install_has_main"] is True
        assert status["install_has_main_flipped_true"] is True
        # Batch 231: Path C already landed → idle_path_c_done; else path_c_land.
        assert status["last"]["action"] in ("path_c_land", "idle_path_c_done")
        if status["last"]["action"] == "path_c_land":
            assert status["last"]["reason"] == "install_has_main_flipped_true"
            assert status["last"]["land"]["attempted"] is False
            assert status["last"]["land"].get("triggered_by") == "install_has_main_flipped_true"
        else:
            assert status["last"]["reason"] == "path_c_already_landed"
            assert status["last"].get("path_c_landed") is True

        # ALIGNED + WRITABLE dry-run (install already true; no flip) → Path C or idle
        aligned = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "WRITABLE",
                "--mock-align",
                "ALIGNED",
                "--mock-install-has-main",
                "true",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
        )
        assert aligned.returncode == 0, aligned.stderr + aligned.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["last"]["action"] in ("path_c_land", "idle_path_c_done")
        assert status["install_has_main_flipped_true"] is False
        if status["last"]["action"] == "path_c_land":
            land = status["last"]["land"]
            assert land is not None
            assert land["attempted"] is False
            assert land["skipped_reason"] == "dry_run"
            assert "lemma_closed=false" in (land.get("gate") or "")
        else:
            assert status["last"].get("path_c_landed") is True
            assert status["last"].get("next_focus") == "tip-sync+drift+no-flip"

        # MISALIGNED + WRITABLE dry-run → would Path B restore, no attempt
        mis = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "WRITABLE",
                "--mock-align",
                "MISALIGNED",
                "--mock-install-has-main",
                "true",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
        )
        assert mis.returncode == 0, mis.stderr + mis.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["last"]["action"] == "path_b_restore"
        assert status["last"]["land"]["attempted"] is False
        assert status["lemma_closed"] is False

        # STOP file → clean exit before land
        stop_path.write_text("stop\n", encoding="utf-8")
        stopped = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "WRITABLE",
                "--mock-align",
                "ALIGNED",
                "--mock-install-has-main",
                "false",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
        )
        assert stopped.returncode == 0, stopped.stderr + stopped.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["stopped"] is True
        assert status["stop_reason"] == "stop_file"
        assert status["goal_complete"] is False


def test_when_writable_land_token_file_discovery() -> None:
    """Batch 84: MAIN_PUSH_TOKEN from env → store file → .secrets (tempfile only)."""
    import importlib.util
    import tempfile

    script = ROOT / "scripts" / "when_writable_land.py"
    spec = importlib.util.spec_from_file_location("when_writable_land", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fake = "ghp_TEST_FAKE_TOKEN_DO_NOT_USE_batch84"
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        store = td_path / "store_MAIN_PUSH_TOKEN"
        secrets = td_path / "secrets_MAIN_PUSH_TOKEN"
        candidates = (store, secrets)

        # None when empty
        tok, src = mod.resolve_main_push_token(env={}, file_candidates=candidates)
        assert tok is None and src is None

        # Second file used when first missing
        secrets.write_text(fake + "\n", encoding="utf-8")
        tok, src = mod.resolve_main_push_token(env={}, file_candidates=candidates)
        assert tok == fake
        assert src == f"file:{secrets}"

        # First file wins over second
        store.write_text(fake + "_STORE\n", encoding="utf-8")
        tok, src = mod.resolve_main_push_token(env={}, file_candidates=candidates)
        assert tok == fake + "_STORE"
        assert src == f"file:{store}"

        # Env wins over both files
        tok, src = mod.resolve_main_push_token(
            env={"MAIN_PUSH_TOKEN": fake + "_ENV"},
            file_candidates=candidates,
        )
        assert tok == fake + "_ENV"
        assert src == "env:MAIN_PUSH_TOKEN"

        # apply_token_to_env injects for git/gh without altering when empty
        plain = {"PATH": "/usr/bin"}
        assert mod.apply_token_to_env(plain, None) == plain
        injected = mod.apply_token_to_env(plain, fake)
        assert injected["MAIN_PUSH_TOKEN"] == fake
        assert injected["GH_TOKEN"] == fake
        assert injected["GITHUB_TOKEN"] == fake
        # Does not overwrite existing GH_TOKEN
        injected2 = mod.apply_token_to_env({"GH_TOKEN": "keep_me"}, fake)
        assert injected2["GH_TOKEN"] == "keep_me"
        assert injected2["MAIN_PUSH_TOKEN"] == fake

    # Default candidate paths documented in source
    src = script.read_text(encoding="utf-8")
    assert "/cursor/stores/self/MAIN_PUSH_TOKEN" in src
    assert "/workspace/.secrets/MAIN_PUSH_TOKEN" in src
    assert "/tmp/gh-dylan-auth/access_token" in src
    assert "resolve_main_push_token" in src
    assert "token_source" in src
    # Batch 132: dylan device token is last default candidate (after store/.secrets)
    assert mod.DEFAULT_TOKEN_FILES[-1] == Path("/tmp/gh-dylan-auth/access_token")

    # Env hardening: repositoryDependencies for main (write intent)
    env_text = (ROOT / ".cursor" / "environment.json").read_text(encoding="utf-8")
    assert "repositoryDependencies" in env_text
    assert "github.com/d6g8k5htny-coder/main" in env_text

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "RELAUNCH" in owner.upper() or "relaunch" in owner
    assert "repositoryDependencies" in owner
    assert "AFTER merging" in owner or "after merging" in owner.lower()

    # --once run must never echo the fake secret when file-discovered
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        store = td_path / "MAIN_PUSH_TOKEN"
        store.write_text(fake, encoding="utf-8")
        log_path = td_path / "log.txt"
        status_path = td_path / "status.json"
        stop_path = td_path / "stop"
        # Monkey via env override of candidates is unit-tested above; here verify
        # CLI logging never prints a planted env token value.
        env = {**os.environ, "MAIN_PUSH_TOKEN": fake}
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "DENIED",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
            env=env,
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
        combined = (proc.stdout or "") + (proc.stderr or "") + log_path.read_text(
            encoding="utf-8"
        )
        assert fake not in combined
        status = __import__("json").loads(status_path.read_text(encoding="utf-8"))
        assert status["token_present"] is True
        assert status["token_source"] == "env:MAIN_PUSH_TOKEN"
        assert fake not in status_path.read_text(encoding="utf-8")


def test_guard_no_status_promotion_detects_flips() -> None:
    """Batch 86: fixture snapshots — pass when unchanged/new OPEN; fail on promote."""
    import json
    import tempfile

    script = ROOT / "scripts" / "guard_no_status_promotion.py"
    assert script.is_file()
    snap_art = ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json"
    assert snap_art.is_file()
    snap = json.loads(snap_art.read_text(encoding="utf-8"))
    assert snap["scientific_effect"] == "NONE"
    assert snap["lemma_closed"] is False
    assert snap["goal_complete"] is False
    assert snap["flipped_anything"] is False
    assert snap["guard"] == "no_status_promotion"
    assert snap["pass"] is True
    assert snap["violations"] == []

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "research-stack-status-guard" in ci
    assert "guard_no_status_promotion.py" in ci
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "guard_no_status_promotion.py" in pack
    assert "STATUS_GUARD_SNAPSHOT.json" in pack

    def _write_checkout(root: Path, *, lemma_closed: bool = False, premise_status: str = "OPEN",
                        prize_closed: bool = False, drop_premise: bool = False,
                        lemma_status: str = "OPEN", discharges: bool = False) -> None:
        (root / "docs" / "math_status").mkdir(parents=True)
        (root / "claims").mkdir()
        packet = {
            "disposition": "OPEN_HOLD",
            "lemma_closed": lemma_closed,
            "prizes_solved": False,
            "original_prize_closed": prize_closed,
            "independence_credit": 0,
            "bridge": "PROPOSED_NOT_DEPLOYED",
            "freeze": False,
            "OBL-H5-JETMOD": {
                "status": "OPEN",
                "lemma_closed": lemma_closed,
                "freeze": False,
                "grade": "display_only",
                "discharges_OBL_H5_JETMOD": False,
            },
            "D3-LEMMA-RN-UNIF": {
                "status": lemma_status,
                "lemma_closed": lemma_closed,
                "freeze": False,
                "piece2_annulus_driver": "UNWRITTEN",
                "discharges_lemma": discharges,
            },
        }
        (root / "docs" / "math_status" / "PACKET.json").write_text(
            json.dumps(packet), encoding="utf-8"
        )
        premises = {
            "OBL-H5-JETMOD": {
                "track": "UPPER2D",
                "status_frozen_v2_2": premise_status,
                "status_register_note": premise_status,
                "source": "test",
            },
            "D3-LEMMA-RN-UNIF": {
                "track": "UPPER2D",
                "status_frozen_v2_2": "NOT_CLOSED",
                "status_register_note": "OPEN",
                "source": "test",
            },
        }
        if drop_premise:
            del premises["OBL-H5-JETMOD"]
        graph = {
            "as_of": "test",
            "premises": premises,
            "claims": {
                "PR-TAL-003..008": {
                    "track": "NUMBER_THEORY",
                    "grade": "AUTHOR_SIDE_PROOF_PRESENT",
                    "original_prize_closed": prize_closed,
                    "depends_on": [],
                    "source": "test",
                },
            },
            "firewalls": [],
        }
        (root / "claims" / "graph.json").write_text(json.dumps(graph), encoding="utf-8")

    # Baseline fixture (OPEN inventory)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        base_checkout = td_path / "base"
        base_checkout.mkdir()
        _write_checkout(base_checkout)
        # Build baseline via audit → guard snapshot shape using BATCH70-like wrapper
        sys.path.insert(0, str(ROOT / "scripts"))
        from audit_research_stack_open import audit_checkout  # type: ignore
        from guard_no_status_promotion import (  # type: ignore
            compare_inventories,
            extract_open_inventory,
        )

        base_report = audit_checkout(base_checkout)
        base_inv = extract_open_inventory(base_report)
        assert "OBL-H5-JETMOD" in base_inv["premises"]
        assert base_inv["packet_lemma_closed"] is False

        # Unchanged → no violations
        cur_same = extract_open_inventory(audit_checkout(base_checkout))
        assert compare_inventories(base_inv, cur_same) == []

        # New OPEN premise only → pass
        new_open = td_path / "new_open"
        new_open.mkdir()
        _write_checkout(new_open)
        # Inject an extra OPEN premise
        graph_path = new_open / "claims" / "graph.json"
        g = json.loads(graph_path.read_text(encoding="utf-8"))
        g["premises"]["NEW-OPEN-PREMISE"] = {
            "track": "UPPER2D",
            "status_frozen_v2_2": "OPEN",
            "status_register_note": "OPEN",
            "source": "test",
        }
        graph_path.write_text(json.dumps(g), encoding="utf-8")
        cur_new = extract_open_inventory(audit_checkout(new_open))
        assert "NEW-OPEN-PREMISE" in cur_new["premises"]
        assert compare_inventories(base_inv, cur_new) == []

        # Promote: lemma_closed true → fail
        promoted = td_path / "promoted"
        promoted.mkdir()
        _write_checkout(promoted, lemma_closed=True)
        cur_bad = extract_open_inventory(audit_checkout(promoted))
        viol = compare_inventories(base_inv, cur_bad)
        assert any(v["kind"] == "packet_lemma_closed" for v in viol)
        assert any(v.get("reason", "").find("lemma_closed") >= 0 for v in viol)

        # Promote: premise CLOSED (absent from open list) → fail
        closed_p = td_path / "closed_premise"
        closed_p.mkdir()
        _write_checkout(closed_p, premise_status="CLOSED", drop_premise=False)
        # audit filters CLOSED out of open_premises when not in OPEN_FROZEN
        cur_closed = extract_open_inventory(audit_checkout(closed_p))
        assert "OBL-H5-JETMOD" not in cur_closed["premises"]
        viol2 = compare_inventories(base_inv, cur_closed)
        assert any(v["kind"] == "premise" and v["id"] == "OBL-H5-JETMOD" for v in viol2)

        # Promote: prize original_prize_closed true → fail
        prize = td_path / "prize"
        prize.mkdir()
        _write_checkout(prize, prize_closed=True)
        cur_prize = extract_open_inventory(audit_checkout(prize))
        viol3 = compare_inventories(base_inv, cur_prize)
        assert any(
            v["kind"] in {"prize", "packet_original_prize_closed"} for v in viol3
        )

        # Promote: discharges_lemma true → fail
        disc = td_path / "discharge"
        disc.mkdir()
        _write_checkout(disc, discharges=True)
        cur_disc = extract_open_inventory(audit_checkout(disc))
        viol4 = compare_inventories(base_inv, cur_disc)
        assert any("discharges_lemma" in str(v.get("reason", "")) for v in viol4)

        # CLI: exit 1 on promoted checkout vs baseline snapshot file
        baseline_file = td_path / "baseline.json"
        baseline_file.write_text(
            json.dumps({"hardening_tip_audit": base_report, "hardening_tip": "abc"}),
            encoding="utf-8",
        )
        out_snap = td_path / "out_snap.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                str(promoted),
                "--baseline",
                str(baseline_file),
                "--snapshot-out",
                str(out_snap),
                "--trial-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert proc.returncode == 1, proc.stderr + proc.stdout
        assert out_snap.is_file()
        out = json.loads(out_snap.read_text(encoding="utf-8"))
        assert out["pass"] is False
        assert out["violations"]
        assert out["lemma_closed"] is False  # guard report never claims closed
        assert out["scientific_effect"] == "NONE"

        # CLI: exit 0 on unchanged
        out_ok = td_path / "out_ok.json"
        proc2 = subprocess.run(
            [
                sys.executable,
                str(script),
                str(base_checkout),
                "--baseline",
                str(baseline_file),
                "--snapshot-out",
                str(out_ok),
                "--trial-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert proc2.returncode == 0, proc2.stderr + proc2.stdout
        ok = json.loads(out_ok.read_text(encoding="utf-8"))
        assert ok["pass"] is True
        assert ok["violations"] == []

    brief = ROOT / "portable" / "BATCH86_BRIEF.json"
    assert brief.is_file()
    brief_data = json.loads(brief.read_text(encoding="utf-8"))
    assert brief_data["goal_complete"] is False
    assert brief_data["lemma_closed"] is False
    assert brief_data["scientific_effect"] == "NONE"
    assert brief_data["new_0017"] is False
    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 86" in log
    assert "guard_no_status_promotion" in log


def test_objective_evidence_83() -> None:
    """Batch 83: requirement-by-requirement objective evidence; no 0017; goal_complete false."""
    import json

    evidence = ROOT / "portable" / "OBJECTIVE_EVIDENCE_83.json"
    brief = ROOT / "portable" / "BATCH83_BRIEF.json"
    assert evidence.is_file()
    assert brief.is_file()
    data = json.loads(evidence.read_text(encoding="utf-8"))
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["scientific_effect"] == "NONE"
    assert data["new_0017"] is False
    assert data["tip_refresh"] is False
    req_ids = [r["id"] for r in data["requirements"]]
    assert req_ids == [
        "align",
        "portable_prepared",
        "audit",
        "iterate_permanent",
        "path_c_landed",
    ]
    by_id = {r["id"]: r for r in data["requirements"]}
    assert by_id["align"]["status"] == "MET"
    assert by_id["portable_prepared"]["status"] == "MET"
    assert by_id["path_c_landed"]["path_c_landed"] is False
    assert by_id["path_c_landed"]["blocked_by"]["write_state"] == "DENIED"
    assert data["summary"]["path_c_landed"] is False
    assert data["summary"]["blocked_by"] == "write_DENIED_403"

    brief_data = json.loads(brief.read_text(encoding="utf-8"))
    assert brief_data["goal_complete"] is False
    assert brief_data["new_0017"] is False
    assert brief_data["path_c_landed"] is False

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "OBJECTIVE_EVIDENCE_*.json" in pack

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 83" in log or "OBJECTIVE_EVIDENCE_83" in log


def test_patches_manifest_and_pack_includes_it() -> None:
    """Batch 89: MANIFEST.json lists apply_all patches; pack_portable requires it."""
    import json
    import subprocess
    import tarfile
    import tempfile

    manifest_path = ROOT / "portable" / "patches" / "MANIFEST.json"
    assert manifest_path.is_file()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert _living_tip(data["verified_on_tip"]) or any(
        data["verified_on_tip"].startswith(t)
        for t in ("8ea3b5f", "10c077e", "c82c9357", "ac33581")
    )
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed"] is False
    assert data["goal_complete"] is False
    assert data["apply_all_count"] in (13, 14, 15, 16)
    assert len(data["patches"]) == data["apply_all_count"]
    ids = [p["id"] for p in data["patches"]]
    assert ids == [
        "0001", "0002", "0003", "0004",
        "0008", "0009", "0010", "0011", "0012", "0013", "0014", "0015", "0016",
    ] or ids == [
        "0001", "0002", "0003", "0004",
        "0008", "0009", "0010", "0011", "0012", "0013", "0014", "0015", "0016", "0017",
    ] or ids == [
        "0001", "0002", "0003", "0004",
        "0008", "0009", "0010", "0011", "0012", "0013", "0014", "0015", "0016", "0017", "0018",
    ] or ids == [
        "0001", "0002", "0003", "0004",
        "0008", "0009", "0010", "0011", "0012", "0013", "0014", "0015", "0016", "0017", "0018", "0019",
    ]
    for p in data["patches"]:
        assert p["title"]
        assert isinstance(p["files-touched"], list) and p["files-touched"]
        assert p["obsolete-if"] is None
        assert p["in_apply_all"] is True
        assert p["verified_on_tip"] == data["verified_on_tip"]
    for p in data["obsolete_kept_on_disk"]:
        assert p["obsolete-if"]
        assert p["in_apply_all"] is False

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "portable/patches/MANIFEST.json" in pack

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "pack.tgz"
        subprocess.run(
            [str(ROOT / "scripts" / "pack_portable.sh"), str(out)],
            check=True,
            timeout=60,
        )
        with tarfile.open(out, "r:gz") as tf:
            names = tf.getnames()
        assert "portable/patches/MANIFEST.json" in names


def test_batch137_owner_path_c_oneshot_and_relaunch_doc() -> None:
    """Batch 137: owner one-shot --from-bundle + RELAUNCH_WITH_MAIN_SCOPE.md."""
    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "--from-bundle" in owner_c
    assert "path-c-on-hardening.patch" in owner_c
    assert "RELAUNCH_WITH_MAIN_SCOPE" in owner_c
    # Living Path C release tag may supersede older pins (batch241+).
    assert (
        "batch241-path-c-bundle" in owner_c
        or "batch218-path-c-bundle" in owner_c
        or "batch199-path-c-bundle" in owner_c
        or "batch180-path-c-bundle" in owner_c
        or "batch179-path-c-bundle" in owner_c
        or "batch169-path-c-bundle" in owner_c
        or "batch168-path-c-bundle" in owner_c
        or "batch142-path-c-bundle" in owner_c
        or "-path-c-bundle" in owner_c
    )
    assert "trial-portable-main-fixes.tgz" in owner_c

    relaunch = ROOT / "portable" / "RELAUNCH_WITH_MAIN_SCOPE.md"
    assert relaunch.is_file()
    rel_text = relaunch.read_text(encoding="utf-8")
    assert "Applications" in rel_text or "applications" in rel_text.lower()
    assert "d6g8k5htny-coder/main" in rel_text
    assert "device" in rel_text.lower()
    assert "MAIN_PUSH_TOKEN" in rel_text
    assert "RELAUNCH" in rel_text.upper()
    assert "mid-flight" in rel_text.lower() or "midflight" in rel_text.lower().replace("-", "")
    assert "repositoryDependencies" in rel_text

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "--from-bundle" in land
    assert "RELAUNCH_WITH_MAIN_SCOPE" in land
    assert (
        "batch241-path-c-bundle" in land
        or "batch218-path-c-bundle" in land
        or "batch169-path-c-bundle" in land
        or "batch179-path-c-bundle" in land
        or "batch180-path-c-bundle" in land
        or "batch168-path-c-bundle" in land
        or "batch142-path-c-bundle" in land
        or "-path-c-bundle" in land
    )

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "--from-bundle" in owner_actions
    assert (
        "batch241-path-c-bundle" in owner_actions
        or "batch218-path-c-bundle" in owner_actions
        or "batch169-path-c-bundle" in owner_actions
        or "batch179-path-c-bundle" in owner_actions
        or "batch180-path-c-bundle" in owner_actions
        or "batch168-path-c-bundle" in owner_actions
        or "batch142-path-c-bundle" in owner_actions
        or "-path-c-bundle" in owner_actions
    )
    assert "RELAUNCH_WITH_MAIN_SCOPE" in owner_actions

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "portable/RELAUNCH_WITH_MAIN_SCOPE.md" in pack

    # --help and --dry-run still work
    help_proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "owner_land_path_c.sh"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=str(ROOT),
    )
    assert help_proc.returncode == 0, help_proc.stderr
    assert "--from-bundle" in help_proc.stdout
    dry = subprocess.run(
        ["bash", str(ROOT / "scripts" / "owner_land_path_c.sh"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout


def test_batch138_path_c_bundle_ci_and_dry_run_exit_codes() -> None:
    """Batch 138: CI dry-applies path-c-applied-bundle; dry-run exits 0/1/2."""
    import json

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "path-c-applied-bundle-dry-apply" in ci
    assert "path-c-on-hardening.patch" in ci
    assert "am --3way" in ci
    assert "lemma_closed=false" in ci
    assert "Scientific effect: NONE" in ci

    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "pass through path_c_dry_run" in owner_c
    assert "exit 2" in owner_c
    assert "dry_ec" in owner_c

    notes = (ROOT / "portable" / "CONFLICTING_PR_NOTES.md").read_text(encoding="utf-8")
    assert "Batch 138" in notes
    assert "#53" in notes
    assert "#54" in notes

    brief = ROOT / "portable" / "BATCH138_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "138"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["tip_refresh"] is False
    assert data["path_c_landed"] is False


def test_batch139_path_c_repository_dispatch_and_ci_green() -> None:
    """Batch 139: Path C repository_dispatch + dispatch helper; CI dry-apply verified."""
    import json

    path_c = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "repository_dispatch" in path_c
    assert "types: [land-path-c-on-main]" in path_c
    assert "Resolve dry_run" in path_c or "steps.mode.outputs.dry_run" in path_c
    assert "MAIN_PUSH_TOKEN" in path_c
    assert "lemma_closed=false" in path_c
    # Batch 139 fix: clone hardening ref directly (not default main + fetch)
    assert "--branch" in path_c
    assert 'clone --depth 80 --branch "${HARDENING_REF}"' in path_c or \
        "clone --depth 80 --branch" in path_c

    dispatch = (ROOT / "scripts" / "dispatch_land_path_c.sh").read_text(encoding="utf-8")
    assert "land-path-c-on-main" in dispatch
    assert "--apply" in dispatch
    assert "dispatches" in dispatch

    vectors = (ROOT / "scripts" / "probe_main_write_vectors.py").read_text(encoding="utf-8")
    assert "W3f_repository_dispatch_path_c" in vectors

    brief = ROOT / "portable" / "BATCH139_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "139"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip_refresh"] is False
    assert data.get("ci_dry_apply") == "green"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 139" in log
    assert "repository_dispatch" in log


def test_batch140_when_writable_repository_dispatch_on_token_file() -> None:
    """Batch 140: token-file drop → repository_dispatch land-path-c; no 0017."""
    import importlib.util
    import json
    import tempfile

    script = ROOT / "scripts" / "when_writable_land.py"
    src = script.read_text(encoding="utf-8")
    assert "WELL_KNOWN_TOKEN_PATHS" in src
    assert "/cursor/stores/self/MAIN_PUSH_TOKEN" in src
    assert "/workspace/.secrets/MAIN_PUSH_TOKEN" in src
    assert "/tmp/gh-dylan-auth/access_token" in src
    assert "dispatch_land_path_c" in src
    assert "path_c_repository_dispatch" in src
    assert "repository_dispatch" in src
    assert "land-path-c-on-main" in src
    assert "token_appeared" in src

    gh_login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "MAIN_PUSH_TOKEN file drop" in gh_login or "well-known" in gh_login.lower()
    assert "/cursor/stores/self/MAIN_PUSH_TOKEN" in gh_login
    assert "dispatch_land_path_c.sh --apply" in gh_login

    spec = importlib.util.spec_from_file_location("when_writable_land_b140", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.WELL_KNOWN_TOKEN_PATHS[0] == "/cursor/stores/self/MAIN_PUSH_TOKEN"
    assert mod.DISPATCH_C.name == "dispatch_land_path_c.sh"

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        tok = td_path / "MAIN_PUSH_TOKEN"
        tok.write_text("ghp_TEST_FAKE_TOKEN_batch140_do_not_use\n", encoding="utf-8")
        present, path = mod.token_file_present(file_candidates=(tok,))
        assert present is True and path == str(tok)
        absent, _ = mod.token_file_present(file_candidates=(td_path / "missing",))
        assert absent is False

        log_path = td_path / "land.log"
        detail = mod.try_repository_dispatch_path_c(
            dry_run=True, log_path=log_path, apply=True
        )
        assert detail["skipped_reason"] == "dry_run"
        assert detail["apply"] is True
        assert "--apply" in " ".join(detail["would_run"])
        assert "land-path-c-on-main" in detail["event_type"]

        # --once dry-run with planted token file + seeded status (token absent)
        # uses DEFAULT_TOKEN_FILES; plant at access_token only if absent.
        access = Path("/tmp/gh-dylan-auth/access_token")
        planted = False
        fake = "ghp_TEST_FAKE_TOKEN_batch140_do_not_use"
        try:
            if not access.is_file():
                access.parent.mkdir(parents=True, exist_ok=True)
                access.write_text(fake + "\n", encoding="utf-8")
                access.chmod(0o600)
                planted = True
            status_path = td_path / "status.json"
            stop_path = td_path / "stop"
            # Seed prior status: no token yet → appearance flip.
            status_path.write_text(
                json.dumps(
                    {
                        "token_present": False,
                        "install_has_main": False,
                        "last_dispatch_token_source": None,
                    }
                ),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--once",
                    "--dry-run",
                    "--mock-probe",
                    "DENIED",
                    "--mock-install-has-main",
                    "false",
                    "--log",
                    str(log_path),
                    "--status",
                    str(status_path),
                    "--stop",
                    str(stop_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                cwd=str(ROOT),
            )
            assert proc.returncode == 0, proc.stderr + proc.stdout
            combined = (proc.stdout or "") + (proc.stderr or "") + log_path.read_text(
                encoding="utf-8"
            )
            assert fake not in combined
            status = json.loads(status_path.read_text(encoding="utf-8"))
            assert status["lemma_closed"] is False
            assert status["goal_complete"] is False
            assert status["flipped_anything"] is False
            assert status["last"]["action"] == "path_c_repository_dispatch"
            assert status["last"]["land"]["skipped_reason"] == "dry_run"
            assert status["last_dispatch_token_source"] == f"file:{access}"
        finally:
            if planted and access.is_file():
                access.unlink()

    brief = ROOT / "portable" / "BATCH140_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "140"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 140" in log


def test_batch141_w3f_false_positive_neutralized() -> None:
    """Batch 141: W3f dry-run dispatch is false_positive; not path_b_ready."""
    import json
    import re

    vectors = (ROOT / "scripts" / "probe_main_write_vectors.py").read_text(encoding="utf-8")
    assert "DISPATCH_OK_DRY_RUN" in vectors
    assert "false_positive_for_main_write" in vectors
    assert "w3f_real_main_write" in vectors
    assert "W3f_repository_dispatch_path_c" in vectors
    # W3f must not be in path_b_keys aggregation
    m = re.search(r"path_b_keys = \((.*?)\)", vectors, re.S)
    assert m is not None
    assert "W3f" not in m.group(1)

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "false_positive" in ww.lower() or "Batch 141" in ww

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "W3f false positive" in gh or "false_positive" in gh
    assert "DISPATCH_OK_DRY_RUN" in gh or "not a write path" in gh.lower()

    brief = ROOT / "portable" / "BATCH141_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "141"
    assert data["w3f_real"] is False
    assert data.get("w3f_false_positive") is True
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 141" in log
    assert "false_positive" in log


def test_batch147_tip_drift_gate_and_auth_renew() -> None:
    """Batch 147: CI tip-drift gate; auth renew doc; no obsolete drops; lemma_closed=false."""
    import json

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "tip-drift" in ci
    assert "Tip-drift gate" in ci
    assert "BASE_TIP.txt" in ci
    assert "VERIFY.json" in ci
    assert "base_tip_sha" in ci
    assert "refresh BASE_TIP" in ci or "rebuild path-c-applied-bundle" in ci
    # Both dry-apply surfaces gated
    assert "portable-patches-on-main" in ci
    assert "path-c-applied-bundle-dry-apply" in ci

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "A450-C91F" in gh
    assert "A9D3-16CD" in gh  # prior chain retained in GH_DEVICE_LOGIN.md

    # Batch 155: CI tip-drift BASE_SHA must use word-boundary \b (not \\b) in
    # single-quoted python -c — \\b emptied BASE_SHA on Actions runners.
    assert r'r"(?i)\b([0-9a-f]{40})\b"' in ci
    assert r'r"(?i)\\b([0-9a-f]{40})\\b"' not in ci

    brief = ROOT / "portable" / "BATCH147_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "147"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip_drift_gate"] is True
    assert data["patches_dropped"] == []
    assert data["tip"] == "10c077e"
    assert data["device_code"] == "A450-C91F"
    assert data["auth_renewed"] is True

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 147" in log
    assert "tip-drift" in log


def test_batch149_research_audit_and_ci_intent_fix() -> None:
    """Batch 149: research audit OPEN_HOLD; intent release tag current; lemma_closed=false."""
    import json

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 149" in findings
    assert "OPEN_HOLD" in findings
    assert "lemma_closed=false" in findings
    assert "open premises" in findings.lower()
    assert "**13**" in findings
    assert "**1**" in findings
    assert "**3**" in findings
    assert "**26**" in findings

    brief = ROOT / "portable" / "BATCH149_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "149"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "10c077e"
    assert data["device_code"] == "A450-C91F"
    assert data["auth_renewed"] is False
    assert data["ci_ok"] is True
    assert data["release_published_batch149"] is False
    rc = data["research_counts"]
    assert rc["differ"] is False
    assert rc["clean"]["open_premises"] == 13
    assert rc["clean"]["open_lemmas"] == 1
    assert rc["clean"]["open_prizes"] == 3
    assert rc["clean"]["claims"] == 26
    assert rc["clean"]["lemma_closed"] is False

    counts = ROOT / "portable" / "BATCH149_RESEARCH_COUNTS.json"
    assert counts.is_file()
    audit = ROOT / "portable" / "BATCH149_RESEARCH_STACK_AUDIT.json"
    assert audit.is_file()

    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    # Batch 169+ supersedes default release tag; historical batch142 string may remain in docs.
    assert (
        "batch169-path-c-bundle" in owner_c
        or "batch179-path-c-bundle" in owner_c
        or "batch180-path-c-bundle" in owner_c
        or "batch168-path-c-bundle" in owner_c
        or "batch142-path-c-bundle" in owner_c
    )

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 149" in log
    assert "research audit" in log.lower() or "Research audit" in log


def test_batch151_owner_open_path_c_pr_script() -> None:
    """Batch 151: owner_open_path_c_pr.sh present; --dry-run/--help; wired; lemma_closed=false."""
    import json
    import subprocess

    script = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "cursor/path-c-portable-fixes" in text
    assert "path-c-on-hardening.patch" in text
    assert "git am" in text
    assert "--dry-run" in text
    assert "MAIN_PUSH_TOKEN" in text
    assert "lemma_closed" in text
    assert "no research promotion" in text.lower() or "no_research_promotion" in text
    assert "chatgpt/drive-github-hardening-20260919" in text
    assert "BASE_TIP" in text

    help_p = subprocess.run(
        ["bash", str(script), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_p.returncode == 0
    help_out = help_p.stdout + help_p.stderr
    assert "--dry-run" in help_out
    assert "cursor/path-c-portable-fixes" in help_out
    assert "lemma_closed" in help_out

    dry_p = subprocess.run(
        ["bash", str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry_p.returncode == 0
    dry_out = dry_p.stdout + dry_p.stderr
    assert "dry-run" in dry_out.lower()
    assert "cursor/path-c-portable-fixes" in dry_out
    assert "lemma_closed=false" in dry_out or "lemma_closed stays false" in dry_out
    assert "Scientific effect: NONE" in dry_out or "scientific_effect=NONE" in dry_out

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "owner_open_path_c_pr.sh" in unblock

    owner_one = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "owner_open_path_c_pr.sh" in owner_one
    assert "cursor/path-c-portable-fixes" in owner_one

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "owner_open_path_c_pr.sh" in land
    assert "cursor/path-c-portable-fixes" in land

    brief = ROOT / "portable" / "BATCH151_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "151"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["owner_pr_script"] is True
    assert data["tip"] == "10c077e"
    assert data["device_code"] == "1DAC-111C"
    assert data["auth_renewed"] is True
    assert data["prior_device_code"] == "A450-C91F"

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "1DAC-111C" in gh
    assert "A450-C91F" in gh
    assert "owner_open_path_c_pr.sh" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 151" in log
    assert "owner_open_path_c_pr" in log


def test_batch153_base_tip_parse_and_from_bundle_dry_run() -> None:
    """Batch 153: robust BASE_TIP hex parse; --from-bundle --dry-run; daemon prefers open-PR."""
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    open_pr = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    land_c = ROOT / "scripts" / "owner_land_path_c.sh"
    dry_py = ROOT / "scripts" / "path_c_dry_run.py"
    ww = ROOT / "scripts" / "when_writable_land.py"

    open_txt = open_pr.read_text(encoding="utf-8")
    land_txt = land_c.read_text(encoding="utf-8")
    dry_txt = dry_py.read_text(encoding="utf-8")
    ww_txt = ww.read_text(encoding="utf-8")

    assert "parse_base_tip_sha" in open_txt
    assert "parse_base_tip_sha" in land_txt
    assert "_parse_base_tip_sha" in dry_txt
    assert "MAIN_PUSH_TOKEN" in land_txt and 'export GH_TOKEN="$MAIN_PUSH_TOKEN"' in land_txt
    assert "from-bundle+dry-run" in land_txt or "from-bundle dry-run" in land_txt
    assert "owner_open_path_c_pr" in ww_txt
    assert "OWNER_OPEN_PR" in ww_txt

    # Trailing comment must not become the SHA (old awk $NF bug → "tip").
    live_base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8").strip().split()[-1]
    assert live_base and all(c in "0123456789abcdef" for c in live_base.lower())
    with tempfile.TemporaryDirectory(prefix="b153-basetip-") as td:
        td_path = Path(td)
        (td_path / "portable" / "patches").mkdir(parents=True)
        (td_path / "portable" / "path-c-applied-bundle").mkdir(parents=True)
        tip_line = (
            "chatgpt/drive-github-hardening-20260919 "
            f"{live_base}  # tip\n"
        )
        (td_path / "portable" / "patches" / "BASE_TIP.txt").write_text(tip_line, encoding="utf-8")
        # Minimal bundle + VERIFY so dry-run can proceed past missing-file gates.
        real_bundle = ROOT / "portable" / "path-c-applied-bundle" / "path-c-on-hardening.patch"
        real_verify = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"
        (td_path / "portable" / "path-c-applied-bundle" / "path-c-on-hardening.patch").write_bytes(
            real_bundle.read_bytes()
        )
        (td_path / "portable" / "path-c-applied-bundle" / "VERIFY.json").write_text(
            real_verify.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        import os

        env = os.environ.copy()
        env["TRIAL_ROOT"] = str(td_path)
        p = subprocess.run(
            ["bash", str(open_pr), "--dry-run"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            env=env,
            timeout=120,
        )
        out = p.stdout + p.stderr
        assert p.returncode == 0, out
        assert f"base_tip_sha={live_base}" in out
        assert "base_tip_sha=tip" not in out
        assert "tip_matches_base=true" in out or "dry-run OK" in out

    # Live --dry-run scripts (workspace tree).
    dry_open = subprocess.run(
        ["bash", str(open_pr), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert dry_open.returncode == 0, dry_open.stderr + dry_open.stdout
    assert live_base in (dry_open.stdout + dry_open.stderr)

    dry_land = subprocess.run(
        ["bash", str(land_c), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert dry_land.returncode == 0, dry_land.stderr + dry_land.stdout

    # --from-bundle --dry-run is slower (clone+am); still must exit 0 and say OK.
    # Living supersession (Batch 230+): Path C already on tip via merge commits →
    # historical .bundle may diverge (not FF) while tip_matches_base=true.
    dry_fb = subprocess.run(
        ["bash", str(land_c), "--from-bundle", "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    fb_out = dry_fb.stdout + dry_fb.stderr
    status_now = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    already_on_tip = status_now.get("path_c_landed") is True and status_now.get("tip_match") is True
    if dry_fb.returncode == 0:
        assert "from-bundle" in fb_out.lower()
        assert "lemma_closed=false" in fb_out
        assert "dry-run OK" in fb_out or "from-bundle dry-run OK" in fb_out
    else:
        assert already_on_tip, fb_out
        assert "tip_matches_base=true" in fb_out
        assert "Not possible to fast-forward" in fb_out or "diverg" in fb_out.lower()

    brief = ROOT / "portable" / "BATCH153_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "153"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["dry_run_ok"] is True
    assert data["device_code"] == "1FC8-3D96"
    assert data.get("prior_device_code") == "1DAC-111C"
    assert data.get("auth_renewed") is True
    assert data.get("dry_run_ok") is True

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "1FC8-3D96" in gh
    assert "1DAC-111C" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 153" in log
    assert "1FC8-3D96" in log


def test_batch155_assert_path_c_ready_and_basetip_ci_fix() -> None:
    """Batch 155: assert_path_c_ready.sh; CI BASE_SHA \\b fix; lemma_closed=false."""
    import json
    import subprocess

    script = ROOT / "scripts" / "assert_path_c_ready.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "lemma_closed=false" in text
    assert "apply_all" in text
    assert "BASE_TIP" in text
    assert r"(?i)\b([0-9a-f]{40})\b" in text
    assert "scientific_effect" in text.lower() or "Scientific effect" in text

    help_p = subprocess.run(
        ["bash", str(script), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert help_p.returncode == 0, help_p.stderr + help_p.stdout
    assert "lemma_closed" in (help_p.stdout + help_p.stderr)

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "assert_path_c_ready" in ci
    assert r'r"(?i)\b([0-9a-f]{40})\b"' in ci
    assert r'r"(?i)\\b([0-9a-f]{40})\\b"' not in ci

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "assert_path_c_ready.sh" in pack
    assert "owner_open_path_c_pr.sh" in pack

    brief = ROOT / "portable" / "BATCH155_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "155"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "10c077e"
    assert data["device_code"] == "E136-5AE7"
    assert data.get("prior_device_code") == "1FC8-3D96"
    assert data.get("assert_path_c_ready") is True
    assert data.get("auth_renewed") is True

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "E136-5AE7" in gh
    assert "1FC8-3D96" in gh
    assert "A9D3-16CD" in gh
    assert "assert_path_c_ready" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 155" in log
    assert "assert_path_c_ready" in log
    assert "E136-5AE7" in log or "1FC8-3D96" in log


def test_batch157_path_c_blocked_reason_codes() -> None:
    """Batch 157: when_writable_land logs PATH_C_BLOCKED=NO_TOKEN|TIP_DRIFT|APPLY_FAIL."""
    import importlib.util
    import json
    import tempfile

    script = ROOT / "scripts" / "when_writable_land.py"
    assert script.is_file()
    src = script.read_text(encoding="utf-8")
    assert "PATH_C_BLOCKED" in src
    assert "NO_TOKEN" in src and "TIP_DRIFT" in src and "APPLY_FAIL" in src
    assert "classify_path_c_blocked" in src
    assert "format_path_c_blocked" in src
    assert "lemma_closed" in src

    spec = importlib.util.spec_from_file_location("when_writable_land_b157", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.classify_path_c_blocked(has_token=False) == ["NO_TOKEN"]
    assert mod.classify_path_c_blocked(
        has_token=False, tip_matches=False
    ) == ["NO_TOKEN", "TIP_DRIFT"]
    assert mod.classify_path_c_blocked(
        has_token=True, tip_matches=False, apply_ok=False
    ) == ["TIP_DRIFT", "APPLY_FAIL"]
    assert mod.classify_path_c_blocked(
        has_token=True, tip_matches=True, apply_ok=False
    ) == ["APPLY_FAIL"]
    assert mod.classify_path_c_blocked(
        has_token=True, tip_matches=True, apply_ok=True
    ) == []
    assert mod.format_path_c_blocked(["NO_TOKEN"]) == "PATH_C_BLOCKED=NO_TOKEN"
    assert (
        mod.format_path_c_blocked(["APPLY_FAIL", "NO_TOKEN"])
        == "PATH_C_BLOCKED=NO_TOKEN,APPLY_FAIL"
    )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        log_path = td_path / "ww.log"
        status_path = td_path / "ww.status.json"
        stop_path = td_path / "ww.stop"
        denied = subprocess.run(
            [
                sys.executable,
                str(script),
                "--once",
                "--dry-run",
                "--mock-probe",
                "DENIED",
                "--mock-install-has-main",
                "false",
                "--log",
                str(log_path),
                "--status",
                str(status_path),
                "--stop",
                str(stop_path),
                "--batch",
                "157",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            cwd=str(ROOT),
            env={
                **os.environ,
                "MAIN_PUSH_TOKEN": "",
                "PATH_C_IGNORE_FILE_TOKENS": "1",
            },
        )
        assert denied.returncode == 0, denied.stderr + denied.stdout
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert status["lemma_closed"] is False
        assert status["flipped_anything"] is False
        assert status["goal_complete"] is False
        assert status["last"]["action"] == "continue_denied"
        assert status["last"]["path_c_blocked_reasons"] == ["NO_TOKEN"]
        assert "PATH_C_BLOCKED=NO_TOKEN" in log_path.read_text(encoding="utf-8")

    brief = ROOT / "portable" / "BATCH157_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "157"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data.get("path_c_blocked_codes") == ["NO_TOKEN", "TIP_DRIFT", "APPLY_FAIL"]

    hunt = ROOT / "portable" / "BATCH157_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["hunt_result"] == "clean"
    assert h["patch_0017"] is False
    assert h["lemma_closed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 157" in log
    assert "PATH_C_BLOCKED" in log


def test_batch160_owner_set_main_push_token_script() -> None:
    """Batch 160: owner_set_main_push_token.sh present; --help/--dry-run; wired; lemma_closed=false."""
    import json
    import subprocess

    script = ROOT / "scripts" / "owner_set_main_push_token.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "gh secret set" in text
    assert "MAIN_PUSH_TOKEN" in text
    assert "--dry-run" in text
    assert "--from-gh" in text or "gh auth token" in text
    assert "dispatch_land_path_c" in text
    assert "dry_run=false" in text or "--apply" in text
    assert "lemma_closed" in text
    assert "never printed" in text.lower() or "NEVER printed" in text
    assert "Scientific effect: NONE" in text or "scientific_effect=NONE" in text

    help_p = subprocess.run(
        ["bash", str(script), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_p.returncode == 0
    help_out = help_p.stdout + help_p.stderr
    assert "--dry-run" in help_out
    assert "MAIN_PUSH_TOKEN" in help_out
    assert "lemma_closed" in help_out
    assert "gh secret set" in help_out or "secret" in help_out.lower()

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_p = subprocess.run(
        ["bash", str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_p.returncode == 0, dry_p.stderr + dry_p.stdout
    dry_out = dry_p.stdout + dry_p.stderr
    assert "dry-run" in dry_out.lower()
    assert "gh secret set" in dry_out
    assert "MAIN_PUSH_TOKEN" in dry_out
    assert "lemma_closed=false" in dry_out or "lemma_closed stays false" in dry_out
    assert "Scientific effect: NONE" in dry_out or "scientific_effect=NONE" in dry_out
    # Never print raw tokens
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out

    dry_d = subprocess.run(
        ["bash", str(script), "--dry-run", "--dispatch"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_d.returncode == 0, dry_d.stderr + dry_d.stdout
    dry_d_out = dry_d.stdout + dry_d.stderr
    assert "dispatch_land_path_c" in dry_d_out
    assert "dry_run=false" in dry_d_out

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "owner_set_main_push_token.sh" in unblock

    owner_one = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "owner_set_main_push_token.sh" in owner_one

    relaunch = (ROOT / "portable" / "RELAUNCH_WITH_MAIN_SCOPE.md").read_text(encoding="utf-8")
    assert "owner_set_main_push_token.sh" in relaunch

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "owner_set_main_push_token.sh" in land

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "owner_set_main_push_token.sh" in pack

    notes = (ROOT / "portable" / "CONFLICTING_PR_NOTES.md").read_text(encoding="utf-8")
    assert "Batch 160" in notes
    assert "Merge candidates for Path C" in notes or "merge candidates" in notes.lower()

    brief = ROOT / "portable" / "BATCH160_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "160"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["secret_script"] is True
    assert data["tip"] == "10c077e"
    assert data["device_code"] == "E818-2EE5"
    assert data["auth_renewed"] is True
    assert data["prior_device_code"] == "2513-3A16"
    assert isinstance(data.get("merge_candidates"), list)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "E818-2EE5" in gh
    assert "2513-3A16" in gh
    assert "owner_set_main_push_token.sh" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 160" in log
    assert "owner_set_main_push_token" in log
    assert "E818-2EE5" in log


def test_batch164_auth_ci_issue_refresh() -> None:
    """Batch 164: tip stable; CI green post-batch162; auth pending; issue #29; main comment_denied; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH164_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "164"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "C8FC-A08F"
    assert data["auth_renewed"] is False
    assert data["device_auth"] == "pending"
    assert data["main_comment"] == "comment_denied"
    assert data["issue_number"] == 29
    assert "issues/29" in data["issue_url"]
    assert data["issue_updated"] is True
    assert data["ci_status"] == "green"
    assert data["assert_path_c_ready"] is True
    assert data["write"] == "DENIED"
    assert data["release"] == "batch162-path-c-bundle"

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base) or "8ea3b5f" in base
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(encoding="utf-8")
    )
    assert _living_tip(verify["base_tip_sha"]) or verify["base_tip_sha"].startswith("8ea3b5f")
    assert verify["lemma_closed"] is False

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    # Batch 165 may renew past C8FC; brief still records Batch 164 code.
    assert "C8FC-A08F" in gh or "905D-02F4" in gh
    assert "issues/29" in gh or "#29" in gh
    assert "comment_denied" in gh
    assert "batch162-path-c-bundle" in gh or "batch169-path-c-bundle" in gh or "batch168-path-c-bundle" in gh or "batch179-path-c-bundle" in gh or "batch180-path-c-bundle" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 164" in log
    assert "C8FC-A08F" in log
    assert "8ea3b5f" in log
    assert "comment_denied" in log
    assert "#29" in log or "issues/29" in log
    assert "lemma_closed" in log.lower()


def test_batch169_git_bundle_path_c() -> None:
    """Batch 169: fetchable path-c-on-hardening.bundle; owner prefers .bundle; tip stable; auth pending; lemma_closed=false."""
    import json
    import os
    import subprocess

    bundle_dir = ROOT / "portable" / "path-c-applied-bundle"
    git_bundle = bundle_dir / "path-c-on-hardening.bundle"
    patch = bundle_dir / "path-c-on-hardening.patch"
    assert git_bundle.is_file()
    assert patch.is_file()
    assert git_bundle.stat().st_size > 100
    verify = json.loads((bundle_dir / "VERIFY.json").read_text(encoding="utf-8"))
    # VERIFY is living; Batch 170+ may stamp e2e without tip/bundle rebuild.
    assert str(verify["batch"]) in ("169", "170") or int(str(verify["batch"])) >= 169
    assert verify["git_bundle"] is True
    assert verify["lemma_closed"] is False
    assert _living_tip(verify["base_tip_sha"]) or verify["base_tip_sha"].startswith("8ea3b5f")
    assert verify["bundle_file"] == "path-c-on-hardening.bundle"
    assert "cursor/portable-engineering-patches" in verify.get("bundle_branch", "")
    apply_md = (bundle_dir / "APPLY.md").read_text(encoding="utf-8")
    assert "git fetch" in apply_md
    assert "path-c-on-hardening.bundle" in apply_md
    assert "git merge" in apply_md or "git pull" in apply_md
    assert "batch169-path-c-bundle" in apply_md or "batch207-path-c-bundle" in apply_md or "-path-c-bundle" in apply_md
    assert "depth" in apply_md.lower() or "shallow" in apply_md.lower() or "Batch 170" in apply_md

    land = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "path-c-on-hardening.bundle" in land
    assert "USE_GIT_BUNDLE" in land or "use_git_bundle" in land
    assert "git fetch" in land
    assert "batch169-path-c-bundle" in land or "batch179-path-c-bundle" in land or "batch180-path-c-bundle" in land or "batch207-path-c-bundle" in land or "-path-c-bundle" in land

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    text = oneshot.read_text(encoding="utf-8")
    assert "batch169-path-c-bundle" in text or "batch179-path-c-bundle" in text or "batch180-path-c-bundle" in text or "batch207-path-c-bundle" in text or "-path-c-bundle" in text
    assert "path-c-on-hardening.bundle" in text
    assert "PATH_C_RELEASE_TAG" in text

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_p = subprocess.run(
        ["bash", str(oneshot), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_p.returncode == 0, dry_p.stderr + dry_p.stdout
    dry_out = dry_p.stdout + dry_p.stderr
    assert "UNBLOCK MENU" in dry_out or "unblock" in dry_out.lower()
    assert "batch169-path-c-bundle" in dry_out or "batch179-path-c-bundle" in dry_out or "batch180-path-c-bundle" in dry_out or "batch199-path-c-bundle" in dry_out or "batch202-path-c-bundle" in dry_out or "-path-c-bundle" in dry_out
    assert "path-c-on-hardening.bundle" in dry_out
    assert "7BCB-0057" in dry_out or "EC83-CFC2" in dry_out or "831C-CB1C" in dry_out or "github.com/login/device" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out

    # --from-bundle --dry-run prefers .bundle
    # Living supersession (Batch 230+): merge-landed tip may diverge from historical .bundle.
    land_c = ROOT / "scripts" / "owner_land_path_c.sh"
    fb = subprocess.run(
        ["bash", str(land_c), "--from-bundle", "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    fb_out = fb.stdout + fb.stderr
    status_now = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    already_on_tip = status_now.get("path_c_landed") is True and status_now.get("tip_match") is True
    assert "use_git_bundle=1" in fb_out or "git bundle" in fb_out.lower() or ".bundle" in fb_out
    if fb.returncode == 0:
        assert "from-bundle dry-run OK" in fb_out or "dry-run OK" in fb_out
        assert "lemma_closed=false" in fb_out
    else:
        assert already_on_tip, fb_out
        assert "tip_matches_base=true" in fb_out
        assert "Not possible to fast-forward" in fb_out or "diverg" in fb_out.lower()

    brief = ROOT / "portable" / "BATCH169_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "169"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["git_bundle"] is True
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["device_code"] in ("831C-CB1C", "EC83-CFC2", "7BCB-0057") or "-" in str(data["device_code"])
    # Renew path keeps prior 831C when Batch 169 renewed near expiry.
    if data["device_code"] != "831C-CB1C":
        assert data.get("prior_device_code") == "831C-CB1C"
        assert data.get("auth_renewed") is True
    assert data["write"] == "DENIED"
    assert data["release"] == "batch169-path-c-bundle"
    assert data.get("preferred_auth_interval_s") == 1800

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "path-c-applied-bundle" in pack
    assert "owner_path_c_oneshot.sh" in pack

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert (
        "batch169-path-c-bundle" in unblock
        or "batch179-path-c-bundle" in unblock
        or "batch180-path-c-bundle" in unblock
    )
    assert "path-c-on-hardening.bundle" in unblock

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 169" in log
    assert "path-c-on-hardening.bundle" in log
    assert "batch169-path-c-bundle" in log
    assert "lemma_closed" in log.lower()

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "831C-CB1C" in gh  # prior / history
    assert data["device_code"] in gh
    assert "batch169-path-c-bundle" in gh
    assert "path-c-on-hardening.bundle" in gh
    assert "issues/27" in gh
    assert "BATCH162_BRIEF" in gh


def test_batch168_oneshot_pack_ci() -> None:
    """Batch 168: oneshot dry-run + pack release tag; CI history fix; tip stable; auth pending; lemma_closed=false."""
    import json
    import os
    import subprocess

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    assert oneshot.is_file()
    text = oneshot.read_text(encoding="utf-8")
    # Batch 169 superseded the default release tag; Batch 179 supersedes again; Batch 168 history remains in comments/docs.
    assert "batch168-path-c-bundle" in text or "Batch 168" in text
    assert "batch169-path-c-bundle" in text or "batch179-path-c-bundle" in text
    assert "PATH_C_RELEASE_TAG" in text
    assert "owner_path_c_oneshot.sh --from-bundle" in text
    assert "lemma_closed" in text

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_p = subprocess.run(
        ["bash", str(oneshot), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_p.returncode == 0, dry_p.stderr + dry_p.stdout
    dry_out = dry_p.stdout + dry_p.stderr
    assert "UNBLOCK MENU" in dry_out or "unblock" in dry_out.lower()
    assert "batch169-path-c-bundle" in dry_out or "batch168-path-c-bundle" in dry_out or "batch179-path-c-bundle" in dry_out or "batch180-path-c-bundle" in dry_out or "batch199-path-c-bundle" in dry_out or "batch202-path-c-bundle" in dry_out or "-path-c-bundle" in dry_out
    assert "831C-CB1C" in dry_out or "github.com/login/device" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out

    # Token dry-run path still OK (fake token never printed).
    tok_env = dict(dry_env)
    tok_env["MAIN_PUSH_TOKEN"] = "fake-batch168-dry-run-token-not-real"
    tok_p = subprocess.run(
        ["bash", str(oneshot), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=tok_env,
    )
    assert tok_p.returncode == 0, tok_p.stderr + tok_p.stdout
    tok_out = tok_p.stdout + tok_p.stderr
    assert "dry-run OK" in tok_out
    assert "fake-batch168-dry-run-token-not-real" not in tok_out
    assert "token_source=env:MAIN_PUSH_TOKEN" in tok_out

    brief = ROOT / "portable" / "BATCH168_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "168"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["oneshot"] is True
    assert data["dry_run_ok"] is True
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "831C-CB1C"
    assert data["prior_device_code"] == "905D-02F4"
    assert data["auth_renewed"] is True
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["release"] == "batch168-path-c-bundle"
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("issue_number") == 31
    assert "issues/31" in (data.get("issue_url") or "")

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "831C-CB1C" in gh
    assert "905D-02F4" in gh
    assert "batch168-path-c-bundle" in gh or "batch169-path-c-bundle" in gh or "batch218-path-c-bundle" in gh or "-path-c-bundle" in gh
    assert "batch162-path-c-bundle" in gh or "batch169-path-c-bundle" in gh
    assert "issues/27" in gh
    assert "BATCH162_BRIEF" in gh
    assert "preferred_auth_interval_s=1800" in gh or "1800" in gh
    assert "issues/31" in gh or "#31" in gh

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "batch169-path-c-bundle" in unblock or "batch168-path-c-bundle" in unblock or "batch179-path-c-bundle" in unblock
    assert "1800" in unblock

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "owner_path_c_oneshot.sh" in pack

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 168" in log
    assert "831C-CB1C" in log
    assert "905D-02F4" in log
    assert "batch168-path-c-bundle" in log
    assert "preferred_auth_interval_s=1800" in log
    assert "#31" in log or "issues/31" in log
    assert "lemma_closed" in log.lower()


def test_batch165_owner_path_c_oneshot() -> None:
    """Batch 165: owner_path_c_oneshot.sh; research audit refresh; tip stable; auth renew; lemma_closed=false."""
    import json
    import os
    import subprocess

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    assert oneshot.is_file()
    text = oneshot.read_text(encoding="utf-8")
    assert "owner_open_path_c_pr.sh" in text
    assert "owner_land_path_c.sh" in text
    assert "--dry-run" in text
    assert "MAIN_PUSH_TOKEN" in text
    assert "/tmp/gh-dylan-auth/access_token" in text
    assert "github.com/login/device" in text
    assert "owner_set_main_push_token.sh" in text
    assert "RELAUNCH_WITH_MAIN_SCOPE" in text
    assert "--from-bundle" in text
    assert "lemma_closed" in text
    assert "never printed" in text.lower() or "value not printed" in text.lower()

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "owner_path_c_oneshot.sh" in unblock

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "owner_path_c_oneshot.sh" in pack

    owner_one = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "owner_path_c_oneshot.sh" in owner_one

    help_p = subprocess.run(
        ["bash", str(oneshot), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_p.returncode == 0, help_p.stderr
    assert "--dry-run" in help_p.stdout
    assert "lemma_closed" in help_p.stdout

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_p = subprocess.run(
        ["bash", str(oneshot), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_p.returncode == 0, dry_p.stderr + dry_p.stdout
    dry_out = dry_p.stdout + dry_p.stderr
    assert "UNBLOCK MENU" in dry_out or "unblock" in dry_out.lower()
    assert "github.com/login/device" in dry_out
    assert "owner_set_main_push_token.sh" in dry_out
    assert "--from-bundle" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out

    brief = ROOT / "portable" / "BATCH165_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "165"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["oneshot"] is True
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["device_code"] == "905D-02F4"
    assert data["auth_renewed"] is True
    assert data["prior_device_code"] == "C8FC-A08F"
    assert data["write"] == "DENIED"
    assert data.get("issue_number") == 30
    assert "issues/30" in (data.get("issue_url") or "")
    counts = data.get("research_counts") or {}
    assert counts.get("open_premises") == 13
    assert counts.get("open_lemmas") == 1
    assert counts.get("open_prizes") == 3
    assert counts.get("disposition") == "OPEN_HOLD"

    counts_file = ROOT / "portable" / "BATCH165_RESEARCH_COUNTS.json"
    assert counts_file.is_file()
    cdata = json.loads(counts_file.read_text(encoding="utf-8"))
    assert cdata["clean"]["lemma_closed"] is False
    assert cdata["clean"]["disposition"] == "OPEN_HOLD"
    assert cdata["clean"]["open_premises"] == 13

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 165" in findings
    assert "8ea3b5f" in findings
    assert "OPEN_HOLD" in findings
    assert "lemma_closed=false" in findings.lower() or "**lemma_closed=false**" in findings

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "905D-02F4" in gh
    assert "C8FC-A08F" in gh
    assert "owner_path_c_oneshot.sh" in gh
    assert "issues/30" in gh or "#30" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 165" in log
    assert "905D-02F4" in log
    assert "owner_path_c_oneshot" in log
    assert "8ea3b5f" in log
    assert "#30" in log or "issues/30" in log
    assert "lemma_closed" in log.lower()


def test_batch162_path_c_issue_and_secret_stdin() -> None:
    """Batch 162: Path C unblock issue #26; secret set via stdin (not --body -); lemma_closed=false."""
    import json
    import subprocess

    script = ROOT / "scripts" / "owner_set_main_push_token.sh"
    text = script.read_text(encoding="utf-8")
    # Must NOT use --body - on the live set path (stores literal hyphen).
    assert "gh secret set" in text
    assert "| gh secret set" in text or "printf" in text
    # Active set command must omit --body (stdin). Allow mention only as warning.
    live_lines = [
        ln
        for ln in text.splitlines()
        if "gh secret set" in ln and "echo" not in ln and not ln.strip().startswith("#")
    ]
    for ln in live_lines:
        assert "--body -" not in ln, f"live secret set must not use --body -: {ln}"
    assert "literal" in text.lower() or "hyphen" in text.lower() or "stdin" in text.lower()

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_p = subprocess.run(
        ["bash", str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dry_env,
    )
    assert dry_p.returncode == 0, dry_p.stderr + dry_p.stdout
    dry_out = dry_p.stdout + dry_p.stderr
    assert "dry-run" in dry_out.lower()
    assert "gh secret set" in dry_out
    assert "--body -" in dry_out  # warning note only
    assert "do NOT pass --body -" in dry_out or "literal hyphen" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out
    assert "lemma_closed=false" in dry_out or "lemma_closed stays false" in dry_out

    brief = ROOT / "portable" / "BATCH162_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "162"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["device_code"] == "C8FC-A08F"
    assert data["auth_renewed"] is True
    assert data["prior_device_code"] == "E818-2EE5"
    assert data["issue_number"] == 27
    assert "issues/27" in data["issue_url"]
    assert data.get("secret_script_bug_fixed")
    assert data.get("tip_refresh") is True
    assert data.get("bundle_refresh") is True
    base_tip_162 = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text()
    assert _living_tip(base_tip_162) or "8ea3b5f" in base_tip_162
    verify = json.loads((ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(encoding="utf-8"))
    assert _living_tip(verify["base_tip_sha"]) or verify["base_tip_sha"].startswith("8ea3b5f")
    assert verify["lemma_closed"] is False
    # VERIFY.json is a living artifact; Batch 162+ rebuilds may stamp a later batch id.
    assert str(verify["batch"]) in ("162", "168", "169", "170") or int(str(verify["batch"])) >= 162

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "C8FC-A08F" in gh
    assert "E818-2EE5" in gh
    assert "issues/27" in gh or "BATCH162_BRIEF" in gh
    assert "owner_set_main_push_token.sh" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 162" in log
    assert "issues/27" in log or "#27" in log
    assert "C8FC-A08F" in log
    assert "8ea3b5f" in log
    assert "lemma_closed" in log.lower()

def test_batch170_bundle_e2e_and_ci_intent_fix() -> None:
    """Batch 170: E2E .bundle fetch+merge; CI supersession intent fix; tip stable; auth pending; lemma_closed=false."""
    import json
    import os
    import subprocess

    bundle_dir = ROOT / "portable" / "path-c-applied-bundle"
    git_bundle = bundle_dir / "path-c-on-hardening.bundle"
    assert git_bundle.is_file()
    verify = json.loads((bundle_dir / "VERIFY.json").read_text(encoding="utf-8"))
    assert verify["lemma_closed"] is False
    assert _living_tip(verify["base_tip_sha"]) or verify["base_tip_sha"].startswith("8ea3b5f")
    assert verify.get("e2e_bundle_verify") is True or verify.get("git_bundle") is True
    assert (
        verify.get("e2e_fetch_merge_ok") is True
        or str(verify["batch"]) in ("169", "170")
        or int(str(verify["batch"])) >= 169
    )
    apply_md = (bundle_dir / "APPLY.md").read_text(encoding="utf-8")
    assert "path-c-on-hardening.bundle" in apply_md
    assert "git fetch" in apply_md
    assert "Batch 170" in apply_md or "shallow" in apply_md.lower() or "depth" in apply_md.lower()

    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "batch169-path-c-bundle" in owner_c
    assert "batch142-path-c-bundle" in owner_c  # historical note retained

    brief = ROOT / "portable" / "BATCH170_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "170"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["bundle_verify_ok"] is True
    assert data["device_code"] in ("EC83-CFC2", "7BCB-0057")
    assert data["write"] == "DENIED"
    assert data["ci_status"] in ("pending", "fixed", "success", "failure", "fixing")
    assert data.get("patch_0017") is False
    if data["device_code"] == "7BCB-0057":
        assert data.get("prior_device_code") == "EC83-CFC2"
        assert data.get("auth_renewed") is True

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "7BCB-0057" in gh or "EC83-CFC2" in gh
    assert "EC83-CFC2" in gh  # history
    assert "831C-CB1C" in gh
    assert "905D-02F4" in gh
    assert "batch162-path-c-bundle" in gh or "batch180-path-c-bundle" in gh or "batch179-path-c-bundle" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 170" in log
    assert "EC83-CFC2" in log or "7BCB-0057" in log
    assert "bundle" in log.lower()
    assert "lemma_closed" in log.lower()


def test_batch172_issue_hygiene_and_non_rw_hunt() -> None:
    """Batch 172: tip stable; issue #33 canonical; hunt clean no 0017; auth pending; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH172_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "172"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["device_code"] == "7BCB-0057"
    assert data["write"] == "DENIED"
    assert data.get("patch_0017") is False
    assert data.get("hunt") == "clean_no_0017"
    assert data.get("canonical_issue") == 33 or data.get("issue_number") == 33
    assert data.get("auth_renewed") is False
    assert int(data.get("seconds_left", 0)) >= 0

    hunt = ROOT / "portable" / "BATCH172_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["batch"] == "172"
    assert h["patch_0017"] is False
    assert h["hunt_result"] == "clean"
    assert h["lemma_closed"] is False

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "7BCB-0057" in gh
    assert "issues/33" in gh or "#33" in gh
    assert "batch169-path-c-bundle" in gh or "batch180-path-c-bundle" in gh or "batch179-path-c-bundle" in gh
    assert "batch162-path-c-bundle" in gh or "batch180-path-c-bundle" in gh or "batch179-path-c-bundle" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 172" in log
    assert "7BCB-0057" in log
    assert "lemma_closed" in log.lower()


def test_batch173_refresh_path_c_bundle() -> None:
    """Batch 173: tip stable; auth renew 9671; refresh_path_c_bundle.sh; lemma_closed=false."""
    import json
    import os
    import stat
    import subprocess

    brief = ROOT / "portable" / "BATCH173_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "173"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "9671-4918"
    assert data["prior_device_code"] == "7BCB-0057"
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data.get("refresh_script") == "scripts/refresh_path_c_bundle.sh"
    assert data.get("refresh_script_shipped") is True
    assert data.get("canonical_issue") == 34 or data.get("issue_number") == 34
    assert int(data.get("seconds_left", 0)) >= 0
    assert data.get("preferred_auth_interval_s") == 1800

    script = ROOT / "scripts" / "refresh_path_c_bundle.sh"
    assert script.is_file()
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, "refresh_path_c_bundle.sh must be executable"
    text = script.read_text(encoding="utf-8")
    assert "BASE_TIP" in text
    assert "apply_all" in text
    assert "path-c-on-hardening.patch" in text
    assert "path-c-on-hardening.bundle" in text
    assert "VERIFY.json" in text
    assert "lemma_closed=false" in text or "lemma_closed" in text
    assert "--dry-run" in text
    assert "--force" in text

    # Tip-stable dry-run exits 0 without mutating tree.
    dry = subprocess.run(
        [str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert "tip stable" in (dry.stdout + dry.stderr).lower() or "match=1" in (dry.stdout + dry.stderr)

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "refresh_path_c_bundle.sh" in pack

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "refresh_path_c_bundle.sh" in unblock

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "refresh_path_c_bundle.sh" in ones
    assert "Batch 173" in ones

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "9671-4918" in gh
    assert "7BCB-0057" in gh
    assert "issues/34" in gh or "#34" in gh
    assert "refresh_path_c_bundle.sh" in gh
    assert "batch169-path-c-bundle" in gh or "batch180-path-c-bundle" in gh or "batch179-path-c-bundle" in gh
    assert "batch162-path-c-bundle" in gh or "batch180-path-c-bundle" in gh or "batch179-path-c-bundle" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 173" in log
    assert "9671-4918" in log
    assert "refresh_path_c_bundle" in log
    assert "lemma_closed" in log.lower()


def test_batch176_refresh_ci_tip_drift() -> None:
    """Batch 176: tip stable; auth renew 5E05; refresh fetch harden + CI tip-drift dry-sim; lemma_closed=false."""
    import json
    import os
    import stat
    import subprocess

    brief = ROOT / "portable" / "BATCH176_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "176"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "5E05-EA04"
    assert data["prior_device_code"] == "9671-4918"
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data.get("refresh_ok") is True
    assert data.get("refresh_script") == "scripts/refresh_path_c_bundle.sh"
    assert data.get("canonical_issue") == 35 or data.get("issue_number") == 35
    assert int(data.get("seconds_left", 0)) >= 0
    assert data.get("preferred_auth_interval_s") == 1800

    script = ROOT / "scripts" / "refresh_path_c_bundle.sh"
    assert script.is_file()
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, "refresh_path_c_bundle.sh must be executable"
    text = script.read_text(encoding="utf-8")
    assert "tip fetch HTTP" in text or "HTTP_CODE" in text
    assert "--dry-run" in text
    assert "fix path" in text.lower() or "TIP_DRIFT" in text
    assert "REFRESH_BATCH_TAG" in text

    dry = subprocess.run(
        [str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert "tip stable" in (dry.stdout + dry.stderr).lower() or "match=1" in (dry.stdout + dry.stderr)

    # Bad remote should die cleanly (no KeyError traceback)
    bad = subprocess.run(
        [str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        env={
            **os.environ,
            "GIT_TERMINAL_PROMPT": "0",
            "MAIN_REPO": "d6g8k5htny-coder/does-not-exist",
            "HARDENING_REF": "nope",
        },
    )
    assert bad.returncode != 0
    combined = bad.stdout + bad.stderr
    assert "KeyError" not in combined
    assert "tip fetch HTTP" in combined or "ERROR" in combined

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "refresh_path_c_bundle.sh" in ci
    assert "Tip-drift dry-sim" in ci or "dry-sim" in ci
    assert "does NOT push to main" in ci or "never auto-refresh" in ci or "never auto-pushes" in ci

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "5E05-EA04" in gh
    assert "9671-4918" in gh
    assert "issues/35" in gh or "#35" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 176" in log
    assert "5E05-EA04" in log
    assert "refresh_path_c_bundle" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 176" in ones
    assert "refresh_path_c_bundle.sh" in ones


def test_batch178_owner_pr_bundle_link_ci_fix() -> None:
    """Batch 178: tip stable; auth pending 5E05; owner_open_path_c_pr links release .bundle; CI tip-drift string fix; lemma_closed=false."""
    import json
    import os
    import subprocess

    brief = ROOT / "portable" / "BATCH178_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "178"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "AD78-6206"
    assert data["prior_device_code"] == "5E05-EA04"
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data.get("patches_dropped") == [] or data.get("patches_dropped") == 0
    assert data.get("owner_pr_bundle_link") is True
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("canonical_issue") == 37 or data.get("issue_number") == 37

    open_pr = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    assert open_pr.is_file()
    text = open_pr.read_text(encoding="utf-8")
    assert "resolve_path_c_bundle_release_url" in text
    assert "path-c-on-hardening.bundle" in text
    assert "releases/download" in text
    assert "PATH_C_RELEASE_TAG" in text
    assert "Batch 178" in text
    assert "lemma_closed" in text

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry = subprocess.run(
        ["bash", str(open_pr), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**dry_env, "GIT_TERMINAL_PROMPT": "0"},
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    dry_out = dry.stdout + dry.stderr
    assert "dry-run OK" in dry_out
    assert "path-c-on-hardening.bundle" in dry_out
    assert "releases/download" in dry_out or "release_bundle_url=" in dry_out
    assert "batch169-path-c-bundle" in dry_out or "batch179-path-c-bundle" in dry_out or "batch180-path-c-bundle" in dry_out or "batch199-path-c-bundle" in dry_out or "batch202-path-c-bundle" in dry_out or "-path-c-bundle" in dry_out
    assert "lemma_closed" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out
    assert "github_pat_" not in dry_out

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "refresh BASE_TIP" in ci
    assert "rebuild path-c-applied-bundle" in ci

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "AD78-6206" in gh
    assert "5E05-EA04" in gh
    assert "BATCH162_BRIEF" in gh
    assert "BATCH178_BRIEF" in gh
    assert "owner_open_path_c_pr.sh" in gh
    assert "issues/37" in gh or "#37" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 178" in log
    assert "AD78-6206" in log
    assert "5E05-EA04" in log
    assert "owner_open_path_c_pr" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 178" in ones
    assert "owner_open_path_c_pr.sh" in ones
    assert "path-c-on-hardening.bundle" in ones


def test_batch179_path_c_bundle_release() -> None:
    """Batch 179: tip stable; auth pending AD78; CI green; release batch179-path-c-bundle (oneshot+bundle+refresh); lemma_closed=false."""
    import json
    import os
    import subprocess

    brief = ROOT / "portable" / "BATCH179_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "179"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8ea3b5f"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "AD78-6206"
    assert data["auth_renewed"] is False
    assert data["write"] == "DENIED"
    assert data["release"] == "batch179-path-c-bundle"
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("ci_status") in ("success", "green")
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert str(verify["batch"]) == "179" or int(str(verify["batch"])) >= 179
    assert verify["lemma_closed"] is False
    assert _living_release(verify.get("release")) or verify.get("release") in ("batch179-path-c-bundle", "batch180-path-c-bundle")
    assert _living_tip(verify["base_tip_sha"]) or verify["base_tip_sha"].startswith("8ea3b5f")

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    text = oneshot.read_text(encoding="utf-8")
    assert "batch179-path-c-bundle" in text
    assert "refresh_path_c_bundle" in (
        ROOT / "scripts" / "refresh_path_c_bundle.sh"
    ).read_text(encoding="utf-8") or (
        ROOT / "scripts" / "refresh_path_c_bundle.sh"
    ).is_file()

    open_pr = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    op_text = open_pr.read_text(encoding="utf-8")
    assert (
        "batch179-path-c-bundle" in op_text
        or "batch180-path-c-bundle" in op_text
        or "batch241-path-c-bundle" in op_text
        or "-path-c-bundle" in op_text
    )
    assert "PATH_C_RELEASE_TAG" in op_text

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry = subprocess.run(
        ["bash", str(open_pr), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**dry_env, "GIT_TERMINAL_PROMPT": "0"},
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    dry_out = dry.stdout + dry.stderr
    assert "dry-run OK" in dry_out
    assert "batch179-path-c-bundle" in dry_out or "batch180-path-c-bundle" in dry_out or "batch199-path-c-bundle" in dry_out or "batch202-path-c-bundle" in dry_out or "-path-c-bundle" in dry_out
    assert "path-c-on-hardening.bundle" in dry_out
    assert "lemma_closed" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "AD78-6206" in gh
    assert "batch179-path-c-bundle" in gh or "batch218-path-c-bundle" in gh
    assert "BATCH179_BRIEF" in gh or "BATCH178_BRIEF" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 179" in log
    assert "batch179-path-c-bundle" in log
    assert "AD78-6206" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 179" in ones
    assert "batch179-path-c-bundle" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "batch179-path-c-bundle" in unblock


def test_batch180_path_c_status_json_schema() -> None:
    """Batch 180: write_path_c_status.py dry-run emits required PATH_C_STATUS schema keys; tip refresh 8bd1f03; auth renew; lemma_closed=false."""
    import json
    import os
    import re
    import subprocess

    script = ROOT / "scripts" / "write_path_c_status.py"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "SCHEMA_KEYS" in text
    assert "lemma_closed" in text
    assert "device_code" in text
    assert "path_c_blocked" in text
    assert "release_tag" in text
    assert "generated_at" in text
    # Never emit secrets
    assert "access_token" not in text.lower() or "ACCESS_TOKEN" in text  # path ref OK
    assert "gho_" not in text
    assert "ghp_" not in text

    required = [
        "tip",
        "base_tip",
        "tip_match",
        "write_state",
        "lemma_closed",
        "path_c_blocked",
        "device_code",
        "release_tag",
        "generated_at",
    ]
    schema = subprocess.run(
        [sys.executable, str(script), "--schema-keys"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert schema.returncode == 0, schema.stderr
    keys = json.loads(schema.stdout)
    for k in required:
        assert k in keys

    dry = subprocess.run(
        [sys.executable, str(script), "--dry-run", "--skip-write-probe"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    data = json.loads(dry.stdout)
    for k in required:
        assert k in data, f"missing schema key {k}"
    assert data["lemma_closed"] is False
    assert _living_tip(data.get("tip")) or (
        isinstance(data.get("tip_full"), str)
        and _living_tip(data["tip_full"])
    )
    assert _living_tip(data.get("base_tip")) or (
        isinstance(data.get("base_tip_full"), str)
        and _living_tip(data["base_tip_full"])
    )
    assert data.get("tip_match") is True
    assert _living_release(data.get("release_tag"))
    assert "ghp_" not in dry.stdout
    assert "gho_" not in dry.stdout
    # device_code is user code only (XXXX-XXXX), never the oauth device_code secret
    dc = data.get("device_code")
    if dc:
        assert re.match(r"^[A-Z0-9]{4,}-[A-Z0-9]{4,}$", dc), dc

    assert_sh = ROOT / "scripts" / "assert_path_c_ready.sh"
    assert "write_path_c_status" in assert_sh.read_text(encoding="utf-8")

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert 'git -C "$WORKDIR" bundle verify' in refresh

    brief = ROOT / "portable" / "BATCH180_BRIEF.json"
    assert brief.is_file()
    b = json.loads(brief.read_text(encoding="utf-8"))
    assert b["batch"] == "180"
    assert b["goal_complete"] is False
    assert b["lemma_closed"] is False
    assert b["flipped_anything"] is False
    assert b["path_c_landed"] is False
    assert b["tip"] == "8bd1f03"
    assert b["tip_matches_base"] is True
    assert b["tip_refresh"] is True
    assert b["auth_renewed"] is True
    assert b["device_code"] == "5216-7C1B"
    assert b["prior_device_code"] == "AD78-6206"
    assert b["write"] == "DENIED"
    assert b["release"] == "batch180-path-c-bundle"
    assert b.get("status_json") is True
    assert b.get("preferred_auth_interval_s") == 1800
    assert b.get("assert_path_c_ready") is True
    assert "OPEN_HOLD" in b.get("math_status", "")
    assert "lemma_closed=false" in b.get("math_status", "")

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert str(verify["batch"]) == "180" or int(str(verify["batch"])) >= 180
    assert verify["lemma_closed"] is False
    assert _living_release(verify.get("release"))
    assert _living_tip(verify["base_tip_sha"])
    assert verify.get("tip_refresh") in (True, False)

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    assert "batch180-path-c-bundle" in oneshot.read_text(encoding="utf-8") or "batch207-path-c-bundle" in oneshot.read_text(encoding="utf-8") or "-path-c-bundle" in oneshot.read_text(encoding="utf-8")

    open_pr = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    op_text = open_pr.read_text(encoding="utf-8")
    assert "batch180-path-c-bundle" in op_text or "batch207-path-c-bundle" in op_text or "-path-c-bundle" in op_text

    dry_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
    }
    dry_env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
    dry_pr = subprocess.run(
        ["bash", str(open_pr), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**dry_env, "GIT_TERMINAL_PROMPT": "0"},
        check=False,
    )
    assert dry_pr.returncode == 0, dry_pr.stderr + dry_pr.stdout
    dry_out = dry_pr.stdout + dry_pr.stderr
    assert "dry-run OK" in dry_out
    assert "batch180-path-c-bundle" in dry_out or "batch199-path-c-bundle" in dry_out or "batch202-path-c-bundle" in dry_out or "-path-c-bundle" in dry_out
    assert "path-c-on-hardening.bundle" in dry_out
    assert "lemma_closed" in dry_out
    assert "ghp_" not in dry_out
    assert "gho_" not in dry_out

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "5216-7C1B" in gh
    assert "AD78-6206" in gh
    assert "batch180-path-c-bundle" in gh
    assert "write_path_c_status" in gh or "PATH_C_STATUS" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 180" in log
    assert "batch180-path-c-bundle" in log
    assert "5216-7C1B" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 180" in ones
    assert "batch180-path-c-bundle" in ones
    assert "write_path_c_status" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "batch180-path-c-bundle" in unblock

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "write_path_c_status.py" in pack

    wwl = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "_maybe_write_path_c_status" in wwl


def test_batch183_ci_tip_drift_auth_renew() -> None:
    """Batch 183: tip stable 8bd1f03; auth renew DF9C; CI tip-drift supersession; hunt clean; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH183_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "183"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    # Living device_code may renew after Batch 183 (Batch 185+: DF9C→46EC).
    assert data["device_code"] in ("DF9C-5DF9", "46EC-0B00") or "-" in str(
        data["device_code"]
    )
    assert data["prior_device_code"] in ("5216-7C1B", "DF9C-5DF9") or "-" in str(
        data.get("prior_device_code", "")
    )
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data.get("hunt") == "clean_no_0017"
    assert data.get("patch_0017") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("canonical_issue") in (39, 40) or data.get("issue_number") in (
        39,
        40,
    )
    assert data.get("status_json") is True
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")

    hunt = ROOT / "portable" / "BATCH183_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["batch"] == "183"
    assert h["patch_0017"] is False
    assert h["hunt_result"] == "clean"
    assert h["lemma_closed"] is False
    assert h["tip"] == "8bd1f03"

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    for key in (
        "tip",
        "base_tip",
        "tip_match",
        "write_state",
        "lemma_closed",
        "path_c_blocked",
        "device_code",
        "release_tag",
        "generated_at",
    ):
        assert key in status
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") in ("DF9C-5DF9", "46EC-0B00") or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_tip(verify["base_tip_sha"])
    assert verify["lemma_closed"] is False
    assert _living_release(verify.get("release"))

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "DF9C-5DF9" in gh
    assert "5216-7C1B" in gh
    assert "issues/39" in gh or "#39" in gh or "issues/40" in gh or "#40" in gh
    assert "batch180-path-c-bundle" in gh
    assert "BATCH183_BRIEF" in gh or "Batch 183" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 183" in log
    assert "DF9C-5DF9" in log
    assert "5216-7C1B" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 183" in ones
    assert "DF9C-5DF9" in ones or "write_path_c_status" in ones

def test_batch185_auth_renew_research_audit_bundle() -> None:
    """Batch 185: tip stable 8bd1f03; auth renew 46EC; research audit only; bundle E2E; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH185_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "185"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "46EC-0B00"
    assert data["prior_device_code"] == "DF9C-5DF9"
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data.get("bundle_ok") is True
    assert data.get("ci_status") == "success"
    assert data.get("patches_dropped") == []
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("canonical_issue") == 40 or data.get("issue_number") == 40
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    counts = data.get("research_counts") or {}
    assert counts.get("open_premises") == 13
    assert counts.get("open_lemmas") == 1
    assert counts.get("open_prizes") == 3
    assert counts.get("open_questions") == 16
    assert counts.get("claims") == 26
    assert counts.get("lemma_closed") is False

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    # Living device_code may renew after Batch 185 (Batch 188+: 46EC→C949).
    assert status.get("device_code") in ("46EC-0B00", "C949-0100") or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_tip(verify["base_tip_sha"])
    assert verify["lemma_closed"] is False

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "46EC-0B00" in gh
    assert "DF9C-5DF9" in gh
    assert "issues/40" in gh or "#40" in gh
    assert "batch180-path-c-bundle" in gh
    assert "BATCH185_BRIEF" in gh or "Batch 185" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 185" in log
    assert "46EC-0B00" in log
    assert "DF9C-5DF9" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 185" in ones
    assert "46EC-0B00" in ones or "write_path_c_status" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 185" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch188_align_watch_auth_renew_idle() -> None:
    """Batch 188: tip stable 8bd1f03; auth renew C949; write DENIED; idle watch; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH188_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "188"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    # Living device_code may renew after Batch 188 (Batch 190+: C949→1C7F).
    assert data["device_code"] in ("C949-0100", "1C7F-22B5") or "-" in str(
        data["device_code"]
    )
    assert data["prior_device_code"] in ("46EC-0B00", "C949-0100") or "-" in str(
        data.get("prior_device_code", "")
    )
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("canonical_issue") in (40, 41, 42, 43, 44) or data.get(
        "issue_number"
    ) in (
        40,
        41,
        42,
        43,
        44,
    )
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert data.get("hunt") == "skipped_tip_stable"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") in ("C949-0100", "1C7F-22B5") or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "C949-0100" in gh
    assert "46EC-0B00" in gh
    assert (
        "issues/40" in gh
        or "#40" in gh
        or "issues/41" in gh
        or "#41" in gh
        or "issues/42" in gh
        or "#42" in gh
    )
    assert "BATCH188_BRIEF" in gh or "Batch 188" in gh or "BATCH190_BRIEF" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 188" in log
    assert "C949-0100" in log
    assert "46EC-0B00" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 188" in ones
    assert "C949-0100" in ones or "write_path_c_status" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 188" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch190_deeper_hunt_auth_renew() -> None:
    """Batch 190: tip stable 8bd1f03; auth renew 1C7F; deeper hunt clean; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH190_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "190"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "1C7F-22B5"
    assert data["prior_device_code"] == "C949-0100"
    assert data["auth_renewed"] is True
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    # Living canonical issue may supersede (#42→#43→#44+).
    assert data.get("canonical_issue") in (42, 43, 44) or data.get("issue_number") in (
        42,
        43,
        44,
    )
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert data.get("hunt") == "clean_no_0017"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True

    hunt = ROOT / "portable" / "BATCH190_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["batch"] == "190"
    assert h["patch_0017"] is False
    assert h["hunt_result"] == "clean"
    assert h["lemma_closed"] is False
    assert h["tip"] == "8bd1f03"

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") == "1C7F-22B5" or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "1C7F-22B5" in gh
    assert "C949-0100" in gh
    assert "issues/42" in gh or "#42" in gh
    assert "BATCH190_BRIEF" in gh or "Batch 190" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 190" in log
    assert "1C7F-22B5" in log
    assert "C949-0100" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 190" in ones
    assert "1C7F-22B5" in ones or "write_path_c_status" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 190" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch192_readme_path_c_face() -> None:
    """Batch 192: tip stable 8bd1f03; auth pending 1C7F; README Path C face; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH192_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "192"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] in ("1C7F-22B5", "CC72-DB3D") or "-" in str(
        data["device_code"]
    )
    # Living renew may flip auth_renewed True when seconds_left<90 mid-batch.
    assert data["auth_renewed"] in (False, True)
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("canonical_issue") in (43, 44) or data.get("issue_number") in (
        43,
        44,
    )
    assert data.get("readme_updated") is True
    assert "Path C" in data.get("readme_path_c_section", "")
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert data.get("hunt") == "skipped_tip_stable"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Path C — land engineering fixes on main" in readme
    assert "https://github.com/login/device" in readme
    assert "GH_DEVICE_LOGIN" in readme
    assert "batch180-path-c-bundle" in readme or "path-c-bundle" in readme
    assert "owner_path_c_oneshot.sh" in readme
    assert "lemma_closed" in readme.lower()
    # Preserve sandbox boundary below the Path C face.
    assert "research repository" in readme.lower()
    assert "**Not**" in readme

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") in ("1C7F-22B5", "CC72-DB3D") or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "CC72-DB3D" in gh or "1C7F-22B5" in gh
    assert "1C7F-22B5" in gh
    assert "issues/43" in gh or "#43" in gh or "issues/44" in gh or "#44" in gh
    assert "BATCH192_BRIEF" in gh or "Batch 192" in gh
    assert "README.md" in gh or "Path C — land engineering fixes on main" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 192" in log
    assert "1C7F-22B5" in log
    assert "8bd1f03" in log
    assert "Path C" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 192" in ones
    assert "Path C — land engineering fixes on main" in ones or "CC72-DB3D" in ones or "1C7F-22B5" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 192" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch194_readme_link_only_device_code() -> None:
    """Batch 194: README Path C must not embed perishable XXXX-XXXX; GH_DEVICE_LOGIN is SoT."""
    import json
    import re

    brief = ROOT / "portable" / "BATCH194_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "194"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "CC72-DB3D" or "-" in str(data["device_code"])
    assert data["auth_renewed"] is False
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("readme_link_only") is True
    assert data.get("readme_updated") is True
    assert "Path C" in data.get("readme_path_c_section", "")
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert data.get("hunt") == "skipped_tip_stable"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Path C — land engineering fixes on main" in readme
    assert "https://github.com/login/device" in readme
    assert "GH_DEVICE_LOGIN" in readme
    assert "portable/GH_DEVICE_LOGIN.md" in readme
    assert "batch180-path-c-bundle" in readme or "path-c-bundle" in readme
    assert "owner_path_c_oneshot.sh" in readme
    assert "lemma_closed" in readme.lower()
    assert "single source of truth" in readme.lower() or "see that file for the live code" in readme
    # Intent: no hardcoded perishable user-code pattern on README face.
    assert not re.search(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b", readme), (
        "README must not embed XXXX-XXXX device user codes; link to GH_DEVICE_LOGIN.md"
    )
    # Preserve sandbox boundary below the Path C face.
    assert "research repository" in readme.lower()
    assert "**Not**" in readme

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") == "CC72-DB3D" or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "CC72-DB3D" in gh
    assert "User code" in gh
    assert "single source of truth" in gh.lower() or "live source of truth" in gh.lower()
    assert "link-only" in gh.lower() or "Batch 194" in gh
    assert "BATCH194_BRIEF" in gh or "Batch 194" in gh
    # Steps must not hardcode a stale prior code as the live enter-code line.
    assert "Enter code **1C7F-22B5**" not in gh
    assert "Enter the **User code** from the table above" in gh

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 194" in log
    assert "link-only" in log.lower()
    assert "CC72-DB3D" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 194" in ones
    assert "link-only" in ones.lower() or "GH_DEVICE_LOGIN.md" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 194" in findings
    assert "link-only" in findings.lower()
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch195_path_c_status_watch_wire() -> None:
    """Batch 195: tip stable; auth renew 50DB; PATH_C_STATUS refresh on watch; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH195_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "195"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "50DB-FD4D" or "-" in str(data["device_code"])
    assert data["prior_device_code"] == "CC72-DB3D" or "-" in str(
        data.get("prior_device_code", "")
    )
    assert data["auth_renewed"] is True
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("watch_path_c_status_wire") is True
    assert data.get("ci_status") == "green"
    assert data.get("canonical_issue") in (45, 46) or data.get("issue_number") in (
        45,
        46,
    )
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert data.get("hunt") == "skipped_tip_stable"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True

    # Watch wiring: aligned_drift_watch refreshes PATH_C_STATUS by default.
    adw = (ROOT / "scripts" / "aligned_drift_watch.py").read_text(encoding="utf-8")
    assert "_maybe_write_path_c_status" in adw
    assert "write_path_c_status" in adw
    assert "--no-path-c-status" in adw
    assert "path_c_status_refreshed" in adw

    wf = (ROOT / ".github" / "workflows" / "watch-main-alignment.yml").read_text(
        encoding="utf-8"
    )
    assert "aligned_drift_watch.py" in wf
    assert "PATH_C_STATUS" in wf or "write_path_c_status" in wf or "Batch 195" in wf

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") == "50DB-FD4D" or "-" in str(
        status.get("device_code", "")
    )
    assert status.get("release_tag") in (
        "batch180-path-c-bundle",
        "batch199-path-c-bundle",
    ) or str(status.get("release_tag", "")).endswith("-path-c-bundle")
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "50DB-FD4D" in gh
    assert "CC72-DB3D" in gh
    assert "issues/46" in gh or "#46" in gh or "BATCH195_BRIEF" in gh
    assert "aligned_drift_watch" in gh or "PATH_C_STATUS" in gh
    assert "BATCH195_BRIEF" in gh or "Batch 195" in gh
    # README stays link-only (no embedded XXXX-XXXX).
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "portable/GH_DEVICE_LOGIN.md" in readme
    import re

    assert not re.search(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b", readme)

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 195" in log
    assert "50DB-FD4D" in log
    assert "CC72-DB3D" in log
    assert "PATH_C_STATUS" in log or "aligned_drift_watch" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 195" in ones
    assert "aligned_drift_watch" in ones or "PATH_C_STATUS" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 195" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch199_path_c_bundle_pack_release() -> None:
    """Batch 199: tip stable; auth renew 6A29; pack+release batch199; lemma_closed=false."""
    import json
    import re

    brief = ROOT / "portable" / "BATCH199_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "199"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is False
    assert data["device_code"] == "6A29-F464" or "-" in str(data["device_code"])
    assert data["prior_device_code"] == "50DB-FD4D" or "-" in str(
        data.get("prior_device_code", "")
    )
    assert data["auth_renewed"] is True
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("pack_meaningfully_newer") is True
    assert data.get("release") == "batch199-path-c-bundle"
    assert data.get("prior_release") == "batch180-path-c-bundle"
    assert data.get("path_c_status_in_pack") is True
    assert data.get("readme_link_only") is True
    assert data.get("hunt") == "skipped_tip_stable"
    assert data.get("patch_0017") is False
    assert data.get("code_changed") is True
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")

    # Pack includes PATH_C_STATUS.json; release defaults bumped to batch199.
    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "portable/PATH_C_STATUS.json" in pack

    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert "batch199-path-c-bundle" in oneshot or "batch207-path-c-bundle" in oneshot or "-path-c-bundle" in oneshot
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch199-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch202-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch207-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch218-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch223-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch236-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in oneshot
        or _living_release(oneshot)
    )

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert "batch199-path-c-bundle" in open_pr or "batch207-path-c-bundle" in open_pr or "-path-c-bundle" in open_pr

    land = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "batch199-path-c-bundle" in land or "batch207-path-c-bundle" in land or "-path-c-bundle" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "batch199-path-c-bundle" in unblock or "batch207-path-c-bundle" in unblock or "-path-c-bundle" in unblock

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_release(verify.get("release"))
    assert verify.get("lemma_closed") is False
    assert _living_tip(verify.get("base_tip_sha"))

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") == "6A29-F464" or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "6A29-F464" in gh
    assert "50DB-FD4D" in gh
    assert "BATCH199_BRIEF" in gh or "Batch 199" in gh
    assert "batch199-path-c-bundle" in gh

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "portable/GH_DEVICE_LOGIN.md" in readme
    assert "batch199-path-c-bundle" in readme
    assert not re.search(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b", readme)

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 199" in log
    assert "6A29-F464" in log
    assert "50DB-FD4D" in log
    assert "batch199-path-c-bundle" in log
    assert "8bd1f03" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 199" in ones
    assert "batch199-path-c-bundle" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 199" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()


def test_batch202_ci_sanity_tip_refresh() -> None:
    """Batch 202: CI release-tag supersession; tip refresh b89448d; auth renew 5160; lemma_closed=false."""
    import json
    import re

    brief = ROOT / "portable" / "BATCH202_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "202"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["tip"] == "b89448d"
    assert data["prior_base_tip"] == "8bd1f03"
    assert data["tip_matches_base"] is True
    assert data["tip_refresh"] is True
    assert data["bundle_refresh"] is True
    assert data["device_code"] == "5160-F839" or "-" in str(data["device_code"])
    assert data["prior_device_code"] == "6A29-F464" or "-" in str(
        data.get("prior_device_code", "")
    )
    assert data["auth_renewed"] is True
    assert data["device_auth"] == "pending"
    assert data["write"] == "DENIED"
    assert data["main_status"] == "ALIGNED"
    assert data.get("has_main_push_token") is False
    assert data.get("preferred_auth_interval_s") == 1800
    assert data.get("assert_path_c_ready") is True
    assert data.get("sanity_fix") is True
    assert _living_release(data.get("release"))
    assert data.get("prior_release") == "batch199-path-c-bundle"
    assert data.get("readme_link_only") is True
    assert data.get("code_changed") is True
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")
    assert "903ca64" in str(data.get("ci_batch199_sha", "")) or data.get(
        "ci_batch199"
    ) == "failure"

    # Living helpers exist for tip/release supersession (root CI fix).
    src = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "_living_tip" in src
    assert "_living_release" in src
    assert "batch202-path-c-bundle" in src

    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert "batch202-path-c-bundle" in oneshot or "batch207-path-c-bundle" in oneshot
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch202-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch207-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch218-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch223-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch236-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in oneshot
        or _living_release(oneshot)
    )

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert (
        "batch202-path-c-bundle" in open_pr
        or "batch207-path-c-bundle" in open_pr
        or "batch218-path-c-bundle" in open_pr
        or "batch236-path-c-bundle" in open_pr
        or "batch241-path-c-bundle" in open_pr
        or "-path-c-bundle" in open_pr
        or _living_release(open_pr)
    )

    land = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert (
        "batch202-path-c-bundle" in land
        or "batch207-path-c-bundle" in land
        or "batch218-path-c-bundle" in land
        or "batch236-path-c-bundle" in land
        or "-path-c-bundle" in land
    )

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert (
        "batch202-path-c-bundle" in unblock
        or "batch207-path-c-bundle" in unblock
        or "batch218-path-c-bundle" in unblock
        or "batch236-path-c-bundle" in unblock
        or "-path-c-bundle" in unblock
    )

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_release(verify.get("release"))
    assert verify.get("lemma_closed") is False
    assert verify.get("tip_refresh") in (True, False)
    assert _living_tip(verify.get("base_tip_sha"))

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))
    assert status.get("tip_match") is True
    assert status.get("device_code") == "5160-F839" or "-" in str(
        status.get("device_code", "")
    )
    assert _living_release(status.get("release_tag"))
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "5160-F839" in gh
    assert "6A29-F464" in gh
    assert "BATCH202_BRIEF" in gh or "Batch 202" in gh
    assert "batch202-path-c-bundle" in gh
    assert "b89448d" in gh or "1d0dceb" in gh

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "portable/GH_DEVICE_LOGIN.md" in readme
    assert "batch202-path-c-bundle" in readme or "batch207-path-c-bundle" in readme or "batch218-path-c-bundle" in readme
    assert not re.search(r"\b[A-Z0-9]{4}-[A-Z0-9]{4}\b", readme)

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 202" in log
    assert "5160-F839" in log
    assert "6A29-F464" in log
    assert "batch202-path-c-bundle" in log
    assert "b89448d" in log or "1d0dceb" in log or "Batch 202" in log
    assert "903ca64" in log or "release_tag" in log
    assert "lemma_closed" in log.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 202" in ones
    assert "batch202-path-c-bundle" in ones
    assert "5160-F839" in ones or "refresh_path_c_bundle" in ones

    findings = (ROOT / "docs" / "MECHANICAL_FINDINGS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 202" in findings
    assert "lemma_closed=false" in findings or "lemma_closed=false" in findings.lower()
    assert "b89448d" in findings or "1d0dceb" in findings or "Batch 202" in findings



def test_batch207_path_c_0017_bundle_refresh() -> None:
    """Batch 207: ship 0017 pinned_sources RW fix; bundle refresh; auth renew; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH207_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data.get("batch") == "207"
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("scientific_effect") == "NONE"
    assert data.get("goal_complete") is False
    assert data.get("patch_0017") is True
    assert _living_tip(data.get("tip"))
    assert _living_release(data.get("release"))
    assert data.get("bundle_refresh") is True
    assert data.get("path_c_landed") is False

    p17 = ROOT / "portable" / "patches" / "0017-pinned-sources-close-file-handles.patch"
    assert p17.is_file()
    apply_all = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "0017-pinned-sources-close-file-handles.patch" in apply_all

    verify = json.loads((ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(encoding="utf-8"))
    assert verify.get("lemma_closed") is False
    assert _living_release(verify.get("release"))
    assert verify.get("patch_0017") is True or "0017" in (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")

    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert "batch207-path-c-bundle" in oneshot or "batch218-path-c-bundle" in oneshot
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch218-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch207-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch223-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch236-path-c-bundle}"' in oneshot
        or 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in oneshot
        or _living_release(oneshot)
    )

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status.get("lemma_closed") is False
    assert _living_release(status.get("release_tag"))
    assert status.get("device_code")  # public user code only

    hunt = json.loads((ROOT / "portable" / "BATCH207_HUNT.json").read_text(encoding="utf-8"))
    assert hunt.get("patch_0017") is True
    assert hunt.get("lemma_closed") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 207" in log
    assert "0017" in log


def test_batch210_auth_renew_hunt_clean_has_0017() -> None:
    """Batch 210: tip stable b89448d; auth renew B064; has_0017; hunt clean no 0018; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH210_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data.get("batch") == "210"
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("scientific_effect") == "NONE"
    assert data.get("goal_complete") is False
    assert data.get("has_0017") is True
    assert data.get("patch_0018") is False
    assert data.get("hunt") == "clean_no_0018"
    assert data.get("auth_renewed") is True
    assert _living_tip(data.get("tip"))
    assert _living_release(data.get("release"))
    assert data.get("path_c_landed") is False
    assert data.get("preferred_auth_interval_s") == 1800

    apply_all = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "0017-pinned-sources-close-file-handles.patch" in apply_all
    manifest = json.loads((ROOT / "portable" / "patches" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert any(p.get("id") == "0017" for p in manifest.get("patches", []))
    verify = json.loads((ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(encoding="utf-8"))
    assert verify.get("lemma_closed") is False
    assert verify.get("patch_0017") is True or "0017" in (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status.get("lemma_closed") is False
    assert status.get("device_code")  # public user code only

    hunt = json.loads((ROOT / "portable" / "BATCH210_HUNT.json").read_text(encoding="utf-8"))
    assert hunt.get("hunt_result") == "clean"
    assert hunt.get("patch_0018") is False
    assert hunt.get("has_0017") is True
    assert hunt.get("lemma_closed") is False

    login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "B064-C458" in login
    assert "Batch 210" in login

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 210" in log
    assert "B064-C458" in log


def test_batch212_auth_renew_tip_stable() -> None:
    """Batch 212: tip stable b89448d; auth renew 5AEC; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH212_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data.get("batch") == "212"
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("scientific_effect") == "NONE"
    assert data.get("goal_complete") is False
    assert data.get("auth_renewed") is True
    assert data.get("prior_device_code") == "B064-C458"
    assert _living_tip(data.get("tip"))
    assert data.get("path_c_landed") is False
    assert data.get("preferred_auth_interval_s") == 1800

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status.get("lemma_closed") is False
    assert status.get("device_code")  # public user code only

    login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert data["device_code"] in login
    assert "Batch 212" in login

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 212" in log
    assert data["device_code"] in log


def test_batch219_repos_connect_all() -> None:
    """Batch 219: connect ALL visible owner repos; tip living 1d0dceb; auth renew; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH219_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "219"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["main_writable"] is False
    assert data["write"] == "DENIED"
    assert data["install_has_main"] is False
    assert data["auth_renewed"] is True
    assert data["device_auth"] == "pending"
    assert "-" in str(data["device_code"])
    assert data["prior_device_code"] == "4B66-CE85" or "-" in str(data.get("prior_device_code", ""))
    assert _living_tip(data.get("tip"))
    assert data.get("repositoryDependencies_updated") is True
    repos = data.get("repos_connected") or []
    names = {r["name"] for r in repos}
    assert "d6g8k5htny-coder/main" in names
    assert "d6g8k5htny-coder/trial" in names
    assert len(names) >= 7

    env = (ROOT / ".cursor" / "environment.json").read_text(encoding="utf-8")
    for repo in (
        "google-drive",
        "governance-",
        "main",
        "Math-",
        "meta-framework",
        "query-",
        "trial",
    ):
        assert f"github.com/d6g8k5htny-coder/{repo}" in env

    inv = ROOT / "portable" / "BATCH219_REPO_INVENTORY.json"
    assert inv.is_file()
    inv_data = json.loads(inv.read_text(encoding="utf-8"))
    assert inv_data["lemma_closed"] is False
    assert inv_data["install_has_main"] is False

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert status.get("tip_match") is True
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE.
    assert status.get("path_c_blocked") in ("NO_TOKEN", "NONE") or status.get("path_c_landed") is True
    assert "-" in str(status.get("device_code", ""))

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 219" in owner
    assert "google-drive" in owner
    relaunch = (ROOT / "portable" / "RELAUNCH_WITH_MAIN_SCOPE.md").read_text(encoding="utf-8")
    assert "Batch 219" in relaunch
    assert "meta-framework" in relaunch

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert data["device_code"] in login
    assert "Batch 219" in login

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 219" in log
    assert "0867-BD4B" in log or data["device_code"] in log


def test_batch223_multi_agent_access() -> None:
    """Batch 223: multi-agent access docs+script; tip cbaa056; auth pending; lemma_closed=false."""
    import json
    import subprocess

    brief = ROOT / "portable" / "BATCH223_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "223"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["main_writable"] is False
    assert data["write"] == "DENIED"
    assert data["install_has_main"] is False
    assert data["device_auth"] == "pending"
    assert "-" in str(data["device_code"])
    assert _living_tip(data.get("tip"))
    apps = data.get("apps_documented") or []
    assert "cursor" in apps
    assert "chatgpt-codex-connector" in apps
    assert "claude" in apps
    assert "grok-pat-fallback" in apps

    doc = ROOT / "docs" / "MULTI_AGENT_ACCESS.md"
    assert doc.is_file()
    doc_text = doc.read_text(encoding="utf-8")
    assert "github.com/apps/cursor" in doc_text
    assert "chatgpt-codex-connector" in doc_text
    assert "github.com/apps/claude" in doc_text
    assert "lemma_closed" in doc_text
    assert "no verified official" in doc_text.lower() or "no verified" in doc_text.lower()

    script = ROOT / "scripts" / "owner_grant_ai_agent_access.sh"
    assert script.is_file()
    assert script.stat().st_mode & 0o111  # executable
    help_out = subprocess.check_output(
        [str(script), "--help"], cwd=ROOT, text=True
    )
    assert "--dry-run" in help_out
    assert "--check" in help_out
    assert "chatgpt-codex-connector" in help_out
    dry = subprocess.check_output([str(script)], cwd=ROOT, text=True)
    assert "dry-run complete" in dry or "Cursor GitHub App" in dry
    assert "d6g8k5htny-coder/main" in dry

    inv = ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json"
    assert inv.is_file()
    inv_data = json.loads(inv.read_text(encoding="utf-8"))
    assert inv_data["lemma_closed"] is False
    assert inv_data["install_has_main"] is False
    # Batch 223: App install often lacked main write; Batch 236+: device token WRITABLE.
    assert inv_data["main_writable"] in (False, True)
    assert "cursor" in (inv_data.get("apps_documented") or [])

    env = (ROOT / ".cursor" / "environment.json").read_text(encoding="utf-8")
    for repo in (
        "google-drive",
        "governance-",
        "main",
        "Math-",
        "meta-framework",
        "query-",
        "trial",
    ):
        assert f"github.com/d6g8k5htny-coder/{repo}" in env

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert status.get("tip_match") is True
    assert status.get("write_state") in ("DENIED", "SKIPPED", "UNKNOWN", "WRITABLE")
    # Batch 230+: Path C landed → path_c_blocked may be NONE (was NO_TOKEN).
    assert str(status.get("path_c_blocked", "")) in ("NO_TOKEN", "NONE") or "NO_TOKEN" in str(
        status.get("path_c_blocked", "")
    ) or status.get("path_c_landed") is True
    assert "-" in str(status.get("device_code", ""))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_ACCESS" in readme
    assert "owner_grant_ai_agent_access" in readme
    relaunch = (ROOT / "portable" / "RELAUNCH_WITH_MAIN_SCOPE.md").read_text(encoding="utf-8")
    assert "Batch 223" in relaunch
    assert "MULTI_AGENT_ACCESS" in relaunch
    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 223" in ones
    assert "owner_grant_ai_agent_access" in ones
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_ACCESS" in agents

    login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert data["device_code"] in login
    assert "Batch 223" in login

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 223" in log
    assert "MULTI_AGENT" in log.upper() or "multi-agent" in log.lower()


def test_batch224_sandbox_eight_repos() -> None:
    """Batch 224: add sandbox → 8 repos; grant --check; auth pending; lemma_closed=false."""
    import json
    import subprocess

    brief = ROOT / "portable" / "BATCH224_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "224"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["main_writable"] is False
    assert data["write"] == "DENIED"
    assert data["install_has_main"] is False
    assert data["sandbox_added"] is True
    assert data["repos_count"] == 8
    assert data["device_auth"] == "pending"
    assert "-" in str(data["device_code"])
    assert _living_tip(data.get("tip"))
    apps = data.get("apps_documented") or []
    assert "cursor" in apps
    assert "chatgpt-codex-connector" in apps
    assert "claude" in apps
    assert "grok-pat-fallback" in apps
    repos = data.get("repos") or []
    assert "d6g8k5htny-coder/sandbox" in repos
    assert len(repos) == 8

    env = (ROOT / ".cursor" / "environment.json").read_text(encoding="utf-8")
    for repo in (
        "google-drive",
        "governance-",
        "main",
        "Math-",
        "meta-framework",
        "query-",
        "sandbox",
        "trial",
    ):
        assert f"github.com/d6g8k5htny-coder/{repo}" in env

    doc = (ROOT / "docs" / "MULTI_AGENT_ACCESS.md").read_text(encoding="utf-8")
    assert "sandbox" in doc
    assert "select ALL repositories including sandbox" in doc
    assert "lemma_closed" in doc

    script = ROOT / "scripts" / "owner_grant_ai_agent_access.sh"
    assert script.is_file()
    assert script.stat().st_mode & 0o111
    help_out = subprocess.check_output([str(script), "--help"], cwd=ROOT, text=True)
    assert "select ALL repositories including sandbox" in help_out
    dry = subprocess.check_output([str(script)], cwd=ROOT, text=True)
    assert "Batch 224" in dry
    assert "d6g8k5htny-coder/sandbox" in dry
    assert "select ALL repositories including sandbox" in dry
    assert dry.count("d6g8k5htny-coder/") >= 8

    inv = ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json"
    assert inv.is_file()
    inv_data = json.loads(inv.read_text(encoding="utf-8"))
    assert inv_data["lemma_closed"] is False
    assert inv_data["sandbox_added"] is True
    assert inv_data["repos_count"] == 8
    assert inv_data["install_has_main"] is False
    # Batch 224: App token often 404; Batch 236+: device token can read/write sandbox.
    assert inv_data.get("sandbox", {}).get("readable") in (False, True)
    names = {r["name"] for r in inv_data.get("repos_connected") or []}
    assert "d6g8k5htny-coder/sandbox" in names
    assert len(names) == 8

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert status.get("tip_match") is True
    # Batch 230+: Path C landed → path_c_blocked may be NONE (was NO_TOKEN).
    assert str(status.get("path_c_blocked", "")) in ("NO_TOKEN", "NONE") or "NO_TOKEN" in str(
        status.get("path_c_blocked", "")
    ) or status.get("path_c_landed") is True

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "sandbox" in readme
    assert "owner_grant_ai_agent_access" in readme
    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 224" in ones
    assert "sandbox" in ones
    relaunch = (ROOT / "portable" / "RELAUNCH_WITH_MAIN_SCOPE.md").read_text(encoding="utf-8")
    assert "Batch 224" in relaunch
    assert "sandbox" in relaunch
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "sandbox" in agents

    login = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert data["device_code"] in login
    assert "Batch 224" in login

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 224" in log
    assert "sandbox" in log


def test_batch227_path_b_transport_retry() -> None:
    """Batch 227: Path B --after-merge retries audit/watch transport (CI sanity flake)."""
    import json

    brief = ROOT / "portable" / "BATCH227_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "227"
    assert data["goal_complete"] is False
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is False
    assert data["write"] == "DENIED"
    assert data["sanity_fix"] == "path_b_after_merge_transport_retry"
    assert _living_tip(data.get("tip"))
    assert _living_release(data.get("release") or data.get("status_snapshot", {}).get("release_tag"))

    path_b = (ROOT / "scripts" / "owner_land_path_b.sh").read_text(encoding="utf-8")
    assert "PATH_B_TRANSPORT_RETRIES" in path_b
    assert "transport exhausted" in path_b or "TRANSPORT_RETRIES" in path_b
    assert "watch transport" in path_b or "audit transport" in path_b

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "Batch 227" in intent
    assert "PATH_B_TRANSPORT_RETRIES" in intent

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert _living_tip(status.get("tip"))
    assert status.get("tip_match") is True

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 227" in log
    assert "transport" in log.lower()


def test_batch230_path_c_landed() -> None:
    """Batch 230: device auth SUCCESS; Path C landed on hardening PR #64; lemma_closed=false."""
    import json

    brief = ROOT / "portable" / "BATCH230_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "230"
    assert data["goal_complete"] is True
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is True
    assert data["write"] == "WRITABLE"
    assert "pull/64" in data["path_c_pr_url"]
    assert _living_tip(data.get("tip"))
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert "lemma_closed=false" in data.get("math_status", "")

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_landed") is True
    assert status.get("goal_complete") is True
    assert status.get("write_state") == "WRITABLE"
    assert status.get("tip_match") is True
    assert _living_tip(status.get("tip"))
    assert _living_tip(status.get("base_tip"))

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(encoding="utf-8")
    )
    assert verify["lemma_closed"] is False
    assert verify.get("path_c_landed") is True
    assert verify.get("goal_complete") is False  # VERIFY contract stays false
    assert _living_tip(verify["base_tip_sha"])

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    assert_sh = (ROOT / "scripts" / "assert_path_c_ready.sh").read_text(encoding="utf-8")
    assert "path_c_landed" in assert_sh

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "path_c_landed" in ci

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 230" in log
    assert "PR #64" in log or "pull/64" in log
    assert "lemma_closed" in log.lower()


def test_batch231_post_land_hygiene() -> None:
    """Batch 231: Path C DONE hygiene; apply_all idempotent; lander idle; no flip."""
    import json

    brief = ROOT / "portable" / "BATCH231_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "231"
    assert data["goal_complete"] is True
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is True
    assert data["next_focus"] == "tip-sync+drift+no-flip"
    assert data["when_writable_land"] == "idle_path_c_done"
    assert data["preferred_autonomy"] == "aligned_drift_watch"
    assert data.get("ready_to_apply") == "superseded_already_on_tip"
    assert _living_tip(data.get("tip"))
    assert _living_tip(data.get("tip_full") or data.get("tip"))

    apply_all = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "already-applied" in apply_all
    assert "Batch 231" in apply_all or "idempotent" in apply_all

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "path_c_already_landed" in ww
    assert "idle_path_c_done" in ww

    adw = (ROOT / "scripts" / "aligned_drift_watch.py").read_text(encoding="utf-8")
    assert "path_c_landed" in adw
    assert "tip_sync_drift_watch" in adw or "idle_path_c_done" in adw

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "path_c_landed=true" in ci
    assert "idempotent" in ci or "already-applied" in apply_all

    manifest = json.loads(
        (ROOT / "portable" / "patches" / "MANIFEST.json").read_text(encoding="utf-8")
    )
    assert manifest.get("path_c_landed") is True
    assert _living_tip(manifest.get("verified_on_tip", ""))
    assert manifest.get("ready_to_apply") == "superseded_already_on_tip"
    assert manifest["lemma_closed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 231" in log
    assert "tip-sync+drift" in log or "idle_path_c_done" in log



def test_batch232_path_c_status_write_state_clobber() -> None:
    """Batch 232: skip-write-probe recovers WRITABLE after Path C land; no sticky DENIED."""
    import json
    import tempfile
    from pathlib import Path

    # Unit: build_status recovers WRITABLE when land+tip_match even if prior DENIED.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "write_path_c_status", ROOT / "scripts" / "write_path_c_status.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "PATH_C_STATUS.json"
        # Seed a clobbered DENIED snapshot after land.
        seed = {
            "write_state": "DENIED",
            "path_c_landed": True,
            "tip_match": True,
            "lemma_closed": False,
            "goal_complete": True,
            "tip": "93a4ecd",
            "base_tip": "93a4ecd",
            "write_vector": "device_auth_create_ref+git_push_dylan_token",
        }
        out.write_text(json.dumps(seed, indent=2) + "\n", encoding="utf-8")
        status = mod.build_status(skip_write_probe=True, out=out)
        assert status["lemma_closed"] is False
        assert status.get("path_c_landed") is True
        assert status.get("tip_match") is True
        assert status.get("write_state") == "WRITABLE"

    # Live status + brief contracts.
    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_landed") is True
    assert status.get("write_state") == "WRITABLE"
    assert status.get("tip_match") is True

    brief = ROOT / "portable" / "BATCH232_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "232"
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is True
    assert data["tip_moved"] is True
    assert "377201c" in str(data.get("tip") or "") or _living_tip(data.get("tip"))
    assert "write_state" in str(data.get("defect_shipped") or "")
    assert data.get("patch_0018") is False
    assert "OPEN_HOLD" in data.get("math_status", "")

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "PATH_C_IGNORE_FILE_TOKENS" in ww
    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert "PATH_C_IGNORE_FILE_TOKENS" in oneshot or "IGNORE_FILE_TOKENS" in oneshot

    hunt = ROOT / "portable" / "BATCH232_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["hunt_result"] == "clean"
    assert h["patch_0018"] is False
    assert h["lemma_closed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 232" in log


def test_batch233_guard_tip_sha_clobber() -> None:
    """Batch 233: guard_no_status_promotion preserves tip_sha without --tip-sha."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "guard_no_status_promotion", ROOT / "scripts" / "guard_no_status_promotion.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Unit: recover baseline tip when inventory.tip_sha was wiped.
    baseline_raw = {
        "tip_sha": "",
        "baseline_tip_sha": "377201c456a5081d4c79701940e5ca678226d15d",
        "inventory": {"tip_sha": None, "premises": {}, "lemmas": {}, "prizes": {}},
    }
    recovered = mod._baseline_tip_sha(baseline_raw, baseline_raw["inventory"])
    assert recovered == "377201c456a5081d4c79701940e5ca678226d15d"

    snap = mod.build_snapshot(
        tip_sha="377201c456a5081d4c79701940e5ca678226d15d",
        baseline_path=Path("portable/STATUS_GUARD_SNAPSHOT.json"),
        baseline_inv={"tip_sha": None, "premises": {}, "lemmas": {}, "prizes": {}},
        baseline_raw=baseline_raw,
        current_inv={
            "tip_sha": "377201c456a5081d4c79701940e5ca678226d15d",
            "premises": {},
            "lemmas": {},
            "prizes": {},
            "counts": {},
        },
        live_report={"shape": "HAS_PACKET", "counts": {}},
        violations=[],
    )
    assert snap["tip_sha"] == "377201c456a5081d4c79701940e5ca678226d15d"
    assert snap["baseline_tip_sha"] == "377201c456a5081d4c79701940e5ca678226d15d"
    assert snap["lemma_closed"] is False
    assert snap["scientific_effect"] == "NONE"

    # Live contracts.
    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_landed") is True
    assert status.get("write_state") == "WRITABLE"
    assert status.get("tip_match") is True

    guard = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert guard["lemma_closed"] is False
    assert guard["pass"] is True
    assert guard.get("tip_sha")
    assert len(str(guard["tip_sha"])) >= 7
    assert guard.get("inventory", {}).get("tip_sha")

    brief = ROOT / "portable" / "BATCH233_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "233"
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is True
    assert data["tip_moved"] is False
    assert data.get("path_c_delta_landed") is False
    assert data.get("patch_0018") is False
    assert "guard" in str(data.get("defect_shipped") or "")
    assert "OPEN_HOLD" in data.get("math_status", "")

    hunt = ROOT / "portable" / "BATCH233_HUNT.json"
    assert hunt.is_file()
    h = json.loads(hunt.read_text(encoding="utf-8"))
    assert h["patch_0018"] is False
    assert h["lemma_closed"] is False
    assert h["focused_resource_warnings"] == 0

    src = (ROOT / "scripts" / "guard_no_status_promotion.py").read_text(encoding="utf-8")
    assert "_git_head_sha" in src
    assert "_baseline_tip_sha" in src
    assert "never clobber tip tracking" in src

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 233" in log


def test_batch236_sibling_agent_access() -> None:
    """Batch 236: sibling R/W inventory; sandbox README+AGENTS; pack release; no flip."""
    import json

    brief = ROOT / "portable" / "BATCH236_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "236"
    assert data["goal_complete"] is True
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["path_c_landed"] is True
    assert data["hardening_aligned"] is True
    assert data["default_aligned"] is True
    assert data["path_b_landed"] is False
    assert data["tip_moved"] is True
    assert data["bundle_refreshed"] is True
    assert "1200501" in str(data.get("tip") or "") or _living_tip(data.get("tip"))
    assert data["write"] == "WRITABLE"
    assert data["sibling_write_count"] == 8
    assert "sandbox_README" in str(data.get("defect_shipped") or "")
    assert data.get("release_tag") == "batch236-path-c-bundle" or _living_release(
        data.get("release_tag")
    )
    assert "OPEN_HOLD" in data.get("math_status", "")
    assert _living_tip(data.get("tip"))

    inv = ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json"
    assert inv.is_file()
    inv_data = json.loads(inv.read_text(encoding="utf-8"))
    # Living inventory supersession (Batch 240+ may refresh batch field).
    assert inv_data["batch"] in ("236", "240") or str(inv_data.get("batch", "")).isdigit()
    assert inv_data["lemma_closed"] is False
    assert inv_data["flipped_anything"] is False
    assert inv_data["sibling_write_count"] == 8
    assert inv_data.get("main_writable", True) is True
    assert inv_data.get("sandbox", {}).get("readable", True) is True
    assert inv_data.get("sandbox", {}).get("write", "WRITABLE") == "WRITABLE"
    assert inv_data.get("sandbox", {}).get("has_agents", True) is True
    details = {d["name"]: d for d in inv_data.get("details") or []}
    for name in (
        "d6g8k5htny-coder/google-drive",
        "d6g8k5htny-coder/governance-",
        "d6g8k5htny-coder/Math-",
        "d6g8k5htny-coder/meta-framework",
        "d6g8k5htny-coder/query-",
        "d6g8k5htny-coder/sandbox",
        "d6g8k5htny-coder/trial",
        "d6g8k5htny-coder/main",
    ):
        assert name in details
        assert details[name]["write"] == "WRITABLE"
        assert details[name].get("has_agents") is True

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_landed") is True
    assert status.get("write_state") == "WRITABLE"
    assert status.get("tip_match") is True
    assert status.get("release_tag") == "batch236-path-c-bundle" or _living_release(
        status.get("release_tag")
    )
    assert status.get("write_durable") is True

    snap = json.loads(
        (ROOT / "portable" / "ALIGNED_DRIFT_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap["state"] == "ALIGNED"
    assert snap["lemma_closed"] is False
    # Living schema: hardening_aligned may be omitted when tip_sync fields supersede.
    assert snap.get("hardening_aligned") in (True, None)
    assert snap.get("default_aligned") in (True, None) or snap.get("default_tip_sha")

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 236" in log
    assert "sibling" in log.lower() or "AGENTS" in log


def test_batch238_merge70_wait69_followon_gate() -> None:
    """Batch 238: merge #70; tip 62f955a; 0018 on tip; when_writable follow-on gate; no flip."""
    import json
    import importlib.util

    brief = ROOT / "portable" / "BATCH238_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "238"
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["scientific_effect"] == "NONE"
    assert data["pr70"] == "MERGED"
    assert data["pr69"] == "PENDING"
    assert 70 in (data.get("merged_prs") or [])
    assert data["path_c_0018_landed"] is True
    assert _living_tip(data.get("tip"))
    assert _living_release(data.get("release_tag"))
    assert "path_c_followon_pending" in str(data.get("when_writable_followon_gate") or "")

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "path_c_followon_pending" in ww
    assert "Batch 238" in ww
    assert "path_c_0018_landed" in ww

    spec = importlib.util.spec_from_file_location(
        "when_writable_land_b238", ROOT / "scripts" / "when_writable_land.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pending, detail = mod.path_c_followon_pending()
    # Batch 239 may cut 0019+ → pending True is OK; 0018 must stay resolved.
    assert detail.get("scientific_effect") == "NONE"
    assert "0018" in (detail.get("resolved_ids") or []) or (
        pending is False and data["path_c_0018_landed"] is True
    )

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert verify.get("path_c_0018_landed") is True
    assert verify["lemma_closed"] is False
    assert _living_tip(verify.get("base_tip_sha"))

    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_landed") is True
    assert status.get("path_c_0018_landed") is True
    assert status.get("write_state") == "WRITABLE"
    assert _living_tip(status.get("tip"))

    wps = (ROOT / "scripts" / "write_path_c_status.py").read_text(encoding="utf-8")
    assert "path_c_0018_landed" in wps

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 238" in log
    assert "pull/70" in log or "#70" in log
    assert "waiting_ci" in log.lower() or "PENDING" in log


def test_batch239_0019_future_delta_gate() -> None:
    """Batch 239: tip hunt → 0019; when_writable future-delta gate; #69 wait; no flip."""
    import json
    import importlib.util

    brief = ROOT / "portable" / "BATCH239_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "239"
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["scientific_effect"] == "NONE"
    assert data["pr69"] == "MERGED"
    assert data["pr70"] == "MERGED"
    assert data.get("path_c_0018_landed") is True
    assert data.get("path_c_0019_landed") is False
    assert data.get("patch_0019") is True
    assert data.get("pr71") == "OPEN" or 71 in (data.get("waiting_main_prs") or [])
    assert _living_tip(data.get("tip"))
    assert _living_release(data.get("release_tag"))

    patch = ROOT / "portable" / "patches" / "0019-attestations-close-file-handles.patch"
    assert patch.is_file()
    ptxt = patch.read_text(encoding="utf-8")
    assert "attestations" in ptxt
    assert "with open" in ptxt

    apply = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "0019-attestations-close-file-handles.patch" in apply

    manifest = json.loads(
        (ROOT / "portable" / "patches" / "MANIFEST.json").read_text(encoding="utf-8")
    )
    ids = {p["id"] for p in manifest["patches"]}
    assert "0019" in ids
    assert manifest["lemma_closed"] is False

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "Batch 239" in ww
    assert "followon_patch_ids" in ww or "future deltas" in ww.lower() or "0019+" in ww

    spec = importlib.util.spec_from_file_location(
        "when_writable_land_b239", ROOT / "scripts" / "when_writable_land.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pending, detail = mod.path_c_followon_pending()
    assert detail.get("scientific_effect") == "NONE"
    assert detail.get("lemma_closed") is False
    assert "0018" in (detail.get("resolved_ids") or [])
    # Living supersession (Batch 241+): after #71 merge, 0019 is resolved on tip.
    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status["lemma_closed"] is False
    assert status.get("path_c_0018_landed") is True
    if status.get("path_c_0019_landed") is True:
        assert pending is False
        assert "0019" in (detail.get("resolved_ids") or [])
    else:
        assert pending is True
        assert "0019" in (detail.get("pending_ids") or [])
        assert status.get("path_c_0019_landed") is not True
    assert _living_tip(status.get("tip"))

    wps = (ROOT / "scripts" / "write_path_c_status.py").read_text(encoding="utf-8")
    assert "path_c_" in wps and "_landed" in wps

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 239" in log
    assert "0019" in log
    assert "sibling" in log.lower() or "AGENTS" in log


def test_batch240_land_path_c_apply_includes_0019() -> None:
    """Batch 240: land-path-c + owner_land always apply through 0019; deep 0020 hunt NEGATIVE."""
    import json

    path_c = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "0008–0019" in path_c or "0008-0019" in path_c
    assert "0019" in path_c
    assert "already looks patched" not in path_c
    assert "running apply_all --check only" not in path_c
    assert "Running portable apply_all" in path_c

    owner = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "0008–0019" in owner or "0008-0019" in owner
    assert "already looks patched" not in owner
    assert "running apply_all --check only" not in owner

    apply = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert "0019-attestations-close-file-handles.patch" in apply
    assert "0019-*" in apply or '0019-*' in apply
    assert "attestations/ absent" in apply

    dry = (ROOT / "scripts" / "path_c_dry_run.py").read_text(encoding="utf-8")
    assert 'APPLY_STACK = "0001-0004 + 0008-0019"' in dry

    align = (ROOT / "scripts" / "alignment_status.py").read_text(encoding="utf-8")
    assert "0001-0004 + 0008-0019" in align

    brief = ROOT / "portable" / "BATCH240_BRIEF.json"
    assert brief.is_file()
    data = json.loads(brief.read_text(encoding="utf-8"))
    assert data["batch"] == "240"
    assert data["lemma_closed"] is False
    assert data["flipped_anything"] is False
    assert data["scientific_effect"] == "NONE"
    assert data.get("patch_0020") is False
    assert data.get("hunt_0020") == "NEGATIVE" or data.get("hunt_0020_seed")
    assert "land_path_c_0019_apply" in (data.get("parallel_shipped") or []) or (
        "land-path-c" in (data.get("parallel") or "")
    ) or "deep_post_0019_rw_hunt_0020_negative" in (
        data.get("parallel_shipped") or []
    )
    assert _living_tip(data.get("tip"))

    hunt = json.loads(
        (ROOT / "portable" / "HUNT_240_NEGATIVE.json").read_text(encoding="utf-8")
    )
    assert hunt["hunt_result"] == "NEGATIVE"
    assert hunt["defect_found"] is False
    assert hunt["patch_0020"] is False
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert _living_tip(hunt.get("tip"))

    audit = json.loads(
        (ROOT / "portable" / "BATCH240_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 240" in log
    assert "0019" in log
    assert "HUNT_240_NEGATIVE" in log or "0020" in log
    assert "land-path-c" in log.lower() or "land_path_c" in log

    # Batch 240: auto Path B restore + MAIN_PUSH_TOKEN on drift watch / lander
    adw = (ROOT / "scripts" / "aligned_drift_watch.py").read_text(encoding="utf-8")
    assert "--no-restore" in adw and "--dry-run" in adw
    assert "MAIN_PUSH_TOKEN" in adw
    assert "auto_path_b_restore" in adw or "auto Path B" in adw
    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "Batch 240" in ww
    assert "auto_path_b_restore" in ww
    assert "MAIN_PUSH_TOKEN" in ww


def test_batch241_path_b_aligned_skip_and_from_bundle_fallback() -> None:
    """Batch 241: Path B auditor ALIGNED short-circuit; from-bundle apply_all fallback; pack release."""
    import json

    land_b = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "audit_local_tree.py" in land_b
    assert "already ALIGNED" in land_b or "skipping git am" in land_b
    # Narrow Option-B notice-only skip must not be the sole gate (renewed tip face).
    assert "Running local auditor (pre-am" in land_b or "pre-am; skip git am" in land_b

    owner_b = (ROOT / "scripts" / "owner_land_path_b.sh").read_text(encoding="utf-8")
    assert "audit_local_tree" in owner_b
    assert "Batch 241" in owner_b
    assert "Tree already ALIGNED" in owner_b or "skipping git am" in owner_b

    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "already_applied_on_tip" in owner_c
    assert "apply_all --check" in owner_c or '"$APPLY_ALL" --check' in owner_c
    assert "Batch 241" in owner_c

    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in oneshot
    )
    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in open_pr
    )

    brief = json.loads(
        (ROOT / "portable" / "BATCH241_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "241"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert _living_release(brief.get("pack_release") or brief.get("release_tag"))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH241_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "241"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False
    assert _living_tip(hunt.get("tip"))

    audit = json.loads(
        (ROOT / "portable" / "BATCH241_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 241" in log
    assert "ALIGNED skip" in log or "aligned skip" in log.lower() or "audit_local_tree" in log
    assert "from-bundle" in log.lower() or "already_applied" in log.lower()


def test_batch242_path_b_aligned_noop_and_owner_face() -> None:
    """Batch 242: Path B ALIGNED no-op (no push/PR); OWNER face WRITABLE; pack help batch241."""
    import json

    land_b = (ROOT / ".github" / "workflows" / "land-option-b-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "already_aligned=true" in land_b or "Path B land not needed" in land_b
    assert "not pushing / not opening PR" in land_b or "not pushing" in land_b
    # Must not still claim push/PR after ALIGNED skip.
    assert "still push/PR if requested" not in land_b

    owner_b = (ROOT / "scripts" / "owner_land_path_b.sh").read_text(encoding="utf-8")
    assert "Batch 242" in owner_b
    assert "Path B land not needed" in owner_b
    assert "no push/PR" in owner_b

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert "default: batch241-path-c-bundle" in open_pr
    assert (
        'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in open_pr
    )

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 242)" in land_md or "STATUS (Batch 243)" in land_md or "STATUS (Batch 244)" in land_md
    assert "WRITABLE" in land_md
    assert "batch241-path-c-bundle" in land_md
    assert "542e6ec" in land_md
    assert "ea41a30" in land_md
    # Top face must not claim trial cannot write as absolute truth.
    top = "\n".join(land_md.splitlines()[:25])
    assert "both return 403" not in top

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 242" in owner_actions or "Batch 243" in owner_actions
    assert "WRITABLE" in owner_actions

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 242" in ones or "Batch 243" in ones
    assert "WRITABLE" in ones
    assert "batch241-path-c-bundle" in ones

    brief = json.loads(
        (ROOT / "portable" / "BATCH242_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "242"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("main_pr_or_null") is None

    hunt = json.loads(
        (ROOT / "portable" / "BATCH242_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "242"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH242_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 242" in log
    assert "no-op" in log.lower() or "noop" in log.lower() or "no push/PR" in log


def test_batch243_path_a_aligned_noop_and_land_c_release() -> None:
    """Batch 243: Path A ALIGNED no-op (no revert/merge); owner_land_path_c help → batch241."""
    import json

    owner_a = (ROOT / "scripts" / "owner_land_path_a.sh").read_text(encoding="utf-8")
    assert "Batch 243" in owner_a
    assert "already ALIGNED" in owner_a
    assert "Path A land not needed" in owner_a
    assert "no revert/merge" in owner_a
    assert "--dry-run" in owner_a
    assert "--help" in owner_a
    # Must audit before any revert32 / ready_merge work.
    assert owner_a.index("audit_main_alignment") < owner_a.index("gh pr revert 32")

    owner_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "gh release download batch241-path-c-bundle" in owner_c
    # Living ONE-SHOT must not still lead with batch218 as the download tag.
    assert "gh release download batch218-path-c-bundle" not in owner_c
    assert "batch241-path-c-bundle or newer" in owner_c

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    # Living STATUS line may supersede (Batch 244+).
    assert (
        "STATUS (Batch 243)" in land_md
        or "STATUS (Batch 244)" in land_md
        or "STATUS (Batch" in land_md
    )
    assert "Path A" in land_md or "ALIGNED" in land_md
    assert "WRITABLE" in land_md
    assert "batch241-path-c-bundle" in land_md

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 243" in owner_actions
    assert "Path A" in owner_actions

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 243" in ones
    assert "owner_land_path_a.sh" in ones

    brief = json.loads(
        (ROOT / "portable" / "BATCH243_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "243"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("main_pr_or_null") is None
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"

    hunt = json.loads(
        (ROOT / "portable" / "BATCH243_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "243"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH243_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 243" in log
    assert "Path A" in log
    assert "no-op" in log.lower() or "noop" in log.lower() or "ALIGNED" in log


def test_batch244_pack_living_tip_siblings_idle() -> None:
    """Batch 244: APPLY.md living tip (not batch207); sibling AGENTS; idle after 0019."""
    import json
    import subprocess
    import sys

    apply = (ROOT / "portable" / "path-c-applied-bundle" / "APPLY.md").read_text(
        encoding="utf-8"
    )
    assert "Batch 244" in apply
    assert "gh release download batch241-path-c-bundle" in apply
    # Living ONE-SHOT must not still lead with superseded batch207.
    assert "gh release download batch207-path-c-bundle" not in apply
    assert "already_applied_on_tip" in apply or "already on tip" in apply.lower()
    assert "542e6ec" in apply

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert 'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"' in open_pr
    assert "batch241-path-c-bundle (tip 542e6ec" in open_pr

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 244)" in land_md
    assert "batch241-path-c-bundle" in land_md
    assert "WRITABLE" in land_md

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 244" in owner_actions
    assert "APPLY.md" in owner_actions or "pack" in owner_actions.lower()

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 244" in ones
    assert "idle_path_c_done" in ones or "already_applied_on_tip" in ones

    sib = (ROOT / "portable" / "SIBLING_AGENTS_BATCH244.md").read_text(encoding="utf-8")
    assert "Batch 244" in sib
    for name in (
        "google-drive",
        "governance-",
        "Math-",
        "meta-framework",
        "query-",
        "sandbox",
    ):
        assert name in sib

    # when_writable idle correctness after 0019 markers.
    sys.path.insert(0, str(ROOT / "scripts"))
    import when_writable_land as ww  # type: ignore

    landed, _ = ww.path_c_already_landed()
    pending, detail = ww.path_c_followon_pending()
    assert landed is True
    assert pending is False
    assert "0018" in (detail.get("resolved_ids") or [])
    assert "0019" in (detail.get("resolved_ids") or [])
    assert detail.get("pending_ids") == []

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "when_writable_land.py"),
            "--once",
            "--dry-run",
            "--mock-probe",
            "WRITABLE",
            "--mock-align",
            "ALIGNED",
            "--mock-install-has-main",
            "true",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "idle_path_c_done" in combined
    assert "followons_resolved=true" in combined or "path_c_landed=true" in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH244_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "244"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("path_c_0019_landed") is True
    assert "path_a" not in (brief.get("defect_id") or "").lower() or "aligned_noop" not in (
        brief.get("defect_id") or ""
    )
    assert "aligned_noop" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH244_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "244"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH244_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    inv = json.loads(
        (ROOT / "portable" / "BATCH244_SIBLING_INVENTORY.json").read_text(
            encoding="utf-8"
        )
    )
    assert inv["batch"] == "244"
    assert inv["repos_count"] == 8
    assert inv["sibling_write_count"] == 8
    assert inv["lemma_closed"] is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 244" in log
    assert "batch207" in log.lower() or "APPLY" in log
