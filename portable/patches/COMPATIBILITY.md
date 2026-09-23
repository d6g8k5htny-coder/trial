# Portable patch compatibility matrix

Checked 2026-09-23 ~17:57 UTC (batch 17).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0005 (tip-cut) | `math_status_check` | Focused tests* |
|-----|-----|---------------------------|---------------------|----------------|
| hardening (post-#17) | `3e8f388` | OK | problems=0 | **86 passed** |
| hardening (post-#18) | `340d98a` | **0005 tip-cut fails**† | — | use `0005-pre17-…` |
| PR #19 head | `d47e44d` | OK | problems=0 | **86 passed** |
| PR #20 head | `c46463b` | **0005 tip-cut fails**‡ | problems=0 | **90 passed** with 0001–0004 + `0005-pre17` + **0006** |
| PR #17 head (merged) | `833ca55` / tip | tip-cut 0005 OK | problems=0 | 86 passed |
| PR #21 head | `d1e7d0e` | OK for 0001–0004; 0005 tip-cut N/A shape | problems=0 | **81 passed**¶ |

\* Default slice: `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py`

† Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-inventable-probes-restore-receipts-after-test.patch` instead (not in `apply_all.sh`).

‡ PR #20 is based on pre-#17 inventable test shape and also adds instrumentation STATUS tests. Stack: tip `apply_all` 0001–0004 + `0005-pre17` + optional **0006** (instrumentation restore). Do **not** put 0006 in `apply_all.sh` until #20 (or equivalent) lands on the hardening tip.

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- Batch **17** refreshes BASE_TIP to `3e8f388` (PR #17 fail-closed JETMOD shortcut refusals merged). Tip-cut 0005 restores receipts after the expanded test.
- Optional **0006** (`0006-instrumentation-status-restore-receipts-after-test.patch`): same dirty-digest class as 0005, for `tests/test_inventable_jetmod_instrumentation_status.py` on PR #20 only. Not in `apply_all.sh`.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` cases), not tip defects.
- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/`;
  portable **0002** remains necessary after that draft merges.
- PR #19 moved `837a2b4` → `d47e44d` (accepts tip-cut 0005).
- Default `main` alignment is independent (Path A/B); these patches are Path C.
