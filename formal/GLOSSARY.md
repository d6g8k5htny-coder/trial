# Formal glossary — program terminology → standard mathematics → Lean

Layer 1 requirement: **every non-standard program term used in a formal
statement must map to a standard mathematical object**, and that object must
have (or be scheduled for) a Lean definition.  A term that cannot be mapped is
either ill-defined or genuinely novel; novelty must then be justified against
the literature, not assumed.

Rules for this file:

* Each row cites the **source artifact** on `d6g8k5htny-coder/main`
  (hardening branch mirror under `drive/mirrors/…`) from which the standard
  definition was read.  No definition is invented here.
* `Lean` column: a declaration in `formal/lean/Side24Formal/`, or
  `UNMAPPED` (no Lean object yet) with the reason.
* Status words (`lemma_closed`, prize, discharge…) never appear as claims.
  **Scientific effect: NONE.**

Legend for the mapping column: **mapped** (Lean def exists), **schedulable**
(standard object identified, Lean def not yet written), **UNMAPPED** (no
sourced standard definition located — do not use in a formal statement until
sourced).

---

## A. Objects the pilot formalizes

| Program term | Standard mathematics | Source (artifact) | Lean | Mapping |
|---|---|---|---|---|
| planar Bargmann–Fock field | centered stationary Gaussian random field on ℝ² with covariance `K(x,y) = exp(−(x²+y²)/2)` | LS-DER-042 eq. (1); LS-DER-041 eq. (3) | — (the *field* is not needed for the constant) | schedulable (Mathlib: `ProbabilityTheory`, Gaussian measures; no stationary GRF library yet) |
| planar short-lifetime coefficient `c_∞` / "c_infinity" / "planar coefficient" | the real constant `2^(2/3)·3^(5/6)·Γ(1/6)/(54·π^(3/2))`, defined as the per-unit-area leading coefficient of the short-lifetime first-moment density in the planar limit | LS-DER-042 eq. (30)–(31), THEOREM 8.1; LS-DER-041 (role as `L→∞` limit of `c_L`) | `Side24Formal.cPlanar` | **mapped** |
| "finite and strictly positive" (of `c_∞`) | `0 < c_∞ < ∞` (a real number, so finiteness is automatic; positivity is the theorem) | LS-DER-042 THEOREM 8.1 | `Side24Formal.cPlanar_pos` | **mapped** |
| torus-area / total normalization `C_L^tot = L²·c_L`; "576 c_24" | multiplication by the area `L²` of the flat torus `T_L² = (ℝ/Lℤ)²`; `24² = 576` | LS-DER-042 §7 eq. (32); LS-DER-043 eq. (268); LS-DATA-043B `c_24_total_576x` | `Side24Formal.torusAreaFactor`, `torusAreaFactor_24` | **mapped** (normalization only) |
| Γ(1/6) (as a numerical input) | Euler Gamma function at `1/6`; `Γ(1/6) = 5.566316001780235204250096…` | LS-DER-042 eq. (29) `I_κ = (1/12)·3^(7/6)·Γ(1/6)` | `Real.Gamma (1/6)` (Mathlib); enclosure only as hypothesis `hΓ` | mapped (value **not** kernel-bounded; see blueprint) |

## B. Objects named in the roadmap or the program that the pilot does *not* formalize

