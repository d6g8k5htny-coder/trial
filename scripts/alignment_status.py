#!/usr/bin/env python3
"""Emit a single JSON alignment status for Dylan's two public repos.

Read-only. Scientific effect: NONE. Exit 0 always unless transport fails (2).
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


def _token() -> str | None:
    """Prefer GH_TOKEN / GITHUB_TOKEN so CI avoids unauthenticated rate limits."""
    import os

    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def gh_json(url: str) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-alignment-status",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def main_alignment() -> dict:
    proc = subprocess.run(
        [sys.executable, str(__file__).replace("alignment_status.py", "audit_main_alignment.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    report = {}
    if proc.stdout.strip():
        report = json.loads(proc.stdout)
    report["audit_exit"] = proc.returncode
    report["audit_stderr"] = proc.stderr.strip()
    return report


def open_prs(repo: str) -> list[dict]:
    data = gh_json(f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=30")
    out = []
    for pr in data:
        out.append(
            {
                "number": pr["number"],
                "title": pr["title"],
                "draft": pr.get("draft"),
                "base": pr["base"]["ref"],
                "head": pr["head"]["ref"],
                "html_url": pr["html_url"],
            }
        )
    return out


def main() -> int:
    try:
        main_repo = gh_json("https://api.github.com/repos/d6g8k5htny-coder/main")
        trial_repo = gh_json("https://api.github.com/repos/d6g8k5htny-coder/trial")
        hardening = gh_json(
            "https://api.github.com/repos/d6g8k5htny-coder/main/commits/"
            "chatgpt/drive-github-hardening-20260919"
        )
        alignment = main_alignment()
        prs = open_prs("d6g8k5htny-coder/main")
    except (urllib.error.URLError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "scientific_effect": "NONE"}, indent=2))
        return 2

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "trial": {
            "default_branch": trial_repo["default_branch"],
            "description": trial_repo.get("description"),
            "html_url": trial_repo["html_url"],
        },
        "main": {
            "default_branch": main_repo["default_branch"],
            "default_tip_sha": alignment.get("default_tip_sha"),
            "description": main_repo.get("description"),
            "alignment": alignment,
            "working_branch": "chatgpt/drive-github-hardening-20260919",
            "working_tip_sha": hardening["sha"],
            "working_tip_message": hardening["commit"]["message"].split("\n", 1)[0],
            "open_prs": prs,
            "critical_path": {
                "pr2_url": "https://github.com/d6g8k5htny-coder/main/pull/2",
                "note": "PR #2 MERGEABLE/CLEAN lands q0 tree on default main",
            },
        },
        "portable_in_trial": [
            "portable/main-default-branch/",
            "portable/pr2-landing/",
            "portable/patches/",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
