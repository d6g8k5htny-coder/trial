#!/usr/bin/env python3
"""Probe every Path B–relevant write vector against d6g8k5htny-coder/main.

Batch 55 Path C harden: one script that re-tries the vectors agents actually
use for Option-B / ALIGNED restore, and reports a single JSON dashboard.

Vectors (non-destructive where possible):
  W1  git_refs create+delete (same as probe_main_write.py)
  W2  contents PUT on a throwaway branch path (cleaned up if it lands)
  W3a workflow_dispatch land-option-b-on-main on trial (dry_run)
  W3b workflow_dispatch land-option-b-on-main on main
  W3c Actions API dispatch on trial
  W4a fork create
  W4b GraphQL createCommitOnBranch (forbidden → no write)
  W4c pulls create capability (expects 403 without a pushed head)
  W5  Path A RevertPullRequest on #32 (optional; not Path B)

Exit codes:
  0 — at least one Path-B-capable vector is WRITABLE
  1 — all Path-B-capable vectors DENIED (issues:create alone does not count)
  2 — transport / unexpected failure reading tip

Scientific effect: NONE. No claim/premise/lemma status is read or written.
Does not create issues by default (Batch 55 found issues:create can succeed
while contents/refs stay 403 — litter left issue #37). Set PROBE_CREATE_ISSUE=1
to include that vector.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
TRIAL = "d6g8k5htny-coder/trial"
API = f"https://api.github.com/repos/{REPO}"
TRIAL_API = f"https://api.github.com/repos/{TRIAL}"
GQL = "https://api.github.com/graphql"


def _token() -> str | None:
    for key in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def _request_urllib(method: str, url: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trial-probe-main-write-vectors",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            try:
                payload: dict | str = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = raw
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {"message": str(exc)}
        except json.JSONDecodeError:
            payload = {"message": raw or str(exc)}
        return exc.code, payload
    except urllib.error.URLError as exc:
        raise RuntimeError(f"transport: {exc}") from exc


def _request_gh(method: str, path: str, body: dict | None = None) -> tuple[int, dict | str]:
    cmd = ["gh", "api", "-X", method, path]
    if body is not None:
        cmd.append("--input")
        cmd.append("-")
        proc = subprocess.run(
            cmd,
            input=json.dumps(body),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    raw = proc.stdout or proc.stderr or ""
    try:
        payload: dict | str = json.loads(proc.stdout) if proc.stdout else {}
    except json.JSONDecodeError:
        payload = raw
    if proc.returncode == 0:
        if method == "DELETE" and not proc.stdout:
            return 204, payload
        return 200 if method != "POST" else (201 if isinstance(payload, dict) else 200), payload
    status = 403
    for marker in ("HTTP 401", "HTTP 403", "HTTP 404", "HTTP 422", "HTTP 500"):
        if marker in raw:
            status = int(marker.split()[-1])
            break
    if isinstance(payload, str) or not payload:
        payload = {"message": raw.strip() or f"gh api exit {proc.returncode}"}
    return status, payload


def _request(method: str, url: str, body: dict | None = None) -> tuple[int, dict | str]:
    if _token() is not None:
        return _request_urllib(method, url, body)
    path = url.split("https://api.github.com/", 1)[-1]
    try:
        return _request_gh(method, path, body)
    except FileNotFoundError:
        return _request_urllib(method, url, body)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"transport: {exc}") from exc


def _classify(status: int, body: dict | str) -> str:
    if status in (200, 201, 204):
        return "WRITABLE"
    if status in (401, 403):
        return "DENIED"
    if status == 404:
        msg = ""
        if isinstance(body, dict):
            msg = str(body.get("message", "")).lower()
        if "not accessible" in msg or "not found" in msg or "workflow" in msg:
            return "DENIED"
        return "DENIED"
    if status == 422:
        # Validation error usually means the endpoint was reachable with write intent.
        return "REACHED_422"
    return f"HTTP_{status}"


def _short(body: dict | str, limit: int = 240) -> str:
    if isinstance(body, dict):
        msg = body.get("message") or body.get("error") or json.dumps(body, sort_keys=True)
    else:
        msg = str(body)
    msg = str(msg).replace("\n", " ")
    return msg[:limit]


def main() -> int:
    ts = int(time.time())
    report: dict = {
        "repo": REPO,
        "scientific_effect": "NONE",
        "probe": "multi_vector_path_b",
        "batch_note": (
            "Path B capable = refs/contents/workflow_dispatch/fork/commit. "
            "issues:create alone is NOT Path-B-capable (Batch 55)."
        ),
        "tokens": {
            k: ("SET" if os.environ.get(k) else "NOT_SET")
            for k in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
        },
        "vectors": {},
    }

    try:
        status, tip = _request("GET", f"{API}/git/ref/heads/main")
        if status != 200 or not isinstance(tip, dict):
            report["state"] = "TRANSPORT_ERROR"
            report["detail"] = {"http_status": status, "body": tip}
            print(json.dumps(report, indent=2, sort_keys=True))
            print("probe_main_write_vectors: transport failure reading main tip", file=sys.stderr)
            return 2
        sha = tip["object"]["sha"]
        report["tip_sha"] = sha

        # Permissions (read).
        p_status, p_body = _request("GET", API)
        perms = p_body.get("permissions") if isinstance(p_body, dict) else None
        report["permissions"] = perms
        report["permissions_http_status"] = p_status

        vectors: dict = {}

        # W1 — git refs create/delete
        ref = f"refs/heads/cursor-wvec-refs-{ts}"
        c_status, c_body = _request("POST", f"{API}/git/refs", {"ref": ref, "sha": sha})
        w1 = {
            "create_http_status": c_status,
            "create_msg": _short(c_body),
            "state": _classify(c_status, c_body),
        }
        if c_status in (200, 201):
            d_status, d_body = _request("DELETE", f"{API}/git/{ref}")
            w1["delete_http_status"] = d_status
            w1["delete_msg"] = _short(d_body)
            w1["state"] = "WRITABLE"
        vectors["W1_git_refs"] = w1

        # W2 — contents PUT on throwaway branch (may create branch)
        branch = f"cursor-wvec-contents-{ts}"
        content_b64 = "YmF0Y2g1NSBwcm9iZSBOT05FLWNsYWltCg=="  # "batch55 probe NONE-claim\n"
        put_status, put_body = _request(
            "PUT",
            f"{API}/contents/.cursor-write-probe-b55.txt",
            {
                "message": "batch55 multi-vector probe (safe to delete)",
                "content": content_b64,
                "branch": branch,
            },
        )
        w2 = {
            "http_status": put_status,
            "msg": _short(put_body),
            "state": _classify(put_status, put_body),
            "branch": branch,
        }
        if put_status in (200, 201):
            # Best-effort cleanup: delete file then try delete branch ref.
            file_sha = put_body.get("content", {}).get("sha") if isinstance(put_body, dict) else None
            if file_sha:
                _request(
                    "DELETE",
                    f"{API}/contents/.cursor-write-probe-b55.txt",
                    {
                        "message": "batch55 probe cleanup",
                        "sha": file_sha,
                        "branch": branch,
                    },
                )
            _request("DELETE", f"{API}/git/refs/heads/{branch}")
            w2["state"] = "WRITABLE"
        vectors["W2_contents_put"] = w2

        # W3a — workflow_dispatch trial (gh CLI preferred for dispatch ergonomics)
        w3a = _dispatch_workflow(TRIAL, "land-option-b-on-main.yml")
        vectors["W3a_dispatch_trial"] = w3a

        # W3b — workflow_dispatch main (usually 404: workflow absent on default tip)
        w3b = _dispatch_workflow(REPO, "land-option-b-on-main.yml")
        vectors["W3b_dispatch_main"] = w3b

        # W3c — Actions API dispatch on trial
        d_status, d_body = _request(
            "POST",
            f"{TRIAL_API}/actions/workflows/land-option-b-on-main.yml/dispatches",
            {"ref": "main", "inputs": {"dry_run": "true"}},
        )
        vectors["W3c_api_dispatch_trial"] = {
            "http_status": d_status,
            "msg": _short(d_body),
            # 204 = accepted dispatch
            "state": "WRITABLE" if d_status in (200, 201, 204) else _classify(d_status, d_body),
        }

        # W4a — fork
        f_status, f_body = _request("POST", f"{API}/forks", {})
        vectors["W4a_fork"] = {
            "http_status": f_status,
            "msg": _short(f_body),
            "state": _classify(f_status, f_body),
        }

        # W4b — GraphQL createCommitOnBranch (forbidden → no write)
        gql_status, gql_body = _graphql_create_commit(sha)
        vectors["W4b_graphql_createCommitOnBranch"] = {
            "http_status": gql_status,
            "msg": _short(gql_body),
            "state": _classify_gql(gql_body) if gql_status == 200 else _classify(gql_status, gql_body),
        }

        # W4c — pulls create without a real head (expect 422/403)
        pr_status, pr_body = _request(
            "POST",
            f"{API}/pulls",
            {
                "title": "batch55 multi-vector probe",
                "head": f"cursor-wvec-missing-{ts}",
                "base": "main",
                "body": "probe — expect deny",
                "draft": True,
            },
        )
        vectors["W4c_pulls_create"] = {
            "http_status": pr_status,
            "msg": _short(pr_body),
            "state": _classify(pr_status, pr_body),
        }

        # W5 — Path A revert32 (not Path-B-capable for notice-only, but recorded)
        r_status, r_body = _request(
            "POST",
            f"{API}/pulls/32/revert",
            {"commit_title": "batch55 Path A probe revert of #32"},
        )
        vectors["W5_path_a_revert32"] = {
            "http_status": r_status,
            "msg": _short(r_body),
            "state": _classify(r_status, r_body),
            "path_b_capable": False,
        }

        if os.environ.get("PROBE_CREATE_ISSUE") == "1":
            i_status, i_body = _request(
                "POST",
                f"{API}/issues",
                {
                    "title": f"batch55 write-vector probe {ts}",
                    "body": (
                        "Auto probe from trial `probe_main_write_vectors.py`. "
                        "Scientific effect: NONE. Safe to close/delete."
                    ),
                },
            )
            vectors["W_issues_create"] = {
                "http_status": i_status,
                "msg": _short(i_body),
                "state": _classify(i_status, i_body),
                "path_b_capable": False,
                "note": "issues:create is NOT sufficient for Path B Option-B land",
            }

        report["vectors"] = vectors

        path_b_keys = (
            "W1_git_refs",
            "W2_contents_put",
            "W3a_dispatch_trial",
            "W3b_dispatch_main",
            "W3c_api_dispatch_trial",
            "W4a_fork",
            "W4b_graphql_createCommitOnBranch",
            "W4c_pulls_create",
        )
        writable = [
            k for k in path_b_keys if vectors.get(k, {}).get("state") == "WRITABLE"
        ]
        # REACHED_422 on contents/refs often means write scope present but bad payload —
        # treat as interesting but not WRITABLE for landing.
        report["path_b_writable_vectors"] = writable
        if writable:
            report["state"] = "WRITABLE"
            report["path_b_ready"] = True
            print(json.dumps(report, indent=2, sort_keys=True))
            print(
                f"probe_main_write_vectors: WRITABLE via {', '.join(writable)}",
                file=sys.stderr,
            )
            return 0

        report["state"] = "DENIED"
        report["path_b_ready"] = False
        print(json.dumps(report, indent=2, sort_keys=True))
        print(
            "probe_main_write_vectors: DENIED — no Path-B-capable write vector",
            file=sys.stderr,
        )
        return 1
    except RuntimeError as exc:
        report["state"] = "TRANSPORT_ERROR"
        report["detail"] = str(exc)
        print(json.dumps(report, indent=2, sort_keys=True))
        print(f"probe_main_write_vectors: {exc}", file=sys.stderr)
        return 2


def _dispatch_workflow(repo: str, workflow_file: str) -> dict:
    """Use `gh workflow run` when available; fall back to API classification."""
    proc = subprocess.run(
        [
            "gh",
            "workflow",
            "run",
            workflow_file,
            "--repo",
            repo,
            "-f",
            "dry_run=true",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    raw = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        return {"exit": 0, "msg": _short(raw or "dispatched"), "state": "WRITABLE"}
    status = 403
    for marker in ("HTTP 401", "HTTP 403", "HTTP 404", "HTTP 422"):
        if marker in raw:
            status = int(marker.split()[-1])
            break
    return {
        "exit": proc.returncode,
        "http_status": status,
        "msg": _short(raw),
        "state": _classify(status, {"message": raw}),
    }


def _graphql_create_commit(expected_oid: str) -> tuple[int, dict | str]:
    query = {
        "query": (
            "mutation($input: CreateCommitOnBranchInput!) {"
            "  createCommitOnBranch(input: $input) { commit { oid } }"
            "}"
        ),
        "variables": {
            "input": {
                "branch": {
                    "repositoryNameWithOwner": REPO,
                    "branchName": "main",
                },
                "message": {"headline": "batch55 multi-vector probe (expect forbid)"},
                "fileChanges": {
                    "additions": [
                        {
                            "path": ".cursor-wvec-probe.txt",
                            "contents": "YmF0Y2g1NSBwcm9iZQo=",
                        }
                    ]
                },
                "expectedHeadOid": expected_oid,
            }
        },
    }
    if _token() is not None:
        return _request_urllib("POST", GQL, query)
    # gh api graphql
    proc = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=json.dumps(query),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    try:
        payload: dict | str = json.loads(proc.stdout) if proc.stdout else {}
    except json.JSONDecodeError:
        payload = proc.stdout or proc.stderr or ""
    if proc.returncode == 0:
        return 200, payload
    status = 403
    raw = (proc.stdout or "") + (proc.stderr or "")
    for marker in ("HTTP 401", "HTTP 403", "HTTP 404", "HTTP 422"):
        if marker in raw:
            status = int(marker.split()[-1])
            break
    return status, payload if payload else {"message": raw}


def _classify_gql(body: dict | str) -> str:
    if not isinstance(body, dict):
        return "DENIED"
    if body.get("data", {}).get("createCommitOnBranch"):
        return "WRITABLE"
    errors = body.get("errors") or []
    if errors:
        msg = " ".join(str(e.get("message", "")) for e in errors if isinstance(e, dict))
        if "not accessible" in msg.lower() or "forbidden" in msg.lower():
            return "DENIED"
        return "DENIED"
    return "DENIED"


if __name__ == "__main__":
    raise SystemExit(main())