| Program term | Standard mathematics (as sourced) | Source (artifact) | Lean | Mapping |
|---|---|---|---|---|
| side-24 coefficient `c_24` / "exact fixed side-24 specific coefficient" | the analogue of `c_∞` for the centered stationary Gaussian field `f_24` on the flat torus `T_24²` with normalized periodized covariance `K_L(x₁,x₂) = k_L(x₁)k_L(x₂)`, `k_L(t) = Σₙ e^{−(t+nL)²/2} / Σₙ e^{−(nL)²/2}`, `L = 24` | LS-DER-041 eq. (1)–(2); LS-DER-043 (`c_L`, `c_24`, eq. 261–268); LS-DATA-043B `c_24_specific` (220 dps, "not a certified interval proof") | UNMAPPED | schedulable — needs periodized kernel + the angular reduction; `c_24 ≠ c_∞` is *stated* by the source, not formalized |
| periodization correction `c_24 − c_∞`; "certified negative side-24 sign" | difference of the two coefficients; the source reports relative interval `(−2.1824, −2.1823)×10⁻¹¹⁸` | LS-DER-043 header (successor LS-DER-045); LS-DER-044/045/059/062/063 | UNMAPPED | schedulable after `c_24` |
| lifetime / "short-lifetime" `ℓ` | persistence lifetime (birth value minus death value) of a finite non-essential superlevel-set `H₀` bar of the field | LS-DER-040 THEOREM 8.1 (eq. 29: `ν̄_all(ℓ) = c_all,spec·ℓ^(−1/3)(1+o(1))`) | UNMAPPED | schedulable (needs persistent homology of superlevel sets — not in Mathlib) |
| "lifetime coefficient" / `c_all,spec` | the constant in the `ℓ^(−1/3)` leading asymptotic of the first-moment density of lifetimes per unit area | LS-DER-040 eq. (29)–(30) | UNMAPPED | schedulable; in the planar limit it is `cPlanar` by LS-DER-041/042 (that identification is *not* formalized) |
| elder rule / "elder-rule death saddle" / elder maximum | standard persistent-homology elder rule: at an `H₀` merge of two superlevel components, the component whose maximum has the **smaller** value dies (the "younger" one); the surviving component's maximum is the "elder maximum" | LS-DER-035 §(47), Case II; LS-DER-051 (events `A_r`, `E_r`, `L_same,r`) | UNMAPPED | schedulable (sublevel/superlevel filtration of a Morse function) |
| "elder density" (roadmap wording) | *not found under that name in the mirror.*  Closest sourced object: the first-moment (Palm) density of maximum–saddle pairs **selected by the elder rule** — i.e. the conditional intensity of critical-point pairs given the elder-selection event `E_r` | LS-DER-051 (elder-selection cubic theorem `1 − p_r = O(r³)`), S2-DER-010 (persistence-pair point process, unit multiplicity) | UNMAPPED | **UNMAPPED** — term must be replaced by "elder-selected pair intensity" with an explicit citation before any formal use |
| "candidate density" (roadmap wording) | *not found as a mathematical term.*  In the corpus "candidate" is a **review status** ("same-family theorem candidate", "COMPLETE … CANDIDATE / REVIEW DEFERRED"), not a density | e.g. LS-DER-040 status line; LS-DER-042 "Authority: same-OpenAI-family theorem candidate only" | n/a | **UNMAPPED** — status vocabulary; never a formal object |
| "Universal Law mathematics" | *not found in the hardening mirror as a defined term* (GitHub description field of `main` reads "universal law"; the ALIGNED landing README speaks of the q0 / SIDE24 program). | `d6g8k5htny-coder/main` repo description; README | n/a | **UNMAPPED** — branding, not mathematics |
| minus-one-third law / fold-cancellation universality | dimension-independent exponent `−1/3` in `ν̄(ℓ) ∼ c·ℓ^(−1/3)`, derived from the `A₂` fold normal form `r dr = (6^(2/3)/3)·κ^(−2/3)·ℓ^(−1/3) dℓ` | LS-DER-046 eq. (17) | UNMAPPED | schedulable; the scalar `A₂` algebra is already Lean-checked upstream in `GP-FOR-189` (`foldPotential`, `ec005_fold_gap`) |
| Hermite / "lifetime coefficient as a Hermite-expansion coefficient" (roadmap wording) | *not sourced in the Theorem B folder*; `docs/CLOSURE_PIPELINE.md` links "Hermite checks" to obligation A1 only | CLOSURE_PIPELINE.md | n/a | **UNMAPPED** — do not use until an artifact defines it |
| RN-UNIF / `D3-LEMMA-RN-UNIF`, `OBL-H5-JETMOD` | research-program obligations (OPEN); not mathematical objects for this layer | PACKET / registers on `main` | n/a | out of scope — **never** touched by Layer 1 |

---

## C. Standard Mathlib objects the pilot relies on

| Mathlib object | Role |
|---|---|
| `Real.rpow` (`x ^ (y : ℝ)`), `Real.rpow_mul`, `Real.rpow_natCast`, `Real.rpow_le_rpow` | rational-exponent powers and their monotonicity |
| `Real.Gamma`, `Real.Gamma_pos_of_pos` | Γ(1/6) and its positivity |
| `Real.pi_gt_d20`, `Real.pi_lt_d20` | π to 20 decimals (the precision ceiling that forces the 19-digit window) |
| `norm_num` | exact rational arithmetic on the 25-digit enclosures |
| `div_le_div_iff₀`, `mul_le_mul`, `positivity`, `nlinarith` | order-arithmetic glue |

## D. How to extend

1. Add the row here **first** with its source artifact and standard definition.
2. Write the Lean `def` in `Glossary.lean` (docstring names the artifact + equation).
3. State the theorem in a new module; hypotheses = scope.
4. Add the entry to `formal/formalization_status.json` at `specified`, write
   `formal/blueprint/<ID>.md`, then let `scripts/formal_gate.py --run-lake`
   earn `proved` / `kernel_checked`.
5. Never edit the informal source; if the prose and the Lean disagree, record
   a scope disposition (as the 19- vs 20-digit window row does).
