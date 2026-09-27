#!/usr/bin/env python3
"""Terminal gate for an automation pulse that has nothing to commit.

Call this before any tracked-file write. When release-critical source identity
and recorded capabilities are unchanged and no substantive defect is present,
the process prints ``action=idle_no_commit`` and exits 0. The caller returns
immediately. Pulse-only stamps are not source identity and are not a reason to
write:

- ``print_owner_unblock.sh`` batch header and history echoes
- ``REFRESH_BATCH_TAG`` default in ``refresh_path_c_bundle.sh``
- last-resort ``return "N"`` fallbacks in the inventory and wake helpers
- ``VERIFY.refresh_batch`` and ``VERIFY.generated_at_utc``

A real source change, a capability change, or an explicit substantive defect
exits 1 so the repair can proceed. This gate does not write tracked files,
does not alter schedules, and does not change the release content-hash
detector (that detector still compares raw critical-script bytes).

Scientific effect: NONE. Never flips lemma_closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]

# Files whose pulse stamps were rewritten by idle batches and then flagged
# script_stale by the raw content-hash detector.
SOURCE_FILES = (
    "scripts/refresh_path_c_bundle.sh",
    "scripts/refresh_ai_agent_access_inventory.py",
    "scripts/post_batch322_wake_comments.py",
    "scripts/print_owner_unblock.sh",
    "portable/path-c-applied-bundle/VERIFY.json",
    "portable/patches/BASE_TIP.txt",
)
INVENTORY = "portable/AI_AGENT_ACCESS_INVENTORY.json"

_PULSE_COMMENT = re.compile(
    r"(?m)^[ \t]*# Batch \d+: last-resort bumped[^\n]*\n?"
)
_FALLBACK_RETURN = re.compile(r'(?m)^[ \t]*return "\d+"\s*$')
_REFRESH_DEFAULT = re.compile(r"REFRESH_BATCH_TAG:-\d+")
_HEADER = re.compile(r"=== Batch \d+")
_ECHO_PULSE = re.compile(r'(?m)^echo " +Batch \d+:[^\n]*\n?')
_VERIFY_REFRESH = re.compile(r'("refresh_batch"\s*:\s*)\d+')
_VERIFY_GENERATED = re.compile(
    r'("generated_at_utc"\s*:\s*")[^"]*(")'
)

_NON_DEFECTS = {
    "",
    "none",
    "no defect",
    "no_defect",
    "hunt negative",
    "hunt_negative",
    "idle",
    "idle_no_commit",
}


def normalize_source(rel: str, text: str) -> str:
    """Drop pulse stamps so identity is the remaining source."""
    name = Path(rel).name
    if name == "refresh_path_c_bundle.sh":
        return _REFRESH_DEFAULT.sub("REFRESH_BATCH_TAG:-0", text)
    if name in {
        "refresh_ai_agent_access_inventory.py",
        "post_batch322_wake_comments.py",
    }:
        text = _PULSE_COMMENT.sub("", text)
        matches = list(_FALLBACK_RETURN.finditer(text))
        if matches:
            last = matches[-1]
            text = text[: last.start()] + 'return "0"' + text[last.end() :]
        return text
    if name == "print_owner_unblock.sh":
        text = _HEADER.sub("=== Batch 0", text, count=1)
        text = _ECHO_PULSE.sub("", text)
        return text.rstrip() + "\n"
    if name == "VERIFY.json":
        text = _VERIFY_REFRESH.sub(r"\g<1>0", text)
        return _VERIFY_GENERATED.sub(r"\g<1>0\2", text)
    return text


def source_identity(files: Mapping[str, str]) -> str:
    digest = hashlib.sha256()
    for rel in sorted(files):
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(normalize_source(rel, files[rel]).encode())
        digest.update(b"\0")
    return digest.hexdigest()


def substantive_defect(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if text.lower() in _NON_DEFECTS:
        return None
    return text


def capability_fingerprint(inventory: Mapping[str, object]) -> dict:
    """Permissions and coverage. Pulse timestamps, batch, and tip shas are omitted."""
    details = []
    raw_details = inventory.get("details") or []
    if isinstance(raw_details, list):
        for row in raw_details:
            if not isinstance(row, dict):
                continue
            details.append(
                {
                    "name": row.get("name"),
                    "push": row.get("push"),
                    "admin": row.get("admin"),
                    "write": row.get("write"),
                    "has_agents": row.get("has_agents"),
                    "default_branch": row.get("default_branch"),
                }
            )
    details.sort(key=lambda row: str(row.get("name") or ""))
    sandbox = inventory.get("sandbox")
    sandbox = sandbox if isinstance(sandbox, dict) else {}
    return {
        "durable_sibling_coverage": inventory.get("durable_sibling_coverage"),
        "durable_writable": inventory.get("durable_writable"),
        "main_writable": inventory.get("main_writable"),
        "sibling_write_count": inventory.get("sibling_write_count"),
        "sandbox": {
            "readable": sandbox.get("readable"),
            "write": sandbox.get("write"),
            "has_agents": sandbox.get("has_agents"),
        },
        "details": details,
    }


def _fingerprint_sha(fingerprint: Mapping[str, object]) -> str:
    payload = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def decide(
    *,
    current_files: Mapping[str, str],
    baseline_files: Mapping[str, str],
    current_inventory: Mapping[str, object],
    baseline_inventory: Mapping[str, object],
    defect: str | None = None,
) -> dict:
    """Return the pulse decision. This function does not write files."""
    missing = sorted(
        rel
        for rel in SOURCE_FILES
        if rel not in current_files or rel not in baseline_files
    )
    # Identity is compared on the shared source set. A missing baseline or
    # current file is a real difference.
    identity_keys = [rel for rel in SOURCE_FILES if rel in current_files or rel in baseline_files]
    current_src = {rel: current_files.get(rel, "") for rel in identity_keys}
    baseline_src = {rel: baseline_files.get(rel, "") for rel in identity_keys}
    present = all(rel in current_files and rel in baseline_files for rel in SOURCE_FILES)
    identity_unchanged = present and source_identity(current_src) == source_identity(
        baseline_src
    )
    current_cap = capability_fingerprint(current_inventory)
    baseline_cap = capability_fingerprint(baseline_inventory)
    capabilities_unchanged = current_cap == baseline_cap
    defect_text = substantive_defect(defect)
    reasons: list[str] = []
    if not identity_unchanged:
        reasons.append("source_identity")
    if not capabilities_unchanged:
        reasons.append("capabilities")
    if defect_text:
        reasons.append("defect")
    idle = not reasons
    if idle:
        action = "idle_no_commit"
    elif defect_text and identity_unchanged and capabilities_unchanged:
        action = "substantive_defect"
    elif not identity_unchanged and capabilities_unchanged and not defect_text:
        action = "substantive_source_change"
    elif identity_unchanged and not capabilities_unchanged and not defect_text:
        action = "substantive_capability_change"
    else:
        action = "substantive_work"
    return {
        "action": action,
        "write_tracked_files": not idle,
        "source_identity_unchanged": identity_unchanged,
        "capabilities_unchanged": capabilities_unchanged,
        "substantive_defect": defect_text,
        "reasons": reasons,
        "source_identity": source_identity(current_src),
        "capability_fingerprint": _fingerprint_sha(current_cap),
        "lemma_closed": False,
        "flipped_anything": False,
        "scientific_effect": "NONE",
        "missing_sources": missing,
    }


def _git_show(root: Path, rel: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"HEAD:{rel}"],
        cwd=root,
        text=True,
    )


def evaluate(root: Path, defect: str | None = None) -> dict:
    """Compare the worktree to HEAD. Does not write tracked files."""
    current_files = {
        rel: (root / rel).read_text(encoding="utf-8") for rel in SOURCE_FILES
    }
    baseline_files = {rel: _git_show(root, rel) for rel in SOURCE_FILES}
    current_inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    baseline_inventory = json.loads(_git_show(root, INVENTORY))
    report = decide(
        current_files=current_files,
        baseline_files=baseline_files,
        current_inventory=current_inventory,
        baseline_inventory=baseline_inventory,
        defect=defect,
    )
    report["baseline"] = "HEAD"
    return report


def _report_line(report: dict) -> str:
    if report.get("action") == "idle_no_commit":
        return (
            "idle_no_commit: source identity and capabilities unchanged; "
            "no substantive defect; return before tracked-file writes"
        )
    reasons = ",".join(report.get("reasons") or []) or "unspecified"
    return f"{report.get('action')}: {reasons}; tracked-file writes allowed"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="trial checkout (default: repository root)",
    )
    parser.add_argument(
        "--defect",
        default=None,
        help="substantive defect id from the hunt; empty and hunt-negative are idle",
    )
    args = parser.parse_args(argv)
    try:
        report = evaluate(args.root, defect=args.defect)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"idle_no_commit: evaluate failed: {exc}", file=sys.stderr)
        return 2
    print(_report_line(report), file=sys.stderr)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report.get("action") == "idle_no_commit":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
