#!/usr/bin/env python3
"""Path C tip gate — decide whether the live hardening tip is acceptable.

Scientific effect: NONE. Never flips lemma_closed / prizes / premises.

Before this helper every gate (trial CI, refresh_path_c_bundle.sh,
assert_path_c_ready.sh, owner_land_path_c.sh, owner_open_path_c_pr.sh,
path_c_dry_run.py) required the live ``chatgpt/drive-github-hardening-20260919``
SHA to be byte-equal to ``portable/patches/BASE_TIP.txt``.  That was the right
contract while Path C still had to be *applied*: a bundle cut on a stale base
must not silently dry-apply on a moved tip.

Path C is now landed (``VERIFY.json`` ``path_c_landed=true``; the 0019 merge is
in hardening history) and the wake loop keeps BASE_TIP immutable while the
hardening branch is actively developed.  Under those two facts ``live == BASE``
can never be true again, so the equality gate is red forever without saying
anything about Path C.  The honest question is ancestry:

    TIP_MATCH        live == BASE_TIP                              -> tip_ok
    LANDED_ANCESTOR  path_c_landed and BASE_TIP is an ancestor of live
                     and the recorded 0019 merge is an ancestor of live
                                                                   -> tip_ok
    TIP_DRIFT        anything else (BASE not in live history,
                     rewritten branch, Path C not landed)          -> not ok
    UNKNOWN          ancestry could not be established (no history,
                     no network)                                   -> not ok

``tip_matches_base`` stays a literal equality so no consumer is lied to; the
new ``tip_ok`` / ``tip_state`` carry the gate decision.

CLI::

    python3 scripts/path_c_tip_gate.py [--live SHA] [--repo-dir DIR]
        [--trial-root DIR] [--sh | --json]

Exit 0 when tip_ok, 1 on TIP_DRIFT, 2 on UNKNOWN / resolution failure.
``--sh`` prints ``KEY=VALUE`` lines safe to ``eval`` in bash.
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

REPO = "d6g8k5htny-coder/main"
HARDENING = "chatgpt/drive-github-hardening-20260919"
_SHA40 = re.compile(r"(?i)\b([0-9a-f]{40})\b")
_SHA7 = re.compile(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)")
_DEEPEN_STEPS = (200, 400, 800, 1600)


def parse_base_tip_sha(line: str) -> str:
    m = _SHA40.search(line or "")
    if m:
        return m.group(1).lower()
    m = _SHA7.search(line or "")
    return m.group(1).lower() if m else ""


def _trial_root() -> Path:
    here = Path(__file__).resolve()
    for cand in (here.parents[1], Path.cwd()):
        if (cand / "portable" / "patches" / "BASE_TIP.txt").is_file():
            return cand
    return here.parents[1]


def read_base_tip(trial_root: Path) -> str:
    p = trial_root / "portable" / "patches" / "BASE_TIP.txt"
    if not p.is_file():
        return ""
    first = p.read_text(encoding="utf-8").replace("\r", "").splitlines()
    return parse_base_tip_sha(first[0] if first else "")


def read_verify(trial_root: Path) -> dict:
    p = trial_root / "portable" / "path-c-applied-bundle" / "VERIFY.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _sha_prefix_eq(a: str, b: str) -> bool:
    a = (a or "").lower()
    b = (b or "").lower()
    if not a or not b or len(a) < 7 or len(b) < 7:
        return False
    return a == b or a.startswith(b) or b.startswith(a)


def _token() -> str:
    for k in ("GITHUB_TOKEN", "GH_TOKEN", "MAIN_PUSH_TOKEN"):
        v = os.environ.get(k, "").strip()
        if v:
            return v
    return ""


def _has_commit(repo_dir: Path, sha: str) -> bool:
    return _run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=repo_dir).returncode == 0


def is_ancestor_git(repo_dir: Path, ancestor: str, descendant: str) -> bool | None:
    """merge-base --is-ancestor with progressive deepening on shallow clones.

    Returns True / False when git can decide, None when it cannot (object
    missing after the deepen budget, not a repo, git errors).
    """
    if not (repo_dir / ".git").exists() and not (repo_dir / "HEAD").exists():
        return None
    shallow = _run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo_dir).stdout.strip() == "true"
    steps = list(_DEEPEN_STEPS) if shallow else []
    while True:
        if _has_commit(repo_dir, ancestor) and _has_commit(repo_dir, descendant):
            r = _run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=repo_dir)
            if r.returncode == 0:
                return True
            if r.returncode == 1:
                # On a shallow clone "not ancestor" may just mean the history is
                # cut; deepen and retry, and let the API decide once the deepen
                # budget is spent rather than reporting a false negative.
                if not shallow:
                    return False
                if not steps:
                    return None
            elif r.returncode != 0:
                return None
        if not steps:
            return None
        n = steps.pop(0)
        deep = _run(["git", "fetch", "--quiet", f"--deepen={n}", "origin"], cwd=repo_dir, timeout=900)
        if deep.returncode != 0:
            # Some hosts reject --deepen after --filter clones; try an explicit ref fetch.
            _run(["git", "fetch", "--quiet", "--depth", str(n), "origin", ancestor], cwd=repo_dir, timeout=900)


def is_ancestor_api(ancestor: str, descendant: str, token: str = "") -> bool | None:
    """GitHub compare API: status ahead/identical => ancestor; behind/diverged => not."""
    url = f"https://api.github.com/repos/{REPO}/compare/{ancestor}...{descendant}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "trial-path-c-tip-gate"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed https host
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None
    status = str(data.get("status") or "")
    if status in ("ahead", "identical"):
        return True
    if status in ("behind", "diverged"):
        return False
    return None


_HISTORY_CLONE: dict[str, Path | None] = {}


def _history_clone(token: str = "") -> Path | None:
    """Blobless shallow clone of the hardening branch (commits+trees only).

    Used when no --repo-dir was given. Lives in a reusable cache dir
    (PATH_C_TIP_GATE_CACHE, default $TMPDIR/path-c-tip-gate-cache) so repeated
    gate calls across processes cost one fetch, not one compare-API call each
    (anonymous API quota is 60/h on shared runners). Cached per process too.
    """
    if "clone" in _HISTORY_CLONE:
        return _HISTORY_CLONE["clone"]
    import tempfile

    url = f"https://github.com/{REPO}.git"
    if token:
        url = f"https://x-access-token:{token}@github.com/{REPO}.git"
    cache_root = Path(os.environ.get("PATH_C_TIP_GATE_CACHE") or (Path(tempfile.gettempdir()) / "path-c-tip-gate-cache"))
    dest = cache_root / "main"
    if (dest / ".git").is_dir():
        fetch = _run(
            ["git", "fetch", "--quiet", "origin", f"+refs/heads/{HARDENING}:refs/remotes/origin/{HARDENING}"],
            cwd=dest,
            timeout=600,
        )
        _HISTORY_CLONE["clone"] = dest if fetch.returncode == 0 else dest
        return dest
    cache_root.mkdir(parents=True, exist_ok=True)
    r = _run(
        ["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", "--depth", str(_DEEPEN_STEPS[0]), "--branch", HARDENING, url, str(dest)],
        timeout=900,
    )
    _HISTORY_CLONE["clone"] = dest if r.returncode == 0 else None
    return _HISTORY_CLONE["clone"]


def is_ancestor(ancestor: str, descendant: str, repo_dir: Path | None, token: str = "") -> tuple[bool | None, str]:
    if _sha_prefix_eq(ancestor, descendant):
        return True, "identical"
    if repo_dir is not None:
        got = is_ancestor_git(repo_dir, ancestor, descendant)
        if got is not None:
            return got, "git"
    if os.environ.get("PATH_C_TIP_GATE_NO_CLONE", "") != "1":
        clone = _history_clone(token)
        if clone is not None:
            got = is_ancestor_git(clone, ancestor, descendant)
            if got is not None:
                return got, "git_cache_clone"
    got = is_ancestor_api(ancestor, descendant, token)
    if got is not None:
        return got, "api"
    return None, "none"


def resolve_live_sha(repo_dir: Path | None, token: str = "") -> str:
    if repo_dir is not None:
        for ref in (f"refs/remotes/origin/{HARDENING}", "HEAD"):
            r = _run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=repo_dir)
            sha = r.stdout.strip().lower()
            if r.returncode == 0 and _SHA40.fullmatch(sha):
                return sha
    url = f"https://github.com/{REPO}.git"
    if token:
        url = f"https://x-access-token:{token}@github.com/{REPO}.git"
    r = _run(["git", "ls-remote", url, f"refs/heads/{HARDENING}"], timeout=120)
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and _SHA40.fullmatch(parts[0].lower()):
            return parts[0].lower()
    return ""


def evaluate(
    live_sha: str,
    base_sha: str,
    *,
    path_c_landed: bool,
    landed_merge_sha: str = "",
    repo_dir: Path | None = None,
    token: str = "",
) -> dict:
    out: dict = {
        "live_sha": live_sha,
        "base_tip_sha": base_sha,
        "path_c_landed": bool(path_c_landed),
        "landed_merge_sha": landed_merge_sha or "",
        "tip_matches_base": False,
        "base_is_ancestor_of_live": None,
        "landed_merge_is_ancestor_of_live": None,
        "ancestry_via": "n/a",
        "tip_state": "UNKNOWN",
        "tip_ok": False,
        "scientific_effect": "NONE",
    }
    if not live_sha or not base_sha:
        out["tip_state"] = "UNKNOWN"
        out["reason"] = "missing live or BASE_TIP sha"
        return out
    if _sha_prefix_eq(live_sha, base_sha):
        out["tip_matches_base"] = True
        out["base_is_ancestor_of_live"] = True
        out["landed_merge_is_ancestor_of_live"] = True if landed_merge_sha else None
        out["tip_state"] = "TIP_MATCH"
        out["tip_ok"] = True
        return out
    if not path_c_landed:
        out["tip_state"] = "TIP_DRIFT"
        out["reason"] = "live != BASE_TIP and Path C not landed — bundle must be refreshed before apply"
        return out
    base_anc, via = is_ancestor(base_sha, live_sha, repo_dir, token)
    out["base_is_ancestor_of_live"] = base_anc
    out["ancestry_via"] = via
    if base_anc is None:
        out["tip_state"] = "UNKNOWN"
        out["reason"] = "could not establish BASE_TIP ancestry (no history / no network)"
        return out
    if base_anc is False:
        out["tip_state"] = "TIP_DRIFT"
        out["reason"] = "BASE_TIP is not in live hardening history (rewritten or diverged branch)"
        return out
    if landed_merge_sha:
        merge_anc, via2 = is_ancestor(landed_merge_sha, live_sha, repo_dir, token)
        out["landed_merge_is_ancestor_of_live"] = merge_anc
        if via2 != "identical":
            out["ancestry_via"] = via if via == via2 else f"{via}+{via2}"
        if merge_anc is None:
            out["tip_state"] = "UNKNOWN"
            out["reason"] = "could not establish 0019 merge ancestry"
            return out
        if merge_anc is False:
            out["tip_state"] = "TIP_DRIFT"
            out["reason"] = "recorded Path C 0019 merge is not in live hardening history"
            return out
    out["tip_state"] = "LANDED_ANCESTOR"
    out["tip_ok"] = True
    return out


def gate(
    live_sha: str = "",
    *,
    trial_root: Path | None = None,
    repo_dir: Path | None = None,
    token: str | None = None,
) -> dict:
    root = trial_root or _trial_root()
    tok = _token() if token is None else token
    verify = read_verify(root)
    live = (live_sha or "").strip().lower() or resolve_live_sha(repo_dir, tok)
    res = evaluate(
        live,
        read_base_tip(root),
        path_c_landed=verify.get("path_c_landed") is True,
        landed_merge_sha=str(verify.get("path_c_0019_merge_commit_sha") or ""),
        repo_dir=repo_dir,
        token=tok,
    )
    res["trial_root"] = str(root)
    return res


def _sh_quote(v) -> str:
    s = "" if v is None else str(v)
    if isinstance(v, bool):
        s = "true" if v else "false"
    return "'" + s.replace("'", "'\"'\"'") + "'"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Path C tip gate (TIP_MATCH | LANDED_ANCESTOR | TIP_DRIFT | UNKNOWN)")
    ap.add_argument("--live", default="", help="live hardening SHA (default: resolve from --repo-dir or ls-remote)")
    ap.add_argument("--repo-dir", default="", help="clone of d6g8k5htny-coder/main to use for ancestry (may be shallow)")
    ap.add_argument("--trial-root", default="", help="trial checkout root (default: auto)")
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--sh", action="store_true", help="print KEY=VALUE lines for bash eval")
    fmt.add_argument("--json", action="store_true", help="print JSON (default)")
    args = ap.parse_args(argv)

    res = gate(
        args.live,
        trial_root=Path(args.trial_root).resolve() if args.trial_root else None,
        repo_dir=Path(args.repo_dir).resolve() if args.repo_dir else None,
    )
    if args.sh:
        for k in (
            "tip_state",
            "tip_ok",
            "tip_matches_base",
            "live_sha",
            "base_tip_sha",
            "landed_merge_sha",
            "path_c_landed",
            "base_is_ancestor_of_live",
            "landed_merge_is_ancestor_of_live",
            "ancestry_via",
            "reason",
        ):
            print(f"TIP_GATE_{k.upper()}={_sh_quote(res.get(k))}")
    else:
        print(json.dumps(res, indent=2, sort_keys=True))
    if res["tip_ok"]:
        return 0
    return 1 if res["tip_state"] == "TIP_DRIFT" else 2


if __name__ == "__main__":
    sys.exit(main())
