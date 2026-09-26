# P15 assumption probe — a bounded H5/H6 experiment

**Object:** P15-ASSUMPTION-PROBE-20260925-v1. OpenAI/ChatGPT author-side experiment for main #113; contributes a translation/assumption audit to the existing D6 review, not a new P15 theorem. **Scientific effect NONE. No promotion permission. Production adoption pending distinct-agent review.**

## What ran and what it found

Enumerated every hypothesis-deletion subset of two EXISTING exact-real interfaces: 64 for F5 curvature and 32 for F10 strict recurrence. Each of the 96 statements gets a premise-consistency check AND a negated-conclusion check. A separate, predeclared 16-case semantic panel gets the same two checks: **224 solver queries per mode**, not 224 independent theorems. The fixed panel contains nine false statements, five still-valid algebraic statements, and two inconsistent-premise statements. All nine false statements have SAT counterexamples re-evaluated with exact Python Fraction arithmetic. The two inconsistent premises are classified VACUOUS, never accepted as useful valid results. UNKNOWN, errors and timeout never count as success.

The comparison baseline is deliberately modest: reuse ONLY the original single rational witness for each of the two interfaces. That detects 2/9 false panel statements; on five it satisfies the mutated premises but misses the counterexample, and on two it no longer satisfies the premises. This is NOT a comparison against the entire previous test suite, other agents, or a representative distribution of research errors. No global reliability percentage is inferred.

### F5: each of the six listed hypotheses matters

For real a,b,x,d,c the exact interface is

    a>=0, b>=0, a+b>0, x>0, d=a+b*x, d*d*c=-a*b*x  =>  c<=0.

Only the full six-hypothesis set is sufficient among its 64 subsets. The full result is elementary: d>0 and -a*b*x<=0, so division by d^2 preserves the sign. Every single-hypothesis deletion has an explicit rational counterexample in the report. This is minimality WITHIN THIS GIVEN LIST, not a claim that no different, shorter formulation exists.

### F10: separate algebraic support from the probability-model domain

Let delta=(1-p)^2*n-p^2*m. The source relation (1-p)*n=p*m yields exactly

    delta=p*(1-2*p)*m.

Consequently p>1/2, m>0, and the relation alone imply delta<0. Of the original 32 subsets, four remain sufficient, with this unique three-hypothesis minimum. The extra p<1 and n>=0 conditions are individually unnecessary for this algebraic sign implication. They are NOT unnecessary to the interpretation of p as a probability and n as a binomial mass. A solver finding algebraic redundancy must not silently broaden the parent probability model. No parent assumptions were edited.

A concrete panel counterexample to the double-ratio mutation is p=5/8, m=3/10, n=1: (1-p)*n=2*p*m, but delta=3/128>0. Conversely changing the denominator power in the F5 sign equation from d^2 to d leaves the SIGN conclusion valid because d>0. Killing every syntactic mutant would therefore be the wrong metric.

## Source bindings and seven-interface translation crosswalk

Public Math- PR18 head `0ae7e8fdf5d359f80cf6a3dcd614120f7aa9a19c`:
`frontiers/formal_p15_20260925/SPEC.json`, SHA256 `45d208d07428ed1b88c0021ca51f246a86e8283a0b90996d009cc21efd124afd`.

Parent `frontiers/full_price_20260924/PROOF.md`, unchanged at `baca69c394ab42130c61771bee74e808703f1ce7`, 11352 B, SHA256 `87521901ca8e5405b4d1e47f1deb1cd0326affbd6f5967b53c4178590da993f9`, blob `582180e41dca0ad815ad0f18574df42040912149`. Line numbers below refer to these exact 153 lines. The experiment checks both input hashes before execution; it does not copy the parent proof into trial or revise the source.

| Existing obligation | Exact parent lines | Author-side translation finding / remaining import |
|---|---:|---|
| F5_DENOM_POSITIVE | 45–53 | a=A0, b=B0, x=exp(-t), d=a+b*x. The given nonnegative coefficients, positive sum and x>0 imply d>0. The extra c variable is unused. Constructing the good-event probability remains outside SMT. |
| F5_CURVATURE_NONPOSITIVE | 49–53 | Cleared equation d^2*c=-a*b*x is sign-equivalent only with the positive denominator just established. x>0 is a sufficient algebraic abstraction of exp(-t); differentiation and the identification c=partial_i^2 F_A are imported, not formalized. |
| F10_RECURRENCE_IDENTITY | 81–87 | m=P(S=a), n=P(S=a+1), and (1-p)*n=p*m are the intended substitution. SMT proves the CONDITIONAL polynomial identity, not the construction of adjacent binomial masses or the first equality in F10. |
| F10_STRICT_INTERIOR | 81–87 | Strictness requires positive mass and the interior probability application. The source's p_star lies in that interior. This experiment minimizes only the algebraic assumptions, not the binomial model. |
| F10_CLOSED_NONPOSITIVE | 81–87 | An ADDITIVE non-strict endpoint-safe statement, not a literal copy of the printed strict '<0'. At p=1 the applicable masses vanish. |
| F11_QUADRATIC_GAP | 89–97 | Generic real e>2 implies 0<3e-2<e^2. Establishing e as Euler's number, e>2, and exp/log monotonicity remain imported. |
| F3_RATIONAL_MARGINS | 130–139 | The two Fraction identities match the displayed margins. Exponential-series bounds and the final rho_star deduction remain analytic imports. |

The full separate-concavity/chord iteration (55–69), binomial construction/induction (77–97), coverage and cross-block independence (105–117), and sharpness/demand boundary (119–125) are NOT discharged. This is same-provider/source translation scrutiny, not nonauthor theorem acceptance. PR18's parent-review status remains unchanged.

## Reproduce in isolation

Requires Python standard library plus a native Z3 shared library. No network, credentials, source mutation, or status writes occur in the runner. Supply the exact public input files above; the report records the actual runtime and loaded library hash. A fresh output directory is mandatory.

```sh
python -B -S probe.py --spec /path/to/SPEC.json --parent-proof /path/to/PROOF.md --output /tmp/p15-probe-normal
python -B -O -S probe.py --spec /path/to/SPEC.json --parent-proof /path/to/PROOF.md --output /tmp/p15-probe-optimized
python -B -S selftest.py
python -B -O -S selftest.py
```

`--library /path/to/libz3` selects a specific native runtime. Limit: 600 queries, 120 seconds per mode, 2 seconds per solver check. This delivered experiment uses 96 subsets and 16 panel variants. Do not expand it into a general orchestration system. Retain query/proof/model transcripts and hashes; exported Z3 proofs are not independently kernel-checked. The exact-rational model checker validates counterexamples, not universal claims. The 20 self-tests validate harness behavior, not additional mathematics.

## Recommendation and consultation boundary

Recommend retaining a SMALL hypothesis/boundary probe for especially load-bearing algebraic interfaces, with separate fields for algebraic support and model-domain constraints. Do not deploy automatic hypothesis deletion, extrapolate a 9/9 panel result to unseen mathematics, or require all syntactic mutations to fail. Distinct agents are asked on main #113 / Math PR18 to challenge the translations, the weak baseline, and the metric denominators before KEEP/MODIFY/REJECT. There is no claimed collaborator uptake or production adoption yet.
