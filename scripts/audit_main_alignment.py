#!/usr/bin/env python3
"""Audit whether d6g8k5htny-coder/main default tip matches q0 intent.

Read-only. Uses the public GitHub API. Exit codes:
  0 — default tip already looks like the q0 program (or notice is in place)
  1 — misalignment detected (abandoned complexity-physics face, or missing notice)
  2 — transport / API failure

No claim status is read or written.

Batch 256: brief retries on 429 / secondary rate-limit 403.
Batch 340: exponential backoff + x-ratelimit-reset (peer land 066994c).
Batch 340b: after API rate-limit exhaustion, fall back to git ls-remote +
raw.githubusercontent.com (retries alone still exit 2 when reset window is long);
CI soft-continues residual transport exit 2.
Batch 343: Intent suite calls this with timeout=60s. Honoring x-ratelimit-reset
up to SLEEP_CAP=60 burns the whole budget before raw fallback (CI runs
36176016910 / 36176143525 TimeoutExpired). AUDIT_TRANSPORT_EARLY_FALLBACK=1
escalates to RateLimitExhausted immediately so raw/ls-remote runs inside budget.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
API = f"https://api.github.com/repos/{REPO}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}"
COMPLEXITY_MARKERS = (
    "Multiscale Retrodiction Complexity",
    "complexity-physics-framework",
    "δC = 0",
)
Q0_MARKERS = (
    "q0 Research Program",
    "SIDE24",
    "chatgpt/drive-github-hardening-20260919",
    "PR #2",
)

# Batch 256: brief retries on 429 / secondary rate-limit 403 (Intent + drift watch).
# Batch 340: CI align-watch (run 36172207352) still exited 2 after ~6s — default
# 3×2s exhausted under installation primary rate-limit 403. Raise attempts,
# exponential backoff, honor x-ratelimit-reset. Misalignment exit 1 unchanged.
_TRANSPORT_RETRIES = int(os.environ.get("AUDIT_TRANSPORT_RETRIES", "6"))
_TRANSPORT_SLEEP_S = float(os.environ.get("AUDIT_TRANSPORT_SLEEP_S", "3"))
_TRANSPORT_SLEEP_CAP_S = float(os.environ.get("AUDIT_TRANSPORT_SLEEP_CAP_S", "60"))
# Batch 343: Intent timeout class — skip long reset sleeps; raw fallback instead.
_TRANSPORT_EARLY_FALLBACK = os.environ.get(
    "AUDIT_TRANSPORT_EARLY_FALLBACK", "0"
).strip().lower() in ("1", "true", "yes", "on")


class RateLimitExhausted(urllib.error.URLError):
    """API rate-limit retries exhausted — callers may try raw/ls-remote fallback."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _token() -> str | None:
    """Prefer GH_TOKEN / GITHUB_TOKEN so CI avoids unauthenticated rate limits."""
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def _is_rate_limited(exc: BaseException) -> bool:
    """True for HTTP 429 or GitHub primary/secondary rate-limit 403 bodies."""
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code == 429:
            return True
        body = ""
        try:
            raw = exc.read()
            if raw:
                body = raw.decode("utf-8", errors="replace")
                # Allow later str(exc) / diagnostics; HTTPError.read is one-shot.
                exc.msg = (exc.msg or "") + f" body={body[:200]}"
        except Exception:  # noqa: BLE001 — best-effort body sniff
            body = ""
        blob = f"{exc.code} {exc.reason} {body}".lower()
        # Primary: "API rate limit exceeded for installation"
        # Secondary: "You have exceeded a secondary rate limit"
        return (
            "rate limit" in blob
            or "secondary rate" in blob
            or "rate_limit" in blob
        )
    return "rate limit" in str(exc).lower() or "rate_limit" in str(exc).lower()


def _retry_after_seconds(exc: BaseException, attempt: int) -> float:
    """Exponential backoff; honor Retry-After and x-ratelimit-reset when present."""
    delay = _TRANSPORT_SLEEP_S * (2 ** (attempt - 1))
    if isinstance(exc, urllib.error.HTTPError) and exc.headers:
        ra = exc.headers.get("Retry-After")
        if ra is not None:
            try:
                delay = max(delay, float(ra))
            except ValueError:
                pass
        # Primary rate-limit reset is a unix epoch second.
        reset = exc.headers.get("X-RateLimit-Reset") or exc.headers.get(
            "x-ratelimit-reset"
        )
        if reset is not None:
            try:
                wait = float(reset) - time.time()
                if wait > 0:
                    delay = max(delay, wait)
            except ValueError:
                pass
    return min(delay, _TRANSPORT_SLEEP_CAP_S)


