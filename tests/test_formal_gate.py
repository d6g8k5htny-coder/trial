"""Layer 1 formal-gate tests (Batch 828).

These prove the *gate* is fail-closed.  They do not run Lean.  A green run
here is not research evidence (AGENTS.md); it says only that
``scripts/formal_gate.py`` refuses unearned ``kernel_checked`` status.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "formal_gate.py"
STATUS = ROOT / "formal" / "formalization_status.json"
LEAN_DIR = ROOT / "formal" / "lean"

sys.path.insert(0, str(ROOT / "scripts"))
import formal_gate  # noqa: E402


def _run_gate(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(root), *extra],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _sandbox(tmp_path: Path) -> Path:
    """Copy the formal layer (sources + ledger + receipts + blueprint) to tmp."""
    dst = tmp_path / "trial"
    (dst / "formal").mkdir(parents=True)
    for name in ("formalization_status.json", "formalization_status.schema.json", "GLOSSARY.md"):
        shutil.copy(ROOT / "formal" / name, dst / "formal" / name)
    shutil.copytree(ROOT / "formal" / "blueprint", dst / "formal" / "blueprint")
    shutil.copytree(ROOT / "formal" / "receipts", dst / "formal" / "receipts")
    (dst / "formal" / "lean").mkdir()
    for name in ("lakefile.toml", "lean-toolchain", "lake-manifest.json", "Side24Formal.lean"):
        shutil.copy(LEAN_DIR / name, dst / "formal" / "lean" / name)
    shutil.copytree(LEAN_DIR / "Side24Formal", dst / "formal" / "lean" / "Side24Formal")
    shutil.copytree(LEAN_DIR / "controls", dst / "formal" / "lean" / "controls")
    shutil.copytree(LEAN_DIR / "tools", dst / "formal" / "lean" / "tools")
    return dst


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(p: Path, data: dict) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Committed tree
# --------------------------------------------------------------------------- #


def test_formal_layer_files_exist() -> None:
    assert STATUS.is_file()
    assert (ROOT / "formal" / "formalization_status.schema.json").is_file()
    assert (ROOT / "formal" / "GLOSSARY.md").is_file()
    assert (ROOT / "formal" / "README.md").is_file()
    assert (ROOT / "formal" / "blueprint" / "SIDE24-PILOT-001.md").is_file()
    assert (LEAN_DIR / "lakefile.toml").is_file()
    assert (LEAN_DIR / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.19.0"
    assert (LEAN_DIR / "Side24Formal" / "Glossary.lean").is_file()
    assert (LEAN_DIR / "Side24Formal" / "Side24Pilot.lean").is_file()
    assert (LEAN_DIR / "tools" / "PrintAxioms.lean").is_file()
    assert (LEAN_DIR / "controls" / "Mutant_WindowShift.lean").is_file()
    assert (LEAN_DIR / "controls" / "Mutant_WrongDenominator.lean").is_file()
    assert (ROOT / ".github" / "workflows" / "formal-gate.yml").is_file()
    assert (ROOT / "docs" / "FORMAL_VERIFICATION_LAYER.md").is_file()


def test_committed_ledger_passes_gate_and_earns_kernel_checked() -> None:
    proc = _run_gate(ROOT, "--json-stdout")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["pass"] is True
    assert report["scientific_effect"] == "NONE"
    assert report["lemma_closed"] is False
    assert report["flipped_anything"] is False
    (entry,) = [t for t in report["theorems"] if t["id"] == "SIDE24-PILOT-001"]
    assert entry["earned_status"] == "kernel_checked"
    assert entry["verification_level"] == "L5"
    assert entry["lane_display"].startswith("KERNEL_CHECKED")
    # Author-side until a distinct reviewer signs the alignment.
    assert entry["alignment_review"] == "author_side"
    assert "AUTHOR_SIDE" in entry["lane_display"]
    assert "lemma_closed=false" in proc.stderr


def test_ledger_scope_discipline() -> None:
    status = _load(STATUS)
    assert status["scientific_effect"] == "NONE"
    assert status["lemma_closed"] is False
    assert status["toolchain"]["lean"] == "leanprover/lean4:v4.19.0"
    assert status["toolchain"]["mathlib_rev"] == "c44e0c8ee63ca166450922a373c7409c5d26b00b"
    (th,) = status["theorems"]
    assert th["does_not_claim"], "scope discipline requires an explicit does-not-claim list"
    assert any("c_24" in s for s in th["does_not_claim"])
    assert th["hypotheses_are_scope"], "Γ(1/6) enclosure must be declared as scope"
    assert th["explicit_axioms"] == []
    assert th["informal_source"]["sha256"] == (
        "54cedb1eba9d72648619468beed9b8870bb3d28dbe206805dc72b4f796557cf3"
    )
    assert formal_gate.validate_schema(status) == []


def test_pinned_hashes_match_sources() -> None:
    status = _load(STATUS)
    for mod, rec in status["modules"].items():
        path = LEAN_DIR / rec["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == rec["lean_source_sha256"], mod


def test_receipt_binds_current_tree() -> None:
    status = _load(STATUS)
    receipts = formal_gate.find_receipts(ROOT)
    assert receipts, "a committed binding receipt is required for kernel_checked"
    binding = [rp for rp in receipts if not formal_gate.receipt_binds(_load(rp), status, LEAN_DIR)]
    assert binding, "no committed receipt binds the current tree"
    rec = _load(binding[0])
    assert rec["lake_build_exit_code"] == 0
    for decl, axioms in rec["axioms"].items():
        assert "sorryAx" not in axioms, decl
        assert set(axioms) <= formal_gate.STANDARD_AXIOMS, decl
    outcomes = {c["path"]: c["outcome"] for c in rec["negative_controls"]}
    assert outcomes == {
        "controls/Mutant_WindowShift.lean": "REJECTED",
        "controls/Mutant_WrongDenominator.lean": "REJECTED",
    }


def test_lean_sources_have_no_sorry_and_state_scope() -> None:
    pilot = (LEAN_DIR / "Side24Formal" / "Side24Pilot.lean").read_text(encoding="utf-8")
    glossary = (LEAN_DIR / "Side24Formal" / "Glossary.lean").read_text(encoding="utf-8")
    assert not formal_gate.SORRY_TOKEN.search(pilot)
    assert not formal_gate.SORRY_TOKEN.search(glossary)
    # Closed form of LS-DER-042 eq. (30): exponents 2/3, 5/6, 3/2; constant 54; Γ(1/6).
    assert "(2 : ℝ) ^ ((2 : ℝ) / 3)" in glossary
    assert "(3 : ℝ) ^ ((5 : ℝ) / 6)" in glossary
    assert "Gamma (1 / 6)" in glossary
    assert "54 * π ^ ((3 : ℝ) / 2)" in glossary
    # 19-digit window and the explicit Γ(1/6) hypothesis.
    assert "Set.Ioo (0.0734069193060342710 : ℝ) 0.0734069193060342711" in pilot
    assert "5.5663160017802352042500" in pilot
    assert "Scientific effect: NONE" in pilot


# --------------------------------------------------------------------------- #
# Fail-closed behaviour (sandbox copies)
# --------------------------------------------------------------------------- #


def test_gate_fails_on_module_hash_drift(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    pilot = box / "formal" / "lean" / "Side24Formal" / "Side24Pilot.lean"
    pilot.write_text(pilot.read_text(encoding="utf-8") + "\n-- drift\n", encoding="utf-8")
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert any("hash mismatch" in p for p in report["problems"])
    assert any("receipt module hash stale" in n for notes in report["receipt_notes"].values() for n in notes)
    (entry,) = report["theorems"]
    assert entry["earned_status"] == "proved"  # no binding receipt → below kernel_checked


def test_pin_then_stale_receipt_still_fails_closed(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    pilot = box / "formal" / "lean" / "Side24Formal" / "Side24Pilot.lean"
    pilot.write_text(pilot.read_text(encoding="utf-8") + "\n-- drift\n", encoding="utf-8")
    proc = _run_gate(box, "--pin", "--json-stdout")
    # Hashes are re-pinned, but the receipt no longer binds → kernel_checked not earned.
    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert not any("hash mismatch" in p for p in report["problems"])
    assert any("declared kernel_checked but only earned proved" in p for p in report["problems"])


def test_gate_fails_on_sorry(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    pilot = box / "formal" / "lean" / "Side24Formal" / "Side24Pilot.lean"
    text = pilot.read_text(encoding="utf-8").replace(
        "theorem cPlanar_pos : 0 < cPlanar := by",
        "theorem cPlanar_pos : 0 < cPlanar := by\n  sorry\n  -- unreachable",
    )
    pilot.write_text(text, encoding="utf-8")
    _run_gate(box, "--pin")
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    (entry,) = json.loads(proc.stdout)["theorems"]
    assert entry["earned_status"] == "specified"


def test_gate_fails_when_receipt_has_sorryAx(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    rp = next((box / "formal" / "receipts").glob("*.json"))
    rec = _load(rp)
    rec["axioms"]["Side24Formal.cPlanar_decimal_enclosure"].append("sorryAx")
    _dump(rp, rec)
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert any("forbidden/undeclared axioms" in p and "sorryAx" in p for p in report["problems"])


def test_gate_fails_when_receipt_has_undeclared_axiom(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    rp = next((box / "formal" / "receipts").glob("*.json"))
    rec = _load(rp)
    rec["axioms"]["Side24Formal.cPlanar_pos"].append("Side24Formal.parentTheoremAssumed")
    _dump(rp, rec)
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    # Declaring the axiom explicitly re-admits it (scope made precise, as the roadmap prescribes).
    st = _load(box / "formal" / "formalization_status.json")
    st["theorems"][0]["explicit_axioms"] = ["Side24Formal.parentTheoremAssumed"]
    _dump(box / "formal" / "formalization_status.json", st)
    proc2 = _run_gate(box, "--json-stdout")
    assert proc2.returncode == 0, proc2.stderr


def test_gate_fails_when_negative_control_accepted(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    rp = next((box / "formal" / "receipts").glob("*.json"))
    rec = _load(rp)
    rec["negative_controls"][0]["outcome"] = "ACCEPTED"
    rec["negative_controls"][0]["exit_code"] = 0
    _dump(rp, rec)
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert any("negative control ACCEPTED" in n for notes in report["receipt_notes"].values() for n in notes)


def test_gate_fails_on_toolchain_or_mathlib_drift(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    (box / "formal" / "lean" / "lean-toolchain").write_text("leanprover/lean4:v4.20.0\n")
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    report = json.loads(proc.stdout)
    assert any("toolchain pin drift" in p for p in report["problems"])


def test_gate_fails_on_missing_blueprint_or_decl_reference(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    bp = box / "formal" / "blueprint" / "SIDE24-PILOT-001.md"
    bp.write_text(bp.read_text(encoding="utf-8").replace("cPlanar_decimal_enclosure", "cPlanar_decimal_enclosurX"))
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    assert any("blueprint does not reference lean decl cPlanar_decimal_enclosure" in p
               for p in json.loads(proc.stdout)["problems"])
    bp.unlink()
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    assert any("blueprint missing" in p for p in json.loads(proc.stdout)["problems"])


def test_gate_rejects_status_vocabulary_as_claim(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    sp = box / "formal" / "formalization_status.json"
    st = _load(sp)
    st["theorems"][0]["title"] = "coefficient bound — lemma_closed: true"
    _dump(sp, st)
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 1
    assert any("research-status vocabulary" in p for p in json.loads(proc.stdout)["problems"])


def test_schema_rejects_lemma_closed_true_and_bad_ladder() -> None:
    status = _load(STATUS)
    bad = copy.deepcopy(status)
    bad["lemma_closed"] = True
    assert any("lemma_closed" in e for e in formal_gate.validate_schema(bad))
    bad = copy.deepcopy(status)
    bad["theorems"][0]["formalization_status"] = "verified"
    assert any("formalization_status" in e for e in formal_gate.validate_schema(bad))
    bad = copy.deepcopy(status)
    bad["theorems"][0]["alignment_review"] = {"status": "distinct_reviewer"}
    assert any("requires 'reviewer'" in e for e in formal_gate.validate_schema(bad))
    bad = copy.deepcopy(status)
    bad["theorems"][0]["does_not_claim"] = []
    assert any("does_not_claim" in e for e in formal_gate.validate_schema(bad))


def test_distinct_reviewer_changes_lane_display_only(tmp_path: Path) -> None:
    box = _sandbox(tmp_path)
    sp = box / "formal" / "formalization_status.json"
    st = _load(sp)
    st["theorems"][0]["alignment_review"] = {"status": "distinct_reviewer", "reviewer": "example-org"}
    _dump(sp, st)
    proc = _run_gate(box, "--json-stdout")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    (entry,) = report["theorems"]
    assert entry["lane_display"] == "KERNEL_CHECKED / ALIGNMENT_REVIEWED"
    # Still no research-status effect.
    assert report["lemma_closed"] is False and report["flipped_anything"] is False


def test_parse_axiom_output() -> None:
    text = (
        "'Side24Formal.cPlanar_pos' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
        "'Foo.bar' does not depend on any axioms\n"
        "warning: something else\n"
    )
    parsed = formal_gate.parse_axiom_output(text)
    assert parsed == {
        "Side24Formal.cPlanar_pos": ["propext", "Classical.choice", "Quot.sound"],
        "Foo.bar": [],
    }


def test_formal_gate_workflow_contract() -> None:
    wf = (ROOT / ".github" / "workflows" / "formal-gate.yml").read_text(encoding="utf-8")
    assert "formal_gate.py" in wf
    assert "--run-lake" in wf
    assert "lake exe cache get" in wf
    assert "lean-toolchain" in wf
    assert "Scientific effect: NONE" in wf
    assert "schedule:" not in wf  # AGENTS.md: never enable scheduled workflows for R2-06 prose
    assert "ai-prover-cross-check" in wf
    assert "workflow_dispatch" in wf


@pytest.mark.skipif(shutil.which("lake") is None and not (Path.home() / ".elan/bin/lake").is_file(),
                    reason="Lean toolchain not installed")
def test_run_lake_reproduces_receipt(tmp_path: Path) -> None:
    """When Lean is present, a fresh --run-lake must reproduce the committed receipt."""
    out = tmp_path / "receipt.json"
    proc = subprocess.run(
        [sys.executable, str(GATE), "--run-lake", "--receipt-out", str(out), "--json-stdout"],
        capture_output=True, text=True, timeout=3600, check=False,
        env={**__import__("os").environ, "PATH": f"{Path.home()}/.elan/bin:" + __import__("os").environ["PATH"]},
    )
    assert proc.returncode == 0, proc.stderr
    fresh = _load(out)
    committed = _load(formal_gate.find_receipts(ROOT)[0])
    for key in ("toolchain", "mathlib_rev", "module_sha256", "axioms", "lake_build_exit_code", "axioms_exit_code"):
        assert fresh[key] == committed[key], key
    assert [c["outcome"] for c in fresh["negative_controls"]] == ["REJECTED", "REJECTED"]
