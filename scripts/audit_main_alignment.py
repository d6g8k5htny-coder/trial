#!/usr/bin/env python3
"""Audit whether d6g8k5htny-coder/main default tip matches q0 intent.

Read-only. Uses the public GitHub API. Exit codes:
  0 — default tip already looks like the q0 program (or notice is in place)
  1 — misalignment detected (abandoned complexity-physics face, or missing notice)
  2 — transport / API failure

No claim status is read or written.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
API = f"https://api.github.com/repos/{REPO}"
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
_TRANSPORT_RETRIES = int(os.environ.get("AUDIT_TRANSPORT_RETRIES", "3"))
_TRANSPORT_SLEEP_S = float(os.environ.get("AUDIT_TRANSPORT_SLEEP_S", "2"))


def _token() -> str | None:
    """Prefer GH_TOKEN / GITHUB_TOKEN so CI avoids unauthenticated rate limits."""
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def _is_rate_limited(exc: BaseException) -> bool:
    """True for HTTP 429 or GitHub secondary rate-limit 403 bodies."""
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
        return "rate limit" in blob or "secondary rate" in blob
    return "rate limit" in str(exc).lower()


def _retry_after_seconds(exc: BaseException, attempt: int) -> float:
    delay = _TRANSPORT_SLEEP_S * attempt
    if isinstance(exc, urllib.error.HTTPError) and exc.headers:
        ra = exc.headers.get("Retry-After")
        if ra is not None:
            try:
                delay = max(delay, float(ra))
            except ValueError:
                pass
    return min(delay, 30.0)


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
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if _is_rate_limited(exc) and attempt < attempts:
                time.sleep(_retry_after_seconds(exc, attempt))
                # Rebuild request — prior HTTPError may have consumed the body.
                req = urllib.request.Request(url, headers=headers)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            if _is_rate_limited(exc) and attempt < attempts:
                time.sleep(_retry_after_seconds(exc, attempt))
                continue
            raise
    assert last_exc is not None
    raise last_exc


def get_readme_text() -> tuple[str, str]:
    meta = get_json(f"{API}/readme")
    import base64

    text = base64.b64decode(meta["content"]).decode("utf-8")
    return text, meta.get("sha", "")


def main() -> int:
    try:
        repo = get_json(API)
        default = repo["default_branch"]
        commit = get_json(f"{API}/commits/{default}")
        sha = commit["sha"]
        readme, _ = get_readme_text()
        tree = get_json(f"{API}/git/trees/{default}")
        root_names = {item["path"] for item in tree.get("tree", [])}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        # Batch 155: also catch http.client.RemoteDisconnected (OSError) and
        # mid-request connection drops so CI Intent suite gets exit 2, not crash.
        # Batch 256: rate-limit retries happen inside get_json; exhausted → exit 2.
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
    }
    print(json.dumps(report, indent=2, sort_keys=True))

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
