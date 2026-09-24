#!/usr/bin/env python3
"""Background lander: poll write access and auto-land Path C when possible.

Loop (default interval 300s):
  1. Exit cleanly if STOP file exists.
  2. Call GET /installation/repositories; set status install_has_main true/false.
     If install_has_main flips false→true, attempt Path C immediately this cycle.
  3. Probe write on d6g8k5htny-coder/main; if DENIED (and no install flip) →
     if a MAIN_PUSH_TOKEN file appeared at a well-known path, fire trial
     repository_dispatch land-path-c-on-main (--apply) once, then sleep.
  4. Audit alignment:
       MISALIGNED → restore_main_face (Path B) then continue.
       ALIGNED + writable → owner_land_path_c (apply_all on hardening + push).
  5. Always respect lemma_closed=false (owner_land_path_c fail-closed gate).
  6. Log to /tmp/cursor/when_writable_land.log and status JSON under
     /cursor/stores/self/when_writable_land.status.json.

Flags:
  --once       Single iteration then exit (no sleep).
  --dry-run    Decide and log only; never invoke real land scripts.
  --interval N Poll interval seconds (default 300; env WHEN_WRITABLE_INTERVAL).
  --mock-probe / --mock-align / --mock-install-has-main  Intent-test states.

Token discovery (first existing wins; value never printed):
  1. env MAIN_PUSH_TOKEN
  2. /cursor/stores/self/MAIN_PUSH_TOKEN (file contents)
  3. /workspace/.secrets/MAIN_PUSH_TOKEN (file contents)
  4. /tmp/gh-dylan-auth/access_token (device-flow user token after authorize)
Injected into child git/gh/probe/land env as MAIN_PUSH_TOKEN (+ GH_TOKEN /
GITHUB_TOKEN when those are unset).

Batch 140 — repository_dispatch when token file appears:
  Well-known MAIN_PUSH_TOKEN file paths (drop a PAT here; value never logged):
    /cursor/stores/self/MAIN_PUSH_TOKEN
    /workspace/.secrets/MAIN_PUSH_TOKEN
    /tmp/gh-dylan-auth/access_token
  When a file at one of those paths appears (or flips absent→present) while
  direct main write is still DENIED, this lander fires once:
    scripts/dispatch_land_path_c.sh --apply
  which POSTs repository_dispatch type=land-path-c-on-main on trial.
  Apply land still needs trial Actions secret MAIN_PUSH_TOKEN; the file drop
  is the agent-side signal to attempt that channel (W3f is Contents:write).

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
DISPATCH_C = ROOT / "scripts" / "dispatch_land_path_c.sh"

MAIN_FULL = "d6g8k5htny-coder/main"
INSTALL_REPOS_PATH = "/installation/repositories"
# Documented drop paths for MAIN_PUSH_TOKEN (Batch 140 repository_dispatch).
WELL_KNOWN_TOKEN_PATHS: tuple[str, ...] = (
    "/cursor/stores/self/MAIN_PUSH_TOKEN",
    "/workspace/.secrets/MAIN_PUSH_TOKEN",
    "/tmp/gh-dylan-auth/access_token",
)

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
# Batch 132: also load renewed device-flow user token so Path C lands without
# a separate MAIN_PUSH_TOKEN drop once Dylan authorizes at github.com/login/device.
DEFAULT_TOKEN_FILES: tuple[Path, ...] = (
    Path("/cursor/stores/self/MAIN_PUSH_TOKEN"),
    Path("/workspace/.secrets/MAIN_PUSH_TOKEN"),
    Path("/tmp/gh-dylan-auth/access_token"),
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


def _read_status_json(status_path: Path) -> dict:
    try:
        if not status_path.is_file():
            return {}
        data = json.loads(status_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _read_prev_install_has_main(status_path: Path) -> bool | None:
    """Previous cycle's install_has_main from status JSON (None if unknown)."""
    data = _read_status_json(status_path)
    if not data:
        return None
    if "install_has_main" in data:
        val = data["install_has_main"]
        if val is None:
            return None
        return bool(val)
    last = data.get("last") or {}
    if "install_has_main" in last:
        val = last["install_has_main"]
        if val is None:
            return None
        return bool(val)
    return None


def _read_prev_token_present(status_path: Path) -> bool | None:
    """Previous cycle's token_present (None if unknown)."""
    data = _read_status_json(status_path)
    if not data:
        return None
    if "token_present" in data:
        return bool(data["token_present"])
    return None


