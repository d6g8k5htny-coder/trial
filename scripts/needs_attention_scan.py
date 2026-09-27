#!/usr/bin/env python3
"""Read-only scan of every owner repo for agent work that needs attention.

Writes ``needs_attention/SNAPSHOT.json`` and ``needs_attention/TRIAGE.md``.

Findings (engineering coordination only):

* ``PR_CHECKS_FAILING``     — open PR whose head has failing/erroring check runs
* ``PR_CONFLICTING``        — open PR GitHub reports as ``dirty`` (merge conflict)
* ``PR_CHANGES_REQUESTED``  — open PR whose latest review per reviewer is CHANGES_REQUESTED
* ``PR_STALE_DRAFT``        — open draft PR untouched for >= ``--stale-hours``
* ``LEASE_EXPIRED``         — ``governance-`` work lease still ACTIVE/OFFERED past ``expires_at``
* ``CARD_OPEN``             — open card in ``needs_attention/cards``

Uses the GitHub REST API with ``GITHUB_TOKEN``/``GH_TOKEN`` (falls back to
``gh auth token``). Transport failures are recorded per repo, never fatal.

Scientific effect: NONE. Never writes to GitHub. Exit 0 always on a completed
scan (findings are data, not failures); exit 2 on usage/IO errors.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNER = "d6g8k5htny-coder"
REPOS = (
    "main",
    "Math-",
    "trial",
    "governance-",
    "query-",
    "Universal-Law-Workspace",
    "sandbox",
    "meta-framework",
    "google-drive",
    "d6g8k5htny-coder",
)
LEASE_PATH = "work_leases/CURRENT.json"
FAILING_CONCLUSIONS = {"failure", "timed_out", "action_required", "cancelled", "startup_failure"}
SEVERITY = {
    "PR_CHECKS_FAILING": "high",
    "PR_CONFLICTING": "high",
    "PR_CHANGES_REQUESTED": "medium",
    "LEASE_EXPIRED": "medium",
    "PR_STALE_DRAFT": "low",
    "CARD_OPEN": "info",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(text: str | None) -> datetime | None:
    if not text or not isinstance(text, str):
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=20, check=False)
        tok = out.stdout.strip()
        return tok or None
    except (OSError, subprocess.SubprocessError):
        return None


class GitHub:
    def __init__(self, token: str | None) -> None:
        self.token = token
        self.calls = 0
        self.errors: list[str] = []

    def get(self, path: str, params: str = "") -> object | None:
        url = f"https://api.github.com{path}{('?' + params) if params else ''}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "trial-needs-attention-scan"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self.calls += 1
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            self.errors.append(f"HTTP {exc.code} {path}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            self.errors.append(f"transport {path}: {exc}")
        return None


# ---------------------------------------------------------------- pure logic


def classify_pr(
    pr: dict,
    check_runs: list[dict] | None,
    reviews: list[dict] | None,
    *,
    now: datetime,
    stale_hours: int,
    repo: str,
) -> list[dict]:
    """Return findings for one open PR (pure; testable offline)."""
    findings: list[dict] = []
    number = pr.get("number")
    url = pr.get("html_url") or f"https://github.com/{repo}/pull/{number}"
    base = {"repo": repo, "pr": number, "url": url, "title": pr.get("title"), "author": (pr.get("user") or {}).get("login"), "head_ref": (pr.get("head") or {}).get("ref"), "draft": bool(pr.get("draft"))}

    failing = []
    latest_runs: dict[str, dict] = {}
    for run in check_runs or []:
        # GitHub returns every attempt for the head SHA; keep the newest per check
        # name so a superseded red rerun does not mask a later green one.
        name = run.get("name") or "?"
        key = (run.get("completed_at") or run.get("started_at") or "", run.get("id") or 0)
        prev = latest_runs.get(name)
        if prev is None or key > prev["_key"]:
            latest_runs[name] = {**run, "_key": key}
    for run in latest_runs.values():
        concl = (run.get("conclusion") or "").lower()
        if concl in FAILING_CONCLUSIONS:
            failing.append({"name": run.get("name"), "conclusion": concl, "url": run.get("html_url")})
    if failing:
        findings.append({**base, "kind": "PR_CHECKS_FAILING", "detail": failing})

    if pr.get("mergeable_state") == "dirty" or pr.get("mergeable") is False:
        findings.append({**base, "kind": "PR_CONFLICTING", "detail": {"mergeable_state": pr.get("mergeable_state")}})

    latest: dict[str, str] = {}
    for rv in sorted(reviews or [], key=lambda r: r.get("submitted_at") or ""):
        login = (rv.get("user") or {}).get("login")
        state = (rv.get("state") or "").upper()
        if login and state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[login] = state
    blockers = sorted(k for k, v in latest.items() if v == "CHANGES_REQUESTED")
    if blockers:
        findings.append({**base, "kind": "PR_CHANGES_REQUESTED", "detail": {"reviewers": blockers}})

    updated = _parse_iso(pr.get("updated_at"))
    if pr.get("draft") and updated and now - updated >= timedelta(hours=stale_hours):
        findings.append({**base, "kind": "PR_STALE_DRAFT", "detail": {"updated_at": pr.get("updated_at"), "idle_hours": round((now - updated).total_seconds() / 3600, 1)}})

    for f in findings:
        f["severity"] = SEVERITY[f["kind"]]
    return findings


def expired_leases(ledger: dict, *, now: datetime) -> list[dict]:
    """ACTIVE/OFFERED leases whose expires_at is in the past (pure)."""
    out: list[dict] = []
    for lease in ledger.get("leases", []) if isinstance(ledger, dict) else []:
        state = lease.get("state")
        exp = _parse_iso(lease.get("expires_at"))
        if state in ("ACTIVE", "OFFERED") and exp and exp < now:
            src = lease.get("source") or {}
            out.append(
                {
                    "kind": "LEASE_EXPIRED",
                    "severity": SEVERITY["LEASE_EXPIRED"],
                    "repo": f"{OWNER}/governance-",
                    "work_id": lease.get("work_id"),
                    "state": state,
                    "expires_at": lease.get("expires_at"),
                    "overdue_hours": round((now - exp).total_seconds() / 3600, 1),
                    "owner": (lease.get("owner") or {}).get("provider"),
                    "source_repo": src.get("repo"),
                    "source_pr": src.get("pr"),
                    "scope": lease.get("scope"),
                }
            )
    return out


def open_cards(root: Path) -> list[dict]:
    out: list[dict] = []
    for path in sorted((root / "needs_attention" / "cards").glob("*.json")):
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if card.get("status") in ("OPEN", "IN_PROGRESS"):
            out.append(
                {
                    "kind": "CARD_OPEN",
                    "severity": SEVERITY["CARD_OPEN"],
                    "repo": card.get("repo"),
                    "card": card.get("id"),
                    "status": card.get("status"),
                    "title": card.get("title"),
                    "path": path.relative_to(root).as_posix(),
                }
            )
    return out


def render_triage(snapshot: dict) -> str:
    lines = [
        "# needs_attention — TRIAGE (auto-generated; scientific effect NONE)",
        "",
        f"Generated `{snapshot['generated_at']}` · repos scanned {snapshot['repos_scanned']} · open PRs {snapshot['open_prs']} · API calls {snapshot['api_calls']}",
        "",
        "Findings are coordination signals only. Nothing here promotes, closes, or discharges research status.",
        "",
    ]
    by_kind: dict[str, list[dict]] = {}
    for f in snapshot["findings"]:
        by_kind.setdefault(f["kind"], []).append(f)
    order = ["CARD_OPEN", "PR_CHECKS_FAILING", "PR_CONFLICTING", "PR_CHANGES_REQUESTED", "LEASE_EXPIRED", "PR_STALE_DRAFT"]
    for kind in order:
        items = by_kind.get(kind) or []
        lines.append(f"## {kind} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("- none")
        for f in items:
            if kind == "CARD_OPEN":
                lines.append(f"- `{f['card']}` [{f['status']}] {f['title']} — `{f['path']}`")
            elif kind == "LEASE_EXPIRED":
                lines.append(f"- `{f['work_id']}` [{f['state']}] overdue {f['overdue_hours']}h (owner={f['owner']}, {f['source_repo']}#{f['source_pr']}) — {f['scope']}")
            else:
                extra = ""
                if kind == "PR_CHECKS_FAILING":
                    extra = " — failing: " + ", ".join(sorted({d['name'] or '?' for d in f['detail']}))
                elif kind == "PR_CHANGES_REQUESTED":
                    extra = " — by " + ", ".join(f["detail"]["reviewers"])
                elif kind == "PR_STALE_DRAFT":
                    extra = f" — idle {f['detail']['idle_hours']}h"
                lines.append(f"- [{f['repo'].split('/')[-1]}#{f['pr']}]({f['url']}) {f['title']} (draft={f['draft']}){extra}")
        lines.append("")
    if snapshot.get("transport_errors"):
        lines.append("## transport errors")
        lines.append("")
        lines.extend(f"- {e}" for e in snapshot["transport_errors"])
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- live scan


def scan(root: Path, *, stale_hours: int, repos: tuple[str, ...], gh: GitHub, now: datetime) -> dict:
    findings: list[dict] = []
    open_prs = 0
    scanned = 0
    for name in repos:
        repo = f"{OWNER}/{name}"
        prs = gh.get(f"/repos/{repo}/pulls", "state=open&per_page=100")
        if not isinstance(prs, list):
            continue
        scanned += 1
        for summary in prs:
            number = summary.get("number")
            detail = gh.get(f"/repos/{repo}/pulls/{number}") or summary
            sha = ((detail.get("head") or {}).get("sha")) or ""
            runs_payload = gh.get(f"/repos/{repo}/commits/{sha}/check-runs", "per_page=100") if sha else None
            check_runs = (runs_payload or {}).get("check_runs") if isinstance(runs_payload, dict) else None
            reviews = gh.get(f"/repos/{repo}/pulls/{number}/reviews", "per_page=100")
            open_prs += 1
            findings.extend(
                classify_pr(detail, check_runs, reviews if isinstance(reviews, list) else None, now=now, stale_hours=stale_hours, repo=repo)
            )
    ledger_raw = gh.get(f"/repos/{OWNER}/governance-/contents/{LEASE_PATH}", "ref=main")
    if isinstance(ledger_raw, dict) and ledger_raw.get("encoding") == "base64":
        import base64

        try:
            ledger = json.loads(base64.b64decode(ledger_raw["content"]).decode("utf-8"))
            findings.extend(expired_leases(ledger, now=now))
            ledger_updated = ledger.get("updated_at")
        except (ValueError, json.JSONDecodeError):
            ledger_updated = None
    else:
        ledger_updated = None
    findings = open_cards(root) + findings
    sev_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda f: (sev_rank.get(f["severity"], 9), f.get("repo") or "", f.get("pr") or 0))
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    return {
        "schema": "needs_attention.snapshot/v1",
        "generated_at": _iso(now),
        "scientific_effect": "NONE",
        "lemma_closed_flipped": False,
        "repos_requested": [f"{OWNER}/{r}" for r in repos],
        "repos_scanned": scanned,
        "open_prs": open_prs,
        "api_calls": gh.calls,
        "authenticated": bool(gh.token),
        "lease_ledger_updated_at": ledger_updated,
        "counts": counts,
        "findings": findings,
        "transport_errors": gh.errors,
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(root))
    ap.add_argument("--stale-hours", type=int, default=48)
    ap.add_argument("--repos", default=",".join(REPOS), help="comma-separated repo names under the owner")
    ap.add_argument("--out", help="snapshot path (default needs_attention/SNAPSHOT.json)")
    ap.add_argument("--no-write", action="store_true", help="print snapshot JSON only")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not (root / "needs_attention").is_dir():
        print(f"needs_attention_scan: missing {root / 'needs_attention'}", file=sys.stderr)
        return 2
    repos = tuple(r for r in args.repos.split(",") if r)
    snapshot = scan(root, stale_hours=args.stale_hours, repos=repos, gh=GitHub(_token()), now=_utc_now())
    text = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    if args.no_write:
        print(text)
        return 0
    out = Path(args.out) if args.out else root / "needs_attention" / "SNAPSHOT.json"
    out.write_text(text, encoding="utf-8")
    (out.parent / "TRIAGE.md").write_text(render_triage(snapshot) + "\n", encoding="utf-8")
    print(
        f"needs_attention_scan: repos={snapshot['repos_scanned']} open_prs={snapshot['open_prs']} "
        f"findings={len(snapshot['findings'])} {snapshot['counts']} errors={len(snapshot['transport_errors'])} -> {out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
