# `formal/` — Layer 1: formal specification and proof (Lean 4 + Mathlib)

This directory adds a **machine-checked lane** to the program's verification
stack.  Layer 0 (provenance hashes, scope discipline, no-status-promotion
gate, verification museum) is untouched; Layer 1 sits on top of it.

**Scientific effect: NONE.**  `lake build` going green is a kernel check of
the statements in this directory.  It is not claim promotion, lemma closure,
prize status or premise discharge on `d6g8k5htny-coder/main`
(`lemma_closed` stays `false`).  Full design: [`docs/FORMAL_VERIFICATION_LAYER.md`](../docs/FORMAL_VERIFICATION_LAYER.md).

## Layout

| Path | Purpose |
|------|---------|
| `lean/` | Lake project `side24formal` (Lean `v4.19.0`, Mathlib `c44e0c8e…` — same pins as the research repo's recovered GP-FOR-192 bundle) |
| `lean/Side24Formal/Glossary.lean` | Lean definitions behind glossary terms (`cPlanar`, …) |
| `lean/Side24Formal/Side24Pilot.lean` | pilot theorem **SIDE24-PILOT-001** and helpers |
| `lean/tools/PrintAxioms.lean` | axiom audit (`#print axioms` for every theorem) |
| `lean/controls/` | negative controls — semantic mutants the kernel must **reject** |
| `formalization_status.json` | per-theorem ledger: status ladder, scope, hypotheses, review lane |
| `formalization_status.schema.json` | JSON Schema for the ledger |
| `blueprint/<ID>.md` | informal ↔ formal alignment sheet per theorem |
| `receipts/` | `lake build` receipts that *bind* module hashes + toolchain + axioms + controls |
| `GLOSSARY.md` | program term → standard mathematics → Lean name |

## Quick check (no Lean needed)

```bash
python3 scripts/formal_gate.py          # fail-closed: hashes, ladder, receipts, blueprint
```

## Full check (Lean needed; ~1 min after Mathlib cache)

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.19.0
export PATH="$HOME/.elan/bin:$PATH"
cd formal/lean && lake exe cache get && cd ../..
python3 scripts/formal_gate.py --run-lake --receipt-out formal/receipts/lake-build-side24-pilot-001.json
```

## Status ladder (earned, never declared upward)

`none → specified → proved → kernel_checked`

* **specified** — the Lean statement exists (hypotheses **are** the scope).
* **proved** — proof script has no `sorry` (still author-side text).
* **kernel_checked** — a receipt binds the current source hashes, toolchain,
  Mathlib revision, `lake build` exit 0, axioms ⊆ `{propext, Classical.choice,
  Quot.sound}` ∪ declared explicit axioms, no `sorryAx`, and all negative
  controls REJECTED.

`kernel_checked` maps to **L5** in the research repo's
`architecture/scientific_state/v1/VERIFICATION_LEVELS.json` vocabulary — and
that file's rule applies verbatim: *"verification_level ≠ acceptance"*.

## Editing a Lean file

Any change to a module invalidates the receipt (hash mismatch → gate FAIL).
Re-pin and re-run:

```bash
python3 scripts/formal_gate.py --pin
python3 scripts/formal_gate.py --run-lake --receipt-out formal/receipts/lake-build-<id>.json
```
