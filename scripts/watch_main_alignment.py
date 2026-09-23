#!/usr/bin/env python3
"""Watch whether d6g8k5htny-coder/main default tip has become aligned.

Exit codes:
  0 — ALIGNED (q0 program or Option-B notice on default tip)
  1 — still MISALIGNED
  2 — transport failure

Prints one JSON object. Scientific effect: NONE.
Intended for autonomous timer batches: when exit flips to 0, refresh trial docs.

Batch 62+: embeds autonomous window status (permanent mode) by default so a
single timer pulse sees ALIGNED/MISALIGNED + PERMANENT_OPEN without a second
process. Use --no-window to skip the store read.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_main_alignment.py"
WINDOW = ROOT / "scripts" / "check_autonomous_window.py"


def _parse_json_stdout(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Human line then JSON, or multi-line JSON object.
        try:
            start = text.index("{")
            return json.loads(text[start:])
        except (ValueError, json.JSONDecodeError):
            return {"raw_stdout": text[-2000:]}


def _window_payload() -> tuple[dict, int]:
    if not WINDOW.is_file():
        return {
            "state": "SCRIPT_MISSING",
            "hard_stop": False,
            "within_window": True,
            "reason": f"missing {WINDOW}",
            "scientific_effect": "NONE",
        }, 0
    proc = subprocess.run(
        [sys.executable, str(WINDOW)],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = _parse_json_stdout(proc.stdout)
    if not payload:
        payload = {
            "state": "PARSE_ERROR",
            "hard_stop": False,
            "within_window": True,
            "stderr": (proc.stderr or "").strip()[-500:],
            "scientific_effect": "NONE",
        }
    payload.setdefault("scientific_effect", "NONE")
    payload["window_exit"] = proc.returncode
    return payload, proc.returncode


def _route_hint(align_state: str, window: dict | None) -> dict:
    """Non-binding routing hint for permanent-autonomy timer batches."""
    win_state = (window or {}).get("state")
    permanent = win_state == "PERMANENT_OPEN"
    if align_state == "ALIGNED":
        action = "path_c_hardening_if_writable_else_dry_run"
        prefer = "Path_C"
    elif align_state == "MISALIGNED":
        action = "path_b_if_writable_else_portable_prepare"
        prefer = "Path_B"
    else:
        action = "retry_transport"
        prefer = "none"
    return {
        "prefer": prefer,
        "action": action,
        "permanent_window": permanent,
        "goal_complete": False,
        "note": (
            "Never flip lemma_closed / research status. "
            "Path C stays on chatgpt/drive-github-hardening-20260919 when "
            "default tip lacks PACKET.json."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="Skip autonomous window embed (Batch 61 helper still available alone)",
    )
    args = parser.parse_args()

    proc = subprocess.run(
        [sys.executable, str(AUDIT)],
        capture_output=True,
        text=True,
        check=False,
    )
    report: dict = {
        "watched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "audit_exit": proc.returncode,
        "audit_stderr": proc.stderr.strip(),
    }
    if proc.stdout.strip():
        try:
            report["audit"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            report["audit_stdout_raw"] = proc.stdout
    if proc.returncode == 0:
        report["state"] = "ALIGNED"
    elif proc.returncode == 1:
        report["state"] = "MISALIGNED"
    else:
        report["state"] = "TRANSPORT_ERROR"

    if not args.no_window:
        window, _win_ec = _window_payload()
        report["autonomous_window"] = window
        report["route"] = _route_hint(report["state"], window)
    else:
        report["autonomous_window"] = None
        report["route"] = _route_hint(report["state"], None)

    print(json.dumps(report, indent=2, sort_keys=True))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
