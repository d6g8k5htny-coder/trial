# Lean build receipts

Each `*.json` here is written by `scripts/formal_gate.py --run-lake` and has
`schema_id = trial.formal.lean_build_receipt.v1`.  A receipt **binds** a
`kernel_checked` status only while *all* of the following still hold:

* `module_sha256[*]` equals the SHA-256 of every module listed in
  `formal/formalization_status.json` (edit a `.lean` file → receipt is stale);
* `toolchain` equals `formal/lean/lean-toolchain` and the ledger's pin;
* `mathlib_rev` equals the `mathlib` entry in `formal/lean/lake-manifest.json`;
* `lake_build_exit_code == 0` and `axioms_exit_code == 0`;
* every declaration's `axioms` ⊆ `{propext, Classical.choice, Quot.sound}` ∪
  the entry's `explicit_axioms`, and never `sorryAx`;
* every negative control has `outcome == "REJECTED"`.

A receipt is a **local execution record** (same wording as the research repo's
recovered-Lean note): it is not an authenticated timestamp and not independent
review.  CI (`.github/workflows/formal-gate.yml`) re-runs `lake build` on a
fresh runner and uploads its own receipt as an artifact for comparison.

Scientific effect: NONE.