def get_json(url: str) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-alignment-audit",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    last_exc: BaseException | None = None
    attempts = max(1, _TRANSPORT_RETRIES)
    rate_limited_any = False
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if _is_rate_limited(exc):
                rate_limited_any = True
                # Batch 343: escalate immediately under EARLY_FALLBACK so Intent
                # timeout=60 is not consumed by x-ratelimit-reset sleeps.
                if _TRANSPORT_EARLY_FALLBACK:
                    print(
                        f"audit: rate-limit early-fallback "
                        f"code={getattr(exc, 'code', '?')} "
                        f"(skip reset sleep → raw)",
                        file=sys.stderr,
                    )
                    raise RateLimitExhausted(str(exc)) from exc
                if attempt < attempts:
                    delay = _retry_after_seconds(exc, attempt)
                    print(
                        f"audit: rate-limit retry {attempt}/{attempts} "
                        f"sleep={delay:.1f}s code={getattr(exc, 'code', '?')}",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    # Rebuild request — prior HTTPError may have consumed the body.
                    req = urllib.request.Request(url, headers=headers)
                    continue
                raise RateLimitExhausted(str(exc)) from exc
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            if _is_rate_limited(exc):
                rate_limited_any = True
                if _TRANSPORT_EARLY_FALLBACK:
                    print(
                        f"audit: rate-limit early-fallback "
                        f"transport={type(exc).__name__} "
                        f"(skip reset sleep → raw)",
                        file=sys.stderr,
                    )
                    raise RateLimitExhausted(str(exc)) from exc
                if attempt < attempts:
                    delay = _retry_after_seconds(exc, attempt)
                    print(
                        f"audit: rate-limit retry {attempt}/{attempts} "
                        f"sleep={delay:.1f}s transport={type(exc).__name__}",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
            raise
    assert last_exc is not None
    if rate_limited_any:
        raise RateLimitExhausted(str(last_exc)) from last_exc
    raise last_exc


def get_readme_text() -> tuple[str, str]:
    meta = get_json(f"{API}/readme")
    import base64

    text = base64.b64decode(meta["content"]).decode("utf-8")
    return text, meta.get("sha", "")


def _raw_get_text(url: str) -> str:
    headers = {"User-Agent": "trial-alignment-audit-raw"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _raw_exists(url: str) -> bool:
    headers = {"User-Agent": "trial-alignment-audit-raw"}
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return 200 <= getattr(resp, "status", 200) < 300
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 404, 405):
            try:
                _raw_get_text(url)
                return True
            except Exception:  # noqa: BLE001
                return False
        return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _ls_remote_sha(branch: str = "main") -> str:
    """Tip SHA without REST — avoids installation rate-limit ceilings."""
    url = f"https://github.com/{REPO}.git"
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", url, f"refs/heads/{branch}"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) >= 40:
            return parts[0].strip().lower()
    return ""


def _audit_via_raw_fallback() -> dict:
    """Read-only audit without api.github.com (Batch 340b rate-limit escape)."""
    default = "main"
    sha = _ls_remote_sha(default)
    if not sha:
        raise RuntimeError("ls-remote returned no SHA for default branch")
    readme = _raw_get_text(f"{RAW_BASE}/{default}/README.md")
    root_names: set[str] = set()
    if _raw_exists(f"{RAW_BASE}/{default}/AGENTS.md"):
        root_names.add("AGENTS.md")
    if _raw_exists(f"{RAW_BASE}/{default}/body"):
        root_names.add("body")
    if _raw_exists(f"{RAW_BASE}/{default}/.github/workflows/ci.yml") or _raw_exists(
        f"{RAW_BASE}/{default}/.github/CODEOWNERS"
    ):
        root_names.add(".github")
    print(
        f"audit: raw/ls-remote fallback OK tip={sha[:7]} branch={default}",
        file=sys.stderr,
    )
    return {
        "default_branch": default,
        "default_tip_sha": sha,
        "readme": readme,
        "root_names": root_names,
        "via": "raw_ls_remote",
    }


def _audit_via_api() -> dict:
    repo = get_json(API)
    default = repo["default_branch"]
    commit = get_json(f"{API}/commits/{default}")
    sha = commit["sha"]
    readme, _ = get_readme_text()
    tree = get_json(f"{API}/git/trees/{default}")
    root_names = {item["path"] for item in tree.get("tree", [])}
    return {
        "default_branch": default,
        "default_tip_sha": sha,
        "readme": readme,
        "root_names": root_names,
        "via": "api",
    }


def main() -> int:
    via = "api"
    try:
        try:
            payload = _audit_via_api()
        except RateLimitExhausted as exc:
            print(
                f"audit: API rate-limit exhausted ({exc.reason}); "
                "trying raw/ls-remote fallback",
                file=sys.stderr,
            )
            payload = _audit_via_raw_fallback()
        except urllib.error.HTTPError as exc:
            if _is_rate_limited(exc):
                print(
                    f"audit: API rate-limit ({exc}); trying raw/ls-remote fallback",
                    file=sys.stderr,
                )
                payload = _audit_via_raw_fallback()
            else:
                raise
        via = str(payload.get("via") or "api")
        default = payload["default_branch"]
        sha = payload["default_tip_sha"]
        readme = payload["readme"]
        root_names = payload["root_names"]
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        # Batch 155: also catch http.client.RemoteDisconnected (OSError) and
        # mid-request connection drops so CI Intent suite gets exit 2, not crash.
        # Batch 256/340: rate-limit retries inside get_json; Batch 340b raw
        # fallback may still leave residual transport → exit 2.
        print(f"audit: transport failure: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — audit must never crash Intent suite
        print(f"audit: transport failure: {exc}", file=sys.stderr)
        return 2

    complexity_hits = [m for m in COMPLEXITY_MARKERS if m in readme]
    q0_hits = [m for m in Q0_MARKERS if m in readme]
    has_body = "body" in root_names
    has_agents = "AGENTS.md" in root_names
    has_workflows = ".github" in root_names

    report = {
        "repo": REPO,
        "default_branch": default,
        "default_tip_sha": sha,
        "root_has_body": has_body,
        "root_has_AGENTS_md": has_agents,
        "root_has_dot_github": has_workflows,
        "complexity_markers_present": complexity_hits,
        "q0_or_notice_markers_present": q0_hits,
        "scientific_effect": "NONE",
        "audit_via": via,
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    # Misalignment predicate unchanged (Batch 340 does not weaken detection).
    misaligned = bool(complexity_hits) or (not q0_hits and not has_agents)
    if misaligned:
        print(
            "audit: MISALIGNED — default tip still presents pre-q0 face "
            "or lacks q0/notice markers.",
            file=sys.stderr,
        )
        return 1
    print("audit: OK — default tip carries q0 program or redirect notice.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
