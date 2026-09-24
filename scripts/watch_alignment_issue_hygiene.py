#!/usr/bin/env python3
"""Upsert/close trial \"main ALIGNED drift\" issues for watch-main-alignment.

Batch 252: installation/App tokens hit two list/search bugs that left drift
issues stranded or created duplicates when open-issue counts were high:

  1) REST ``GET /repos/.../issues?state=open`` can return ``[]`` for App tokens
     while GraphQL still sees the open issues (device-user PAT lists them).
  2) Search API / ``gh issue list --search`` under App tokens often returns
     ``total_count=0`` or ghost ``{number:0}`` rows — never use Search here.

This helper paginates GraphQL ``repository.issues`` and matches the exact
title client-side. On ALIGNED it closes **all** open matches (dedupe). On
MISALIGNED it reopens/updates the lowest-number canonical and closes other
open duplicates into it.

Scientific effect: NONE. Never flips lemma_closed / prizes / premises /
research status. Never writes to d6g8k5htny-coder/main.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

DEFAULT_TITLE = "main ALIGNED drift"
DEFAULT_REPO = "d6g8k5htny-coder/trial"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gh_api_graphql(query: str, variables: dict[str, Any] | None = None) -> dict:
    """Run gh api graphql with per-field -f/-F bindings (not Search API).

    Batch 252: App/install tokens must not use Search; bind variables as
    individual fields (``-f`` strings / ``-F`` typed) — a single JSON
    ``variables=`` blob is unreliable across gh versions.
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, val in (variables or {}).items():
        if val is None:
            # Cursor on first page: explicit GraphQL null.
            cmd.extend(["-F", f"{key}=null"])
        elif isinstance(val, bool):
            cmd.extend(["-F", f"{key}={str(val).lower()}"])
        elif isinstance(val, (int, float)):
            cmd.extend(["-F", f"{key}={val}"])
        else:
            cmd.extend(["-f", f"{key}={val}"])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"graphql failed exit={proc.returncode}: "
            f"{(proc.stderr or proc.stdout or '')[-800:]}"
        )
    payload = json.loads(proc.stdout or "{}")
    if payload.get("errors"):
        raise RuntimeError(f"graphql errors: {payload['errors']!r}"[:800])
    return payload


def list_issues_by_exact_title(
    owner: str,
    name: str,
    title: str,
    *,
    page_size: int = 100,
    max_pages: int = 20,
    graphql_runner=_gh_api_graphql,
) -> list[dict[str, Any]]:
    """Return all issues with exact title via GraphQL (OPEN+CLOSED).

    Never uses Search API. Never relies on REST open-list (App-token empty).
    """
    query = """
    query($owner:String!, $name:String!, $cursor:String, $pageSize:Int!) {
      repository(owner:$owner, name:$name) {
        issues(
          first: $pageSize,
          after: $cursor,
          states: [OPEN, CLOSED],
          orderBy: {field: UPDATED_AT, direction: DESC}
        ) {
          pageInfo { hasNextPage endCursor }
          nodes { number title state url }
        }
      }
    }
    """
    hits: list[dict[str, Any]] = []
    cursor = None
    for _ in range(max_pages):
        payload = graphql_runner(
            query,
            {
                "owner": owner,
                "name": name,
                "cursor": cursor,
                "pageSize": page_size,
            },
        )
        repo = (payload.get("data") or {}).get("repository") or {}
        conn = repo.get("issues") or {}
        for node in conn.get("nodes") or []:
            if (node or {}).get("title") == title:
                hits.append(
                    {
                        "number": int(node["number"]),
                        "title": node["title"],
                        "state": str(node.get("state") or "").upper(),
                        "url": node.get("url") or "",
                    }
                )
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
        if not cursor:
            break
    hits.sort(key=lambda x: x["number"])
    return hits


