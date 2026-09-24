#!/usr/bin/env python3
"""Mechanical OPEN inventory for the q0 research stack (read-only).

Walks PACKET.json / claims/graph.json / selected registers on a *local*
checkout and lists premises, lemmas, prizes, claims, and open questions
that remain OPEN at the frozen / packet layer.

Scientific effect: NONE.
Never writes research status. Never flips lemma_closed / prizes / premises.
Exit 0 on a successful read (even when many items are OPEN).
Exit 2 on usage / missing inputs / IO errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

OPEN_FROZEN = {"OPEN", "NOT_CLOSED", "NAMED_HYPOTHESIS", "PARTIAL"}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _oq_mechanically_open(register_status: str, live_state: str) -> bool:
    rs = (register_status or "").upper()
    ls = (live_state or "").upper()
    if rs.startswith("CLOSED") and "OPEN" not in rs:
        return False
    if "TERMINAL" in ls and "OPEN" not in ls and "NONTERMINAL" not in ls:
        # terminal closed rows stay closed unless register says OPEN
        if not rs.startswith("OPEN"):
            return False
    if rs.startswith("OPEN") or rs == "OPEN":
        return True
    if ls.startswith("OPEN") or ls == "OPEN" or " OPEN" in f" {ls}":
        return True
    if rs.startswith("HOLD") or rs.startswith("REBASED"):
        return True
    return False


def audit_checkout(root: Path) -> dict[str, Any]:
    """Return a mechanical OPEN inventory for ``root``. Does not mutate files."""
    report: dict[str, Any] = {
        "root": str(root.resolve()),
        "scientific_effect": "NONE",
        "flipped_anything": False,
        "lemma_closed": False,
        "goal_complete": False,
        "audit_kind": "research_stack_mechanical_open_list",
    }

    packet_path = root / "docs" / "math_status" / "PACKET.json"
    graph_path = root / "claims" / "graph.json"
    oq_path = root / "registers" / "json" / "open_questions.json"

    if not packet_path.is_file():
        report["shape"] = "NO_PACKET"
        report["note"] = (
            "Checkout lacks docs/math_status/PACKET.json — typically the "
            "post-#41 ALIGNED default tip (body under history/). Research "
            "stack inventory requires the hardening tip."
        )
        report["open_premises"] = []
        report["open_lemmas"] = []
        report["open_obligations_packet"] = []
        report["open_prizes"] = []
        report["claims_inventory"] = []
        report["open_questions"] = []
        report["evidence_paths"] = []
        report["packet"] = None
        return report

    packet = _load_json(packet_path)
    report["shape"] = "HAS_PACKET"
    report["packet"] = {
        "path": "docs/math_status/PACKET.json",
        "disposition": packet.get("disposition"),
        "lemma_closed": packet.get("lemma_closed"),
        "prizes_solved": packet.get("prizes_solved"),
        "original_prize_closed": packet.get("original_prize_closed"),
        "independence_credit": packet.get("independence_credit"),
        "bridge": packet.get("bridge"),
        "freeze": packet.get("freeze"),
        "authority": packet.get("authority"),
        "base_branch": packet.get("base_branch"),
        "base_commit": packet.get("base_commit"),
        "as_of": packet.get("as_of"),
    }
    # Packet flags must remain false; this audit never writes them.
    report["lemma_closed"] = False
    report["lemma_closed_confirmation"] = packet.get("lemma_closed") is False
    report["prizes_solved_confirmation"] = packet.get("prizes_solved") is False
    report["original_prize_closed_confirmation"] = (
        packet.get("original_prize_closed") is False
    )
    report["packet_lemma_closed_raw"] = packet.get("lemma_closed")
    report["packet_prizes_solved_raw"] = packet.get("prizes_solved")
    report["packet_original_prize_closed_raw"] = packet.get("original_prize_closed")

    obl_jet = packet.get("OBL-H5-JETMOD") or {}
    obl_rnu = packet.get("D3-LEMMA-RN-UNIF") or {}
    open_obligations = []
    for oid, blob in (("OBL-H5-JETMOD", obl_jet), ("D3-LEMMA-RN-UNIF", obl_rnu)):
        if not isinstance(blob, dict):
            continue
        open_obligations.append(
            {
                "id": oid,
                "status": blob.get("status"),
                "lemma_closed": blob.get("lemma_closed"),
                "freeze": blob.get("freeze"),
                "extra": {
                    k: blob[k]
                    for k in blob
                    if k
                    not in {"status", "lemma_closed", "freeze"}
                },
            }
        )
    report["open_obligations_packet"] = open_obligations
    report["open_lemmas"] = [
        {
            "id": "D3-LEMMA-RN-UNIF",
            "status": obl_rnu.get("status"),
            "lemma_closed": obl_rnu.get("lemma_closed"),
            "piece2_annulus_driver": obl_rnu.get("piece2_annulus_driver"),
            "discharges_lemma": obl_rnu.get("discharges_lemma"),
            "source": "docs/math_status/PACKET.json",
        }
    ]

    open_premises: list[dict[str, Any]] = []
    claims_inventory: list[dict[str, Any]] = []
    open_prizes: list[dict[str, Any]] = []
    d1_validity: list[str] = []
    firewalls: list[str] = []

    if graph_path.is_file():
        graph = _load_json(graph_path)
        report["claims_graph_as_of"] = graph.get("as_of")
        for pid, prem in (graph.get("premises") or {}).items():
            froz = prem.get("status_frozen_v2_2")
            open_premises.append(
                {
                    "id": pid,
                    "track": prem.get("track"),
                    "status_frozen_v2_2": froz,
                    "status_register_note": prem.get("status_register_note"),
                    "mechanically_open_at_frozen_layer": froz in OPEN_FROZEN
                    or froz is None,
                    "source": prem.get("source"),
                }
            )
        for cid, claim in (graph.get("claims") or {}).items():
            row = {
                "id": cid,
                "track": claim.get("track"),
                "grade": claim.get("grade"),
                "depends_on": claim.get("depends_on") or [],
                "original_prize_closed": claim.get("original_prize_closed"),
                "independence_credit": claim.get("independence_credit"),
                "source": claim.get("source"),
            }
            claims_inventory.append(row)
            if claim.get("track") == "NUMBER_THEORY" or claim.get(
                "original_prize_closed"
            ) is False:
                open_prizes.append(
                    {
                        **row,
                        "note": "FW-NO-PRIZE-CLOSURE: original_prize_closed must stay false",
                    }
                )
        d1 = (graph.get("claims") or {}).get("D1-v2.2(2)") or {}
        d1_validity = list(d1.get("depends_on") or [])
        firewalls = [f.get("id") for f in (graph.get("firewalls") or []) if f.get("id")]

    report["open_premises"] = [
        p for p in open_premises if p["mechanically_open_at_frozen_layer"]
    ]
    report["premises_all"] = open_premises
    report["claims_inventory"] = claims_inventory
    report["open_prizes"] = open_prizes
    report["d1_v2_2_validity_premises_still_named"] = d1_validity
    report["firewalls"] = firewalls

    open_questions: list[dict[str, Any]] = []
    if oq_path.is_file():
        oq = _load_json(oq_path)
        header = oq.get("header") or []
        # Expected columns from GP-REG export
        for row in oq.get("rows") or []:
            if not isinstance(row, list) or not row:
                continue
            oid = str(row[0])
            if oid in {"PROTOCOL", "OQ ID"} or oid.startswith("OQ ID"):
                continue
            reg = row[3] if len(row) > 3 else ""
            live = row[5] if len(row) > 5 else ""
            if _oq_mechanically_open(str(reg), str(live)):
                open_questions.append(
                    {
                        "id": oid,
                        "decision_class": row[1] if len(row) > 1 else "",
                        "priority": row[2] if len(row) > 2 else "",
                        "register_status": reg,
                        "live_state": live,
                        "next_decisive_action": row[6] if len(row) > 6 else "",
                    }
                )
    report["open_questions"] = open_questions

    report["counts"] = {
        "open_premises_frozen_layer": len(report["open_premises"]),
        "open_lemmas": len(report["open_lemmas"]),
        "open_obligations_packet": len(report["open_obligations_packet"]),
        "open_prizes": len(report["open_prizes"]),
        "claims_total": len(claims_inventory),
        "open_questions": len(open_questions),
    }
    report["evidence_paths"] = [
        "docs/math_status/PACKET.json",
        "docs/math_status/STATUS.md",
        "docs/math_status/STATUS_JETMOD.md",
        "docs/math_status/STATUS_RN_UNIF.md",
        "docs/math_status/math_console_snapshot.json",
        "claims/graph.json",
        "registers/json/open_questions.json",
    ]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List OPEN premises/lemmas/prizes/claims from a local checkout. "
            "Read-only. Scientific effect: NONE."
        )
    )
    parser.add_argument(
        "checkout",
        type=Path,
        help="Path to a local clone (default tip or hardening tip)",
    )
    parser.add_argument(
        "--tip-sha",
        default="",
        help="Optional tip SHA to embed in the report (caller supplies)",
    )
    args = parser.parse_args(argv)
    root = args.checkout
    if not root.is_dir():
        print(f"audit_research_stack_open: not a directory: {root}", file=sys.stderr)
        return 2
    try:
        report = audit_checkout(root)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"audit_research_stack_open: failure: {exc}", file=sys.stderr)
        return 2
    if args.tip_sha:
        report["tip_sha"] = args.tip_sha
    print(json.dumps(report, indent=2, sort_keys=False))
    shape = report.get("shape")
    counts = report.get("counts") or {}
    print(
        f"audit_research_stack_open: shape={shape} "
        f"open_premises={counts.get('open_premises_frozen_layer', 0)} "
        f"open_lemmas={counts.get('open_lemmas', 0)} "
        f"open_prizes={counts.get('open_prizes', 0)} "
        f"open_questions={counts.get('open_questions', 0)} "
        f"lemma_closed={report.get('lemma_closed')} "
        f"flipped_anything=false scientific_effect=NONE",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
