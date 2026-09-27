/-
# Side24Formal.Side24Pilot — pilot theorem SIDE24-PILOT-001

Layer 1 pilot chosen by the formal-layer roadmap: "one small theorem — the
SIDE24 coefficient bound".  The informal source is `LS-DER-042-v1.0`
THEOREM 8.1 (closed-form planar coefficient, "finite and strictly positive")
together with its decimal expansion eq. (31)
`0.0734069193060342710301359629577740500…`.

What is kernel-checked here, unconditionally:

* `cPlanar_pos` — the closed-form coefficient is strictly positive
  (the positivity half of THEOREM 8.1).
* `cPlanar_mem_Icc_of_factor_bounds` — a monotone enclosure lemma: rational
  enclosures of the four transcendental factors yield a rational enclosure
  of `cPlanar`.
* `two_rpow_two_thirds_bounds`, `three_rpow_five_sixths_bounds`,
  `pi_rpow_three_halves_bounds` — 25-digit rational enclosures of
  `2^(2/3)`, `3^(5/6)` and `π^(3/2)` (the last from Mathlib's
  `Real.pi_gt_d20` / `Real.pi_lt_d20`).

What is kernel-checked *conditionally* (hypotheses are the scope):

* `cPlanar_decimal_enclosure` — assuming a 22-digit rational enclosure of
  `Γ(1/6)` (Mathlib has no such bound; the hypothesis is an explicit,
  reviewable input), `cPlanar` lies in the 19-digit window
  `(0.0734069193060342710, 0.0734069193060342711)`.

Scope dispositions (recorded in `formal/blueprint/SIDE24-PILOT-001.md`):

* The roadmap's 20-digit example window is **not** formalized: with π known
  to 20 decimals in Mathlib the derived enclosure of `cPlanar` has width
  ≈ 3.5e-22, which does not fit inside the 20-digit window.  The formal
  statement is therefore loosened to 19 digits — a scope narrowing, stated
  explicitly rather than hidden.
* Nothing here is about the exact side-24 torus coefficient `c_24`, the
  periodization correction, limit interchange, or any research status.

Scientific effect: NONE.
-/
import Side24Formal.Glossary

namespace Side24Formal

open Real

/-! ## Helpers: rational enclosures of `x ^ (p / q)` via integer powers -/

