#!/usr/bin/env python3
"""Report autonomous work-window status from agent stores.

Honors permanent mode: when autonomous_window_mode.txt is
PERMANENT_UNTIL_OWNER_INTERVENES, never hard-stop on elapsed wall-clock
(even if started_at + window_seconds would otherwise expire). Stop only when
the owner intervenes (mode file cleared / changed).

Exit codes:
  0 — window open (continue work)
  1 — window expired (hard-stop; finite mode only)
  2 — store/config error

Prints one JSON object. Scientific effect: NONE.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MODE_FILE = "autonomous_window_mode.txt"
STARTED_FILE = "autonomous_48h_started_at.txt"
WINDOW_SECONDS_FILE = "autonomous_48h_window_seconds.txt"
PERMANENT_FILE = "autonomous_permanent_extension.txt"
PERMANENT_MODE = "PERMANENT_UNTIL_OWNER_INTERVENES"
DEFAULT_WINDOW_SECONDS = 172800  # legacy 48h


def _store_candidates() -> list[Path]:
    """Prefer explicit AUTONOMOUS_STORE_DIR; never treat Path('') as cwd."""
    out: list[Path] = []
    env = (os.environ.get("AUTONOMOUS_STORE_DIR") or "").strip()
    if env:
        out.append(Path(env))
    out.append(Path("/cursor/stores/self"))
    out.append(Path.home() / ".cursor" / "stores" / "self")
    return out


def _find_store() -> Path | None:
    for candidate in _store_candidates():
        # Prefer a dir that already has the mode or started_at file.
        if not candidate.is_dir():
            continue
        if (candidate / MODE_FILE).is_file() or (candidate / STARTED_FILE).is_file():
            return candidate
    for candidate in _store_candidates():
        if candidate.is_dir():
            return candidate
    return None


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _parse_utc(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def main() -> int:
    now = datetime.now(timezone.utc)
    store = _find_store()
    report: dict = {
        "checked_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "store_dir": str(store) if store else None,
    }
    if store is None:
        report["state"] = "STORE_MISSING"
        report["within_window"] = False
        report["hard_stop"] = True
        report["reason"] = "no autonomous store directory found"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    mode_raw = _read_text(store / MODE_FILE) or "FINITE_48H"
    mode = mode_raw.splitlines()[0].strip() if mode_raw else "FINITE_48H"
    started_raw = _read_text(store / STARTED_FILE)
    window_raw = _read_text(store / WINDOW_SECONDS_FILE)
    permanent_note = _read_text(store / PERMANENT_FILE)

    report["window_mode"] = mode
    report["started_at_utc"] = started_raw
    report["permanent_extension_note_present"] = bool(permanent_note)

    try:
        window_seconds = int(window_raw) if window_raw else DEFAULT_WINDOW_SECONDS
    except ValueError:
        report["state"] = "BAD_WINDOW_SECONDS"
        report["within_window"] = False
        report["hard_stop"] = True
        report["reason"] = f"invalid window seconds: {window_raw!r}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    report["window_seconds"] = window_seconds

    if mode == PERMANENT_MODE:
        report["state"] = "PERMANENT_OPEN"
        report["within_window"] = True
        report["hard_stop"] = False
        report["stop_condition"] = "owner_intervene_only"
        report["finale"] = False
        if started_raw:
            try:
                started = _parse_utc(started_raw)
                elapsed = max(0.0, (now - started).total_seconds())
                report["elapsed_seconds"] = int(elapsed)
                report["elapsed_hours"] = round(elapsed / 3600.0, 3)
            except ValueError:
                report["elapsed_parse_error"] = started_raw
        report["reason"] = (
            "owner extended permanently until intervene; "
            "do not 48h-finale; continue autonomous batches"
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    # Finite / legacy 48h mode
    if not started_raw:
        report["state"] = "STARTED_AT_MISSING"
        report["within_window"] = False
        report["hard_stop"] = True
        report["reason"] = f"missing {STARTED_FILE} in finite mode"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    try:
        started = _parse_utc(started_raw)
    except ValueError as exc:
        report["state"] = "BAD_STARTED_AT"
        report["within_window"] = False
        report["hard_stop"] = True
        report["reason"] = f"cannot parse started_at: {exc}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    elapsed = max(0.0, (now - started).total_seconds())
    remaining = window_seconds - elapsed
    report["elapsed_seconds"] = int(elapsed)
    report["elapsed_hours"] = round(elapsed / 3600.0, 3)
    report["remaining_seconds"] = int(remaining)
    report["remaining_hours"] = round(remaining / 3600.0, 3)
    report["stop_condition"] = "wall_clock_window"

    if remaining <= 0:
        report["state"] = "EXPIRED"
        report["within_window"] = False
        report["hard_stop"] = True
        report["finale"] = True
        report["reason"] = "finite window elapsed — hard-stop; leave finale summary"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    report["state"] = "OPEN"
    report["within_window"] = True
    report["hard_stop"] = False
    report["finale"] = False
    report["reason"] = "finite window still open"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
