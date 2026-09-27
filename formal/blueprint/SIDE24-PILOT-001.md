# Blueprint — SIDE24-PILOT-001

Lightweight blueprint (Lean Blueprint style, Markdown instead of LaTeX) that
pins the **informal** statement to the **formal** Lean declarations so a
distinct reviewer can check *alignment* (does the Lean say what the prose
says?) without re-proving anything — the kernel already did that.

`scripts/formal_gate.py` checks that every `lean_decl` listed here exists in
the Lean module and that the informal-source frozen-body hash is cited.

**Scientific effect: NONE.** `lemma_closed` stays `false`.

---

## Informal source (Layer 0 provenance)

| Field | Value |
|-------|-------|
| Repo / branch | `d6g8k5htny-coder/main` @ `chatgpt/drive-github-hardening-20260919` |
| Artifact | `LS-DER-042-v1.0 — Closed-Form Planar Bargmann–Fock Short-Lifetime Coefficient` |
| Frozen body | between `BEGIN_PLANAR_COEFFICIENT_FROZEN_BODY` / `END_PLANAR_COEFFICIENT_FROZEN_BODY`, 7073 bytes |
| Frozen body SHA-256 | `54cedb1eba9d72648619468beed9b8870bb3d28dbe206805dc72b4f796557cf3` (recomputed = declared `BODY_SHA256`) |
| Export file SHA-256 | `6a24c1af04b1b4fdc482baf09e97da953284d3381853be09e2bbad4baacef25b` |
| Informal status as recorded | COMPLETE CLOSED-FORM COEFFICIENT CANDIDATE / REVIEW DEFERRED; same-OpenAI-family; independence credit ZERO |

### Informal statement (verbatim, eq. (30)–(31), THEOREM 8.1)

> c_∞ = 2^(2/3) 3^(5/6) Γ(1/6) / [54 π^(3/2)]  (30)
>
> c_∞ = 0.0734069193060342710301359629577740500…  (31)
>
> THEOREM 8.1 — Under the exact directed all-typed contact convention and
> ordinary per-unit-area normalization, the planar Bargmann–Fock
> short-lifetime coefficient is the constant in (30), finite and strictly
> positive.

Cross-check: `LS-DATA-043B-v1.0` field `c_planar_closed` =
`0.073406919306034271030135962957774050017664244684…` (220 dps) — agrees with
an independent 60-digit `mpmath` evaluation of (30) performed while building
this pilot.

---

## Formal statements (Layer 1)

Module: `formal/lean/Side24Formal/Glossary.lean`, `formal/lean/Side24Formal/Side24Pilot.lean`

| Informal object | Lean declaration | Kind | Kernel status |
|-----------------|------------------|------|---------------|
| c_∞, eq. (30) | `cPlanar` | `def : ℝ` | definition |
| "finite and strictly positive" (THEOREM 8.1, positivity half) | `cPlanar_pos : 0 < cPlanar` | theorem, unconditional | kernel-checked |
| enclosure propagation (monotonicity of (30) in its factors) | `cPlanar_mem_Icc_of_factor_bounds` | theorem, unconditional | kernel-checked |
| 2^(2/3) to 25 digits | `two_rpow_two_thirds_bounds` | theorem, unconditional | kernel-checked |
| 3^(5/6) to 25 digits | `three_rpow_five_sixths_bounds` | theorem, unconditional | kernel-checked |
| π^(3/2) to 25 digits (from Mathlib `Real.pi_gt_d20` / `Real.pi_lt_d20`) | `pi_rpow_three_halves_bounds` | theorem, unconditional | kernel-checked |
| decimal expansion eq. (31), first 19 digits | `cPlanar_decimal_enclosure` | theorem, **conditional** on `hΓ` | kernel-checked given `hΓ` |

### Alignment notes a distinct reviewer must confirm

1. `cPlanar` uses exponents `2/3`, `5/6`, `3/2`, base constants `2`, `3`, `π`,
   `Real.Gamma (1/6)`, and denominator constant `54` — exactly eq. (30).
   No unordered-pair `1/2`, no torus-area factor (LS-DER-042 §9 firewall).
2. The window in `cPlanar_decimal_enclosure` is
   `(0.0734069193060342710, 0.0734069193060342711)` — the first 19
   significant digits of eq. (31).
3. The hypothesis `hΓ : Γ(1/6) ∈ [5.5663160017802352042500,
   5.5663160017802352042501]` is the **entire** unverified input.  Its value
   (`5.566316001780235204250096…`) was produced author-side with `mpmath`
   at 60 digits; Mathlib carries no bound on `Γ(1/6)`.

### Scope dispositions

* **Loosened window.** The roadmap's example
  `0.07340691930603427103 < c < 0.07340691930603427104` (20 digits) is *not*
  provable from Mathlib's 20-decimal π bounds: the derived enclosure has width
  ≈ 3.5e-22 and its lower end (≈ …7102988) falls below `…71030`.  The formal
  statement is loosened to 19 digits.  Recovering the 20th digit needs a
  sharper kernel-checked π bound (or π^(3/2) enclosure) — a follow-on item,
  not a hidden gap.
* **Derivation not formalized.** Steps (1)–(29) of the frozen body (pin
  covariance, Gaussian integrals, angular reduction) are not in Lean.  The
  pilot formalizes the *constant* and its numerics, not the *model*.

### Does not claim

* the exact finite side-24 torus coefficient `c_24` or `576·c_24` (`LS-DER-043`);
* the periodization correction or its sign (`LS-DER-044/045/059/062/063`);
* commutation of `L → ∞` and `ℓ → 0`;
* any research status: `lemma_closed`, prizes, premises, obligations, review
  ledger rows on `d6g8k5htny-coder/main` are untouched.

---

## Negative controls (semantic mutants; kernel must reject)

| Control | Mutation | Expected |
|---------|----------|----------|
| `controls/Mutant_WindowShift.lean` | window shifted +1 ulp | REJECTED |
| `controls/Mutant_WrongDenominator.lean` | `54 → 56` (simulated wrong Jacobian factor, §10 reopening condition) | REJECTED |

---

## Review lanes for this entry

| Lane | Status |
|------|--------|
| Layer 0 provenance (hash of informal frozen body) | bound (`54cedb1e…`) |
| Layer 1 kernel check (`lake build`, axioms, controls) | see binding receipt in `formal/receipts/` |
| Alignment review (statement matches prose) | **author_side** — a distinct reviewer has not signed |
| AI-prover cross-check | NOT_RUN |
| Research-status effect | NONE |