def pick_canonical(issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Lowest number wins (stable canonical across reopen cycles)."""
    if not issues:
        return None
    return sorted(issues, key=lambda x: x["number"])[0]


def open_duplicates(
    issues: list[dict[str, Any]], canonical_number: int
) -> list[dict[str, Any]]:
    return [
        i
        for i in issues
        if i.get("state") == "OPEN" and int(i["number"]) != int(canonical_number)
    ]


def misaligned_body(tip_sha: str, watched_at: str) -> str:
    short = (tip_sha or "")[:12]
    return f"""## main ALIGNED drift

Remote `d6g8k5htny-coder/main` default tip looks **MISALIGNED**.

| field | value |
| --- | --- |
| tip_sha | `{tip_sha}` |
| tip_short | `{short}` |
| watched_at_utc | {watched_at} |
| preferred_restore | Path B (`restore_main_face.sh`) |
| alternate | Path A (PR #2 / revert-of-revert) |

Scientific effect: **NONE**. Never flip `lemma_closed` / prizes / premises / research status.
This issue lives on **trial** only — the watch never writes to `main`.

Re-run: Actions → `watch-main-alignment` → Run workflow.
"""


def _run_gh(args: list[str], *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"dry_run": True, "args": args, "ok": True}
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    return {
        "dry_run": False,
        "args": args,
        "ok": proc.returncode == 0,
        "exit": proc.returncode,
        "stdout": (proc.stdout or "")[-500:],
        "stderr": (proc.stderr or "")[-500:],
    }


def apply_hygiene(
    *,
    state: str,
    tip_sha: str,
    repo: str,
    title: str = DEFAULT_TITLE,
    dry_run: bool = False,
    issues: list[dict[str, Any]] | None = None,
    graphql_runner=_gh_api_graphql,
) -> dict[str, Any]:
    """Apply ALIGNED close-all / MISALIGNED upsert+dedupe. Never flips research."""
    owner, _, name = repo.partition("/")
    if not owner or not name:
        raise ValueError(f"repo must be owner/name, got {repo!r}")

    state_u = (state or "").strip().upper()
    watched_at = _now_utc()
    short = (tip_sha or "")[:12]
    report: dict[str, Any] = {
        "action": "noop",
        "state": state_u,
        "repo": repo,
        "title": title,
        "tip_sha": tip_sha,
        "tip_short": short,
        "watched_at_utc": watched_at,
        "dry_run": dry_run,
        "list_via": "graphql_exact_title",
        "avoid_search_api": True,
        "avoid_rest_open_list": True,
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "flipped_anything": False,
        "issues_matched": [],
        "canonical": None,
        "closed": [],
        "reopened": None,
        "created": None,
        "ops": [],
    }

    if state_u in ("TRANSPORT_ERROR", "") or state_u is None:
        report["action"] = "leave_untouched"
        report["reason"] = "transport_or_unknown_state"
        return report

    if issues is None:
        issues = list_issues_by_exact_title(
            owner, name, title, graphql_runner=graphql_runner
        )
    report["issues_matched"] = issues

    if state_u == "ALIGNED":
        open_hits = [i for i in issues if i.get("state") == "OPEN"]
        if not open_hits:
            report["action"] = "aligned_noop"
            report["reason"] = "no_open_drift_issue"
            return report
        report["action"] = "aligned_close_all"
        for hit in open_hits:
            n = int(hit["number"])
            comment = (
                f"Default tip ALIGNED again @ `{short}` ({watched_at}). "
                f"Closing drift issue #{n} (Batch 252 close-all dedupe). "
                "Scientific effect: NONE. Never flipped research status."
            )
            op = _run_gh(
                [
                    "issue",
                    "close",
                    str(n),
                    "--repo",
                    repo,
                    "--comment",
                    comment,
                ],
                dry_run=dry_run,
            )
            report["ops"].append(op)
            if op.get("ok"):
                report["closed"].append(n)
        return report

    if state_u == "MISALIGNED":
        canonical = pick_canonical(issues)
        body = misaligned_body(tip_sha, watched_at)
        body_path = None
        try:
            if dry_run:
                body_path = "/dev/null"
            else:
                import tempfile

                fd, body_path = tempfile.mkstemp(prefix="aligned-drift-", suffix=".md")
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(body)

            if canonical is None:
                report["action"] = "misaligned_create"
                op = _run_gh(
                    [
                        "issue",
                        "create",
                        "--repo",
                        repo,
                        "--title",
                        title,
                        "--body-file",
                        body_path,
                    ],
                    dry_run=dry_run,
                )
                report["ops"].append(op)
                report["created"] = True
                return report

            canon_n = int(canonical["number"])
            report["canonical"] = canon_n
            report["action"] = "misaligned_upsert_dedupe"
            # Reopen + edit + comment canonical.
            for args in (
                ["issue", "reopen", str(canon_n), "--repo", repo],
                [
                    "issue",
                    "edit",
                    str(canon_n),
                    "--repo",
                    repo,
                    "--body-file",
                    body_path,
                ],
                [
                    "issue",
                    "comment",
                    str(canon_n),
                    "--repo",
                    repo,
                    "--body",
                    f"Still MISALIGNED @ `{short}` ({watched_at}). Scientific effect: NONE.",
                ],
            ):
                op = _run_gh(args, dry_run=dry_run)
                report["ops"].append(op)
            report["reopened"] = canon_n

            for dup in open_duplicates(issues, canon_n):
                dn = int(dup["number"])
                comment = (
                    f"Batch 252 dedupe: duplicate open drift issue closed into "
                    f"canonical #{canon_n} (still MISALIGNED @ `{short}`). "
                    "Scientific effect: NONE."
                )
                op = _run_gh(
                    [
                        "issue",
                        "close",
                        str(dn),
                        "--repo",
                        repo,
                        "--comment",
                        comment,
                    ],
                    dry_run=dry_run,
                )
                report["ops"].append(op)
                if op.get("ok"):
                    report["closed"].append(dn)
            return report
        finally:
            if body_path and body_path != "/dev/null" and os.path.isfile(body_path):
                try:
                    os.remove(body_path)
                except OSError:
                    pass

    report["action"] = "leave_untouched"
    report["reason"] = f"unhandled_state:{state_u}"
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=(
            "GraphQL exact-title hygiene for trial 'main ALIGNED drift' issues. "
            "Avoids Search API + App REST open-list empties. Scientific effect: NONE."
        )
    )
    p.add_argument(
        "--state",
        required=True,
        help="ALIGNED | MISALIGNED | TRANSPORT_ERROR",
    )
    p.add_argument("--tip-sha", default="", help="Default tip SHA from drift watch")
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO))
    p.add_argument("--title", default=DEFAULT_TITLE)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="List + plan only; do not create/close/comment",
    )
    p.add_argument(
        "--json-issues",
        default="",
        help="Optional JSON list of {number,title,state} (tests / offline)",
    )
    args = p.parse_args(argv)

    issues = None
    if args.json_issues:
        issues = json.loads(args.json_issues)

    report = apply_hygiene(
        state=args.state,
        tip_sha=args.tip_sha,
        repo=args.repo,
        title=args.title,
        dry_run=args.dry_run,
        issues=issues,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    # Soft-fail only on hard graphql/ops collapse when not dry-run leave_untouched.
    if report.get("action") in ("leave_untouched", "aligned_noop", "aligned_close_all",
                                 "misaligned_create", "misaligned_upsert_dedupe"):
        ops = report.get("ops") or []
        if ops and not args.dry_run and any(not o.get("ok") for o in ops):
            return 1
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
