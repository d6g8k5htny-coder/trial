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
       ALIGNED + writable → owner_open_path_c_pr.sh when present (bundle am →
       open PR into hardening); else owner_land_path_c (apply_all + push/PR).
  5. Always respect lemma_closed=false (Path C scripts fail-closed).
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
  is the agent-side signal to attempt that channel.
  Batch 141: W3f dry-run repository_dispatch on *trial* is a false_positive for
  main write (path_b_ready must stay false until apply + MAIN_PUSH_TOKEN).

Batch 157 — PATH_C_BLOCKED reason codes (logged; research untouched):
  When Path C cannot land (write DENIED / tip drift / apply fail), log a clear
  machine-readable line:
    PATH_C_BLOCKED=NO_TOKEN
    PATH_C_BLOCKED=TIP_DRIFT
    PATH_C_BLOCKED=APPLY_FAIL
  or a comma-joined combination (e.g. PATH_C_BLOCKED=NO_TOKEN,TIP_DRIFT).
  Codes:
    NO_TOKEN   — no MAIN_PUSH_TOKEN / device-flow token for main write
    TIP_DRIFT  — portable BASE_TIP.txt ≠ live hardening tip
    APPLY_FAIL — apply_all --check failed on the current tip
  Never flips lemma_closed / prizes / premises / research status.

