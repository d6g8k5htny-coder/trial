/-
NEGATIVE CONTROL 2 — must FAIL to elaborate.

Semantic mutant of the closed form: the `LS-DER-042` §10 reopening condition
"the contact theorem carries a factor other than 1/6" is simulated by
replacing the denominator constant 54 with 56 (i.e. a wrong Jacobian factor).
The mutated constant is then claimed to lie in the *same* 19-digit window as
`cPlanar`.  It does not (the value moves by ≈ 3.6%), so `norm_num` must reject
the final step.
-/
import Side24Formal

namespace Side24Formal

open Real

noncomputable def MUTANT_cPlanar56 : ℝ :=
  (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) * Gamma (1 / 6)
    / (56 * π ^ ((3 : ℝ) / 2))

theorem MUTANT_wrong_denominator
    (hΓ : Gamma (1 / 6) ∈
      Set.Icc (5.5663160017802352042500 : ℝ) 5.5663160017802352042501) :
    MUTANT_cPlanar56 ∈ Set.Ioo (0.0734069193060342710 : ℝ) 0.0734069193060342711 := by
  obtain ⟨h₁l, h₁u⟩ := two_rpow_two_thirds_bounds
  obtain ⟨h₂l, h₂u⟩ := three_rpow_five_sixths_bounds
  obtain ⟨h₃l, h₃u⟩ := hΓ
  obtain ⟨h₄l, h₄u⟩ := pi_rpow_three_halves_bounds
  have hΓpos := Gamma_one_sixth_pos
  unfold MUTANT_cPlanar56
  constructor
  · rw [lt_div_iff₀ (by positivity)]
    nlinarith [mul_le_mul h₁l h₂l (by norm_num) (by positivity)]
  · rw [div_lt_iff₀ (by positivity)]
    nlinarith [mul_le_mul h₁u h₂u (by positivity) (by norm_num)]

end Side24Formal
