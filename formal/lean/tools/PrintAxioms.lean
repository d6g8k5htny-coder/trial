/-
Axiom audit for every theorem in the Side24Formal pilot.

Run (from `formal/lean`, after `lake build`):

    lake env lean tools/PrintAxioms.lean

`scripts/formal_gate.py --run-lake` parses the output.  A theorem is only
allowed to be recorded as `kernel_checked` when its axiom list is a subset of
`{propext, Classical.choice, Quot.sound}` plus any *declared* explicit axioms,
and `sorryAx` never appears.
-/
import Side24Formal

open Side24Formal

#print axioms Side24Formal.cPlanar
#print axioms Side24Formal.cPlanar_eq_div
#print axioms Side24Formal.torusAreaFactor_24
#print axioms Side24Formal.rpow_natDiv_le_of_pow_le
#print axioms Side24Formal.le_rpow_natDiv_of_pow_le
#print axioms Side24Formal.Gamma_one_sixth_pos
#print axioms Side24Formal.cPlanar_pos
#print axioms Side24Formal.cPlanarNumerator_pos
#print axioms Side24Formal.cPlanarDenominator_pos
#print axioms Side24Formal.cPlanar_mem_Icc_of_factor_bounds
#print axioms Side24Formal.two_rpow_two_thirds_bounds
#print axioms Side24Formal.three_rpow_five_sixths_bounds
#print axioms Side24Formal.pi_rpow_three_halves_bounds
#print axioms Side24Formal.cPlanar_decimal_enclosure
