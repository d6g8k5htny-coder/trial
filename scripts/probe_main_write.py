#!/usr/bin/env python3
"""Probe whether the current credential can write to d6g8k5htny-coder/main.

Creates (or attempts to create) a unique throwaway ref via the Git Data API,
then deletes it on success. Never touches default ``main`` contents.

Also queries ``GET /installation/repositories`` and reports ``install_has_main``
(true when ``d6g8k5htny-coder/main`` is in the App installation selection).

Batch 287 — ``repositories`` must be a list: ``null`` / non-list used to
collapse via ``or []`` into a false empty install selection (same class of
bug Batch 286 fixed in grant ``--check``). Now reports
``install_query_mode=repositories_unavailable`` instead.

Batch 262 — token resolution order (never printed):
  1. env MAIN_PUSH_TOKEN / GH_TOKEN / GITHUB_TOKEN
  2. durable files: /cursor/stores/self/MAIN_PUSH_TOKEN,
     /workspace/.secrets/MAIN_PUSH_TOKEN, /tmp/gh-dylan-auth/access_token
  3. else ``gh`` host login (App/ghs) via ``gh api``
Set ``PATH_C_IGNORE_FILE_TOKENS=1`` to skip file discovery (tests / App-only).

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
import uuid
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
MAIN_FULL = "d6g8k5htny-coder/main"
API = f"https://api.github.com/repos/{REPO}"
INSTALL_REPOS_URL = "https://api.github.com/installation/repositories"

# Batch 262: discover durable file tokens (same paths as when_writable_land).
# Without this, print_owner_unblock live probes reported DENIED under App/ghs
# while PATH_C_STATUS.write_state=WRITABLE via /tmp/gh-dylan-auth/access_token.
# Never prints token material. Respect PATH_C_IGNORE_FILE_TOKENS=1.
_TOKEN_SOURCE: str | None = None
_DEFAULT_TOKEN_FILES = (
    "/cursor/stores/self/MAIN_PUSH_TOKEN",
    "/workspace/.secrets/MAIN_PUSH_TOKEN",
    "/tmp/gh-dylan-auth/access_token",
)


def _ignore_file_tokens() -> bool:
    return (os.environ.get("PATH_C_IGNORE_FILE_TOKENS") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _token() -> str | None:
    """Return write token from env or durable file paths. Never logs the value."""
    global _TOKEN_SOURCE
    for key in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        val = (os.environ.get(key) or "").strip()
        if val:
            _TOKEN_SOURCE = f"env:{key}"
            return val
    if _ignore_file_tokens():
        _TOKEN_SOURCE = None
        return None
    for path in _DEFAULT_TOKEN_FILES:
        try:
            if not os.path.isfile(path):
                continue
            with open(path, encoding="utf-8") as fh:
                raw = fh.read().strip()
        except OSError:
            continue
        if raw:
            _TOKEN_SOURCE = f"file:{path}"
            return raw
    _TOKEN_SOURCE = None
    return None


def _token_source() -> str | None:
    """Label for JSON reports (path/env key only — never the secret)."""
    if _TOKEN_SOURCE is not None:
        return _TOKEN_SOURCE
    _token()  # populate _TOKEN_SOURCE
    return _TOKEN_SOURCE


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


def _probe_ref_name() -> str:
    """Unique throwaway ref — never reuse second-granularity timestamps alone.

    Batch 254: concurrent probes (sibling agents / when_writable + manual) that
    both used second-granularity ``cursor-write-probe-<unix_seconds>`` names
    collided in the same second → HTTP 422 "Reference already exists" was
    misreported as TRANSPORT_ERROR while write was actually WRITABLE. Use
    time_ns + pid + short uuid so names do not collide under concurrency.
    """
    return (
        f"refs/heads/cursor-write-probe-"
        f"{time.time_ns()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    )


def _create_body_already_exists(body: dict | str | None) -> bool:
    if not isinstance(body, dict):
        return False
    msg = str(body.get("message") or "").lower()
    return "already exists" in msg


def _parse_installation_repos_body(
    body: dict,
) -> tuple[list[str] | None, int | None, str | None, str | None]:
    """Parse GET /installation/repositories JSON body.

    Batch 287: require ``repositories`` to be a real list. Pre-287 used
    ``body.get("repositories") or []``, so ``null`` / non-list collapsed to an
    empty listing → ``names=[]`` + ``install_has_main=False`` (looked like an
    App with zero repos). Same class of false-empty Batch 286 fixed in
    ``owner_grant_ai_agent_access --check``. Returns
    ``(names, total, selection, error)``; ``error`` is set when the body is not
    a valid install listing (caller must not treat names=[] as authoritative).
    """
    repos = body.get("repositories") if isinstance(body, dict) else None
    if not isinstance(repos, list):
        return None, None, None, "repositories_not_list"
    names: list[str] = []
    for repo in repos:
        if isinstance(repo, dict):
            full = repo.get("full_name") or ""
            if full:
                names.append(str(full))
    total = body.get("total_count")
    selection = body.get("repository_selection")
    return (
        names,
        int(total) if isinstance(total, int) else None,
        str(selection) if selection is not None else None,
        None,
    )


def check_installation_repositories() -> dict:
    """Return install_has_main + names from GET /installation/repositories.

    Fail-soft: transport errors yield install_has_main=None with detail.

    Batch 253 — user/PAT token load must not poison this App-only endpoint:
    when MAIN_PUSH_TOKEN / device-flow user token is injected into env,
    urllib Bearer auth gets HTTP 403 on ``/installation/repositories`` and
    previously left ``install_has_main=None`` (names=[]). Fall back to
    ``gh api`` with user-token env vars stripped so the host App login can
    answer the installation selection. Never prints tokens.
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
    used_user_token = _token() is not None
    # App-only endpoint: user/PAT Bearer → 401/403. Retry via gh hosts login.
    if used_user_token and status in (401, 403):
        out["user_token_install_http_status"] = status
        out["user_token_install_denied"] = True
        out["fallback"] = "gh_api_without_user_token_env"
        import subprocess

        clean_env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")
        }
        proc = subprocess.run(
            ["gh", "api", "/installation/repositories"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env=clean_env,
        )
        raw = (proc.stdout or "").strip()
        if proc.returncode != 0:
            err = (proc.stderr or raw or f"gh exit {proc.returncode}")[-500:]
            out["fallback_error"] = err
            # Still not an installation credential — report false (not None)
            # so when_writable flip detection sees a concrete bool under
            # durable user-token write (WRITABLE) instead of None poison.
            out["install_has_main"] = False
            out["install_query_mode"] = "user_token_not_installation"
            out["body"] = body if isinstance(body, dict) else {"raw": str(body)[:500]}
            return out
        try:
            fb_body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            out["fallback_error"] = "json_decode"
            out["install_has_main"] = False
            out["install_query_mode"] = "user_token_not_installation"
            return out
        if not isinstance(fb_body, dict):
            out["install_has_main"] = False
            out["install_query_mode"] = "user_token_not_installation"
            return out
        names, total, selection, parse_err = _parse_installation_repos_body(fb_body)
        if parse_err is not None:
            # Batch 287: null/non-list ≠ empty App selection.
            out["http_status"] = 200
            out["install_has_main"] = False
            out["names"] = []
            out["install_query_mode"] = "repositories_unavailable"
            out["installation_note"] = (
                "repositories null or non-list (not an install listing)"
            )
            out["parse_error"] = parse_err
            out["body"] = fb_body
            return out
        out["http_status"] = 200
        out["total_count"] = total
        out["repository_selection"] = selection
        out["names"] = names or []
        out["install_has_main"] = MAIN_FULL in (names or [])
        out["install_query_mode"] = "gh_app_fallback_after_user_token_403"
        return out
    if status != 200 or not isinstance(body, dict):
        out["body"] = body if isinstance(body, dict) else {"raw": str(body)[:500]}
        return out
    names, total, selection, parse_err = _parse_installation_repos_body(body)
    if parse_err is not None:
        out["install_has_main"] = False
        out["names"] = []
        out["install_query_mode"] = "repositories_unavailable"
        out["installation_note"] = (
            "repositories null or non-list (not an install listing)"
        )
        out["parse_error"] = parse_err
        out["body"] = body
        return out
    out["total_count"] = total
    out["repository_selection"] = selection
    out["names"] = names or []
    out["install_has_main"] = MAIN_FULL in (names or [])
    out["install_query_mode"] = "direct"
    return out


def main() -> int:
    report: dict = {
        "repo": REPO,
        "scientific_effect": "NONE",
        "probe": "git_refs_create_delete",
    }
    # Resolve token first so reports include token_source (never the secret).
    _token()
    report["token_source"] = _token_source()
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
        report["tip_sha"] = sha

        # Batch 254: unique name + retry on 422 already-exists (collision residue).
        create_status: int | None = None
        create_body: dict | str | None = None
        name = ""
        attempts: list[dict] = []
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            name = _probe_ref_name()
            create_status, create_body = _request(
                "POST", f"{API}/git/refs", {"ref": name, "sha": sha}
            )
            attempts.append(
                {
                    "attempt": attempt,
                    "ref": name,
                    "create_http_status": create_status,
                    "already_exists": _create_body_already_exists(create_body),
                }
            )
            if create_status in (200, 201):
                break
            if create_status == 422 and _create_body_already_exists(create_body):
                # Another probe won the race on this exact name — retry unique.
                continue
            break
        report["probe_ref"] = name
        report["create_http_status"] = create_status
        report["create_body"] = create_body
        if len(attempts) > 1:
            report["create_attempts"] = attempts

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
