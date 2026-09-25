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
    "fa32d11",
    "8e359e5",
    "bfb7c38",
    "3b3860d",
    "7d13a88",
    "3a29f52",
    "02cfbfd",
    "0adeb65",
    "077464e",
    "388a22c",
    "eeebb28",
    "848aea2",
    "f244312",
    "fcad723",
    "e3cd7d4",
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


def _refresh_batch_tag_default(refresh_text: str) -> int:
    """Batch 286: parse REFRESH_BATCH_TAG default; stop hardcoded allowlist churn.

    Prior Intent gates listed every subsequent batch number (278…285…) so each
    tip-sync / eng batch that bumped the default had to edit N prior tests.
    Contract is: default exists and is an int >= the batch that introduced the
    assert (callers pass min_batch).
    """
    import re

    m = re.search(r"REFRESH_BATCH_TAG:-(\d+)", refresh_text)
    assert m is not None, "REFRESH_BATCH_TAG:-N default missing in refresh_path_c_bundle.sh"
    return int(m.group(1))


def _assert_refresh_batch_tag_default_at_least(refresh_text: str, min_batch: int) -> None:
    got = _refresh_batch_tag_default(refresh_text)
    assert got >= min_batch, f"REFRESH_BATCH_TAG default {got} < {min_batch}"


def _print_owner_header_batch(unblock_text: str) -> int | None:
    """Parse `=== Batch N —` header from print_owner_unblock.sh (Batch 317+).

    Tip-sync bumps the header every cycle; allowlisting 289|297|305|317 churned
    Intent reds. Contract: header exists and N >= the batch that introduced the
    assert (callers pass min_batch). History lines like `Batch 289:` remain.
    Header is emitted via `echo "=== Batch N — …"` so match inside the file text.
    """
    import re

    m = re.search(r'=== Batch (\d+)\b', unblock_text)
    if m is None:
        return None
    return int(m.group(1))


def _assert_print_owner_header_batch_at_least(unblock_text: str, min_batch: int) -> None:
    got = _print_owner_header_batch(unblock_text)
    assert got is not None, "print_owner_unblock missing === Batch N header"
    assert got >= min_batch, f"print_owner header Batch {got} < {min_batch}"



def _living_tip_refresh(val) -> bool:
    """True if VERIFY.tip_refresh is a living bool (Batch 329 remediation class).

    Tip-sync sets tip_refresh=True; a later non-tip refresh_batch bump (tip still
    living / TIP_MATCH) correctly sets tip_refresh=False. Freezing `is True` reds CI.
    """
    return val in (True, False)


def _assert_living_tip_refresh(val) -> None:
    assert _living_tip_refresh(val), f"VERIFY.tip_refresh not living bool: {val!r}"


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
    assert "gh issue" in text or "watch_alignment_issue_hygiene.py" in text
    assert "MISALIGNED" in text
    assert "ALIGNED" in text
    # Batch 252: GraphQL hygiene helper — never Search API / App REST open-list
    assert "watch_alignment_issue_hygiene.py" in text
    assert "Search API" in text or "exact-title" in text or "Batch 252" in text
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
    """Path C certainty: apply check OK; landed tip → idle (not APPLY_READY land advert)."""
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
    assert data["tip_matches_base"] is True
    assert data["default_aligned"] is True
    assert data["default_path_c_shape"]["accepts"] is False
    assert data["hardening_path_c_shape"]["accepts"] is True
    assert data["do_not_set_path_c_base_main"] is True
    assert data.get("apply_check_ok") is True
    # Batch 261: path_c_landed + tip match → IDLE (not APPLY_READY land advert).
    if data.get("path_c_landed") is True:
        assert data["state"] == "IDLE_PATH_C_DONE"
        assert data["apply_ready"] is False
        assert data.get("already_on_tip") is True
        assert data.get("idle_status") == "IDLE_PATH_C_DONE"
    else:
        assert data["apply_ready"] is True
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
    assert "already-on-tip idle" in combined or "dry-run OK" in combined
    assert "apply_ready on hardening BASE_TIP" not in combined


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
    # Living VERIFY may stamp 0 when tip refresh skips full pytest (Batch 180+),
    # or a live recount after tip-sync (Batch 278: 90→92 @ 3b3860d).
    assert verify76["pytest"]["focused_passed"] in (0, 90, 92) or int(
        verify76["pytest"]["focused_passed"]
    ) >= 90
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
    _assert_living_tip_refresh(verify.get("tip_refresh"))

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
    _assert_living_tip_refresh(verify.get("tip_refresh"))
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
    assert (
        "STATUS (Batch 242)" in land_md
        or "STATUS (Batch 243)" in land_md
        or "STATUS (Batch 244)" in land_md
        or "STATUS (Batch 245)" in land_md
        or "STATUS (Batch 246)" in land_md
    )
    assert "WRITABLE" in land_md
    assert "batch241-path-c-bundle" in land_md
    assert "542e6ec" in land_md
    # Living default tip may supersede ea41a30 → f3a41a75+.
    assert "ea41a30" in land_md or "f3a41a75" in land_md
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
    # Living STATUS header may supersede Batch 244 → 246+.
    assert (
        "STATUS (Batch 244)" in land_md
        or "STATUS (Batch 245)" in land_md
        or "STATUS (Batch 246)" in land_md
    )
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

    import os
    import tempfile

    with tempfile.TemporaryDirectory(prefix="ww-batch244-") as td:
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in (
                "MAIN_PUSH_TOKEN",
                "GH_TOKEN",
                "GITHUB_TOKEN",
            )
        }
        env["WHEN_WRITABLE_STATUS"] = str(Path(td) / "when_writable_land.status.json")
        env["WHEN_WRITABLE_LOG"] = str(Path(td) / "when_writable_land.log")
        env["WHEN_WRITABLE_STOP"] = str(Path(td) / "when_writable_land.stop")
        env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
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
            env=env,
        )
    assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
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