def _read_last_dispatch_token_source(status_path: Path) -> str | None:
    """Token source label already used for a repository_dispatch --apply."""
    data = _read_status_json(status_path)
    if not data:
        return None
    val = data.get("last_dispatch_token_source")
    if isinstance(val, str) and val:
        return val
    last = data.get("last") or {}
    val = last.get("dispatch_token_source") if isinstance(last, dict) else None
    return val if isinstance(val, str) and val else None


def token_file_present(
    file_candidates: list[Path] | tuple[Path, ...] | None = None,
) -> tuple[bool, str | None]:
    """Return (present, path_str) for first non-empty well-known token file.

    Does not read env. Never returns file contents.
    """
    candidates = file_candidates if file_candidates is not None else DEFAULT_TOKEN_FILES
    for path in candidates:
        try:
            if path.is_file() and path.read_text(encoding="utf-8").strip():
                return True, str(path)
        except OSError:
            continue
    return False, None


def try_repository_dispatch_path_c(
    *,
    dry_run: bool,
    log_path: Path,
    apply: bool = True,
) -> dict:
    """Fire trial repository_dispatch land-path-c-on-main via helper script.

    apply=True → dispatch_land_path_c.sh --apply (needs trial secret for land).
    Never prints tokens. Scientific effect NONE.
    """
    detail: dict = {
        "label": "repository_dispatch_land_path_c",
        "attempted": False,
        "dry_run": dry_run,
        "apply": apply,
        "exit": None,
        "stdout_tail": None,
        "stderr_tail": None,
        "skipped_reason": None,
        "script": str(DISPATCH_C),
        "event_type": "land-path-c-on-main",
        "well_known_token_paths": list(WELL_KNOWN_TOKEN_PATHS),
    }
    if not DISPATCH_C.is_file():
        detail["skipped_reason"] = "dispatch_script_missing"
        return detail
    cmd = ["bash", str(DISPATCH_C)]
    if apply:
        cmd.append("--apply")
    else:
        cmd.append("--dry-run")
    if dry_run:
        detail["skipped_reason"] = "dry_run"
        detail["would_run"] = cmd
        _log(log_path, f"would repository_dispatch {' '.join(cmd)}")
        return detail
    detail["attempted"] = True
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
        cwd=str(ROOT),
        env=_child_env(),
    )
    detail["exit"] = proc.returncode
    detail["stdout_tail"] = (proc.stdout or "")[-2000:]
    detail["stderr_tail"] = (proc.stderr or "")[-1500:]
    _log(
        log_path,
        f"repository_dispatch apply={apply} exit={proc.returncode} "
        f"attempted=true event=land-path-c-on-main",
    )
    return detail


