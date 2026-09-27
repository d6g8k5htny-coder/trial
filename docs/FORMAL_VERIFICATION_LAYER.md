# Formal verification layer (Layer 1) — design, status, and coordination note

**Batch 828 (2026-09-27).**  Owner directive (Dylan Roy, pre-approved: "implement
anything and everything … coordinate with all other agents and future agents
for all repositories"): extend the existing provenance-bound, scope-disciplined,
fail-closed verification system with a **formal layer** so that natural-language
proofs become *provenance-bound formal proofs that are also machine-checked*.

**Scientific effect: NONE.**  Nothing in this layer promotes, closes, or
discharges a claim, premise, prize or lemma.  `lemma_closed` stays `false`.
The research repo's own vocabulary already anticipates this layer:
`architecture/scientific_state/v1/VERIFICATION_LEVELS.json` defines **L5 =
proof-assistant checked** and states *"verification_level ≠ acceptance"*.
Layer 1 is the machinery that lets an entry *earn* L5 honestly.

---

## 1. What is kept (Layer 0 — unchanged)

| Existing asset | Where it lives | Role in the stack |
|---|---|---|
| Provenance binding (SHA-256 of frozen bodies, git SHAs, byte-level source projections) | `main` artifacts (`BODY_SHA256`, `_MANIFEST.jsonl`), trial `portable/*` | Layer 0 — identifies *which* bytes were checked |
| Scope discipline ("does not claim", reconnaissance memos, reopening conditions) | `main` DER artifacts §9–§10 | Layer 0 — becomes the **hypotheses** of Lean theorems |
| Hard gate (fail-closed CI, `guard_no_status_promotion.py`, math_status walls) | trial `ci.yml`, `main` `tools/math_status_check.py` | Layer 0 — unchanged; Layer 1 adds a second, independent gate |
| Verification museum / review-status display | `main` (review ledger, verification levels) | displays all lanes; Layer 1 supplies a `lane_display` string |
| Explicit AI-authorship labels, zero same-provider independence credit | every artifact header | carried into `alignment_review.author` |

## 2. What is added (Layer 1)

```
formal/
  lean/                      Lake project (Lean v4.19.0 + Mathlib c44e0c8e…, same pins as main's GP-FOR-192 recovery)
    Side24Formal/Glossary.lean       definitions behind glossary terms
    Side24Formal/Side24Pilot.lean    SIDE24-PILOT-001
    tools/PrintAxioms.lean           axiom audit
    controls/*.lean                  negative controls (kernel must REJECT)
  formalization_status.json  per-theorem ledger (status ladder, scope, review lane)
  formalization_status.schema.json
  blueprint/<ID>.md          informal ↔ formal alignment sheet
  receipts/*.json            lake-build receipts binding hashes + toolchain + axioms + controls
  GLOSSARY.md                program term → standard maths → Lean
scripts/formal_gate.py       fail-closed gate (static; --run-lake; --pin)
tests/test_formal_gate.py    proves the gate refuses unearned status
.github/workflows/formal-gate.yml   static gate → fresh-runner kernel check → optional AI-prover lane
```

### 2.1 Status ladder — earned, never declared

| `formalization_status` | Earned when | Museum lane string |
|---|---|---|
| `none` | — | — |
| `specified` | Lean declarations exist (the statement's hypotheses **are** the scope) | `SPECIFIED / AUTHOR_SIDE_CANDIDATE` |
| `proved` | + no `sorry` token in the module | `PROVED / AUTHOR_SIDE_CANDIDATE` |
| `kernel_checked` | + a **binding receipt**: `lake build` exit 0; module SHA-256s, toolchain and Mathlib rev identical to the tree; axioms ⊆ `{propext, Classical.choice, Quot.sound}` ∪ declared `explicit_axioms`; no `sorryAx`; every negative control REJECTED | `KERNEL_CHECKED / AUTHOR_SIDE_ALIGNMENT` |
| `kernel_checked` **and** `alignment_review.status = distinct_reviewer` | a reviewer from a different organization confirms the Lean statement says what the prose says | `KERNEL_CHECKED / ALIGNMENT_REVIEWED` |

The gate fails (exit 1) whenever the declared status exceeds the earned one.
`verification_level` in the gate report is `L5` only for `kernel_checked`,
else `L0` — an unchecked proof script is prose.

### 2.2 Hash check

`formal/formalization_status.json` pins `lean_source_sha256` per module; the
receipt pins the same hashes.  Editing a `.lean` file makes *both* stale:
`--pin` refreshes the ledger, but only a successful `--run-lake` refreshes the
receipt.  The checked artifact is therefore always exactly the committed one.

### 2.3 Blueprint alignment (the "does the Lean say what I think" problem)

`formal/blueprint/<ID>.md` quotes the informal statement verbatim (with the
frozen-body SHA-256), lists every Lean declaration, and spells out the
alignment items a distinct reviewer must confirm plus the scope dispositions
where formal and informal differ.  The gate checks that every `lean_decl` is
referenced and that the source hash is cited.  Upgrading to full
`leanblueprint` (LaTeX + plasTeX dependency graph) is a drop-in later step; the
Markdown sheet carries the same fields.

### 2.4 Handling the specific challenges from the roadmap

| Challenge | How Layer 1 handles it |
|---|---|
| Non-standard terminology | `formal/GLOSSARY.md`: every term → standard object → Lean name, with a **source artifact** per row.  Terms with no sourced definition ("elder density", "candidate density", "Universal Law mathematics", Hermite-coefficient wording) are marked **UNMAPPED** and may not appear in a formal statement until sourced. |
| Parent-theorem dependencies | Either formalize first, or add a Lean `axiom` and list it in `explicit_axioms` with a blueprint scope note ("assumed; not independently verified").  The gate admits *declared* axioms only; undeclared ones fail. |
| Numerical bounds | Exact rationals + `norm_num`.  Pilot: 25-digit rational enclosures of `2^(2/3)`, `3^(5/6)`, `π^(3/2)` proved from integer-power inequalities; π from Mathlib's `pi_gt_d20/pi_lt_d20`. |
| AI authorship | `alignment_review.author` records the generating agent; status stays `author_side` until a distinct reviewer signs.  The reviewer checks the *statement*, not the proof. |
| Transcendental inputs Mathlib lacks | Made **explicit hypotheses** (`hypotheses_are_scope`), e.g. the 22-digit `Γ(1/6)` enclosure in the pilot. |

## 3. Pilot result — SIDE24-PILOT-001

Informal source: `LS-DER-042-v1.0` eq. (30)–(31), THEOREM 8.1 (frozen body
`54cedb1e…`, 7073 bytes — recomputed equal to the artifact's declared
`BODY_SHA256`).

| Lean declaration | Statement | Kernel |
|---|---|---|
| `cPlanar` | `2^(2/3)·3^(5/6)·Γ(1/6)/(54·π^(3/2))` | def |
| `cPlanar_pos` | `0 < cPlanar` (positivity half of THEOREM 8.1) | ✔ unconditional |
| `cPlanar_mem_Icc_of_factor_bounds` | factor enclosures ⇒ enclosure of `cPlanar` | ✔ unconditional |
| `two_rpow_two_thirds_bounds`, `three_rpow_five_sixths_bounds`, `pi_rpow_three_halves_bounds` | 25-digit rational enclosures | ✔ unconditional |
| `cPlanar_decimal_enclosure` | given `Γ(1/6) ∈ [5.5663160017802352042500, …501]`: `0.0734069193060342710 < cPlanar < 0.0734069193060342711` | ✔ conditional on `hΓ` |

Axioms for all 13 declarations: `[propext, Classical.choice, Quot.sound]`; no
`sorryAx`.  Negative controls `Mutant_WindowShift` (+1 ulp) and
`Mutant_WrongDenominator` (`54→56`) are rejected by the kernel.

**Scope disposition found by the pilot ("see what breaks"):** the roadmap's
20-digit example window is *not* provable — Mathlib knows π to 20 decimals,
which yields an enclosure of width ≈ 3.5e-22 that misses the 20th digit.  The
formal statement is loosened to 19 digits and the gap is recorded, not hidden.
Recovering the digit requires a sharper kernel-checked π bound (follow-on).

**Does not claim:** `c_24`, `576·c_24`, the periodization correction or its
sign, limit interchange, correctness of the derivation (1)–(29), or any status.

## 4. Extended hard gate

* `formal-gate.yml` job 1 runs the static gate on every PR touching
  `formal/**` — no Lean needed, fails closed.
* Job 2 installs the pinned toolchain on a **fresh runner**, runs
  `--run-lake`, and requires the committed receipt to reproduce (toolchain,
  Mathlib rev, module hashes, axioms, control outcomes).
* Job 3 (`workflow_dispatch` only) is the **AI-prover cross-check lane**: a
  caller-supplied prover writes `crosscheck/Generated.lean`; the same kernel
  checks it; the outcome is recorded in `ai_prover_cross_check` as an
  *additional* lane — never as acceptance.
* No `schedule:` trigger (AGENTS.md / R2-06).

The existing `ci.yml` is untouched; its `research-stack-status-guard` remains
the Layer 0 promotion wall.  Layer 1 adds a criterion; it removes none.

## 5. Other systems

| System | Position |
|---|---|
| **Lean 4 + Mathlib** | primary backend (pins shared with `main`'s GP-FOR-192 recovery) |
| **Coq** | optional; statements-only mirror acceptable; not required for core verification |
| **Metamath** | skip unless an external requirement appears |
| **AlphaProof / Goedel-Prover / DeepSeek-Prover** | lane 3 cross-check; same kernel decides |
| **Peer review** | papers in glossary-standard language; Lean project as supplementary material; reviewers assess significance + alignment, kernel guarantees logic |

## 6. Roadmap status

| Step | Status |
|---|---|
| 1 Pilot (SIDE24 coefficient bound) | **done** — kernel-checked, author-side alignment |
| 2 Glossary | **done (v1)** — 5 mapped, 8 schedulable, 5 UNMAPPED rows flagged |
| 3 Formalization review lane | **defined** — `alignment_review` field + reviewer checklist in blueprint; no distinct reviewer has signed yet |
| 4 CI integration | **done** — `formal-gate.yml` + `formal_gate.py` |
| 5 Expand (next theorems) | candidates: `c_24` via periodized kernel (LS-DER-041/043); `−1/3` fold law scalar algebra (LS-DER-046, reusing GP-FOR-189 `foldPotential`); sharper π bound to recover the 20th digit |
| 6 External validation | not started (owner decision; this sandbox cannot submit) |
| 7 AI-prover cross-check | lane exists (`workflow_dispatch`); `NOT_RUN` |

## 7. Coordination — what every agent (Cursor, ChatGPT/Codex, Claude, Grok, future) must know

1. **Layer 1 lives in `trial/formal/`** until the owner lands it on `main`
   (portable handoff: `portable/formal-layer/`).  Do not create a second,
   divergent Lean project elsewhere; extend this one.
2. **Never declare status upward.**  Edit `formalization_status.json` only to
   add entries at `specified`, then let `scripts/formal_gate.py --run-lake`
   earn `proved` / `kernel_checked`.  A PR whose gate fails is not mergeable.
3. **Hypotheses are the scope.**  Anything not in the Lean hypotheses is not
   claimed; anything Mathlib lacks becomes an explicit hypothesis or a
   declared axiom with a blueprint note.
4. **Glossary first.**  No formal statement may use a term absent from
   `formal/GLOSSARY.md`; UNMAPPED rows must be sourced before use.
5. **Pins are shared.**  Lean `v4.19.0` / Mathlib `c44e0c8e…` match the
   research repo's recovered bundle; change both trees together or not at all.
6. **Same-provider = zero independence credit** (unchanged program rule).  An
   AI-generated Lean proof is `author_side` until a distinct reviewer signs
   the *alignment*; the kernel already did the logic.
7. **Scientific effect stays NONE.**  L5 is evidence metadata.  `lemma_closed`,
   prizes, premises, obligations and review-ledger rows on `main` are never
   touched from this layer.  A green `trial` run is not research evidence.
