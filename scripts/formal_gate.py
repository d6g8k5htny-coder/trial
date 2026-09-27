#!/usr/bin/env python3
"""Layer 1 formal-verification gate (fail-closed).

Extends the existing hard gate (provenance + no-status-promotion) with a
*formal* criterion: a theorem may only carry ``formalization_status =
kernel_checked`` when a Lean build receipt proves the kernel accepted it.

What this gate checks (``check`` mode; needs no Lean toolchain):

* ``formal/formalization_status.json`` validates against the schema in
  ``formal/formalization_status.schema.json`` (required keys / enums).
* Every referenced Lean module exists and its SHA-256 matches the pinned
  ``lean_source_sha256`` (hash check — the checked artifact is the intended
  one).
* Status ladder ``none < specified < proved < kernel_checked`` is earned:
  - ``specified``: declaration name appears in the Lean module.
  - ``proved``: additionally no ``sorry`` token in the module text.
  - ``kernel_checked``: additionally a receipt under ``formal/receipts/``
    binds the *current* module hashes, toolchain and Mathlib revision, has
    ``lake_build_exit_code == 0``, lists the declaration's axioms as a subset
    of ``{propext, Classical.choice, Quot.sound}`` ∪ declared
    ``explicit_axioms``, never lists ``sorryAx``, and every negative control
    (semantic mutant) was rejected by the kernel.
* Blueprint alignment: each entry has ``formal/blueprint/<id>.md`` naming the
  same ``lean_decls``; each named declaration exists in the module.
* Scientific-effect invariant: no entry may carry research-status vocabulary
  (``lemma_closed``, ``prize``, ``discharge``…) as a *claim*; the status
  file must declare ``scientific_effect: NONE``.

``--run-lake``: additionally runs ``lake build``, the axiom audit
(``tools/PrintAxioms.lean``) and the negative controls, and writes a receipt.
``--pin``: rewrite ``lean_source_sha256`` for every module (author-side action;
it invalidates old receipts, so the entry drops below ``kernel_checked`` until
``--run-lake`` succeeds again).

Exit codes: 0 pass, 1 gate FAIL (fail-closed), 2 usage / IO.

Scientific effect: NONE.  A green run here is a kernel check of the Lean
statements in ``formal/``; it does not promote, close or discharge any claim,
premise, prize or lemma on the research program (``lemma_closed`` stays false).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_LADDER = ["none", "specified", "proved", "kernel_checked"]
ALIGNMENT_REVIEW = ["unreviewed", "author_side", "distinct_reviewer"]
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN_AXIOMS = {"sorryAx"}
# Research-status vocabulary that must never appear as a claim in formal metadata.
STATUS_WORDS = re.compile(
    r"\b(lemma_closed\s*[:=]\s*true|prizes?_solved\s*[:=]\s*true|"
    r"discharged|promoted|CLOSED_AT_FROZEN)\b",
    re.IGNORECASE,
)
SORRY_TOKEN = re.compile(r"(?<![A-Za-z0-9_'])sorry(?![A-Za-z0-9_'])")
AXIOM_LINE = re.compile(r"^'(?P<decl>[^']+)' depends on axioms: \[(?P<axioms>[^\]]*)\]\s*$")
AXIOM_NONE = re.compile(r"^'(?P<decl>[^']+)' does not depend on any axioms\s*$")


def _root() -> Path:
    return Path(__file__).resolve().parent.parent


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# Schema (minimal, dependency-free validation; full JSON Schema kept alongside)
# --------------------------------------------------------------------------- #

REQUIRED_TOP = {
    "schema_id": str,
    "schema_version": int,
    "scientific_effect": str,
    "lemma_closed": bool,
    "lean_project_dir": str,
    "toolchain": dict,
    "modules": dict,
    "theorems": list,
    "negative_controls": list,
}
REQUIRED_TOOLCHAIN = {"lean": str, "mathlib_rev": str}
REQUIRED_THEOREM = {
    "id": str,
    "informal_source": dict,
    "informal_statement": str,
    "lean_module": str,
    "lean_decls": list,
    "formalization_status": str,
    "explicit_axioms": list,
    "hypotheses_are_scope": list,
    "does_not_claim": list,
    "alignment_review": dict,
    "verification_level_if_kernel_checked": str,
}
REQUIRED_SOURCE = {"repo": str, "path": str, "sha256": str}
REQUIRED_ALIGNMENT = {"status": str}


def validate_schema(status: dict[str, Any]) -> list[str]:
    errs: list[str] = []

    def need(obj: Any, spec: dict[str, type], where: str) -> None:
        if not isinstance(obj, dict):
            errs.append(f"{where}: expected object")
            return
        for key, typ in spec.items():
            if key not in obj:
                errs.append(f"{where}: missing '{key}'")
            elif not isinstance(obj[key], typ) or (typ is int and isinstance(obj[key], bool)):
                errs.append(f"{where}.{key}: expected {typ.__name__}")

    need(status, REQUIRED_TOP, "status")
    if errs:
        return errs
    if status["schema_id"] != "trial.formal.formalization_status.v1":
        errs.append("status.schema_id must be 'trial.formal.formalization_status.v1'")
    if status["scientific_effect"] != "NONE":
        errs.append("status.scientific_effect must be 'NONE'")
    if status["lemma_closed"] is not False:
        errs.append("status.lemma_closed must be false (formal layer never flips it)")
    need(status["toolchain"], REQUIRED_TOOLCHAIN, "status.toolchain")
    for mod, rec in status["modules"].items():
        need(rec, {"path": str, "lean_source_sha256": str}, f"modules[{mod}]")
    seen_ids: set[str] = set()
    for i, th in enumerate(status["theorems"]):
        where = f"theorems[{i}]"
        need(th, REQUIRED_THEOREM, where)
        if not isinstance(th, dict):
            continue
        tid = th.get("id")
        if isinstance(tid, str):
            if tid in seen_ids:
                errs.append(f"{where}: duplicate id {tid}")
            seen_ids.add(tid)
        if th.get("formalization_status") not in STATUS_LADDER:
            errs.append(f"{where}.formalization_status not in {STATUS_LADDER}")
        need(th.get("informal_source"), REQUIRED_SOURCE, f"{where}.informal_source")
        need(th.get("alignment_review"), REQUIRED_ALIGNMENT, f"{where}.alignment_review")
        ar = th.get("alignment_review") or {}
        if isinstance(ar, dict) and ar.get("status") not in ALIGNMENT_REVIEW:
            errs.append(f"{where}.alignment_review.status not in {ALIGNMENT_REVIEW}")
        if isinstance(ar, dict) and ar.get("status") == "distinct_reviewer" and not ar.get("reviewer"):
            errs.append(f"{where}.alignment_review: distinct_reviewer requires 'reviewer'")
        if th.get("verification_level_if_kernel_checked") != "L5":
            errs.append(f"{where}.verification_level_if_kernel_checked must be 'L5' (metadata only)")
        if not th.get("lean_decls"):
            errs.append(f"{where}.lean_decls must be non-empty")
        if not th.get("does_not_claim"):
            errs.append(f"{where}.does_not_claim must be non-empty (scope discipline)")
    for i, nc in enumerate(status["negative_controls"]):
        need(nc, {"path": str, "expected": str}, f"negative_controls[{i}]")
        if isinstance(nc, dict) and nc.get("expected") != "REJECTED":
            errs.append(f"negative_controls[{i}].expected must be 'REJECTED'")
    return errs


# --------------------------------------------------------------------------- #
# Lean project helpers
# --------------------------------------------------------------------------- #


def read_toolchain(project: Path) -> str:
    return (project / "lean-toolchain").read_text(encoding="utf-8").strip()


def read_mathlib_rev(project: Path) -> str:
    manifest = _load_json(project / "lake-manifest.json")
    for pkg in manifest.get("packages", []):
        if pkg.get("name") == "mathlib":
            return str(pkg.get("rev", ""))
    return ""


def parse_axiom_output(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        m = AXIOM_LINE.match(line)
        if m:
            axioms = [a.strip() for a in m.group("axioms").split(",") if a.strip()]
            out[m.group("decl")] = axioms
            continue
        m = AXIOM_NONE.match(line)
        if m:
            out[m.group("decl")] = []
    return out


def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as exc:
        return 127, f"{exc}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s: {' '.join(cmd)}"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _lake_bin() -> str | None:
    lake = shutil.which("lake")
    if lake:
        return lake
    home = Path(os.environ.get("HOME", "~")).expanduser()
    cand = home / ".elan" / "bin" / "lake"
    return str(cand) if cand.is_file() else None


def run_lake_and_receipt(
    root: Path, status: dict[str, Any], receipt_out: Path, timeout: int
) -> tuple[int, dict[str, Any]]:
    """Run lake build + axiom audit + negative controls; write receipt."""
    project = root / status["lean_project_dir"]
    lake = _lake_bin()
    receipt: dict[str, Any] = {
        "schema_id": "trial.formal.lean_build_receipt.v1",
        "generated_at_utc": _utc_now(),
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "lean_project_dir": status["lean_project_dir"],
        "toolchain": read_toolchain(project),
        "mathlib_rev": read_mathlib_rev(project),
        "lake_bin": lake,
        "module_sha256": {},
        "lake_build_exit_code": None,
        "lake_build_tail": "",
        "axioms": {},
        "axioms_exit_code": None,
        "negative_controls": [],
    }
    for mod, rec in status["modules"].items():
        receipt["module_sha256"][mod] = sha256_file(project / rec["path"])
    if lake is None:
        receipt["lake_build_exit_code"] = 127
        receipt["lake_build_tail"] = "lake not found (install elan; see formal/README.md)"
        receipt_out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return 2, receipt

    code, out = _run([lake, "build"], project, timeout)
    receipt["lake_build_exit_code"] = code
    receipt["lake_build_tail"] = "\n".join(
        [ln for ln in out.splitlines() if not ln.startswith("trace:")][-40:]
    )
    if code == 0:
        acode, aout = _run([lake, "env", "lean", "tools/PrintAxioms.lean"], project, timeout)
        receipt["axioms_exit_code"] = acode
        receipt["axioms"] = parse_axiom_output(aout)
        for nc in status["negative_controls"]:
            ccode, cout = _run([lake, "env", "lean", nc["path"]], project, timeout)
            receipt["negative_controls"].append(
                {
                    "path": nc["path"],
                    "exit_code": ccode,
                    "outcome": "REJECTED" if ccode != 0 else "ACCEPTED",
                    "tail": "\n".join(cout.splitlines()[-6:]),
                }
            )
    receipt_out.parent.mkdir(parents=True, exist_ok=True)
    receipt_out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return (0 if code == 0 else 1), receipt


# --------------------------------------------------------------------------- #
# Gate evaluation
# --------------------------------------------------------------------------- #


def find_receipts(root: Path) -> list[Path]:
    rdir = root / "formal" / "receipts"
    if not rdir.is_dir():
        return []
    return sorted(p for p in rdir.glob("*.json") if p.name != "README.json")


def receipt_binds(receipt: dict[str, Any], status: dict[str, Any], project: Path) -> list[str]:
    """Reasons a receipt does NOT bind the current tree (empty ⇒ binds)."""
    reasons: list[str] = []
    if receipt.get("schema_id") != "trial.formal.lean_build_receipt.v1":
        reasons.append("receipt schema_id mismatch")
    if receipt.get("lake_build_exit_code") != 0:
        reasons.append(f"lake_build_exit_code={receipt.get('lake_build_exit_code')}")
    if receipt.get("toolchain") != read_toolchain(project):
        reasons.append("toolchain mismatch vs lean-toolchain")
    if receipt.get("toolchain") != status["toolchain"]["lean"]:
        reasons.append("toolchain mismatch vs status.toolchain.lean")
    if receipt.get("mathlib_rev") != read_mathlib_rev(project):
        reasons.append("mathlib_rev mismatch vs lake-manifest.json")
    if receipt.get("mathlib_rev") != status["toolchain"]["mathlib_rev"]:
        reasons.append("mathlib_rev mismatch vs status.toolchain.mathlib_rev")
    for mod, rec in status["modules"].items():
        cur = sha256_file(project / rec["path"]) if (project / rec["path"]).is_file() else ""
        if receipt.get("module_sha256", {}).get(mod) != cur:
            reasons.append(f"receipt module hash stale: {mod}")
    if receipt.get("axioms_exit_code") != 0:
        reasons.append("axiom audit did not run cleanly")
    ncs = {nc["path"]: nc for nc in receipt.get("negative_controls", [])}
    for nc in status["negative_controls"]:
        got = ncs.get(nc["path"])
        if got is None:
            reasons.append(f"negative control not run: {nc['path']}")
        elif got.get("outcome") != "REJECTED":
            reasons.append(f"negative control ACCEPTED by kernel (gate failure): {nc['path']}")
    return reasons


def evaluate(root: Path, status: dict[str, Any], research_checkout: Path | None) -> dict[str, Any]:
    project = root / status["lean_project_dir"]
    problems: list[str] = []
    entries: list[dict[str, Any]] = []

    # Toolchain pins must agree with the project files.
    if project.is_dir():
        tc = read_toolchain(project)
        if tc != status["toolchain"]["lean"]:
            problems.append(f"toolchain pin drift: status={status['toolchain']['lean']} project={tc}")
        rev = read_mathlib_rev(project)
        if rev != status["toolchain"]["mathlib_rev"]:
            problems.append(f"mathlib pin drift: status={status['toolchain']['mathlib_rev']} manifest={rev}")
    else:
        problems.append(f"lean project dir missing: {project}")

    # Module hash lock.
    module_text: dict[str, str] = {}
    for mod, rec in status["modules"].items():
        path = project / rec["path"]
        if not path.is_file():
            problems.append(f"module missing: {mod} → {rec['path']}")
            continue
        cur = sha256_file(path)
        if cur != rec["lean_source_sha256"]:
            problems.append(f"hash mismatch: {mod} pinned={rec['lean_source_sha256'][:12]} actual={cur[:12]}")
        module_text[mod] = path.read_text(encoding="utf-8")

    # Receipts that bind the current tree.
    binding: list[tuple[Path, dict[str, Any]]] = []
    receipt_notes: dict[str, list[str]] = {}
    if project.is_dir():
        for rp in find_receipts(root):
            try:
                rec = _load_json(rp)
            except (OSError, json.JSONDecodeError) as exc:
                receipt_notes[rp.name] = [f"unreadable: {exc}"]
                continue
            reasons = receipt_binds(rec, status, project)
            receipt_notes[rp.name] = reasons
            if not reasons:
                binding.append((rp, rec))

    # Optional research-checkout provenance check of informal sources.
    for th in status["theorems"]:
        tid = th["id"]
        entry: dict[str, Any] = {
            "id": tid,
            "declared_status": th["formalization_status"],
            "earned_status": "none",
            "alignment_review": th["alignment_review"]["status"],
            "problems": [],
        }
        mod = th["lean_module"]
        text = module_text.get(mod)
        if text is None:
            entry["problems"].append(f"module not loaded: {mod}")
        else:
            missing = [d for d in th["lean_decls"] if not re.search(rf"\b{re.escape(d)}\b", text)]
            if missing:
                entry["problems"].append(f"lean_decls not found in {mod}: {missing}")
            else:
                entry["earned_status"] = "specified"
                if not SORRY_TOKEN.search(text):
                    entry["earned_status"] = "proved"
                    # kernel_checked requires a binding receipt covering every decl.
                    for rp, rec in binding:
                        ok = True
                        allowed = STANDARD_AXIOMS | set(th.get("explicit_axioms") or [])
                        for d in th["lean_decls"]:
                            full = f"Side24Formal.{d}" if not d.startswith("Side24Formal.") else d
                            axioms = rec.get("axioms", {}).get(full)
                            if axioms is None:
                                axioms = rec.get("axioms", {}).get(d)
                            if axioms is None:
                                ok = False
                                entry["problems"].append(f"receipt {rp.name} lacks axiom report for {d}")
                                break
                            bad = set(axioms) & FORBIDDEN_AXIOMS
                            extra = set(axioms) - allowed
                            if bad or extra:
                                ok = False
                                entry["problems"].append(
                                    f"{d}: forbidden/undeclared axioms {sorted(bad | extra)} (receipt {rp.name})"
                                )
                                break
                        if ok:
                            entry["earned_status"] = "kernel_checked"
                            entry["receipt"] = rp.name
                            break
        # Blueprint alignment.
        bp = root / "formal" / "blueprint" / f"{tid}.md"
        if not bp.is_file():
            entry["problems"].append(f"blueprint missing: formal/blueprint/{tid}.md")
        else:
            bp_text = bp.read_text(encoding="utf-8")
            for d in th["lean_decls"]:
                if d not in bp_text:
                    entry["problems"].append(f"blueprint does not reference lean decl {d}")
            if th["informal_source"]["sha256"] not in bp_text:
                entry["problems"].append("blueprint does not cite informal_source.sha256")
        # Scope discipline: metadata may not read as a status claim.
        blob = json.dumps(th)
        if STATUS_WORDS.search(blob):
            entry["problems"].append("research-status vocabulary used as a claim in formal metadata")
        # Optional provenance check against a research checkout.
        if research_checkout is not None:
            src = research_checkout / th["informal_source"]["path"]
            if not src.is_file():
                entry["problems"].append(f"informal source missing in research checkout: {src.name}")
            else:
                entry["informal_source_file_sha256"] = sha256_file(src)
                if th["informal_source"].get("file_sha256") and (
                    entry["informal_source_file_sha256"] != th["informal_source"]["file_sha256"]
                ):
                    entry["problems"].append("informal source file hash drift vs research checkout")
        # Ladder: declared must not exceed earned.
        if STATUS_LADDER.index(th["formalization_status"]) > STATUS_LADDER.index(entry["earned_status"]):
            entry["problems"].append(
                f"declared {th['formalization_status']} but only earned {entry['earned_status']}"
            )
        # Lane display (museum): what may be shown.
        if entry["earned_status"] == "kernel_checked" and entry["alignment_review"] == "distinct_reviewer":
            entry["lane_display"] = "KERNEL_CHECKED / ALIGNMENT_REVIEWED"
        elif entry["earned_status"] == "kernel_checked":
            entry["lane_display"] = "KERNEL_CHECKED / AUTHOR_SIDE_ALIGNMENT"
        else:
            entry["lane_display"] = f"{entry['earned_status'].upper()} / AUTHOR_SIDE_CANDIDATE"
        entry["verification_level"] = "L5" if entry["earned_status"] == "kernel_checked" else "L0"
        entries.append(entry)
        problems.extend(f"[{tid}] {p}" for p in entry["problems"])

    return {
        "generated_at_utc": _utc_now(),
        "gate": "formal_layer_1",
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "flipped_anything": False,
        "pass": not problems,
        "problems": problems,
        "binding_receipts": [rp.name for rp, _ in binding],
        "receipt_notes": receipt_notes,
        "theorems": entries,
        "note": (
            "verification_level is evidence metadata (L5 = proof-assistant checked); "
            "it is never scientific acceptance, claim promotion, or lemma closure."
        ),
    }


def pin_hashes(root: Path, status: dict[str, Any], status_path: Path) -> None:
    project = root / status["lean_project_dir"]
    for mod, rec in status["modules"].items():
        rec["lean_source_sha256"] = sha256_file(project / rec["path"])
    status["toolchain"]["lean"] = read_toolchain(project)
    status["toolchain"]["mathlib_rev"] = read_mathlib_rev(project)
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None, help="trial repo root")
    ap.add_argument("--status", type=Path, default=None, help="formalization_status.json path")
    ap.add_argument("--run-lake", action="store_true", help="run lake build + audits, write receipt")
    ap.add_argument("--receipt-out", type=Path, default=None, help="receipt path for --run-lake")
    ap.add_argument("--pin", action="store_true", help="re-pin module hashes + toolchain (author-side)")
    ap.add_argument("--research-checkout", type=Path, default=None, help="optional main clone for provenance")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--json-stdout", action="store_true")
    ap.add_argument("--report-out", type=Path, default=None, help="write gate report JSON here")
    args = ap.parse_args(argv)

    root = (args.root or _root()).resolve()
    status_path = (args.status or root / "formal" / "formalization_status.json").resolve()
    if not status_path.is_file():
        print(f"formal_gate: missing {status_path}", file=sys.stderr)
        return 2
    try:
        status = _load_json(status_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"formal_gate: cannot read status: {exc}", file=sys.stderr)
        return 2

    schema_errs = validate_schema(status)
    if schema_errs:
        for e in schema_errs:
            print(f"formal_gate: SCHEMA {e}", file=sys.stderr)
        return 1

    if args.pin:
        pin_hashes(root, status, status_path)
        print(f"formal_gate: pinned module hashes + toolchain into {status_path}", file=sys.stderr)

    if args.run_lake:
        receipt_out = args.receipt_out or (
            root / "formal" / "receipts" / f"lake-build-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        )
        code, receipt = run_lake_and_receipt(root, status, receipt_out, args.timeout)
        print(
            f"formal_gate: lake build exit={receipt['lake_build_exit_code']} "
            f"axioms_exit={receipt['axioms_exit_code']} controls="
            f"{[(c['path'], c['outcome']) for c in receipt['negative_controls']]} "
            f"receipt={receipt_out}",
            file=sys.stderr,
        )
        if code == 2:
            return 2

    report = evaluate(root, status, args.research_checkout)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json_stdout:
        print(json.dumps(report, indent=2))
    for th in report["theorems"]:
        print(
            f"formal_gate: {th['id']} declared={th['declared_status']} earned={th['earned_status']} "
            f"lane='{th['lane_display']}' level={th['verification_level']}",
            file=sys.stderr,
        )
    print(
        f"formal_gate: pass={report['pass']} problems={len(report['problems'])} "
        f"binding_receipts={report['binding_receipts']} lemma_closed=false "
        f"flipped_anything=false scientific_effect=NONE",
        file=sys.stderr,
    )
    for p in report["problems"][:30]:
        print(f"  PROBLEM {p}", file=sys.stderr)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
