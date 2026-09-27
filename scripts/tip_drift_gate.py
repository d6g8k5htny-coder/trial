#!/usr/bin/env python3
"""tip_drift_gate — decide whether BASE_TIP vs live hardening tip is acceptable.

Path C landed on the hardening branch (``VERIFY.path_c_landed=true``,
``IDLE@0019``). After that, the hardening branch keeps moving because other
agents merge engineering PRs into it several times an hour. A strict
``live == BASE_TIP`` gate can therefore never stay green, and it painted 98 of
the last 100 trial ``main`` CI runs red (Batch 513→808 "keep-prior") while every
agent PR in trial inherited the same unrelated failure.

Gate semantics (fail-closed):

* ``EXACT``     — live tip == BASE_TIP → OK (unchanged behaviour).
* ``ANCESTOR``  — Path C is landed **and** BASE_TIP is an ancestor of the live
  tip → OK. The landed Path C commits are still in history (no rewrite) and the
  downstream ``math_status_check`` / ``lemma_closed=false`` gates still run on
  the live tip. Lag is reported as a notice, not an error.
* ``DRIFT``     — anything else (not landed, BASE_TIP not in live history,
  ancestry unresolvable) → exit 1 with the documented fix path.

Ancestry is resolved from a local clone when ``--repo-dir`` is given
(deepening a shallow clone as needed), then via the GitHub compare API, then
via a cached treeless ``git fetch`` of the hardening ref into a temp bare repo
(``$TIP_DRIFT_CACHE_DIR`` or ``$TMPDIR/trial-tip-drift-gate``) so a stale or
missing API token never turns lag into a false DRIFT. Unresolvable ancestry is
still treated as DRIFT (never silently OK).

Scientific effect: NONE. Never flips lemma_closed / prizes / premises.
Exit: 0 gate OK, 1 drift, 2 usage.
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

MAIN_REPO = "d6g8k5htny-coder/main"
HARDENING_REF = "chatgpt/drive-github-hardening-20260919"
FIX_PATH = "./scripts/refresh_path_c_bundle.sh"
_SHA40 = re.compile(r"(?i)\b([0-9a-f]{40})\b")


def parse_sha(text: str) -> str | None:
    m = _SHA40.search(text or "")
    if m:
        return m.group(1).lower()
    m = re.search(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)", text or "")
    return m.group(1).lower() if m else None


def read_base_tip(path: Path) -> str | None:
    if not path.is_file():
        return None
    first = path.read_text(encoding="utf-8").replace("\r", "").splitlines()
    return parse_sha(first[0]) if first else None


def read_landed(verify_path: Path | None) -> bool:
    if verify_path is None or not verify_path.is_file():
        return False
    try:
        with verify_path.open(encoding="utf-8") as fh:
            return json.load(fh).get("path_c_landed") is True
    except (OSError, json.JSONDecodeError):
        return False


def sha_matches(base: str | None, live: str | None) -> bool | None:
    if not base or not live:
        return None
    b, l = base.lower(), live.lower()
    if len(b) == 40:
        return l == b
    if 7 <= len(b) < 40:
        return l.startswith(b)
    return None


def _token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=timeout, check=False
    )


def ancestor_via_git(base: str, live: str, repo_dir: Path, deepen_steps: tuple[int, ...] = (200, 800)) -> bool | None:
    """merge-base --is-ancestor on a (possibly shallow) clone; deepen on demand."""
    if not (repo_dir / ".git").exists() and not (repo_dir / "HEAD").exists():
        return None
    if len(base) < 40:
        return None

    def _check() -> bool | None:
        have = _run(["git", "cat-file", "-e", f"{base}^{{commit}}"], cwd=repo_dir)
        if have.returncode != 0:
            return None
        anc = _run(["git", "merge-base", "--is-ancestor", base, live], cwd=repo_dir)
        if anc.returncode == 0:
            return True
        if anc.returncode == 1:
            return False
        return None

    result = _check()
    if result is not None:
        return result
    shallow = _run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo_dir)
    if shallow.stdout.strip() != "true":
        return result
    for depth in deepen_steps:
        _run(["git", "fetch", "-q", f"--deepen={depth}", "origin", HARDENING_REF], cwd=repo_dir, timeout=300)
        result = _check()
        if result is not None:
            return result
    _run(["git", "fetch", "-q", "--unshallow", "origin", HARDENING_REF], cwd=repo_dir, timeout=600)
    return _check()


def _cache_repo_dir() -> Path:
    override = os.environ.get("TIP_DRIFT_CACHE_DIR")
    if override:
        return Path(override)
    return Path(tempfile.gettempdir()) / "trial-tip-drift-gate" / MAIN_REPO.replace("/", "__")


def ancestor_via_temp_fetch(base: str, live: str, repo: str = MAIN_REPO) -> tuple[bool | None, int | None]:
    """Treeless fetch of the hardening ref into a cached bare repo; ancestry via git.

    Works without any API token (public repo or git credential helper). The repo
    is reused across invocations so repeated gate calls (tests, status writers)
    only pay for incremental fetches. Failures return (None, None) → fail closed.
    """
    if len(base) < 40 or len(live) < 40:
        return None, None
    cache = _cache_repo_dir()
    try:
        cache.mkdir(parents=True, exist_ok=True)
        if not (cache / "HEAD").exists():
            init = _run(["git", "init", "-q", "--bare", str(cache)])
            if init.returncode != 0:
                return None, None
        url = os.environ.get("TIP_DRIFT_REMOTE_URL") or f"https://github.com/{repo}.git"

        def _have(sha: str) -> bool:
            return _run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=cache).returncode == 0

        if not (_have(base) and _have(live)):
            _run(
                ["git", "-c", "protocol.version=2", "fetch", "-q", "--filter=tree:0", url, HARDENING_REF],
                cwd=cache,
                timeout=600,
            )
        for sha in (base, live):
            if not _have(sha):
                _run(["git", "-c", "protocol.version=2", "fetch", "-q", "--filter=tree:0", url, sha], cwd=cache, timeout=600)
        if not (_have(base) and _have(live)):
            return None, None
        anc = _run(["git", "merge-base", "--is-ancestor", base, live], cwd=cache)
        if anc.returncode not in (0, 1):
            return None, None
        ahead = None
        cnt = _run(["git", "rev-list", "--count", f"{base}..{live}"], cwd=cache)
        if cnt.returncode == 0 and cnt.stdout.strip().isdigit():
            ahead = int(cnt.stdout.strip())
        return anc.returncode == 0, ahead
    except (OSError, subprocess.SubprocessError):
        return None, None


def ancestor_via_api(base: str, live: str, repo: str = MAIN_REPO) -> tuple[bool | None, int | None]:
    """GitHub compare: base is ancestor iff status in {identical, ahead} (behind_by==0)."""
    url = f"https://api.github.com/repos/{repo}/compare/{base}...{live}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "trial-tip-drift-gate"}
    tok = _token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        return None, None
    status = data.get("status")
    behind = data.get("behind_by")
    ahead = data.get("ahead_by")
    if status in ("identical", "ahead") and behind == 0:
        return True, ahead if isinstance(ahead, int) else None
    if status in ("behind", "diverged"):
        return False, ahead if isinstance(ahead, int) else None
    return None, None


def evaluate(
    *,
    live: str | None,
    base: str | None,
    landed: bool,
    repo_dir: Path | None = None,
    use_api: bool = True,
    use_temp_fetch: bool = True,
) -> dict:
    """Return gate verdict dict; ``ok`` True only for EXACT or landed ANCESTOR."""
    report: dict = {
        "live_sha": live,
        "base_tip_sha": base,
        "path_c_landed": bool(landed),
        "tip_matches_base": sha_matches(base, live),
        "base_is_ancestor_of_live": None,
        "ahead_by": None,
        "ancestry_via": None,
        "mode": "DRIFT",
        "ok": False,
        "scientific_effect": "NONE",
        "lemma_closed_flipped": False,
        "fix_path": FIX_PATH,
    }
    if not live or not base:
        report["error"] = "missing live or BASE_TIP sha"
        return report
    if report["tip_matches_base"] is True:
        report.update(mode="EXACT", ok=True, base_is_ancestor_of_live=True, ahead_by=0)
        return report

    anc: bool | None = None
    if repo_dir is not None:
        try:
            anc = ancestor_via_git(base, live, repo_dir)
        except (OSError, subprocess.SubprocessError):
            anc = None
        if anc is not None:
            report["ancestry_via"] = "git"
    if anc is None and use_api:
        anc, ahead = ancestor_via_api(base, live)
        if anc is not None:
            report["ancestry_via"] = "github_compare_api"
            report["ahead_by"] = ahead
    if anc is None and use_temp_fetch:
        anc, ahead = ancestor_via_temp_fetch(base, live)
        if anc is not None:
            report["ancestry_via"] = "git_temp_fetch"
            report["ahead_by"] = ahead
    report["base_is_ancestor_of_live"] = anc
    if anc is True and report["ahead_by"] is None and repo_dir is not None:
        cnt = _run(["git", "rev-list", "--count", f"{base}..{live}"], cwd=repo_dir)
        if cnt.returncode == 0 and cnt.stdout.strip().isdigit():
            report["ahead_by"] = int(cnt.stdout.strip())

    if anc is True and landed:
        report.update(mode="ANCESTOR", ok=True)
    elif anc is True and not landed:
        report["reason"] = "BASE_TIP is an ancestor but Path C is not landed; bundle must be re-cut on the live tip"
    elif anc is False:
        report["reason"] = "BASE_TIP is not in the live tip history (rewrite/force-push?)"
    else:
        report["reason"] = "ancestry unresolvable (no clone / API transport); failing closed"
    return report


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--live", required=True, help="live hardening tip SHA")
    ap.add_argument("--base", help="BASE_TIP SHA (default: parse --base-file)")
    ap.add_argument("--base-file", default=str(root / "portable/patches/BASE_TIP.txt"))
    ap.add_argument("--verify", default=str(root / "portable/path-c-applied-bundle/VERIFY.json"))
    ap.add_argument("--repo-dir", help="local clone of main hardening for ancestry (deepened as needed)")
    ap.add_argument("--no-api", action="store_true", help="do not consult the GitHub compare API")
    ap.add_argument(
        "--no-temp-fetch", action="store_true", help="do not fall back to a cached treeless git fetch for ancestry"
    )
    ap.add_argument("--json", action="store_true", help="print JSON verdict")
    args = ap.parse_args(argv)

    live = parse_sha(args.live)
    base = parse_sha(args.base) if args.base else read_base_tip(Path(args.base_file))
    if not live:
        print("tip_drift_gate: usage: --live must be a hex SHA", file=sys.stderr)
        return 2
    if not base:
        print(f"::error::tip-drift: empty BASE_TIP — fix: {FIX_PATH}")
        return 1
    landed = read_landed(Path(args.verify) if args.verify else None)
    report = evaluate(
        live=live,
        base=base,
        landed=landed,
        repo_dir=Path(args.repo_dir) if args.repo_dir else None,
        use_api=not args.no_api,
        use_temp_fetch=not args.no_temp_fetch,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if report["ok"]:
        if report["mode"] == "EXACT":
            print(f"tip-drift gate OK: live==BASE_TIP @ {live[:7]}")
        else:
            lag = report.get("ahead_by")
            lag_s = f"{lag} commit(s)" if isinstance(lag, int) else "unknown count"
            print(
                f"tip-drift gate OK: BASE_TIP {base[:7]} is an ancestor of live {live[:7]} "
                f"(path_c_landed=true; live ahead by {lag_s}; via {report.get('ancestry_via')})"
            )
            print(
                f"::notice::tip-lag: BASE_TIP {base[:7]} lags live hardening {live[:7]} by {lag_s}; "
                f"Path C already on tip, no rebuild required (optional: {FIX_PATH})"
            )
        return 0
    print(f"::error::tip-drift: live hardening SHA {live} vs BASE_TIP {base}: {report.get('reason') or report.get('error')}")
    print(f"::error::tip-drift: fix path: {FIX_PATH}  (refresh BASE_TIP + rebuild path-c-applied-bundle; does NOT push to main hardening)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
