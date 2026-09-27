#!/usr/bin/env python3
"""Fail-closed validator for ``needs_attention/`` handoff cards.

Checks every ``needs_attention/cards/*.json`` and ``needs_attention/resolved/*.json``
against the ``needs_attention/v1`` schema described in ``needs_attention/README.md``:
required keys, status enum, unique ids, ``scientific_effect == "NONE"``, no
research-status keys, and resolution fields on resolved cards.

Scientific effect: NONE. Read-only. Exit 0 valid, 1 violations, 2 usage/IO.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "needs_attention/v1"
STATUSES_OPEN = ("OPEN", "IN_PROGRESS")
STATUSES_CLOSED = ("RESOLVED", "WITHDRAWN")
REQUIRED = (
    "schema",
    "id",
    "title",
    "status",
    "opened_at",
    "opened_by",
    "repo",
    "refs",
    "blocker",
    "ask",
    "scientific_effect",
)
FORBIDDEN_KEY_RE = re.compile(
    r"(?i)^(lemma_closed|prize.*|premise.*|claim_status|discharge.*|promot.*)$"
)
ID_RE = re.compile(r"^NA-\d{4,}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _root() -> Path:
    return Path(__file__).resolve().parent.parent


def _walk_keys(obj: object, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            if FORBIDDEN_KEY_RE.match(str(k)):
                found.append(path)
            found.extend(_walk_keys(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_walk_keys(v, f"{prefix}[{i}]"))
    return found


def validate_card(card: dict, *, resolved_dir: bool, filename: str) -> list[str]:
    errs: list[str] = []
    for key in REQUIRED:
        if key not in card:
            errs.append(f"missing key {key!r}")
    if errs:
        return errs
    if card["schema"] != SCHEMA:
        errs.append(f"schema {card['schema']!r} != {SCHEMA!r}")
    if not isinstance(card["id"], str) or not ID_RE.match(card["id"]):
        errs.append(f"bad id {card['id']!r} (expect NA-NNNN)")
    elif not filename.startswith(card["id"] + "-") and filename != card["id"] + ".json":
        errs.append(f"filename {filename!r} does not start with id {card['id']!r}")
    status = card["status"]
    if status not in STATUSES_OPEN + STATUSES_CLOSED:
        errs.append(f"bad status {status!r}")
    if resolved_dir and status not in STATUSES_CLOSED:
        errs.append(f"card under resolved/ has status {status!r}")
    if not resolved_dir and status in STATUSES_CLOSED:
        errs.append(f"card under cards/ has closed status {status!r} (git mv to resolved/)")
    if not isinstance(card["opened_at"], str) or not ISO_RE.match(card["opened_at"]):
        errs.append("opened_at must be ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    if card["scientific_effect"] != "NONE":
        errs.append("scientific_effect must be the literal 'NONE'")
    if not isinstance(card["opened_by"], dict) or "provider" not in card["opened_by"]:
        errs.append("opened_by must be an object with 'provider'")
    if not isinstance(card["refs"], dict):
        errs.append("refs must be an object")
    for text_key in ("title", "blocker", "ask"):
        if not isinstance(card[text_key], str) or not card[text_key].strip():
            errs.append(f"{text_key} must be a non-empty string")
    if status in STATUSES_CLOSED:
        if not (isinstance(card.get("resolution"), str) and card["resolution"].strip()):
            errs.append("closed card needs non-empty 'resolution'")
        if not (isinstance(card.get("resolved_at"), str) and ISO_RE.match(card["resolved_at"])):
            errs.append("closed card needs ISO-8601 'resolved_at'")
        if not card.get("resolved_by"):
            errs.append("closed card needs 'resolved_by'")
    forbidden = _walk_keys(card)
    if forbidden:
        errs.append(f"research-status keys forbidden on cards: {forbidden}")
    return errs


def check_tree(root: Path) -> tuple[int, list[str], dict]:
    base = root / "needs_attention"
    report: dict = {"schema": SCHEMA, "scientific_effect": "NONE", "cards": [], "errors": []}
    if not base.is_dir():
        report["errors"].append(f"missing directory {base}")
        return 2, report["errors"], report
    seen: dict[str, str] = {}
    problems: list[str] = []
    for sub, resolved in (("cards", False), ("resolved", True)):
        d = base / sub
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.json")):
            rel = path.relative_to(root).as_posix()
            try:
                card = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                problems.append(f"{rel}: unreadable JSON ({exc})")
                continue
            if not isinstance(card, dict):
                problems.append(f"{rel}: card must be a JSON object")
                continue
            errs = validate_card(card, resolved_dir=resolved, filename=path.name)
            cid = card.get("id")
            if isinstance(cid, str):
                if cid in seen:
                    errs.append(f"duplicate id {cid} (also {seen[cid]})")
                else:
                    seen[cid] = rel
            report["cards"].append(
                {"path": rel, "id": cid, "status": card.get("status"), "errors": errs}
            )
            problems.extend(f"{rel}: {e}" for e in errs)
    report["errors"] = problems
    report["open_count"] = sum(1 for c in report["cards"] if c["status"] in STATUSES_OPEN and not c["errors"])
    return (1 if problems else 0), problems, report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(_root()))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    code, problems, report = check_tree(Path(args.root))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for p in problems:
            print(f"needs_attention_check: {p}", file=sys.stderr)
        print(
            f"needs_attention_check: {'OK' if code == 0 else 'FAIL'} cards={len(report.get('cards', []))} "
            f"open={report.get('open_count', 0)} errors={len(problems)} scientific_effect=NONE"
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
