# Portable patch compatibility matrix

Checked 2026-09-23 ~17:28 UTC (batch 15).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0004 | `math_status_check` | Focused tests* |
|-----|-----|-----------------|---------------------|----------------|
| hardening (post-#15) | `1ea0ae8` | OK | problems=0 | 84 passed |
| PR #18 head | `278822e` | OK | problems=0 | **86 passed** |
| PR #20 head | `c8ec3d1` | OK | problems=0 | 84 passed |
| PR #21 head | `d1e7d0e` | OK | problems=0 | **81 passed**† |

\* Default slice: `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py`

† PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/`;
  portable **0002** remains necessary after that draft merges.
- PR #21 does not touch `math_console.py` / `PACKET.json`; no 0002 regen needed.
- PR #16 (cold-start nav docs) **merged**; did not move hardening tip off `1ea0ae8`.
- Re-run this matrix when a merge edits `PACKET.json` or `math_console.py`.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
