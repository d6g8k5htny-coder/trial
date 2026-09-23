#!/usr/bin/env python3
"""Watch whether d6g8k5htny-coder/main default tip has become aligned.

Exit codes:
  0 — ALIGNED (q0 program or Option-B notice on default tip)
  1 — still MISALIGNED
  2 — transport failure

Prints one JSON object. Scientific effect: NONE.
Intended for autonomous timer batches: when exit flips to 0, refresh trial docs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts" / "audit_main_alignment.py"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(AUDIT)],
        capture_output=True,
        text=True,
        check=False,
    )
    report = {
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
    print(json.dumps(report, indent=2, sort_keys=True))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
