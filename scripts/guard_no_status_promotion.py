#!/usr/bin/env python3
"""Guard: fail if research stack OPEN items were promoted / closed.

Compares a live hardening (or local) checkout against
``portable/BATCH70_RESEARCH_STACK_AUDIT.json`` or the last
``portable/STATUS_GUARD_SNAPSHOT.json``.

FAIL (exit 1) when any previously-OPEN premise / lemma / prize /
packet obligation flips to closed / discharged / promoted, or when
``lemma_closed`` becomes true anywhere in PACKET.

PASS (exit 0) when unchanged or only *new* OPEN items appear.
Always writes ``portable/STATUS_GUARD_SNAPSHOT.json`` on a successful
read (even when failing the promotion check).

Scientific effect: NONE. Never writes research status on the checkout.
Exit 2 on usage / missing inputs / IO errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse mechanical OPEN inventory (read-only).
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from audit_research_stack_open import (  # noqa: E402
    OPEN_FROZEN,
    audit_checkout,
)

CLOSED_TOKENS = {
    "CLOSED",
    "DISCHARGED",
    "PROMOTED",
    "SOLVED",
    "DONE",
    "TERMINAL",
    "DISCHARGE",
    "PROMOTE",
}


def _trial_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _status_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _looks_closed(status: Any) -> bool:
    """True if a status string indicates closed / discharged / promoted."""
    tok = _status_token(status)
    if not tok:
        return False
    if tok in OPEN_FROZEN:
        return False
    # Exact closed tokens or leading CLOSED/DISCHARGED/PROMOTED…
    for closed in CLOSED_TOKENS:
        if tok == closed or tok.startswith(closed + " ") or tok.startswith(closed + "_"):
            # Avoid matching OPEN-with-CLOSED-in-note; require start or exact.
            if tok.startswith("OPEN"):
                return False
            return True
    # Frozen-layer closed forms seen in claims graph
    if tok in {"CLOSED_AT_FROZEN", "DISCHARGED_AT_FROZEN"}:
        return True
    return False


def _was_open_status(status: Any) -> bool:
    tok = _status_token(status)
    if not tok:
        return True  # missing treated as open at frozen layer (audit convention)
    if tok in OPEN_FROZEN:
        return True
    if tok.startswith("OPEN") or tok.startswith("HOLD") or tok.startswith("REBASED"):
        return True
    return False


def extract_open_inventory(report: dict[str, Any]) -> dict[str, Any]:
    """Normalize an audit report (or nested hardening_tip_audit) into guard keys."""
    # Unwrap Batch 70 artifact shape if needed.
    if "hardening_tip_audit" in report and isinstance(report["hardening_tip_audit"], dict):
        src = report["hardening_tip_audit"]
        tip_sha = report.get("hardening_tip") or src.get("tip_sha")
    else:
        src = report
        tip_sha = src.get("tip_sha") or report.get("hardening_tip") or report.get("tip_sha")

    packet = src.get("packet") or {}
    premises: dict[str, str] = {}
    for row in src.get("open_premises") or []:
        if not isinstance(row, dict):
            continue
        pid = row.get("id")
        if not pid:
            continue
        premises[str(pid)] = _status_token(
            row.get("status_frozen_v2_2") or row.get("status") or "OPEN"
        )

    lemmas: dict[str, dict[str, Any]] = {}
    for row in src.get("open_lemmas") or []:
        if not isinstance(row, dict):
            continue
        lid = row.get("id")
        if not lid:
            continue
        lemmas[str(lid)] = {
            "status": _status_token(row.get("status") or "OPEN"),
            "lemma_closed": bool(row.get("lemma_closed")),
            "discharges_lemma": bool(row.get("discharges_lemma")),
        }

    obligations: dict[str, dict[str, Any]] = {}
    for row in src.get("open_obligations_packet") or []:
        if not isinstance(row, dict):
            continue
        oid = row.get("id")
        if not oid:
            continue
        extra = row.get("extra") or {}
        obligations[str(oid)] = {
            "status": _status_token(row.get("status") or "OPEN"),
            "lemma_closed": bool(row.get("lemma_closed")),
            "discharges_lemma": bool(extra.get("discharges_lemma"))
            if isinstance(extra, dict)
            else False,
            "discharges_OBL_H5_JETMOD": bool(extra.get("discharges_OBL_H5_JETMOD"))
            if isinstance(extra, dict)
            else False,
        }

    prizes: dict[str, dict[str, Any]] = {}
    for row in src.get("open_prizes") or []:
        if not isinstance(row, dict):
            continue
        prid = row.get("id")
        if not prid:
            continue
        prizes[str(prid)] = {
            "original_prize_closed": bool(row.get("original_prize_closed")),
            "grade": row.get("grade"),
        }

    return {
        "tip_sha": tip_sha,
        "shape": src.get("shape"),
        "packet_lemma_closed": bool(packet.get("lemma_closed"))
        if packet
        else bool(src.get("lemma_closed")),
        "packet_prizes_solved": bool(packet.get("prizes_solved")) if packet else False,
        "packet_original_prize_closed": bool(packet.get("original_prize_closed"))
        if packet
        else False,
        "packet_disposition": packet.get("disposition") if packet else None,
        "premises": premises,
        "lemmas": lemmas,
        "obligations": obligations,
        "prizes": prizes,
        "counts": src.get("counts")
        or {
            "open_premises_frozen_layer": len(premises),
            "open_lemmas": len(lemmas),
            "open_obligations_packet": len(obligations),
            "open_prizes": len(prizes),
        },
    }


def compare_inventories(
    baseline: dict[str, Any], current: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return list of promotion violations (empty ⇒ OK)."""
    violations: list[dict[str, Any]] = []

    # Packet-level lemma / prize flags must stay false.
    if current.get("packet_lemma_closed") is True:
        violations.append(
            {
                "kind": "packet_lemma_closed",
                "id": "PACKET",
                "baseline": False,
                "current": True,
                "reason": "lemma_closed flipped true on PACKET",
            }
        )
    if current.get("packet_prizes_solved") is True:
        violations.append(
            {
                "kind": "packet_prizes_solved",
                "id": "PACKET",
                "baseline": baseline.get("packet_prizes_solved"),
                "current": True,
                "reason": "prizes_solved flipped true on PACKET",
            }
        )
    if current.get("packet_original_prize_closed") is True:
        violations.append(
            {
                "kind": "packet_original_prize_closed",
                "id": "PACKET",
                "baseline": baseline.get("packet_original_prize_closed"),
                "current": True,
                "reason": "original_prize_closed flipped true on PACKET",
            }
        )

    # Premises: baseline OPEN → current closed/discharged/promoted, or missing
    # from open list while status looks closed (audit drops closed from open_*).
    cur_prem = current.get("premises") or {}
    for pid, b_status in (baseline.get("premises") or {}).items():
        if not _was_open_status(b_status):
            continue
        if pid not in cur_prem:
            violations.append(
                {
                    "kind": "premise",
                    "id": pid,
                    "baseline": b_status,
                    "current": "ABSENT_FROM_OPEN_LIST",
                    "reason": "OPEN premise no longer in open_premises (likely closed/promoted)",
                }
            )
            continue
        c_status = cur_prem[pid]
        if _looks_closed(c_status):
            violations.append(
                {
                    "kind": "premise",
                    "id": pid,
                    "baseline": b_status,
                    "current": c_status,
                    "reason": "OPEN premise status became closed/discharged/promoted",
                }
            )

    # Lemmas
    cur_lem = current.get("lemmas") or {}
    for lid, brow in (baseline.get("lemmas") or {}).items():
        b_status = brow.get("status") if isinstance(brow, dict) else brow
        if not _was_open_status(b_status):
            continue
        if lid not in cur_lem:
            violations.append(
                {
                    "kind": "lemma",
                    "id": lid,
                    "baseline": brow,
                    "current": "ABSENT_FROM_OPEN_LIST",
                    "reason": "OPEN lemma no longer listed (likely closed/discharged)",
                }
            )
            continue
        crow = cur_lem[lid]
        if crow.get("lemma_closed") is True:
            violations.append(
                {
                    "kind": "lemma",
                    "id": lid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "lemma_closed flipped true",
                }
            )
        if crow.get("discharges_lemma") is True and not brow.get("discharges_lemma"):
            violations.append(
                {
                    "kind": "lemma",
                    "id": lid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "discharges_lemma flipped true",
                }
            )
        if _looks_closed(crow.get("status")):
            violations.append(
                {
                    "kind": "lemma",
                    "id": lid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "OPEN lemma status became closed/discharged/promoted",
                }
            )

    # Packet obligations
    cur_obl = current.get("obligations") or {}
    for oid, brow in (baseline.get("obligations") or {}).items():
        b_status = brow.get("status") if isinstance(brow, dict) else brow
        if not _was_open_status(b_status):
            continue
        if oid not in cur_obl:
            violations.append(
                {
                    "kind": "obligation",
                    "id": oid,
                    "baseline": brow,
                    "current": "ABSENT_FROM_OPEN_LIST",
                    "reason": "OPEN packet obligation no longer listed",
                }
            )
            continue
        crow = cur_obl[oid]
        if crow.get("lemma_closed") is True:
            violations.append(
                {
                    "kind": "obligation",
                    "id": oid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "obligation lemma_closed flipped true",
                }
            )
        for flag in ("discharges_lemma", "discharges_OBL_H5_JETMOD"):
            if crow.get(flag) is True and not brow.get(flag):
                violations.append(
                    {
                        "kind": "obligation",
                        "id": oid,
                        "baseline": brow,
                        "current": crow,
                        "reason": f"{flag} flipped true",
                    }
                )
        if _looks_closed(crow.get("status")):
            violations.append(
                {
                    "kind": "obligation",
                    "id": oid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "OPEN obligation status became closed/discharged/promoted",
                }
            )

    # Prizes: original_prize_closed must stay false; absence from open list = promotion
    cur_prz = current.get("prizes") or {}
    for prid, brow in (baseline.get("prizes") or {}).items():
        was_open = (
            not bool(brow.get("original_prize_closed"))
            if isinstance(brow, dict)
            else True
        )
        if not was_open:
            continue
        if prid not in cur_prz:
            violations.append(
                {
                    "kind": "prize",
                    "id": prid,
                    "baseline": brow,
                    "current": "ABSENT_FROM_OPEN_LIST",
                    "reason": "OPEN prize no longer listed (likely closed)",
                }
            )
            continue
        crow = cur_prz[prid]
        if crow.get("original_prize_closed") is True:
            violations.append(
                {
                    "kind": "prize",
                    "id": prid,
                    "baseline": brow,
                    "current": crow,
                    "reason": "original_prize_closed flipped true",
                }
            )

    return violations


