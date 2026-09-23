#!/usr/bin/env python3
"""Audit a *local* checkout the same way audit_main_alignment.py audits remote main.

Used by Path B dry-run (land-option-b-on-main.yml) and owner verification after
``git am`` of the Option-B format-patch. Does not touch the network.

Exit codes:
  0 — tree looks ALIGNED (q0/notice markers, no complexity-physics face)
  1 — MISALIGNED
  2 — usage / IO error

Scientific effect: NONE. No claim status is read or written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Keep in lockstep with scripts/audit_main_alignment.py
COMPLEXITY_MARKERS = (
    "Multiscale Retrodiction Complexity",
    "complexity-physics-framework",
    "δC = 0",
)
Q0_MARKERS = (
    "q0 Research Program",
    "SIDE24",
    "chatgpt/drive-github-hardening-20260919",
    "PR #2",
)


def audit_tree(root: Path) -> tuple[int, dict]:
    readme_path = root / "README.md"
    if not readme_path.is_file():
        report = {
            "root": str(root),
            "error": "README.md missing",
            "scientific_effect": "NONE",
        }
        return 2, report

    readme = readme_path.read_text(encoding="utf-8")
    root_names = {p.name for p in root.iterdir()}
    complexity_hits = [m for m in COMPLEXITY_MARKERS if m in readme]
    q0_hits = [m for m in Q0_MARKERS if m in readme]
    has_agents = "AGENTS.md" in root_names
    has_body = "body" in root_names

    report = {
        "root": str(root.resolve()),
        "root_has_body": has_body,
        "root_has_AGENTS_md": has_agents,
        "complexity_markers_present": complexity_hits,
        "q0_or_notice_markers_present": q0_hits,
        "scientific_effect": "NONE",
    }
    # Same predicate as audit_main_alignment.main
    misaligned = bool(complexity_hits) or (not q0_hits and not has_agents)
    if misaligned:
        report["state"] = "MISALIGNED"
        return 1, report
    report["state"] = "ALIGNED"
    return 0, report


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] in {"-h", "--help"}:
        print(
            "usage: audit_local_tree.py <checkout-root>\n"
            "  Exit 0=ALIGNED, 1=MISALIGNED, 2=usage/IO. Scientific effect: NONE.",
            file=sys.stderr,
        )
        return 2
    root = Path(args[0])
    if not root.is_dir():
        print(f"audit_local_tree: not a directory: {root}", file=sys.stderr)
        return 2
    try:
        code, report = audit_tree(root)
    except OSError as exc:
        print(f"audit_local_tree: IO failure: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    if code == 0:
        print(
            "audit_local_tree: OK — would satisfy remote audit_main_alignment "
            "(ALIGNED-ish).",
            file=sys.stderr,
        )
    elif code == 1:
        print(
            "audit_local_tree: MISALIGNED — Option-B / q0 notice markers missing "
            "or complexity-physics face still present.",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
