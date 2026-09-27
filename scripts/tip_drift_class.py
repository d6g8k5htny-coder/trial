#!/usr/bin/env python3
"""Classify live hardening tip vs portable BASE_TIP (Path C drift class).

Sidecar b3c6 (2026-09-27): hardening merges land several times per hour, so a
strict ``live == BASE_TIP`` gate reds every trial-ci run between an upstream
merge and the next tip-sync pulse (651 consecutive red runs, 2026-09-26 13:00Z →
2026-09-27). Path C is landed (patches already on tip), so a live tip that
*descends* from BASE_TIP still carries the engineering stack; only a tip that
is behind / diverged (force-push, branch reset) is a landing hazard.

Classes (stdout, one word):

    MATCH        live == BASE_TIP (prefix-tolerant)
    DESCENDANT   live is ahead of BASE_TIP (BASE_TIP is an ancestor)
    BEHIND       live is an ancestor of BASE_TIP (tip reset)
    DIVERGED     neither is an ancestor of the other
    UNKNOWN      compare unavailable (network / auth / bad input)

Exit codes: 0 MATCH, 0 DESCENDANT only when ``--landed`` (or VERIFY.json says
``path_c_landed: true``), 1 otherwise, 2 UNKNOWN.

Scientific effect: NONE. Never flips lemma_closed / prizes / premises / research.
Read-only: one GitHub compare API call (token optional; never printed).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_REPO = os.environ.get("MAIN_REPO", "d6g8k5htny-coder/main")
VERIFY_FILE = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"

_HEX = re.compile(r"(?i)^[0-9a-f]{7,40}$")
_CACHE: dict[str, str] = {}


def _token() -> str:
    return (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("MAIN_PUSH_TOKEN")
        or ""
    )


def _compare_status(base: str, live: str, repo: str = MAIN_REPO, timeout: int = 30) -> str:
    """GitHub compare status: identical | ahead | behind | diverged | '' (unknown)."""
    key = f"{repo}:{base}...{live}"
    if key in _CACHE:
        return _CACHE[key]
    url = f"https://api.github.com/repos/{repo}/compare/{base}...{live}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-tip-drift-class",
    }
    tok = _token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    status = ""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.load(resp)
        status = str(data.get("status") or "")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        status = ""
    if not status:
        try:
            p = subprocess.run(
                ["gh", "api", f"repos/{repo}/compare/{base}...{live}", "--jq", ".status"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if p.returncode == 0:
                status = p.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            status = ""
    _CACHE[key] = status
    return status


def classify(base: str | None, live: str | None, repo: str = MAIN_REPO) -> str:
    """Return MATCH | DESCENDANT | BEHIND | DIVERGED | UNKNOWN."""
    b = str(base or "").strip().lower()
    l = str(live or "").strip().lower()
    if not (_HEX.match(b) and _HEX.match(l)):
        return "UNKNOWN"
    if b == l or b.startswith(l) or l.startswith(b):
        return "MATCH"
    status = _compare_status(b, l, repo)
    return {
        "identical": "MATCH",
        "ahead": "DESCENDANT",
        "behind": "BEHIND",
        "diverged": "DIVERGED",
    }.get(status, "UNKNOWN")


def path_c_landed(verify_file: Path = VERIFY_FILE) -> bool:
    try:
        return json.loads(verify_file.read_text(encoding="utf-8")).get("path_c_landed") is True
    except (OSError, ValueError):
        return False


def acceptable(cls: str, landed: bool) -> bool:
    """MATCH always; DESCENDANT only when Path C is landed on tip."""
    return cls == "MATCH" or (cls == "DESCENDANT" and landed)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", help="BASE_TIP SHA (7-40 hex)")
    ap.add_argument("live", help="live hardening SHA (7-40 hex)")
    ap.add_argument("--repo", default=MAIN_REPO)
    ap.add_argument("--landed", action="store_true", help="treat DESCENDANT as acceptable (else read VERIFY.json)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of the bare class")
    args = ap.parse_args(argv)
    cls = classify(args.base, args.live, args.repo)
    landed = args.landed or path_c_landed()
    ok = acceptable(cls, landed)
    if args.json:
        print(json.dumps({
            "base": args.base, "live": args.live, "class": cls,
            "path_c_landed": landed, "acceptable": ok,
            "scientific_effect": "NONE", "lemma_closed": False,
        }, sort_keys=True))
    else:
        print(cls)
    if cls == "UNKNOWN":
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
