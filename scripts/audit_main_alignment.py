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


def _token() -> str | None:
    """Prefer GH_TOKEN / GITHUB_TOKEN so CI avoids unauthenticated rate limits."""
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def get_json(url: str) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-alignment-audit",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


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
    except urllib.error.URLError as exc:
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
