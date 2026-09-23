# Portable patch compatibility matrix

Checked 2026-09-23 ~18:05 UTC (batch 18).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0005 (tip-cut) | `math_status_check` | Focused tests* |
|-----|-----|---------------------------|---------------------|----------------|
| hardening (post-#17) | `3e8f388` | OK | problems=0 | **86 passed** |
| hardening (post-#18) | `340d98a` | **0005 tip-cut fails**† | — | use `0005-pre17-…` |
| PR #19 head | `d47e44d` | OK (batch 17) | problems=0 | **86 passed** |
| PR #20 head | `4103ee1` | OK (tip-cut 0005)‡ | problems=0 | **90 passed** with 0001–0005 + **0006** |
| PR #17 head (merged) | `833ca55` / tip | tip-cut 0005 OK | problems=0 | 86 passed |
| PR #21 head | `d1e7d0e` | OK for 0001–0004; 0005 tip-cut N/A shape | problems=0 | **81 passed**¶ |

\* Default slice: `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py` (+ instrumentation on #20).

† Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-inventable-probes-restore-receipts-after-test.patch` instead (not in `apply_all.sh`).

‡ PR #20 moved `c46463b` → **`4103ee1`**. Tip-cut **0005** now applies; `0005-pre17` does **not**. Still needs optional **0006** for instrumentation STATUS dirty digests. Do **not** put 0006 in `apply_all.sh` until #20 (or equivalent) lands on the hardening tip — see patches README “When to promote 0006”.

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- Batch **18** reconfirms BASE_TIP `3e8f388` (unchanged). No tip-level **0007** — broader workflow-integrity failures are host `python` missing on PATH, not tip defects.
- Optional **0006** remains PR #20-only until instrumentation STATUS tests exist on the hardening tip.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` / workflow integrity cases), not tip defects.
- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/` until **0002** is applied.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
