#!/usr/bin/env python3
"""Path C dry-run certainty: hardening tip apply_all --check + default tip shape.

Post-ALIGNED tips (owner PR #41 @ 1c6e74b, and earlier post-#2) can be ALIGNED
while lacking Path-C shape (no docs/math_status/PACKET.json / carriers_verify).
This script reports whether portable patches are ready to land on the hardening
BASE_TIP *without* pushing. Does not open PRs or promote research status.

Exit codes:
  0 — apply check OK: APPLY_READY (landable) OR IDLE_PATH_C_DONE (already on tip)
  1 — apply check failed or hardening tip not Path-C shaped
  2 — transport / missing inputs

Batch 261: when VERIFY.path_c_landed and tip_matches_base, do not advertise
APPLY_READY / apply_ready=true (that lied after Path C landed on tip). Report
IDLE_PATH_C_DONE with already_on_tip=true and apply_ready=false; apply_check_ok
still reflects apply_all --check.

Scientific effect: NONE.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = "d6g8k5htny-coder/main"
HARDENING = "chatgpt/drive-github-hardening-20260919"
APPLY_STACK = "0001-0004 + 0008-0019"
_SHA40 = re.compile(r"(?i)\b([0-9a-f]{40})\b")
_SHA_SHORT = re.compile(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)")


def _parse_base_tip_sha(line: str) -> str | None:
    """Extract hex SHA from BASE_TIP.txt; ignore trailing comments / KEY=value noise."""
    text = (line or "").strip()
    if not text:
        return None
    m = _SHA40.search(text)
    if m:
        return m.group(1).lower()
    m = _SHA_SHORT.search(text)
    if m:
        return m.group(1).lower()
    return None


def _trial_root() -> Path:
    env = os.environ.get("TRIAL_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )


def _tree_accepts_path_c(clone: Path, tip_ref: str) -> dict:
    """Hardening-shaped tree required by apply_all root guard + patch hunks."""
    needed = (
        "docs/math_status/PACKET.json",
        "tools/carriers_verify.py",
        "tools/math_status_check.py",
    )
    missing: list[str] = []
    for path in needed:
        probe = _run(["git", "cat-file", "-e", f"{tip_ref}:{path}"], cwd=clone)
        if probe.returncode != 0:
            missing.append(path)
    return {
        "tip_ref": tip_ref,
        "accepts": not missing,
        "missing": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workdir",
        default="",
        help="Reuse an existing dir; default is a temp dir cleaned on exit",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Do not delete the workdir (for inspection)",
    )
    parser.add_argument(
        "--json-out",
        default="",
        help="Optional path to write the certainty JSON (also printed to stdout)",
    )
    parser.add_argument(
        "--probe-rebase",
        action="store_true",
        default=True,
        help="Probe PATH_C_REBASE_ONTO_MAIN feasibility (default: on)",
    )
    parser.add_argument(
        "--skip-rebase-probe",
        action="store_true",
        help="Skip rebase conflict probe (faster)",
    )
    parser.add_argument(
        "--skip-apply-check",
        action="store_true",
        help="Skip apply_all --check (shape + tip currency only)",
    )
    args = parser.parse_args()
    probe_rebase = args.probe_rebase and not args.skip_rebase_probe

    trial = _trial_root()
    apply_all = trial / "portable/patches/apply_all.sh"
    base_tip_file = trial / "portable/patches/BASE_TIP.txt"
    base_tip_line = (
        base_tip_file.read_text(encoding="utf-8").strip() if base_tip_file.is_file() else ""
    )
    # Batch 153: hex SHA extract (not last whitespace field — comments spoil $NF).
    base_sha = _parse_base_tip_sha(base_tip_line.splitlines()[0] if base_tip_line else "")

    report: dict = {
        "probe": "path_c_dry_run_certainty",
        "repo": REPO,
        "scientific_effect": "NONE",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trial_root": str(trial),
        "apply_stack": APPLY_STACK,
        "hardening_ref": HARDENING,
        "base_tip_file": base_tip_line,
        "base_tip_sha": base_sha,
        "state": "UNKNOWN",
        "apply_ready": False,
        "recommended_base": HARDENING,
        "rebase_onto_main_advised": False,
        "owner_script": "scripts/owner_land_path_c.sh",
        "write_required_to_land": True,
        "post_aligned_note": (
            "Default tip may be ALIGNED (e.g. owner PR #41 @ 1c6e74b) while lacking "
            "Path-C shape (PACKET.json / carriers_verify). Keep Path C on hardening "
            "BASE_TIP. Do not set PATH_C_BASE=main. PATH_C_REBASE_ONTO_MAIN is usually "
            "NOT advised after #41 (history/ relocation; rebase conflicts)."
        ),
    }

    if not apply_all.is_file():
        report["state"] = "MISSING_APPLY_ALL"
        report["error"] = f"missing {apply_all}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    cleanup = False
    if args.workdir:
        work = Path(args.workdir).resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        work = Path(tempfile.mkdtemp(prefix="path-c-dry-run."))
        cleanup = not args.keep

    clone_dir = work / "main"
    try:
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        # Clone default tip shallow, then fetch hardening tip explicitly.
        # A plain `git fetch origin <branch>` after shallow clone often leaves
        # origin/<hardening> unresolved — pin the remote-tracking ref.
        clone = _run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                f"https://github.com/{REPO}.git",
                str(clone_dir),
            ]
        )
        if clone.returncode != 0:
            # Fallback without partial clone (older git / hosts).
            if clone_dir.exists():
                shutil.rmtree(clone_dir)
            clone = _run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "80",
                    f"https://github.com/{REPO}.git",
                    str(clone_dir),
                ]
            )
        if clone.returncode != 0:
            report["state"] = "CLONE_FAILED"
            report["error"] = (clone.stderr or clone.stdout or "clone failed")[-500:]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2

        fetch_hard = _run(
            [
                "git",
                "fetch",
                "--depth",
                "80",
                "origin",
                f"+refs/heads/{HARDENING}:refs/remotes/origin/{HARDENING}",
            ],
            cwd=clone_dir,
        )
        fetch_main = _run(
            [
                "git",
                "fetch",
                "--depth",
                "80",
                "origin",
                "+refs/heads/main:refs/remotes/origin/main",
            ],
            cwd=clone_dir,
        )
        if fetch_hard.returncode != 0:
            report["state"] = "FETCH_HARDENING_FAILED"
            report["error"] = (fetch_hard.stderr or fetch_hard.stdout or "fetch hardening")[-500:]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2
        if fetch_main.returncode != 0:
            report["state"] = "FETCH_MAIN_FAILED"
            report["error"] = (fetch_main.stderr or fetch_main.stdout or "fetch main")[-500:]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2

        hard_sha_proc = _run(
            ["git", "rev-parse", f"origin/{HARDENING}"], cwd=clone_dir
        )
        main_sha_proc = _run(["git", "rev-parse", "origin/main"], cwd=clone_dir)
        if hard_sha_proc.returncode != 0 or main_sha_proc.returncode != 0:
            report["state"] = "REV_PARSE_FAILED"
            report["error"] = (
                (hard_sha_proc.stderr or "") + (main_sha_proc.stderr or "")
            )[-500:]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2
        hard_sha = hard_sha_proc.stdout.strip()
        main_sha = main_sha_proc.stdout.strip()
        if not hard_sha or not main_sha or "origin/" in hard_sha:
            report["state"] = "REV_PARSE_FAILED"
            report["error"] = f"bad shas hard={hard_sha!r} main={main_sha!r}"
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2
        report["hardening_sha"] = hard_sha
        report["default_tip_sha"] = main_sha
        report["tip_matches_base"] = bool(
            base_sha and hard_sha and hard_sha.startswith(base_sha[:7])
        )

        hard_shape = _tree_accepts_path_c(clone_dir, f"origin/{HARDENING}")
        main_shape = _tree_accepts_path_c(clone_dir, "origin/main")
        report["hardening_path_c_shape"] = hard_shape
        report["default_path_c_shape"] = main_shape

        # Local auditor on default tip (ALIGNED vs Path-C shape are independent).
        audit_local = trial / "scripts/audit_local_tree.py"
        if audit_local.is_file():
            # Sparse checkout of default tip files into a temp tree is heavy;
            # use remote tip via a detached worktree of origin/main.
            main_wt = work / "main-tip"
            if main_wt.exists():
                shutil.rmtree(main_wt)
            _run(
                ["git", "worktree", "add", "--detach", str(main_wt), "origin/main"],
                cwd=clone_dir,
            )
            aud = _run([sys.executable, str(audit_local), str(main_wt)])
            aud_payload: dict = {}
            if aud.stdout.strip():
                try:
                    text = aud.stdout.strip()
                    aud_payload = json.loads(text[text.find("{") :])
                except json.JSONDecodeError:
                    aud_payload = {"raw": aud.stdout[-500:]}
            report["default_local_auditor"] = aud_payload
            report["default_aligned"] = aud.returncode == 0 and aud_payload.get("state") == "ALIGNED"
            _run(["git", "worktree", "remove", "--force", str(main_wt)], cwd=clone_dir)

        if not hard_shape["accepts"]:
            report["state"] = "HARDENING_NOT_PATH_C_SHAPED"
            report["apply_ready"] = False
            report["error"] = f"hardening tip missing {hard_shape['missing']}"
            text = json.dumps(report, indent=2, sort_keys=True)
            print(text)
            if args.json_out:
                Path(args.json_out).write_text(text + "\n", encoding="utf-8")
            return 1

        # apply_all --check on a clean hardening worktree
        # Batch 231: when Path C already landed, apply_all is idempotent
        # (already-applied skips); treat tip as apply_ready.
        apply_exit = None
        apply_out = ""
        path_c_landed = False
        verify_path = trial / "portable" / "path-c-applied-bundle" / "VERIFY.json"
        if verify_path.is_file():
            try:
                verify = json.loads(verify_path.read_text(encoding="utf-8"))
                path_c_landed = verify.get("path_c_landed") is True
            except (OSError, json.JSONDecodeError):
                path_c_landed = False
        report["path_c_landed"] = path_c_landed
        if args.skip_apply_check:
            report["apply_all_check"] = "skipped"
        else:
            apply_wt = work / "apply-check"
            if apply_wt.exists():
                shutil.rmtree(apply_wt)
            _run(
                ["git", "worktree", "add", "--detach", str(apply_wt), f"origin/{HARDENING}"],
                cwd=clone_dir,
            )
            check = _run(["bash", str(apply_all), "--check"], cwd=apply_wt)
            apply_exit = check.returncode
            apply_out = ((check.stdout or "") + (check.stderr or ""))[-800:]
            report["apply_all_check_exit"] = apply_exit
            report["apply_all_check_tail"] = apply_out
            if path_c_landed and apply_exit == 0:
                report["apply_all_check"] = "ok_already_landed_idempotent"
            _run(["git", "worktree", "remove", "--force", str(apply_wt)], cwd=clone_dir)

        # Rebase probe: PATH_C_REBASE_ONTO_MAIN after #41 typically CONFLICTS.
        # Batch 67+: also enumerate conflict paths / categories (conflict-aware readiness).
        rebase_state = "SKIPPED"
        rebase_tail = ""
        conflict_paths: list[str] = []
        conflict_categories: dict[str, list[str]] = {}
        if not probe_rebase:
            rebase_state = "NOT_PROBED"
        elif main_shape["accepts"]:
            # Main already Path-C shaped — rebase less relevant; base could be main.
            rebase_state = "N_A_MAIN_ALREADY_PATH_C"
            report["recommended_base"] = "main"
            report["rebase_onto_main_advised"] = False
        else:
            rebase_wt = work / "rebase-probe"
            if rebase_wt.exists():
                shutil.rmtree(rebase_wt)
            _run(
                ["git", "worktree", "add", "--detach", str(rebase_wt), f"origin/{HARDENING}"],
                cwd=clone_dir,
            )
            reb = _run(["git", "rebase", "origin/main"], cwd=rebase_wt)
            rebase_tail = ((reb.stdout or "") + (reb.stderr or ""))[-800:]
            if reb.returncode == 0:
                rebase_state = "CLEAN"
                # Still not advised blindly post-#41: history layout differs; leave advised=false
                # unless operator explicitly wants integration.
                report["rebase_onto_main_advised"] = False
            else:
                rebase_state = "CONFLICTING"
                report["rebase_onto_main_advised"] = False
                unmerged = _run(
                    ["git", "diff", "--name-only", "--diff-filter=U"], cwd=rebase_wt
                )
                conflict_paths = sorted(
                    {
                        line.strip()
                        for line in (unmerged.stdout or "").splitlines()
                        if line.strip()
                    }
                )
                if not conflict_paths:
                    porcelain = _run(["git", "status", "--porcelain"], cwd=rebase_wt)
                    for line in (porcelain.stdout or "").splitlines():
                        if len(line) >= 4 and line[:2] in {
                            "UU",
                            "AA",
                            "DU",
                            "UD",
                            "AU",
                            "UA",
                        }:
                            conflict_paths.append(line[3:].strip())
                    conflict_paths = sorted(set(conflict_paths))
                for path in conflict_paths:
                    if path.startswith(".github/") or path.endswith(
                        ("ci.yml", "research.yml")
                    ):
                        cat = "ci_workflows"
                    elif path in {"AGENTS.md", "CLAUDE.md"} or "bridge" in path.lower():
                        cat = "bridge_agents"
                    elif path.startswith("history/") or path == "body" or path.startswith(
                        "body/"
                    ):
                        cat = "history_relocation"
                    elif path.startswith("tools/"):
                        cat = "tools_stubs_vs_full"
                    elif path in {"README.md"} or (
                        path.startswith("docs/") and "math_status" not in path
                    ):
                        cat = "docs_landing"
                    else:
                        cat = "other"
                    conflict_categories.setdefault(cat, []).append(path)
                _run(["git", "rebase", "--abort"], cwd=rebase_wt)
            _run(["git", "worktree", "remove", "--force", str(rebase_wt)], cwd=clone_dir)

        report["rebase_onto_main_state"] = rebase_state
        report["rebase_onto_main_tail"] = rebase_tail
        report["rebase_conflict_path_count"] = len(conflict_paths)
        report["rebase_conflict_paths"] = conflict_paths
        report["rebase_conflict_categories"] = conflict_categories
        report["path_c_base_main_ok"] = bool(main_shape["accepts"])
        report["do_not_set_path_c_base_main"] = not main_shape["accepts"]
        report["conflict_aware_report"] = (
            "portable/PATH_C_REBASE_CONFLICT_REPORT_<batch>.json"
        )

        apply_ok = args.skip_apply_check or apply_exit == 0
        apply_check_ok = bool(apply_ok and hard_shape["accepts"])
        report["apply_check_ok"] = apply_check_ok
        tip_match = report.get("tip_matches_base") is True
        # Batch 261: landed + tip match → idle (same class as owner_land_path_c /
        # owner_open_path_c_pr already-on-tip). Do not advertise APPLY_READY land.
        already_on_tip = bool(path_c_landed and tip_match and apply_check_ok)
        report["already_on_tip"] = already_on_tip
        if already_on_tip:
            report["state"] = "IDLE_PATH_C_DONE"
            report["idle_status"] = "IDLE_PATH_C_DONE"
            report["apply_ready"] = False
        elif apply_check_ok:
            report["apply_ready"] = True
            report["state"] = "APPLY_READY"
            if not main_shape["accepts"] and report.get("default_aligned"):
                report["state"] = "APPLY_READY_POST_ALIGNED_KEEP_HARDENING"
        else:
            report["apply_ready"] = False
            report["state"] = "APPLY_CHECK_FAILED"
            report["error"] = apply_out or "apply_all --check failed"

        text = json.dumps(report, indent=2, sort_keys=True)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        return 0 if (report["apply_ready"] or already_on_tip) else 1
    finally:
        if cleanup and work.exists():
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