def resolve_baseline(trial_root: Path, explicit: Path | None) -> tuple[Path, dict[str, Any]]:
    """Pick STATUS_GUARD_SNAPSHOT if present, else BATCH70 audit."""
    if explicit is not None:
        data = _load_json(explicit)
        return explicit, data
    snap = trial_root / "portable" / "STATUS_GUARD_SNAPSHOT.json"
    batch70 = trial_root / "portable" / "BATCH70_RESEARCH_STACK_AUDIT.json"
    if snap.is_file():
        data = _load_json(snap)
        # Prefer nested inventory if this is already a guard snapshot
        return snap, data
    if batch70.is_file():
        return batch70, _load_json(batch70)
    raise FileNotFoundError(
        "no baseline: need portable/STATUS_GUARD_SNAPSHOT.json or "
        "portable/BATCH70_RESEARCH_STACK_AUDIT.json"
    )


def _git_head_sha(checkout: Path) -> str:
    """Best-effort HEAD SHA for tip tracking; empty string if unavailable."""
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if proc.returncode != 0:
        return ""
    sha = (proc.stdout or "").strip()
    return sha if len(sha) >= 7 else ""


def _baseline_tip_sha(baseline_raw: dict[str, Any], baseline_inv: dict[str, Any]) -> str | None:
    """Recover baseline tip even when a prior write clobbered inventory.tip_sha."""
    for candidate in (
        baseline_inv.get("tip_sha"),
        baseline_raw.get("tip_sha"),
        baseline_raw.get("baseline_tip_sha"),
    ):
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def build_snapshot(
    *,
    tip_sha: str,
    baseline_path: Path,
    baseline_inv: dict[str, Any],
    baseline_raw: dict[str, Any] | None = None,
    current_inv: dict[str, Any],
    live_report: dict[str, Any],
    violations: list[dict[str, Any]],
) -> dict[str, Any]:
    new_open_premises = sorted(
        set(current_inv.get("premises") or {}) - set(baseline_inv.get("premises") or {})
    )
    new_open_lemmas = sorted(
        set(current_inv.get("lemmas") or {}) - set(baseline_inv.get("lemmas") or {})
    )
    new_open_prizes = sorted(
        set(current_inv.get("prizes") or {}) - set(baseline_inv.get("prizes") or {})
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "guard": "no_status_promotion",
        "scientific_effect": "NONE",
        "goal_complete": False,
        "lemma_closed": False,
        "flipped_anything": False,
        "tip_sha": tip_sha,
        "baseline_path": str(baseline_path),
        "baseline_tip_sha": _baseline_tip_sha(baseline_raw or {}, baseline_inv),
        "pass": len(violations) == 0,
        "violations": violations,
        "new_open_only": {
            "premises": new_open_premises,
            "lemmas": new_open_lemmas,
            "prizes": new_open_prizes,
        },
        "inventory": current_inv,
        # Keep full live audit counts for forensics (not a status write).
        "live_shape": live_report.get("shape"),
        "live_counts": live_report.get("counts"),
        "packet": live_report.get("packet"),
        "open_premises": live_report.get("open_premises"),
        "open_lemmas": live_report.get("open_lemmas"),
        "open_obligations_packet": live_report.get("open_obligations_packet"),
        "open_prizes": live_report.get("open_prizes"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail if OPEN premises/lemmas/prizes were closed/discharged/promoted "
            "vs baseline snapshot. Scientific effect: NONE."
        )
    )
    parser.add_argument(
        "checkout",
        type=Path,
        nargs="?",
        default=None,
        help="Path to hardening (or local) clone with PACKET.json",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Override baseline JSON (default: STATUS_GUARD_SNAPSHOT or BATCH70 audit)",
    )
    parser.add_argument(
        "--trial-root",
        type=Path,
        default=None,
        help="Trial repo root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--snapshot-out",
        type=Path,
        default=None,
        help="Where to write STATUS_GUARD_SNAPSHOT.json",
    )
    parser.add_argument(
        "--tip-sha",
        default="",
        help="Optional tip SHA to embed (caller supplies)",
    )
    parser.add_argument(
        "--json-stdout",
        action="store_true",
        help="Print full snapshot JSON to stdout",
    )
    args = parser.parse_args(argv)

    trial_root = (args.trial_root or _trial_root()).resolve()
    checkout = args.checkout
    if checkout is None:
        print(
            "guard_no_status_promotion: checkout path required "
            "(hardening tip clone or local)",
            file=sys.stderr,
        )
        return 2
    checkout = checkout.resolve()
    if not checkout.is_dir():
        print(
            f"guard_no_status_promotion: not a directory: {checkout}",
            file=sys.stderr,
        )
        return 2

    snapshot_out = (
        args.snapshot_out.resolve()
        if args.snapshot_out
        else trial_root / "portable" / "STATUS_GUARD_SNAPSHOT.json"
    )

    try:
        baseline_path, baseline_raw = resolve_baseline(trial_root, args.baseline)
        # If baseline is a prior guard snapshot, inventory is nested under "inventory"
        if isinstance(baseline_raw.get("inventory"), dict) and baseline_raw.get(
            "guard"
        ) == "no_status_promotion":
            baseline_inv = baseline_raw["inventory"]
            # Preserve tip from snapshot root / prior baseline when inventory lacks it
            recovered = _baseline_tip_sha(baseline_raw, baseline_inv)
            if recovered and not baseline_inv.get("tip_sha"):
                baseline_inv = {**baseline_inv, "tip_sha": recovered}
        else:
            baseline_inv = extract_open_inventory(baseline_raw)

        live_report = audit_checkout(checkout)
        # Batch 233: never clobber tip tracking. Prefer --tip-sha, else git HEAD,
        # else whatever the live audit already carried.
        tip_sha = (args.tip_sha or "").strip() or _git_head_sha(checkout)
        if tip_sha:
            live_report["tip_sha"] = tip_sha
        current_inv = extract_open_inventory(live_report)
        if tip_sha:
            current_inv["tip_sha"] = tip_sha
        elif current_inv.get("tip_sha"):
            tip_sha = str(current_inv["tip_sha"])

        # NO_PACKET on default tip cannot be compared as a promotion pass against
        # a HAS_PACKET baseline — treat as usage error so CI clones hardening tip.
        if live_report.get("shape") == "NO_PACKET" and baseline_inv.get("shape") == "HAS_PACKET":
            print(
                "guard_no_status_promotion: checkout is NO_PACKET but baseline is "
                "HAS_PACKET — pass the hardening tip clone",
                file=sys.stderr,
            )
            return 2

        violations = compare_inventories(baseline_inv, current_inv)
        snapshot = build_snapshot(
            tip_sha=str(tip_sha),
            baseline_path=baseline_path,
            baseline_inv=baseline_inv,
            baseline_raw=baseline_raw if isinstance(baseline_raw, dict) else {},
            current_inv=current_inv,
            live_report=live_report,
            violations=violations,
        )
        snapshot_out.parent.mkdir(parents=True, exist_ok=True)
        snapshot_out.write_text(
            json.dumps(snapshot, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError, FileNotFoundError) as exc:
        print(f"guard_no_status_promotion: failure: {exc}", file=sys.stderr)
        return 2

    if args.json_stdout:
        print(json.dumps(snapshot, indent=2, sort_keys=False))

    n_viol = len(violations)
    counts = current_inv.get("counts") or {}
    print(
        f"guard_no_status_promotion: pass={n_viol == 0} violations={n_viol} "
        f"shape={live_report.get('shape')} "
        f"open_premises={counts.get('open_premises_frozen_layer', 0)} "
        f"open_lemmas={counts.get('open_lemmas', 0)} "
        f"open_prizes={counts.get('open_prizes', 0)} "
        f"baseline={baseline_path.name} snapshot={snapshot_out} "
        f"lemma_closed=false flipped_anything=false scientific_effect=NONE",
        file=sys.stderr,
    )
    if n_viol:
        for v in violations[:20]:
            print(
                f"  VIOLATION [{v.get('kind')}] {v.get('id')}: {v.get('reason')}",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