def check_installation_repositories(
    *,
    mock: bool | None = None,
) -> tuple[bool | None, dict]:
    """GET /installation/repositories → (install_has_main, detail).

    install_has_main is True iff d6g8k5htny-coder/main is listed; None on
    transport failure. Prefer probe_main_write.check_installation_repositories
    when available; fall back to ``gh api``.
    """
    if mock is not None:
        return mock, {
            "mocked": True,
            "install_has_main": mock,
            "endpoint": INSTALL_REPOS_PATH,
            "names": [MAIN_FULL] if mock else ["d6g8k5htny-coder/trial"],
        }

    # Prefer shared helper from probe_main_write (same token discovery).
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("probe_main_write", PROBE)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            helper = getattr(mod, "check_installation_repositories", None)
            if callable(helper):
                detail = helper()
                return detail.get("install_has_main"), detail
    except Exception:  # noqa: BLE001 — fall through to gh
        pass

    proc = subprocess.run(
        ["gh", "api", INSTALL_REPOS_PATH],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
        cwd=str(ROOT),
        env=_child_env(),
    )
    detail: dict = {
        "endpoint": INSTALL_REPOS_PATH,
        "install_has_main": None,
        "http_status": None,
        "names": [],
    }
    raw = (proc.stdout or "").strip()
    if proc.returncode != 0:
        detail["error"] = (proc.stderr or raw or f"gh exit {proc.returncode}")[-500:]
        detail["http_status"] = 403 if "403" in (proc.stderr or "") else None
        return None, detail
    try:
        body = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        detail["error"] = "json_decode"
        detail["raw_tail"] = raw[-500:]
        return None, detail
    repos = body.get("repositories") or []
    names = [
        str(r.get("full_name"))
        for r in repos
        if isinstance(r, dict) and r.get("full_name")
    ]
    detail["http_status"] = 200
    detail["total_count"] = body.get("total_count")
    detail["repository_selection"] = body.get("repository_selection")
    detail["names"] = names
    has_main = MAIN_FULL in names
    detail["install_has_main"] = has_main
    return has_main, detail


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
    mock_install_has_main: bool | None,
    batch: str,
    log_path: Path,
    status_path: Path,
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
        "install_has_main": None,
        "install_has_main_flipped_true": False,
        "installation_repositories": None,
        "token_file_present": False,
        "token_file_path": None,
        "token_appeared": False,
        "dispatch_token_source": None,
    }

    prev_install = _read_prev_install_has_main(status_path)
    prev_token_present = _read_prev_token_present(status_path)
    last_dispatch_src = _read_last_dispatch_token_source(status_path)
    file_present, file_path = token_file_present()
    report["token_file_present"] = file_present
    report["token_file_path"] = file_path
    # Fire once when a well-known token file is present and we have not yet
    # dispatched for that path (absent/unknown → present, or first sighting).
    token_appeared = False
    if file_present and file_path:
        dispatch_src_candidate = f"file:{file_path}"
        if last_dispatch_src != dispatch_src_candidate and prev_token_present is not True:
            token_appeared = True
    report["token_appeared"] = token_appeared

    install_has_main, install_detail = check_installation_repositories(
        mock=mock_install_has_main,
    )
    report["install_has_main"] = install_has_main
    report["installation_repositories"] = install_detail
    flipped = prev_install is False and install_has_main is True
    report["install_has_main_flipped_true"] = flipped
    report["prev_install_has_main"] = prev_install
    _log(
        log_path,
        f"install_has_main={install_has_main} prev={prev_install} "
        f"flipped_true={flipped} names={install_detail.get('names')} "
        f"token_file_present={file_present} token_appeared={report['token_appeared']}",
    )

    probe_state, probe_payload = _probe(mock_probe)
    # Prefer install_has_main from live probe JSON when not mocked.
    if mock_install_has_main is None and "install_has_main" in probe_payload:
        probe_install = probe_payload.get("install_has_main")
        if probe_install is not None:
            install_has_main = bool(probe_install)
            report["install_has_main"] = install_has_main
            flipped = prev_install is False and install_has_main is True
            report["install_has_main_flipped_true"] = flipped
        if isinstance(probe_payload.get("installation_repositories"), dict):
            report["installation_repositories"] = probe_payload["installation_repositories"]

    report["probe"] = {"state": probe_state, "detail": probe_payload}
    _log(log_path, f"probe={probe_state}")

    if probe_state == "DENIED" and not flipped:
        # Batch 140: MAIN_PUSH_TOKEN file appeared → try trial repository_dispatch.
        if report["token_appeared"] and file_present and file_path:
            dispatch_src = f"file:{file_path}"
            if last_dispatch_src == dispatch_src:
                report["action"] = "continue_denied"
                report["reason"] = "write_denied_dispatch_already_fired"
                _log(
                    log_path,
                    "action=continue_denied (write DENIED; repository_dispatch "
                    "already fired for this token file)",
                )
                return report
            report["action"] = "path_c_repository_dispatch"
            report["reason"] = "main_push_token_file_appeared_write_denied"
            report["dispatch_token_source"] = dispatch_src
            land = try_repository_dispatch_path_c(
                dry_run=dry_run, log_path=log_path, apply=True
            )
            land["triggered_by"] = "MAIN_PUSH_TOKEN_file_appeared"
            land["token_file_path"] = file_path
            land["well_known_token_paths"] = list(WELL_KNOWN_TOKEN_PATHS)
            land["note"] = (
                "Fired repository_dispatch land-path-c-on-main --apply because a "
                "MAIN_PUSH_TOKEN file appeared while direct main write is DENIED. "
                "Actions apply still needs trial secret MAIN_PUSH_TOKEN."
            )
            report["land"] = land
            _log(
                log_path,
                f"action=path_c_repository_dispatch attempted={land.get('attempted')} "
                f"exit={land.get('exit')} dry_run={dry_run} "
                f"token_file={file_path}",
            )
            return report
        report["action"] = "continue_denied"
        report["reason"] = "write_denied"
        _log(log_path, "action=continue_denied (write DENIED)")
        return report

    if probe_state == "DENIED" and flipped:
        # Install just gained main — re-probe once, then attempt Path C if writable.
        _log(log_path, "install_has_main flipped true — re-probe then Path C attempt")
        probe_state, probe_payload = _probe(mock_probe)
        report["probe"] = {
            "state": probe_state,
            "detail": probe_payload,
            "reprobe_after_install_flip": True,
        }
        _log(log_path, f"reprobe_after_install_flip={probe_state}")
        if probe_state != "WRITABLE":
            # Still denied after install flip — try dispatch if token file present.
            if file_present and file_path:
                dispatch_src = f"file:{file_path}"
                if last_dispatch_src != dispatch_src:
                    report["action"] = "path_c_repository_dispatch"
                    report["reason"] = "install_has_main_true_write_denied_token_file"
                    report["dispatch_token_source"] = dispatch_src
                    land = try_repository_dispatch_path_c(
                        dry_run=dry_run, log_path=log_path, apply=True
                    )
                    land["triggered_by"] = "install_flip_plus_MAIN_PUSH_TOKEN_file"
                    land["token_file_path"] = file_path
                    report["land"] = land
                    _log(
                        log_path,
                        "action=path_c_repository_dispatch after install flip "
                        f"exit={land.get('exit')}",
                    )
                    return report
            report["action"] = "continue_denied_after_install_flip"
            report["reason"] = "install_has_main_true_but_write_still_denied"
            _log(
                log_path,
                "action=continue_denied_after_install_flip "
                "(install has main; write still DENIED)",
            )
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

    # Writable (or install flip + writable after re-probe): Path B vs Path C.
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
        report["reason"] = (
            "misaligned_writable_after_install_flip" if flipped else "misaligned_writable"
        )
        cmd = ["bash", str(RESTORE), "--batch", str(batch)]
        if dry_run:
            cmd = ["bash", str(RESTORE), "--dry-run", "--batch", str(batch)]
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
        report["reason"] = (
            "install_has_main_flipped_true" if flipped else "aligned_writable"
        )
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
        if flipped:
            land["triggered_by"] = "install_has_main_flipped_true"
        report["land"] = land
        _log(
            log_path,
            f"action=path_c_land attempted={land.get('attempted')} "
            f"exit={land.get('exit')} dry_run={dry_run} gate=lemma_closed=false "
            f"flipped_install={flipped}",
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
    parser.add_argument(
        "--mock-install-has-main",
        choices=("true", "false"),
        default=None,
        help="Intent-test: skip live /installation/repositories; force true/false",
    )
    args = parser.parse_args()

    if args.interval < 0:
        print("when_writable_land: ERROR: --interval must be >= 0", file=sys.stderr)
        return 2

    log_path = Path(args.log)
    status_path = Path(args.status)
    stop_path = Path(args.stop)
    mock_install: bool | None = None
    if args.mock_install_has_main is not None:
        mock_install = args.mock_install_has_main == "true"

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
        f"batch={args.batch} {token_note} scientific_effect=NONE lemma_closed=false "
        f"install_repos_poll=true",
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
                    "install_has_main": (last_report or {}).get("install_has_main"),
                    "last": last_report or None,
                }
                _write_status(status_path, status)
                _log(log_path, f"STOP file present ({stop_path}) — exiting cleanly")
                return 0

            iteration += 1
            try:
                report = _one_iteration(
                    dry_run=args.dry_run,
                    mock_probe=args.mock_probe,
                    mock_align=args.mock_align,
                    mock_install_has_main=mock_install,
                    batch=str(args.batch),
                    log_path=log_path,
                    status_path=status_path,
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
                    "install_has_main": None,
                    "install_has_main_flipped_true": False,
                }
                _log(log_path, f"action=continue_error err={exc}")

            last_report = report
            dispatch_src = report.get("dispatch_token_source")
            status = {
                "updated_at_utc": _utc_now(),
                "running": not args.once,
                "stopped": False,
                "iteration": iteration,
                "interval_seconds": args.interval,
                "dry_run": args.dry_run,
                "once": args.once,
                "batch": str(args.batch),
                "token_present": bool(token) or bool(report.get("token_file_present")),
                "token_source": token_source or (
                    f"file:{report.get('token_file_path')}"
                    if report.get("token_file_path")
                    else "none"
                ),
                "token_file_present": bool(report.get("token_file_present")),
                "token_file_path": report.get("token_file_path"),
                "last_dispatch_token_source": dispatch_src
                or _read_last_dispatch_token_source(status_path),
                "scientific_effect": "NONE",
                "goal_complete": False,
                "lemma_closed": False,
                "flipped_anything": False,
                "install_has_main": report.get("install_has_main"),
                "install_has_main_flipped_true": report.get(
                    "install_has_main_flipped_true", False
                ),
                "tmux_session_hint": "when-writable-land",
                "well_known_token_paths": list(WELL_KNOWN_TOKEN_PATHS),
                "last": report,
            }
            _write_status(status_path, status)
            _log(
                log_path,
                f"iter={iteration} action={report.get('action')} "
                f"install_has_main={report.get('install_has_main')} "
                f"status_written={status_path}",
            )

            if args.once:
                _log(log_path, "once=true — exiting after single iteration")
                return 0

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
            "install_has_main": (last_report or {}).get("install_has_main"),
            "last": last_report or None,
        }
        _write_status(status_path, status)
        _log(log_path, "KeyboardInterrupt — exiting cleanly")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
