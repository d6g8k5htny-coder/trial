#!/usr/bin/env python3
"""Write portable/PATH_C_STATUS.json — portable Path C readiness snapshot.

Emits tip / base_tip / tip_match / write_state / lemma_closed / path_c_blocked
reason / device_code (user code only; never secrets) / release_tag / generated_at.

Scientific effect: NONE. Never flips lemma_closed / prizes / premises / research.
Does not push. Safe for CI, assert_path_c_ready, and watch scripts.

Usage:
  python3 scripts/write_path_c_status.py
  python3 scripts/write_path_c_status.py --dry-run
  python3 scripts/write_path_c_status.py --out portable/PATH_C_STATUS.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "portable" / "PATH_C_STATUS.json"
BASE_TIP_FILE = ROOT / "portable" / "patches" / "BASE_TIP.txt"
VERIFY_FILE = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"
HARDENING_REF = os.environ.get(
    "HARDENING_REF", "chatgpt/drive-github-hardening-20260919"
)
MAIN_REPO = os.environ.get("MAIN_REPO", "d6g8k5htny-coder/main")
DEVICE_STATE = Path("/tmp/gh-dylan-auth/device_poll_state.json")
NEW_CODE_PUBLIC = Path("/tmp/gh-dylan-auth/new_code_public.json")
ACCESS_TOKEN = Path("/tmp/gh-dylan-auth/access_token")
GH_DEVICE_LOGIN_MD = ROOT / "portable" / "GH_DEVICE_LOGIN.md"

# Schema keys required by Batch 180 intent tests (stable contract).
SCHEMA_KEYS = (
    "tip",
    "base_tip",
    "tip_match",
    "write_state",
    "lemma_closed",
    "path_c_blocked",
    "device_code",
    "release_tag",
    "generated_at",
)

PATH_C_BLOCKED_NO_TOKEN = "NO_TOKEN"
PATH_C_BLOCKED_TIP_DRIFT = "TIP_DRIFT"
PATH_C_BLOCKED_APPLY_FAIL = "APPLY_FAIL"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _token() -> str | None:
    for key in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    if ACCESS_TOKEN.is_file():
        try:
            val = ACCESS_TOKEN.read_text(encoding="utf-8").strip()
            if val:
                return val
        except OSError:
            pass
    return None


def _parse_base_tip_sha(text: str) -> str | None:
    m = re.search(r"(?i)\b([0-9a-f]{40})\b", text)
    if m:
        return m.group(1).lower()
    m = re.search(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)", text)
    if m:
        return m.group(1).lower()
    return None


def _read_base_tip() -> tuple[str | None, str]:
    if not BASE_TIP_FILE.is_file():
        return None, ""
    line = BASE_TIP_FILE.read_text(encoding="utf-8").splitlines()[0].strip()
    return _parse_base_tip_sha(line), line


def _fetch_live_tip() -> str | None:
    url = f"https://api.github.com/repos/{MAIN_REPO}/commits/{HARDENING_REF}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-write-path-c-status",
    }
    tok = _token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None
    sha = (data.get("sha") or "").strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", sha):
        return sha
    return None


def _tip_matches(base: str | None, live: str | None) -> bool | None:
    if not base or not live:
        return None
    b = base.lower()
    live_l = live.lower()
    if len(b) == 40:
        return live_l == b
    if 7 <= len(b) < 40:
        return live_l.startswith(b)
    return None


def _probe_write_state() -> str:
    """Lightweight write probe; never prints token material."""
    # Prefer existing probe script if available (captures DENIED/WRITABLE).
    probe = ROOT / "scripts" / "probe_main_write.py"
    if probe.is_file():
        import subprocess

        env = {k: v for k, v in os.environ.items()}
        # Keep host tokens for accurate probe; do not echo them.
        try:
            proc = subprocess.run(
                [sys.executable, str(probe)],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=str(ROOT),
                env=env,
                check=False,
            )
            if proc.stdout.strip():
                payload = json.loads(proc.stdout)
                state = payload.get("state")
                if isinstance(state, str) and state:
                    return state
            if proc.returncode == 0:
                return "WRITABLE"
            if proc.returncode == 1:
                return "DENIED"
        except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
            pass
    return "UNKNOWN"


def _has_main_push_token() -> bool:
    if os.environ.get("MAIN_PUSH_TOKEN"):
        return True
    for path in (
        Path("/cursor/stores/self/MAIN_PUSH_TOKEN"),
        ROOT / ".secrets" / "MAIN_PUSH_TOKEN",
        ACCESS_TOKEN,
    ):
        if path.is_file():
            try:
                if path.read_text(encoding="utf-8").strip():
                    return True
            except OSError:
                continue
    return False


def _device_code_public() -> tuple[str | None, float | None, str | None]:
    """Return (user_code, seconds_left, auth_status). Never returns device_code secret."""
    user_code: str | None = None
    seconds_left: float | None = None
    auth_status: str | None = None

    if ACCESS_TOKEN.is_file():
        try:
            if ACCESS_TOKEN.read_text(encoding="utf-8").strip():
                auth_status = "SUCCESS"
        except OSError:
            pass

    if DEVICE_STATE.is_file():
        try:
            state = json.loads(DEVICE_STATE.read_text(encoding="utf-8"))
            user_code = state.get("user_code") or user_code
            started = float(state.get("started_at") or 0)
            expires_in = float(state.get("expires_in") or 0)
            if started and expires_in:
                seconds_left = max(0.0, expires_in - (time.time() - started))
            if auth_status != "SUCCESS":
                if seconds_left is not None and seconds_left <= 0:
                    auth_status = "EXPIRED"
                else:
                    auth_status = "pending"
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    if user_code is None and NEW_CODE_PUBLIC.is_file():
        try:
            pub = json.loads(NEW_CODE_PUBLIC.read_text(encoding="utf-8"))
            user_code = pub.get("user_code") or user_code
            if seconds_left is None and pub.get("seconds_left") is not None:
                seconds_left = float(pub["seconds_left"])
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    if user_code is None and GH_DEVICE_LOGIN_MD.is_file():
        try:
            text = GH_DEVICE_LOGIN_MD.read_text(encoding="utf-8")
            m = re.search(r"User code\s*\|\s*`([A-Z0-9]{4,}-[A-Z0-9]{4,})`", text)
            if m:
                user_code = m.group(1)
        except OSError:
            pass

    return user_code, seconds_left, auth_status


def _release_tag() -> str | None:
    if VERIFY_FILE.is_file():
        try:
            verify = json.loads(VERIFY_FILE.read_text(encoding="utf-8"))
            rel = verify.get("release")
            if isinstance(rel, str) and rel:
                return rel
            batch = verify.get("batch")
            if batch is not None:
                return f"batch{batch}-path-c-bundle"
        except (OSError, json.JSONDecodeError):
            pass
    # Fall back to oneshot default if present.
    oneshot = ROOT / "scripts" / "owner_path_c_oneshot.sh"
    if oneshot.is_file():
        try:
            text = oneshot.read_text(encoding="utf-8")
            m = re.search(
                r'PATH_C_RELEASE_TAG=\$\{\w+:-([a-z0-9-]+-path-c-bundle)\}',
                text,
            )
            if m:
                return m.group(1)
        except OSError:
            pass
    return None


def _lemma_closed_from_verify() -> bool:
    """Always prefer false; never promote. Read VERIFY/math note only."""
    if VERIFY_FILE.is_file():
        try:
            verify = json.loads(VERIFY_FILE.read_text(encoding="utf-8"))
            if "lemma_closed" in verify:
                return bool(verify["lemma_closed"])
        except (OSError, json.JSONDecodeError):
            pass
    return False


def _read_verify() -> dict:
    if not VERIFY_FILE.is_file():
        return {}
    try:
        data = json.loads(VERIFY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _prior_status(out: Path | None = None) -> dict:
    """Read existing PATH_C_STATUS so assert refresh does not wipe land fields."""
    path = out or DEFAULT_OUT
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _land_fields_from_verify(verify: dict) -> dict:
    """Carry Path C land evidence from VERIFY into PATH_C_STATUS (no research flip)."""
    if verify.get("path_c_landed") is not True:
        return {}
    out: dict = {"path_c_landed": True}
    pr = verify.get("path_c_pr_url")
    if isinstance(pr, str) and pr:
        out["path_c_pr_url"] = pr
    merge_sha = verify.get("merge_commit_sha") or verify.get("base_tip_sha")
    if isinstance(merge_sha, str) and merge_sha:
        out["path_c_sha"] = merge_sha
    applied = verify.get("applied_commit_sha")
    if isinstance(applied, str) and applied:
        out["path_c_applied_sha"] = applied
    vector = verify.get("write_vector")
    if isinstance(vector, str) and vector:
        out["write_vector"] = vector
    # Batch 238/239: preserve follow-on 00NN (≥0018) land markers across refreshes.
    # Explicit keys include path_c_0018_landed (PR #70) and later path_c_0019_landed+.
    for key, val in verify.items():
        if (
            isinstance(key, str)
            and key.startswith("path_c_")
            and key.endswith("_landed")
            and key != "path_c_landed"
            and val is True
        ):
            out[key] = True
            via_key = key[: -len("_landed")] + "_via"
            via = verify.get(via_key)
            if isinstance(via, str) and via:
                out[via_key] = via
    return out


def _classify_blocked(
    *,
    has_token: bool,
    tip_match: bool | None,
    write_state: str,
) -> str:
    reasons: list[str] = []
    if not has_token and write_state != "WRITABLE":
        reasons.append(PATH_C_BLOCKED_NO_TOKEN)
    if tip_match is False:
        reasons.append(PATH_C_BLOCKED_TIP_DRIFT)
    if not reasons:
        if write_state == "WRITABLE" and tip_match is True:
            return "NONE"
        if not has_token:
            return PATH_C_BLOCKED_NO_TOKEN
        return "NONE"
    return ",".join(reasons)


def build_status(*, skip_write_probe: bool = False, out: Path | None = None) -> dict:
    base_sha, _base_line = _read_base_tip()
    live_sha = _fetch_live_tip()
    tip_match = _tip_matches(base_sha, live_sha)
    verify = _read_verify()
    land = _land_fields_from_verify(verify)
    prior = _prior_status(out)
    prior_ws = prior.get("write_state")
    if skip_write_probe:
        # Batch 232: after Path C landed on matching tip, land-time write was
        # WRITABLE. Do not sticky-preserve a later probe-clobber DENIED (hourly
        # watch uses --skip-write-probe and used to lock DENIED forever).
        # Also do not clobber a recorded land snapshot with SKIPPED.
        if land.get("path_c_landed") and tip_match is True:
            write_state = "WRITABLE"
        elif land.get("path_c_landed") and prior_ws in ("WRITABLE", "DENIED"):
            write_state = prior_ws
        else:
            write_state = "SKIPPED"
    else:
        write_state = _probe_write_state()
        # After Path C land on matching tip, do not clobber land-time WRITABLE
        # with a transient DENIED probe (ghs/cursor[bot] 403 while Dylan land stands).
        if (
            land.get("path_c_landed")
            and tip_match is True
            and prior_ws == "WRITABLE"
            and write_state == "DENIED"
        ):
            write_state = "WRITABLE"
    has_token = _has_main_push_token()
    device_code, seconds_left, auth_status = _device_code_public()
    release_tag = _release_tag()
    lemma_closed = _lemma_closed_from_verify()
    # Hard rule: never flip research — force false in status contract.
    lemma_closed = False if lemma_closed is not True else False
    blocked = _classify_blocked(
        has_token=has_token, tip_match=tip_match, write_state=write_state
    )

    tip_short = (live_sha or "")[:7] or None
    base_short = (base_sha or "")[:7] or None

    # Operational Path C land goal (not research). VERIFY.goal_complete stays false.
    goal_complete = bool(land.get("path_c_landed") is True and tip_match is True)

    status = {
        "tip": tip_short,
        "tip_full": live_sha,
        "base_tip": base_short,
        "base_tip_full": base_sha,
        "tip_match": tip_match,
        "write_state": write_state,
        "lemma_closed": lemma_closed,
        "path_c_blocked": blocked,
        "path_c_blocked_reason": blocked,
        "device_code": device_code,
        "device_auth": auth_status,
        "seconds_left": round(seconds_left, 1) if seconds_left is not None else None,
        "release_tag": release_tag,
        "generated_at": _utc_now(),
        "scientific_effect": "NONE",
        "goal_complete": goal_complete,
        "hardening_ref": HARDENING_REF,
        "has_token": has_token,
    }
    if land:
        status.update(land)
        # Preserve prior write_vector when VERIFY omitted it.
        if "write_vector" not in status:
            prior_vec = prior.get("write_vector")
            if isinstance(prior_vec, str) and prior_vec:
                status["write_vector"] = prior_vec
            elif write_state == "WRITABLE":
                status["write_vector"] = prior.get("write_vector") or "device_auth_create_ref+git_push_dylan_token"
    # Batch 236: preserve write durability markers (Batch 235+) across status
    # refreshes — do not clobber write_durable / main_push_token_set when a
    # watch/assert rewrites PATH_C_STATUS.json.
    for durable_key in (
        "write_durable",
        "write_durable_via",
        "main_push_token_set",
        "main_push_token_set_repos",
        "write_vector",
    ):
        if durable_key not in status or status.get(durable_key) in (None, ""):
            prior_val = prior.get(durable_key)
            if prior_val not in (None, "", False) or (
                durable_key == "write_durable" and prior_val is True
            ):
                if prior_val is not None:
                    status[durable_key] = prior_val
    if write_state == "WRITABLE" and prior.get("write_durable") is True:
        status["write_durable"] = True
        if prior.get("write_durable_via"):
            status["write_durable_via"] = prior["write_durable_via"]
        if prior.get("main_push_token_set") is True:
            status["main_push_token_set"] = True
            if prior.get("main_push_token_set_repos"):
                status["main_push_token_set_repos"] = prior["main_push_token_set_repos"]
    # Batch 238/239: preserve path_c_00NN_landed (≥0018) from VERIFY or prior.
    # Covers path_c_0018_landed and any later path_c_0019_landed+ follow-ons.
    for src in (prior, verify):
        for key, val in src.items():
            if (
                isinstance(key, str)
                and key.startswith("path_c_")
                and key.endswith("_landed")
                and key != "path_c_landed"
                and val is True
                and status.get(key) is not True
            ):
                status[key] = True
                via_key = key[: -len("_landed")] + "_via"
                via = src.get(via_key)
                if isinstance(via, str) and via and not status.get(via_key):
                    status[via_key] = via
    # Ensure schema keys exist even if None.
    for key in SCHEMA_KEYS:
        status.setdefault(key, None)
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write portable/PATH_C_STATUS.json (no secrets; lemma_closed=false)."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output path (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON to stdout; do not write file",
    )
    parser.add_argument(
        "--skip-write-probe",
        action="store_true",
        help="Skip probe_main_write (faster; write_state=SKIPPED)",
    )
    parser.add_argument(
        "--schema-keys",
        action="store_true",
        help="Print required schema keys as JSON array and exit",
    )
    args = parser.parse_args(argv)

    if args.schema_keys:
        print(json.dumps(list(SCHEMA_KEYS)))
        return 0

    out: Path = args.out
    if not out.is_absolute():
        out = ROOT / out

    status = build_status(skip_write_probe=args.skip_write_probe, out=out)
    text = json.dumps(status, indent=2, sort_keys=True) + "\n"

    if args.dry_run:
        # Never print secrets — status contract excludes tokens by design.
        sys.stdout.write(text)
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"write_path_c_status: wrote {out}")
    print(
        f"write_path_c_status: tip={status.get('tip')} base_tip={status.get('base_tip')} "
        f"tip_match={status.get('tip_match')} write_state={status.get('write_state')} "
        f"lemma_closed={status.get('lemma_closed')} path_c_blocked={status.get('path_c_blocked')} "
        f"device_code={status.get('device_code')} release_tag={status.get('release_tag')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
