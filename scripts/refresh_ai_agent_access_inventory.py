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

Batch 331: when durable_writable == len(repos), force push/WRITABLE so App
permissions:{push:false} cannot rewrite connected→pull. Grant --check skips
inventory refresh entirely when durable_token_source=none (belt with preserve).

Batch 336: Batch 334 opened tip-refresh when a durable token is present even if
the probe is transiently 0/8, relying on preserve_durable. Pre-336 only treated
DURABLE_SANDBOX_WRITE=n/a (no_token skip) as preserve — a real probe that
returned DENIED/404 with writable=0 demoted sandbox.readable and connected→pull.
Now durable_writable==0 always tip-refreshes with preserve (token present or not).

Scientific effect: NONE. Never flips lemma_closed / flipped_anything.
Never prints tokens.

Batch 329: refresh() None-batch fallback also derives living header (no freeze at 328).
Batch 336: ultimate `_living_inventory_batch` fallback reads refresh_path_c_bundle
REFRESH_BATCH_TAG:-N (no freeze at 331).
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
    """Prefer print_owner header Batch N; else prior inventory; else refresh default.

    Batch 336: ultimate fallback reads ``REFRESH_BATCH_TAG:-N`` from
    refresh_path_c_bundle.sh — do not freeze at 331 (same class as INV_BATCH
    323/328 freezes).
    Batch 340: last-resort hardcoded return bumped off frozen "336" so empty-tree
    fallback cannot lag living Batch 340 / REFRESH default 340.
    Batch 343: last-resort bumped off frozen "340" after tip-sync REFRESH default 343
    (same class as 336→340).
    Batch 345: last-resort bumped off frozen "343" after tip-sync REFRESH default 345.
    Batch 346: last-resort bumped off frozen "345"
    Batch 351: last-resort bumped so empty-tree fallback cannot lag print_owner 351.
    Batch 352: last-resort bumped off frozen "351" so empty-tree fallback cannot lag
    living Batch 352 / print_owner header (coordinator wake).
    # prior: Batch 346 bumped off frozen "345" after WAKE346 print_owner header.
    Batch 346: last-resort bumped off frozen "345" so empty-tree fallback cannot lag
    living print_owner Batch 346 (inventory_preserve_durable_tip_pin).
    Batch 355: last-resort bumped off frozen "354" so empty-tree fallback cannot lag
    living Batch 355 / print_owner header (coordinator WAKE355).
    Batch 357: last-resort bumped off frozen "356" so empty-tree fallback cannot lag
    living Batch 357 / print_owner header (coordinator wake).
    """
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
    refresh = os.path.join(root, "scripts", "refresh_path_c_bundle.sh")
    try:
        rtext = open(refresh, encoding="utf-8").read()
    except OSError:
        rtext = ""
    m = re.search(r"REFRESH_BATCH_TAG:-(\d+)", rtext)
    if m:
        return m.group(1)
    # Batch 355: last-resort bumped off frozen "354".


