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
Read-only: one GitHub compare API call (token optional; never printed); when
the API is unavailable (rate limit / auth), ancestry is taken from a cached
commits-only git mirror of the hardening branch (``_git_compare_status``).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_REPO = os.environ.get("MAIN_REPO", "d6g8k5htny-coder/main")
VERIFY_FILE = ROOT / "portable" / "path-c-applied-bundle" / "VERIFY.json"

_HEX = re.compile(r"(?i)^[0-9a-f]{7,40}$")
_CACHE: dict[str, str] = {}
HARDENING_BRANCH = os.environ.get("HARDENING_BRANCH", "chatgpt/drive-github-hardening-20260919")


def _token() -> str:
    return (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("MAIN_PUSH_TOKEN")
        or ""
    )


def _git_mirror_dir(repo: str) -> Path:
    root = Path(os.environ.get("TIP_DRIFT_GIT_CACHE") or os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())
    return root / f"trial-tip-drift-{repo.replace('/', '__')}.git"


def _git(args: list[str], cwd: Path | None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False, env=env,
    )


def _git_compare_status(base: str, live: str, repo: str = MAIN_REPO, timeout: int = 120) -> str:
    """Compare status from git ancestry instead of the REST API.

    Cached bare mirror (commits only, ``--filter=tree:0``) of the hardening
    branch of the public research repo; no token, no API rate limit. Returns
    identical | ahead | behind | diverged, or '' when either SHA cannot be
    resolved (unknown stays unknown — never guessed).
    """
    d = _git_mirror_dir(repo)
    url = os.environ.get("TIP_DRIFT_GIT_URL") or f"https://github.com/{repo}.git"
    try:
        if not (d / "HEAD").is_file():
            d.mkdir(parents=True, exist_ok=True)
            if _git(["init", "-q", "--bare", str(d)], cwd=None).returncode != 0:
                return ""
        refspec = f"+refs/heads/{HARDENING_BRANCH}:refs/remotes/hardening/{HARDENING_BRANCH}"
        if _git(["fetch", "-q", "--filter=tree:0", url, refspec], cwd=d, timeout=timeout).returncode != 0:
            return ""

        def resolve(sha: str) -> str:
            r = _git(["rev-parse", "--verify", "-q", f"{sha}^{{commit}}"], cwd=d)
            if r.returncode == 0:
                return r.stdout.strip()
            if len(sha) == 40:  # exact SHAs may be fetched directly when reachable from any ref
                if _git(["fetch", "-q", "--filter=tree:0", url, sha], cwd=d, timeout=timeout).returncode == 0:
                    r = _git(["rev-parse", "--verify", "-q", f"{sha}^{{commit}}"], cwd=d)
                    if r.returncode == 0:
                        return r.stdout.strip()
            return ""

        b, l = resolve(base), resolve(live)
        if not b or not l:
            return ""
        if b == l:
            return "identical"
        if _git(["merge-base", "--is-ancestor", b, l], cwd=d).returncode == 0:
            return "ahead"
        if _git(["merge-base", "--is-ancestor", l, b], cwd=d).returncode == 0:
            return "behind"
        return "diverged"
    except (OSError, subprocess.SubprocessError):
        return ""


def _compare_status(base: str, live: str, repo: str = MAIN_REPO, timeout: int = 30) -> str:
    """GitHub compare status: identical | ahead | behind | diverged | '' (unknown)."""
    key = f"{repo}:{base}...{live}"
    if key in _CACHE:
        return _CACHE[key]
    url = f"https://api.github.com/repos/{repo}/compare/{base}...{live}"
    base_headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-tip-drift-class",
    }

    def _fetch(with_token: bool) -> str:
        headers = dict(base_headers)
        tok = _token() if with_token else ""
        if with_token and not tok:
            return ""
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                return str(json.load(resp).get("status") or "")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
            return ""

    # Token first (higher rate limit); a bad/expired token (401/403) must not
    # poison the answer — the research repo is public, so retry anonymously.
    status = _fetch(with_token=True) or _fetch(with_token=False)
    if not status:
        # NA-0009: on Actions both API paths can be exhausted at once (the
        # installation token's hourly budget is shared by every trial-ci run,
        # anonymous is per-runner-IP). Ancestry needs no API at all.
        status = _git_compare_status(base, live, repo)
    if not status:
        # gh CLI fallback: as-is, then with a possibly-bad env token stripped so
        # gh falls back to its own auth store (or anonymous on public repos).
        for strip_env in (False, True):
            env = dict(os.environ)
            if strip_env:
                for k in ("GITHUB_TOKEN", "GH_TOKEN", "MAIN_PUSH_TOKEN"):
                    env.pop(k, None)
            try:
                p = subprocess.run(
                    ["gh", "api", f"repos/{repo}/compare/{base}...{live}", "--jq", ".status"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                    env=env,
                )
                if p.returncode == 0 and p.stdout.strip():
                    status = p.stdout.strip()
                    break
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


def strict_tip() -> bool:
    """PATH_C_STRICT_TIP=1 restores the pre-b3c6 exact-equality gate (operator escape hatch)."""
    return os.environ.get("PATH_C_STRICT_TIP") == "1"


def acceptable(cls: str, landed: bool) -> bool:
    """MATCH always; DESCENDANT only when Path C is landed on tip (and not strict)."""
    if strict_tip():
        return cls == "MATCH"
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