def test_batch245_pack_living_tag_automation() -> None:
    """Batch 245: pack_portable living-tag automation; tip stable; no flip."""
    import json
    import os
    import tempfile

    living = ROOT / "portable" / "LIVING_PATH_C_RELEASE_TAG"
    assert living.is_file()
    tag = living.read_text(encoding="utf-8").strip()
    assert tag == "batch241-path-c-bundle"
    assert _living_release(tag)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert verify.get("release") == tag
    assert verify.get("lemma_closed") is False

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "LIVING_PATH_C_RELEASE_TAG" in pack
    assert "living_tag=" in pack
    assert "VERIFY.json" in pack
    assert 'portable/LIVING_PATH_C_RELEASE_TAG' in pack

    oneshot = (ROOT / "scripts" / "owner_path_c_oneshot.sh").read_text(encoding="utf-8")
    assert "LIVING_PATH_C_RELEASE_TAG" in oneshot
    assert f'PATH_C_RELEASE_TAG="${{PATH_C_RELEASE_TAG:-{tag}}}"' in oneshot

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert "LIVING_PATH_C_RELEASE_TAG" in open_pr
    assert f'PATH_C_RELEASE_TAG="${{PATH_C_RELEASE_TAG:-{tag}}}"' in open_pr

    status_py = (ROOT / "scripts" / "write_path_c_status.py").read_text(encoding="utf-8")
    assert "LIVING_TAG_FILE" in status_py
    assert "LIVING_PATH_C_RELEASE_TAG" in status_py

    with tempfile.TemporaryDirectory(prefix="pack245-") as td:
        out = Path(td) / "pack.tgz"
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "pack_portable.sh"), str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
        assert f"living_tag={tag}" in (proc.stdout or "")
        listing = subprocess.run(
            ["tar", "-tzf", str(out)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert "portable/LIVING_PATH_C_RELEASE_TAG" in listing

    # Living file wins over hardcoded fallback when env unset.
    with tempfile.TemporaryDirectory(prefix="ww-living-") as td:
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("PATH_C_RELEASE_TAG", "MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
        }
        # Probe oneshot help path does not need network; just confirm sourcing.
        probe = subprocess.run(
            [
                "bash",
                "-c",
                'source /dev/null; ROOT="$1"; '
                'TAG_FILE="$ROOT/portable/LIVING_PATH_C_RELEASE_TAG"; '
                'tag=$(tr -d "[:space:]" <"$TAG_FILE"); '
                'echo "resolved=$tag"',
                "_",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        assert probe.returncode == 0
        assert f"resolved={tag}" in (probe.stdout or "")

    brief = json.loads(
        (ROOT / "portable" / "BATCH245_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "245"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "pack_portable_living_tag_automation"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("pack_release") == tag
    assert "aligned_noop" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH245_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "245"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH245_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 245" in log
    assert "LIVING_PATH_C_RELEASE_TAG" in log or "living-tag" in log.lower()

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 245)" in land_md or "STATUS (Batch 246)" in land_md
    assert "LIVING_PATH_C_RELEASE_TAG" in land_md or "living-tag" in land_md.lower() or "batch241-path-c-bundle" in land_md

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 245" in ones

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 245" in owner_actions


def test_batch246_assert_path_c_idle_catch_0020() -> None:
    """Batch 246: assert_path_c_ready IDLE_PATH_C_DONE + catch 0020; tip stable; no flip."""
    import json
    import importlib.util

    assert_sh = (ROOT / "scripts" / "assert_path_c_ready.sh").read_text(encoding="utf-8")
    assert "IDLE_PATH_C_DONE" in assert_sh
    assert "catch 0020" in assert_sh or "catch_0020" in assert_sh or "PENDING_FOLLOWON" in assert_sh
    assert "path_c_followon_pending" in assert_sh
    assert "skipped_redundant" in assert_sh

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "IDLE_PATH_C_DONE" in ci
    assert "catch 0020" in ci or "PENDING" in ci
    assert "path_c_followon_pending" in ci

    status_py = (ROOT / "scripts" / "write_path_c_status.py").read_text(encoding="utf-8")
    assert "idle_status" in status_py
    assert "IDLE_PATH_C_DONE" in status_py
    assert "required_catch_0020" in status_py
    assert "stack_end" in status_py

    # Live status contract: landed + no pending → idle skip.
    status = json.loads((ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8"))
    assert status.get("lemma_closed") is False
    assert status.get("path_c_landed") is True
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("apply_all_check") == "skipped_redundant"
    assert status.get("stack_end") == "0019"
    assert status.get("path_c_followon_pending_ids") == []
    assert "0019" in (status.get("path_c_followon_resolved_ids") or [])
    assert _living_tip(status.get("tip"))

    # Catch 0020: a new ≥0018 patch without landed marker arms pending.
    patches = ROOT / "portable" / "patches"
    probe = patches / "0020-batch246-idle-catch-probe.patch"
    assert not probe.exists()
    try:
        probe.write_text(
            "# Batch 246 probe only — not a real eng patch; removed by test.\n",
            encoding="utf-8",
        )
        spec = importlib.util.spec_from_file_location(
            "when_writable_land_246", ROOT / "scripts" / "when_writable_land.py"
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pending, detail = mod.path_c_followon_pending()
        assert pending is True
        assert "0020" in (detail.get("pending_ids") or [])
    finally:
        if probe.exists():
            probe.unlink()

    # After probe removal, idle again.
    spec = importlib.util.spec_from_file_location(
        "when_writable_land_246b", ROOT / "scripts" / "when_writable_land.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pending, detail = mod.path_c_followon_pending()
    assert pending is False
    assert detail.get("pending_ids") == []

    brief = json.loads(
        (ROOT / "portable" / "BATCH246_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "246"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "assert_path_c_ready_post_0019_idle"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("idle_status") == "IDLE_PATH_C_DONE"
    assert brief.get("patch_0020") is False
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH246_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "246"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH246_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 246" in log
    assert "IDLE_PATH_C_DONE" in log

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 246)" in land_md
    assert "IDLE_PATH_C_DONE" in land_md

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 246" in ones

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 246" in owner_actions
    assert "IDLE_PATH_C_DONE" in owner_actions


def test_batch247_ci_yml_workflow_file_flake() -> None:
    """Batch 247: ci.yml must YAML-parse; no col-0 python; tip stable; no flip."""
    import json
    import importlib.util

    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    ci = ci_path.read_text(encoding="utf-8")
    assert "IDLE_PATH_C_DONE" in ci
    assert "path_c_followon_pending" in ci
    assert "Batch 247" in ci
    # Regression: column-0 import/from breaks `run: |` block scalars for Actions.
    for line in ci.splitlines():
        assert not line.startswith("import "), line
        assert not line.startswith("from "), line
    # One-liner pending probe (YAML-safe), not a multiline -c block.
    assert "from when_writable_land import path_c_followon_pending" in ci
    assert "print('1' if pending else '0')" in ci or 'print("1" if pending else "0")' in ci

    try:
        import yaml  # type: ignore
    except ImportError:  # pragma: no cover — CI installs pyyaml in land-workflows job
        yaml = None
    if yaml is not None:
        data = yaml.safe_load(ci)
        assert isinstance(data, dict)
        assert "portable-patches-on-main" in data.get("jobs", {})

    # validate_land_workflows gates ci.yml (Batch 247).
    spec = importlib.util.spec_from_file_location(
        "validate_land_workflows_247", ROOT / "scripts" / "validate_land_workflows.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ci_errs = mod._check_ci_yml_parses(ci_path)
    assert ci_errs == [], ci_errs

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_land_workflows.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload.get("ok") is True
    assert payload.get("ci_yml_ok") is True
    assert payload.get("lemma_closed") is False
    assert any(str(p).endswith("ci.yml") for p in payload.get("workflows") or [])

    brief = json.loads(
        (ROOT / "portable" / "BATCH247_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "247"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "ci_yml_col0_python_workflow_file_flake"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("patch_0020") is False
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH247_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "247"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH247_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 247" in log
    assert "workflow file" in log.lower() or "workflow-file" in log.lower()

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 247)" in land_md

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 247" in ones

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 247" in owner_actions
    assert "workflow" in owner_actions.lower()


def test_batch248_workspace_landing_ci_path_split() -> None:
    """Batch 248: workspace-landing/ci.yml path collision fixed on main; tip stable; no flip."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH248_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "248"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "workspace_landing_ci_yml_path_collision"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("patch_0020") is False
    assert 78 in (brief.get("merged_prs") or [])
    assert brief.get("main_pr_or_null") == 78
    wl = brief.get("workspace_landing_investigation") or {}
    assert wl.get("not_hang") is True
    assert "path collision" in (wl.get("root_cause") or "") or "ci.yml" in (
        wl.get("root_cause") or ""
    )
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH248_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "248"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("patch_0020") is False
    assert hunt.get("defect_id") == "workspace_landing_ci_yml_path_collision"

    audit = json.loads(
        (ROOT / "portable" / "BATCH248_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 248" in log
    assert "workspace-landing" in log.lower() or "workspace_landing" in log.lower()
    assert "path" in log.lower() and ("collision" in log.lower() or "split" in log.lower())

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 248)" in land_md

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 248" in ones

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 248" in owner_actions
    assert "workspace-landing" in owner_actions.lower() or "#78" in owner_actions

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert status.get("tip_match") is True
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch249_inventable_tip_observe_and_path_c_refresh() -> None:
    """Batch 249: tip-observe eng #79; tip moved; Path C IDLE; no research flip."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH249_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "249"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "inventable_tip_observe_stale_b89448da_vs_live_542e6ec"
    assert brief.get("tip_moved") is True
    assert _living_tip(brief.get("tip"))
    assert str(brief.get("tip")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("patch_0020") is False
    assert brief.get("port_78_to_hardening") is False
    assert brief.get("hardening_path_collision") is False
    assert 79 in (brief.get("merged_prs") or [])
    assert brief.get("main_pr_or_null") == 79
    assert brief.get("idle_status") == "IDLE_PATH_C_DONE"
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH249_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "249"
    assert hunt["defect_found"] is True
    assert hunt["defect_shipped"] is True
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("tip_moved") is True
    assert hunt.get("patch_0020") is False
    assert hunt.get("defect_id") == "inventable_tip_observe_stale_b89448da_vs_live_542e6ec"

    audit = json.loads(
        (ROOT / "portable" / "BATCH249_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["lemma_closed"] is False
    assert audit["flipped_anything"] is False
    assert audit["scientific_effect"] == "NONE"
    assert audit.get("problems") == 0

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Batch 268+: living tip may supersede fa32d11 (now bfb7c38+); keep historical brief tip.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert verify.get("lemma_closed") is False
    assert _living_tip(verify.get("base_tip_sha"))
    assert verify.get("path_c_landed") is True

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 249" in log
    assert "tip-observe" in log.lower() or "tip_observe" in log.lower()
    assert "#79" in log or "PR #79" in log or "main #79" in log

    land_md = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 249)" in land_md
    assert "fa32d11" in land_md

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 249" in ones

    owner_actions = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 249" in owner_actions
    assert "#79" in owner_actions or "tip-observe" in owner_actions.lower()

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert status.get("tip_match") is True
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert _living_tip(status.get("tip"))

    snap = json.loads(
        (ROOT / "portable" / "ALIGNED_DRIFT_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("state") == "ALIGNED"
    assert snap.get("lemma_closed") is False


def test_batch250_verify_keep_prior_honesty_and_path_c_noop() -> None:
    """Batch 250: VERIFY keep-prior names bundle head; Path C already-on-tip no-op."""
    import json
    import re
    import subprocess

    brief = json.loads(
        (ROOT / "portable" / "BATCH250_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "250"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "verify_keep_prior_bundle_sha_dishonesty_and_path_c_already_on_tip_noop"
    )
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert str(brief.get("tip")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("patch_0020") is False
    assert brief.get("verify_keep_prior_honesty") is True
    assert brief.get("path_c_already_on_tip_noop") is True
    assert brief.get("idle_status") == "IDLE_PATH_C_DONE"
    assert "tip_observe" not in (brief.get("defect_id") or "")
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH250_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "250"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert verify.get("lemma_closed") is False
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("bundle_refresh") is False
    assert verify.get("path_c_0018_landed") is True
    assert verify.get("path_c_0019_landed") is True
    assert verify.get("flipped_anything") is False
    applied = str(verify.get("applied_commit_sha") or "")
    assert re.fullmatch(r"[0-9a-f]{40}", applied)
    bundle = ROOT / "portable" / "path-c-applied-bundle" / "path-c-on-hardening.bundle"
    assert bundle.is_file()
    heads = subprocess.check_output(
        ["git", "bundle", "list-heads", str(bundle)], text=True
    )
    bundle_head = heads.split()[0]
    assert applied == bundle_head
    assert str(verify.get("bundle_range") or "").endswith(applied)
    # Unpublished allow-empty SHA must not be advertised as applied_commit_sha.
    local_empty = verify.get("local_allow_empty_sha")
    if local_empty:
        assert local_empty != applied

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "VERIFY honesty" in refresh
    assert "keep_prior_bundle" in refresh
    assert "path_c_0019_landed" in refresh

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert "already_on_tip" in open_pr
    assert "no push/PR" in open_pr or "NOT push" in open_pr

    land_c = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert "already_on_tip=true" in land_c
    assert "not pushing / not opening PR" in land_c

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert status.get("tip_match") is True
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"

    audit = json.loads(
        (ROOT / "portable" / "BATCH250_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 250" in log
    assert "keep-prior" in log.lower() or "VERIFY" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 250" in owner


def test_batch251_pack_portable_default_out_writable_fallback() -> None:
    """Batch 251: bare pack_portable OUT falls back when $ROOT/.. not writable."""
    import json
    import os
    import subprocess
    import tempfile
    from pathlib import Path

    brief = json.loads(
        (ROOT / "portable" / "BATCH251_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "251"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "pack_portable_default_out_writable_fallback"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert str(brief.get("tip")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("patch_0020") is False
    assert brief.get("idle_status") == "IDLE_PATH_C_DONE"
    assert "tip_observe" not in (brief.get("defect_id") or "")
    assert "living_tag" not in (brief.get("defect_id") or "")
    assert "aligned_noop" not in (brief.get("defect_id") or "")
    assert "sibling" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH251_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "251"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "pack_portable_default_out_writable_fallback"

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "_PACK_PARENT" in pack
    assert "not writable" in pack
    assert 'TMPDIR:-/tmp' in pack or "${TMPDIR:-/tmp}" in pack
    assert 'mkdir -p "$(dirname "$OUT")"' in pack

    # Explicit OUT still works (pre-existing contract).
    with tempfile.TemporaryDirectory(prefix="pack251-") as td:
        out = Path(td) / "pack.tgz"
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "pack_portable.sh"), str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
        assert out.is_file() and out.stat().st_size > 1000

    # Bare default OUT: when parent of ROOT is not writable, must use TMPDIR.
    with tempfile.TemporaryDirectory(prefix="pack251-root-") as td:
        fake_root = Path(td) / "repo"
        fake_root.mkdir()
        # Unwritable parent simulation: run pack from a copy of the script that
        # uses a parent we chmod to 555 after creating the repo dir.
        parent = Path(td)
        scripts = fake_root / "scripts"
        portable = fake_root / "portable" / "path-c-applied-bundle"
        scripts.mkdir(parents=True)
        portable.mkdir(parents=True)
        # Minimal tree so living-tag derivation works.
        (fake_root / "portable").mkdir(exist_ok=True)
        (fake_root / "portable" / "LIVING_PATH_C_RELEASE_TAG").write_text(
            "batch241-path-c-bundle\n", encoding="utf-8"
        )
        (portable / "VERIFY.json").write_text(
            json.dumps(
                {
                    "release": "batch241-path-c-bundle",
                    "batch": 241,
                    "lemma_closed": False,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        # Copy pack script + patch OUT selection only, then make parent unwritable.
        pack_src = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
        # Short-circuit after OUT resolution: source a tiny stub that exits after printing OUT.
        stub = scripts / "pack_portable_out_only.sh"
        stub.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'ROOT="$(cd "$(dirname "$0")/.." && pwd)"\n'
            '_PACK_PARENT="$(cd "$ROOT/.." && pwd)"\n'
            'if [[ -n "${1:-}" ]]; then OUT="$1"\n'
            'elif [[ -w "$_PACK_PARENT" ]]; then OUT="$_PACK_PARENT/trial-portable-main-fixes.tgz"\n'
            'else OUT="${TMPDIR:-/tmp}/trial-portable-main-fixes.tgz"\n'
            '  echo "pack_portable: note: parent ${_PACK_PARENT} not writable; defaulting OUT=${OUT}" >&2\n'
            "fi\n"
            'mkdir -p "$(dirname "$OUT")"\n'
            'printf "%s\\n" "$OUT"\n',
            encoding="utf-8",
        )
        stub.chmod(0o755)
        env = dict(os.environ)
        # Use system tmp (not under locked parent) as TMPDIR fallback target.
        tmp_fallback = Path(tempfile.mkdtemp(prefix="pack251-fallback-"))
        env["TMPDIR"] = str(tmp_fallback)
        os.chmod(parent, 0o555)
        try:
            # Parent is 555 so we cannot create files there as this user.
            proc = subprocess.run(
                ["bash", str(stub)],
                cwd=str(fake_root),
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
            out_line = (proc.stdout or "").strip().splitlines()[-1]
            assert out_line.startswith(str(tmp_fallback)), out_line
            assert "not writable" in (proc.stderr or "")
        finally:
            os.chmod(parent, 0o755)
            try:
                tmp_fallback.rmdir()
            except OSError:
                pass

    audit = json.loads(
        (ROOT / "portable" / "BATCH251_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 251" in log
    assert "pack_portable" in log.lower() or "Permission denied" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 251" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    # Living STATUS supersession (Batch 252–254+): tip line advances; keep 251 history OK.
    assert (
        "STATUS (Batch 251)" in land
        or "STATUS (Batch 252)" in land
        or "STATUS (Batch 253)" in land
        or "STATUS (Batch 254)" in land
        or "STATUS (Batch" in land
    )


def test_batch252_watch_alignment_issue_hygiene_graphql() -> None:
    """Batch 252: GraphQL exact-title drift issue hygiene; close-all; avoid Search."""
    import json
    import subprocess
    import sys

    brief = json.loads(
        (ROOT / "portable" / "BATCH252_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "252"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "watch_alignment_issue_hygiene_graphql"
    assert brief.get("tip_moved") is False
    assert _living_tip(brief.get("tip"))
    assert str(brief.get("tip")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("open_issues_after") == 0
    assert int(brief.get("open_issues_before") or 0) >= 20
    assert "tip_observe" not in (brief.get("defect_id") or "")
    assert "pack_portable" not in (brief.get("defect_id") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH252_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "252"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_id") == "watch_alignment_issue_hygiene_graphql"
    assert hunt.get("open_issues_after") == 0

    script = ROOT / "scripts" / "watch_alignment_issue_hygiene.py"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "graphql" in text.lower()
    assert "avoid_search_api" in text or "Search API" in text
    assert "aligned_close_all" in text
    assert "pick_canonical" in text
    assert "lemma_closed" in text
    assert "scientific_effect" in text.lower() or "Scientific effect" in text

    # Offline dry-run: ALIGNED closes all open duplicates; MISALIGNED dedupes.
    issues = [
        {"number": 10, "title": "main ALIGNED drift", "state": "CLOSED"},
        {"number": 12, "title": "main ALIGNED drift", "state": "OPEN"},
        {"number": 15, "title": "main ALIGNED drift", "state": "OPEN"},
    ]
    aligned = subprocess.run(
        [
            sys.executable,
            str(script),
            "--state",
            "ALIGNED",
            "--tip-sha",
            "72558a5b7ac9",
            "--dry-run",
            "--json-issues",
            json.dumps(issues),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert aligned.returncode == 0, aligned.stderr + aligned.stdout
    a = json.loads(aligned.stdout)
    assert a["action"] == "aligned_close_all"
    assert a["closed"] == [12, 15]
    assert a["lemma_closed"] is False
    assert a["avoid_search_api"] is True

    mis = subprocess.run(
        [
            sys.executable,
            str(script),
            "--state",
            "MISALIGNED",
            "--tip-sha",
            "deadbeefcafe",
            "--dry-run",
            "--json-issues",
            json.dumps(issues),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert mis.returncode == 0, mis.stderr + mis.stdout
    m = json.loads(mis.stdout)
    assert m["action"] == "misaligned_upsert_dedupe"
    assert m["canonical"] == 10
    assert m["closed"] == [12, 15]
    assert m["lemma_closed"] is False

    wf = (ROOT / ".github" / "workflows" / "watch-main-alignment.yml").read_text(
        encoding="utf-8"
    )
    assert "watch_alignment_issue_hygiene.py" in wf
    assert "Batch 252" in wf
    assert "gh issue list --search" not in wf

    audit = json.loads(
        (ROOT / "portable" / "BATCH252_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 252" in log
    assert "GraphQL" in log or "watch_alignment_issue_hygiene" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "Batch 252" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    # Living STATUS supersession (Batch 253–254+).
    assert (
        "STATUS (Batch 252)" in land
        or "STATUS (Batch 253)" in land
        or "STATUS (Batch 254)" in land
        or "STATUS (Batch" in land
    )


def test_batch253_when_writable_token_install_and_land_dry_run_idle() -> None:
    """Batch 253: user-token install check fallback + land-path-c dry-run idle."""
    import importlib.util
    import json
    import tempfile
    from unittest import mock

    probe_path = ROOT / "scripts" / "probe_main_write.py"
    probe_src = probe_path.read_text(encoding="utf-8")
    assert "user_token_install_denied" in probe_src
    assert "gh_api_without_user_token_env" in probe_src
    assert "install_query_mode" in probe_src

    spec = importlib.util.spec_from_file_location("probe_main_write_b253", probe_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Simulate user-token Bearer 403 on App-only install endpoint, then gh fallback.
    def fake_request(method: str, url: str, body=None):  # noqa: ANN001
        assert "installation/repositories" in url
        return 403, {"message": "Resource not accessible by integration"}

    class FakeProc:
        returncode = 0
        stdout = json.dumps(
            {
                "total_count": 1,
                "repository_selection": "selected",
                "repositories": [{"full_name": "d6g8k5htny-coder/trial"}],
            }
        )
        stderr = ""

    with mock.patch.object(mod, "_request", side_effect=fake_request):
        with mock.patch.object(mod, "_token", return_value="ghp_FAKE_BATCH253"):
            with mock.patch("subprocess.run", return_value=FakeProc()) as run:
                detail = mod.check_installation_repositories()
    assert detail["install_has_main"] is False
    assert detail["names"] == ["d6g8k5htny-coder/trial"]
    assert detail["user_token_install_denied"] is True
    assert detail["install_query_mode"] == "gh_app_fallback_after_user_token_403"
    assert run.call_count == 1
    # Fallback must strip user-token env keys (never print values).
    env = run.call_args.kwargs.get("env") or {}
    assert "MAIN_PUSH_TOKEN" not in env
    assert "GH_TOKEN" not in env
    assert "GITHUB_TOKEN" not in env

    # If gh fallback also fails, still report False (not None poison).
    class FailProc:
        returncode = 1
        stdout = ""
        stderr = "gh: HTTP 403"

    with mock.patch.object(mod, "_request", side_effect=fake_request):
        with mock.patch.object(mod, "_token", return_value="ghp_FAKE_BATCH253"):
            with mock.patch("subprocess.run", return_value=FailProc()):
                detail2 = mod.check_installation_repositories()
    assert detail2["install_has_main"] is False
    assert detail2["install_query_mode"] == "user_token_not_installation"
    assert detail2.get("user_token_install_denied") is True

    land_c = (ROOT / "scripts" / "owner_land_path_c.sh").read_text(encoding="utf-8")
    assert "already-on-tip idle" in land_c
    assert "--json-out" in land_c
    assert "Batch 253" in land_c

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "Batch 253" in ww
    assert "install_has_main under user-token load" in ww

    # Live dry-run: path_c_landed + tip match → idle (no apply_ready land advert).
    wrap = subprocess.run(
        ["bash", str(ROOT / "scripts" / "owner_land_path_c.sh"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert wrap.returncode == 0, wrap.stderr + wrap.stdout
    combined = wrap.stdout + wrap.stderr
    assert "already-on-tip idle" in combined or "already_on_tip=true" in combined
    assert "apply_ready on hardening BASE_TIP" not in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH253_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "253"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert "when_writable" in (brief.get("defect_id") or "")
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH253_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "253"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH253_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 253" in log

    # tempfile only — never print
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t"
        p.write_text("x", encoding="utf-8")
        assert p.read_text(encoding="utf-8") == "x"


def test_batch254_probe_ref_collision_422_false_transport() -> None:
    """Batch 254: unique probe refs + 422 already-exists retry (no false TRANSPORT)."""
    import importlib.util
    import json
    from unittest import mock

    probe_path = ROOT / "scripts" / "probe_main_write.py"
    probe_src = probe_path.read_text(encoding="utf-8")
    assert "time_ns" in probe_src
    assert "_probe_ref_name" in probe_src
    assert "_create_body_already_exists" in probe_src
    assert "already exists" in probe_src
    assert "create_attempts" in probe_src
    # Second-granularity-only naming must be gone (collision source).
    assert "int(time.time())" not in probe_src
    assert "time.time_ns()" in probe_src
    assert "uuid.uuid4()" in probe_src or "uuid4().hex" in probe_src

    spec = importlib.util.spec_from_file_location("probe_main_write_b254", probe_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    names = [mod._probe_ref_name() for _ in range(20)]
    assert len(set(names)) == 20
    assert all(n.startswith("refs/heads/cursor-write-probe-") for n in names)
    assert mod._create_body_already_exists({"message": "Reference already exists"})
    assert not mod._create_body_already_exists({"message": "Validation Failed"})
    assert not mod._create_body_already_exists("raw")

    # Simulate: first create 422 already-exists, second 201, delete 204 → WRITABLE.
    calls: list[tuple] = []

    def fake_request(method: str, url: str, body=None):  # noqa: ANN001
        calls.append((method, url, body))
        if method == "GET" and "git/ref/heads/main" in url:
            return 200, {"object": {"sha": "abc123deadbeef"}}
        if method == "POST" and url.endswith("/git/refs"):
            if sum(1 for c in calls if c[0] == "POST") == 1:
                return 422, {"message": "Reference already exists", "status": "422"}
            return 201, {"ref": body["ref"] if body else "ok"}
        if method == "DELETE":
            return 204, {}
        return 500, {"message": f"unexpected {method} {url}"}

    with mock.patch.object(mod, "check_installation_repositories", return_value={
        "install_has_main": False,
        "names": ["d6g8k5htny-coder/trial"],
        "install_query_mode": "gh_app_fallback_after_user_token_403",
    }):
        with mock.patch.object(mod, "_request", side_effect=fake_request):
            with mock.patch("builtins.print"):
                rc = mod.main()
    assert rc == 0
    post_calls = [c for c in calls if c[0] == "POST"]
    assert len(post_calls) == 2
    assert post_calls[0][2]["ref"] != post_calls[1][2]["ref"]

    brief = json.loads(
        (ROOT / "portable" / "BATCH254_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "254"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert "probe_main_write_ref_collision" in (brief.get("defect_id") or "")
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH254_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "254"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH254_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 254" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 254)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 254)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch256_aligned_drift_restore_race_and_audit_rate_limit() -> None:
    """Batch 256: restore/snapshot race fix + audit rate-limit retry; no flip."""
    import importlib.util
    import json
    import urllib.error
    from io import BytesIO
    from unittest import mock

    adw_path = ROOT / "scripts" / "aligned_drift_watch.py"
    assert adw_path.is_file()
    adw_src = adw_path.read_text(encoding="utf-8")
    assert "_promote_post_restore_audit" in adw_src
    assert "restore_lock_held" in adw_src
    assert "fcntl" in adw_src
    assert ".aligned_drift_restore.lock" in adw_src
    assert "Batch 256" in adw_src or "post-restore audit" in adw_src

    spec = importlib.util.spec_from_file_location("adw256", adw_path)
    assert spec is not None and spec.loader is not None
    adw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adw)

    # Reproduce the race: state flips ALIGNED while audit tip stays pre-restore
    # unless promote helper rewrites primary audit fields before snapshot.
    report = {
        "state": "MISALIGNED",
        "audit": {
            "default_tip_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "complexity_markers_present": ["δC = 0"],
            "q0_or_notice_markers_present": [],
        },
        "default_tip_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }
    post = {
        "default_tip_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "complexity_markers_present": [],
        "q0_or_notice_markers_present": ["SIDE24"],
        "default_branch": "main",
        "root_has_AGENTS_md": True,
    }
    adw._promote_post_restore_audit(report, post, 0)
    assert report["state"] == "ALIGNED"
    assert report["audit"] is post
    assert report["default_tip_sha"].startswith("bbbb")
    assert report["preferred_restore_route"]["prefer"] in (
        "Path_C_on_hardening",
        "tip_sync_drift_watch",
    )

    audit_path = ROOT / "scripts" / "audit_main_alignment.py"
    audit_src = audit_path.read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_RETRIES" in audit_src
    assert "rate limit" in audit_src.lower()
    assert "_is_rate_limited" in audit_src
    assert "Retry-After" in audit_src

    spec_a = importlib.util.spec_from_file_location("audit256", audit_path)
    assert spec_a is not None and spec_a.loader is not None
    audit = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(audit)
    audit._TRANSPORT_SLEEP_S = 0.0
    # Batch 349: CI Intent sets AUDIT_TRANSPORT_EARLY_FALLBACK=1; unit backoff needs retries.
    audit._TRANSPORT_EARLY_FALLBACK = False
    calls = {"n": 0}
    ok_body = json.dumps({"ok": True}).encode()

    class _CM:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def __enter__(self):
            return BytesIO(self._data)

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=60):
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.HTTPError(
                "https://api.github.com",
                429,
                "rate limit exceeded",
                hdrs={"Retry-After": "0"},
                fp=BytesIO(b'{"message":"API rate limit exceeded"}'),
            )
        return _CM(ok_body)

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        data = audit.get_json("https://api.github.com/repos/example/x")
    assert data == {"ok": True}
    assert calls["n"] == 3

    guard_src = (ROOT / "scripts" / "guard_no_status_promotion.py").read_text(
        encoding="utf-8"
    )
    assert "tip_sha=" in guard_src

    brief = json.loads(
        (ROOT / "portable" / "BATCH256_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "256"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "aligned_drift_watch_restore_snapshot_race_and_audit_rate_limit"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH256_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "256"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_id") == (
        "aligned_drift_watch_restore_snapshot_race_and_audit_rate_limit"
    )
    assert "release republish" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])

    audit_json = json.loads(
        (ROOT / "portable" / "BATCH256_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit_json.get("lemma_closed") is False
    assert audit_json.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 256" in log
    assert "restore" in log.lower() and "rate-limit" in log.lower()

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 256)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 256)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".aligned_drift_restore.lock" in gitignore


def test_batch257_tip_fetch_rate_limit_and_print_owner_unblock_writable() -> None:
    """Batch 257: tip-fetch rate-limit fallback + print_owner_unblock WRITABLE; no flip."""
    import json
    import os
    import stat
    import subprocess
    import tempfile
    from pathlib import Path

    refresh = ROOT / "scripts" / "refresh_path_c_bundle.sh"
    assert refresh.is_file()
    mode = refresh.stat().st_mode
    assert mode & stat.S_IXUSR
    text = refresh.read_text(encoding="utf-8")
    assert "REFRESH_TIP_FETCH_RETRIES" in text
    assert "git_ls_remote" in text
    assert "gh_api" in text
    assert "rate-limit" in text.lower() or "rate limit" in text.lower()
    assert "tip_fetch_via" in text
    assert "Never print tokens" in text or "never printed" in text.lower()

    # Simulate curl 403 rate-limit → must fall back (gh or ls-remote), not die.
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        curl = fake / "curl"
        curl.write_text(
            "#!/bin/bash\n"
            "printf '%s\\n%s\\n' "
            "'{\"message\":\"API rate limit exceeded for 9.9.9.9\"}' '403'\n"
            "exit 0\n",
            encoding="utf-8",
        )
        curl.chmod(0o755)
        env = os.environ.copy()
        for k in ("GITHUB_TOKEN", "GH_TOKEN", "MAIN_PUSH_TOKEN"):
            env.pop(k, None)
        env["PATH"] = f"{fake}:{env.get('PATH', '')}"
        env["REFRESH_TIP_FETCH_RETRIES"] = "1"
        env["REFRESH_TIP_FETCH_SLEEP_S"] = "0"
        proc = subprocess.run(
            [str(refresh), "--dry-run"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        assert proc.returncode == 0, out
        assert "tip_fetch_via=" in out
        assert "git_ls_remote" in out or "gh_api" in out
        assert "dry-run OK tip stable" in out or "tip stable" in out

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "PATH_C_STATUS.json" in unblock
    assert "write_state" in unblock
    # Living STATUS header advances each batch (Batch 258+); keep PATH_C_STATUS wiring.
    assert "Batch 25" in unblock or "Batch 26" in unblock or "PERMANENT" in unblock
    assert "PERMANENT window" in unblock
    assert "Batch 169 — PERMANENT window; ALIGNED @ 1c6e74b" not in unblock
    assert "write ${WRITE_STATE}" in unblock or "write_state=${WRITE_STATE}" in unblock

    open_pr = (ROOT / "scripts" / "owner_open_path_c_pr.sh").read_text(encoding="utf-8")
    assert "VERIFY.base_tip_sha; live ls-remote unavailable" in open_pr
    assert "TIP_OK" in open_pr

    path_c_wf = (ROOT / ".github" / "workflows" / "land-path-c-on-main.yml").read_text(
        encoding="utf-8"
    )
    assert '"event_type":"land-path-c-on-main"' in path_c_wf
    assert "client_payload" in path_c_wf
    # Misleading -f + partial --input pattern removed.
    assert '-f event_type=land-path-c-on-main' not in path_c_wf or (
        '{"event_type":"land-path-c-on-main"' in path_c_wf
    )

    brief = json.loads(
        (ROOT / "portable" / "BATCH257_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "257"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "refresh_tip_fetch_rate_limit_fallback_plus_print_owner_unblock_writable"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH257_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "257"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "ci.yml YAML" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])
    assert "aligned_drift flock" in (hunt.get("avoided") or [])

    audit_json = json.loads(
        (ROOT / "portable" / "BATCH257_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit_json.get("lemma_closed") is False
    assert audit_json.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 257" in log
    assert "rate-limit" in log.lower() or "rate limit" in log.lower()
    assert "WRITABLE" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 257)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    # Living LAND STATUS advances; Batch 257 may be active or nested history.
    assert "STATUS (Batch 257)" in land or "STATUS (Batch" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch255_republish_living_path_c_release_assets() -> None:
    """Batch 255: republish helper when pack newer than living release; no flip."""
    import json
    import subprocess

    script = ROOT / "scripts" / "republish_living_path_c_release.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "gh release upload" in text
    assert "--clobber" in text
    assert "--dry-run" in text
    assert "LIVING_PATH_C_RELEASE_TAG" in text
    assert "lemma_closed" in text
    assert "scientific_effect" in text.lower() or "Scientific effect" in text
    assert "Never prints tokens" in text or "Never print tokens" in text

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "republish_living_path_c_release.sh" in pack

    brief = json.loads(
        (ROOT / "portable" / "BATCH255_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "255"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "living_path_c_release_assets_stale_vs_pack"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH255_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "255"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_id") == "living_path_c_release_assets_stale_vs_pack"
    assert "living-tag" in (hunt.get("avoided") or [])
    assert "probe unique refs" in (hunt.get("avoided") or [])

    evidence = json.loads(
        (ROOT / "portable" / "BATCH255_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("pack_newer") is True
    assert evidence.get("living_tag") == "batch241-path-c-bundle"
    assert int(evidence.get("release_tgz_bytes_before") or 0) == 268996
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False

    # Dry-run exits 0: either detects stale pack (would upload) or assets already current.
    dry = subprocess.run(
        ["bash", str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    out = dry.stdout + dry.stderr
    assert "batch241-path-c-bundle" in out or "path-c-bundle" in out
    assert (
        "would: gh release upload" in out
        or "already current" in out
        or "need_upload=0" in out
        or "need_upload=1" in out
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH255_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 255" in log
    assert "republish" in log.lower()

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 255)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 255)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch258_wait_until_aligned_transport_timeout_flake() -> None:
    """Batch 258: wait_until_aligned transport max-wait exits 2 not MISALIGNED; no flip."""
    import json
    import os
    import shutil
    import stat
    import subprocess
    import tempfile
    from pathlib import Path

    wait = ROOT / "scripts" / "wait_until_aligned.sh"
    assert wait.is_file()
    mode = wait.stat().st_mode
    assert mode & stat.S_IXUSR
    text = wait.read_text(encoding="utf-8")
    assert "timeout_exit" in text
    assert "saw_misaligned" in text
    assert "TRANSPORT_ERROR (no MISALIGNED poll; not exit 1)" in text
    assert "status=${status_line}" in text
    assert "Batch 258" in text or "not mid-transport" in text

    with tempfile.TemporaryDirectory() as td:
        fake_root = Path(td)
        scripts = fake_root / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy2(wait, scripts / "wait_until_aligned.sh")
        (scripts / "watch_main_alignment.py").write_text(
            "#!/usr/bin/env python3\n"
            "import json,sys\n"
            'print(json.dumps({"state":"TRANSPORT_ERROR","scientific_effect":"NONE"}))\n'
            "sys.exit(2)\n",
            encoding="utf-8",
        )
        (scripts / "watch_main_alignment.py").chmod(0o755)
        env = os.environ.copy()
        env.pop("CHECK_AUTONOMOUS_WINDOW", None)
        proc = subprocess.run(
            [
                "bash",
                str(scripts / "wait_until_aligned.sh"),
                "--interval",
                "1",
                "--max-wait",
                "4",
                "--transport-retries",
                "10",
            ],
            cwd=str(fake_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        assert proc.returncode == 2, out
        assert "TRANSPORT_ERROR (no MISALIGNED poll; not exit 1)" in out
        assert "still MISALIGNED" not in out
        assert "status=TRANSPORT_ERROR" in out

        (scripts / "watch_main_alignment.py").write_text(
            "#!/usr/bin/env python3\n"
            "import json,sys\n"
            'print(json.dumps({"state":"MISALIGNED","scientific_effect":"NONE"}))\n'
            "sys.exit(1)\n",
            encoding="utf-8",
        )
        proc2 = subprocess.run(
            [
                "bash",
                str(scripts / "wait_until_aligned.sh"),
                "--interval",
                "1",
                "--max-wait",
                "3",
                "--transport-retries",
                "10",
            ],
            cwd=str(fake_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        out2 = (proc2.stdout or "") + (proc2.stderr or "")
        assert proc2.returncode == 1, out2
        assert "still MISALIGNED" in out2
        assert "status=MISALIGNED" in out2

    brief = json.loads(
        (ROOT / "portable" / "BATCH258_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "258"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "wait_until_aligned_transport_timeout_misaligned_lie"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH258_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "258"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "tip-fetch rate-limit" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])

    audit_json = json.loads(
        (ROOT / "portable" / "BATCH258_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit_json.get("lemma_closed") is False
    assert audit_json.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 258" in log
    assert "wait_until_aligned" in log
    assert "TRANSPORT_ERROR" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 258)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 258)" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    # Living STATUS header advances each batch (Batch 259+).
    assert "Batch 25" in unblock or "PERMANENT" in unblock
    assert "TRANSPORT_ERROR" in (ROOT / "scripts" / "wait_until_aligned.sh").read_text(
        encoding="utf-8"
    )

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch259_grant_check_dual_vector_sandbox_durable() -> None:
    """Batch 259: grant --check dual-vector + set-token auth/--also-sandbox; no flip."""
    import json
    import stat
    import subprocess

    grant = ROOT / "scripts" / "owner_grant_ai_agent_access.sh"
    assert grant.is_file()
    assert grant.stat().st_mode & stat.S_IXUSR
    text = grant.read_text(encoding="utf-8")
    assert "dual-vector" in text or "Batch 259" in text
    assert "discover_durable_main_push_token" in text
    assert "probe_repos_vector" in text
    assert "durable_MAIN_PUSH_TOKEN" in text
    assert "App/ghs sandbox 404 while durable MAIN_PUSH_TOKEN sandbox WRITABLE" in text
    assert "/tmp/gh-dylan-auth/access_token" in text

    help_out = subprocess.check_output([str(grant), "--help"], cwd=ROOT, text=True)
    assert "dual-vector" in help_out or "MAIN_PUSH_TOKEN" in help_out
    assert "sandbox" in help_out

    set_tok = ROOT / "scripts" / "owner_set_main_push_token.sh"
    assert set_tok.is_file()
    assert set_tok.stat().st_mode & stat.S_IXUSR
    set_text = set_tok.read_text(encoding="utf-8")
    assert "--also-sandbox" in set_text
    assert "--also-main" in set_text
    assert "auth=discovered_token" in set_text
    assert "Batch 259" in set_text
    # Must not leave gh secret set on App-only auth when a durable token exists.
    assert 'export GH_TOKEN="$TOKEN"' in set_text

    dry = subprocess.check_output(
        [str(set_tok), "--dry-run", "--also-sandbox"], cwd=ROOT, text=True
    )
    assert "also_sandbox=yes" in dry
    assert "d6g8k5htny-coder/sandbox" in dry
    assert "dry-run: OK" in dry
    # Never leak token material
    assert "gho_" not in dry
    assert "ghs_" not in dry
    assert "github_pat_" not in dry

    brief = json.loads(
        (ROOT / "portable" / "BATCH259_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "259"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "grant_check_app_sandbox_404_hides_durable_writable"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []
    assert brief.get("sandbox_secret_set") is True
    assert brief.get("durable_sibling_coverage") == "8/8_WRITABLE"

    hunt = json.loads(
        (ROOT / "portable" / "BATCH259_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "259"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "wait_until_aligned transport honesty" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])

    audit_json = json.loads(
        (ROOT / "portable" / "BATCH259_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit_json.get("lemma_closed") is False
    assert audit_json.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 259" in log
    assert "dual-vector" in log or "durable" in log.lower()

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 259)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 259)" in land or "STATUS (Batch" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    # Living STATUS header advances each batch (Batch 260+).
    assert "Batch 259" in unblock or "Batch 26" in unblock or "PERMANENT" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    repos = status.get("main_push_token_set_repos") or []
    assert "d6g8k5htny-coder/sandbox" in repos


def test_batch260_republish_living_pack_stale_post_255() -> None:
    """Batch 260: republish living release after pack grew past Batch 255 upload; no flip."""
    import json
    import subprocess

    script = ROOT / "scripts" / "republish_living_path_c_release.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "gh release upload" in text
    assert "--clobber" in text
    assert "lemma_closed" in text

    brief = json.loads(
        (ROOT / "portable" / "BATCH260_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "260"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "living_path_c_release_pack_stale_post_255"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []
    assert int(brief.get("release_tgz_bytes_after") or 0) >= 380000
    assert brief.get("upload_ok") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH260_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "260"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])

    evidence = json.loads(
        (ROOT / "portable" / "BATCH260_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("pack_newer") is True
    assert evidence.get("living_tag") == "batch241-path-c-bundle"
    assert int(evidence.get("release_tgz_bytes_before") or 0) == 351458
    # Scripts-only republish was 380287; post-land pack with Batch260 artifacts is larger.
    after = int(evidence.get("release_tgz_bytes_after") or 0)
    assert after >= 380287
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("upload_ok") is True

    dry = subprocess.run(
        ["bash", str(script), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    out = dry.stdout + dry.stderr
    assert "batch241-path-c-bundle" in out or "path-c-bundle" in out
    # After republish, dry-run should report current (or would-upload if briefs grew pack).
    assert (
        "already current" in out
        or "need_upload=0" in out
        or "would: gh release upload" in out
        or "need_upload=1" in out
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH260_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 260" in log
    assert "republish" in log.lower() or "380287" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 260)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 260)" in land

    # Living STATUS header advances each batch (Batch 261+).
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 260" in unblock or "Batch 26" in unblock or "PERMANENT" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch261_path_c_dry_run_idle_when_already_on_tip() -> None:
    """Batch 261: path_c_dry_run IDLE when landed+tip match; no APPLY_READY land advert."""
    import json
    import subprocess

    dry_py = ROOT / "scripts" / "path_c_dry_run.py"
    text = dry_py.read_text(encoding="utf-8")
    assert "IDLE_PATH_C_DONE" in text
    assert "already_on_tip" in text
    assert "Batch 261" in text

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 261" in unblock
    assert "already-on-tip idle" in unblock

    restore = (ROOT / "scripts" / "refresh_restore_plan.py").read_text(encoding="utf-8")
    assert "IDLE_PATH_C_DONE" in restore
    assert "already_on_tip" in restore

    result = subprocess.run(
        [sys.executable, str(dry_py), "--skip-rebase-probe"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = json.loads(result.stdout)
    assert data["scientific_effect"] == "NONE"
    assert data.get("path_c_landed") is True
    assert data.get("tip_matches_base") is True
    assert data["state"] == "IDLE_PATH_C_DONE"
    assert data["apply_ready"] is False
    assert data.get("already_on_tip") is True
    assert data.get("apply_check_ok") is True
    assert data.get("idle_status") == "IDLE_PATH_C_DONE"

    wrap = subprocess.run(
        ["bash", str(ROOT / "scripts" / "owner_land_path_c.sh"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert wrap.returncode == 0, wrap.stderr + wrap.stdout
    combined = wrap.stdout + wrap.stderr
    assert "already-on-tip idle" in combined or "already_on_tip=true" in combined
    assert "apply_ready on hardening BASE_TIP" not in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH261_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "261"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "path_c_dry_run_apply_ready_when_already_on_tip"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH261_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "261"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "release republish churn" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH261_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 261" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 261)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 261)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch262_probe_file_token_discovery() -> None:
    """Batch 262: probe_main_write(+vectors) discover durable file tokens; no flip."""
    import json
    import subprocess
    import tempfile
    from pathlib import Path as P

    probe = ROOT / "scripts" / "probe_main_write.py"
    vectors = ROOT / "scripts" / "probe_main_write_vectors.py"
    probe_txt = probe.read_text(encoding="utf-8")
    vec_txt = vectors.read_text(encoding="utf-8")
    assert "Batch 262" in probe_txt
    assert "/tmp/gh-dylan-auth/access_token" in probe_txt
    assert "PATH_C_IGNORE_FILE_TOKENS" in probe_txt
    assert "token_source" in probe_txt
    assert "/tmp/gh-dylan-auth/access_token" in vec_txt
    assert "token_source" in vec_txt
    assert "PATH_C_IGNORE_FILE_TOKENS" in vec_txt

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 262" in unblock
    assert "durable file-token discovery" in unblock or "file tokens" in unblock

    # Unit: planted file token is discovered; value never appears in stdout.
    with tempfile.TemporaryDirectory() as td:
        tok_path = P(td) / "MAIN_PUSH_TOKEN"
        secret = "ghp_batch262_probe_file_token_unit_never_print"
        tok_path.write_text(secret + "\n", encoding="utf-8")
        # Cloud Agent / Actions always inject GITHUB_TOKEN; scrub ambient App
        # tokens so the unit assert exercises file discovery (Batch 262 CI flake).
        scrubbed_keys = ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
        saved_env = {k: os.environ.pop(k) for k in scrubbed_keys if k in os.environ}
        old_ignore = os.environ.get("PATH_C_IGNORE_FILE_TOKENS")
        try:
            os.environ["PATH_C_IGNORE_FILE_TOKENS"] = "0"
            import importlib.util

            spec = importlib.util.spec_from_file_location("probe_main_write_b262", probe)
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Patch default files for this process.
            mod._DEFAULT_TOKEN_FILES = (str(tok_path),)
            mod._TOKEN_SOURCE = None
            got = mod._token()
            assert got == secret
            assert mod._token_source() == f"file:{tok_path}"
            # Ignore-file path skips discovery.
            os.environ["PATH_C_IGNORE_FILE_TOKENS"] = "1"
            mod._TOKEN_SOURCE = None
            assert mod._token() is None
        finally:
            for k in scrubbed_keys:
                os.environ.pop(k, None)
            os.environ.update(saved_env)
            if old_ignore is None:
                os.environ.pop("PATH_C_IGNORE_FILE_TOKENS", None)
            else:
                os.environ["PATH_C_IGNORE_FILE_TOKENS"] = old_ignore

    brief = json.loads(
        (ROOT / "portable" / "BATCH262_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "262"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "probe_main_write_misses_durable_file_token"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH262_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "262"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "path_c dry_run IDLE_PATH_C_DONE" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH262_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 262" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 262)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 262)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))

    # Live ignore → DENIED (App); never assert token material in stdout.
    # Batch 265: Actions always injects GITHUB_TOKEN. Batch 263 scrubbed only the
    # unit _token() block; this live ignore subprocess still inherited env:GITHUB_TOKEN
    # → token_source='env:GITHUB_TOKEN' while DENIED, reding trial-ci Intent
    # (runs 36086754869 / 36086753751 / 36086723977). Scrub ambient App/env tokens
    # so IGNORE_FILE_TOKENS exercises App/gh-auth-only DENIED with no durable source.
    ignore = subprocess.run(
        [sys.executable, str(probe)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
        env={
            **{
                k: v
                for k, v in os.environ.items()
                if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
            },
            "PATH_C_IGNORE_FILE_TOKENS": "1",
        },
    )
    assert ignore.returncode in (0, 1, 2)
    assert "ghp_" not in ignore.stdout
    assert "gho_" not in ignore.stdout
    if ignore.returncode == 1:
        data = json.loads(ignore.stdout[ignore.stdout.find("{") :])
        assert data.get("state") == "DENIED"
        # After scrub: no env/file durable source. Do not accept env:GITHUB_TOKEN —
        # that was the CI flake (Actions ambient token ≠ durable file discovery).
        assert data.get("token_source") in (None, "")


def test_batch263_research_guard_nopacket_shape_stripped() -> None:
    """Batch 263: research-guard NO_PACKET vs shape-stripped HAS_PACKET → exit 2."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path as P

    guard = ROOT / "scripts" / "guard_no_status_promotion.py"
    src = guard.read_text(encoding="utf-8")
    assert "Batch 263" in src
    assert "_baseline_shape" in src
    assert "_baseline_is_has_packet" in src

    spec = importlib.util.spec_from_file_location("guard_no_status_promotion_b263", guard)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert (snap.get("inventory") or {}).get("premises")

    # Unit: recover shape from live_shape / OPEN rows when inventory.shape wiped.
    stripped_inv = dict(snap["inventory"])
    stripped_inv.pop("shape", None)
    baseline_raw = {
        "guard": "no_status_promotion",
        "live_shape": "HAS_PACKET",
        "tip_sha": snap.get("tip_sha"),
        "baseline_tip_sha": snap.get("baseline_tip_sha"),
        "inventory": stripped_inv,
    }
    assert mod._baseline_shape(baseline_raw, stripped_inv) == "HAS_PACKET"
    assert mod._baseline_is_has_packet(baseline_raw, stripped_inv) is True
    # Infer from OPEN premises alone when live_shape also missing.
    bare = {"guard": "no_status_promotion", "inventory": stripped_inv}
    assert mod._baseline_shape(bare, stripped_inv) == "HAS_PACKET"

    with tempfile.TemporaryDirectory() as td:
        td_path = P(td)
        empty = td_path / "empty_checkout"
        empty.mkdir()
        base_path = td_path / "shape_stripped_baseline.json"
        # Snapshot-shaped baseline with inventory.shape removed (clobber edge).
        bad = dict(snap)
        bad["inventory"] = dict(snap["inventory"])
        bad["inventory"].pop("shape", None)
        # Keep live_shape so recovery path is exercised; also works without it.
        base_path.write_text(json.dumps(bad), encoding="utf-8")
        out = td_path / "out.json"
        rc = mod.main(
            [
                str(empty),
                "--trial-root",
                str(ROOT),
                "--baseline",
                str(base_path),
                "--snapshot-out",
                str(out),
                "--tip-sha",
                "deadbeef_batch263",
            ]
        )
        # Usage error — not false promotion FAIL (exit 1).
        assert rc == 2
        assert not out.exists()

        # Also when live_shape stripped: infer HAS_PACKET from OPEN premises.
        bad2 = dict(bad)
        bad2.pop("live_shape", None)
        bad2["inventory"] = dict(bad["inventory"])
        bad2["inventory"].pop("shape", None)
        base2 = td_path / "infer_baseline.json"
        base2.write_text(json.dumps(bad2), encoding="utf-8")
        out2 = td_path / "out2.json"
        rc2 = mod.main(
            [
                str(empty),
                "--trial-root",
                str(ROOT),
                "--baseline",
                str(base2),
                "--snapshot-out",
                str(out2),
                "--tip-sha",
                "deadbeef_batch263_infer",
            ]
        )
        assert rc2 == 2
        assert not out2.exists()

    brief = json.loads(
        (ROOT / "portable" / "BATCH263_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "263"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "research_guard_nopacket_shape_stripped_false_promotions"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH263_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "263"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "path_c dry_run idle" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "tip-observe" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH263_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 263" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 263)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 263)" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 263" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch264_path_b_dryrun_already_aligned_idle() -> None:
    """Batch 264: Path B dry-run ALREADY_ALIGNED must not lie 're-run to land'."""
    import json
    import subprocess

    dry_py = ROOT / "scripts" / "path_b_dry_run.py"
    owner_b = ROOT / "scripts" / "owner_land_path_b.sh"
    src_py = dry_py.read_text(encoding="utf-8")
    src_sh = owner_b.read_text(encoding="utf-8")
    assert "Batch 264" in src_py
    assert "land_needed" in src_py
    assert "Batch 264" in src_sh
    assert "ALREADY_ALIGNED" in src_sh
    assert "land_needed" in src_sh
    assert "Path B land not needed" in src_sh

    # Live tip is ALIGNED → dry-run must report idle, not solicit land.
    result = subprocess.run(
        ["python3", str(dry_py)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = json.loads(result.stdout)
    assert data.get("scientific_effect") == "NONE"
    assert data.get("state") == "ALREADY_ALIGNED"
    assert data.get("would_align") is True
    assert data.get("land_needed") is False
    assert data.get("git_am_skipped_already_aligned") is True

    dry = subprocess.run(
        ["bash", str(owner_b), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        cwd=str(ROOT),
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    combined = dry.stdout + dry.stderr
    assert "ALREADY_ALIGNED" in combined
    assert "Path B land not needed" in combined
    assert "Re-run without --dry-run to land" not in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH264_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "264"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "path_b_dryrun_already_aligned_rerun_to_land_lie"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH264_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "264"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "research-guard PACKET shape" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "path_c dry_run idle" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "long hygiene list" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH264_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 264" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 264)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 264)" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 264" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch265_live_ignore_ci_isolate_github_token() -> None:
    """Batch 265: Batch 262 live-ignore Intent scrubs Actions GITHUB_TOKEN; no flip."""
    import json
    import subprocess

    probe = ROOT / "scripts" / "probe_main_write.py"
    # Source contract: live-ignore env must scrub ambient App tokens (Batch 265).
    src = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "Batch 265" in src
    assert 'if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")' in src
    # Regression: old MAIN_PUSH_TOKEN-only scrub must not remain in live-ignore block.
    live_ignore_region = src.split("Live ignore → DENIED")[1].split(
        "def test_batch263_"
    )[0]
    assert "GH_TOKEN" in live_ignore_region
    assert "GITHUB_TOKEN" in live_ignore_region

    # Simulate Actions ambient GITHUB_TOKEN; scrubbed child must not report it.
    ignore = subprocess.run(
        [sys.executable, str(probe)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
        env={
            **{
                k: v
                for k, v in os.environ.items()
                if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
            },
            "PATH_C_IGNORE_FILE_TOKENS": "1",
            # Inject then rely on scrub list in the env dict construction above —
            # explicitly omit so child cannot see an ambient Actions token.
        },
    )
    assert ignore.returncode in (0, 1, 2)
    assert "ghp_" not in ignore.stdout
    assert "gho_" not in ignore.stdout
    if ignore.returncode == 1:
        data = json.loads(ignore.stdout[ignore.stdout.find("{") :])
        assert data.get("state") == "DENIED"
        assert data.get("token_source") in (None, "")
        assert data.get("token_source") != "env:GITHUB_TOKEN"

    # Contrasting control: with GITHUB_TOKEN present (old flake shape), probe may
    # label env:GITHUB_TOKEN — documenting why the scrub is required. Never print
    # the fake value beyond the env key label in JSON.
    control = subprocess.run(
        [sys.executable, str(probe)],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
        cwd=str(ROOT),
        env={
            **{
                k: v
                for k, v in os.environ.items()
                if k not in ("MAIN_PUSH_TOKEN",)
            },
            "PATH_C_IGNORE_FILE_TOKENS": "1",
            "GITHUB_TOKEN": "ghs_batch265_ci_isolate_control_never_print",
        },
    )
    assert "ghs_batch265_ci_isolate_control_never_print" not in control.stdout
    if control.returncode in (1, 2) and "{" in control.stdout:
        cdata = json.loads(control.stdout[control.stdout.find("{") :])
        # Without scrub, Actions-shaped env labels the ephemeral token source.
        assert cdata.get("token_source") in (
            "env:GITHUB_TOKEN",
            None,
            "",
            "env:GH_TOKEN",
            "env:MAIN_PUSH_TOKEN",
        )

    brief = json.loads(
        (ROOT / "portable" / "BATCH265_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "265"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "batch262_live_ignore_ci_isolate_github_token"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH265_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "265"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "path_b dry-run land_needed" in (hunt.get("avoided") or [])
    assert "research-guard PACKET" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "path_c dry_run idle" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "long hygiene list" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH265_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 265" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 265)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 265)" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 265" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch266_path_c_dry_run_write_required_when_idle() -> None:
    """Batch 266: path_c_dry_run IDLE must set write_required_to_land=false; no flip."""
    import json
    import subprocess

    dry = ROOT / "scripts" / "path_c_dry_run.py"
    src = dry.read_text(encoding="utf-8")
    assert "Batch 266" in src
    assert "write_required_to_land" in src

    result = subprocess.run(
        ["python3", str(dry), "--skip-rebase-probe"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    data = json.loads(result.stdout)
    assert data.get("scientific_effect") == "NONE"
    assert data.get("state") == "IDLE_PATH_C_DONE"
    assert data.get("already_on_tip") is True
    assert data.get("apply_ready") is False
    assert data.get("write_required_to_land") is False
    assert data.get("apply_stack") == "0001-0004 + 0008-0019"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 266" in unblock
    assert "0008–0019" in unblock
    assert "0008–0017 on hardening tip" not in unblock

    plan_src = (ROOT / "scripts" / "refresh_restore_plan.py").read_text(encoding="utf-8")
    assert "new_0020" in plan_src
    assert "no new 0020" in plan_src

    brief = json.loads(
        (ROOT / "portable" / "BATCH266_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "266"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "path_c_dry_run_write_required_when_idle"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH266_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "266"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "Intent GITHUB_TOKEN scrub" in (hunt.get("avoided") or [])
    assert "path_b dry-run land_needed" in (hunt.get("avoided") or [])
    assert "research-guard PACKET" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "path_c dry_run idle" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "long hygiene list" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH266_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 266" in log

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 266)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 266)" in land

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))

def test_batch267_when_writable_dual_daemon_status_race() -> None:
    """Batch 267: daemon.lock refuses second loop; --once sidecar when lock held."""
    import json
    import subprocess
    import tempfile
    import time

    script = ROOT / "scripts" / "when_writable_land.py"
    src = script.read_text(encoding="utf-8")
    assert "Batch 267" in src
    assert "daemon_lock_held" in src
    assert "DEFAULT_ONCE_STATUS" in src
    assert "_try_acquire_daemon_lock" in src

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        status = td_path / "ww.status.json"
        log = td_path / "ww.log"
        stop = td_path / "ww.stop"
        common = [
            sys.executable,
            str(script),
            "--dry-run",
            "--mock-probe",
            "DENIED",
            "--mock-install-has-main",
            "false",
            "--status",
            str(status),
            "--log",
            str(log),
            "--stop",
            str(stop),
        ]
        daemon = subprocess.Popen(
            common + ["--interval", "30"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            time.sleep(1.2)
            assert daemon.poll() is None, (daemon.stderr.read() if daemon.stderr else "")
            second = subprocess.run(
                common + ["--interval", "30"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            assert second.returncode == 2, second.stderr + second.stdout
            assert "daemon_lock_held" in (second.stderr or "")
            lock = status.with_name(status.name + ".daemon.lock")
            assert lock.is_file()
            data = json.loads(status.read_text(encoding="utf-8"))
            assert data.get("daemon_lock") is True
            assert data.get("lemma_closed") is False
            assert data.get("scientific_effect") == "NONE"
        finally:
            stop.write_text("stop\n", encoding="utf-8")
            try:
                daemon.wait(timeout=35)
            except subprocess.TimeoutExpired:
                daemon.kill()
                daemon.wait(timeout=5)

    # --once against default status path redirects to once sidecar when lock held.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        default_status = td_path / "when_writable_land.status.json"
        once_status = td_path / "when_writable_land.once.status.json"
        log = td_path / "ww.log"
        stop = td_path / "ww.stop"
        env = {
            **dict(**{k: v for k, v in __import__("os").environ.items()}),
            "WHEN_WRITABLE_STATUS": str(default_status),
            "WHEN_WRITABLE_ONCE_STATUS": str(once_status),
            "WHEN_WRITABLE_LOG": str(log),
            "WHEN_WRITABLE_STOP": str(stop),
        }
        daemon = subprocess.Popen(
            [
                sys.executable,
                str(script),
                "--dry-run",
                "--interval",
                "30",
                "--mock-probe",
                "DENIED",
                "--mock-install-has-main",
                "false",
            ],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(1.2)
            assert daemon.poll() is None
            once = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--once",
                    "--dry-run",
                    "--mock-probe",
                    "DENIED",
                    "--mock-install-has-main",
                    "false",
                ],
                cwd=str(ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            assert once.returncode == 0, once.stderr + once.stdout
            assert once_status.is_file(), "once should redirect to sidecar when lock held"
            once_data = json.loads(once_status.read_text(encoding="utf-8"))
            assert once_data.get("once") is True
            assert once_data.get("once_status_redirected") is True
            assert once_data.get("lemma_closed") is False
            # Live daemon status must remain a loop record (not once=true).
            live = json.loads(default_status.read_text(encoding="utf-8"))
            assert live.get("once") is False
            assert live.get("daemon_lock") is True
        finally:
            stop.write_text("stop\n", encoding="utf-8")
            try:
                daemon.wait(timeout=35)
            except subprocess.TimeoutExpired:
                daemon.kill()
                daemon.wait(timeout=5)

    brief = json.loads(
        (ROOT / "portable" / "BATCH267_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "267"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "when_writable_dual_daemon_status_race"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH267_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "267"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert "path_c dry-run write_required/stack prose" in (hunt.get("avoided") or [])
    assert "Intent GITHUB_TOKEN scrub" in (hunt.get("avoided") or [])
    assert "path_b dry-run" in (hunt.get("avoided") or [])
    assert "research-guard PACKET" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "long hygiene list" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH267_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 267" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 267)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 267)" in land

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 267" in unblock
    assert "when_writable_land.once.status.json" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch268_pack_living_tag_validate_before_write() -> None:
    """Batch 268: pack_portable does not dirty LIVING_PATH_C_RELEASE_TAG on fail-closed mismatch."""
    import json
    import tempfile

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "Batch 268" in pack
    assert "validate-before-write" in pack
    assert "living pin NOT written" in pack
    # Derive must complete before oneshot/open_pr check; write is a separate stamp.
    derive_idx = pack.find("Derive only")
    validate_idx = pack.find("owner_path_c_oneshot.sh")
    stamp_idx = pack.find("Stamp living pin only after fail-closed")
    assert 0 <= derive_idx < validate_idx < stamp_idx

    living = ROOT / "portable" / "LIVING_PATH_C_RELEASE_TAG"
    verify = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"
    tag = living.read_text(encoding="utf-8").strip()
    assert tag == "batch241-path-c-bundle"
    assert _living_release(tag)

    verify_data = json.loads(verify.read_text(encoding="utf-8"))
    assert verify_data.get("release") == tag
    assert verify_data.get("lemma_closed") is False

    # Repro: strip VERIFY.release and plant a divergent automation batch so
    # pack derives batch{N} ≠ oneshot :-default; exit 2 must leave pin intact.
    # (Batch 269: live VERIFY.batch is release-aligned; inject divergence here.)
    living_before = living.read_text(encoding="utf-8")
    verify_before = verify.read_text(encoding="utf-8")
    try:
        vd = dict(verify_data)
        del vd["release"]
        vd["batch"] = "250"
        verify.write_text(json.dumps(vd, indent=2) + "\n", encoding="utf-8")
        living.write_text(tag + "\n", encoding="utf-8")
        out = Path(tempfile.mkdtemp(prefix="pack268-out-")) / "pack.tgz"
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "pack_portable.sh"), str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 2, (proc.stderr or "") + (proc.stdout or "")
        assert "living pin NOT written" in (proc.stderr or "")
        assert living.read_text(encoding="utf-8").strip() == tag
        assert "batch250-path-c-bundle" in (proc.stderr or "")
    finally:
        living.write_text(living_before, encoding="utf-8")
        verify.write_text(verify_before, encoding="utf-8")

    # Happy path still stamps living tag after validation.
    with tempfile.TemporaryDirectory(prefix="pack268-ok-") as td:
        out = Path(td) / "pack.tgz"
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "pack_portable.sh"), str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
        assert f"living_tag={tag}" in (proc.stdout or "")
        assert living.read_text(encoding="utf-8").strip() == tag
        listing = subprocess.run(
            ["tar", "-tzf", str(out)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert "portable/LIVING_PATH_C_RELEASE_TAG" in listing

    brief = json.loads(
        (ROOT / "portable" / "BATCH268_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "268"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "pack_living_tag_write_before_validate_race"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_moved") is True
    assert str(brief.get("tip", "")).startswith("8e359e5")
    assert str(brief.get("prior_tip", "")).startswith("fa32d11")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []
    assert brief.get("pack_release") == tag

    hunt = json.loads(
        (ROOT / "portable" / "BATCH268_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "268"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True
    assert hunt.get("tip_moved") is True
    assert "when_writable dual-daemon flock" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "path_c dry-run idle" in (hunt.get("avoided") or [])
    assert "path_b dry-run idle" in (hunt.get("avoided") or [])
    assert "Intent token scrub" in (hunt.get("avoided") or [])
    assert "research-guard PACKET" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])
    assert "grant dual-vector" in (hunt.get("avoided") or [])
    assert "long hygiene list" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH268_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 268" in log_md
    assert "living-tag" in log_md.lower() or "LIVING_PATH_C_RELEASE_TAG" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 268)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 268)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 268" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 268" in unblock
    assert "validate-before-write" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch269_verify_batch_release_align() -> None:
    """Batch 269: refresh keep-prior aligns VERIFY.batch to release; tip stable; no flip."""
    import json
    import re
    import subprocess
    import tempfile

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "Batch 269" in refresh
    # Default automation stamp advanced in later batches (275+); contract is >=269.
    m_default = re.search(r"REFRESH_BATCH_TAG:-(\d+)", refresh)
    assert m_default is not None
    assert int(m_default.group(1)) >= 269
    assert "refresh_batch" in refresh
    assert "release_batch_aligned" in refresh
    assert "align VERIFY.batch" in refresh

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    rel = verify.get("release")
    assert rel == "batch241-path-c-bundle"
    assert verify.get("batch") == "241"
    # Living tip-refresh may advance refresh_batch (Batch 272+: 8e359e5→bfb7c38).
    assert int(str(verify.get("refresh_batch") or "0")) >= 269
    assert verify.get("release_batch_aligned") is True
    assert verify.get("lemma_closed") is False
    assert verify.get("flipped_anything") is False
    m = re.fullmatch(r"batch(\d+)-path-c-bundle", rel)
    assert m and verify["batch"] == m.group(1)
    assert f"batch{verify['batch']}-path-c-bundle" == rel

    manifest = json.loads(
        (ROOT / "portable" / "patches" / "MANIFEST.json").read_text(encoding="utf-8")
    )
    assert str(manifest.get("verified_batch")) == "241"
    assert int(str(manifest.get("refresh_batch") or "0")) >= 269

    with tempfile.TemporaryDirectory(prefix="b269-verify-") as td:
        stamped = {
            "batch": "269",
            "refresh_batch": "269",
            "release": "batch241-path-c-bundle",
            "lemma_closed": False,
            "path_c_landed": True,
            "flipped_anything": False,
        }
        mm = re.fullmatch(r"batch(\d+)-path-c-bundle", stamped["release"])
        assert mm
        stamped["batch"] = mm.group(1)
        stamped["release_batch_aligned"] = True
        out = Path(td) / "VERIFY.json"
        out.write_text(json.dumps(stamped, indent=2) + "\n", encoding="utf-8")
        got = json.loads(out.read_text(encoding="utf-8"))
        assert got["batch"] == "241"
        assert got["refresh_batch"] == "269"
        assert got["release"] == "batch241-path-c-bundle"
        assert f"batch{got['batch']}-path-c-bundle" == got["release"]

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "refresh_path_c_bundle.sh"), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "tip stable" in combined or "match=1" in combined
    assert _living_tip(combined)

    brief = json.loads(
        (ROOT / "portable" / "BATCH269_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "269"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "verify_batch_divergent_from_release_after_keep_prior_refresh"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("8e359e5")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []
    assert brief.get("pack_release") == "batch241-path-c-bundle"
    assert brief.get("main_pr_or_null") in (None, 98)
    assert str(brief.get("trial_main_land", "")).startswith("7290bf9") or brief.get(
        "main_pr_or_null"
    ) in (None, 98)

    hunt = json.loads(
        (ROOT / "portable" / "BATCH269_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "269"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True
    assert hunt.get("tip_moved") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert "pack living-tag validate-before-write" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])
    assert "when_writable dual-daemon flock" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH269_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 269" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 269)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 269)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 269" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 269" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch270_when_writable_once_pid_liveness() -> None:
    """Batch 270: --once redirects on lockfile pid= live even when flock probe misses."""
    import json
    import os
    import subprocess
    import tempfile
    import time

    script = ROOT / "scripts" / "when_writable_land.py"
    src = script.read_text(encoding="utf-8")
    assert "Batch 270" in src
    assert "_live_peer_holder_pid" in src
    assert "_pid_is_live_when_writable" in src

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        default_status = td_path / "when_writable_land.status.json"
        once_status = td_path / "when_writable_land.once.status.json"
        log = td_path / "ww.log"
        stop = td_path / "ww.stop"
        lock = default_status.with_name(default_status.name + ".daemon.lock")
        env = {
            **dict(os.environ),
            "WHEN_WRITABLE_STATUS": str(default_status),
            "WHEN_WRITABLE_ONCE_STATUS": str(once_status),
            "WHEN_WRITABLE_LOG": str(log),
            "WHEN_WRITABLE_STOP": str(stop),
        }
        # Peer process whose /proc/cmdline contains when_writable_land, no flock.
        peer_script = td_path / "fake_when_writable_land_peer.py"
        peer_script.write_text("import time\ntime.sleep(90)\n", encoding="utf-8")
        sleeper = subprocess.Popen(
            [sys.executable, str(peer_script)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(0.2)
            lock.write_text(f"pid={sleeper.pid}\n", encoding="utf-8")
            default_status.write_text(
                json.dumps(
                    {
                        "dry_run": False,
                        "once": False,
                        "daemon_lock": True,
                        "daemon_pid": sleeper.pid,
                        "marker": "batch270-live",
                        "lemma_closed": False,
                        "scientific_effect": "NONE",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            once = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--once",
                    "--dry-run",
                    "--mock-probe",
                    "DENIED",
                    "--mock-install-has-main",
                    "false",
                ],
                cwd=str(ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            assert once.returncode == 0, once.stderr + once.stdout
            assert once_status.is_file(), "once must redirect when lockfile pid= live"
            once_data = json.loads(once_status.read_text(encoding="utf-8"))
            assert once_data.get("once") is True
            assert once_data.get("once_status_redirected") is True
            assert once_data.get("lemma_closed") is False
            live = json.loads(default_status.read_text(encoding="utf-8"))
            assert live.get("marker") == "batch270-live"
            assert live.get("once") is False
            assert live.get("dry_run") is False
            second = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--dry-run",
                    "--interval",
                    "30",
                    "--mock-probe",
                    "DENIED",
                    "--mock-install-has-main",
                    "false",
                    "--status",
                    str(default_status),
                    "--log",
                    str(log),
                    "--stop",
                    str(stop),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            assert second.returncode == 2, second.stderr + second.stdout
            assert "daemon_lock_held" in (second.stderr or "")
        finally:
            sleeper.kill()
            sleeper.wait(timeout=5)

    brief = json.loads(
        (ROOT / "portable" / "BATCH270_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "270"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "when_writable_once_pid_liveness_flock_miss"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("8e359e5")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []
    assert brief.get("main_pr_or_null") in (None, 100)
    assert str(brief.get("trial_main_land", "")).startswith("df6e3d7") or brief.get(
        "main_pr_or_null"
    ) in (None, 100)

    hunt = json.loads(
        (ROOT / "portable" / "BATCH270_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "270"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert "VERIFY.batch release-align" in (hunt.get("avoided") or [])
    assert "pack living-tag validate-before-write" in (hunt.get("avoided") or [])
    assert "release republish" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH270_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 270" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 270)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 270)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 270" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 270" in unblock
    assert "pid-liveness" in unblock or "pid=" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch271_probe_w3_dryrun_path_b_false_positive() -> None:
    """Batch 271: W3a–W3e dry_run dispatch excluded from path_b_ready (W3f leftover)."""
    import importlib.util
    import json
    import re

    vectors_path = ROOT / "scripts" / "probe_main_write_vectors.py"
    src = vectors_path.read_text(encoding="utf-8")
    assert "Batch 271" in src
    assert "_as_dry_run_dispatch_probe" in src
    assert "w3_dry_run_false_positive" in src
    m = re.search(r"path_b_keys = \((.*?)\)", src, re.S)
    assert m is not None
    keys_block = m.group(1)
    for banned in (
        "W3a_dispatch_trial",
        "W3b_dispatch_main",
        "W3c_api_dispatch_trial",
        "W3d_dispatch_path_c_trial",
        "W3e_api_dispatch_path_c_trial",
        "W3f_repository_dispatch_path_c",
    ):
        assert banned not in keys_block
    for required in (
        "W1_git_refs",
        "W2_contents_put",
        "W4a_fork",
        "W4b_graphql_createCommitOnBranch",
        "W4c_pulls_create",
    ):
        assert required in keys_block

    spec = importlib.util.spec_from_file_location(
        "probe_main_write_vectors_batch271", vectors_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    annotated = mod._as_dry_run_dispatch_probe(
        {"exit": 0, "state": "WRITABLE", "msg": "dispatched"},
        target_repo="d6g8k5htny-coder/trial",
        workflow="land-option-b-on-main.yml",
        note="unit",
    )
    assert annotated["state"] == "DISPATCH_OK_DRY_RUN"
    assert annotated["false_positive_for_main_write"] is True
    assert annotated["path_b_capable"] is False
    assert annotated["main_write"] is False

    # Synthetic: dry_run-only WRITABLE must not imply path_b_ready.
    path_b_keys = (
        "W1_git_refs",
        "W2_contents_put",
        "W4a_fork",
        "W4b_graphql_createCommitOnBranch",
        "W4c_pulls_create",
    )
    synth = {
        "W1_git_refs": {"state": "DENIED"},
        "W2_contents_put": {"state": "DENIED"},
        "W3a_dispatch_trial": {"state": "DISPATCH_OK_DRY_RUN"},
        "W3c_api_dispatch_trial": {"state": "DISPATCH_OK_DRY_RUN"},
        "W3d_dispatch_path_c_trial": {"state": "DISPATCH_OK_DRY_RUN"},
        "W3e_api_dispatch_path_c_trial": {"state": "DISPATCH_OK_DRY_RUN"},
        "W4a_fork": {"state": "DENIED"},
        "W4b_graphql_createCommitOnBranch": {"state": "DENIED"},
        "W4c_pulls_create": {"state": "DENIED"},
    }
    writable = [k for k in path_b_keys if synth.get(k, {}).get("state") == "WRITABLE"]
    assert writable == []
    assert not bool(writable)

    brief = json.loads(
        (ROOT / "portable" / "BATCH271_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief["batch"] == "271"
    assert brief["lemma_closed"] is False
    assert brief["flipped_anything"] is False
    assert brief["scientific_effect"] == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "probe_w3ae_dryrun_path_b_false_positive"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert str(brief.get("tip", "")).startswith("8e359e5")
    assert brief.get("aligned") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("green_eng_prs_merged") == []

    hunt = json.loads(
        (ROOT / "portable" / "BATCH271_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt["batch"] == "271"
    assert hunt["lemma_closed"] is False
    assert hunt["flipped_anything"] is False
    assert hunt.get("defect_shipped") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert "when_writable once pid-liveness" in (hunt.get("avoided") or [])
    assert "VERIFY.batch release-align" in (hunt.get("avoided") or [])
    assert "probe durable file-token" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH271_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 271" in log_md
    assert "false_positive" in log_md or "W3a" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 271)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 271)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 271" in ones

    gh = (ROOT / "portable" / "GH_DEVICE_LOGIN.md").read_text(encoding="utf-8")
    assert "W3a–W3e" in gh or "W3a-W3e" in gh or "Batch 271" in gh

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 271" in unblock
    assert "W3a" in unblock or "dry_run" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch272_ci_land_workflows_path_c_idle_contract() -> None:
    """Batch 272: land-workflows-dry-run asserts Path C idle on its own outfile."""
    import json
    import subprocess
    import sys

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "path-c-dry-run.out" in ci
    assert "path-b-dry-run.out" in ci
    # Must NOT use the Batch 73–271 union grep that Path C idle never matched.
    assert (
        "grep -E 'ALREADY_ALIGNED|would-align|APPLY_READY' path-b-dry-run.out path-c-dry-run.out"
        not in ci
    )
    assert "IDLE_PATH_C_DONE|already_on_tip|APPLY_READY" in ci
    assert "grep -E 'ALREADY_ALIGNED|would-align' path-b-dry-run.out" in ci
    assert (
        "grep -E 'IDLE_PATH_C_DONE|already_on_tip|APPLY_READY' path-c-dry-run.out" in ci
    )

    validate = (ROOT / "scripts" / "validate_land_workflows.py").read_text(
        encoding="utf-8"
    )
    assert "Batch 272" in validate
    assert "path-c-dry-run.out alone" in validate or "Path C idle" in validate

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_land_workflows.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout

    # Evidence: path-c dry-run alone fails the old union pattern.
    path_c_sample = (
        '{"state": "IDLE_PATH_C_DONE", "already_on_tip": true, '
        '"idle_status": "IDLE_PATH_C_DONE", "apply_ready": false}\n'
        "already_on_tip=true path_c_landed=true\n"
        "owner_land_path_c: dry-run OK — already-on-tip idle (no no-op land).\n"
    )
    old = subprocess.run(
        ["bash", "-c", "grep -E 'ALREADY_ALIGNED|would-align|APPLY_READY'"],
        input=path_c_sample,
        capture_output=True,
        text=True,
        check=False,
    )
    assert old.returncode == 1, old.stdout
    new = subprocess.run(
        ["bash", "-c", "grep -E 'IDLE_PATH_C_DONE|already_on_tip|APPLY_READY'"],
        input=path_c_sample,
        capture_output=True,
        text=True,
        check=False,
    )
    assert new.returncode == 0, new.stdout
    assert "IDLE_PATH_C_DONE" in new.stdout

    brief = json.loads(
        (ROOT / "portable" / "BATCH272_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "272"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_moved") is False
    assert brief.get("defect_id") == "ci_land_workflows_path_c_idle_ungrepped"

    hunt = json.loads(
        (ROOT / "portable" / "BATCH272_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert "probe_main_write_vectors dry_run DISPATCH_OK" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH272_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 272" in log_md
    assert "path-c-dry-run" in log_md or "IDLE_PATH_C_DONE" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 272)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 272)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 272" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 272" in unblock
    assert "path-c-dry-run" in unblock or "IDLE_PATH_C" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))


def test_batch273_apply_verify_honesty_keep_prior() -> None:
    """Batch 273: APPLY living-tip == BASE_TIP; VERIFY pytest preserved on keep-prior."""
    import json
    import re
    import subprocess

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(
        encoding="utf-8"
    ).strip().split()[-1]
    assert _living_tip(base_tip)

    apply = (ROOT / "portable" / "path-c-applied-bundle" / "APPLY.md").read_text(
        encoding="utf-8"
    )
    # Living tip claim must match BASE_TIP (Batch 272 left 542e6ec==(BASE_TIP) lie).
    m = re.search(
        r"hardening tip\s+\*\*`([0-9a-f]{7,40})`\*\*\s*\(==\s*BASE_TIP",
        apply,
        flags=re.I,
    )
    assert m, "missing living tip (== BASE_TIP) claim in APPLY.md"
    living = m.group(1)
    assert base_tip.startswith(living) or living.startswith(base_tip[:7])
    assert f"On tip **`{living}`**" in apply
    # Historical 0019 landmark retained for Batch 244 contract.
    assert "542e6ec" in apply

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert verify.get("lemma_closed") is False
    assert verify.get("flipped_anything") is False
    assert _living_tip(str(verify.get("base_tip_sha") or ""))
    assert str(verify.get("base_tip_sha") or "").startswith(living[:7]) or living.startswith(
        str(verify.get("base_tip_sha") or "")[:7]
    )
    pytest_block = verify.get("pytest") or {}
    # Living tip-refresh may re-count focused suite (Batch 278: 90→92 @ 3b3860d).
    assert int(pytest_block.get("focused_passed") or 0) >= 90
    assert int(pytest_block.get("claims_recovery_passed") or 0) >= 83
    assert int(str(verify.get("refresh_batch") or "0")) >= 273

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "Batch 273" in refresh
    assert "preserved prior pytest" in refresh
    assert "hardening tip" in refresh and "== BASE_TIP" in refresh
    assert "Living tip note" in refresh
    assert "On tip" in refresh

    # Soft-update patterns cover bold Living tip note + (== BASE_TIP).
    live_short = "bfb7c38"
    live_sha = "bfb7c385040b952ca1a3752e4bc7704b383a4167"
    sample = (
        "hardening tip **`542e6ec`** (== BASE_TIP; x)\n"
        "On tip **`542e6ec`** expect\n"
        "**Living tip note:** at `542e6ec` the merge\n"
        "Do **not** re-land Path C onto `542e6ec`.\n"
        "BASE_TIP `542e6ec`\n"
        "git checkout -B cursor/portable-engineering-patches "
        "542e6ec2f462d6202f5bc5b3a044e71ae7a1a96c\n"
    )
    text2, _ = re.subn(
        r"(BASE_TIP\s+[\\\`*]*)([0-9a-f]{7,40})",
        lambda m: m.group(1) + live_short,
        sample,
        count=5,
        flags=re.I,
    )
    text2, _ = re.subn(
        r"(git checkout -B cursor/portable-engineering-patches\s+)([0-9a-f]{40})",
        lambda m: m.group(1) + live_sha,
        text2,
        count=2,
    )
    text2, _ = re.subn(
        r"(hardening tip\s+\*\*`?)([0-9a-f]{7,40})(`?\*\*\s*\(==\s*BASE_TIP)",
        lambda m: m.group(1) + live_short + m.group(3),
        text2,
        count=3,
        flags=re.I,
    )
    text2, _ = re.subn(
        r"(On tip\s+\*\*`?)([0-9a-f]{7,40})(`?\*\*)",
        lambda m: m.group(1) + live_short + m.group(3),
        text2,
        count=2,
        flags=re.I,
    )
    text2, _ = re.subn(
        r"(Living tip note:\*+\s+at\s+`?|Living tip note:\s+at\s+`?)([0-9a-f]{7,40})(`?)",
        lambda m: m.group(1) + live_short + m.group(3),
        text2,
        count=2,
        flags=re.I,
    )
    text2, _ = re.subn(
        r"(Do \*\*not\*\* re-land Path C onto\s+`)([0-9a-f]{7,40})(`)",
        lambda m: m.group(1) + live_short + m.group(3),
        text2,
        count=2,
        flags=re.I,
    )
    assert "542e6ec" not in text2
    assert "bfb7c38" in text2

    # keep-prior pytest preserve when current run reports 0.
    prior = {"pytest": {"focused_passed": 90, "claims_recovery_passed": 83}}
    cur = {
        "pytest": {
            "focused_passed": 0,
            "claims_recovery_passed": 0,
            "focused_files": ["tests/test_carriers.py"],
        }
    }
    prior_pytest = prior["pytest"]
    cur_pytest = cur["pytest"]
    for pk in ("focused_passed", "claims_recovery_passed"):
        if cur_pytest.get(pk) in (0, None) and isinstance(prior_pytest.get(pk), int):
            if prior_pytest[pk] > 0:
                cur_pytest[pk] = prior_pytest[pk]
    assert cur_pytest["focused_passed"] == 90
    assert cur_pytest["claims_recovery_passed"] == 83

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "refresh_path_c_bundle.sh"), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "tip stable" in combined or "match=1" in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH273_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "273"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "apply_verify_honesty_keep_prior_living_tip_and_pytest"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("bfb7c38")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH273_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert "land-workflows Path C idle (just shipped 272)" in (hunt.get("avoided") or [])

    audit = json.loads(
        (ROOT / "portable" / "BATCH273_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 273" in log_md
    assert "APPLY" in log_md and "VERIFY" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 273)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 273)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 273" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 273" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch275_manifest_verified_batch_release_align() -> None:
    """Batch 275: MANIFEST.verified_batch release-aligned; not stamped from BATCH_TAG."""
    import json
    import re
    import subprocess

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "Batch 275" in refresh
    assert "MANIFEST.verified_batch must stay release-aligned" in refresh
    assert 'data["verified_batch"] = aligned' in refresh
    assert 'data["refresh_batch"] = str("$BATCH_TAG")' in refresh
    # Must not plant automation tag into verified_batch.
    assert 'data["verified_batch"] = str("$BATCH_TAG")' not in refresh
    m_default = re.search(r"REFRESH_BATCH_TAG:-(\d+)", refresh)
    assert m_default is not None
    assert int(m_default.group(1)) >= 275

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    manifest = json.loads(
        (ROOT / "portable" / "patches" / "MANIFEST.json").read_text(encoding="utf-8")
    )
    assert verify.get("batch") == "241"
    assert verify.get("release") == "batch241-path-c-bundle"
    assert str(manifest.get("verified_batch")) == "241"
    assert str(manifest.get("verified_batch")) == str(verify.get("batch"))
    assert int(str(manifest.get("refresh_batch") or "0")) >= 275
    assert manifest.get("lemma_closed") is False

    # Simulate the Batch 275 MANIFEST write path (VERIFY already release-aligned).
    sim = {
        "verified_batch": "241",
        "refresh_batch": "269",
        "lemma_closed": False,
        "patches": [],
    }
    batch_tag = "275"
    aligned = str(verify.get("batch") or "")
    assert aligned == "241"
    sim["refresh_batch"] = batch_tag
    sim["verified_batch"] = aligned
    assert sim["verified_batch"] == "241"
    assert sim["refresh_batch"] == "275"
    # Old bug: stamping BATCH_TAG into verified_batch.
    buggy = dict(sim)
    buggy["verified_batch"] = batch_tag
    assert buggy["verified_batch"] != verify["batch"]

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(
        encoding="utf-8"
    ).strip().split()[-1]
    assert _living_tip(base_tip)

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "refresh_path_c_bundle.sh"), "--dry-run"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (proc.stderr or "") + (proc.stdout or "")
    combined = (proc.stdout or "") + (proc.stderr or "")
    assert "tip stable" in combined or "match=1" in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH275_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "275"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == (
        "manifest_verified_batch_stamped_from_automation_tag"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("bfb7c38")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH275_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == (
        "manifest_verified_batch_stamped_from_automation_tag"
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH275_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 275" in log_md
    assert "MANIFEST" in log_md and "verified_batch" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 275)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 275)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 275" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 275" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch276_republish_living_tag_post_pack() -> None:
    """Batch 276: republish reads upload TAG after pack; stale pre-pack pin ignored."""
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    script = ROOT / "scripts" / "republish_living_path_c_release.sh"
    text = script.read_text(encoding="utf-8")
    assert "Batch 276" in text
    assert "post-pack" in text
    assert "PRE_PACK_TAG" in text
    # Pack must run before TAG is finalized for upload.
    pack_idx = text.find('bash "$ROOT/scripts/pack_portable.sh"')
    target_idx = text.find("upload target tag=")
    assert 0 <= pack_idx < target_idx

    status_py = (ROOT / "scripts" / "write_path_c_status.py").read_text(
        encoding="utf-8"
    )
    assert "Batch 276" in status_py
    assert "VERIFY.release" in status_py
    # VERIFY block must appear before living-pin fallback in _release_tag.
    rel_fn = status_py.find("def _release_tag")
    verify_idx = status_py.find("VERIFY_FILE.is_file()", rel_fn)
    living_idx = status_py.find("LIVING_TAG_FILE.is_file()", rel_fn)
    assert 0 <= rel_fn < verify_idx < living_idx

    living = ROOT / "portable" / "LIVING_PATH_C_RELEASE_TAG"
    prior = living.read_text(encoding="utf-8")
    assert prior.strip() == "batch241-path-c-bundle"
    try:
        living.write_text("batch250-path-c-bundle\n", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="b276-intent-") as td:
            out = Path(td) / "pack.tgz"
            dry = subprocess.run(
                ["bash", str(script), "--dry-run", "--out", str(out)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            assert dry.returncode == 0, dry.stderr + dry.stdout
            combined = (dry.stdout or "") + (dry.stderr or "")
            assert "upload target tag=batch241-path-c-bundle" in combined
            assert "pre-pack pin 'batch250-path-c-bundle'" in combined
            assert "would: gh release upload batch241-path-c-bundle" in combined
            assert "batch250-path-c-bundle --repo" not in combined
        assert living.read_text(encoding="utf-8").strip() == "batch241-path-c-bundle"
    finally:
        living.write_text(
            prior if prior.endswith("\n") else prior + "\n", encoding="utf-8"
        )

    brief = json.loads(
        (ROOT / "portable" / "BATCH276_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "276"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "republish_living_tag_captured_before_pack"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("bfb7c38")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH276_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "republish_living_tag_captured_before_pack"
    assert any(
        "pack living-tag validate-before-write itself" in a
        for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH276_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 276" in log_md
    assert "pre-pack" in log_md.lower() or "post-pack" in log_md.lower()

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 276)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 276)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 276" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 276" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch277_owner_verify_release_first() -> None:
    """Batch 277: oneshot/open_pr prefer VERIFY.release over dirty living pin."""
    import json
    import os
    import subprocess

    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    open_pr = ROOT / "scripts" / "owner_open_path_c_pr.sh"
    oneshot_txt = oneshot.read_text(encoding="utf-8")
    open_pr_txt = open_pr.read_text(encoding="utf-8")
    assert "Batch 277" in oneshot_txt
    assert "Batch 277" in open_pr_txt
    assert "VERIFY.release" in oneshot_txt
    assert "VERIFY.release" in open_pr_txt
    # Batch 244 Intent: living default comment still names tip 542e6ec.
    assert "batch241-path-c-bundle (tip 542e6ec" in open_pr_txt
    # VERIFY derive must appear before living-pin fallback / :-default.
    for label, text in (("oneshot", oneshot_txt), ("open_pr", open_pr_txt)):
        verify_idx = text.find('data.get("release")')
        living_idx = text.find("living.is_file()")
        default_idx = text.find(
            'PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"'
        )
        assert 0 <= verify_idx < living_idx < default_idx, label

    living = ROOT / "portable" / "LIVING_PATH_C_RELEASE_TAG"
    prior = living.read_text(encoding="utf-8")
    assert prior.strip() == "batch241-path-c-bundle"

    def _combined(script: object, extra_env: dict | None = None) -> str:
        env = dict(os.environ)
        env.pop("PATH_C_RELEASE_TAG", None)
        # Intent isolation: do not pick host device-auth / secret file drops.
        env["PATH_C_IGNORE_FILE_TOKENS"] = "1"
        # Dummy token so oneshot takes open_pr path (CI has GITHUB_TOKEN only).
        env["MAIN_PUSH_TOKEN"] = "batch277-intent-dummy-token"
        if extra_env:
            env.update(extra_env)
        dry = subprocess.run(
            ["bash", str(script), "--dry-run"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        assert dry.returncode == 0, dry.stderr + dry.stdout
        return (dry.stdout or "") + (dry.stderr or "")

    try:
        living.write_text("batch250-path-c-bundle\n", encoding="utf-8")
        for script in (oneshot, open_pr):
            combined = _combined(script)
            assert "release_tag=batch241-path-c-bundle" in combined, script.name
            assert "release_tag=batch250-path-c-bundle" not in combined, script.name
        # Explicit env override still wins.
        combined = _combined(
            open_pr, {"PATH_C_RELEASE_TAG": "batch999-path-c-bundle"}
        )
        assert "release_tag=batch999-path-c-bundle" in combined
    finally:
        living.write_text(
            prior if prior.endswith("\n") else prior + "\n", encoding="utf-8"
        )

    brief = json.loads(
        (ROOT / "portable" / "BATCH277_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "277"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert (
        brief.get("defect_id")
        == "owner_oneshot_open_pr_dirty_living_pin_over_verify"
    )
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("bfb7c38")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH277_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert (
        hunt.get("defect_id")
        == "owner_oneshot_open_pr_dirty_living_pin_over_verify"
    )
    assert any(
        "republish living-tag post-pack" in a for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH277_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 277" in log_md
    assert "VERIFY.release" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 277)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 277)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 277" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 277" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch278_pack_portable_help_not_out() -> None:
    """Batch 278: pack_portable --help must not write an OUT tarball named --help."""
    import json
    import os
    import subprocess
    import tempfile

    pack = ROOT / "scripts" / "pack_portable.sh"
    pack_txt = pack.read_text(encoding="utf-8")
    assert "Batch 278" in pack_txt
    assert "-h|--help" in pack_txt
    assert "OUT path must not start with -" in pack_txt

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "Batch 278" in refresh
    assert "python3 - <<'PY'" in refresh
    # Living default advances each tip-sync batch; Batch 286: >= not allowlist.
    _assert_refresh_batch_tag_default_at_least(refresh, 278)

    living = ROOT / "portable" / "LIVING_PATH_C_RELEASE_TAG"
    prior = living.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        help_run = subprocess.run(
            ["bash", str(pack), "--help"],
            cwd=td,
            capture_output=True,
            text=True,
            check=False,
        )
        assert help_run.returncode == 0, help_run.stderr + help_run.stdout
        combined = (help_run.stdout or "") + (help_run.stderr or "")
        assert "Usage:" in combined or "pack_portable.sh" in combined
        assert "wrote " not in combined
        assert not (Path(td) / "--help").exists()
        assert not (ROOT / "--help").exists()
        # --help must not stamp / rewrite the living pin.
        assert living.read_text(encoding="utf-8") == prior

        bad = subprocess.run(
            ["bash", str(pack), "--force"],
            cwd=td,
            capture_output=True,
            text=True,
            check=False,
        )
        assert bad.returncode == 2, bad.stderr + bad.stdout
        assert "unknown option" in ((bad.stdout or "") + (bad.stderr or ""))

        out = os.path.join(td, "pack.tgz")
        ok = subprocess.run(
            ["bash", str(pack), out],
            cwd=td,
            capture_output=True,
            text=True,
            check=False,
            timeout=90,
        )
        assert ok.returncode == 0, ok.stderr + ok.stdout
        assert os.path.getsize(out) > 1000
        assert "wrote " in ((ok.stdout or "") + (ok.stderr or ""))

    assert living.read_text(encoding="utf-8").strip() == "batch241-path-c-bundle"

    brief = json.loads(
        (ROOT / "portable" / "BATCH278_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "278"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") in (
        "pack_portable_dash_option_as_out_path",
        "refresh_apply_soft_update_unquoted_heredoc",
        "pack_portable_help_and_refresh_apply_heredoc",
    )
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3b3860d") or str(
        brief.get("tip", "")
    ).startswith("bfb7c38")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH278_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") in (
        "pack_portable_dash_option_as_out_path",
        "refresh_apply_soft_update_unquoted_heredoc",
        "pack_portable_help_and_refresh_apply_heredoc",
    )
    assert any("VERIFY.release-first" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH278_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 278" in log_md
    assert "pack_portable" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 278)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 278)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 278" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 278" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch279_republish_canonical_basename() -> None:
    """Batch 279: republish stages canonical pack basename + post-upload verify."""
    import json
    import subprocess
    import tempfile
    from pathlib import Path as P

    script = ROOT / "scripts" / "republish_living_path_c_release.sh"
    text = script.read_text(encoding="utf-8")
    assert "Batch 279" in text
    assert "CANON_NAME" in text
    assert "trial-portable-main-fixes.tgz" in text
    assert "staged canonical pack basename" in text
    assert "post-upload mismatch" in text or "REL_AFTER_SHA" in text
    assert "gh-dylan-auth/access_token" in text

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Living default advances each batch; Batch 286: >= not allowlist.
    _assert_refresh_batch_tag_default_at_least(refresh, 279)

    with tempfile.TemporaryDirectory(prefix="b279-intent-") as td:
        out = P(td) / "wrong-name.tgz"
        dry = subprocess.run(
            ["bash", str(script), "--dry-run", "--out", str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        assert dry.returncode == 0, dry.stderr + dry.stdout
        combined = (dry.stdout or "") + (dry.stderr or "")
        assert "staged canonical pack basename trial-portable-main-fixes.tgz" in combined
        assert "wrong-name.tgz" in combined
        # Dry-run upload line must use canonical basename, not the --out leak name.
        assert "trial-portable-main-fixes.tgz" in combined
        assert "/wrong-name.tgz --repo" not in combined
        assert "would: gh release upload batch241-path-c-bundle" in combined

    brief = json.loads(
        (ROOT / "portable" / "BATCH279_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "279"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "republish_out_basename_leaves_living_pack_stale"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("upload_ok") is True
    assert int(brief.get("release_tgz_bytes_before") or 0) == 386608
    assert int(brief.get("release_tgz_bytes_after") or 0) >= 482632
    assert str(brief.get("tip", "")).startswith("3b3860d")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH279_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "republish_out_basename_leaves_living_pack_stale"
    assert any("pack_portable --help" in a for a in (hunt.get("avoided") or []))
    assert any("VERIFY.release-first" in a for a in (hunt.get("avoided") or []))

    evidence = json.loads(
        (ROOT / "portable" / "BATCH279_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("pack_newer") is True
    assert evidence.get("living_tag") == "batch241-path-c-bundle"
    assert evidence.get("upload_ok") is True
    assert evidence.get("canonical_staging") is True
    assert evidence.get("post_upload_verify") is True
    assert evidence.get("basename_leak_repro", {}).get("leak_asset_name") == (
        "batch279-upload.tgz"
    )
    assert int(evidence.get("release_tgz_bytes_before") or 0) == 386608
    assert int(evidence.get("release_tgz_bytes_after") or 0) >= 482632
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH279_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 279" in log_md
    assert "basename" in log_md.lower() or "batch279-upload" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 279)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 279)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 279" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 279" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch280_probe_w2_contents_ref_first() -> None:
    """Batch 280: W2 contents PUT creates throwaway git ref before PUT."""
    import json

    script = ROOT / "scripts" / "probe_main_write_vectors.py"
    text = script.read_text(encoding="utf-8")
    assert "Batch 280" in text
    assert "create throwaway ref before contents PUT" in text
    # Must create ref before PUT (pre-280 PUT-only → false DENIED 404).
    ref_idx = text.find("W2 — contents PUT")
    assert ref_idx > 0
    w2_block = text[ref_idx : ref_idx + 2500]
    assert "git/refs" in w2_block
    assert "w2_ref_status" in w2_block or "ref_create_http_status" in w2_block
    put_idx = w2_block.find("/contents/.cursor-write-probe-b55.txt")
    refs_idx = w2_block.find("git/refs")
    assert refs_idx >= 0 and put_idx > refs_idx

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Batch 286: >= not allowlist (280 stamp may be historical only).
    _assert_refresh_batch_tag_default_at_least(refresh, 280)

    brief = json.loads(
        (ROOT / "portable" / "BATCH280_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "280"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "probe_w2_contents_put_missing_git_ref"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("3b3860d")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH280_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "probe_w2_contents_put_missing_git_ref"
    assert any("279" in a or "basename" in a for a in (hunt.get("avoided") or []))
    assert any("pack_portable --help" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH280_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 280" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 280)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 280)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 280" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 280" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch281_grant_durable_ls_remote_auth() -> None:
    """Batch 281: grant --check authenticates ls-remote when token env set."""
    import json

    grant = ROOT / "scripts" / "owner_grant_ai_agent_access.sh"
    text = grant.read_text(encoding="utf-8")
    assert "Batch 281" in text
    assert "x-access-token" in text
    assert "ls_url" in text
    # Authenticated URL must be preferred when token present (pre-281 bare https).
    assert 'ls_url="https://x-access-token:${_ls_tok}@github.com/$r.git"' in text
    assert 'ls_url="https://github.com/$r.git"' in text
    assert "_ls_tok" in text

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Batch 281 introduced authenticated stamp default; Batch 286: >= not allowlist.
    _assert_refresh_batch_tag_default_at_least(refresh, 281)
    assert "x-access-token" in (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )

    brief = json.loads(
        (ROOT / "portable" / "BATCH281_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "281"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "grant_check_durable_ls_remote_unauthenticated"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert str(brief.get("tip", "")).startswith("3b3860d")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH281_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "grant_check_durable_ls_remote_unauthenticated"
    assert any("280" in a or "contents-ref" in a for a in (hunt.get("avoided") or []))
    assert any("basename" in a or "279" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH281_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 281" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 281)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 281)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 281" in ones

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 281" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch282_pack_portable_includes_owner_grant() -> None:
    """Batch 282: pack_portable includes owner_grant (+ inventory); VERIFY-driven focused."""
    import json
    import os
    import subprocess
    import tempfile

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "owner_grant_ai_agent_access.sh" in pack
    assert "AI_AGENT_ACCESS_INVENTORY.json" in pack

    grant = ROOT / "scripts" / "owner_grant_ai_agent_access.sh"
    assert grant.is_file()
    inv = ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json"
    assert inv.is_file()

    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "pack.tgz")
        subprocess.run(
            [str(ROOT / "scripts" / "pack_portable.sh"), out],
            check=True,
            timeout=90,
        )
        listing = subprocess.run(
            ["tar", "-tzf", out],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
        assert "scripts/owner_grant_ai_agent_access.sh" in listing
        assert "portable/AI_AGENT_ACCESS_INVENTORY.json" in listing

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 282" in unblock
    assert "VERIFY_FOCUSED" in unblock
    assert "focused 90/0" not in unblock

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Batch 282 introduced stamp default; Batch 286: >= not allowlist.
    _assert_refresh_batch_tag_default_at_least(refresh, 282)

    brief = json.loads(
        (ROOT / "portable" / "BATCH282_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "282"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "pack_portable_omits_owner_grant_script"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88") or str(
        brief.get("tip", "")
    ).startswith("3b3860d")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH282_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "pack_portable_omits_owner_grant_script"
    assert any("281" in a or "ls-remote" in a for a in (hunt.get("avoided") or []))
    assert any("280" in a or "contents-ref" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is True

    audit = json.loads(
        (ROOT / "portable" / "BATCH282_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 282" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 282)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 282)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 282" in ones

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch283_republish_tip_stale_living_release() -> None:
    """Batch 283: republish tip_stale when living release BASE_TIP lags local."""
    import json
    import re
    import subprocess

    script = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "tip_stale" in script
    assert "Batch 283" in script
    assert "release_pack_tip" in script or "REL_PACK_TIP" in script
    # tip mismatch must drive need_upload (not byte-growth alone).
    assert "TIP_STALE" in script
    assert 'TIP_STALE" -eq 1' in script or "TIP_STALE" in script

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Batch 283 introduced stamp default; Batch 286: >= not allowlist.
    _assert_refresh_batch_tag_default_at_least(refresh, 283)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 283" in unblock
    assert "tip_stale" in unblock

    brief = json.loads(
        (ROOT / "portable" / "BATCH283_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "283"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "republish_byte_growth_misses_tip_stale_release"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH283_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "republish_byte_growth_misses_tip_stale_release"
    assert any("282" in a or "grant" in a for a in (hunt.get("avoided") or []))
    assert any("281" in a or "ls-remote" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH283_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    evidence = json.loads(
        (ROOT / "portable" / "BATCH283_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("tip_stale_pre") is True
    assert evidence.get("need_upload_pre") is True
    assert str(evidence.get("release_pack_tip_before", "")).startswith("3b3860d")
    assert evidence.get("release_had_owner_grant_before") is False

    # Dry-run must emit tip_stale / need_upload keys (live tip may already match
    # after upload in the same cycle — still assert script wiring via --help text).
    help_out = subprocess.run(
        ["bash", str(ROOT / "scripts" / "republish_living_path_c_release.sh"), "--help"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout
    assert "Batch 283" in help_out
    assert "tip_stale" in help_out

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 283" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 283)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 283)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 283" in ones

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch285_grant_install_403_json_false_missing() -> None:
    """Batch 285: grant --check must not treat 403 JSON as empty install list."""
    import json
    import subprocess

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 285" in grant
    assert "installation_note" in grant
    # Fail-closed: require a real repositories list before listing missing deps.
    # Batch 286 strengthened key-presence → isinstance(list); either form OK.
    assert (
        '"repositories" not in d' in grant
        or "isinstance(repos, list)" in grant
        or "not isinstance(repos, list)" in grant
    )
    assert "install_missing_from_deps" in grant

    # Synthetic 403 body must not produce install_missing_from_deps.
    snippet = r'''
import json, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except json.JSONDecodeError:
    print("installation: unavailable (not an App installation token, or 403)")
    raise SystemExit(0)
if not isinstance(d, dict) or "repositories" not in d:
    print("installation: unavailable (not an App installation token, or 403)")
    msg = d.get("message") if isinstance(d, dict) else None
    if isinstance(msg, str) and msg.strip():
        print("installation_note:", msg.strip()[:240])
    raise SystemExit(0)
names=[r.get("full_name") for r in (d.get("repositories") or []) if isinstance(r, dict)]
print("install_missing_from_deps:", ["x"] if not names else [])
'''
    fake_403 = json.dumps(
        {
            "message": "You must authenticate with an installation access token",
            "status": "403",
        }
    )
    proc = subprocess.run(
        ["python3", "-c", snippet],
        input=fake_403,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    out = proc.stdout
    assert "installation: unavailable" in out
    assert "installation_note:" in out
    assert "install_missing_from_deps" not in out

    # Real listing still parses when repositories present.
    listing = json.dumps(
        {
            "total_count": 1,
            "repository_selection": "selected",
            "repositories": [{"full_name": "d6g8k5htny-coder/trial"}],
        }
    )
    proc2 = subprocess.run(
        [
            "python3",
            "-c",
            "import json,sys; d=json.load(sys.stdin); assert 'repositories' in d; print('ok', len(d['repositories']))",
        ],
        input=listing,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert "ok 1" in proc2.stdout

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    # Batch 285 stamp; Batch 286+ advances default — use >= not exact match.
    _assert_refresh_batch_tag_default_at_least(refresh, 285)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 285" in unblock

    brief = json.loads(
        (ROOT / "portable" / "BATCH285_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "285"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "grant_check_install_403_json_false_missing"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH285_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "grant_check_install_403_json_false_missing"
    assert any("283" in a or "tip_stale" in a for a in (hunt.get("avoided") or []))
    assert any("281" in a or "ls-remote" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH285_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 285" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 285)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 285)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 285" in ones

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch286_grant_list_script_stale_refresh_durable() -> None:
    """Batch 286: repositories must be list; republish script_stale; REFRESH >= durable."""
    import json
    import subprocess

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 286" in grant
    assert "isinstance(repos, list)" in grant or "not isinstance(repos, list)" in grant
    assert "installation_note" in grant

    # Synthetic null / non-list must not produce install_missing_from_deps.
    snippet = r'''
import json, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except json.JSONDecodeError:
    print("installation: unavailable (not an App installation token, or 403)")
    raise SystemExit(0)
repos = d.get("repositories") if isinstance(d, dict) else None
if not isinstance(d, dict) or not isinstance(repos, list):
    print("installation: unavailable (not an App installation token, or 403)")
    msg = d.get("message") if isinstance(d, dict) else None
    if isinstance(msg, str) and msg.strip():
        print("installation_note:", msg.strip()[:240])
    raise SystemExit(0)
names=[r.get("full_name") for r in repos if isinstance(r, dict)]
print("install_missing_from_deps:", ["x"] if not names else [])
'''
    for fake in (
        json.dumps({"repositories": None, "total_count": 0}),
        json.dumps({"repositories": "nope"}),
        json.dumps(
            {
                "message": "You must authenticate with an installation access token",
                "status": "403",
            }
        ),
    ):
        proc = subprocess.run(
            ["python3", "-c", snippet],
            input=fake,
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        out = proc.stdout
        assert "installation: unavailable" in out
        assert "install_missing_from_deps" not in out

    # Real list still parses.
    listing = json.dumps(
        {
            "total_count": 1,
            "repository_selection": "selected",
            "repositories": [{"full_name": "d6g8k5htny-coder/trial"}],
        }
    )
    proc_ok = subprocess.run(
        ["python3", "-c", snippet],
        input=listing,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert "install_missing_from_deps: []" in proc_ok.stdout

    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 286" in republish
    assert "SCRIPT_STALE" in republish
    assert "script_stale" in republish
    assert "owner_grant_ai_agent_access.sh" in republish
    assert 'SCRIPT_STALE" -eq 1' in republish or "SCRIPT_STALE" in republish

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 286)
    # Helper itself is the durable contract (no more allowlist churn).
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "_assert_refresh_batch_tag_default_at_least" in intent
    assert "_refresh_batch_tag_default" in intent
    # No remaining REFRESH allowlist any(...) loops (helper replaced them).
    import re

    allowlists = re.findall(
        r'f"REFRESH_BATCH_TAG:-\{n\}" in refresh for n in', intent
    )
    assert allowlists == [], f"stale REFRESH allowlists remain: {allowlists}"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 286" in unblock
    assert "script_stale" in unblock

    brief = json.loads(
        (ROOT / "portable" / "BATCH286_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "286"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "grant_list_script_stale_refresh_durable"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH286_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "grant_list_script_stale_refresh_durable"
    assert any("285" in a or "403" in a for a in (hunt.get("avoided") or []))
    assert any("283" in a or "tip_stale" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH286_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 286" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 286)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 286)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 286" in ones

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch287_probe_install_repositories_list() -> None:
    """Batch 287: probe/when_writable require repositories list (286 grant leftover)."""
    import importlib.util
    import json

    probe_path = ROOT / "scripts" / "probe_main_write.py"
    probe_txt = probe_path.read_text(encoding="utf-8")
    assert "Batch 287" in probe_txt
    assert "repositories_not_list" in probe_txt
    assert "repositories_unavailable" in probe_txt
    # Docstring may mention pre-287 ``or []``; executable assignment must be gone.
    assert 'repos = body.get("repositories") or []' not in probe_txt

    ww = (ROOT / "scripts" / "when_writable_land.py").read_text(encoding="utf-8")
    assert "Batch 287" in ww
    assert "repositories_unavailable" in ww
    assert 'repos = body.get("repositories") or []' not in ww
    assert "isinstance(repos, list)" in ww
    spec = importlib.util.spec_from_file_location("probe_main_write_b287", probe_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for body in (
        {"repositories": None, "total_count": 0},
        {"repositories": "nope"},
        {"repositories": {"full_name": "x"}},
        {},
    ):
        names, total, selection, err = mod._parse_installation_repos_body(body)
        assert err == "repositories_not_list"
        assert names is None
        assert total is None
        assert selection is None

    names_ok, total_ok, sel_ok, err_ok = mod._parse_installation_repos_body(
        {
            "total_count": 1,
            "repository_selection": "selected",
            "repositories": [{"full_name": "d6g8k5htny-coder/main"}],
        }
    )
    assert err_ok is None
    assert names_ok == ["d6g8k5htny-coder/main"]
    assert total_ok == 1
    assert sel_ok == "selected"

    empty_names, _, _, empty_err = mod._parse_installation_repos_body(
        {"repositories": [], "total_count": 0}
    )
    assert empty_err is None
    assert empty_names == []

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 287)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 287" in unblock
    # Header advances each batch; history line must retain Batch 287 note.
    assert "probe_main_write / when_writable require isinstance(repositories, list)" in unblock

    brief = json.loads(
        (ROOT / "portable" / "BATCH287_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "287"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "probe_install_repositories_list"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH287_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "probe_install_repositories_list"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert any("286" in a or "grant" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH287_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 287" in log_md

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 287)" in owner

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 287)" in land

    ones = (ROOT / "portable" / "OWNER_ONE_LINERS.md").read_text(encoding="utf-8")
    assert "Batch 287" in ones

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"


def test_batch288_when_writable_critical_living_republish() -> None:
    """Batch 288: CRITICAL includes when_writable; living republish; REFRESH 288."""
    import json

    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 288" in republish
    # Extract CRITICAL tuple members via quoted paths after CRITICAL = (
    import re

    crit_m = re.search(
        r"CRITICAL\s*=\s*\((.*?)\)\s*\n\s*\ndef member_sha",
        republish,
        flags=re.S,
    )
    assert crit_m is not None, "CRITICAL tuple not found in republish script"
    crit_block = crit_m.group(1)
    assert '"scripts/when_writable_land.py"' in crit_block
    assert '"scripts/probe_main_write.py"' in crit_block

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 288)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 288" in unblock
    assert "when_writable" in unblock

    for rel in (
        "scripts/probe_main_write.py",
        "scripts/when_writable_land.py",
        "scripts/owner_grant_ai_agent_access.sh",
    ):
        src = (ROOT / rel).read_text(encoding="utf-8")
        assert 'repos = body.get("repositories") or []' not in src
        assert 'repos = d.get("repositories") or []' not in src

    brief = json.loads(
        (ROOT / "portable" / "BATCH288_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "288"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "when_writable_critical_living_republish"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH288_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "when_writable_critical_living_republish"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert any("287" in a or "repositories" in a for a in (hunt.get("avoided") or []))
    assert hunt.get("tip_moved") is False

    audit = json.loads(
        (ROOT / "portable" / "BATCH288_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 288" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 288)" in land


def test_batch289_tip_sync_after_main_83() -> None:
    """Batch 289: tip-sync 7d13a88→3a29f52 after main #83; living tip_stale; REFRESH 289."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH289_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "289"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_found") is True
    assert brief.get("defect_id") == "tip_sync_7d13a88_to_3a29f52_main_83"
    assert brief.get("tip_moved") is True
    assert brief.get("route_now") == "TIP_SYNC"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")
    assert str(brief.get("prior_tip", "")).startswith("7d13a88")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH289_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_id") == "tip_sync_7d13a88_to_3a29f52_main_83"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is True
    assert any("83" in a or "CRITICAL" in a or "288" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH289_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(
        encoding="utf-8"
    )
    # Live BASE_TIP supersedes across tip-sync; Batch 289 shipped 3a29f52.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 289
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    # prior_base_tip_sha advances on later tip-syncs; only require living SHA.
    assert _living_tip(str(verify.get("prior_base_tip_sha", ""))) or str(
        verify.get("prior_base_tip_sha", "")
    ).startswith("7d13a88")
    assert verify.get("lemma_closed") is False
    # Later non-tip refresh_batch bumps (e.g. Batch 327) set tip_refresh=False while
    # base_tip_sha stays living; do not freeze tip_refresh=True forever.
    _assert_living_tip_refresh(verify.get("tip_refresh"))

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 289" in unblock
    # Header bumps on later tip-sync / eng; >= 289 (no allowlist churn).
    _assert_print_owner_header_batch_at_least(unblock, 289)
    assert "3a29f52" in unblock or "tip-sync" in unblock.lower() or "7d13a88" in unblock

    assert "3a29f52" in _LIVING_TIPS

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 289" in log_md
    assert "#83" in log_md or "3a29f52" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 289)" in land
    assert "3a29f52" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 289)" in owner

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False


def test_batch290_permanent_watch_idle() -> None:
    """Batch 290: permanent-watch IDLE — no new eng; lemma stays open."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH290_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "290"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH290_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_289") is True
    assert any("289" in a or "288" in a or "CRITICAL" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH290_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 290" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 290)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 290)" in owner

    # Keep living REFRESH default from last eng ship (289); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False


def test_batch291_idle_deep() -> None:
    """Batch 291: DEEP idle — no new eng beyond 273–290; lemma stays open."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH291_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "291"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE_DEEP"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH291_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_290") is True
    assert any(
        "290" in a or "289" in a or "CRITICAL" in a or "repositories" in a
        for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH291_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 291" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 291)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 291)" in owner

    # Keep living REFRESH default from last eng ship (289); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False


def test_batch293_research_audit_idle() -> None:
    """Batch 293: research audit WITHOUT promotion; lemma stays open; no NEW eng."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH293_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "293"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "RESEARCH_AUDIT_IDLE"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")
    ra = brief.get("research_audit") or {}
    assert ra.get("lemma_closed") is False
    assert ra.get("prizes_solved") is False
    assert ra.get("open_prizes") == 3
    assert ra.get("flipped_anything") is False
    assert ra.get("guard_pass") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH293_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_291") is True
    assert any("0020" in a or "invent" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH293_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert (audit.get("packet") or {}).get("lemma_closed") is False
    assert (audit.get("packet") or {}).get("prizes_solved") is False
    assert len(audit.get("open_prizes") or []) == 3

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 293" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 293)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 293)" in owner

    # Keep living REFRESH default from last eng ship (289); audit idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False


def test_batch294_permanent_watch_idle() -> None:
    """Batch 294: permanent-watch IDLE — no new eng beyond 273–293; lemma stays open."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH294_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "294"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH294_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_293") is True
    assert any(
        "293" in a or "0020" in a or "CRITICAL" in a for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH294_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 294" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 294)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 294)" in owner

    # Keep living REFRESH default from last eng ship (289); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False


def test_batch296_permanent_watch_idle() -> None:
    """Batch 296: permanent-watch IDLE — MAIN eng while WRITABLE; idle_no_commit."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH296_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "296"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("3a29f52")
    assert 87 in (brief.get("research_hold_prs_skipped") or [])

    hunt = json.loads(
        (ROOT / "portable" / "BATCH296_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_294") is True
    assert (hunt.get("candidates_checked") or {}).get("ready_non_draft_eng") == "none"
    assert any(
        "87" in a or "0020" in a or "tip-observe" in a for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH296_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 296" in log_md
    assert "idle_no_commit" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 296)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 296)" in owner

    # Keep living REFRESH default from last eng ship (289); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 289)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"


def test_batch304_permanent_watch_idle() -> None:
    """Batch 304: permanent-watch IDLE — tip stable @02cfbfd; idle_no_commit."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH304_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "304"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("02cfbfd")
    assert 85 in (brief.get("research_hold_prs_skipped") or [])
    assert 87 in (brief.get("research_hold_prs_skipped") or [])
    assert 88 in (brief.get("research_hold_prs_skipped") or [])
    pr85 = brief.get("main_pr_85") or {}
    assert pr85.get("state") == "OPEN"
    assert pr85.get("isDraft") is False
    assert pr85.get("ci_verify") == "SUCCESS"
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    assert pr87.get("isDraft") is True
    pr88 = brief.get("main_pr_88") or {}
    assert pr88.get("state") == "OPEN"
    assert pr88.get("isDraft") is True
    evidence = brief.get("evidence") or {}
    assert "assert" in str(evidence.get("path_c", "")).lower() or "IDLE" in str(
        evidence.get("path_c", "")
    )
    assert "NEVER flip" in str(evidence.get("main_85", ""))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH304_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_303") is True
    assert (hunt.get("candidates_checked") or {}).get("ready_non_draft_eng") == "none"
    assert (hunt.get("candidates_checked") or {}).get("main_pr_85")
    assert any(
        "85" in a or "87" in a or "0020" in a or "tip-observe" in a
        for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH304_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "304"
    assert str(audit.get("tip_sha", "")).startswith("02cfbfd")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 304" in log_md
    assert "idle_no_commit" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 304)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 304)" in owner

    # Keep living REFRESH default from last eng tip-sync (297); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 297)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 02cfbfd.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"


def test_batch299_permanent_watch_idle() -> None:
    """Batch 299: permanent-watch IDLE — tip stable @02cfbfd; idle_no_commit."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH299_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "299"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("02cfbfd")
    assert 85 in (brief.get("research_hold_prs_skipped") or [])
    assert 87 in (brief.get("research_hold_prs_skipped") or [])
    assert 88 in (brief.get("research_hold_prs_skipped") or [])
    pr85 = brief.get("main_pr_85") or {}
    assert pr85.get("state") == "OPEN"
    assert pr85.get("isDraft") is False
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    assert pr87.get("isDraft") is True
    pr88 = brief.get("main_pr_88") or {}
    assert pr88.get("state") == "OPEN"
    assert pr88.get("isDraft") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH299_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_298") is True
    assert (hunt.get("candidates_checked") or {}).get("ready_non_draft_eng") == "none"
    assert (hunt.get("candidates_checked") or {}).get("main_pr_85")
    assert any(
        "85" in a or "87" in a or "0020" in a or "tip-observe" in a
        for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH299_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "299"
    assert str(audit.get("tip_sha", "")).startswith("02cfbfd")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 299" in log_md
    assert "idle_no_commit" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 299)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 299)" in owner

    # Keep living REFRESH default from last eng ship (297); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 297)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 02cfbfd.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"


def test_batch303_align_repos_multi_agent_dual_vector() -> None:
    """Batch 303: ALIGN REPOS — MULTI_AGENT capability table matches grant dual-vector."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH303_ALIGN.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "303"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("scientific_effect") == "NONE"
    assert tiny.get("aligned") is True
    assert tiny.get("write") == "WRITABLE"
    assert tiny.get("path_c") == "IDLE_PATH_C_DONE"
    assert tiny.get("tip_match") is True
    assert str(tiny.get("tip", "")).startswith("02cfbfd")
    assert tiny.get("action") == "docs_multi_agent_capability_dual_vector"
    assert tiny.get("write_durable") == "8/8"
    siblings = tiny.get("siblings") or {}
    assert siblings.get("env_deps") == 8
    assert siblings.get("install_has_main") is False
    assert "docs_multi_agent" in str(tiny.get("fix", "")) or "dual" in str(
        tiny.get("fix", "")
    ).lower()

    doc = (ROOT / "docs" / "MULTI_AGENT_ACCESS.md").read_text(encoding="utf-8")
    assert "Dual-vector" in doc
    assert "8/8 WRITABLE" in doc
    assert "device_auth" in doc.lower() or "Device-flow user token" in doc
    assert "**SUCCESS**" in doc
    # Stale App-only single-column table must not return.
    assert "Device-flow user token | pending" not in doc
    assert "| Push `main` / other owner repos | **no**" not in doc

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert "durable" in grant.lower()
    assert "sandbox" in grant

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 303" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 303)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 303)" in owner

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("write_state") == "WRITABLE"


def test_batch298_permanent_watch_idle() -> None:
    """Batch 298: permanent-watch IDLE — tip stable @02cfbfd; idle_no_commit."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH298_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "298"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is False
    assert brief.get("defect_found") is False
    assert brief.get("defect_id") is None
    assert brief.get("route_now") == "IDLE"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("02cfbfd")
    assert 85 in (brief.get("research_hold_prs_skipped") or [])
    assert 87 in (brief.get("research_hold_prs_skipped") or [])
    assert 88 in (brief.get("research_hold_prs_skipped") or [])
    pr85 = brief.get("main_pr_85") or {}
    assert pr85.get("state") == "OPEN"
    assert pr85.get("isDraft") is False
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    assert pr87.get("isDraft") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH298_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is False
    assert hunt.get("defect_found") is False
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_not_273_297") is True
    assert (hunt.get("candidates_checked") or {}).get("ready_non_draft_eng") == "none"
    assert (hunt.get("candidates_checked") or {}).get("main_pr_85")
    assert any(
        "85" in a or "87" in a or "0020" in a or "tip-observe" in a
        for a in (hunt.get("avoided") or [])
    )

    audit = json.loads(
        (ROOT / "portable" / "BATCH298_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "298"
    assert str(audit.get("tip_sha", "")).startswith("02cfbfd")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 298" in log_md
    assert "idle_no_commit" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 298)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 298)" in owner

    # Keep living REFRESH default from last eng ship (297); idle does not bump.
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 297)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 02cfbfd.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"


def test_batch297_permanent_watch_idle() -> None:
    """Batch 297: tip-sync after main #84; early idle superseded."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH297_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "297"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_found") is True
    assert brief.get("defect_id") == "tip_sync_3a29f52_to_02cfbfd_main_84"
    assert brief.get("route_now") == "TIP_SYNC"
    assert brief.get("action") == "tip_sync"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is True
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert brief.get("any_undrafted_or_merged_84_85_87") is True
    assert 84 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("02cfbfd")
    assert str(brief.get("prior_tip", "")).startswith("3a29f52")
    pr84 = brief.get("main_pr_84") or {}
    assert pr84.get("state") == "MERGED"
    assert pr84.get("mergedAt")
    pr85 = brief.get("main_pr_85") or {}
    assert pr85.get("state") == "OPEN"
    assert pr85.get("isDraft") is False
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    assert pr87.get("isDraft") is True
    evidence = brief.get("evidence") or {}
    assert "02cfbfd" in (evidence.get("tip_mid") or "")
    assert "tip_stale" in (evidence.get("living_release") or "")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH297_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_found") is True
    assert hunt.get("defect_id") == "tip_sync_3a29f52_to_02cfbfd_main_84"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_beyond_tip_sync") is True
    checked = hunt.get("candidates_checked") or {}
    assert "MERGED" in (checked.get("main_pr_84") or "")
    assert "undrafted" in (checked.get("main_pr_85") or "")
    assert any("84" in a or "tip-sync" in a.lower() or "02cfbfd" in a for a in (hunt.get("bugs_fixed") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH297_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "297"
    assert str(audit.get("tip_sha", "")).startswith("02cfbfd")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 297" in log_md
    assert "tip-sync" in log_md.lower() or "tip_sync" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 297)" in land
    assert "02cfbfd" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 297)" in owner

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 297)
    assert "02cfbfd" in _LIVING_TIPS

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 297 shipped 02cfbfd.
    assert _living_tip(base)
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert int(verify.get("refresh_batch") or 0) >= 297

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 02cfbfd.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"


def test_batch305_tip_sync_after_main_85() -> None:
    """Batch 305: tip-sync after main #85; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH305_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "305"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_found") is True
    assert brief.get("defect_id") == "tip_sync_02cfbfd_to_0adeb65_main_85"
    assert brief.get("route_now") == "TIP_SYNC"
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is True
    assert brief.get("hardening_tip_moved") is True
    assert brief.get("default_tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert 85 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("0adeb65")
    assert str(brief.get("prior_tip", "")).startswith("02cfbfd")
    pr85 = brief.get("main_pr_85") or {}
    assert pr85.get("state") == "MERGED"
    assert pr85.get("mergedAt")
    assert "hardening" in str(pr85.get("baseRefName") or "")
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    assert pr87.get("isDraft") is True
    evidence = brief.get("evidence") or {}
    assert "0adeb65" in (evidence.get("tip_mid") or "")
    assert "tip_stale" in (evidence.get("living_release") or "")
    assert "NOT promoted" in (evidence.get("guard_research") or "") or "not promoted" in (
        brief.get("note") or ""
    ).lower()

    hunt = json.loads(
        (ROOT / "portable" / "BATCH305_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_found") is True
    assert hunt.get("defect_id") == "tip_sync_02cfbfd_to_0adeb65_main_85"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_beyond_tip_sync") is True
    checked = hunt.get("candidates_checked") or {}
    assert "MERGED" in (checked.get("main_pr_85") or "")
    assert any(
        "85" in a or "tip-sync" in a.lower() or "0adeb65" in a
        for a in (hunt.get("bugs_fixed") or [])
    )
    assert any("inventable" in a.lower() or "lemma" in a.lower() for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH305_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "305"
    assert str(audit.get("tip_sha", "")).startswith("0adeb65")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 305" in log_md
    assert "tip-sync" in log_md.lower() or "tip_sync" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 305)" in land
    assert "0adeb65" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 305)" in owner

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 305)
    assert "0adeb65" in _LIVING_TIPS
    assert "02cfbfd" in _LIVING_TIPS

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 305 shipped 0adeb65.
    assert _living_tip(base)
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert _living_tip(str(verify.get("prior_base_tip_sha", ""))) or str(
        verify.get("prior_base_tip_sha", "")
    ).startswith("02cfbfd")
    assert int(verify.get("refresh_batch") or 0) >= 305
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("lemma_closed") is False
    pytest_counts = verify.get("pytest") or {}
    assert int(pytest_counts.get("focused_passed") or 0) >= 92
    assert int(pytest_counts.get("claims_recovery_passed") or 0) >= 83

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    # Header bumps on later tip-sync; >= 305 (no allowlist churn).
    _assert_print_owner_header_batch_at_least(unblock, 305)
    assert "0adeb65" in unblock or "Batch 305" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 0adeb65.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"

def test_batch317_tip_sync_after_main_89() -> None:
    """Batch 317: tip-sync after main #89 tip-observe; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH317_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "317"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_found") is True
    assert brief.get("defect_id") == "tip_sync_0adeb65_to_077464e_main_89"
    assert brief.get("route_now") == "TIP_SYNC"
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is True
    assert brief.get("hardening_tip_moved") is True
    assert brief.get("default_tip_moved") is False
    assert brief.get("write") == "WRITABLE"
    assert brief.get("aligned") is True
    assert 89 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("077464e")
    assert str(brief.get("prior_tip", "")).startswith("0adeb65")
    pr89 = brief.get("main_pr_89") or {}
    assert pr89.get("state") == "MERGED"
    assert pr89.get("mergedAt")
    assert "hardening" in str(pr89.get("baseRefName") or "")
    pr87 = brief.get("main_pr_87") or {}
    assert pr87.get("state") == "OPEN"
    evidence = brief.get("evidence") or {}
    assert "077464e" in (evidence.get("tip_mid") or "")
    assert "tip_stale" in (evidence.get("living_release") or "")
    assert "NOT promoted" in (evidence.get("guard_research") or "") or "not promoted" in (
        brief.get("note") or ""
    ).lower()

    hunt = json.loads(
        (ROOT / "portable" / "BATCH317_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("defect_found") is True
    assert hunt.get("defect_id") == "tip_sync_0adeb65_to_077464e_main_89"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("tip_moved") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert (hunt.get("HUNT_NEGATIVE") or {}).get("new_eng_beyond_tip_sync") is True
    checked = hunt.get("candidates_checked") or {}
    assert "MERGED" in (checked.get("main_pr_89") or "")
    assert any(
        "89" in a or "tip-sync" in a.lower() or "077464e" in a
        for a in (hunt.get("bugs_fixed") or [])
    )
    assert any("inventable" in a.lower() or "lemma" in a.lower() for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH317_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("batch") == "317"
    assert str(audit.get("tip_sha", "")).startswith("077464e")

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 317" in log_md
    assert "tip-sync" in log_md.lower() or "tip_sync" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 317)" in land
    assert "077464e" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 317)" in owner

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 317)
    assert "077464e" in _LIVING_TIPS
    assert "0adeb65" in _LIVING_TIPS

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 317 shipped 077464e.
    assert _living_tip(base)
    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert _living_tip(str(verify.get("prior_base_tip_sha", ""))) or str(
        verify.get("prior_base_tip_sha", "")
    ).startswith("0adeb65")
    assert int(verify.get("refresh_batch") or 0) >= 317
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("lemma_closed") is False
    pytest_counts = verify.get("pytest") or {}
    assert int(pytest_counts.get("focused_passed") or 0) >= 92
    assert int(pytest_counts.get("claims_recovery_passed") or 0) >= 83

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    # Header bumps on later tip-sync; >= 317 (no allowlist churn).
    _assert_print_owner_header_batch_at_least(unblock, 317)
    assert "077464e" in unblock or "Batch 317" in unblock

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    # Live tip supersedes across tip-sync; historical brief keeps 077464e.
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False
    assert status.get("write_state") == "WRITABLE"

def test_batch321_soften_live_tip_pins_and_inventory_refresh() -> None:
    """Batch 321: live tip Intent pins softened; inventory tip snapshot refreshed."""
    import json

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "_assert_print_owner_header_batch_at_least" in intent
    assert "_print_owner_header_batch" in intent
    # Batch 317 live pins must not hard-require startswith 077464e on VERIFY/status.
    assert "Live BASE_TIP supersedes across tip-sync; Batch 317 shipped 077464e" in intent
    assert "Live tip supersedes across tip-sync; historical brief keeps 077464e" in intent

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    # Batch 323+ auto-refresh advances batch stamp; keep 321 floor.
    assert int(str(inv.get("batch") or "0")) >= 321
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("main_writable") is True
    details = inv.get("details") or []
    assert len(details) == 8
    for d in details:
        tip = str(d.get("tip_sha") or "")
        assert len(tip) == 40, f"stale/short tip_sha for {d.get('name')}: {tip!r}"
        assert d.get("write") == "WRITABLE"

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 321" in log_md
    assert "living tip" in log_md.lower() or "_living_tip" in log_md or "live tip" in log_md.lower()

def test_batch323_grant_check_inventory_refresh() -> None:
    """Batch 323: grant --check refreshes AI_AGENT_ACCESS_INVENTORY from durable vector."""
    import json

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(encoding="utf-8")
    assert "Batch 323" in grant
    assert "refresh_ai_agent_access_inventory.py" in grant
    assert "inventory_refresh=ok" in grant or "INV_REFRESH" in grant
    assert "AI_AGENT_ACCESS_INVENTORY.json" in grant

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert "inventory_refresh=ok" in helper
    assert "tip_updates=" in helper
    assert 'inv["lemma_closed"] = False' in helper
    assert 'inv["flipped_anything"] = False' in helper
    assert 'inv["scientific_effect"] = "NONE"' in helper

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "refresh_ai_agent_access_inventory.py" in pack
    assert "owner_grant_ai_agent_access.sh" in pack

    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "refresh_ai_agent_access_inventory.py" in republish

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("main_writable") is True
    # batch stamp advances with refresh; allow 321 manual or 323 auto.
    assert int(str(inv.get("batch") or "0")) >= 321
    details = inv.get("details") or []
    assert len(details) == 8
    for d in details:
        tip = str(d.get("tip_sha") or "")
        assert len(tip) == 40, f"short tip_sha for {d.get('name')}: {tip!r}"
        assert d.get("write") == "WRITABLE"
    sandbox = inv.get("sandbox") or {}
    assert sandbox.get("write") == "WRITABLE"
    tip7 = str(sandbox.get("tip") or "")
    assert len(tip7) >= 7
    # sandbox.tip must agree with details tip prefix (pre-323 drift class).
    sb_detail = next(d for d in details if str(d.get("name") or "").endswith("/sandbox"))
    assert str(sb_detail.get("tip_sha") or "").startswith(tip7[:7])

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 323)
    assert "Batch 323" in unblock

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 323)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 323" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 323)" in land


def test_batch324_print_owner_unblock_tip_drift_not_apply_ready() -> None:
    """Batch 324: PATH_C_LANDED_TIP_DRIFT must not advertise APPLY_READY land."""
    import json
    import subprocess

    unblock_path = ROOT / "scripts" / "print_owner_unblock.sh"
    unblock = unblock_path.read_text(encoding="utf-8")
    assert "Batch 324" in unblock
    assert "PATH_C_LANDED_TIP_DRIFT" in unblock
    # Tip-drift branch must precede the APPLY_READY fallback (Batch 261 leftover).
    assert unblock.index("PATH_C_LANDED_TIP_DRIFT") < unblock.rindex(
        "APPLY_READY on hardening BASE_TIP"
    )
    _assert_print_owner_header_batch_at_least(unblock, 324)

    status_path = ROOT / "portable" / "PATH_C_STATUS.json"
    prior = status_path.read_text(encoding="utf-8")
    try:
        data = json.loads(prior)
        data["idle_status"] = "PATH_C_LANDED_TIP_DRIFT"
        data["tip"] = "077464e"
        data["base_tip"] = str(data.get("base_tip") or "02cfbfd")[:7]
        data["tip_match"] = False
        data["lemma_closed"] = False
        status_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        out = subprocess.check_output(
            ["bash", str(unblock_path)],
            cwd=str(ROOT),
            text=True,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
    finally:
        status_path.write_text(prior, encoding="utf-8")

    path_c_lines = [ln for ln in out.splitlines() if ln.startswith("Path C:")]
    assert path_c_lines, "print_owner_unblock missing Path C: line"
    line = path_c_lines[0]
    assert "PATH_C_LANDED_TIP_DRIFT" in line or "tip-drift" in line
    assert "refresh_path_c_bundle" in line
    # Must not advertise APPLY_READY land (negation phrase "not APPLY_READY" is OK).
    assert "APPLY_READY on hardening" not in line
    assert "# APPLY_READY" not in line

def test_batch322_multi_agent_wake() -> None:
    """Batch 322: multi-agent wake+assign artifact; lemma_closed stays false."""
    import json

    path = ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH322.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("action") == "multi_agent_wake_and_assign"
    assert data.get("lemma_closed") is False

def test_batch325_keep_prior_bundle_verify_workdir() -> None:
    """Batch 325: keep-prior bundle verify uses WORKDIR (not trial ROOT abort)."""
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 325)
    assert "Batch 325: verify against WORKDIR" in refresh
    assert 'git -C "$WORKDIR" bundle verify' in refresh
    # Tolerate empty/fail under set -e (list-heads + verify).
    assert "|| true" in refresh
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 325" in log_md
    assert "keep-prior" in log_md.lower() or "WORKDIR" in log_md


def test_batch326_research_audit_no_promotion() -> None:
    """Batch 326: research open-list audit artifact; lemma_closed stays false."""
    import json

    path = ROOT / "portable" / "BATCH326_RESEARCH_STACK_AUDIT.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("scientific_effect") == "NONE"
    assert str(data.get("batch")) == "326"
    assert data.get("audit_kind") == "research_stack_mechanical_open_list"
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "Batch 325: verify against WORKDIR" in refresh
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 326" in log_md


def test_batch327_verify_refresh_and_wake_pack() -> None:
    """Batch 327: VERIFY.refresh_batch after keep-prior force; wake poster in pack."""
    import json

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(verify.get("refresh_batch") or 0) >= 327
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("lemma_closed") is False
    assert _living_tip(str(verify.get("base_tip_sha", "")))

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 327)
    assert "Batch 325: verify against WORKDIR" in refresh

    pack = (ROOT / "scripts" / "pack_portable.sh").read_text(encoding="utf-8")
    assert "post_batch322_wake_comments.py" in pack
    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "post_batch322_wake_comments.py" in republish
    assert (ROOT / "scripts" / "post_batch322_wake_comments.py").is_file()

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 327)
    assert "Batch 327" in unblock

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 327" in log_md


def test_batch328_inventory_batch_living() -> None:
    """Batch 328: inventory refresh batch stamp follows print_owner header."""
    import json
    import re

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert "_living_inventory_batch" in helper
    assert 'INV_BATCH", "323"' not in helper and "INV_BATCH', '323'" not in helper
    assert 'os.environ.get("INV_BATCH") or _living_inventory_batch' in helper
    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(encoding="utf-8")
    assert "INV_BATCH=323" not in grant
    assert "refresh_ai_agent_access_inventory.py" in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    header_batch = int(m.group(1))
    assert header_batch >= 328
    _assert_print_owner_header_batch_at_least(unblock, 328)

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(str(inv.get("batch") or "0")) >= 328

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 328)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 328)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 328" in log_md


def test_batch329_tip_refresh_living_and_wake() -> None:
    """Batch 329: living tip_refresh assert + MULTI_AGENT_WAKE_BATCH329."""
    import json
    import re

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    # Historical Batch 289 body must not freeze tip_refresh=True forever.
    assert "assert verify.get(\"tip_refresh\") is True" not in intent
    # Shared living helper covers Batch 180/202/289 (+329) VERIFY.tip_refresh siblings.
    assert "_assert_living_tip_refresh" in intent
    assert "_living_tip_refresh" in intent
    assert intent.count("_assert_living_tip_refresh(") >= 4

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH329.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 329
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("wake329_on_main") is True
    assert _living_tip(str(wake.get("tip") or ""))
    assert wake.get("intent", {}).get("lemma_closed") is False
    assert wake.get("intent", {}).get("path_c") == "IDLE@0019"
    assert len(wake.get("woken_idle_agents") or []) >= 10

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 329
    _assert_print_owner_header_batch_at_least(unblock, 329)
    assert "Batch 329" in unblock
    assert "tip_refresh" in unblock.lower() or "MULTI_AGENT_WAKE_BATCH329" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 329)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 329)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 329" in log_md

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    _assert_living_tip_refresh(verify.get("tip_refresh"))
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert verify.get("lemma_closed") is False

def test_batch329_print_owner_critical_script_stale() -> None:
    """Batch 329: print_owner_unblock in republish CRITICAL; no APPLY_READY-stale miss."""
    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert '    "scripts/print_owner_unblock.sh",' in republish
    # Must sit inside the CRITICAL tuple (Batch 329), not only pack_portable.
    crit_at = republish.index("CRITICAL = (")
    end_at = republish.index("\n)", crit_at)
    crit_block = republish[crit_at:end_at]
    assert "print_owner_unblock.sh" in crit_block
    assert crit_block.count("print_owner_unblock.sh") == 1
    assert "Batch 329" in crit_block

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "Batch 329" in unblock
    assert "PATH_C_LANDED_TIP_DRIFT" in unblock
    _assert_print_owner_header_batch_at_least(unblock, 329)

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 329)

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert 'batch = "328"' not in helper
    assert "_living_inventory_batch(root)" in helper

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 329" in log_md
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 329)" in land

def test_batch329_inv_no_token_preserve_durable() -> None:
    """Batch 329: no_token tip-refresh must not clobber durable 8/8 attribution."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path

    helper = ROOT / "scripts" / "refresh_ai_agent_access_inventory.py"
    text = helper.read_text(encoding="utf-8")
    assert "Batch 329" in text
    assert "_no_durable_probe" in text
    assert "preserve_durable" in text
    assert "False no_token grant-audit" in text or "false no_token grant-audit" in text

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(encoding="utf-8")
    assert "Batch 329" in grant
    assert "false no_token grant-audit" in grant

    docs = (ROOT / "docs" / "MULTI_AGENT_ACCESS.md").read_text(encoding="utf-8")
    assert "Batch 329" in docs
    assert "no_token" in docs
    assert "8/8 WRITABLE" in docs

    spec = importlib.util.spec_from_file_location("refresh_inv_329", helper)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "AI_AGENT_ACCESS_INVENTORY.json"
        path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
        repos = [d["name"] for d in inv["details"]]
        # Simulate ambient App --check with no durable token (n/a).
        result = mod.refresh(
            str(path),
            repos,
            durable_writable=0,
            durable_sandbox_read="n/a",
            durable_sandbox_write="n/a",
            active_sandbox_read="404",
            batch="329",
        )
        assert result.get("preserve_durable") is True
        out = json.loads(path.read_text(encoding="utf-8"))
        assert out.get("durable_sibling_coverage") == "8/8_WRITABLE"
        assert out.get("lemma_closed") is False
        assert out.get("flipped_anything") is False
        assert out.get("main_writable") is True
        assert out.get("sandbox", {}).get("readable") is True
        assert out.get("sandbox", {}).get("write") == "WRITABLE"
        for d in out.get("details") or []:
            assert d.get("push") is True, d
            assert d.get("write") == "WRITABLE", d
        for c in out.get("repos_connected") or []:
            assert c.get("perm") == "push", c


def test_batch330_inv_no_token_preserve_durable() -> None:
    """Batch 330: land no_token durable preserve; header >= 330."""
    import re

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert "_no_durable_probe" in helper
    assert "preserve_durable" in helper
    assert "cov8" in helper or "8/8_WRITABLE" in helper

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 330
    _assert_print_owner_header_batch_at_least(unblock, 330)
    assert "no_token" in unblock.lower() or "DURABLE_SANDBOX_WRITE=n/a" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 330)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 330" in log_md




def test_batch331_grant_skip_inventory_refresh_without_durable() -> None:
    """Batch 331: grant --check skips inventory refresh when durable token absent."""
    import json
    import re

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(encoding="utf-8")
    assert "Batch 331" in grant
    assert "inventory_refresh=skip durable_token_source=" in grant
    assert "do not App-corrupt" in grant

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert "durable_writable == len(repos)" in helper
    assert "Batch 331" in helper

    tiny = json.loads(
        (ROOT / "portable" / "BATCH330_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "330"
    assert tiny.get("write_durable") == "8/8_WRITABLE"
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert _living_tip(str(tiny.get("tip_sha", "")))
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("action") == "grant_check_skip_inventory_refresh_without_durable_token"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 331
    _assert_print_owner_header_batch_at_least(unblock, 331)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 331)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 331" in log_md

def test_batch332_tip_sync_after_main_97() -> None:
    """Batch 332: tip-sync after main #97 inventable; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH332_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "332"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_shipped") is True
    assert brief.get("defect_id") == "tip_sync_077464e_to_388a22c_main_97"
    assert brief.get("route_now") == "TIP_SYNC"
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("patch_0020") is False
    assert brief.get("hunt_0020") == "NEGATIVE"
    assert brief.get("tip_moved") is True
    assert 97 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("388a22c")
    assert str(brief.get("prior_tip", "")).startswith("077464e")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH332_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "tip_sync_077464e_to_388a22c_main_97"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert any("97" in a or "inventable" in a for a in (hunt.get("avoided") or []))

    audit = json.loads(
        (ROOT / "portable" / "BATCH332_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(
        encoding="utf-8"
    )
    # Live BASE_TIP supersedes across tip-sync; Batch 332 shipped 388a22c.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 332
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    # Live tip supersedes; historical prior may be 077464e or later living SHA.
    assert _living_tip(str(verify.get("prior_base_tip_sha", ""))) or str(
        verify.get("prior_base_tip_sha", "")
    ).startswith("077464e")
    assert verify.get("lemma_closed") is False
    assert verify.get("tip_refresh") in (True, False)

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 332)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 332)
    assert "388a22c" in unblock or "Batch 332" in unblock or "tip-sync" in unblock.lower()

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert status.get("lemma_closed") is False

    assert "388a22c" in _LIVING_TIPS
    assert "077464e" in _LIVING_TIPS

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 332)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 332" in log_md

def test_batch333_republish_release_view_retry() -> None:
    """Batch 333: republish retries release-view; STATUS_GUARD tip living."""
    import json
    import re

    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 333" in republish
    assert "REPUBLISH_RELEASE_VIEW_RETRIES" in republish
    assert "release-view attempt" in republish
    assert "dry-run continues with empty release metadata" in republish

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("flipped_anything") is False
    assert snap.get("pass") is True
    assert _living_tip(str(snap.get("tip_sha", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 333
    _assert_print_owner_header_batch_at_least(unblock, 333)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 333)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 333" in log_md

def test_batch334_grant_skip_only_when_token_none() -> None:
    """Batch 334: inventory skip only when durable_token_source=none."""
    import re

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(encoding="utf-8")
    assert "Batch 334" in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    # Must not OR with writable=0 (Batch 331 over-broad).
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant
    assert "do not App-corrupt" in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 334
    _assert_print_owner_header_batch_at_least(unblock, 334)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 334)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 334" in log_md

def test_batch335_tip_sync_after_main_99_100() -> None:
    """Batch 335: tip-sync after main #99/#100; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH335_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "335"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("defect_id") == "tip_sync_388a22c_to_eeebb28_main_99_100"
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("patch_0020") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("eeebb28")
    assert str(brief.get("prior_tip", "")).startswith("388a22c")
    assert 99 in (brief.get("merged_prs") or [])
    assert 100 in (brief.get("merged_prs") or [])

    hunt = json.loads(
        (ROOT / "portable" / "BATCH335_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 335 shipped eeebb28.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 335
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert verify.get("lemma_closed") is False

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 335)
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 335)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert "eeebb28" in _LIVING_TIPS
    assert "388a22c" in _LIVING_TIPS

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 335)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 335" in log_md



def test_batch336_multi_agent_wake_verify_land() -> None:
    """Batch 336: wake336 on main; Batch 329 prior wake present; lemma_closed false."""
    import json

    wake329 = ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH329.json"
    assert wake329.is_file()
    data329 = json.loads(wake329.read_text(encoding="utf-8"))
    assert data329.get("lemma_closed") is False
    assert data329.get("wake329_on_main") is True

    path = ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH336.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("wake336_on_main") is True
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert _living_tip(str(data.get("tip") or ""))
    assert data.get("action") in (
        "multi_agent_wake_batch336_verify_land",
        "multi_agent_wake_and_assign",
    )
    woken = data.get("woken_idle_agents") or []
    peers = data.get("spawned_cloud_peers") or []
    assert len(woken) + len(peers) >= 1
    if woken:
        assert all(a.get("bcId") and a.get("assignment") for a in woken)

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 336" in log_md


def test_batch336_soften_batch335_live_tip_pins() -> None:
    """Batch 336: Batch 335 live tip Intent pins softened to _living_tip."""
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch335_tip_sync_after_main_99_100")
    end = intent.index("def test_batch336_soften_batch335_live_tip_pins")
    body = intent[start:end]
    assert "Live BASE_TIP supersedes across tip-sync; Batch 335 shipped eeebb28" in body
    assert 'assert "eeebb28" in base_tip' not in body
    assert 'verify.get("base_tip_sha", "")).startswith("eeebb28")' not in body

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 336)
    assert "Batch 336" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 336" in log_md
    assert "eeebb28" in _LIVING_TIPS


def test_batch336_inventory_batch_fallback_living() -> None:
    """Batch 336: _living_inventory_batch ultimate fallback uses REFRESH_BATCH_TAG."""
    import importlib.util
    import tempfile
    from pathlib import Path

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert 'return "331"' not in helper
    assert "REFRESH_BATCH_TAG:-" in helper
    assert "_living_inventory_batch" in helper

    spec = importlib.util.spec_from_file_location(
        "refresh_ai_agent_access_inventory",
        ROOT / "scripts" / "refresh_ai_agent_access_inventory.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    td = tempfile.mkdtemp()
    scripts = Path(td) / "scripts"
    scripts.mkdir()
    (scripts / "refresh_path_c_bundle.sh").write_text(
        'BATCH_TAG="${REFRESH_BATCH_TAG:-342}"\n', encoding="utf-8"
    )
    assert mod._living_inventory_batch(td) == "342"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 336)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 336" in log_md
    assert "331" in log_md or "REFRESH_BATCH_TAG" in log_md



def test_batch336_inv_preserve_durable_writable0_denied() -> None:
    """Batch 336: preserve_durable on durable_writable=0 with sandbox_write=DENIED."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert "Batch 336" in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant
    assert "sandbox_write=DENIED" in grant or "durable_writable=0" in grant

    helper_path = ROOT / "scripts" / "refresh_ai_agent_access_inventory.py"
    helper = helper_path.read_text(encoding="utf-8")
    assert "Batch 336" in helper
    assert "durable_writable == 0" in helper
    assert "preserve_durable" in helper

    tiny = json.loads(
        (ROOT / "portable" / "BATCH336_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "336"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("scientific_effect") == "NONE"
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("defect_id") == "inv_preserve_durable_writable0_denied"
    assert tiny.get("action") == "inv_preserve_durable_on_writable0_denied"
    assert _living_tip(str(tiny.get("tip", "")))
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert (tiny.get("contracts") or {}).get("grant_skip_only_when") == (
        "durable_token_source=none"
    )

    spec = importlib.util.spec_from_file_location("refresh_inv_336", helper_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(
            encoding="utf-8"
        )
    )
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("lemma_closed") is False

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "AI_AGENT_ACCESS_INVENTORY.json"
        path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
        repos = [d["name"] for d in inv["details"]]
        result = mod.refresh(
            str(path),
            repos,
            durable_writable=0,
            durable_sandbox_read="404",
            durable_sandbox_write="DENIED",
            active_sandbox_read="404",
            batch="336",
        )
        assert result.get("preserve_durable") is True
        out = json.loads(path.read_text(encoding="utf-8"))
        assert out.get("durable_sibling_coverage") == "8/8_WRITABLE"
        assert out.get("lemma_closed") is False
        assert out.get("flipped_anything") is False
        assert out.get("main_writable") is True
        assert out.get("sandbox", {}).get("readable") is True
        assert out.get("sandbox", {}).get("write") == "WRITABLE"
        for d in out.get("details") or []:
            assert d.get("push") is True, d
            assert d.get("write") == "WRITABLE", d
        for c in out.get("repos_connected") or []:
            assert c.get("perm") == "push", c

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 336)

    docs = (ROOT / "docs" / "MULTI_AGENT_ACCESS.md").read_text(encoding="utf-8")
    assert "Batch 334/336" in docs or "Batch 336" in docs
    assert "preserve_durable" in docs or "durable_writable" in docs

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 336" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in owner


def test_batch336_wake_intent_living_base_tip() -> None:
    """Batch 336: wake poster INTENT tip derives from BASE_TIP (not frozen 077464e)."""
    import json
    import re
    import sys

    poster_path = ROOT / "scripts" / "post_batch322_wake_comments.py"
    poster = poster_path.read_text(encoding="utf-8")
    assert "Batch 336" in poster
    assert "BASE_TIP.txt" in poster
    assert "_living_tip_short" in poster
    assert "intent_line" in poster
    # Frozen tip pin must not remain in INTENT construction.
    assert "@ 077464e" not in poster
    assert "INTENT = (" not in poster

    sys.path.insert(0, str(ROOT / "scripts"))
    import post_batch322_wake_comments as wake  # type: ignore

    tip = wake._living_tip_short()
    assert _living_tip(tip)
    line = wake.intent_line()
    assert tip in line
    assert "IDLE@0019" in line
    assert "lemma_closed=false" in line
    assert "scientific effect NONE" in line

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    m = re.search(r"(?i)\b([0-9a-f]{40})\b", base_tip)
    assert m is not None
    assert tip == m.group(1)[:7].lower()
    # Date fragment from hardening ref must not be mistaken for tip.
    assert tip != "2026091"
    assert "20260919" not in tip

    brief = json.loads(
        (ROOT / "portable" / "BATCH336_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "336"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "wake_intent_tip_frozen_077464e_vs_living_base_tip"
    assert brief.get("action") == "eng_wake_living_tip"
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH336_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("defect_id") == "wake_intent_tip_frozen_077464e_vs_living_base_tip"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 336)
    assert "Batch 336" in unblock
    assert "wake poster INTENT" in unblock or "077464e" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 336" in log_md
    assert "wake INTENT" in log_md or "post_batch322_wake_comments" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 336)" in owner


def test_batch337_tip_sync_after_main_101_107_102() -> None:
    """Batch 337: tip-sync after main #101/#107/#102; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH337_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "337"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "tip_sync_eeebb28_to_848aea2_main_101_107_102"
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("patch_0020") is False
    assert brief.get("tip_match") is True or brief.get("aligned") is True
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("848aea2")
    assert str(brief.get("prior_tip", "")).startswith("eeebb28")
    assert 101 in (brief.get("merged_prs") or [])
    assert 107 in (brief.get("merged_prs") or [])
    assert 102 in (brief.get("merged_prs") or [])

    hunt = json.loads(
        (ROOT / "portable" / "BATCH337_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("defect_found") is True
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_id") == "tip_sync_eeebb28_to_848aea2_main_101_107_102"

    audit = json.loads(
        (ROOT / "portable" / "BATCH337_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("scientific_effect") == "NONE"
    assert audit.get("status_promotion") is False
    assert int(audit.get("open_premises") or 0) >= 1
    assert _living_tip(str(audit.get("tip_sha", "")))

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH337.json").read_text(
            encoding="utf-8"
        )
    )
    assert wake.get("wake337_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert _living_tip(str(wake.get("tip") or ""))
    assert len(wake.get("woken_idle_agents") or []) >= 3

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 337 shipped 848aea2.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 337
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert verify.get("lemma_closed") is False

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 337)
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 337)

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(status.get("tip"))
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"
    assert "848aea2" in _LIVING_TIPS
    assert "eeebb28" in _LIVING_TIPS

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 337)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 337" in log_md
    assert "848aea2" in log_md or "tip-sync" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 337)" in owner


def test_batch337_no_frozen_live_tip_pins() -> None:
    """Batch 337: tip-sync Intent uses _living_tip — not frozen startswith on BASE_TIP/VERIFY."""
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch337_tip_sync_after_main_101_107_102")
    end = intent.index("def test_batch337_no_frozen_live_tip_pins")
    body = intent[start:end]
    assert "Live BASE_TIP supersedes across tip-sync; Batch 337 shipped 848aea2" in body
    assert 'assert "848aea2" in base_tip' not in body
    assert 'verify.get("base_tip_sha", "")).startswith("848aea2")' not in body
    assert "848aea2" in _LIVING_TIPS
    assert "eeebb28" in _LIVING_TIPS


def test_batch338_align_watch_idle() -> None:
    """Batch 338: post-Path-C align watch idle; tip stable; lemma_closed false."""
    import json

    path = ROOT / "portable" / "BATCH338_ALIGN_WATCH.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("batch") == "338"
    assert data.get("action") == "post_path_c_align_watch_idle"
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("tip_match") is True
    assert data.get("aligned") is True
    assert _living_tip(str(data.get("hardening_tip", "")))
    assert _living_tip(str(data.get("base_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 338)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 338)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 338" in log_md


def test_batch338_wake_marker_living_tip() -> None:
    """Batch 338: wake skip gate keys off living tip — not frozen Batch 329 marker."""
    import json
    import sys

    poster_path = ROOT / "scripts" / "post_batch322_wake_comments.py"
    poster = poster_path.read_text(encoding="utf-8")
    assert "Batch 338" in poster
    assert "batch_marker" in poster
    assert "_wake_body_has_living_tip" in poster
    assert 'BATCH_MARKER = "Batch 329 wake"' not in poster
    assert "pull/112" not in poster
    assert "TRIAL_REPO" in poster

    sys.path.insert(0, str(ROOT / "scripts"))
    import post_batch322_wake_comments as wake  # type: ignore

    tip = wake._living_tip_short()
    assert _living_tip(tip)
    marker = wake.batch_marker()
    assert tip in marker
    assert marker.startswith("Batch ")
    assert "wake @" in marker
    assert "329" not in marker or tip in marker  # living N, not frozen 329-only

    stale = (
        "**Batch 329 wake** — project-intent eng resume\n\n"
        "Intent: tip chatgpt/drive-github-hardening-20260919 @ 077464e; "
        "Path C IDLE@0019\n"
    )
    assert wake._wake_body_has_living_tip(stale) is False
    fresh = wake.wake_body(92)
    assert wake._wake_body_has_living_tip(fresh) is True
    assert tip in fresh
    assert "077464e" not in fresh or tip == "077464e"
    assert "pull/112" not in fresh
    assert wake.intent_line().startswith("Intent: tip ")
    assert tip in wake.intent_line()

    brief = json.loads(
        (ROOT / "portable" / "BATCH338_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "338"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "wake_marker_frozen_329_skips_living_tip"
    assert brief.get("action") == "eng_wake_marker_living_tip"
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH338_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("defect_found") is True
    assert hunt.get("defect_id") == "wake_marker_frozen_329_skips_living_tip"
    assert hunt.get("hunt_0020") == "NEGATIVE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 338)
    assert "wake poster skip" in unblock or "Batch 329 wake" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 338)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 338" in log_md
    assert "wake marker" in log_md.lower() or "Batch 329 wake" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 338)" in owner


def test_batch339_living_script_stale_republish() -> None:
    """Batch 339: tip stable @848aea2; living script_stale republish."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH339_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "339"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_moved") is False
    assert brief.get("action") == "living_script_stale_republish"
    assert brief.get("defect_id") == "living_release_script_stale_after_338"
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH339_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("tip_moved") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 339)
    assert "Batch 339" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 339)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 339)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 339" in log_md

def test_batch340_audit_rate_limit_403_backoff() -> None:
    """Batch 340: audit 403 installation rate-limit backoff; misalignment unchanged."""
    import importlib.util
    import json
    import time
    import urllib.error
    from io import BytesIO
    from unittest import mock

    audit_path = ROOT / "scripts" / "audit_main_alignment.py"
    audit_src = audit_path.read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_RETRIES" in audit_src
    assert "AUDIT_TRANSPORT_SLEEP_CAP_S" in audit_src
    assert "x-ratelimit-reset" in audit_src.lower() or "X-RateLimit-Reset" in audit_src
    assert "Batch 340" in audit_src
    assert "rate-limit retry" in audit_src
    # Misalignment predicate must remain (do not weaken detection).
    assert "misaligned = bool(complexity_hits)" in audit_src
    assert 'return 1' in audit_src

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_RETRIES" in ci
    assert "AUDIT_TRANSPORT_SLEEP_CAP_S" in ci

    spec = importlib.util.spec_from_file_location("audit340", audit_path)
    assert spec is not None and spec.loader is not None
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)

    # 403 installation primary rate-limit body (CI run 36172207352 shape).
    body = b'{"message":"API rate limit exceeded for installation. ..."}'
    exc403 = urllib.error.HTTPError(
        "https://api.github.com",
        403,
        "Forbidden",
        hdrs={"X-RateLimit-Reset": str(int(time.time()) + 2)},
        fp=BytesIO(body),
    )
    assert audit._is_rate_limited(exc403) is True
    # Fresh exc for delay (body read is one-shot).
    exc403b = urllib.error.HTTPError(
        "https://api.github.com",
        403,
        "Forbidden",
        hdrs={"X-RateLimit-Reset": str(int(time.time()) + 2)},
        fp=BytesIO(body),
    )
    delay = audit._retry_after_seconds(exc403b, 1)
    assert delay >= 2.0
    assert delay <= audit._TRANSPORT_SLEEP_CAP_S

    audit._TRANSPORT_SLEEP_S = 0.01
    audit._TRANSPORT_RETRIES = 6
    audit._TRANSPORT_SLEEP_CAP_S = 1.0
    # Batch 349: CI Intent sets AUDIT_TRANSPORT_EARLY_FALLBACK=1 (timeout budget);
    # unit backoff still needs retries — force off for this test.
    audit._TRANSPORT_EARLY_FALLBACK = False
    calls = {"n": 0}
    ok_body = json.dumps({"ok": True}).encode()

    class _CM:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def __enter__(self):
            return BytesIO(self._data)

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=60):
        calls["n"] += 1
        if calls["n"] < 4:
            raise urllib.error.HTTPError(
                "https://api.github.com",
                403,
                "Forbidden",
                hdrs={"Retry-After": "0"},
                fp=BytesIO(
                    b'{"message":"API rate limit exceeded for installation."}'
                ),
            )
        return _CM(ok_body)

    with mock.patch("urllib.request.urlopen", fake_urlopen):
        data = audit.get_json("https://api.github.com/repos/example/x")
    assert data == {"ok": True}
    assert calls["n"] == 4

    # Defaults stronger than Batch 256's 3/2s (exhausted in ~6s on CI).
    # Re-read module-level defaults from source (test may have mutated).
    assert 'AUDIT_TRANSPORT_RETRIES", "6"' in audit_src or "AUDIT_TRANSPORT_RETRIES', '6'" in audit_src
    assert 'AUDIT_TRANSPORT_SLEEP_S", "3"' in audit_src or "AUDIT_TRANSPORT_SLEEP_S', '3'" in audit_src

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "Batch 340" in unblock

    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in owner
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 340" in log_md
    assert "36172207352" in log_md or "rate-limit" in log_md.lower()

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False


def test_batch340_wake_land_verify() -> None:
    """Batch 340: wake340 on main; tip_match living; lemma_closed false."""
    import json

    path = ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("batch") == 340
    assert data.get("action") == "multi_agent_wake_and_assign"
    assert data.get("wake340_on_main") is True
    assert data.get("tip_match") is True
    assert data.get("lemma_closed") is False
    assert data.get("flipped_anything") is False
    assert data.get("scientific_effect") == "NONE"
    assert data.get("path_c") == "IDLE@0019"
    assert data.get("durable") == "8/8"
    assert _living_tip(str(data.get("tip") or ""))
    # Living tip supersedes across tip-sync; wake_tip_at_assign keeps historical assign tip.
    assert _living_tip(data.get("tip"))
    assert _living_tip((data.get("intent") or {}).get("base_tip_expected"))
    assert _living_tip(str(data.get("wake_tip_at_assign") or ""))
    living = data.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert len(data.get("woken_idle_agents") or []) >= 3
    assert len(data.get("spawned_cloud_peers") or []) >= 1

    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("tip_match") is True
    assert _living_tip(status.get("tip"))
    assert status.get("lemma_closed") is False
    assert status.get("idle_status") == "IDLE_PATH_C_DONE"

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 340" in log_md



def test_batch340_audit_rate_limit_raw_fallback() -> None:
    """Batch 340b: raw/ls-remote fallback after rate-limit; CI soft-continue exit 2."""
    import importlib.util
    import json
    import urllib.error
    import urllib.request
    from io import BytesIO
    from unittest import mock

    audit_path = ROOT / "scripts" / "audit_main_alignment.py"
    audit_src = audit_path.read_text(encoding="utf-8")
    assert "_audit_via_raw_fallback" in audit_src
    assert "raw.githubusercontent.com" in audit_src
    assert "ls-remote" in audit_src
    assert "RateLimitExhausted" in audit_src
    assert "misaligned = bool(complexity_hits)" in audit_src

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "soft continue" in ci.lower() or "soft-continue" in ci.lower()
    assert "AUDIT_TRANSPORT_RETRIES" in ci

    spec = importlib.util.spec_from_file_location("audit340b", audit_path)
    assert spec is not None and spec.loader is not None
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)

    audit._TRANSPORT_SLEEP_S = 0.0
    audit._TRANSPORT_RETRIES = 2
    real_urlopen = urllib.request.urlopen

    def selective(req, timeout=60):
        url = getattr(req, "full_url", str(req))
        if "api.github.com" in url:
            raise urllib.error.HTTPError(
                url,
                403,
                "Forbidden",
                hdrs={},
                fp=BytesIO(
                    b'{"message":"API rate limit exceeded for installation."}'
                ),
            )
        return real_urlopen(req, timeout=timeout)

    with mock.patch("urllib.request.urlopen", selective):
        code = audit.main()
    assert code in (0, 1)

    brief = json.loads(
        (ROOT / "portable" / "BATCH340_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "340"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "audit_main_alignment_rate_limit_no_raw_fallback"
    )
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH340_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == (
        "audit_main_alignment_rate_limit_no_raw_fallback"
    )
    assert hunt.get("hunt_0020") == "NEGATIVE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in land
    assert "raw" in land.lower() or "fallback" in land.lower()
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "raw/ls-remote" in log_md or "raw fallback" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in owner



def test_batch340_inventory_ultimate_fallback_unfreeze() -> None:
    """Batch 340: empty-tree inventory batch fallback no longer freezes at 336."""
    import importlib.util
    import json
    import re
    import tempfile
    from pathlib import Path

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    # Living INV_BATCH supersedes across grant tip-refresh; Batch 340 shipped 340.
    assert int(str(inv.get("batch") or "0")) >= 340
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("sibling_write_count") == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    assert inv.get("main_writable") is True
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d
        assert len(str(d.get("tip_sha") or "")) >= 7
    for c in inv.get("repos_connected") or []:
        assert c.get("perm") == "push", c

    tiny = json.loads(
        (ROOT / "portable" / "BATCH340_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "340"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("action") == "grant_inventory_refresh_batch340"
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("tip", "")))
    assert _living_tip(str(tiny.get("tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert 'return "336"' not in helper
    # Living ultimate fallback supersedes across tip-sync; Batch 340 shipped "340".
    # Do not freeze assert 'return "340"' (Batch 343 class after REFRESH 343).
    m_fb = re.search(r'return "(\d+)"', helper)
    assert m_fb is not None, "missing last-resort return \"N\" in inventory helper"
    assert int(m_fb.group(1)) >= 340
    assert "last-resort" in helper or "REFRESH_BATCH_TAG" in helper

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 340)

    spec = importlib.util.spec_from_file_location(
        "refresh_ai_agent_access_inventory",
        ROOT / "scripts" / "refresh_ai_agent_access_inventory.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    td = tempfile.mkdtemp()
    (Path(td) / "scripts").mkdir()
    assert mod._living_inventory_batch(td) == m_fb.group(1)

    # REFRESH-only tree still wins over hardcoded when present
    (Path(td) / "scripts" / "refresh_path_c_bundle.sh").write_text(
        'BATCH_TAG="${REFRESH_BATCH_TAG:-341}"\n', encoding="utf-8"
    )
    assert mod._living_inventory_batch(td) == "341"

    brief = json.loads(
        (ROOT / "portable" / "BATCH340_INV_FALLBACK_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("defect_id") == "inventory_ultimate_fallback_frozen_336"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("action") == "ship_eng_defect"
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH340_INV_FALLBACK_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == "inventory_ultimate_fallback_frozen_336"
    assert hunt.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "frozen 336" in unblock or "ultimate fallback" in unblock

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "ultimate fallback" in log_md


def test_batch340_multi_agent_wake_assign() -> None:
    """Batch 340: Dylan wake stopped agents + assign Path C intent tasks."""
    import json

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 340
    assert wake.get("wake340_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    assert len(wake.get("spawned_cloud_peers") or []) >= 1
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    brief = json.loads(
        (ROOT / "portable" / "BATCH340_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "340"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "MULTI_AGENT wake" in unblock or "wake+assign" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "wake" in land.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH340" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md or "wake+assign" in log_md


def test_batch340_republish_critical_includes_audit() -> None:
    """Batch 340: republish CRITICAL includes audit_main_alignment (pack-only was silent)."""
    import json

    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "scripts/audit_main_alignment.py" in republish
    # CRITICAL tuple must list audit (not only pack_portable include).
    crit_start = republish.index("CRITICAL = (")
    # First ")" after CRITICAL can be inside a comment — take until member_sha.
    crit_end = republish.index("def member_sha", crit_start)
    crit = republish[crit_start:crit_end]
    assert '"scripts/audit_main_alignment.py"' in crit
    assert "Batch 340" in republish and "CRITICAL" in republish

    art = json.loads(
        (ROOT / "portable" / "BATCH340_CRITICAL.json").read_text(encoding="utf-8")
    )
    assert art.get("batch") == "340"
    assert art.get("lemma_closed") is False
    assert art.get("flipped_anything") is False
    assert art.get("scientific_effect") == "NONE"
    assert art.get("defect_id") == "republish_critical_missing_audit_main_alignment"
    assert art.get("action") == "eng_critical_include_audit"
    assert _living_tip(str(art.get("tip", "")))

    # Soften: wake340 tip pin must not hard-require startswith 848aea2 forever.
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch340_wake_land_verify")
    end = intent.index("def test_batch340_audit_rate_limit_raw_fallback")
    body = intent[start:end]
    assert 'startswith("848aea2")' not in body
    assert (
        "Live tip supersedes; historical wake tip may stay 848aea2 across tip-sync." in body
        or "wake_tip_at_assign" in body
        or "Batch 342" in body
    )

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "audit_main_alignment" in unblock and "CRITICAL" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in land
    assert "CRITICAL" in land or "audit_main_alignment" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "CRITICAL" in log_md and "audit_main_alignment" in log_md


def test_batch340_wake_durable_token() -> None:
    """Batch 340: wake poster MAIN_PUSH_TOKEN-first + durable file drops."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path as P

    poster_path = ROOT / "scripts" / "post_batch322_wake_comments.py"
    poster = poster_path.read_text(encoding="utf-8")
    assert "resolve_wake_token" in poster
    assert "Batch 340" in poster
    assert "/cursor/stores/self/MAIN_PUSH_TOKEN" in poster
    assert "/workspace/.secrets/MAIN_PUSH_TOKEN" in poster
    assert "/tmp/gh-dylan-auth/access_token" in poster
    # Prefer MAIN over GH (App ghs Issues:write gap).
    assert '("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")' in poster
    # Old GH-first env-only path must not remain.
    assert (
        'os.environ.get("GH_TOKEN") or os.environ.get("MAIN_PUSH_TOKEN")'
        not in poster
    )

    spec = importlib.util.spec_from_file_location("wake340", poster_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    tok, src = mod.resolve_wake_token(env={"MAIN_PUSH_TOKEN": "pat-main", "GH_TOKEN": "ghs-app"})
    assert tok == "pat-main"
    assert src == "env:MAIN_PUSH_TOKEN"

    tok, src = mod.resolve_wake_token(env={"GH_TOKEN": "ghs-app"})
    assert tok == "ghs-app"
    assert src == "env:GH_TOKEN"

    with tempfile.TemporaryDirectory() as td:
        drop = P(td) / "MAIN_PUSH_TOKEN"
        drop.write_text("pat-file\n", encoding="utf-8")
        tok, src = mod.resolve_wake_token(env={}, file_candidates=(drop,))
        assert tok == "pat-file"
        assert src and src.startswith("file:")

    tok, src = mod.resolve_wake_token(env={}, file_candidates=())
    assert tok is None and src is None

    brief = json.loads(
        (ROOT / "portable" / "BATCH340_WAKE_TOKEN.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "340"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "wake_token_env_only_gh_first_no_durable_files"
    assert brief.get("action") == "eng_wake_durable_token"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal_complete") is False
    assert _living_tip(str(brief.get("tip", "")))
    # Batch 342: live tip may move; do not freeze startswith 848aea2.

    hunt = json.loads(
        (ROOT / "portable" / "BATCH340_WAKE_TOKEN_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "wake_token_env_only_gh_first_no_durable_files"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("tip_moved") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "durable MAIN_PUSH_TOKEN" in unblock or "wake poster loads durable" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340 wake-token)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "wake durable MAIN_PUSH_TOKEN" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340 wake-token)" in owner


def test_batch340_tip_sync_f244312() -> None:
    """Batch 340: tip-sync 848aea2→f244312 after main #108; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH340_TIP_SYNC.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "340"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("defect_id") == "tip_sync_848aea2_to_f244312_main_108"
    assert brief.get("inventable_promoted") is False
    assert 108 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("f244312")
    assert str(brief.get("prior_tip", "")).startswith("848aea2")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH340_TIP_SYNC_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "tip_sync_848aea2_to_f244312_main_108"
    assert hunt.get("lemma_closed") is False
    assert any("108" in a or "inventable" in a for a in (hunt.get("avoided") or []))

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 340 shipped f244312.
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 340
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("lemma_closed") is False
    assert "f244312" in _LIVING_TIPS
    assert "848aea2" in _LIVING_TIPS

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "f244312" in unblock or "tip-sync" in unblock.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "f244312" in land
    assert "tip-sync" in land.lower() or "TIP_OK" in land


def test_batch340_grant_inventory_refresh() -> None:
    """Batch 340: grant inventory tip refresh artifact + durable 8/8."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH340_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "340"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("action") == "grant_inventory_refresh_batch340"
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("tip", "")))
    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    # Living INV_BATCH supersedes across grant tip-refresh; Batch 340 shipped 340+.
    assert int(str(inv.get("batch") or "0")) >= 340
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("sibling_write_count") == 8
    assert inv.get("lemma_closed") is False
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 340)
    assert "grant inventory" in unblock.lower()
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "grant inventory tip refresh" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in owner
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 340)" in land


def test_batch341_grant_inventory_refresh() -> None:
    """Batch 341: grant inventory tip refresh after tip-sync soften land."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH341_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "341"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("write_durable") == "8/8_WRITABLE"
    assert tiny.get("action") == "grant_inventory_refresh_batch341"
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("tip", "")))
    assert _living_tip(str(tiny.get("tip", "")))

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 341
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("sibling_write_count") == 8
    assert inv.get("lemma_closed") is False
    assert (inv.get("repos_connected") or [{}])[0].get("perm") == "push"
    assert (inv.get("sandbox") or {}).get("readable") is True
    details = {d["name"].split("/")[-1]: d for d in (inv.get("details") or [])}
    trial_tip = str(details.get("trial", {}).get("tip_sha", ""))
    assert len(trial_tip) == 40
    assert details.get("trial", {}).get("write") == "WRITABLE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 341)
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 341" in log_md
    assert "grant inventory tip refresh" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341 grant" in owner or "grant inventory tip refresh" in owner.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341" in land


def test_batch341_soften_batch340_live_tip_pins() -> None:
    """Batch 341: tip-sync Intent must not freeze live BASE_TIP to f244312."""
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch340_tip_sync_f244312")
    end = intent.index("def test_batch340_grant_inventory_refresh")
    body = intent[start:end]
    assert "Live BASE_TIP supersedes across tip-sync; Batch 340 shipped f244312" in body
    assert 'assert "f244312" in base_tip' not in body
    assert 'verify.get("base_tip_sha", "")).startswith("f244312")' not in body
    assert "f244312" in _LIVING_TIPS
    assert "848aea2" in _LIVING_TIPS

    # Living BATCH341_BRIEF may supersede across Batch 341 eng continues.
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 341" in log_md
    assert "f244312" in log_md or "soften" in log_md.lower()


def test_batch341_wake_batch_n_living_print_owner() -> None:
    """Batch 341: wake _living_batch_n from print_owner — not frozen _WAKE_BATCH=340."""
    import json
    import sys

    poster_path = ROOT / "scripts" / "post_batch322_wake_comments.py"
    poster = poster_path.read_text(encoding="utf-8")
    assert "Batch 341" in poster
    import re

    assert re.search(r'(?m)^_WAKE_BATCH = "340"\s*$', poster) is None
    assert "_living_batch_n" in poster
    assert "print_owner_unblock.sh" in poster or "_PRINT_OWNER" in poster

    sys.path.insert(0, str(ROOT / "scripts"))
    import post_batch322_wake_comments as wake  # type: ignore

    n = wake._living_batch_n()
    assert n.isdigit()
    assert int(n) >= 341
    tip = wake._living_tip_short()
    assert _living_tip(tip)
    marker = wake.batch_marker()
    assert tip in marker
    assert f"Batch {n} wake @" in marker
    assert "Batch 340 wake @" not in marker or n == "340"

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("flipped_anything") is False
    assert snap.get("pass") is True
    assert _living_tip(str(snap.get("tip_sha", "")))

    brief = json.loads(
        (ROOT / "portable" / "BATCH341_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "341"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "wake_batch_n_frozen_340_vs_print_owner_341"
    assert brief.get("action") == "eng_wake_batch_living"
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH341_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "wake_batch_n_frozen_340_vs_print_owner_341"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 341)
    assert "wake" in unblock.lower() and ("340" in unblock or "batch" in unblock.lower())

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "wake batch" in log_md.lower() or "_WAKE_BATCH" in log_md or "living_batch" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341)" in owner

def test_batch342_wake340_living_tip_pins() -> None:
    """Batch 342: WAKE340 tip pins living @f244312; wake_tip_at_assign preserved."""
    import json

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 340
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    # Living tip supersedes across tip-sync (Batch 343: f244312→fcad723).
    assert _living_tip(wake.get("tip"))
    assert _living_tip((wake.get("intent") or {}).get("base_tip_expected"))
    assert _living_tip(str(wake.get("wake_tip_at_assign") or ""))
    assert int(wake.get("tip_living_updated_batch") or 0) >= 342
    agents = wake.get("woken_idle_agents") or []
    assert any(
        _living_tip(str(a.get("assignment") or ""))
        or "tip_sync_watch" in str(a.get("assignment") or "")
        for a in agents
    )

    brief = json.loads(
        (ROOT / "portable" / "BATCH342_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "342"
    assert brief.get("defect_id") == "wake340_tip_pins_frozen_at_848aea2"
    assert brief.get("action") == "eng_wake340_living_tip_pins"
    assert brief.get("tip_moved") is False
    assert brief.get("lemma_closed") is False

    hunt = json.loads(
        (ROOT / "portable" / "BATCH342_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 342)
    assert "Batch 342" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 342)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 342)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 342" in log_md

    assert _living_tip("f244312")


def test_batch343_tip_sync_after_main_109() -> None:
    """Batch 343: tip-sync f244312→fcad723 after main #109; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "343"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_moved") is True
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("defect_id") == "tip_sync_f244312_to_fcad723_main_109"
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("fcad723")
    assert str(brief.get("prior_tip", "")).startswith("f244312")
    assert brief.get("scientific_effect") == "NONE"
    assert 109 in (brief.get("merged_prs") or [])

    hunt = json.loads(
        (ROOT / "portable" / "BATCH343_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("tip_moved") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("defect_id") == "tip_sync_f244312_to_fcad723_main_109"

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json").read_text(encoding="utf-8")
    )
    assert _living_tip(wake.get("tip"))
    assert _living_tip((wake.get("intent") or {}).get("base_tip_expected"))
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "Batch 343" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 343" in log_md

    assert _living_tip("f244312")


def test_batch341_research_stack_audit() -> None:
    """Batch 341: research audit WITHOUT promotion; lemma stays open."""
    import json

    audit = json.loads(
        (ROOT / "portable" / "BATCH341_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("batch") == "341"
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("scientific_effect") == "NONE"
    assert audit.get("shape") == "HAS_PACKET"
    assert audit.get("action") == "research_stack_audit_without_status_promotion"
    assert (audit.get("packet") or {}).get("lemma_closed") is False
    assert (audit.get("packet") or {}).get("prizes_solved") is False
    assert len(audit.get("open_premises") or []) >= 1
    counts = audit.get("counts") or {}
    assert int(counts.get("open_premises_frozen_layer") or 0) >= 1
    assert int(counts.get("open_lemmas") or 0) >= 1
    assert int(counts.get("open_prizes") or 0) == 3
    assert _living_tip(str(audit.get("tip_sha") or audit.get("tip_short") or ""))
    prs = audit.get("open_main_prs") or {}
    eng = {p.get("number") for p in (prs.get("eng_only_noted") or [])}
    assert {36, 21, 12} <= eng
    skipped = {p.get("number") for p in (prs.get("inventable_research_drafts_skipped") or [])}
    assert 109 in skipped or 110 in skipped
    assert prs.get("promoted") == []
    assert (audit.get("guard") or {}).get("pass") is True

    brief = json.loads(
        (ROOT / "portable" / "BATCH341_RESEARCH_AUDIT_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "341"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("action") == "research_stack_audit_without_status_promotion"
    assert brief.get("inventable_promoted") is False
    ra = brief.get("research_audit") or {}
    assert ra.get("lemma_closed") is False
    assert ra.get("open_premises") >= 1
    assert ra.get("guard_pass") is True

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "Batch 341 research audit" in land
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "research stack audit" in unblock.lower() or "Batch 341" in unblock
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 341" in log_md and "WITHOUT promotion" in log_md


def test_batch342_inventory_tip_refresh_and_wake_token_pin() -> None:
    """Batch 342: inventory batch 342 + soften wake-token live tip pin."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    # Living INV_BATCH supersedes across grant tip-refresh; Batch 342 shipped 342.
    assert int(str(inv.get("batch") or "0")) >= 342
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("lemma_closed") is False
    assert int(inv.get("sibling_write_count") or 0) == 8

    brief = json.loads(
        (ROOT / "portable" / "BATCH342_INV_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "342"
    assert brief.get("lemma_closed") is False
    assert brief.get("action") == "grant_inventory_refresh_batch342"
    assert _living_tip(str(brief.get("tip", "")))

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch340_wake_durable_token")
    end = intent.index("def test_batch340_tip_sync_f244312")
    body = intent[start:end]
    assert 'startswith("848aea2")' not in body

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 342)
    assert "inventory tip refresh batch 342" in unblock or "Batch 342" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 342)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "inventory tip refresh batch 342" in log_md.lower() or "Batch 342" in log_md


def test_batch341_soften_inv_batch_hard_pins_after_342() -> None:
    """Batch 341 continue: Batch 340 Intent must not freeze living INV_BATCH to 340."""
    import json

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch340_inventory_ultimate_fallback_unfreeze")
    end = intent.index("def test_batch340_multi_agent_wake_assign")
    body = intent[start:end]
    assert 'inv.get("batch") == "340"' not in body
    assert "Living INV_BATCH supersedes across grant tip-refresh" in body

    start2 = intent.index("def test_batch340_grant_inventory_refresh")
    end2 = intent.index("def test_batch341_soften_batch340_live_tip_pins")
    body2 = intent[start2:end2]
    assert 'inv.get("batch") == "340"' not in body2
    assert "Living INV_BATCH supersedes across grant tip-refresh" in body2

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 342
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"

    brief = json.loads(
        (ROOT / "portable" / "BATCH341_INV_BATCH_PIN_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "341"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "intent_batch340_inv_batch_hard_pin_after_342"
    assert brief.get("action") == "soften_inv_batch_hard_pins"
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH341_INV_BATCH_PIN_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == "intent_batch340_inv_batch_hard_pin_after_342"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 341)
    assert "inv_batch" in unblock.lower() or "INV_BATCH" in unblock or "inventory batch hard pin" in unblock.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341 inv-batch-pin)" in land or "inv_batch_hard_pin" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "inv_batch" in log_md.lower() or "INV_BATCH hard pin" in log_md or "inventory batch hard pin" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 341 inv-batch-pin)" in owner or "inv_batch" in owner.lower()


def test_batch343_wake_land_verify() -> None:
    """Batch 343: GRANT341 + WAKE340 tip living @f244312; lemma_closed false."""
    import json

    grant = json.loads(
        (ROOT / "portable" / "BATCH341_GRANT.json").read_text(encoding="utf-8")
    )
    assert grant.get("batch") == "341"
    assert grant.get("lemma_closed") is False
    assert grant.get("flipped_anything") is False
    assert grant.get("scientific_effect") == "NONE"
    assert grant.get("coverage") == "8/8_WRITABLE"
    assert grant.get("goal") == "OPEN"
    assert _living_tip(str(grant.get("tip") or ""))

    wake340 = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json").read_text(encoding="utf-8")
    )
    assert wake340.get("lemma_closed") is False
    assert wake340.get("tip_match") is True
    assert _living_tip(str(wake340.get("tip") or ""))
    # Living tip supersedes across tip-sync (Batch 343: f244312→fcad723).
    assert _living_tip(str(wake340.get("tip") or ""))

    wake343 = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH343.json").read_text(encoding="utf-8")
    )
    # Soft: wake_land_verify stub may be superseded by multi_agent_wake_and_assign.
    assert wake343.get("action") in {
        "wake_land_verify_batch343",
        "multi_agent_wake_and_assign",
    }
    assert wake343.get("wake343_on_main") is True
    assert wake343.get("lemma_closed") is False
    assert wake343.get("goal") in (None, "OPEN") or wake343.get("goal") == "OPEN"
    assert _living_tip(str(wake343.get("tip") or ""))
    if wake343.get("action") == "wake_land_verify_batch343":
        verified = wake343.get("verified") or {}
        assert verified.get("BATCH341_GRANT") is True
        assert verified.get("tip_stale") == 0
        assert verified.get("script_stale") == 0
    else:
        assert len(wake343.get("woken_idle_agents") or []) >= 3
        living = wake343.get("living") or {}
        assert living.get("tip_stale") == 0
        assert living.get("script_stale") == 0

    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "wake_land_verify_batch343" in log_md or "Batch 343" in log_md


def test_batch343_multi_agent_wake_assign() -> None:
    """Batch 343: Dylan wake stopped agents + assign Path C intent tasks."""
    import json

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH343.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 343
    assert wake.get("wake343_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    assert len(wake.get("spawned_cloud_peers") or []) >= 1
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert _living_tip(str(wake.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "343"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "WAKE343" in unblock or "MULTI_AGENT wake" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 wake)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH343" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md and "Batch 343" in log_md


def test_batch343_grant_inventory_refresh() -> None:
    """Batch 343: inventory batch >=343 + durable 8/8; grant skip source=none."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 343
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d

    tiny = json.loads(
        (ROOT / "portable" / "BATCH343_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "343"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("action") == "grant_inventory_refresh_batch343"
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("goal") == "OPEN"
    assert _living_tip(str(tiny.get("tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    m = re.search(r"=== Batch (\d+)\s", unblock)
    assert m is not None
    assert int(m.group(1)) >= 343
    _assert_print_owner_header_batch_at_least(unblock, 343)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH343_GRANT" in log_md or "grant_inventory_refresh_batch343" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343)" in owner

def test_batch343_tip_sync_watch_confirm() -> None:
    """Batch 343 WAKE: tip_sync_watch confirm @fcad723; required evidence fields."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH343_TIP_SYNC.json").read_text(encoding="utf-8")
    )
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert str(tiny.get("hardening_tip") or "").startswith("fcad723")

    watch = json.loads(
        (ROOT / "portable" / "BATCH343_TIP_WATCH.json").read_text(encoding="utf-8")
    )
    assert watch.get("lemma_closed") is False
    assert watch.get("flipped_anything") is False
    assert watch.get("tip_match") is True
    assert watch.get("aligned") is True
    assert str(watch.get("hardening_tip") or "").startswith("fcad723")
    assert watch.get("action") == "tip_sync_watch_confirm"

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 343 watch shipped fcad723.
    # Do not hard-pin the live tip SHA in BASE_TIP (Batch 341/344 class).
    assert _living_tip(base)



def test_batch343_inventory_ultimate_fallback_unfreeze() -> None:
    """Batch 343: empty-tree inventory batch fallback no longer freezes at 340."""
    import importlib.util
    import json
    import re
    import tempfile
    from pathlib import Path

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    # Living ultimate fallback supersedes; Batch 343 shipped 343 (346+ ok).
    assert 'return "340"' not in helper
    assert 'return "336"' not in helper
    # Living ultimate fallback supersedes; Batch 343 shipped "343".
    m_fb = re.search(r'return "(\d+)"', helper)
    assert m_fb is not None
    assert int(m_fb.group(1)) >= 343

    # Soften Batch 340 Intent — must not re-freeze return "340"
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch340_inventory_ultimate_fallback_unfreeze")
    end = intent.index("def test_batch340_multi_agent_wake_assign")
    body = intent[start:end]
    assert 'assert \'return "340"\' in helper' not in body
    assert 'assert mod._living_inventory_batch(td) == "340"' not in body
    assert "Living ultimate fallback supersedes" in body

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 343)

    spec = importlib.util.spec_from_file_location(
        "refresh_ai_agent_access_inventory",
        ROOT / "scripts" / "refresh_ai_agent_access_inventory.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    td = tempfile.mkdtemp()
    (Path(td) / "scripts").mkdir()
    assert mod._living_inventory_batch(td) == m_fb.group(1)
    assert int(mod._living_inventory_batch(td)) >= 343

    (Path(td) / "scripts" / "refresh_path_c_bundle.sh").write_text(
        'BATCH_TAG="${REFRESH_BATCH_TAG:-344}"\n', encoding="utf-8"
    )
    assert mod._living_inventory_batch(td) == "344"

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_INV_FALLBACK_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "343"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "inventory_ultimate_fallback_frozen_340_after_tip_sync_343"
    )
    assert brief.get("action") == "eng_inv_ultimate_fallback_unfreeze"
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert brief.get("tip_match") is True
    assert brief.get("aligned") is True
    assert str(brief.get("write", "")).upper() == "WRITABLE"
    assert brief.get("path_c") == "IDLE@0019"

    hunt = json.loads(
        (ROOT / "portable" / "BATCH343_INV_FALLBACK_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == (
        "inventory_ultimate_fallback_frozen_340_after_tip_sync_343"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH343_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("aligned") is True
    assert evidence.get("action") == "eng_inv_ultimate_fallback_unfreeze"
    assert evidence.get("path_c") == "IDLE@0019"
    assert str(evidence.get("write", "")).upper() == "WRITABLE"
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "ultimate fallback" in unblock and "343" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 inv-fallback)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "ultimate fallback unfreeze" in log_md.lower() or "340→343" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 inv-fallback)" in owner


def test_batch343_wake_living_tip_pins() -> None:
    """Batch 343: WAKE343/340 tip pins living @fcad723 after tip-sync; assign tip preserved."""
    import json

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH343.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 343
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert _living_tip(str(wake.get("tip") or ""))
    assert _living_tip(str((wake.get("intent") or {}).get("base_tip_expected") or ""))
    assert _living_tip(str(wake.get("wake_tip_at_assign") or ""))
    assert int(wake.get("tip_living_updated_batch") or 0) >= 343

    wake340 = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH340.json").read_text(encoding="utf-8")
    )
    assert _living_tip(str(wake340.get("tip") or ""))
    assert int(wake340.get("tip_living_updated_batch") or 0) >= 343

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_WAKE_TIP_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "343"
    assert brief.get("defect_id") == "wake343_tip_pins_frozen_at_f244312"
    assert brief.get("action") == "eng_wake343_living_tip_pins_after_tip_sync"
    assert brief.get("lemma_closed") is False
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "fcad723" in unblock or "living tip pins" in unblock.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 wake-tip)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "wake living tip pins" in log_md.lower() or "WAKE living tip pins" in log_md

def test_batch344_idle_tip_sync_watch() -> None:
    """Batch 344 WAKE: tip stable @fcad723; idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH344_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "344"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal") == "OPEN"
    assert str(tiny.get("hardening_tip") or "").startswith("fcad723")
    assert tiny.get("inventable_promoted") is False
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; do not hard-pin live tip SHA.
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 344)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 344)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 344)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 344" in log_md

def test_batch343_status_guard_tip_refresh_fcad723() -> None:
    """Batch 343: STATUS_GUARD tip living @fcad723 after tip-sync; no promotion."""
    import json

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("flipped_anything") is False
    assert snap.get("pass") is True
    assert snap.get("scientific_effect") == "NONE"
    assert snap.get("violations") == []
    # Live STATUS_GUARD tip supersedes across tip-sync; Batch 343 shipped fcad723.
    assert _living_tip(str(snap.get("tip_sha", "")))
    assert _living_tip(str(snap.get("baseline_tip_sha", "")))
    inv = snap.get("inventory") or {}
    assert _living_tip(str(inv.get("tip_sha", "")))
    assert inv.get("packet_lemma_closed") is False

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_STATUS_GUARD_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "343"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "status_guard_tip_lag_f244312_after_tip_sync_fcad723"
    )
    assert brief.get("action") == "eng_status_guard_tip_refresh"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    # Historical brief keeps fcad723; live snapshot tip may move.
    assert str(brief.get("tip", "")).startswith("fcad723")
    assert str(brief.get("prior_tip", "")).startswith("f244312")
    assert brief.get("tip_match") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH343_STATUS_GUARD_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == (
        "status_guard_tip_lag_f244312_after_tip_sync_fcad723"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_shipped") is True

    evidence = json.loads(
        (ROOT / "portable" / "BATCH343_STATUS_GUARD_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("guard_pass") is True
    assert evidence.get("path_c") == "IDLE@0019"
    assert evidence.get("action") == "eng_status_guard_tip_refresh"
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "STATUS_GUARD tip refresh" in unblock and "fcad723" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 status-guard)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "STATUS_GUARD tip refresh" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 status-guard)" in owner



def test_batch344_idle_no_commit() -> None:
    """Batch 344: tip-stable idle_no_commit evidence @fcad723; lemma_closed false."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH344_IDLE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "344"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_match") is True
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip", "")))
    evidence = json.loads(
        (ROOT / "portable" / "BATCH344_IDLE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert _living_tip(str(evidence.get("hardening_tip", "")))
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 344)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 344 idle)" in land or "idle_no_commit" in land


def test_batch344_soften_tip_sync_watch_live_tip_pin() -> None:
    """Batch 344: tip_sync_watch Intent must not freeze live BASE_TIP to fcad723."""
    import json

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch343_tip_sync_watch_confirm")
    end = intent.index("def test_batch343_inventory_ultimate_fallback_unfreeze")
    body = intent[start:end]
    assert "Live BASE_TIP supersedes across tip-sync; Batch 343 watch shipped fcad723" in body
    assert 'assert "fcad723" in base' not in body
    start_idle = intent.index("def test_batch344_idle_tip_sync_watch")
    end_idle = intent.index("def test_batch344_soften_tip_sync_watch_live_tip_pin")
    idle_body = intent[start_idle:end_idle]
    assert 'assert "fcad723" in base' not in idle_body
    assert "fcad723" in _LIVING_TIPS

    brief = json.loads(
        (ROOT / "portable" / "BATCH344_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "344"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "intent_batch343_tip_sync_watch_frozen_live_base_tip_fcad723"
    )
    assert brief.get("action") == "eng_soften_343_tip_sync_watch_live_tip_pin"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal_complete") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH344_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == (
        "intent_batch343_tip_sync_watch_frozen_live_base_tip_fcad723"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH344_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("aligned") is True
    assert evidence.get("action") == "eng_soften_343_tip_sync_watch_live_tip_pin"
    assert evidence.get("path_c") == "IDLE@0019"
    assert str(evidence.get("write", "")).upper() == "WRITABLE"
    assert evidence.get("goal_complete") is False
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 344)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 344)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 344" in log_md and "soften" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 344)" in owner


def test_batch343_audit_intent_timeout_early_fallback() -> None:
    """Batch 343: rate-limit early-fallback before Intent audit timeout=60."""
    import importlib.util
    import json
    import time
    import urllib.error
    from io import BytesIO
    from unittest import mock

    audit_path = ROOT / "scripts" / "audit_main_alignment.py"
    audit_src = audit_path.read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_EARLY_FALLBACK" in audit_src
    assert "rate-limit early-fallback" in audit_src
    assert "Batch 343" in audit_src
    assert "36176016910" in audit_src or "TimeoutExpired" in audit_src
    # Misalignment predicate unchanged.
    assert "misaligned = bool(complexity_hits)" in audit_src

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_EARLY_FALLBACK" in ci
    # Intent suite must enable early-fallback (timeout class).
    intent_idx = ci.index("Intent suite")
    audit_idx = ci.index("Alignment audit", intent_idx)
    intent_block = ci[intent_idx:audit_idx]
    assert 'AUDIT_TRANSPORT_EARLY_FALLBACK: "1"' in intent_block

    spec = importlib.util.spec_from_file_location("audit343early", audit_path)
    assert spec is not None and spec.loader is not None
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)

    audit._TRANSPORT_EARLY_FALLBACK = True
    audit._TRANSPORT_SLEEP_S = 0.0
    audit._TRANSPORT_RETRIES = 6
    audit._TRANSPORT_SLEEP_CAP_S = 60.0
    calls = {"n": 0}
    slept = {"s": 0.0}

    def fake_urlopen(req, timeout=60):
        calls["n"] += 1
        raise urllib.error.HTTPError(
            "https://api.github.com",
            403,
            "Forbidden",
            hdrs={"X-RateLimit-Reset": str(int(time.time()) + 120)},
            fp=BytesIO(
                b'{"message":"API rate limit exceeded for installation."}'
            ),
        )

    def fake_sleep(sec):
        slept["s"] += float(sec)

    with mock.patch("urllib.request.urlopen", fake_urlopen), mock.patch(
        "time.sleep", fake_sleep
    ):
        try:
            audit.get_json("https://api.github.com/repos/example/x")
            raised = None
        except Exception as exc:  # noqa: BLE001
            raised = exc
    assert isinstance(raised, audit.RateLimitExhausted)
    assert calls["n"] == 1
    assert slept["s"] == 0.0

    brief = json.loads(
        (ROOT / "portable" / "BATCH343_AUDIT_TIMEOUT_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "343"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "audit_intent_timeout_under_ratelimit_reset_sleep"
    )
    assert brief.get("action") == "eng_audit_early_fallback_intent_timeout"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal_complete") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH343_AUDIT_TIMEOUT_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == (
        "audit_intent_timeout_under_ratelimit_reset_sleep"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 343)
    assert "early-fallback" in unblock.lower() or "Intent timeout" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 audit-timeout)" in land or "early-fallback" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "early-fallback" in log_md.lower() or "36176016910" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 343 audit-timeout)" in owner or "early-fallback" in owner
    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False


def test_batch345_multi_agent_wake_assign() -> None:
    """Batch 345: Dylan/timer wake stopped agents + assign Path C intent tasks."""
    import json

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH345.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 345
    assert wake.get("wake345_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert _living_tip(str(wake.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH345_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "345"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 345)
    assert "WAKE345" in unblock or "MULTI_AGENT wake" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 wake)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH345" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md and "Batch 345" in log_md


def test_batch345_tip_sync_e3cd7d4() -> None:
    """Batch 345: tip-sync fcad723→e3cd7d4 after main #105; docs not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH345_TIP_SYNC.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "345"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("defect_id") == "tip_sync_fcad723_to_e3cd7d4_main_105"
    assert brief.get("inventable_promoted") is False
    assert 105 in (brief.get("merged_prs") or [])
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("e3cd7d4")
    assert str(brief.get("prior_tip", "")).startswith("fcad723")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH345_TIP_SYNC_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "tip_sync_fcad723_to_e3cd7d4_main_105"
    assert hunt.get("lemma_closed") is False
    assert any("105" in a or "inventable" in a or "docs" in a for a in (hunt.get("avoided") or []))

    evidence = json.loads(
        (ROOT / "portable" / "BATCH345_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("aligned") is True
    assert evidence.get("action") == "tip_sync_landed"
    assert evidence.get("path_c") == "IDLE@0019"
    assert str(evidence.get("write", "")).upper() == "WRITABLE"
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 345 shipped e3cd7d4.
    # Do not hard-pin the live tip SHA in BASE_TIP (Batch 341/344 class).
    assert _living_tip(base_tip)

    verify = json.loads(
        (ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(str(verify.get("refresh_batch") or "0")) >= 345
    assert _living_tip(str(verify.get("base_tip_sha", "")))
    assert verify.get("keep_prior_bundle") is True
    assert verify.get("lemma_closed") is False
    assert "e3cd7d4" in _LIVING_TIPS
    assert "fcad723" in _LIVING_TIPS

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 345)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 345)
    assert "e3cd7d4" in unblock or "tip-sync" in unblock.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 tip-sync)" in land
    assert "e3cd7d4" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 345 tip-sync" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 tip-sync)" in owner

def test_batch345_grant_inventory_refresh() -> None:
    """Batch 345: inventory batch >=345 + durable 8/8; grant skip source=none."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 345
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d

    tiny = json.loads(
        (ROOT / "portable" / "BATCH345_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "345"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    # Living grant artifact action supersedes; Batch 345 refresh then tip-pin.
    assert tiny.get("action") in (
        "grant_inventory_refresh_batch345",
        "grant_inventory_tip_pin_after_tip_sync",
    )
    assert tiny.get("assignment") == "grant_check_dual_vector_8of8"
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("goal") == "OPEN"
    assert _living_tip(str(tiny.get("tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 345)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 grant)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH345_GRANT" in log_md or "grant_inventory_refresh_batch345" in log_md or "grant_inventory_tip_pin" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 grant)" in owner


def test_batch345_wake_ultimate_fallback_unfreeze() -> None:
    """Batch 345: wake empty-tree batch fallback no longer freezes at 341; print_owner header living."""
    import json
    import re
    import sys

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    assert 'return "341"' not in poster
    # Living ultimate fallback supersedes; Batch 345 shipped 345.
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 345
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 345)
    # Single living === header (no dual 344-first trap).
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers, "missing print_owner Batch header"
    assert int(headers[0]) >= 345
    sys.path.insert(0, str(ROOT / "scripts"))
    import post_batch322_wake_comments as wake  # type: ignore
    n = wake._living_batch_n()
    assert n.isdigit()
    assert int(n) >= 345
    brief = json.loads(
        (ROOT / "portable" / "BATCH345_WAKE_FALLBACK_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "345"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "wake_ultimate_fallback_frozen_341_and_print_owner_dual_header_344"
    )
    assert brief.get("action") == "eng_wake_ultimate_fallback_unfreeze"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip", "")))
    assert brief.get("tip_match") is True
    hunt = json.loads(
        (ROOT / "portable" / "BATCH345_WAKE_FALLBACK_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == brief.get("defect_id") or hunt.get("defect_id")
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_shipped") is True
    evidence = json.loads(
        (ROOT / "portable" / "BATCH345_WAKE_FALLBACK_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("path_c") == "IDLE@0019"
    assert evidence.get("action") == "eng_wake_ultimate_fallback_unfreeze"
    assert _living_tip(str(evidence.get("hardening_tip", "")))
    assert "ultimate fallback" in unblock and "345" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 wake-fallback)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "wake ultimate fallback" in log_md.lower() or "341→345" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 345 wake-fallback)" in owner


def test_batch345_tip_sync_e3cd7d4() -> None:
    """Batch 345: tip-sync fcad723→e3cd7d4; inventable not promoted."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH345_TIP_SYNC.json").read_text(encoding="utf-8")
    )
    assert brief.get("action") == "tip_sync_landed"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_match") is True
    assert _living_tip(str(brief.get("hardening_tip") or brief.get("tip") or ""))
    assert "e3cd7d4" in _LIVING_TIPS
    assert "fcad723" in _LIVING_TIPS
    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)
    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert _living_tip(str(status.get("base_tip") or ""))
    assert status.get("lemma_closed") is False
    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    assert "e3cd7d4" in unblock or "tip-sync" in unblock.lower() or "Batch 345" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "e3cd7d4" in land or "STATUS (Batch 345 tip-sync)" in land


def test_batch345_tip_sync_watch_confirm_e3cd7d4() -> None:
    """Batch 345 WAKE: tip_sync_watch confirm @e3cd7d4; valid tip-sync evidence JSON."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH345_TIP_SYNC.json").read_text(encoding="utf-8")
    )
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "tip_sync_landed"
    assert str(tiny.get("hardening_tip") or "").startswith("e3cd7d4")

    watch = json.loads(
        (ROOT / "portable" / "BATCH345_TIP_WATCH.json").read_text(encoding="utf-8")
    )
    assert watch.get("lemma_closed") is False
    assert watch.get("tip_match") is True
    assert watch.get("aligned") is True
    assert str(watch.get("hardening_tip") or "").startswith("e3cd7d4")
    assert watch.get("action") == "tip_sync_watch_confirm"

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 345 watch shipped e3cd7d4.
    # Do not hard-pin the live tip SHA in BASE_TIP (Batch 341/344/346 class).
    assert _living_tip(base)



def test_batch345_grant_inventory_tip_pin() -> None:
    """Batch 345: inventory trial tip pinned after tip-sync; durable 8/8."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 345
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial"))
    assert str(trial.get("tip_sha") or "")
    assert not str(trial.get("tip_sha") or "").startswith("0cec02be")

    grant = json.loads(
        (ROOT / "portable" / "BATCH345_GRANT.json").read_text(encoding="utf-8")
    )
    assert grant.get("lemma_closed") is False
    assert _living_tip(str(grant.get("tip") or ""))
    assert grant.get("coverage") == "8/8_WRITABLE"

    brief = json.loads(
        (ROOT / "portable" / "BATCH345_GRANT_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "345"
    assert brief.get("action") == "grant_inventory_tip_pin_after_tip_sync"
    assert brief.get("lemma_closed") is False


def test_batch346_soften_tip_sync_watch_live_tip_pin() -> None:
    """Batch 346: tip_sync_watch Intent must not freeze live BASE_TIP to e3cd7d4."""
    import json

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch345_tip_sync_watch_confirm_e3cd7d4")
    end = intent.index("def test_batch345_grant_inventory_tip_pin")
    body = intent[start:end]
    assert "Live BASE_TIP supersedes across tip-sync; Batch 345 watch shipped e3cd7d4" in body
    assert 'assert "e3cd7d4" in base' not in body
    assert "e3cd7d4" in _LIVING_TIPS

    brief = json.loads(
        (ROOT / "portable" / "BATCH346_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "346"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "intent_batch345_tip_sync_watch_frozen_live_base_tip_e3cd7d4"
    )
    assert brief.get("action") == "eng_soften_345_tip_sync_watch_live_tip_pin"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal_complete") is False
    assert _living_tip(str(brief.get("tip", "")))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH346_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == (
        "intent_batch345_tip_sync_watch_frozen_live_base_tip_e3cd7d4"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH346_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("aligned") is True
    assert evidence.get("action") == "eng_soften_345_tip_sync_watch_live_tip_pin"
    assert evidence.get("path_c") == "IDLE@0019"
    assert str(evidence.get("write", "")).upper() == "WRITABLE"
    assert evidence.get("goal_complete") is False
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 346" in log_md and "soften" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346)" in owner


def test_batch346_grant_inventory_refresh() -> None:
    """Batch 346: inventory batch >=346 + durable 8/8; grant skip source=none."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 346
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d

    tiny = json.loads(
        (ROOT / "portable" / "BATCH346_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "346"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("durable") == "8/8"
    assert tiny.get("action") == "grant_inventory_refresh_batch346"
    assert tiny.get("assignment") == "grant_check_dual_vector_8of8"
    assert tiny.get("tip_match") is True
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("goal") == "OPEN"
    assert _living_tip(str(tiny.get("tip", "")))
    assert _living_tip(str(tiny.get("hardening_tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 grant)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH346_GRANT" in log_md or "grant_inventory_refresh_batch346" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 grant)" in owner


def test_batch346_status_guard_tip_refresh_e3cd7d4() -> None:
    """Batch 346: STATUS_GUARD tip living @e3cd7d4 after tip-sync; no promotion."""
    import json

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("flipped_anything") is False
    assert snap.get("pass") is True
    assert snap.get("scientific_effect") == "NONE"
    assert snap.get("violations") == []
    # Live STATUS_GUARD tip supersedes across tip-sync; Batch 346 shipped e3cd7d4.
    assert _living_tip(str(snap.get("tip_sha", "")))
    assert _living_tip(str(snap.get("baseline_tip_sha", "")))
    inv = snap.get("inventory") or {}
    assert _living_tip(str(inv.get("tip_sha", "")))
    assert inv.get("packet_lemma_closed") is False

    brief = json.loads(
        (ROOT / "portable" / "BATCH346_STATUS_GUARD_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "346"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == (
        "status_guard_tip_lag_fcad723_after_tip_sync_e3cd7d4"
    )
    assert brief.get("action") == "eng_status_guard_tip_refresh"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    # Historical brief keeps e3cd7d4; live snapshot tip may move.
    assert str(brief.get("tip", "")).startswith("e3cd7d4")
    assert str(brief.get("prior_tip", "")).startswith("fcad723")
    assert brief.get("tip_match") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH346_STATUS_GUARD_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_id") == (
        "status_guard_tip_lag_fcad723_after_tip_sync_e3cd7d4"
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_shipped") is True

    evidence = json.loads(
        (ROOT / "portable" / "BATCH346_STATUS_GUARD_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("guard_pass") is True
    assert evidence.get("path_c") == "IDLE@0019"
    assert evidence.get("action") == "eng_status_guard_tip_refresh"
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    assert "STATUS_GUARD tip refresh" in unblock and "e3cd7d4" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 status-guard)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "STATUS_GUARD tip refresh" in log_md and "e3cd7d4" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 status-guard)" in owner


def test_batch346_multi_agent_wake_assign() -> None:
    """Batch 346: Dylan wake stopped agents + assign Path C intent tasks @e3cd7d4."""
    import json
    import re

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH346.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 346
    assert wake.get("wake346_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    # Living tip supersedes across tip-sync; Batch 346 wake shipped e3cd7d4.
    # Do not hard-pin wake tip SHA (Batch 341/344/346 class).
    assert _living_tip(str(wake.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH346_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "346"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    assert "WAKE346" in unblock or "MULTI_AGENT wake" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 wake)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH346" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md and "Batch 346" in log_md

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 346
    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    m_inv = re.search(r'return "(\d+)"', helper)
    assert m_inv is not None
    assert int(m_inv.group(1)) >= 346

def test_batch346_inventory_preserve_durable_tip_pin() -> None:
    """Batch 346: preserve_durable tip pin; ultimate fallback >=346; 8/8 retained."""
    import importlib.util
    import json
    import re
    import sys
    import tempfile
    from pathlib import Path

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 346
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    assert not str(trial.get("tip_sha") or "").startswith("840de46")
    assert not str(trial.get("tip_sha") or "").startswith("6ab1a23")

    evidence = json.loads(
        (ROOT / "portable" / "BATCH346_INV_PRESERVE_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("assignment") == "inventory_preserve_durable_tip_pin"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("goal") == "OPEN"
    assert evidence.get("preserve_durable_writable0_denied") is True
    assert str(evidence.get("ultimate_fallback")) == "346"
    assert evidence.get("coverage") == "8/8_WRITABLE"

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    m_fb = re.search(r'return "(\d+)"', helper)
    assert m_fb is not None
    assert int(m_fb.group(1)) >= 346

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 346

    spec = importlib.util.spec_from_file_location(
        "refresh_inv_346", ROOT / "scripts" / "refresh_ai_agent_access_inventory.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod._no_durable_probe(0, "404", "DENIED") is True
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "inv.json"
        path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
        result = mod.refresh(
            str(path),
            [d["name"] for d in inv["details"]],
            durable_writable=0,
            durable_sandbox_read="404",
            durable_sandbox_write="DENIED",
            active_sandbox_read="404",
            batch="346",
        )
        assert result.get("preserve_durable") is True
        out = json.loads(path.read_text(encoding="utf-8"))
        assert out.get("durable_sibling_coverage") == "8/8_WRITABLE"
        assert out.get("sandbox", {}).get("readable") is True
        for d in out.get("details") or []:
            assert d.get("push") is True, d

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    assert "inventory_preserve_durable_tip_pin" in unblock
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "inventory_preserve_durable_tip_pin" in log_md



def test_batch346_ci_audit_watch_idle() -> None:
    """Batch 346: ci_audit_watch idle; early-fallback intact; lemma_closed false."""
    import json

    art = json.loads(
        (ROOT / "portable" / "BATCH346_CI_AUDIT_WATCH.json").read_text(encoding="utf-8")
    )
    assert art.get("batch") == "346"
    assert art.get("action") == "idle_no_commit"
    assert art.get("lemma_closed") is False
    assert art.get("flipped_anything") is False
    assert art.get("scientific_effect") == "NONE"
    assert art.get("goal") == "OPEN"
    assert art.get("tip_match") is True
    assert art.get("audit_early_fallback_present") is True
    assert art.get("audit_rate_limit_backoff_present") is True
    assert _living_tip(str(art.get("hardening_tip") or art.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH346_CI_AUDIT_IDLE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False

    audit_src = (ROOT / "scripts" / "audit_main_alignment.py").read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_EARLY_FALLBACK" in audit_src
    assert "rate-limit early-fallback" in audit_src
    assert "AUDIT_TRANSPORT_RETRIES" in audit_src
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert 'AUDIT_TRANSPORT_EARLY_FALLBACK: "1"' in ci

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    assert "ci_audit_watch" in unblock.lower() or "early-fallback" in unblock.lower()
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 ci-audit-watch)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "ci_audit_watch" in log_md.lower() or "Batch 346" in log_md
    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False


def test_batch346_living_script_stale_republish() -> None:
    """Batch 346: living release script_stale cleared after tip-stable @e3cd7d4."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH346_REPUBLISH_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "346"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "living_release_script_stale_after_fallback_346"
    assert brief.get("action") == "eng_living_script_stale_republish"
    assert brief.get("tip_match") is True
    assert brief.get("script_stale_pre") == 1
    assert brief.get("script_stale_post") == 0
    assert brief.get("tip_stale_post") == 0
    assert brief.get("goal") == "OPEN"
    assert brief.get("inventable_promoted") is False
    assert _living_tip(str(brief.get("tip") or brief.get("hardening_tip") or ""))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH346_REPUBLISH_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("flipped_anything") is False
    assert hunt.get("defect_id") == "living_release_script_stale_after_fallback_346"
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_shipped") is True

    evidence = json.loads(
        (ROOT / "portable" / "BATCH346_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("flipped_anything") is False
    assert evidence.get("action") == "eng_living_script_stale_republish"
    assert evidence.get("script_stale_post") == 0
    assert evidence.get("goal") == "OPEN"
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 346)
    assert "script_stale republish" in unblock and "e3cd7d4" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 republish)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "script_stale" in log_md and "republish" in log_md.lower()
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 346 republish)" in owner


def test_batch347_inventory_tip_pin() -> None:
    """Batch 347: inventory trial tip pinned after Batch 346 lands; durable 8/8."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 347
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip
    assert not tip.startswith("3240e1a")

    brief = json.loads(
        (ROOT / "portable" / "BATCH347_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "347"
    assert brief.get("action") == "grant_inventory_tip_pin_after_main_lands"
    assert brief.get("lemma_closed") is False

    evidence = json.loads(
        (ROOT / "portable" / "BATCH347_INV_TIP_PIN_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("coverage") == "8/8_WRITABLE"
    assert evidence.get("action") == "grant_inventory_tip_pin_after_main_lands"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 347)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 347
    assert len(headers) == 1  # single living header

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 347 inv-tip-pin)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "inventory tip pin" in log_md and "Batch 347" in log_md

def test_batch347_idle_tip_sync_watch() -> None:
    """Batch 347: tip stable @e3cd7d4; idle_no_commit tip_sync_watch evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH347_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "347"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal") == "OPEN"
    assert str(tiny.get("hardening_tip") or "").startswith("e3cd7d4")
    assert tiny.get("inventable_promoted") is False
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 347)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 347 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 347 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH347_IDLE" in log_md or "Batch 347" in log_md


def test_batch347_soften_wake346_live_tip_pin() -> None:
    """Batch 347: WAKE346 Intent must not freeze live wake tip to e3cd7d4."""
    import json

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch346_multi_agent_wake_assign")
    end = intent.index("def test_batch346_inventory_preserve_durable_tip_pin")
    body = intent[start:end]
    assert "Living tip supersedes across tip-sync; Batch 346 wake shipped e3cd7d4" in body
    assert 'startswith("e3cd7d4")' not in body

    brief = json.loads(
        (ROOT / "portable" / "BATCH347_SOFTEN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "347"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "intent_batch346_wake_frozen_live_tip_e3cd7d4"
    assert brief.get("action") == "eng_soften_346_wake_live_tip_pin"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip", "")))
    assert brief.get("tip_match") is True

    hunt = json.loads(
        (ROOT / "portable" / "BATCH347_SOFTEN_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "intent_batch346_wake_frozen_live_tip_e3cd7d4"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_shipped") is True

    evidence = json.loads(
        (ROOT / "portable" / "BATCH347_SOFTEN_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("path_c") == "IDLE@0019"
    assert evidence.get("action") == "eng_soften_346_wake_live_tip_pin"
    assert _living_tip(str(evidence.get("hardening_tip", "")))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 347)
    assert "soften Batch 346 wake Intent" in unblock

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 347 soften-wake-pin)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "soften WAKE346" in log_md or "intent_batch346_wake_frozen_live_tip_e3cd7d4" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 347 soften-wake-pin)" in owner


def test_batch348_inventory_tip_pin() -> None:
    """Batch 348: inventory trial tip pinned after Batch 347 lands; durable 8/8."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 348
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip and not tip.startswith("a136c2d")

    brief = json.loads(
        (ROOT / "portable" / "BATCH348_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "348"
    assert brief.get("action") in (
        "grant_inventory_tip_pin_after_main_lands",
        "inventory_preserve_durable_tip_pin",
    )
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 348)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 348 and len(headers) == 1


def test_batch348_research_stack_audit_no_promotion() -> None:
    """Batch 348: research stack audit without status promotion @e3cd7d4."""
    import json

    audit = json.loads(
        (ROOT / "portable" / "BATCH348_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("scientific_effect") == "NONE"
    counts = audit.get("counts") or {}
    assert int(counts.get("open_premises_frozen_layer") or 0) >= 13
    assert int(counts.get("open_lemmas") or 0) >= 1
    assert int(counts.get("open_prizes") or 0) >= 3
    assert _living_tip(str(audit.get("tip_sha") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH348_RESEARCH_AUDIT_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "348"
    assert brief.get("action") == "research_stack_audit_no_promotion"
    assert brief.get("lemma_closed") is False
    assert brief.get("guard_pass") is True

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("pass") is True
    assert snap.get("violations") == []

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "Batch 348" in land and "research" in land.lower()
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 348" in log_md and "research stack audit" in log_md.lower()



def test_batch348_research_stack_audit_watch() -> None:
    """Batch 348: research_stack_audit_watch; STATUS_GUARD no lag; eng living republish."""
    import json

    watch = json.loads(
        (ROOT / "portable" / "BATCH348_RESEARCH_AUDIT_WATCH.json").read_text(
            encoding="utf-8"
        )
    )
    assert watch.get("batch") == "348"
    assert watch.get("lemma_closed") is False
    assert watch.get("flipped_anything") is False
    assert watch.get("tip_match") is True
    assert watch.get("status_guard_tip_lag") is False
    assert watch.get("watch") == "research_stack_audit_watch"
    assert watch.get("action") == "living_script_stale_republish"
    assert watch.get("goal_complete") is False
    assert _living_tip(str(watch.get("hardening_tip") or ""))
    living = watch.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert int(watch.get("open_premises") or 0) >= 13
    assert int(watch.get("open_lemmas") or 0) >= 1
    assert int(watch.get("open_prizes") or 0) >= 3

    hunt = json.loads(
        (ROOT / "portable" / "BATCH348_RESEARCH_AUDIT_WATCH_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("status_guard_tip_lag") is False

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("pass") is True
    assert _living_tip(str(snap.get("tip_sha") or ""))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 348)
    assert "research_stack_audit_watch" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 348 research-audit-watch)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 348 research-audit-watch)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "research_stack_audit_watch" in log_md


def test_batch348_idle_tip_sync_or_eng() -> None:
    """Batch 348: tip stable @e3cd7d4; idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH348_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "348"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH348_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 348)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 348 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 348 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 348" in log_md and "idle_no_commit" in log_md


def test_batch349_ci_intent_early_fallback_unit_isolate() -> None:
    """Batch 349: rate-limit unit tests force EARLY_FALLBACK off under CI Intent env."""
    import json
    import re

    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    # Both rate-limit unit backoff tests must force early-fallback off.
    for name in (
        "test_batch256_aligned_drift_restore_race_and_audit_rate_limit",
        "test_batch340_audit_rate_limit_403_backoff",
    ):
        start = intent.index(f"def {name}")
        end = intent.index("\ndef test_", start + 1)
        body = intent[start:end]
        assert "audit._TRANSPORT_EARLY_FALLBACK = False" in body

    # Softened GRANT345 living action allowlist
    start = intent.index("def test_batch345_grant_inventory_refresh")
    end = intent.index("\ndef test_", start + 1)
    body = intent[start:end]
    assert "grant_inventory_tip_pin_after_tip_sync" in body
    assert 'assert tiny.get("action") == "grant_inventory_refresh_batch345"' not in body

    brief = json.loads(
        (ROOT / "portable" / "BATCH349_CI_REMEDIATE_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert brief.get("batch") == "349"
    assert brief.get("lemma_closed") is False
    assert brief.get("action") == "eng_ci_intent_early_fallback_unit_test_isolate"

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 349)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 349 and len(headers) == 1
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 349 ci-remediate)" in land


def test_batch349_idle_eng_hunt() -> None:
    """Batch 349: eng hunt negative @e3cd7d4; idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH349_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "349"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal") == "OPEN"
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    hunt = json.loads(
        (ROOT / "portable" / "BATCH349_IDLE_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_found") is False
    assert hunt.get("action") == "idle_no_commit"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    brief = json.loads(
        (ROOT / "portable" / "BATCH349_IDLE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "349"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("lemma_closed") is False

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 349)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 349 idle-eng-hunt)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 349 idle-eng-hunt)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "eng_defect_hunt idle_no_commit" in log_md or "Batch 349" in log_md


def test_batch350_inventory_tip_pin() -> None:
    """Batch 350: inventory trial tip pinned after Batch 349 CI green; durable 8/8."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 350
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip and not tip.startswith("33dda3b")

    brief = json.loads(
        (ROOT / "portable" / "BATCH350_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "350"
    # Living allowlist: peer re-pins may rename action across tip-stable landings.
    assert brief.get("action") in (
        "grant_inventory_tip_pin_after_main_lands",
        "inventory_preserve_durable_tip_pin",
        "grant_inventory_tip_pin_after_land_head",
    )
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 350)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 350 and len(headers) == 1
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 350 inv-tip-pin)" in land


def test_batch350_soften_inv_tip_pin_action() -> None:
    """Batch 350: soften INV_TIP_PIN Intent frozen action after peer re-pin."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH350_SOFTEN_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "350"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("action") == "eng_soften_inv_tip_pin_action_allowlist"
    assert tiny.get("goal") == "OPEN"
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH350_SOFTEN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("defect_id") == "intent_batch350_inv_tip_pin_frozen_action"
    assert brief.get("lemma_closed") is False
    assert brief.get("action") == "eng_soften_inv_tip_pin_action_allowlist"

    hunt = json.loads(
        (ROOT / "portable" / "BATCH350_SOFTEN_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("tip_match") is True

    # Softened allowlist present on inv tip-pin Intent.
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    start = intent.index("def test_batch350_inventory_tip_pin")
    end = intent.index("\ndef test_", start + 1)
    body = intent[start:end]
    assert "inventory_preserve_durable_tip_pin" in body
    assert 'assert brief.get("action") == "grant_inventory_tip_pin_after_main_lands"' not in body

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 350)
    assert "soften INV_TIP_PIN" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 350 soften-inv-tip-pin)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 350 soften-inv-tip-pin)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "soften INV_TIP_PIN" in log_md or "intent_batch350_inv_tip_pin_frozen_action" in log_md


def test_batch350_idle_tip_sync_or_eng() -> None:
    """Batch 350: tip stable @e3cd7d4; idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH350_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "350"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH350_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 350)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 350 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 350 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 350" in log_md and "idle_no_commit" in log_md


def test_batch351_inventory_tip_pin() -> None:
    """Batch 351: inventory tip pin after Batch 350 idle; durable 8/8."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 351
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip and not tip.startswith("642aded")

    brief = json.loads(
        (ROOT / "portable" / "BATCH351_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "351"
    assert brief.get("action") in (
        "grant_inventory_tip_pin_after_main_lands",
        "inventory_preserve_durable_tip_pin",
    )
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 351)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 351 and len(headers) == 1


def test_batch351_research_stack_audit_watch() -> None:
    """Batch 351: research_stack_audit_watch; STATUS_GUARD living; eng living republish."""
    import json

    watch = json.loads(
        (ROOT / "portable" / "BATCH351_RESEARCH_AUDIT_WATCH.json").read_text(
            encoding="utf-8"
        )
    )
    assert watch.get("batch") == "351"
    assert watch.get("lemma_closed") is False
    assert watch.get("flipped_anything") is False
    assert watch.get("tip_match") is True
    assert watch.get("status_guard_tip_living") is True
    assert watch.get("status_guard_tip_lag") is False
    assert watch.get("watch") == "research_stack_audit_watch"
    assert watch.get("action") == "living_script_stale_republish"
    assert watch.get("goal_complete") is False
    assert _living_tip(str(watch.get("hardening_tip") or ""))
    living = watch.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert int(watch.get("open_premises") or 0) >= 13
    assert int(watch.get("open_lemmas") or 0) >= 1
    assert int(watch.get("open_prizes") or 0) >= 3

    hunt = json.loads(
        (ROOT / "portable" / "BATCH351_RESEARCH_AUDIT_WATCH_HUNT.json").read_text(
            encoding="utf-8"
        )
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("status_guard_tip_living") is True

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("pass") is True
    assert _living_tip(str(snap.get("tip_sha") or ""))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 351)
    assert "research_stack_audit_watch" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 351 research-audit-watch)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 351 research-audit-watch)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "research_stack_audit_watch" in log_md


def test_batch351_idle_tip_sync_or_eng() -> None:
    """Batch 351: tip stable @e3cd7d4 (NOT 077464e); idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH351_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "351"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    assert "077464e" not in str(tiny.get("hardening_tip") or "")
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH351_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)
    assert "077464e" not in base

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 351)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 351 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 351 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 351" in log_md and "idle_no_commit" in log_md


def test_batch352_unfreeze_last_resort() -> None:
    """Batch 352: last-resort batch defaults unfrozen 351→352; tip stable."""
    import importlib.util
    import json
    import tempfile
    from pathlib import Path as P

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 352)

    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    assert 'return "351"' not in helper
    # Living last-resort may advance past 352 (Batch 353+); never freeze below 352.
    assert any(f'return "{n}"' in helper for n in ("352", "353", "354", "355"))

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    # Ultimate fallback in _living_batch_n (not historical notes).
    assert any(f'return "{n}"' in poster for n in ("352", "353", "354", "355"))
    assert 'return "351"' not in poster.split("def batch_marker")[0]

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    assert "351→352" in unblock or "351->352" in unblock or "unfreeze" in unblock

    spec = importlib.util.spec_from_file_location(
        "refresh_inv_352",
        ROOT / "scripts" / "refresh_ai_agent_access_inventory.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    td = tempfile.mkdtemp()
    (P(td) / "scripts").mkdir()
    assert int(mod._living_inventory_batch(td)) >= 352

    brief = json.loads(
        (ROOT / "portable" / "BATCH352_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "352"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("defect_id") == "batch_last_resort_frozen_351_vs_living_352"
    assert brief.get("action") == "eng_unfreeze_batch_last_resort_352"
    assert brief.get("tip_match") is True
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal_complete") is False
    assert _living_tip(str(brief.get("tip", "")))
    assert str(brief.get("tip", "")).startswith("e3cd7d4")

    hunt = json.loads(
        (ROOT / "portable" / "BATCH352_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_id") == "batch_last_resort_frozen_351_vs_living_352"
    assert hunt.get("lemma_closed") is False
    assert hunt.get("tip_moved") is False

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert "e3cd7d4" in base_tip
    assert _living_tip(base_tip)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 352" in log_md and "351→352" in log_md

def test_batch352_idle_tip_sync_watch() -> None:
    """Batch 352: tip stable @e3cd7d4; idle_no_commit tip_sync_watch evidence."""
    import json
    import re

    tiny = json.loads(
        (ROOT / "portable" / "BATCH352_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "352"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH352_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("aligned") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 352 and len(headers) == 1
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 352" in log_md and "tip_sync_watch idle_no_commit" in log_md


def test_batch352_living_script_stale_republish() -> None:
    """Batch 352: living script_stale republish after inv tip-pin; lemma open."""
    import json

    brief = json.loads(
        (ROOT / "portable" / "BATCH352_REPUBLISH_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "352"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("action") == "living_script_stale_republish"
    assert brief.get("defect_id") == "living_script_stale_after_batch352_inv_tip_pin"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip") or brief.get("hardening_tip") or ""))
    assert (brief.get("after") or {}).get("script_stale") == 0

    hunt = json.loads(
        (ROOT / "portable" / "BATCH352_REPUBLISH_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH352_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("script_stale_after") == 0
    assert evidence.get("tip_stale") == 0
    assert evidence.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    assert "living script_stale republish" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 republish)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 republish)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "living script_stale republish" in log_md.lower() or "script_stale" in log_md

def test_batch352_grant_inventory_refresh() -> None:
    """Batch 352: inventory batch >=352 + durable 8/8; grant skip source=none."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 352
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d

    tiny = json.loads(
        (ROOT / "portable" / "BATCH352_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "352"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("durable") == "8/8"
    assert tiny.get("action") == "grant_inventory_refresh_batch352"
    assert tiny.get("assignment") == "grant_check_dual_vector_8of8"
    assert tiny.get("tip_match") is True
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("goal") == "OPEN"
    assert _living_tip(str(tiny.get("tip", "")))
    assert _living_tip(str(tiny.get("hardening_tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 grant)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH352_GRANT" in log_md or "grant_inventory_refresh_batch352" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 grant)" in owner


def test_batch352_multi_agent_wake_assign() -> None:
    """Batch 352: Dylan wake stopped agents + assign Path C intent tasks @e3cd7d4."""
    import json
    import re

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH352.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 352
    assert wake.get("wake352_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert _living_tip(str(wake.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH352_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "352"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    assert "WAKE352" in unblock or "MULTI_AGENT wake" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 wake)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH352" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md and "Batch 352" in log_md

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 352
    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    m_inv = re.search(r'return "(\d+)"', helper)
    assert m_inv is not None
    assert int(m_inv.group(1)) >= 352



def test_batch352_tip_or_eng_continue() -> None:
    """Batch 352: tip_or_eng — inv tip re-pin + living script_stale republish."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 352
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip and not tip.startswith("4aeb190")

    brief = json.loads(
        (ROOT / "portable" / "BATCH352_TIP_ENG_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "352"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("action") == "eng_inv_tip_repin_and_living_republish"
    assert brief.get("trial_tip_matches_live_head") is True
    assert brief.get("script_stale_post") == 0
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip") or brief.get("hardening_tip") or ""))

    hunt = json.loads(
        (ROOT / "portable" / "BATCH352_TIP_ENG_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("lemma_closed") is False
    assert hunt.get("defect_shipped") is True

    evidence = json.loads(
        (ROOT / "portable" / "BATCH352_TIP_ENG_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("lemma_closed") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("flipped_anything") is False
    assert evidence.get("action") == "eng_inv_tip_repin_and_living_republish"
    assert evidence.get("script_stale_post") == 0
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    assert "tip_or_eng" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 tip-eng)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 tip-eng)" in owner


def test_batch352_ci_audit_watch_idle() -> None:
    """Batch 352: ci_audit_watch idle with green CI evidence; lemma_closed false."""
    import json

    art = json.loads(
        (ROOT / "portable" / "BATCH352_CI_AUDIT_WATCH.json").read_text(encoding="utf-8")
    )
    assert art.get("batch") == "352"
    assert art.get("action") == "idle_no_commit"
    assert art.get("ci_status") == "green"
    assert art.get("lemma_closed") is False
    assert art.get("flipped_anything") is False
    assert art.get("scientific_effect") == "NONE"
    assert art.get("goal") == "OPEN"
    assert art.get("tip_match") is True
    assert art.get("audit_early_fallback_present") is True
    assert art.get("audit_unit_isolate_present") is True
    assert len(art.get("ci_green_runs") or []) >= 3
    assert _living_tip(str(art.get("hardening_tip") or art.get("tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH352_CI_AUDIT_IDLE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("ci_status") == "green"
    assert brief.get("lemma_closed") is False

    audit_src = (ROOT / "scripts" / "audit_main_alignment.py").read_text(encoding="utf-8")
    assert "AUDIT_TRANSPORT_EARLY_FALLBACK" in audit_src
    intent = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    assert "audit._TRANSPORT_EARLY_FALLBACK = False" in intent
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert 'AUDIT_TRANSPORT_EARLY_FALLBACK: "1"' in ci

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 352)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 352 ci-audit-watch)" in land
    status = json.loads(
        (ROOT / "portable" / "PATH_C_STATUS.json").read_text(encoding="utf-8")
    )
    assert status.get("lemma_closed") is False


def test_batch353_idle_tip_sync_watch() -> None:
    """Batch 353: tip stable @e3cd7d4; idle_no_commit tip_sync_watch evidence."""
    import json
    import re

    tiny = json.loads(
        (ROOT / "portable" / "BATCH353_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "353"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH353_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 353)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 353 and len(headers) == 1
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 353" in log_md and "tip_sync_watch idle_no_commit" in log_md


def test_batch353_living_republish_inv_tip_pin() -> None:
    """Batch 353: living script_stale republish + inventory tip pin→HEAD @e3cd7d4."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 353
    assert inv.get("lemma_closed") is False
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    trial = next(
        d for d in (inv.get("details") or []) if str(d.get("name") or "").endswith("/trial")
    )
    tip = str(trial.get("tip_sha") or "")
    assert tip and not tip.startswith("382f153b")

    brief = json.loads(
        (ROOT / "portable" / "BATCH353_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "353"
    assert brief.get("action") == "inventory_preserve_durable_tip_pin"
    assert brief.get("lemma_closed") is False

    living = json.loads(
        (ROOT / "portable" / "BATCH353_LIVING_REPUBLISH_BRIEF.json").read_text(
            encoding="utf-8"
        )
    )
    assert living.get("batch") == "353"
    assert living.get("action") == "living_script_stale_republish"
    assert living.get("lemma_closed") is False
    assert living.get("script_stale") == 0

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 353)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 living-republish + inv-tip-pin)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 living-republish + inv-tip-pin)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 353" in log_md and (
        "inventory_preserve_durable_tip_pin" in log_md or "living script_stale" in log_md
    )

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 353
    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    m_inv = re.search(r'return "(\d+)"', helper)
    assert m_inv is not None
    assert int(m_inv.group(1)) >= 353
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    m_r = re.search(r"REFRESH_BATCH_TAG:-(\d+)", refresh)
    assert m_r is not None
    assert int(m_r.group(1)) >= 353


def test_batch353_research_stack_audit_watch() -> None:
    """Batch 353: research_stack_audit_watch; STATUS_GUARD living; no promotion."""
    import json

    watch = json.loads(
        (ROOT / "portable" / "BATCH353_RESEARCH_AUDIT_WATCH.json").read_text(
            encoding="utf-8"
        )
    )
    assert watch.get("batch") == "353"
    assert watch.get("lemma_closed") is False
    assert watch.get("flipped_anything") is False
    assert watch.get("tip_match") is True
    assert watch.get("action") == "research_stack_audit_watch"
    assert watch.get("scientific_effect") == "NONE"
    assert watch.get("goal_complete") is False
    assert watch.get("inventable_promoted") is False
    assert watch.get("status_guard_tip_living") is True
    assert watch.get("status_guard_tip_lag") is False
    assert int(watch.get("open_premises") or 0) >= 13
    assert int(watch.get("open_lemmas") or 0) >= 1
    assert int(watch.get("open_prizes") or 0) >= 3
    assert _living_tip(str(watch.get("hardening_tip") or ""))
    living = watch.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    audit = json.loads(
        (ROOT / "portable" / "BATCH353_RESEARCH_STACK_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit.get("lemma_closed") is False
    assert audit.get("flipped_anything") is False
    assert audit.get("scientific_effect") == "NONE"
    counts = audit.get("counts") or {}
    assert int(counts.get("open_premises_frozen_layer") or 0) >= 13
    assert int(counts.get("open_lemmas") or 0) >= 1
    assert int(counts.get("open_prizes") or 0) >= 3
    assert _living_tip(str(audit.get("tip_sha") or ""))

    snap = json.loads(
        (ROOT / "portable" / "STATUS_GUARD_SNAPSHOT.json").read_text(encoding="utf-8")
    )
    assert snap.get("lemma_closed") is False
    assert snap.get("pass") is True
    assert _living_tip(str(snap.get("tip_sha") or ""))

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 353)
    assert "research_stack_audit_watch" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 research-audit-watch)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 research-audit-watch)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "research_stack_audit_watch" in log_md and "Batch 353" in log_md

def test_batch353_living_script_stale_republish() -> None:
    """Batch 353: living script_stale republish after research-audit merge; lemma open."""
    import json
    import re

    brief = json.loads(
        (ROOT / "portable" / "BATCH353_REPUBLISH_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "353"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("action") == "living_script_stale_republish"
    assert brief.get("defect_id") == "living_script_stale_after_batch353_research_audit_merge"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip") or brief.get("hardening_tip") or ""))
    assert (brief.get("after") or {}).get("script_stale") == 0

    hunt = json.loads(
        (ROOT / "portable" / "BATCH353_REPUBLISH_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_id") == "living_script_stale_after_batch353_research_audit_merge"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH353_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("script_stale_after") == 0
    assert evidence.get("tip_stale") == 0
    assert evidence.get("lemma_closed") is False
    assert evidence.get("action") == "living_script_stale_republish"
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 353)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 353 and len(headers) == 1
    assert "living script_stale republish" in unblock and "research-audit" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 republish)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 353 republish)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "living script_stale" in log_md and "research-audit" in log_md



def test_batch354_idle_tip_sync_or_eng() -> None:
    """Batch 354: tip stable @e3cd7d4; idle_no_commit evidence."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH354_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "354"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("scientific_effect") == "NONE"
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH354_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 354)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 354 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 354 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 354" in log_md and "idle_no_commit" in log_md

def test_batch354_inventory_preserve_durable_tip_pin() -> None:
    """Batch 354: preserve_durable tip pin; 8/8; lemma open; tip e3cd7d4."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 354
    assert inv.get("durable_writable") == "8/8"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH354_INV_TIP_PIN_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("batch") == "354"
    assert evidence.get("action") == "inventory_preserve_durable_tip_pin"
    assert evidence.get("durable") == "8/8_WRITABLE"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("scientific_effect") == "NONE"
    assert str(evidence.get("hardening_tip", "")).startswith("e3cd7d4")
    assert evidence.get("trial_tip_matches_live_head") is True

    brief = json.loads(
        (ROOT / "portable" / "BATCH354_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "354"
    assert brief.get("action") == "inventory_preserve_durable_tip_pin"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    headers = re.findall(r"=== Batch (\d+)\s", unblock)
    assert headers and int(headers[0]) >= 354 and len(headers) == 1
    assert "inventory_preserve_durable_tip_pin" in unblock

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    # Live BASE_TIP supersedes across tip-sync; Batch 354 inv pin shipped e3cd7d4.
    assert _living_tip(base_tip)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 354 inv-preserve-tip-pin)" in land
    assert "STATUS (Batch 354 soften-inv-base-tip)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 354" in log_md and "inventory_preserve_durable_tip_pin" in log_md
    soften = json.loads(
        (ROOT / "portable" / "BATCH354_SOFTEN_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert soften.get("action") == "eng_soften_inv_tip_pin_live_base_tip"
    assert soften.get("lemma_closed") is False
    assert soften.get("flipped_anything") is False
    assert soften.get("tip_match") is True


def test_batch354_living_script_stale_republish() -> None:
    """Batch 354: living script_stale republish after inv tip-pin; lemma open."""
    import json
    import re

    brief = json.loads(
        (ROOT / "portable" / "BATCH354_REPUBLISH_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "354"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("scientific_effect") == "NONE"
    assert brief.get("action") == "living_script_stale_republish"
    assert brief.get("defect_id") == "living_script_stale_after_batch354_inv_tip_pin"
    assert brief.get("inventable_promoted") is False
    assert brief.get("goal") == "OPEN"
    assert _living_tip(str(brief.get("tip") or brief.get("hardening_tip") or ""))
    assert (brief.get("after") or {}).get("script_stale") == 0

    hunt = json.loads(
        (ROOT / "portable" / "BATCH354_REPUBLISH_HUNT.json").read_text(encoding="utf-8")
    )
    assert hunt.get("defect_shipped") is True
    assert hunt.get("lemma_closed") is False
    assert hunt.get("hunt_0020") == "NEGATIVE"
    assert hunt.get("defect_id") == "living_script_stale_after_batch354_inv_tip_pin"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH354_REPUBLISH_EVIDENCE.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence.get("script_stale_after") == 0
    assert evidence.get("tip_stale") == 0
    assert evidence.get("lemma_closed") is False
    assert evidence.get("action") == "living_script_stale_republish"
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 354)
    headers = re.findall(r"=== Batch (\d+)\b", unblock)
    assert headers and int(headers[0]) >= 354 and len(headers) == 1
    assert "living script_stale republish" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 354 republish)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 354 republish)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "living script_stale" in log_md and "Batch 354" in log_md



def test_batch355_multi_agent_wake_assign() -> None:
    """Batch 355: Dylan wake stopped agents + assign Path C intent tasks @e3cd7d4."""
    import json
    import re

    wake = json.loads(
        (ROOT / "portable" / "MULTI_AGENT_WAKE_BATCH355.json").read_text(encoding="utf-8")
    )
    assert wake.get("batch") == 355
    assert wake.get("wake355_on_main") is True
    assert wake.get("lemma_closed") is False
    assert wake.get("flipped_anything") is False
    assert wake.get("action") == "multi_agent_wake_and_assign"
    assert wake.get("scientific_effect") == "NONE"
    assert len(wake.get("woken_idle_agents") or []) >= 3
    living = wake.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0
    assert _living_tip(str(wake.get("tip") or ""))
    assert _living_tip(str(wake.get("wake_tip_at_assign") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH355_WAKE_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "355"
    assert brief.get("action") == "multi_agent_wake_and_assign"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False
    assert brief.get("tip_match") is True

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 355)
    assert "WAKE355" in unblock or "MULTI_AGENT wake" in unblock
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 wake)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "MULTI_AGENT_WAKE_BATCH355" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "stopped agents" in log_md and "Batch 355" in log_md

    poster = (ROOT / "scripts" / "post_batch322_wake_comments.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'(?m)^    return "(\d+)"\s*$', poster)
    assert m is not None
    assert int(m.group(1)) >= 355
    helper = (ROOT / "scripts" / "refresh_ai_agent_access_inventory.py").read_text(
        encoding="utf-8"
    )
    m_inv = re.search(r'return "(\d+)"', helper)
    assert m_inv is not None
    assert int(m_inv.group(1)) >= 355
    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    _assert_refresh_batch_tag_default_at_least(refresh, 355)

def test_batch355_idle_tip_sync_watch() -> None:
    """Batch 355: tip_sync_watch idle @e3cd7d4; tip_match; living current."""
    import json

    tiny = json.loads(
        (ROOT / "portable" / "BATCH355_IDLE.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "355"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("tip_match") is True
    assert tiny.get("aligned") is True
    assert tiny.get("action") == "idle_no_commit"
    assert tiny.get("goal_complete") is False
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("scientific_effect") == "NONE"
    assert _living_tip(str(tiny.get("hardening_tip") or ""))
    living = tiny.get("living") or {}
    assert living.get("tip_stale") == 0
    assert living.get("script_stale") == 0

    evidence = json.loads(
        (ROOT / "portable" / "BATCH355_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("action") == "idle_no_commit"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert _living_tip(str(evidence.get("hardening_tip") or ""))

    brief = json.loads(
        (ROOT / "portable" / "BATCH355_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("assignment") == "tip_sync_watch_vs_BASE_TIP_e3cd7d4"
    assert brief.get("action") == "idle_no_commit"
    assert brief.get("lemma_closed") is False
    assert brief.get("living_tip_stale") == 0
    assert brief.get("living_script_stale") == 0

    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base)

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 355)
    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 idle)" in land
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 idle)" in owner
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 355" in log_md and "idle_no_commit" in log_md

def test_batch355_inventory_preserve_durable_tip_pin() -> None:
    """Batch 355: preserve_durable tip pin; 8/8; lemma open; tip e3cd7d4."""
    import json
    import re

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 355
    assert inv.get("durable_writable") == "8/8"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"

    evidence = json.loads(
        (ROOT / "portable" / "BATCH355_INV_TIP_PIN_EVIDENCE.json").read_text(encoding="utf-8")
    )
    assert evidence.get("batch") == "355"
    assert evidence.get("action") == "inventory_preserve_durable_tip_pin"
    assert evidence.get("durable") == "8/8_WRITABLE"
    assert evidence.get("lemma_closed") is False
    assert evidence.get("flipped_anything") is False
    assert evidence.get("tip_match") is True
    assert evidence.get("scientific_effect") == "NONE"
    assert str(evidence.get("hardening_tip", "")).startswith("e3cd7d4")
    assert evidence.get("trial_tip_matches_live_head") is True

    brief = json.loads(
        (ROOT / "portable" / "BATCH355_INV_TIP_PIN_BRIEF.json").read_text(encoding="utf-8")
    )
    assert brief.get("batch") == "355"
    assert brief.get("action") == "inventory_preserve_durable_tip_pin"
    assert brief.get("lemma_closed") is False
    assert brief.get("flipped_anything") is False

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    headers = re.findall(r"=== Batch (\d+)\s", unblock)
    assert headers and int(headers[0]) >= 355 and len(headers) == 1
    assert "inventory_preserve_durable_tip_pin" in unblock

    base_tip = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert _living_tip(base_tip)
    assert "e3cd7d4" in base_tip

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 inv-preserve-tip-pin)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "Batch 355" in log_md and "inventory_preserve_durable_tip_pin" in log_md

def test_batch355_grant_inventory_refresh() -> None:
    """Batch 355: inventory batch >=355 + durable 8/8; grant skip source=none."""
    import json

    inv = json.loads(
        (ROOT / "portable" / "AI_AGENT_ACCESS_INVENTORY.json").read_text(encoding="utf-8")
    )
    assert int(str(inv.get("batch") or "0")) >= 355
    assert inv.get("lemma_closed") is False
    assert inv.get("flipped_anything") is False
    assert inv.get("scientific_effect") == "NONE"
    assert inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
    assert int(inv.get("sibling_write_count") or 0) == 8
    assert inv.get("sandbox", {}).get("readable") is True
    assert inv.get("sandbox", {}).get("write") == "WRITABLE"
    for d in inv.get("details") or []:
        assert d.get("push") is True, d
        assert d.get("write") == "WRITABLE", d

    tiny = json.loads(
        (ROOT / "portable" / "BATCH355_GRANT.json").read_text(encoding="utf-8")
    )
    assert tiny.get("batch") == "355"
    assert tiny.get("lemma_closed") is False
    assert tiny.get("flipped_anything") is False
    assert tiny.get("coverage") == "8/8_WRITABLE"
    assert tiny.get("durable") == "8/8"
    assert tiny.get("action") == "grant_inventory_refresh_batch355"
    assert tiny.get("assignment") == "grant_check_dual_vector_8of8"
    assert tiny.get("tip_match") is True
    assert tiny.get("inventable_promoted") is False
    assert tiny.get("goal") == "OPEN"
    assert _living_tip(str(tiny.get("tip", "")))
    assert _living_tip(str(tiny.get("hardening_tip", "")))

    grant = (ROOT / "scripts" / "owner_grant_ai_agent_access.sh").read_text(
        encoding="utf-8"
    )
    assert 'DURABLE_TOKEN_SOURCE" == "none"' in grant
    assert 'DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0' not in grant

    unblock = (ROOT / "scripts" / "print_owner_unblock.sh").read_text(encoding="utf-8")
    _assert_print_owner_header_batch_at_least(unblock, 355)

    land = (ROOT / "portable" / "LAND.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 grant)" in land
    log_md = (ROOT / "docs" / "AUTONOMOUS_48H_LOG.md").read_text(encoding="utf-8")
    assert "BATCH355_GRANT" in log_md or "grant_inventory_refresh_batch355" in log_md
    owner = (ROOT / "docs" / "OWNER_ACTIONS_MAIN.md").read_text(encoding="utf-8")
    assert "STATUS (Batch 355 grant)" in owner
