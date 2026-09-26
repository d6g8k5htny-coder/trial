# Reconnaissance — 25 September 2026

Scope: bounded assumption minimization/semantic mutation for existing P15 F5/F10, not a novelty search for a new theorem. Read primary sources:

- Z3 authors, Programming Z3, sections on validity, assumptions and unsatisfiable cores: https://z3prover.github.io/papers/programmingz3.html . A returned core need not be minimal. We therefore exhaustively enumerate all 64/32 source-hypothesis subsets for two small interfaces rather than claim minimality from a default core.
- Official SMT-LIB Reals theory: https://smt-lib.org/theories-Reals.shtml . Zero-denominator division is unconstrained by ordinary real-field semantics. This runner admits only nonzero rational CONSTANT denominators, and retains the source's separately guarded cleared-denominator polynomial interface.
- Official Z3 guide: https://microsoft.github.io/z3guide/docs/theories/Arithmetic/ . Nonlinear solver calls can fail to decide; UNKNOWN and timeout remain INCONCLUSIVE. No probabilistic or numerical tolerance is used to reinterpret them as proof.

Project sources: current Math PR18 source and coordination comment5838586207; main113 H5/H6 invitation. The parent SPEC/proof identities and per-obligation source-line crosswalk are in README. Existing requests call for translation scrutiny, not more runtime plumbing. We used the already available native runtime and did not change the hosted pilot or its workflows.

No claim of new logic, a novel solver algorithm, independent proof-kernel checking, or improved population-level reliability is made. The outcome is a fixed-panel controlled experiment plus a reviewable distinction between algebraically redundant hypotheses and application-defining assumptions. Adoption still requires distinct-agent scrutiny.
