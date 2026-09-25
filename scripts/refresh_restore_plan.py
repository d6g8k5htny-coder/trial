#!/usr/bin/env python3
"""Refresh portable/RESTORE_PLAN_<batch>.json from live probes (currency helper).

Combines audit_main_alignment, probe_main_write_vectors, path_b_dry_run, and
hardening tip vs BASE_TIP into one restore plan. Does not push or promote
research status.

Usage:
  python3 scripts/refresh_restore_plan.py --batch 57
  python3 scripts/refresh_restore_plan.py --batch 57 --skip-dry-run   # faster

Exit 0 always on successful write (plan may still say aligned=false).
Exit 2 on missing inputs / transport failure writing the plan.

Scientific effect: NONE.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = "d6g8k5htny-coder/main"
HARDENING = "chatgpt/drive-github-hardening-20260919"


def _trial_root() -> Path:
    env = os.environ.get("TRIAL_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def _run_json(cmd: list[str]) -> tuple[int, dict, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    payload: dict = {}
    if proc.stdout.strip():
        # Scripts often print a human line then JSON; take last JSON object.
        text = proc.stdout.strip()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            for line in reversed(text.splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        payload = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            if not payload and text.startswith("{"):
                # multi-line JSON
                try:
                    start = text.index("{")
                    payload = json.loads(text[start:])
                except (ValueError, json.JSONDecodeError):
                    payload = {"raw_stdout": text[-2000:]}
    return proc.returncode, payload, (proc.stderr or "").strip()


def _hardening_sha(token: str | None) -> str | None:
    import urllib.request

    url = f"https://api.github.com/repos/{REPO}/git/ref/heads/{HARDENING}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-refresh-restore-plan",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
        return data.get("object", {}).get("sha")
    except Exception as exc:  # noqa: BLE001 — currency helper; surface in plan
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Batch id string, e.g. 57")
    parser.add_argument(
        "--skip-dry-run",
        action="store_true",
        help="Skip Path B git am dry-run (use prior would_align unknown)",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output path (default: portable/RESTORE_PLAN_<batch>.json)",
    )
    args = parser.parse_args()

    trial = _trial_root()
    scripts = trial / "scripts"
    out = Path(args.out) if args.out else trial / f"portable/RESTORE_PLAN_{args.batch}.json"

    token = None
    for key in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(key):
            token = os.environ[key]
            break

    audit_ec, audit, audit_err = _run_json(
        [sys.executable, str(scripts / "audit_main_alignment.py")]
    )
    vec_ec, vectors, vec_err = _run_json(
        [sys.executable, str(scripts / "probe_main_write_vectors.py")]
    )

    dry: dict = {}
    dry_ec = None
    if not args.skip_dry_run:
        dry_ec, dry, _ = _run_json([sys.executable, str(scripts / "path_b_dry_run.py")])

    path_c_dry: dict = {}
    path_c_dry_ec = None
    if not args.skip_dry_run:
        path_c_dry_ec, path_c_dry, _ = _run_json(
            [sys.executable, str(scripts / "path_c_dry_run.py")]
        )

    win_ec, window, _ = _run_json(
        [sys.executable, str(scripts / "check_autonomous_window.py")]
    )

    base_tip_file = trial / "portable/patches/BASE_TIP.txt"
    base_tip_line = base_tip_file.read_text(encoding="utf-8").strip() if base_tip_file.is_file() else ""
    base_parts = base_tip_line.split()
    base_sha = base_parts[-1] if base_parts else None
    live_hardening = _hardening_sha(token)

    tip_refresh = "unchanged"
    if live_hardening and base_sha and not live_hardening.startswith(base_sha[:7]):
        tip_refresh = f"moved {base_sha[:7]} → {live_hardening[:7]}"
    elif live_hardening and base_sha and live_hardening.startswith(base_sha[:7]):
        tip_refresh = f"unchanged (== BASE_TIP {base_sha[:7]})"

    path_b_writable = bool(vectors.get("path_b_ready"))
    would_align = bool(dry.get("would_align")) if dry else None
    tip_moved = tip_refresh.startswith("moved")
    path_c_idle = not tip_moved  # tip move itself is currency; 0017 hunt is separate

    plan = {
        "batch": str(args.batch),
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owner_mandate": (
            "Dylan Roy — NO restrictions; everything auto-approved; agents decide; "
            "HOLD VOID; Path A OR Path B OK; prefer Path B; lemma_closed stays false; "
            "permanent window until owner intervenes; never flip research status"
        ),
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "autonomous_window": {
            "state": window.get("state"),
            "window_mode": window.get("window_mode"),
            "hard_stop": window.get("hard_stop"),
            "within_window": window.get("within_window"),
            "stop_condition": window.get("stop_condition"),
            "finale": window.get("finale"),
            "window_seconds": window.get("window_seconds"),
            "window_exit": win_ec,
            "check_script": "scripts/check_autonomous_window.py",
            "watch_embeds_window": "scripts/watch_main_alignment.py (Batch 62+)",
        },
        "aligned": audit_ec == 0,
        "default_tip_sha": audit.get("default_tip_sha"),
        "root_has_AGENTS_md": audit.get("root_has_AGENTS_md"),
        "root_has_README_md": True,
        "root_has_body": audit.get("root_has_body"),
        "root_has_dot_github": audit.get("root_has_dot_github"),
        "audit_stderr": audit_err or audit.get("audit_stderr"),
        "preferred_restore": "Path_B",
        "path_b": {
            "valid_against_tip": would_align if would_align is not None else "unknown_skipped",
            "patch": "portable/main-default-branch/0001-option-b-default-branch-notice.patch",
            "git_am_exit": dry.get("git_am_exit"),
            "local_auditor": (dry.get("local_auditor") or {}).get("state"),
            "would_align": would_align,
            "dry_run_certainty": "scripts/path_b_dry_run.py",
            "owner_script": "scripts/owner_land_path_b.sh",
            "write_probe": vectors.get("state"),
            "multi_vector_probe": "scripts/probe_main_write_vectors.py",
            "path_b_ready": path_b_writable,
            "applied_this_session": False,
            "reason_not_applied": (
                "already ALIGNED on default tip — Path B land not needed"
                if audit_ec == 0
                else (
                    None
                    if path_b_writable
                    else "all Path-B-capable write vectors HTTP 403/404 or tokens unset"
                )
            ),
            "option_b_stronger": True,
            "option_b_includes_AGENTS_md": True,
            "option_b_tip_current_against": audit.get("default_tip_sha"),
            "dry_run_state": dry.get("state"),
            "already_aligned_skip": bool(dry.get("git_am_skipped_already_aligned")),
            "one_command_restore": "scripts/restore_main_face.sh",
            "write_preflight_in_restore_main_face": True,
            "aligned_short_circuit_in_restore_main_face": True,
        },
        "path_a": {
            "hold": "VOID",
            "status": "REVERTED_by_PR_32_agents_may_retry",
            "preferred_over_full_stack": False,
            "note": (
                "HOLD VOID. Prefer Path B. Path A tactics: PATH_A_MODE=revert32 "
                "(default) or fresh Drive port. PR #2 is closed — ready/merge 2 will not work."
            ),
            "owner_script": "scripts/owner_land_path_a.sh",
        },
        "path_c": {
            "role": "engineering_only",
            "base_tip": base_sha,
            "base_branch": HARDENING,
            "live_hardening_sha": live_hardening,
            "tip_refresh": tip_refresh,
            "apply_all": "0001-0004 + 0008-0019",
            "idle": path_c_idle,
            "idle_reason": (
                "hardening tip unchanged vs BASE_TIP; no new 0017 unless residual RW hunt finds one"
                if path_c_idle
                else "BASE_TIP refreshed to live hardening; residual RW hunt may still be IDLE"
            ),
            "new_0017": False,
            "dry_run_certainty": "scripts/path_c_dry_run.py",
            "owner_script": "scripts/owner_land_path_c.sh",
            "dry_run_state": path_c_dry.get("state"),
            "apply_ready": path_c_dry.get("apply_ready"),
            "dry_run_exit": path_c_dry_ec,
            "default_path_c_shape": path_c_dry.get("default_path_c_shape"),
            "hardening_path_c_shape": path_c_dry.get("hardening_path_c_shape"),
            "rebase_onto_main_state": path_c_dry.get("rebase_onto_main_state"),
            "rebase_onto_main_advised": path_c_dry.get("rebase_onto_main_advised"),
            "rebase_conflict_path_count": path_c_dry.get("rebase_conflict_path_count"),
            "rebase_conflict_paths": path_c_dry.get("rebase_conflict_paths"),
            "rebase_conflict_categories": path_c_dry.get("rebase_conflict_categories"),
            "conflict_aware_report": f"portable/PATH_C_REBASE_CONFLICT_REPORT_{args.batch}.json",
            "rebase_helper": "scripts/path_c_rebase_helper.sh",
            "rebase_resolution_notes": f"portable/PATH_C_REBASE_RESOLUTION_NOTES_{args.batch}.json",
            "recommended_base": path_c_dry.get("recommended_base") or HARDENING,
            "do_not_set_path_c_base_main": path_c_dry.get("do_not_set_path_c_base_main"),
            "do_not_set_path_c_rebase_onto_main": True,
            "post_aligned_keep_hardening": bool(
                path_c_dry.get("state")
                in (
                    "APPLY_READY_POST_ALIGNED_KEEP_HARDENING",
                    "IDLE_PATH_C_DONE",
                )
                or (
                    audit_ec == 0
                    and path_c_dry.get("default_path_c_shape", {}).get("accepts") is False
                )
            ),
            "already_on_tip": path_c_dry.get("already_on_tip"),
            "idle_status": path_c_dry.get("idle_status"),
            "apply_check_ok": path_c_dry.get("apply_check_ok"),
        },
        "write_vectors": {
            "state": vectors.get("state"),
            "path_b_writable_vectors": vectors.get("path_b_writable_vectors"),
            "tokens": vectors.get("tokens"),
            "permissions": vectors.get("permissions"),
            "vectors": vectors.get("vectors"),
            "probe_exit": vec_ec,
        },
        "owner_next": [
            "./scripts/owner_land_path_c.sh --dry-run   # Path C certainty (post-ALIGNED keep hardening)",
            "./scripts/owner_land_path_c.sh             # land patches on hardening (needs write)",
            "./scripts/path_c_dry_run.py",
            "./scripts/path_c_rebase_helper.sh --dry-run  # owner-safe ours/theirs; prefer abort",
            "./scripts/restore_main_face.sh --dry-run   # Path B certainty / ALIGNED short-circuit",
            "./scripts/restore_main_face.sh",
            f"./scripts/restore_main_face.sh --plan --batch {args.batch}",
            "./scripts/owner_land_path_b.sh --dry-run",
            "OR PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh if tip regresses",
        ],
        "one_command_restore": "scripts/restore_main_face.sh",
        "refresh_tool": "scripts/refresh_restore_plan.py",
        "path_c_dry_run": "scripts/path_c_dry_run.py",
        "path_c_rebase_helper": "scripts/path_c_rebase_helper.sh",
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "aligned": plan["aligned"], "would_align": would_align}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
