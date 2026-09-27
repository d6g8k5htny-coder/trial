/-
NEGATIVE CONTROL 1 — must FAIL to elaborate.

Semantic mutant of `cPlanar_decimal_enclosure`: the 19-digit window is shifted
one unit in the last place upward, so the true value
`0.07340691930603427103…` is no longer inside it.  With the same `Γ(1/6)`
hypothesis the rational arithmetic cannot close and `norm_num` must reject
the lower-bound step.

`scripts/formal_gate.py --run-lake` records the exit code; a mutant that
compiles is a gate FAILURE (the pilot would be vacuous or the window too loose).
-/
import Side24Formal

namespace Side24Formal

open Real

theorem MUTANT_cPlanar_window_shift
    (hΓ : Gamma (1 / 6) ∈
      Set.Icc (5.5663160017802352042500 : ℝ) 5.5663160017802352042501) :
    cPlanar ∈ Set.Ioo (0.0734069193060342711 : ℝ) 0.0734069193060342712 := by
  have h := cPlanar_mem_Icc_of_factor_bounds (by norm_num) (by norm_num) (by norm_num)
    (by norm_num) two_rpow_two_thirds_bounds three_rpow_five_sixths_bounds hΓ
    pi_rpow_three_halves_bounds
  obtain ⟨hl, hu⟩ := h
  constructor
  · exact lt_of_lt_of_le (by norm_num) hl
  · exact lt_of_le_of_lt hu (by norm_num)

end Side24Formal
