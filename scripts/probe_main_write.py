#!/usr/bin/env python3
"""Probe whether the current credential can write to d6g8k5htny-coder/main.

Creates (or attempts to create) a unique throwaway ref via the Git Data API,
then deletes it on success. Never touches default ``main`` contents.

Also queries ``GET /installation/repositories`` and reports ``install_has_main``
(true when ``d6g8k5htny-coder/main`` is in the App installation selection).

Exit codes (for CI / owner automation):
  0 — writable (ref create + delete succeeded)
  1 — denied (HTTP 401/403/404 resource-not-accessible)
  2 — transport / unexpected API failure

Scientific effect: NONE. No claim/premise/lemma status is read or written.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
MAIN_FULL = "d6g8k5htny-coder/main"
API = f"https://api.github.com/repos/{REPO}"
INSTALL_REPOS_URL = "https://api.github.com/installation/repositories"


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
        "User-Agent": "trial-probe-main-write",
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
            payload: dict | str
            try:
                payload = json.loads(raw) if raw else {}
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
    """Fall back to `gh api` so host-stored credentials are exercised."""
    import subprocess

    cmd = ["gh", "api", "-X", method, path]
    if body is not None:
        for key, value in body.items():
            cmd.extend(["-f", f"{key}={value}"])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    raw = proc.stdout or proc.stderr or ""
    try:
        payload: dict | str = json.loads(proc.stdout) if proc.stdout else {}
    except json.JSONDecodeError:
        payload = raw
    if proc.returncode == 0:
        return 200 if method == "DELETE" and not proc.stdout else (201 if method == "POST" else 200), payload
    # gh prints HTTP status in stderr like: gh: ... (HTTP 403)
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
    # No env token: use gh's stored login (cursor[bot] etc.) when available.
    path = url.split("https://api.github.com/", 1)[-1]
    try:
        return _request_gh(method, path, body)
    except FileNotFoundError:
        return _request_urllib(method, url, body)
    except Exception as exc:  # noqa: BLE001 — surface as transport
        raise RuntimeError(f"transport: {exc}") from exc


def check_installation_repositories() -> dict:
    """Return install_has_main + names from GET /installation/repositories.

    Fail-soft: transport errors yield install_has_main=None with detail.
    """
    out: dict = {
        "endpoint": "/installation/repositories",
        "install_has_main": None,
        "http_status": None,
        "total_count": None,
        "repository_selection": None,
        "names": [],
    }
    try:
        status, body = _request("GET", INSTALL_REPOS_URL)
    except RuntimeError as exc:
        out["error"] = str(exc)
        return out
    out["http_status"] = status
    if status != 200 or not isinstance(body, dict):
        out["body"] = body if isinstance(body, dict) else {"raw": str(body)[:500]}
        return out
    repos = body.get("repositories") or []
    names: list[str] = []
    for repo in repos:
        if isinstance(repo, dict):
            full = repo.get("full_name") or ""
            if full:
                names.append(str(full))
    out["total_count"] = body.get("total_count")
    out["repository_selection"] = body.get("repository_selection")
    out["names"] = names
    out["install_has_main"] = MAIN_FULL in names
    return out


def main() -> int:
    report: dict = {
        "repo": REPO,
        "scientific_effect": "NONE",
        "probe": "git_refs_create_delete",
    }
    # Always surface installation selection (even when write is DENIED).
    install = check_installation_repositories()
    report["installation_repositories"] = install
    report["install_has_main"] = install.get("install_has_main")
    try:
        status, tip = _request("GET", f"{API}/git/ref/heads/main")
        if status != 200 or not isinstance(tip, dict):
            report["state"] = "TRANSPORT_ERROR"
            report["detail"] = {"http_status": status, "body": tip}
            print(json.dumps(report, indent=2, sort_keys=True))
            print("probe_main_write: transport failure reading main tip", file=sys.stderr)
            return 2
        sha = tip["object"]["sha"]
        name = f"refs/heads/cursor-write-probe-{int(time.time())}"
        report["tip_sha"] = sha
        report["probe_ref"] = name

        create_status, create_body = _request(
            "POST", f"{API}/git/refs", {"ref": name, "sha": sha}
        )
        report["create_http_status"] = create_status
        report["create_body"] = create_body

        if create_status in (401, 403):
            report["state"] = "DENIED"
            print(json.dumps(report, indent=2, sort_keys=True))
            print(
                "probe_main_write: DENIED — credential cannot create refs on "
                f"{REPO} (HTTP {create_status})",
                file=sys.stderr,
            )
            return 1

        if create_status == 404 and isinstance(create_body, dict):
            # Fine-grained tokens often return 404 instead of 403 for missing scope.
            msg = str(create_body.get("message", "")).lower()
            if "not accessible" in msg or "not found" in msg:
                report["state"] = "DENIED"
                print(json.dumps(report, indent=2, sort_keys=True))
                print(
                    f"probe_main_write: DENIED — HTTP {create_status} creating ref",
                    file=sys.stderr,
                )
                return 1

        if create_status not in (200, 201):
            report["state"] = "TRANSPORT_ERROR"
            print(json.dumps(report, indent=2, sort_keys=True))
            print(
                f"probe_main_write: unexpected create status {create_status}",
                file=sys.stderr,
            )
            return 2

        # Clean up the throwaway ref.
        del_status, del_body = _request("DELETE", f"{API}/git/{name}")
        report["delete_http_status"] = del_status
        report["delete_body"] = del_body
        report["state"] = "WRITABLE"
        print(json.dumps(report, indent=2, sort_keys=True))
        if del_status not in (200, 204):
            print(
                f"probe_main_write: WRITABLE but cleanup HTTP {del_status} "
                f"— delete {name} manually",
                file=sys.stderr,
            )
        else:
            print("probe_main_write: WRITABLE", file=sys.stderr)
        return 0
    except RuntimeError as exc:
        report["state"] = "TRANSPORT_ERROR"
        report["detail"] = str(exc)
        print(json.dumps(report, indent=2, sort_keys=True))
        print(f"probe_main_write: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