/-- Upper bound: `x ^ p ≤ b ^ q` (naturals `p q`, `q ≠ 0`, `0 ≤ x, b`) gives
`x ^ (p / q) ≤ b`.  The premise is decidable rational arithmetic when `x, b` are
rational, so `norm_num` can discharge it. -/
theorem rpow_natDiv_le_of_pow_le {x b : ℝ} {p q : ℕ} (hx : 0 ≤ x) (hb : 0 ≤ b)
    (hq : q ≠ 0) (h : x ^ p ≤ b ^ q) : x ^ ((p : ℝ) / q) ≤ b := by
  have hq' : (q : ℝ) ≠ 0 := by exact_mod_cast hq
  calc x ^ ((p : ℝ) / q) = (x ^ p) ^ ((q : ℝ)⁻¹) := by
        rw [div_eq_mul_inv, Real.rpow_mul hx, Real.rpow_natCast]
    _ ≤ (b ^ q) ^ ((q : ℝ)⁻¹) :=
        Real.rpow_le_rpow (pow_nonneg hx p) h (by positivity)
    _ = b := by
        rw [← Real.rpow_natCast, ← Real.rpow_mul hb, mul_inv_cancel₀ hq', Real.rpow_one]

/-- Lower bound: `a ^ q ≤ x ^ p` gives `a ≤ x ^ (p / q)`. -/
theorem le_rpow_natDiv_of_pow_le {x a : ℝ} {p q : ℕ} (hx : 0 ≤ x) (ha : 0 ≤ a)
    (hq : q ≠ 0) (h : a ^ q ≤ x ^ p) : a ≤ x ^ ((p : ℝ) / q) := by
  have hq' : (q : ℝ) ≠ 0 := by exact_mod_cast hq
  calc a = (a ^ q) ^ ((q : ℝ)⁻¹) := by
        rw [← Real.rpow_natCast, ← Real.rpow_mul ha, mul_inv_cancel₀ hq', Real.rpow_one]
    _ ≤ (x ^ p) ^ ((q : ℝ)⁻¹) :=
        Real.rpow_le_rpow (pow_nonneg ha q) h (by positivity)
    _ = x ^ ((p : ℝ) / q) := by
        rw [div_eq_mul_inv, Real.rpow_mul hx, Real.rpow_natCast]

/-! ## Unconditional facts about `cPlanar` -/

theorem Gamma_one_sixth_pos : 0 < Gamma (1 / 6 : ℝ) :=
  Real.Gamma_pos_of_pos (by norm_num)

/-- Positivity half of `LS-DER-042` THEOREM 8.1: the closed-form planar
coefficient is strictly positive.  Unconditional, kernel-checked. -/
theorem cPlanar_pos : 0 < cPlanar := by
  unfold cPlanar
  have hΓ := Gamma_one_sixth_pos
  positivity

theorem cPlanarNumerator_pos : 0 < cPlanarNumerator := by
  unfold cPlanarNumerator
  have hΓ := Gamma_one_sixth_pos
  positivity

theorem cPlanarDenominator_pos : 0 < cPlanarDenominator := by
  unfold cPlanarDenominator
  positivity

/-- Monotone enclosure: rational enclosures of each factor of `cPlanar` give a
rational enclosure of `cPlanar`.  Unconditional, kernel-checked. -/
theorem cPlanar_mem_Icc_of_factor_bounds {a₁ b₁ a₂ b₂ a₃ b₃ a₄ b₄ : ℝ}
    (ha₁ : 0 ≤ a₁) (ha₂ : 0 ≤ a₂) (ha₃ : 0 ≤ a₃) (ha₄ : 0 < a₄)
    (h₁ : (2 : ℝ) ^ ((2 : ℝ) / 3) ∈ Set.Icc a₁ b₁)
    (h₂ : (3 : ℝ) ^ ((5 : ℝ) / 6) ∈ Set.Icc a₂ b₂)
    (h₃ : Gamma (1 / 6) ∈ Set.Icc a₃ b₃)
    (h₄ : π ^ ((3 : ℝ) / 2) ∈ Set.Icc a₄ b₄) :
    cPlanar ∈ Set.Icc (a₁ * a₂ * a₃ / (54 * b₄)) (b₁ * b₂ * b₃ / (54 * a₄)) := by
  obtain ⟨h₁l, h₁u⟩ := h₁
  obtain ⟨h₂l, h₂u⟩ := h₂
  obtain ⟨h₃l, h₃u⟩ := h₃
  obtain ⟨h₄l, h₄u⟩ := h₄
  have hΓ := Gamma_one_sixth_pos
  have hb₄ : 0 < b₄ := lt_of_lt_of_le ha₄ (le_trans h₄l h₄u)
  have hx₁ : 0 < (2 : ℝ) ^ ((2 : ℝ) / 3) := by positivity
  have hx₂ : 0 < (3 : ℝ) ^ ((5 : ℝ) / 6) := by positivity
  have hx₄ : 0 < π ^ ((3 : ℝ) / 2) := by positivity
  have hnum_le : a₁ * a₂ * a₃ ≤ (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) * Gamma (1 / 6) := by
    have h12 : a₁ * a₂ ≤ (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) :=
      mul_le_mul h₁l h₂l ha₂ hx₁.le
    exact mul_le_mul h12 h₃l ha₃ (by positivity)
  have hb₁ : 0 ≤ b₁ := le_trans ha₁ (le_trans h₁l h₁u)
  have hb₂ : 0 ≤ b₂ := le_trans ha₂ (le_trans h₂l h₂u)
  have hb₃ : 0 ≤ b₃ := le_trans ha₃ (le_trans h₃l h₃u)
  have hnum_ge : (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) * Gamma (1 / 6) ≤ b₁ * b₂ * b₃ := by
    have h12 : (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) ≤ b₁ * b₂ :=
      mul_le_mul h₁u h₂u hx₂.le hb₁
    exact mul_le_mul h12 h₃u hΓ.le (mul_nonneg hb₁ hb₂)
  unfold cPlanar
  constructor
  · -- a₁ a₂ a₃ / (54 b₄) ≤ N / (54 π^(3/2)):  cross-multiply.
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    have hden : 54 * π ^ ((3 : ℝ) / 2) ≤ 54 * b₄ := by nlinarith
    exact mul_le_mul hnum_le hden (by positivity) (by positivity)
  · rw [div_le_div_iff₀ (by positivity) (by positivity)]
    have hden : 54 * a₄ ≤ 54 * π ^ ((3 : ℝ) / 2) := by nlinarith
    exact mul_le_mul hnum_ge hden (by positivity) (mul_nonneg (mul_nonneg hb₁ hb₂) hb₃)

/-! ## 25-digit rational enclosures of the algebraic / π factors -/

/-- `2^(2/3) ∈ [1.5874010519681994747517056, 1.5874010519681994747517057]`. -/
theorem two_rpow_two_thirds_bounds :
    (2 : ℝ) ^ ((2 : ℝ) / 3) ∈
      Set.Icc (1.5874010519681994747517056 : ℝ) 1.5874010519681994747517057 := by
  have hl := le_rpow_natDiv_of_pow_le (x := (2 : ℝ)) (a := 1.5874010519681994747517056)
    (p := 2) (q := 3) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  have hu := rpow_natDiv_le_of_pow_le (x := (2 : ℝ)) (b := 1.5874010519681994747517057)
    (p := 2) (q := 3) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  exact ⟨by simpa using hl, by simpa using hu⟩

/-- `3^(5/6) ∈ [2.498049532966812958826359, 2.4980495329668129588263591]`. -/
theorem three_rpow_five_sixths_bounds :
    (3 : ℝ) ^ ((5 : ℝ) / 6) ∈
      Set.Icc (2.4980495329668129588263590 : ℝ) 2.4980495329668129588263591 := by
  have hl := le_rpow_natDiv_of_pow_le (x := (3 : ℝ)) (a := 2.4980495329668129588263590)
    (p := 5) (q := 6) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  have hu := rpow_natDiv_le_of_pow_le (x := (3 : ℝ)) (b := 2.4980495329668129588263591)
    (p := 5) (q := 6) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  exact ⟨by simpa using hl, by simpa using hu⟩

/-- `π^(3/2) ∈ [5.56832799683170784527779, 5.5683279968317078453043769]`,
from Mathlib's 20-decimal bounds `Real.pi_gt_d20` / `Real.pi_lt_d20`. -/
theorem pi_rpow_three_halves_bounds :
    π ^ ((3 : ℝ) / 2) ∈
      Set.Icc (5.56832799683170784527779 : ℝ) 5.5683279968317078453043769 := by
  have hpi_lo : (3.14159265358979323846 : ℝ) ≤ π := Real.pi_gt_d20.le
  have hpi_hi : π ≤ (3.14159265358979323847 : ℝ) := Real.pi_lt_d20.le
  constructor
  · calc (5.56832799683170784527779 : ℝ)
        ≤ (3.14159265358979323846 : ℝ) ^ ((3 : ℝ) / 2) := by
          have h := le_rpow_natDiv_of_pow_le (x := (3.14159265358979323846 : ℝ))
            (a := 5.56832799683170784527779) (p := 3) (q := 2)
            (by norm_num) (by norm_num) (by norm_num) (by norm_num)
          simpa using h
      _ ≤ π ^ ((3 : ℝ) / 2) := Real.rpow_le_rpow (by norm_num) hpi_lo (by norm_num)
  · calc π ^ ((3 : ℝ) / 2)
        ≤ (3.14159265358979323847 : ℝ) ^ ((3 : ℝ) / 2) :=
          Real.rpow_le_rpow Real.pi_pos.le hpi_hi (by norm_num)
      _ ≤ (5.5683279968317078453043769 : ℝ) := by
          have h := rpow_natDiv_le_of_pow_le (x := (3.14159265358979323847 : ℝ))
            (b := 5.5683279968317078453043769) (p := 3) (q := 2)
            (by norm_num) (by norm_num) (by norm_num) (by norm_num)
          simpa using h

/-! ## Pilot theorem SIDE24-PILOT-001 -/

/-- **SIDE24-PILOT-001.**  *Hypothesis = scope*: a 22-digit rational enclosure
of `Γ(1/6)` (value `5.566316001780235204250096…`), supplied externally because
Mathlib carries no numerical bound on `Γ(1/6)`.  *Conclusion*: the closed-form
planar coefficient of `LS-DER-042` eq. (30)–(31) lies strictly inside the
19-digit window `(0.0734069193060342710, 0.0734069193060342711)`.

Everything except the `Γ(1/6)` enclosure is discharged by the Lean kernel
(rational arithmetic via `norm_num`, monotonicity of `rpow`, Mathlib's π
bounds).  This theorem says nothing about the finite side-24 torus coefficient
`c_24`; see the module docstring for the full "does not claim" list. -/
theorem cPlanar_decimal_enclosure
    (hΓ : Gamma (1 / 6) ∈
      Set.Icc (5.5663160017802352042500 : ℝ) 5.5663160017802352042501) :
    cPlanar ∈ Set.Ioo (0.0734069193060342710 : ℝ) 0.0734069193060342711 := by
  have h := cPlanar_mem_Icc_of_factor_bounds (by norm_num) (by norm_num) (by norm_num)
    (by norm_num) two_rpow_two_thirds_bounds three_rpow_five_sixths_bounds hΓ
    pi_rpow_three_halves_bounds
  obtain ⟨hl, hu⟩ := h
  constructor
  · exact lt_of_lt_of_le (by norm_num) hl
  · exact lt_of_le_of_lt hu (by norm_num)

end Side24Formal
