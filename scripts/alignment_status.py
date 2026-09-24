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


def autonomous_window() -> dict:
    """Embed permanent/finite window status (Batch 62+ dashboard)."""
    import os
    from pathlib import Path

    script = Path(__file__).resolve().parent / "check_autonomous_window.py"
    if not script.is_file():
        return {"state": "SCRIPT_MISSING", "scientific_effect": "NONE"}
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )
    text = (proc.stdout or "").strip()
    if not text:
        return {
            "state": "EMPTY",
            "window_exit": proc.returncode,
            "scientific_effect": "NONE",
        }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            payload = json.loads(text[text.index("{") :])
        except (ValueError, json.JSONDecodeError):
            return {
                "state": "PARSE_ERROR",
                "window_exit": proc.returncode,
                "scientific_effect": "NONE",
            }
    payload["window_exit"] = proc.returncode
    return payload


def base_tip_vs_live(hardening_sha: str) -> dict:
    """Compare portable BASE_TIP.txt to live hardening tip (Path C currency)."""
    from pathlib import Path

    tip_file = Path(__file__).resolve().parents[1] / "portable" / "patches" / "BASE_TIP.txt"
    line = tip_file.read_text(encoding="utf-8").strip() if tip_file.is_file() else ""
    parts = line.split()
    base_sha = parts[-1] if parts else None
    matches = bool(base_sha and hardening_sha and hardening_sha.startswith(base_sha[:7]))
    return {
        "base_tip_file": line or None,
        "base_tip_sha": base_sha,
        "live_hardening_sha": hardening_sha,
        "tip_matches_base": matches,
        "apply_stack": "0001-0004 + 0008-0019",
        "path_c_note": (
            "Keep Path C on hardening when default tip lacks PACKET.json "
            "(post-#41 ALIGNED but not Path-C shaped)."
        ),
    }


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
        window = autonomous_window()
        tip_currency = base_tip_vs_live(hardening["sha"])
    except (urllib.error.URLError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "scientific_effect": "NONE"}, indent=2))
        return 2

    aligned = alignment.get("audit_exit") == 0
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "autonomous_window": window,
        "path_c_tip": tip_currency,
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
                "aligned": aligned,
                "default_tip_note": (
                    "Default tip ALIGNED via owner PR #41 @ 1c6e74b (renew after #32). "
                    "Path B land not needed while ALIGNED. Path C stays on hardening "
                    "(PACKET.json / carriers_verify absent on default tip)."
                ),
                "pr41_url": "https://github.com/d6g8k5htny-coder/main/pull/41",
                "pr2_url": "https://github.com/d6g8k5htny-coder/main/pull/2",
                "pr2_note": "PR #2 was MERGED then reverted by #32; do not ready/merge 2.",
                "prefer_when_misaligned": "Path_B",
                "prefer_when_aligned_writable": "Path_C_on_hardening",
            },
        },
        "portable_in_trial": [
            "portable/main-default-branch/",
            "portable/pr2-landing/",
            "portable/patches/",
            "scripts/check_autonomous_window.py",
            "scripts/path_c_dry_run.py",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
