# Portable patch compatibility matrix

Checked 2026-09-23 ~18:22 UTC (batch 21).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0006 (tip-cut) | `math_status_check` | Focused tests* |
|-----|-----|---------------------------|---------------------|----------------|
| hardening (post-#20) | `1547ec4` | OK | problems=0 | **90 passed** |
| hardening (post-#17) | `3e8f388` | OK for 0001–0005; **0006 N/A**† | problems=0 | **86 passed** |
| hardening (post-#18) | `340d98a` | **0005 tip-cut fails**‡ | — | use `0005-pre17-…` |
| PR #19 head | `d47e44d` | OK 0001–0005; 0006 N/A until rebased | problems=0 | **86 passed** |
| PR #20 (merged) | `4103ee1` → tip | OK | problems=0 | **90 passed** |
| PR #21 head | `d1e7d0e` | OK for 0001–0004; 0005 tip-cut N/A shape | problems=0 | **81 passed**¶ |

\* Default slice @ `1547ec4`: carriers + math_status + inventable probes + gaussian + instrumentation STATUS.

† Pre-#20 tips lack `tests/test_inventable_jetmod_instrumentation_status.py`; omit 0006 or use an older `apply_all` listing.

‡ Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-…` (not in `apply_all.sh`).

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- Batch **21**: BASE_TIP → **`1547ec4`** (PR #20 merge). Promoted **0006** into `apply_all.sh`. CPython 3.11.16: problems=0 / lemma_closed=false / focused **90 passed** / probes clean. No tip-level **0007**. Open drafts: #19 CLEAN, #21 CLEAN; #2 still draft MERGEABLE/CLEAN.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` / workflow integrity cases), not tip defects.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
- Trial CI: portable-patches job now includes the instrumentation STATUS test.
