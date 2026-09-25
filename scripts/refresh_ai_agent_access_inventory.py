#!/usr/bin/env python3
"""Refresh portable/AI_AGENT_ACCESS_INVENTORY.json tip_sha / pushed_at / write.

Batch 323: owner_grant --check used to only *print* a pointer to the inventory
while tip_sha drifted (and sandbox.tip disagreed with details tip_sha). This
writer updates tips from live gh API under the caller's token env.

Batch 328: INV_BATCH default no longer freezes at \"323\" — derive from
print_owner_unblock.sh header (=== Batch N ===) so tip refreshes stamp the
living automation batch. Env INV_BATCH still overrides.

Batch 329: when durable probe is skipped (no_token / DURABLE_SANDBOX_WRITE=n/a),
tip-refresh only — do **not** clobber durable push/admin/perm, sandbox.readable,
or durable_sibling_coverage 8/8 with ambient App/ghs pull-only permissions.
False no_token grant-audit branches are not an eng fix. lemma_closed stays false.

Scientific effect: NONE. Never flips lemma_closed / flipped_anything.
Never prints tokens.

Batch 329: refresh() None-batch fallback also derives living header (no freeze at 328).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def _living_inventory_batch(root: str) -> str:
    """Prefer print_owner header Batch N; else prior inventory batch; else 328."""
    unblock = os.path.join(root, "scripts", "print_owner_unblock.sh")
    try:
        text = open(unblock, encoding="utf-8").read()
    except OSError:
        text = ""
    m = re.search(r"=== Batch (\d+)\s", text)
    if m:
        return m.group(1)
    inv_path = os.path.join(root, "portable", "AI_AGENT_ACCESS_INVENTORY.json")
    try:
        prev = json.load(open(inv_path, encoding="utf-8"))
        b = str(prev.get("batch") or "").strip()
        if b.isdigit():
            return b
    except (OSError, json.JSONDecodeError):
        pass
    return "328"


def _no_durable_probe(
    durable_writable: int,
    durable_sandbox_read: str,
    durable_sandbox_write: str,
) -> bool:
    """True when --check skipped durable vector (no MAIN_PUSH_TOKEN in pod)."""
    if os.environ.get("PRESERVE_DURABLE", "").strip() in ("1", "true", "yes"):
        return True
    if str(durable_sandbox_write) in ("n/a",):
        return True
    if durable_writable == 0 and str(durable_sandbox_read) in ("n/a", "?", ""):
        return True
    return False


def _gh_json(args: list[str]) -> Any:
    try:
        out = subprocess.check_output(
            ["gh", "api", *args],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=60,
        )
        return json.loads(out)
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return None


def _tip_sha(repo: str) -> str:
    d = _gh_json([f"/repos/{repo}/git/ref/heads/main"])
    if isinstance(d, dict):
        sha = (d.get("object") or {}).get("sha") or ""
        if isinstance(sha, str) and len(sha) >= 7:
            return sha
    meta = _gh_json([f"/repos/{repo}"])
    if not isinstance(meta, dict):
        return ""
    branch = meta.get("default_branch") or "main"
    d = _gh_json([f"/repos/{repo}/git/ref/heads/{branch}"])
    if isinstance(d, dict):
        sha = (d.get("object") or {}).get("sha") or ""
        if isinstance(sha, str) and len(sha) >= 7:
            return sha
    return ""


def refresh(
    inv_path: str,
    repos: list[str],
    *,
    owner: str = "d6g8k5htny-coder",
    durable_writable: int = 0,
    durable_sandbox_read: str = "?",
    durable_sandbox_write: str = "DENIED",
    active_sandbox_read: str = "?",
    batch: str | None = None,
) -> dict[str, Any]:
    with open(inv_path, encoding="utf-8") as f:
        inv = json.load(f)

    inv["lemma_closed"] = False
    inv["flipped_anything"] = False
    inv["scientific_effect"] = "NONE"
    inv["generated_at_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    if batch is None:
        # Batch 329: do not freeze at 328 — derive like main() / INV_BATCH path.
        root = str(Path(inv_path).resolve().parents[1])
        batch = _living_inventory_batch(root)
    inv["batch"] = str(batch)
    inv["token_printed"] = False
    inv["multi_agent_script"] = "scripts/owner_grant_ai_agent_access.sh"
    inv["script"] = "scripts/owner_grant_ai_agent_access.sh"

    preserve_durable = _no_durable_probe(
        durable_writable, durable_sandbox_read, durable_sandbox_write
    )

    if not preserve_durable:
        if repos and durable_writable == len(repos):
            inv["durable_sibling_coverage"] = "8/8_WRITABLE"
            inv["sibling_write_count"] = durable_writable
            inv["durable_writable"] = f"{durable_writable}/{len(repos)}"
        elif repos and durable_writable:
            inv["durable_sibling_coverage"] = f"{durable_writable}/{len(repos)}"
            inv["sibling_write_count"] = durable_writable
            inv["durable_writable"] = f"{durable_writable}/{len(repos)}"
    else:
        # Keep prior durable 8/8 attribution; ambient App token ≠ durable loss.
        if inv.get("durable_sibling_coverage") in (None, "", "no_token"):
            if int(inv.get("sibling_write_count") or 0) == 8 or inv.get(
                "durable_writable"
            ) in ("8/8", "8/8_WRITABLE"):
                inv["durable_sibling_coverage"] = "8/8_WRITABLE"

    by_name = {
        d.get("name"): d for d in (inv.get("details") or []) if isinstance(d, dict)
    }
    connected: list[dict[str, str]] = []
    details_out: list[dict[str, Any]] = []
    updated = 0

    for repo in repos:
        meta = _gh_json([f"/repos/{repo}"]) or {}
        tip = _tip_sha(repo)
        prev = by_name.get(repo) or {}
        write = prev.get("write", "DENIED")
        if not preserve_durable:
            if tip and durable_writable == len(repos):
                write = "WRITABLE"
            elif tip and repo.endswith("/sandbox"):
                if durable_sandbox_write in ("WRITABLE", "DENIED"):
                    write = durable_sandbox_write
        perms = meta.get("permissions") if isinstance(meta.get("permissions"), dict) else {}
        if preserve_durable:
            # Ambient ghs is often pull-only on siblings; do not demote durable.
            push = bool(prev.get("push", True))
            admin = bool(prev.get("admin", True))
        else:
            push = bool(perms.get("push", prev.get("push", True)))
            admin = bool(perms.get("admin", prev.get("admin", True)))
        row = {
            "name": repo,
            "push": push,
            "admin": admin,
            "default_branch": meta.get("default_branch")
            or prev.get("default_branch")
            or "main",
            "pushed_at": meta.get("pushed_at") or prev.get("pushed_at"),
            "tip_sha": tip or prev.get("tip_sha") or "",
            "has_agents": prev.get("has_agents", True),
            "write": write,
        }
        if tip and tip != prev.get("tip_sha"):
            updated += 1
        details_out.append(row)
        connected.append({"name": repo, "perm": "push" if row["push"] else "pull"})

        if repo == f"{owner}/sandbox":
            prev_sb = inv.get("sandbox") if isinstance(inv.get("sandbox"), dict) else {}
            if preserve_durable:
                inv["sandbox"] = {
                    "readable": bool(prev_sb.get("readable", True)),
                    "write": prev_sb.get("write")
                    if prev_sb.get("write") in ("WRITABLE", "DENIED")
                    else row["write"],
                    "has_agents": True,
                    "tip": (tip or row["tip_sha"] or "")[:7],
                    "app_read_http": int(active_sandbox_read)
                    if str(active_sandbox_read).isdigit()
                    else prev_sb.get("app_read_http", 404),
                    "durable_read_http": prev_sb.get("durable_read_http", 200),
                    "main_push_token_secret": True,
                }
            else:
                inv["sandbox"] = {
                    "readable": str(durable_sandbox_read) not in ("404", "n/a", "?", ""),
                    "write": durable_sandbox_write
                    if durable_sandbox_write in ("WRITABLE", "DENIED")
                    else row["write"],
                    "has_agents": True,
                    "tip": (tip or row["tip_sha"] or "")[:7],
                    "app_read_http": int(active_sandbox_read)
                    if str(active_sandbox_read).isdigit()
                    else prev_sb.get("app_read_http", 404),
                    "durable_read_http": int(durable_sandbox_read)
                    if str(durable_sandbox_read).isdigit()
                    else prev_sb.get("durable_read_http", 200),
                    "main_push_token_secret": True,
                }
        if repo == f"{owner}/main":
            if preserve_durable:
                inv["main_writable"] = bool(
                    inv.get("main_writable", row["write"] == "WRITABLE")
                )
            else:
                inv["main_writable"] = row["write"] == "WRITABLE"

    inv["details"] = details_out
    inv["repos_connected"] = connected
    inv["repos_count"] = len(details_out)

    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2)
        f.write("\n")

    return {
        "tip_updates": updated,
        "lemma_closed": False,
        "path": inv_path,
        "preserve_durable": preserve_durable,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    inv_path = os.environ.get(
        "INV_PATH", os.path.join(root, "portable", "AI_AGENT_ACCESS_INVENTORY.json")
    )
    owner = os.environ.get("OWNER", "d6g8k5htny-coder")
    repos_csv = os.environ.get("REPOS_CSV", "")
    repos = [r for r in repos_csv.split(",") if r]
    if not repos:
        # Fall back to environment.json repositoryDependencies (JSONC).
        env_path = os.path.join(root, ".cursor", "environment.json")
        try:
            raw = open(env_path, encoding="utf-8").read()
            lines = [
                ln for ln in raw.splitlines() if not ln.lstrip().startswith("//")
            ]
            text = re.sub(r",\s*([}\]])", r"\1", "\n".join(lines))
            env = json.loads(text)
            deps = list(env.get("repositoryDependencies") or [])
            repos = []
            for d in deps:
                d = str(d).strip().rstrip("/")
                if d.startswith("github.com/"):
                    d = d[len("github.com/") :]
                if "/" not in d:
                    d = f"{owner}/{d}"
                repos.append(d)
        except (OSError, json.JSONDecodeError):
            repos = []
    if not os.path.isfile(inv_path):
        print(f"inventory_refresh=skip missing={inv_path}", file=sys.stderr)
        return 0
    try:
        result = refresh(
            inv_path,
            repos,
            owner=owner,
            durable_writable=int(os.environ.get("DURABLE_WRITABLE") or 0),
            durable_sandbox_read=os.environ.get("DURABLE_SANDBOX_READ") or "?",
            durable_sandbox_write=os.environ.get("DURABLE_SANDBOX_WRITE") or "DENIED",
            active_sandbox_read=os.environ.get("ACTIVE_SANDBOX_READ") or "?",
            batch=os.environ.get("INV_BATCH") or _living_inventory_batch(root),
        )
    except (OSError, json.JSONDecodeError) as e:
        print(f"inventory_refresh=skip err={e}", file=sys.stderr)
        return 0
    print(
        "inventory_refresh=ok "
        f"path=portable/AI_AGENT_ACCESS_INVENTORY.json "
        f"tip_updates={result['tip_updates']} "
        f"preserve_durable={str(result.get('preserve_durable', False)).lower()} "
        f"lemma_closed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
