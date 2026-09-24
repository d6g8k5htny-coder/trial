#!/usr/bin/env python3
"""Watch ALIGNED drift on d6g8k5htny-coder/main; snapshot tip + markers.

Pressure context: ALIGNED can be reverted (happened via PR #32). Write is often
DENIED, but agents must stay ready to restore instantly (prefer Path B).

Exit codes:
  0 — ALIGNED (q0 program or Option-B / renewal notice on default tip)
  1 — MISALIGNED
  2 — transport / API failure

Always prints one JSON object including preferred restore route (B vs A) for the
current tip. Always writes portable/ALIGNED_DRIFT_SNAPSHOT.json (tip SHA +
audit markers) unless --no-snapshot.

Optional --restore-if-writable: when MISALIGNED and a Path-B-capable write vector
is WRITABLE, run scripts/restore_main_face.sh (batch land). Never flips
lemma_closed / prizes / premises / research status.

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

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_main_alignment.py"
WATCH = ROOT / "scripts" / "watch_main_alignment.py"
PROBE = ROOT / "scripts" / "probe_main_write.py"
VECTORS = ROOT / "scripts" / "probe_main_write_vectors.py"
RESTORE = ROOT / "scripts" / "restore_main_face.sh"
WINDOW = ROOT / "scripts" / "check_autonomous_window.py"
SNAPSHOT = ROOT / "portable" / "ALIGNED_DRIFT_SNAPSHOT.json"

# Prefer Path B for restore when MISALIGNED; Path A is the alternate
# (PR #2 ready/merge or revert-of-revert). Path C is post-ALIGNED hardening.
ROUTE_WHEN_MISALIGNED = "Path_B"
ROUTE_ALTERNATE = "Path_A"
ROUTE_WHEN_ALIGNED = "Path_C_on_hardening"


def _parse_json_stdout(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.index("{")
            return json.loads(text[start:])
        except (ValueError, json.JSONDecodeError):
            return {"raw_stdout": text[-2000:]}


def _run_json(cmd: list[str], timeout: int = 120) -> tuple[int, dict, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )
    return proc.returncode, _parse_json_stdout(proc.stdout), (proc.stderr or "").strip()


def _preferred_restore_route(align_state: str) -> dict:
    """Prefer Path B over Path A for restore; Path C when already ALIGNED."""
    if align_state == "ALIGNED":
        return {
            "prefer": ROUTE_WHEN_ALIGNED,
            "restore_if_drift": ROUTE_WHEN_MISALIGNED,
            "alternate_restore": ROUTE_ALTERNATE,
            "action": "path_c_hardening_if_writable_else_dry_run",
            "note": (
                "Default tip ALIGNED. Prefer Path C on hardening when writable. "
                "If tip drifts (e.g. another #32-style revert), restore via Path B "
                "first; Path A remains alternate. Never flip lemma_closed."
            ),
        }
    if align_state == "MISALIGNED":
        return {
            "prefer": ROUTE_WHEN_MISALIGNED,
            "alternate_restore": ROUTE_ALTERNATE,
            "action": "path_b_if_writable_else_portable_prepare",
            "note": (
                "MISALIGNED — prefer Path B (Option-B README+AGENTS via "
                "restore_main_face.sh). Path A (PR #2 / revert-of-revert) is "
                "alternate. Never flip lemma_closed / research status."
            ),
        }
    return {
        "prefer": "none",
        "alternate_restore": ROUTE_ALTERNATE,
        "action": "retry_transport",
        "note": "Transport failure; cannot choose restore route until audit succeeds.",
    }


def _window_payload() -> dict:
    if not WINDOW.is_file():
        return {
            "state": "SCRIPT_MISSING",
            "hard_stop": False,
            "within_window": True,
            "scientific_effect": "NONE",
        }
    _ec, payload, err = _run_json([sys.executable, str(WINDOW)], timeout=30)
    if not payload:
        return {
            "state": "PARSE_ERROR",
            "stderr": err[-500:],
            "scientific_effect": "NONE",
        }
    payload.setdefault("scientific_effect", "NONE")
    return payload


def _write_snapshot(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    audit = report.get("audit") or {}
    snap = {
        "generated_at_utc": report.get("watched_at_utc"),
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "state": report.get("state"),
        "default_tip_sha": audit.get("default_tip_sha") or report.get("default_tip_sha"),
        "default_branch": audit.get("default_branch"),
        "complexity_markers_present": audit.get("complexity_markers_present", []),
        "q0_or_notice_markers_present": audit.get("q0_or_notice_markers_present", []),
        "root_has_AGENTS_md": audit.get("root_has_AGENTS_md"),
        "root_has_body": audit.get("root_has_body"),
        "root_has_dot_github": audit.get("root_has_dot_github"),
        "preferred_restore_route": report.get("preferred_restore_route"),
        "write_state": (report.get("write") or {}).get("state"),
        "path_b_ready": (report.get("write") or {}).get("path_b_ready"),
        "threat_note": (
            "ALIGNED can be reverted (PR #32 history). Keep Path B restore ready."
        ),
    }
    path.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        report["snapshot_path"] = str(path.relative_to(ROOT))
    except ValueError:
        report["snapshot_path"] = str(path)
    report["snapshot"] = snap


def _maybe_restore(report: dict, batch: str) -> dict:
    """Run restore_main_face when MISALIGNED + Path-B-capable write."""
    detail: dict = {
        "attempted": False,
        "skipped_reason": None,
        "exit": None,
        "stdout_tail": None,
        "stderr_tail": None,
    }
    if report.get("state") != "MISALIGNED":
        detail["skipped_reason"] = "not_misaligned"
        return detail
    write = report.get("write") or {}
    if write.get("state") != "WRITABLE" and not write.get("path_b_ready"):
        detail["skipped_reason"] = "not_writable"
        return detail
    if not RESTORE.is_file():
        detail["skipped_reason"] = "restore_script_missing"
        return detail
    detail["attempted"] = True
    proc = subprocess.run(
        ["bash", str(RESTORE), "--batch", str(batch)],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )
    detail["exit"] = proc.returncode
    detail["stdout_tail"] = (proc.stdout or "")[-2000:]
    detail["stderr_tail"] = (proc.stderr or "")[-2000:]
    return detail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-snapshot",
        action="store_true",
        help="Skip writing portable/ALIGNED_DRIFT_SNAPSHOT.json",
    )
    parser.add_argument(
        "--snapshot",
        default=str(SNAPSHOT),
        help="Snapshot output path (default: portable/ALIGNED_DRIFT_SNAPSHOT.json)",
    )
    parser.add_argument(
        "--no-probe",
        action="store_true",
        help="Skip write probe / vectors (audit + route + snapshot only)",
    )
    parser.add_argument(
        "--restore-if-writable",
        action="store_true",
        help="If MISALIGNED and Path-B write works, run restore_main_face.sh",
    )
    parser.add_argument(
        "--batch",
        default=os.environ.get("RESTORE_BATCH", "72"),
        help="Batch id passed to restore_main_face when restoring (default 72)",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="Skip autonomous window embed",
    )
    args = parser.parse_args()

    watched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report: dict = {
        "watched_at_utc": watched_at,
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "flipped_anything": False,
    }

    audit_ec, audit, audit_err = _run_json([sys.executable, str(AUDIT)])
    report["audit_exit"] = audit_ec
    report["audit_stderr"] = audit_err
    if audit:
        report["audit"] = audit
        report["default_tip_sha"] = audit.get("default_tip_sha")

    if audit_ec == 0:
        report["state"] = "ALIGNED"
    elif audit_ec == 1:
        report["state"] = "MISALIGNED"
    else:
        report["state"] = "TRANSPORT_ERROR"

    report["preferred_restore_route"] = _preferred_restore_route(report["state"])

    if not args.no_window:
        report["autonomous_window"] = _window_payload()
    else:
        report["autonomous_window"] = None

    write_info: dict = {
        "probed": False,
        "state": None,
        "path_b_ready": None,
        "probe_exit": None,
        "vectors_exit": None,
    }
    if not args.no_probe:
        write_info["probed"] = True
        probe_ec, probe, _probe_err = _run_json([sys.executable, str(PROBE)])
        write_info["probe_exit"] = probe_ec
        write_info["probe"] = {
            "state": probe.get("state"),
            "create_http_status": probe.get("create_http_status"),
        }
        vec_ec, vectors, _vec_err = _run_json([sys.executable, str(VECTORS)], timeout=180)
        write_info["vectors_exit"] = vec_ec
        write_info["path_b_ready"] = bool(vectors.get("path_b_ready"))
        write_info["path_b_writable_vectors"] = vectors.get("path_b_writable_vectors", [])
        # Prefer vectors aggregate state; fall back to single-ref probe.
        write_info["state"] = vectors.get("state") or probe.get("state")
    report["write"] = write_info

    # Instant-restore readiness signal (even when currently ALIGNED).
    report["instant_restore_ready"] = {
        "script": "scripts/restore_main_face.sh",
        "preferred_when_misaligned": ROUTE_WHEN_MISALIGNED,
        "alternate_when_misaligned": ROUTE_ALTERNATE,
        "write_currently": write_info.get("state"),
        "note": (
            "When write flips WRITABLE and tip is MISALIGNED, run "
            "aligned_drift_watch.py --restore-if-writable or restore_main_face.sh."
        ),
    }

    if args.restore_if_writable:
        report["restore"] = _maybe_restore(report, args.batch)
        # Re-audit after restore attempt so exit code reflects post-restore tip.
        if report["restore"].get("attempted"):
            audit_ec2, audit2, audit_err2 = _run_json([sys.executable, str(AUDIT)])
            report["post_restore_audit_exit"] = audit_ec2
            report["post_restore_audit_stderr"] = audit_err2
            if audit2:
                report["post_restore_audit"] = audit2
            if audit_ec2 == 0:
                report["state"] = "ALIGNED"
            elif audit_ec2 == 1:
                report["state"] = "MISALIGNED"
            else:
                report["state"] = "TRANSPORT_ERROR"
            report["preferred_restore_route"] = _preferred_restore_route(report["state"])

    if not args.no_snapshot:
        _write_snapshot(report, Path(args.snapshot))

    print(json.dumps(report, indent=2, sort_keys=True))

    if report["state"] == "ALIGNED":
        return 0
    if report["state"] == "MISALIGNED":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
