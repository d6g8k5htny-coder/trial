/-
# Side24Formal.Glossary — formal definitions behind the program glossary

Layer 1 (formal specification) of the q0 / SIDE24 verification stack.
Every definition here is the Lean object that a non-standard program term
maps to in `formal/GLOSSARY.md`.  The docstring of each definition names the
informal source artifact (Drive / `d6g8k5htny-coder/main` mirror) and the
equation it formalizes, so the informal ↔ formal link is auditable byte-wise.

Scientific effect: NONE.  A definition compiling is not a claim, and a theorem
compiling downstream is not lemma closure, prize status, or premise discharge
on the research program.  Formal status is tracked separately in
`formal/formalization_status.json` and gated by `scripts/formal_gate.py`.
-/
import Mathlib

namespace Side24Formal

noncomputable section

open Real

/-- **Planar Bargmann–Fock short-lifetime coefficient** `c_∞` in closed form.

Informal source: `LS-DER-042-v1.0 — Closed-Form Planar Bargmann–Fock
Short-Lifetime Coefficient`, frozen body eq. (30):

    c_∞ = 2^(2/3) · 3^(5/6) · Γ(1/6) / (54 · π^(3/2)).

Glossary: "planar coefficient" / "c_infinity" / "short-lifetime coefficient
per unit ordinary area" → this real number.  It is *not* the exact finite
side-24 torus coefficient `c_24` (see `LS-DER-043`), which the source states is
"exponentially close but mathematically distinct". -/
def cPlanar : ℝ :=
  (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) * Gamma (1 / 6)
    / (54 * π ^ ((3 : ℝ) / 2))

/-- The numerator factor `2^(2/3) · 3^(5/6) · Γ(1/6)` of `cPlanar`. -/
def cPlanarNumerator : ℝ :=
  (2 : ℝ) ^ ((2 : ℝ) / 3) * (3 : ℝ) ^ ((5 : ℝ) / 6) * Gamma (1 / 6)

/-- The denominator factor `54 · π^(3/2)` of `cPlanar`. -/
def cPlanarDenominator : ℝ := 54 * π ^ ((3 : ℝ) / 2)

theorem cPlanar_eq_div : cPlanar = cPlanarNumerator / cPlanarDenominator := rfl

/-- **Side-24 total coefficient normalization.**  Informal source
`LS-DER-042` §7 / `LS-DATA-043B` field `c_24_total_576x`: the total leading
coefficient on a side-`L` torus is `L² · c_L`.  For `L = 24` the area factor
is `576`.  This is a *definition of the normalization*, not a theorem about
`c_24`; `c_24` itself is not defined in this pilot (see GLOSSARY: UNMAPPED). -/
def torusAreaFactor (L : ℕ) : ℝ := (L : ℝ) ^ 2

theorem torusAreaFactor_24 : torusAreaFactor 24 = 576 := by
  unfold torusAreaFactor; norm_num

end

end Side24Formal
