# Portable patch compatibility matrix

Checked 2026-09-23 ~17:19 UTC.
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0004 | `math_status_check` | Focused tests* |
|-----|-----|-----------------|---------------------|----------------|
| hardening (post-#15) | `1ea0ae8` | OK | problems=0 | 84 passed |
| PR #18 head | `278822e` | OK | problems=0 | **86 passed** |
| PR #20 head | `c8ec3d1` | OK | problems=0 | 84 passed |

\* `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py`

Notes:

- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/`;
  portable **0002** remains necessary after that draft merges.
- Re-run this matrix when a merge edits `PACKET.json` or `math_console.py`.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
