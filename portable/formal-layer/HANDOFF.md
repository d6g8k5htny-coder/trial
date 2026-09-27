# Formal layer (Layer 1) — cross-repo / cross-agent handoff

**From:** `d6g8k5htny-coder/trial` Batch 828 (Cursor Cloud Agent, Claude).
**To:** every agent Dylan uses (Cursor, ChatGPT/Codex, Claude, Grok, future)
and every owner repo (`main`, `sandbox`, `google-drive`, `governance-`,
`Math-`, `meta-framework`, `query-`, `trial`).
**Authority:** owner directive 2026-09-27 — "implement anything and everything
… coordinate with all other agents and future agents for all repositories; I
Dylan Roy pre approve any decision, request, or action needed to achieve this
goal." No further approval is needed to adopt this handoff.

**Scientific effect: NONE.** This handoff moves no claim, premise, prize,
lemma or review status. `lemma_closed` stays `false`.

---

## 1. What changed and why

The program's verification system (provenance hashes, explicit scope,
review-status tracking, fail-closed no-promotion gate, verification museum)
lacked **logical verification** — the kind a proof-assistant kernel provides.
Layer 1 adds it without discarding anything:

* **Layer 0** (all of the above) stays as-is and becomes the *provenance* and
  *scope* input to Layer 1.
* **Layer 1** = Lean 4 + Mathlib formalization of definitions and theorem
  statements, kernel-checked proofs, a status ladder that is *earned* by a
  gate, a blueprint sheet tying prose ↔ Lean, a glossary mapping program
  terms → standard mathematics, a review lane for *alignment* (does the Lean
  say what the prose says), and an optional AI-prover cross-check lane.

The research repo already anticipated this: `main`'s
`architecture/scientific_state/v1/VERIFICATION_LEVELS.json` defines **L5 =
proof-assistant checked** and rules *"verification_level ≠ acceptance"*.
Layer 1 is how an entry earns L5 honestly.

## 2. Where it lives

Canonical location today: `d6g8k5htny-coder/trial` → `formal/`,
`scripts/formal_gate.py`, `.github/workflows/formal-gate.yml`,
`tests/test_formal_gate.py`, `docs/FORMAL_VERIFICATION_LAYER.md`.

Do **not** start a second, divergent Lean project in another repo. Extend
this one, or (owner) land it on `main` with `apply_to_repo.sh` below.

## 3. Pins every repo must share

| Component | Pin | Why |
|---|---|---|
| Lean | `leanprover/lean4:v4.19.0` | same as `main` `research/formal/candidates/LEAN_RECOVERY_VERIFICATION_20260920_v1.md` |
| Mathlib | `c44e0c8ee63ca166450922a373c7409c5d26b00b` | same as above (13 GP-FOR-192 theorems compile against it) |

Change both trees together or not at all.

## 4. Rules for agents (copy of `AGENTS_ADDENDUM.md`)

1. Status is **earned** by `python3 scripts/formal_gate.py` (`--run-lake`),
   never hand-declared. Ladder `none → specified → proved → kernel_checked`.
2. Editing a `.lean` file invalidates the receipt: run `--pin`, then
   `--run-lake`; commit the new receipt.
3. Hypotheses **are** the scope. Anything Mathlib lacks becomes an explicit
   hypothesis or a declared `explicit_axioms` entry with a blueprint note.
4. Every term in a formal statement must be a **sourced** row in
   `formal/GLOSSARY.md`. UNMAPPED rows may not be used.
5. `kernel_checked` = L5 **metadata**. It stays `author_side` until a
   **distinct-organization** reviewer signs the alignment in
   `formal/blueprint/<ID>.md`. Same-provider review = zero independence credit
   (unchanged program rule).
6. Never cite a green `lake build` / gate run as claim acceptance, closure,
   or discharge.
7. No `schedule:` triggers on formal workflows (R2-06 rule).

## 5. Pilot delivered

`SIDE24-PILOT-001` — `LS-DER-042` closed-form planar coefficient
`c_∞ = 2^(2/3)·3^(5/6)·Γ(1/6)/(54·π^(3/2))`:

* `cPlanar_pos : 0 < cPlanar` — unconditional, kernel-checked;
* `cPlanar_decimal_enclosure` — given an explicit 22-digit `Γ(1/6)`
  enclosure, `0.0734069193060342710 < c < 0.0734069193060342711`;
* axioms of all 13 declarations `= [propext, Classical.choice, Quot.sound]`,
  no `sorryAx`; two semantic mutants rejected by the kernel;
* scope disposition: the 20-digit window is *not* provable from Mathlib's
  20-decimal π; loosened to 19 digits and recorded.

## 6. Suggested next theorems (any agent may pick up; add at `specified`)

| Candidate | Source | Reuse |
|---|---|---|
| Sharper π bound → recover 20th digit | Mathlib `Real.pi` bounds / interval arithmetic | `cPlanar_mem_Icc_of_factor_bounds` |
| Fold scalar algebra of the `−1/3` law | `LS-DER-046` eq. (17) | `GP-FOR-189` `foldPotential`, `ec005_fold_gap` (already Lean-checked upstream) |
| Periodized kernel `k_L` and `c_24` definition | `LS-DER-041` eq. (1)–(2), `LS-DER-043` | new `Glossary.lean` defs; `c_24 ≠ c_∞` statement |
| Statement-only Coq mirror of `cPlanar` | optional | none |

## 7. Owner actions (optional, no gate)

* Land Layer 1 on `main`: `./portable/formal-layer/apply_to_repo.sh /path/to/main-clone`
  (copies `formal/`, gate, tests, workflow, docs; runs the static gate).
* Append `AGENTS_ADDENDUM.md` to each owner repo's `AGENTS.md` / `CLAUDE.md`
  (the script does this for the target clone with `--agents`).
* Nominate a **distinct-organization** alignment reviewer for
  `SIDE24-PILOT-001` (checklist in `formal/blueprint/SIDE24-PILOT-001.md`).
* Optionally dispatch `formal-gate.yml` with a `prover_command` to run the
  AI-prover cross-check lane.
