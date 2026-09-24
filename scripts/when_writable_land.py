#!/usr/bin/env python3
"""Background lander: poll write access and auto-land Path C when possible.

Loop (default interval 300s):
  1. Exit cleanly if STOP file exists.
  2. Probe write on d6g8k5htny-coder/main; if DENIED → sleep / continue.
  3. Audit alignment:
       MISALIGNED → restore_main_face (Path B) then continue.
       ALIGNED + writable → owner_land_path_c (apply_all on hardening + push).
  4. Always respect lemma_closed=false (owner_land_path_c fail-closed gate).
  5. Log to /tmp/cursor/when_writable_land.log and status JSON under
     /cursor/stores/self/when_writable_land.status.json.

Flags:
  --once       Single iteration then exit (no sleep).
  --dry-run    Decide and log only; never invoke real land scripts.
  --interval N Poll interval seconds (default 300; env WHEN_WRITABLE_INTERVAL).
  --mock-probe / --mock-align  Deterministic states for intent tests.

Token discovery (first existing wins; value never printed):
  1. env MAIN_PUSH_TOKEN
  2. /cursor/stores/self/MAIN_PUSH_TOKEN (file contents)
  3. /workspace/.secrets/MAIN_PUSH_TOKEN (file contents)
Injected into child git/gh/probe/land env as MAIN_PUSH_TOKEN (+ GH_TOKEN /
GITHUB_TOKEN when those are unset).

Scientific effect: NONE. Never flips lemma_closed / prizes / premises /
research status. goal_complete stays false.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "probe_main_write.py"
AUDIT = ROOT / "scripts" / "audit_main_alignment.py"
RESTORE = ROOT / "scripts" / "restore_main_face.sh"
OWNER_C = ROOT / "scripts" / "owner_land_path_c.sh"

DEFAULT_INTERVAL = int(os.environ.get("WHEN_WRITABLE_INTERVAL", "300"))
DEFAULT_LOG = Path(os.environ.get("WHEN_WRITABLE_LOG", "/tmp/cursor/when_writable_land.log"))
DEFAULT_STATUS = Path(
    os.environ.get(
        "WHEN_WRITABLE_STATUS",
        "/cursor/stores/self/when_writable_land.status.json",
    )
)
DEFAULT_STOP = Path(
    os.environ.get(
        "WHEN_WRITABLE_STOP",
        "/cursor/stores/self/when_writable_land.stop",
    )
)

# Token file candidates (after env). Overridable in tests via resolve_main_push_token.
DEFAULT_TOKEN_FILES: tuple[Path, ...] = (
    Path("/cursor/stores/self/MAIN_PUSH_TOKEN"),
    Path("/workspace/.secrets/MAIN_PUSH_TOKEN"),
)


def resolve_main_push_token(
    *,
    env: dict[str, str] | None = None,
    file_candidates: list[Path] | tuple[Path, ...] | None = None,
) -> tuple[str | None, str | None]:
    """Return (token, source_label). Never logs or returns the secret to stdout.

    Priority: env MAIN_PUSH_TOKEN → first existing non-empty token file.
    """
    environ = env if env is not None else os.environ
    env_val = (environ.get("MAIN_PUSH_TOKEN") or "").strip()
    if env_val:
        return env_val, "env:MAIN_PUSH_TOKEN"

    candidates = file_candidates if file_candidates is not None else DEFAULT_TOKEN_FILES
    for path in candidates:
        try:
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if raw:
            return raw, f"file:{path}"
    return None, None


def apply_token_to_env(base_env: dict[str, str], token: str | None) -> dict[str, str]:
    """Copy env and inject token for git/gh/probe without printing it."""
    out = dict(base_env)
    if not token:
        return out
    out["MAIN_PUSH_TOKEN"] = token
    # Mirror for gh / urllib fallbacks used by probe and land scripts.
    if not (out.get("GH_TOKEN") or "").strip():
        out["GH_TOKEN"] = token
    if not (out.get("GITHUB_TOKEN") or "").strip():
        out["GITHUB_TOKEN"] = token
    return out


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _child_env() -> dict[str, str]:
    """Env for probe/audit/land children, with MAIN_PUSH_TOKEN discovery applied."""
    token, _source = resolve_main_push_token()
    return apply_token_to_env(dict(os.environ), token)


def _run_json(cmd: list[str], timeout: int = 180) -> tuple[int, dict, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        cwd=str(ROOT),
        env=_child_env(),
    )
    return proc.returncode, _parse_json_stdout(proc.stdout), (proc.stderr or "").strip()


def _log(log_path: Path, msg: str) -> None:
    line = f"[{_utc_now()}] {msg}"
    print(line, flush=True)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError as exc:
        print(f"[{_utc_now()}] warn: cannot append log {log_path}: {exc}", flush=True)


def _write_status(status_path: Path, payload: dict) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = status_path.with_suffix(status_path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(status_path)


def _stop_requested(stop_path: Path) -> bool:
    return stop_path.is_file()


def _probe(mock: str | None) -> tuple[str, dict]:
    if mock:
        state = mock.upper()
        return state, {"state": state, "mocked": True, "scientific_effect": "NONE"}
    if not PROBE.is_file():
        return "TRANSPORT_ERROR", {"state": "TRANSPORT_ERROR", "detail": "probe_missing"}
    ec, payload, err = _run_json([sys.executable, str(PROBE)], timeout=90)
    state = (payload.get("state") or "").upper()
    if not state:
        if ec == 0:
            state = "WRITABLE"
        elif ec == 1:
            state = "DENIED"
        else:
            state = "TRANSPORT_ERROR"
    if err:
        payload = {**payload, "stderr_tail": err[-500:]}
    return state, payload


def _align(mock: str | None) -> tuple[str, dict]:
    if mock:
        state = mock.upper()
        return state, {"state": state, "mocked": True, "scientific_effect": "NONE"}
    if not AUDIT.is_file():
        return "TRANSPORT_ERROR", {"state": "TRANSPORT_ERROR", "detail": "audit_missing"}
    ec, payload, err = _run_json([sys.executable, str(AUDIT)], timeout=120)
    if ec == 0:
        state = "ALIGNED"
    elif ec == 1:
        state = "MISALIGNED"
    else:
        state = "TRANSPORT_ERROR"
    if err:
        payload = {**payload, "stderr_tail": err[-500:]}
    payload = {**payload, "state": state, "audit_exit": ec}
    return state, payload


def _run_land(cmd: list[str], dry_run: bool, label: str, timeout: int = 900) -> dict:
    detail: dict = {
        "label": label,
        "attempted": False,
        "dry_run": dry_run,
        "cmd": cmd,
        "exit": None,
        "stdout_tail": None,
        "stderr_tail": None,
        "skipped_reason": None,
    }
    if dry_run:
        detail["skipped_reason"] = "dry_run"
        detail["would_run"] = cmd
        return detail
    detail["attempted"] = True
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        cwd=str(ROOT),
        env=_child_env(),
    )
    detail["exit"] = proc.returncode
    detail["stdout_tail"] = (proc.stdout or "")[-3000:]
    detail["stderr_tail"] = (proc.stderr or "")[-2000:]
    return detail


def _one_iteration(
    *,
    dry_run: bool,
    mock_probe: str | None,
    mock_align: str | None,
    batch: str,
    log_path: Path,
) -> dict:
    report: dict = {
        "iterated_at_utc": _utc_now(),
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "flipped_anything": False,
        "dry_run": dry_run,
        "action": "idle",
        "reason": None,
        "probe": None,
        "align": None,
        "land": None,
    }

    probe_state, probe_payload = _probe(mock_probe)
    report["probe"] = {"state": probe_state, "detail": probe_payload}
    _log(log_path, f"probe={probe_state}")

    if probe_state == "DENIED":
        report["action"] = "continue_denied"
        report["reason"] = "write_denied"
        _log(log_path, "action=continue_denied (write DENIED)")
        return report

    if probe_state == "TRANSPORT_ERROR":
        report["action"] = "continue_transport"
        report["reason"] = "probe_transport_error"
        _log(log_path, "action=continue_transport (probe TRANSPORT_ERROR)")
        return report

    if probe_state != "WRITABLE":
        report["action"] = "continue_unknown_probe"
        report["reason"] = f"unexpected_probe_state:{probe_state}"
        _log(log_path, f"action=continue_unknown_probe probe={probe_state}")
        return report

    # Writable: decide Path B restore vs Path C land from alignment.
    align_state, align_payload = _align(mock_align)
    report["align"] = {"state": align_state, "detail": align_payload}
    tip = align_payload.get("default_tip_sha") or align_payload.get("tip_sha")
    _log(log_path, f"align={align_state} tip={tip}")

    if align_state == "TRANSPORT_ERROR":
        report["action"] = "continue_transport"
        report["reason"] = "align_transport_error"
        _log(log_path, "action=continue_transport (align TRANSPORT_ERROR)")
        return report

    if align_state == "MISALIGNED":
        report["action"] = "path_b_restore"
        report["reason"] = "misaligned_writable"
        cmd = ["bash", str(RESTORE), "--batch", str(batch)]
        if dry_run:
            # Certainty-only Path B path in dry mode.
            cmd = ["bash", str(RESTORE), "--dry-run", "--batch", str(batch)]
            # Still mark as dry — do not execute even --dry-run child unless asked;
            # decide-only keeps network out of unit tests with mocks.
            land = _run_land(cmd, dry_run=True, label="restore_main_face_path_b")
        else:
            land = _run_land(cmd, dry_run=False, label="restore_main_face_path_b")
        report["land"] = land
        _log(
            log_path,
            f"action=path_b_restore attempted={land.get('attempted')} "
            f"exit={land.get('exit')} dry_run={dry_run}",
        )
        return report

    if align_state == "ALIGNED":
        report["action"] = "path_c_land"
        report["reason"] = "aligned_writable"
        # owner_land_path_c fail-closed on lemma_closed!=false after apply_all.
        cmd = ["bash", str(OWNER_C)]
        if dry_run:
            land = _run_land(
                ["bash", str(OWNER_C), "--dry-run"],
                dry_run=True,
                label="owner_land_path_c",
            )
            land["gate"] = "lemma_closed=false (owner_land_path_c fail-closed)"
            land["note"] = (
                "Would run owner_land_path_c.sh (apply_all on hardening + push). "
                "Never promotes research status."
            )
        else:
            land = _run_land(cmd, dry_run=False, label="owner_land_path_c", timeout=1200)
            land["gate"] = "lemma_closed=false (owner_land_path_c fail-closed)"
        report["land"] = land
        _log(
            log_path,
            f"action=path_c_land attempted={land.get('attempted')} "
            f"exit={land.get('exit')} dry_run={dry_run} gate=lemma_closed=false",
        )
        return report

    report["action"] = "continue_unknown_align"
    report["reason"] = f"unexpected_align_state:{align_state}"
    _log(log_path, f"action=continue_unknown_align align={align_state}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single iteration then exit (no sleep)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Decide and log only; never invoke real land scripts",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Seconds between polls (default {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--log",
        default=str(DEFAULT_LOG),
        help=f"Append log path (default {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help=f"Status JSON path (default {DEFAULT_STATUS})",
    )
    parser.add_argument(
        "--stop",
        default=str(DEFAULT_STOP),
        help=f"STOP file path (default {DEFAULT_STOP})",
    )
    parser.add_argument(
        "--batch",
        default=os.environ.get("WHEN_WRITABLE_BATCH", "82"),
        help="Batch id passed to restore_main_face (default 82)",
    )
    parser.add_argument(
        "--mock-probe",
        choices=("WRITABLE", "DENIED", "TRANSPORT_ERROR"),
        default=None,
        help="Intent-test: skip live probe; use this state",
    )
    parser.add_argument(
        "--mock-align",
        choices=("ALIGNED", "MISALIGNED", "TRANSPORT_ERROR"),
        default=None,
        help="Intent-test: skip live audit; use this state",
    )
    args = parser.parse_args()

    if args.interval < 0:
        print("when_writable_land: ERROR: --interval must be >= 0", file=sys.stderr)
        return 2

    log_path = Path(args.log)
    status_path = Path(args.status)
    stop_path = Path(args.stop)

    # Resolve once at start; inject into process env so all children see it.
    # Log source label only — never the token value.
    token, token_source = resolve_main_push_token()
    if token:
        os.environ.update(apply_token_to_env(dict(os.environ), token))
        token_note = f"token_source={token_source}"
    else:
        token_note = "token_source=none"

    _log(
        log_path,
        f"start once={args.once} dry_run={args.dry_run} interval={args.interval}s "
        f"batch={args.batch} {token_note} scientific_effect=NONE lemma_closed=false",
    )

    iteration = 0
    last_report: dict = {}
    try:
        while True:
            if _stop_requested(stop_path):
                status = {
                    "updated_at_utc": _utc_now(),
                    "running": False,
                    "stopped": True,
                    "stop_reason": "stop_file",
                    "stop_path": str(stop_path),
                    "iteration": iteration,
                    "scientific_effect": "NONE",
                    "goal_complete": False,
                    "lemma_closed": False,
                    "flipped_anything": False,
                    "last": last_report or None,
                }
                _write_status(status_path, status)
                _log(log_path, f"STOP file present ({stop_path}) — exiting cleanly")
                # Remove stop file is NOT done — owner owns it; leave for inspection.
                return 0

            iteration += 1
            try:
                report = _one_iteration(
                    dry_run=args.dry_run,
                    mock_probe=args.mock_probe,
                    mock_align=args.mock_align,
                    batch=str(args.batch),
                    log_path=log_path,
                )
            except Exception as exc:  # noqa: BLE001 — keep loop alive
                report = {
                    "iterated_at_utc": _utc_now(),
                    "scientific_effect": "NONE",
                    "goal_complete": False,
                    "lemma_closed": False,
                    "flipped_anything": False,
                    "dry_run": args.dry_run,
                    "action": "continue_error",
                    "reason": f"exception:{exc}",
                    "traceback": traceback.format_exc()[-2000:],
                }
                _log(log_path, f"action=continue_error err={exc}")

            last_report = report
            status = {
                "updated_at_utc": _utc_now(),
                "running": not args.once,
                "stopped": False,
                "iteration": iteration,
                "interval_seconds": args.interval,
                "dry_run": args.dry_run,
                "once": args.once,
                "batch": str(args.batch),
                "token_present": bool(token),
                "token_source": token_source or "none",
                "scientific_effect": "NONE",
                "goal_complete": False,
                "lemma_closed": False,
                "flipped_anything": False,
                "tmux_session_hint": "when-writable-land",
                "last": report,
            }
            _write_status(status_path, status)
            _log(
                log_path,
                f"iter={iteration} action={report.get('action')} "
                f"status_written={status_path}",
            )

            if args.once:
                _log(log_path, "once=true — exiting after single iteration")
                return 0

            # Re-check STOP before sleeping so owner can halt promptly.
            if _stop_requested(stop_path):
                continue

            time.sleep(args.interval)
    except KeyboardInterrupt:
        status = {
            "updated_at_utc": _utc_now(),
            "running": False,
            "stopped": True,
            "stop_reason": "keyboard_interrupt",
            "iteration": iteration,
            "scientific_effect": "NONE",
            "goal_complete": False,
            "lemma_closed": False,
            "flipped_anything": False,
            "last": last_report or None,
        }
        _write_status(status_path, status)
        _log(log_path, "KeyboardInterrupt — exiting cleanly")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