Batch 238 — follow-on 0018 auto-land (do not idle-suppress):
  path_c_landed=true (PR #64 base stack) must NOT force idle_path_c_done while
  path_c_0018_landed is false / unmarked. 0018 couples to top-level
  attestations/ (main PR #70). path_c_followon_pending() gates the idle path;
  when pending, lander falls through to path_c_land with
  reason=path_c_followon_pending. Never flips research status.

Batch 239 — future deltas (0019+) auto-land:
  path_c_followon_pending() scans portable/patches for any 00NN ≥ 0018 whose
  path_c_00NN_landed marker is not True. Cutting 0019+ must re-arm Path C land
  even when path_c_0018_landed=true / path_c_landed=true. Never flips research.

Batch 240 — MAIN_PUSH_TOKEN + auto Path B restore:
  Token discovery (env / well-known files) is injected into every child env at
  start. If default tip is ever MISALIGNED while write is WRITABLE, this lander
  auto-runs restore_main_face.sh (Path B) before any Path C work — same contract
  as aligned_drift_watch.py auto-restore. Token value never printed. Never flips
  research status.

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
# Batch 151/153: preferred Path C open-PR path (bundle am → cursor/path-c-portable-fixes).
OWNER_OPEN_PR = ROOT / "scripts" / "owner_open_path_c_pr.sh"
DISPATCH_C = ROOT / "scripts" / "dispatch_land_path_c.sh"

MAIN_FULL = "d6g8k5htny-coder/main"
HARDENING_REF = "chatgpt/drive-github-hardening-20260919"
INSTALL_REPOS_PATH = "/installation/repositories"
# Documented drop paths for MAIN_PUSH_TOKEN (Batch 140 repository_dispatch).
WELL_KNOWN_TOKEN_PATHS: tuple[str, ...] = (
    "/cursor/stores/self/MAIN_PUSH_TOKEN",
    "/workspace/.secrets/MAIN_PUSH_TOKEN",
    "/tmp/gh-dylan-auth/access_token",
)
# Batch 157: stable Path C blocked reason codes (never promote research).
PATH_C_BLOCKED_NO_TOKEN = "NO_TOKEN"
PATH_C_BLOCKED_TIP_DRIFT = "TIP_DRIFT"
PATH_C_BLOCKED_APPLY_FAIL = "APPLY_FAIL"
PATH_C_BLOCKED_CODES: tuple[str, ...] = (
    PATH_C_BLOCKED_NO_TOKEN,
    PATH_C_BLOCKED_TIP_DRIFT,
    PATH_C_BLOCKED_APPLY_FAIL,
)
BASE_TIP_FILE = ROOT / "portable" / "patches" / "BASE_TIP.txt"
PATH_C_STATUS_FILE = ROOT / "portable" / "PATH_C_STATUS.json"
VERIFY_FILE = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"
APPLY_ALL_SH = ROOT / "portable" / "patches" / "apply_all.sh"
HARDENING_CACHE = Path(
    os.environ.get(
        "WHEN_WRITABLE_HARDENING_CACHE",
        "/tmp/cursor/path-c-hardening-cache",
    )
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


def _ignore_file_tokens(environ: dict[str, str] | None = None) -> bool:
    """Batch 232: PATH_C_IGNORE_FILE_TOKENS=1 skips well-known file drops (tests)."""
    env = environ if environ is not None else os.environ
    return (env.get("PATH_C_IGNORE_FILE_TOKENS") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
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

    if _ignore_file_tokens(environ):
        return None, None

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

    Does not read env token values. Never returns file contents.
    Honors PATH_C_IGNORE_FILE_TOKENS=1 (Batch 232 test isolation).
    """
    if _ignore_file_tokens():
        return False, None
    candidates = file_candidates if file_candidates is not None else DEFAULT_TOKEN_FILES
    for path in candidates:
        try:
            if path.is_file() and path.read_text(encoding="utf-8").strip():
                return True, str(path)
        except OSError:
            continue
    return False, None


def parse_base_tip_sha(tip_file: Path | None = None) -> str | None:
    """Extract hex SHA from portable/patches/BASE_TIP.txt (7–40 chars)."""
    path = tip_file if tip_file is not None else BASE_TIP_FILE
    try:
        line = path.read_text(encoding="utf-8").strip().splitlines()[0]
    except (OSError, IndexError):
        return None
    import re

    m = re.search(r"(?i)\b([0-9a-f]{40})\b", line)
    if m:
        return m.group(1).lower()
    m = re.search(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)", line)
    if m:
        return m.group(1).lower()
    parts = line.split()
    return parts[-1].lower() if parts else None


def fetch_live_hardening_sha(*, timeout: int = 20) -> str | None:
    """Return live hardening tip SHA via GitHub API (no token printed)."""
    import urllib.error
    import urllib.request

    url = (
        f"https://api.github.com/repos/{MAIN_FULL}/git/ref/heads/"
        f"{HARDENING_REF}"
    )
    headers = {"Accept": "application/json", "User-Agent": "when_writable_land"}
    token, _ = resolve_main_push_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None
    sha = (data.get("object") or {}).get("sha")
    return sha.lower() if isinstance(sha, str) and sha else None


def tip_matches_base(base_sha: str | None, live_sha: str | None) -> bool | None:
    """True/False when both known; None if either missing."""
    if not base_sha or not live_sha:
        return None
    b = base_sha.lower()
    live = live_sha.lower()
    if len(b) == 40:
        return live == b
    if 7 <= len(b) < 40:
        return live.startswith(b)
    return None


def path_c_followon_pending() -> tuple[bool, dict]:
    """Detect pending eng follow-ons (0018+) idle must not suppress.

    Path C base stack may already be on tip (PR #64 → path_c_landed=true) while
    a follow-on patch still needs auto-land once tip prerequisites exist
    (0018 requires top-level attestations/ from main PR #70; 0019+ are tip
    ResourceWarning / eng deltas cut after 0018).

    Batch 239: scan portable/patches for any 00NN (≥0018) patch whose
    path_c_00NN_landed marker is not True in VERIFY / PATH_C_STATUS / newest
    BATCH briefs. Hardcoded 0018-only idle would swallow future deltas.

    Never flips research. Returns (pending, detail).
    pending=True → when_writable must fall through to path_c_land, not idle.
    """
    detail: dict = {
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "followons": [],
        "sources": [],
        "batch": "239",
    }
    patches_dir = ROOT / "portable" / "patches"
    followon_ids: list[str] = []
    if patches_dir.is_dir():
        for path in sorted(patches_dir.glob("*.patch")):
            name = path.name
            # Match 0018+, skip obsolete 0005-pre17 style and non-numbered.
            if len(name) < 4 or not name[:4].isdigit():
                continue
            pid = name[:4]
            try:
                n = int(pid)
            except ValueError:
                continue
            if n < 18:
                continue
            followon_ids.append(pid)
    # Deduplicate while preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for pid in followon_ids:
        if pid in seen:
            continue
        seen.add(pid)
        ordered.append(pid)
    followon_ids = ordered

    if not followon_ids:
        detail["skipped_reason"] = "no_followon_patches_ge_0018"
        return False, detail

    def _marker_for(data: dict, pid: str):
        return data.get(f"path_c_{pid}_landed")

    pending_ids: list[str] = []
    resolved_ids: list[str] = []

    # Merge markers from VERIFY / PATH_C_STATUS / newest briefs (first True wins).
    marker_map: dict[str, bool | None] = {pid: None for pid in followon_ids}
    marker_sources: dict[str, str] = {}

    def _ingest(label: str, data: dict) -> None:
        for pid in followon_ids:
            key = f"path_c_{pid}_landed"
            if key not in data:
                continue
            marker = data.get(key)
            detail["sources"].append({"file": label, key: marker})
            if marker is True:
                marker_map[pid] = True
                marker_sources[pid] = f"{label}:{key}=true"
            elif marker is False and marker_map[pid] is not True:
                marker_map[pid] = False
                marker_sources.setdefault(pid, f"{label}:{key}=false")

    for label, path in (
        ("VERIFY.json", VERIFY_FILE),
        ("PATH_C_STATUS.json", PATH_C_STATUS_FILE),
    ):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            detail["sources"].append({"file": label, "error": str(exc)})
            continue
        _ingest(label, data)

    briefs = sorted(
        (ROOT / "portable").glob("BATCH*_BRIEF.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for brief in briefs[:8]:
        try:
            data = json.loads(brief.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # Only ingest briefs that mention at least one follow-on marker.
        if not any(f"path_c_{pid}_landed" in data for pid in followon_ids):
            continue
        _ingest(brief.name, data)
        break  # newest brief with markers is enough

    for pid in followon_ids:
        marker = marker_map.get(pid)
        if marker is True:
            resolved_ids.append(pid)
            detail["followons"].append(
                {
                    "id": pid,
                    "pending": False,
                    "reason": marker_sources.get(pid, f"path_c_{pid}_landed=true"),
                }
            )
        else:
            # Missing marker OR explicit false → pending (patch on disk needs land).
            pending_ids.append(pid)
            reason = marker_sources.get(pid)
            if reason is None:
                reason = f"{pid}_patch_present_no_landed_marker"
            detail["followons"].append(
                {
                    "id": pid,
                    "pending": True,
                    "reason": reason,
                }
            )

    detail["pending_ids"] = pending_ids
    detail["resolved_ids"] = resolved_ids
    detail["followon_patch_ids"] = followon_ids
    if pending_ids:
        return True, detail
    return False, detail


def path_c_already_landed() -> tuple[bool, dict]:
    """Batch 231: Path C DONE on hardening (PR #64) — idle lander; prefer drift watch.

    Reads VERIFY.json / PATH_C_STATUS.json. Never flips research. Returns
    (landed, detail). When landed, when_writable_land must not re-open Path C
    unless follow-on patches (0018+) are still pending.
    """
    detail: dict = {"sources": []}
    for label, path in (
        ("VERIFY.json", VERIFY_FILE),
        ("PATH_C_STATUS.json", PATH_C_STATUS_FILE),
    ):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            detail["sources"].append({"file": label, "error": str(exc)})
            continue
        landed = data.get("path_c_landed") is True
        detail["sources"].append(
            {
                "file": label,
                "path_c_landed": landed,
                "base_tip": data.get("base_tip_sha")
                or data.get("base_tip")
                or data.get("tip"),
            }
        )
        if landed:
            detail["path_c_landed"] = True
            detail["lemma_closed"] = data.get("lemma_closed", False)
            detail["scientific_effect"] = data.get("scientific_effect", "NONE")
            detail["next_focus"] = "tip-sync+drift+no-flip"
            return True, detail
    detail["path_c_landed"] = False
    return False, detail


def classify_path_c_blocked(
    *,
    has_token: bool,
    tip_matches: bool | None = None,
    apply_ok: bool | None = None,
) -> list[str]:
    """Return PATH_C_BLOCKED reason codes (NO_TOKEN / TIP_DRIFT / APPLY_FAIL).

    Scientific effect NONE — classification only; never flips research.
    """
    reasons: list[str] = []
    if not has_token:
        reasons.append(PATH_C_BLOCKED_NO_TOKEN)
    if tip_matches is False:
        reasons.append(PATH_C_BLOCKED_TIP_DRIFT)
    if apply_ok is False:
        reasons.append(PATH_C_BLOCKED_APPLY_FAIL)
    return reasons


def format_path_c_blocked(reasons: list[str]) -> str:
    """Machine-readable PATH_C_BLOCKED=CODE[,CODE] log token."""
    if not reasons:
        return "PATH_C_BLOCKED=NONE"
    # Preserve stable order from PATH_C_BLOCKED_CODES.
    ordered = [c for c in PATH_C_BLOCKED_CODES if c in reasons]
    for r in reasons:
        if r not in ordered:
            ordered.append(r)
    return "PATH_C_BLOCKED=" + ",".join(ordered)


def assess_path_c_readiness(
    *,
    skip: bool = False,
    check_apply: bool | None = None,
) -> tuple[bool | None, bool | None, dict]:
    """Return (tip_matches, apply_ok, detail). Soft-fails to (None, None, …).

    tip: BASE_TIP vs live hardening. apply: apply_all --check on a cached clone
    when tip matches (disabled when skip=True or check_apply=False).
    """
    detail: dict = {"skipped": bool(skip), "scientific_effect": "NONE"}
    if skip:
        return None, None, detail

    base_sha = parse_base_tip_sha()
    live_sha = fetch_live_hardening_sha()
    matches = tip_matches_base(base_sha, live_sha)
    detail.update(
        {
            "base_tip_sha": base_sha,
            "live_hardening_sha": live_sha,
            "tip_matches_base": matches,
        }
    )

    do_apply = check_apply
    if do_apply is None:
        do_apply = os.environ.get("WHEN_WRITABLE_CHECK_APPLY", "1") != "0"

    apply_ok: bool | None = None
    if matches is True and do_apply and APPLY_ALL_SH.is_file():
        apply_ok, apply_detail = _apply_all_check_cached(live_sha or base_sha or "")
        detail["apply_check"] = apply_detail
    elif matches is False:
        apply_ok = None  # tip drift dominates; skip apply
        detail["apply_check"] = {"skipped": True, "reason": "tip_drift"}
    else:
        detail["apply_check"] = {"skipped": True, "reason": "tip_unknown_or_disabled"}

    return matches, apply_ok, detail


def _apply_all_check_cached(tip_sha: str) -> tuple[bool | None, dict]:
    """Run apply_all --check on a shallow cached hardening checkout."""
    detail: dict = {"attempted": False, "exit": None, "cache": str(HARDENING_CACHE)}
    if not tip_sha:
        detail["skipped_reason"] = "no_tip_sha"
        return None, detail
    try:
        HARDENING_CACHE.parent.mkdir(parents=True, exist_ok=True)
        if not (HARDENING_CACHE / ".git").is_dir():
            clone = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    HARDENING_REF,
                    f"https://github.com/{MAIN_FULL}.git",
                    str(HARDENING_CACHE),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if clone.returncode != 0:
                detail["skipped_reason"] = "clone_failed"
                detail["stderr_tail"] = (clone.stderr or "")[-500:]
                return None, detail
        else:
            # Refresh tip in cache (best-effort).
            subprocess.run(
                ["git", "-C", str(HARDENING_CACHE), "fetch", "--depth", "1", "origin", HARDENING_REF],
                capture_output=True,
                text=True,
                check=False,
                timeout=90,
            )
            subprocess.run(
                ["git", "-C", str(HARDENING_CACHE), "checkout", "-f", "FETCH_HEAD"],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
        head = subprocess.run(
            ["git", "-C", str(HARDENING_CACHE), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        head_sha = (head.stdout or "").strip().lower()
        detail["cache_head"] = head_sha
        if tip_sha and head_sha and not (
            head_sha == tip_sha.lower() or head_sha.startswith(tip_sha[:7].lower())
        ):
            detail["skipped_reason"] = "cache_tip_mismatch"
            return None, detail

        detail["attempted"] = True
        check = subprocess.run(
            ["bash", str(APPLY_ALL_SH), "--check"],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
            cwd=str(HARDENING_CACHE),
        )
        detail["exit"] = check.returncode
        detail["stdout_tail"] = (check.stdout or "")[-400:]
        detail["stderr_tail"] = (check.stderr or "")[-400:]
        return check.returncode == 0, detail
    except (OSError, subprocess.TimeoutExpired) as exc:
        detail["skipped_reason"] = f"exception:{type(exc).__name__}"
        return None, detail


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


def _annotate_path_c_blocked(
    report: dict,
    *,
    log_path: Path,
    skip_ready_assess: bool,
    extra_log: str,
) -> None:
    """Attach PATH_C_BLOCKED reason codes and log them (Batch 157)."""
    token, _src = resolve_main_push_token()
    has_token = bool(token) or bool(report.get("token_file_present"))
    tip_matches, apply_ok, ready_detail = assess_path_c_readiness(
        skip=skip_ready_assess
    )
    reasons = classify_path_c_blocked(
        has_token=has_token,
        tip_matches=tip_matches,
        apply_ok=apply_ok,
    )
    # Write denied with no other readiness failure still surfaces NO_TOKEN.
    if not reasons and not has_token:
        reasons = [PATH_C_BLOCKED_NO_TOKEN]
    report["path_c_blocked_reasons"] = reasons
    report["path_c_blocked"] = format_path_c_blocked(reasons)
    report["path_c_ready_detail"] = ready_detail
    report["has_token"] = has_token
    blocked_tok = format_path_c_blocked(reasons)
    _log(log_path, f"{blocked_tok} {extra_log}")
    # Batch 180: refresh portable/PATH_C_STATUS.json (no secrets).
    _maybe_write_path_c_status(report)


def _maybe_write_path_c_status(report: dict | None = None) -> None:
    """Best-effort write of portable/PATH_C_STATUS.json via write_path_c_status.py."""
    script = ROOT / "scripts" / "write_path_c_status.py"
    if not script.is_file():
        return
    try:
        subprocess.run(
            [sys.executable, str(script), "--skip-write-probe"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT),
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if report is not None:
        status_path = ROOT / "portable" / "PATH_C_STATUS.json"
        if status_path.is_file():
            report["path_c_status_path"] = "portable/PATH_C_STATUS.json"


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
        "path_c_blocked_reasons": None,
        "path_c_blocked": None,
    }

    # Skip live tip/apply assess under mock-probe (intent tests stay offline/fast).
    skip_ready = mock_probe is not None

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
                _annotate_path_c_blocked(
                    report,
                    log_path=log_path,
                    skip_ready_assess=skip_ready,
                    extra_log=(
                        "action=continue_denied (write DENIED; repository_dispatch "
                        "already fired for this token file)"
                    ),
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
        _annotate_path_c_blocked(
            report,
            log_path=log_path,
            skip_ready_assess=skip_ready,
            extra_log="action=continue_denied (write DENIED)",
        )
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
            _annotate_path_c_blocked(
                report,
                log_path=log_path,
                skip_ready_assess=skip_ready,
                extra_log=(
                    "action=continue_denied_after_install_flip "
                    "(install has main; write still DENIED)"
                ),
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
        # Batch 240: auto Path B restore under MAIN_PUSH_TOKEN (never print value).
        _tok, tok_src = resolve_main_push_token()
        report["action"] = "path_b_restore"
        report["reason"] = (
            "misaligned_writable_after_install_flip" if flipped else "misaligned_writable"
        )
        report["auto_path_b_restore"] = True
        report["token_source"] = tok_src
        cmd = ["bash", str(RESTORE), "--batch", str(batch)]
        if dry_run:
            cmd = ["bash", str(RESTORE), "--dry-run", "--batch", str(batch)]
            land = _run_land(cmd, dry_run=True, label="restore_main_face_path_b")
        else:
            land = _run_land(cmd, dry_run=False, label="restore_main_face_path_b")
        if isinstance(land, dict):
            land["token_source"] = tok_src
            land["auto_path_b_restore"] = True
        report["land"] = land
        _log(
            log_path,
            f"action=path_b_restore attempted={land.get('attempted')} "
            f"exit={land.get('exit')} dry_run={dry_run} "
            f"token_source={tok_src or 'none'} auto_path_b_restore=true",
        )
        return report

    if align_state == "ALIGNED":
        # Batch 231: Path C already on tip (PR #64) — do not re-land; drift watch.
        # Batch 238/239: unless follow-on eng patches (0018+) still pending auto-land.
        landed, land_detail = path_c_already_landed()
        followon_pending, followon_detail = path_c_followon_pending()
        report["path_c_followon_detail"] = followon_detail
        if landed and not followon_pending:
            report["action"] = "idle_path_c_done"
            report["reason"] = "path_c_already_landed"
            report["path_c_landed"] = True
            report["path_c_landed_detail"] = land_detail
            report["path_c_0018_landed"] = True
            report["path_c_followon_pending_ids"] = []
            report["next_focus"] = "tip-sync+drift+no-flip"
            report["preferred_autonomy"] = "aligned_drift_watch"
            _log(
                log_path,
                "action=idle_path_c_done path_c_landed=true "
                "followons_resolved=true "
                "next=tip-sync+drift+no-flip (skip re-land)",
            )
            return report
        if landed and followon_pending:
            report["path_c_landed"] = True
            report["path_c_landed_detail"] = land_detail
            pending_ids = list(followon_detail.get("pending_ids") or [])
            resolved_ids = list(followon_detail.get("resolved_ids") or [])
            report["path_c_followon_pending_ids"] = pending_ids
            report["path_c_0018_landed"] = "0018" in resolved_ids and "0018" not in pending_ids
            report["reason"] = "path_c_followon_pending"
            _log(
                log_path,
                "action=path_c_land reason=path_c_followon_pending "
                f"pending={pending_ids} resolved={resolved_ids} "
                "path_c_landed=true (base) "
                "gate=lemma_closed=false",
            )
        report["action"] = "path_c_land"
        if not (landed and followon_pending):
            report["reason"] = (
                "install_has_main_flipped_true" if flipped else "aligned_writable"
            )
        # Batch 153: prefer owner_open_path_c_pr.sh (bundle → open PR) when present;
        # fall back to owner_land_path_c.sh (apply_all + PR). Both gate lemma_closed=false.
        use_open_pr = OWNER_OPEN_PR.is_file()
        path_c_script = OWNER_OPEN_PR if use_open_pr else OWNER_C
        path_c_label = "owner_open_path_c_pr" if use_open_pr else "owner_land_path_c"
        cmd = ["bash", str(path_c_script)]
        if dry_run:
            land = _run_land(
                ["bash", str(path_c_script), "--dry-run"],
                dry_run=True,
                label=path_c_label,
            )
            land["gate"] = f"lemma_closed=false ({path_c_label} fail-closed)"
            if use_open_pr:
                land["note"] = (
                    "Would run owner_open_path_c_pr.sh (path-c-applied-bundle git am "
                    "→ push cursor/path-c-portable-fixes → open PR into hardening). "
                    "Never promotes research status."
                )
            else:
                land["note"] = (
                    "Would run owner_land_path_c.sh (apply_all on hardening + push). "
                    "Never promotes research status."
                )
        else:
            land = _run_land(
                cmd, dry_run=False, label=path_c_label, timeout=1200
            )
            land["gate"] = f"lemma_closed=false ({path_c_label} fail-closed)"
        land["path_c_script"] = (
            str(path_c_script.relative_to(ROOT))
            if str(path_c_script).startswith(str(ROOT))
            else str(path_c_script)
        )
        if flipped:
            land["triggered_by"] = "install_has_main_flipped_true"
        report["land"] = land
        # Batch 157: if Path C land failed, surface PATH_C_BLOCKED codes.
        land_exit = land.get("exit")
        if land_exit not in (None, 0) and not dry_run:
            stderr = (land.get("stderr_tail") or "") + (land.get("stdout_tail") or "")
            low = stderr.lower()
            tip_fail = "tip-drift" in low or "tip_drift" in low or "tip match" in low
            apply_fail = (
                "apply_all" in low
                or "apply fail" in low
                or "git am" in low
                or "patch failed" in low
            )
            reasons = classify_path_c_blocked(
                has_token=True,
                tip_matches=False if tip_fail else None,
                apply_ok=False if apply_fail else None,
            )
            if not reasons:
                reasons = [PATH_C_BLOCKED_APPLY_FAIL]
            report["path_c_blocked_reasons"] = reasons
            report["path_c_blocked"] = format_path_c_blocked(reasons)
            _log(
                log_path,
                f"{format_path_c_blocked(reasons)} action=path_c_land "
                f"attempted={land.get('attempted')} exit={land_exit} "
                f"dry_run={dry_run} gate=lemma_closed=false script={path_c_label}",
            )
        else:
            _log(
                log_path,
                f"action=path_c_land attempted={land.get('attempted')} "
                f"exit={land.get('exit')} dry_run={dry_run} gate=lemma_closed=false "
                f"script={path_c_label} flipped_install={flipped}",
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