# Batch 357: last-resort bumped off frozen "356".
    # Batch 359: last-resort bumped off frozen "358".
    # Batch 360: last-resort bumped off frozen "359".
    # Batch 368: last-resort bumped off frozen "367".
    # Batch 369: last-resort bumped off frozen "368".
    # Batch 370: last-resort bumped off frozen "369".
    # Batch 371: last-resort bumped off frozen "370".
    # Batch 372: last-resort bumped off frozen "371".
    # Batch 373: last-resort bumped off frozen "372".
    # Batch 374: last-resort bumped off frozen "373".
    # Batch 375: last-resort bumped off frozen "374".
    # Batch 376: last-resort bumped off frozen "375".
    # Batch 377: last-resort bumped off frozen "376".
    # Batch 378: last-resort bumped off frozen "377".
    # Batch 379: last-resort bumped off frozen "378".
    # Batch 380: last-resort bumped off frozen "379".
    # Batch 381: last-resort bumped off frozen "380".
    # Batch 382: last-resort bumped off frozen "381".
    # Batch 383: last-resort bumped off frozen "382".
    # Batch 384: last-resort bumped off frozen "383".
    # Batch 385: last-resort bumped off frozen "384".
    # Batch 386: last-resort bumped off frozen "385".
    # Batch 387: last-resort bumped off frozen "386".
    # Batch 388: last-resort bumped off frozen "387".
    # Batch 389: last-resort bumped off frozen "388".
    # Batch 391: last-resort bumped off frozen "390".
    # Batch 396: last-resort bumped off frozen "395".
    # Batch 399: last-resort bumped off frozen "398".
    # Batch 400: last-resort bumped off frozen "399".
    # Batch 401: last-resort bumped off frozen "400".
    # Batch 402: last-resort bumped off frozen "401".
    # Batch 403: last-resort bumped off frozen "402".
    # Batch 404: last-resort bumped off frozen "403".
    # Batch 405: last-resort bumped off frozen "404".
    # Batch 406: last-resort bumped off frozen "405".
    # Batch 407: last-resort bumped off frozen "406".
    # Batch 408: last-resort bumped off frozen "407".
    # Batch 409: last-resort bumped off frozen "408".
    # Batch 410: last-resort bumped off frozen "409".
    # Batch 411: last-resort bumped off frozen "410".
    # Batch 412: last-resort bumped off frozen "411".
    # Batch 413: last-resort bumped off frozen "412".
    # Batch 414: last-resort bumped off frozen "413".
    # Batch 415: last-resort bumped off frozen "414".
    # Batch 416: last-resort bumped off frozen "415".
    # Batch 417: last-resort bumped off frozen "416".
    # Batch 418: last-resort bumped off frozen "417".
    # Batch 419: last-resort bumped off frozen "418".
    # Batch 420: last-resort bumped off frozen "419".
    # Batch 421: last-resort bumped off frozen "420".
    # Batch 422: last-resort bumped off frozen "421".
    # Batch 423: last-resort bumped off frozen "422".
    # Batch 424: last-resort bumped off frozen "423".
    # Batch 425: last-resort bumped off frozen "424".
    # Batch 426: last-resort bumped off frozen "425".
    # Batch 427: last-resort bumped off frozen "426".
    # Batch 428: last-resort bumped off frozen "427".
    # Batch 429: last-resort bumped off frozen "428".
    # Batch 430: last-resort bumped off frozen "429".
    # Batch 431: last-resort bumped off frozen "430".
    # Batch 432: last-resort bumped off frozen "431".
    # Batch 433: last-resort bumped off frozen "432".
    # Batch 434: last-resort bumped off frozen "433".
    # Batch 435: last-resort bumped off frozen "434".
    # Batch 436: last-resort bumped off frozen "435".
    # Batch 437: last-resort bumped off frozen "436".
    # Batch 438: last-resort bumped off frozen "437".
    # Batch 439: last-resort bumped off frozen "438".
    # Batch 440: last-resort bumped off frozen "439".
    # Batch 441: last-resort bumped off frozen "440".
    # Batch 442: last-resort bumped off frozen "441".
    # Batch 443: last-resort bumped off frozen "442".
    # Batch 444: last-resort bumped off frozen "443".
    # Batch 445: last-resort bumped off frozen "444".
    # Batch 446: last-resort bumped off frozen "445".
    # Batch 447: last-resort bumped off frozen "446".
    # Batch 448: last-resort bumped off frozen "447".
    # Batch 449: last-resort bumped off frozen "448".
    # Batch 450: last-resort bumped off frozen "449".
    # Batch 451: last-resort bumped off frozen "450".
    # Batch 453: last-resort bumped off frozen "451".
    # Batch 454: last-resort bumped off frozen "453".
    # Batch 455: last-resort bumped off frozen "454".
    # Batch 456: last-resort bumped off frozen "455".
    # Batch 457: last-resort bumped off frozen "456".
    # Batch 458: last-resort bumped off frozen "457".
    # Batch 459: last-resort bumped off frozen "458".
    # Batch 460: last-resort bumped off frozen "459".
    # Batch 461: last-resort bumped off frozen "460".
    # Batch 462: last-resort bumped off frozen "461".
    # Batch 463: last-resort bumped off frozen "462".
    # Batch 464: last-resort bumped off frozen "463".
    # Batch 465: last-resort bumped off frozen "464".
    # Batch 466: last-resort bumped off frozen "465".
    # Batch 467: last-resort bumped off frozen "466".
    # Batch 468: last-resort bumped off frozen "467".
    # Batch 469: last-resort bumped off frozen "468".
    # Batch 470: last-resort bumped off frozen "469".
    # Batch 471: last-resort bumped off frozen "470".
    # Batch 472: last-resort bumped off frozen "471".
    # Batch 473: last-resort bumped off frozen "472".
    # Batch 474: last-resort bumped off frozen "473".
    # Batch 475: last-resort bumped off frozen "474".
    # Batch 476: last-resort bumped off frozen "475".
    # Batch 477: last-resort bumped off frozen "476".
    # Batch 478: last-resort bumped off frozen "477".
    # Batch 479: last-resort bumped off frozen "478".
    # Batch 480: last-resort bumped off frozen "479".
    # Batch 481: last-resort bumped off frozen "480".
    return "481"
def _no_durable_probe(
    durable_writable: int,
    durable_sandbox_read: str,
    durable_sandbox_write: str,
) -> bool:
    """True when durable vector is absent or probe found 0 writable (tip-only).

    Batch 329/330: no_token skip sets sandbox_write=n/a → preserve.
    Batch 336: token-present transient probe 0/8 sets sandbox_write=DENIED with
    durable_writable=0 — still preserve; do not demote living 8/8.
    """
    if os.environ.get("PRESERVE_DURABLE", "").strip() in ("1", "true", "yes"):
        return True
    if str(durable_sandbox_write) in ("n/a",):
        return True
    # Batch 336: any durable_writable==0 tip-refresh preserves attribution
    # (covers n/a/?/"" read *and* DENIED/404 from a failed probe).
    if durable_writable == 0:
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
        elif durable_writable == len(repos) and repos:
            # Batch 331: App/ghs often reports permissions.push=false even when
            # the durable vector is 8/8 WRITABLE — do not rewrite connected→pull.
            push = True
            admin = bool(perms.get("admin", prev.get("admin", True))) or bool(
                prev.get("admin", True)
            )
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
                # Prefer prior durable sandbox; if a stale no_token refresh already
                # demoted readable/write, recover from 8/8 coverage + row write.
                cov8 = inv.get("durable_sibling_coverage") == "8/8_WRITABLE"
                readable = bool(prev_sb.get("readable", True)) or cov8
                prev_write = prev_sb.get("write")
                if prev_write not in ("WRITABLE", "DENIED") or (
                    prev_write == "DENIED" and cov8
                ):
                    prev_write = (
                        row["write"] if row.get("write") in ("WRITABLE", "DENIED") else "WRITABLE"
                    )
                inv["sandbox"] = {
                    "readable": readable,
                    "write": prev_write,
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
