# Portable patch compatibility matrix

Checked 2026-09-23 ~17:45 UTC (batch 16).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0004 | `math_status_check` | Focused tests* |
|-----|-----|-----------------|---------------------|----------------|
| hardening (post-#18) | `340d98a` | OK | problems=0 | **86 passed** |
| hardening (post-#15) | `1ea0ae8` | OK | problems=0 | 84 passed |
| PR #18 head (pre-merge) | `278822e` | OK | problems=0 | **86 passed** |
| PR #20 head | `dc3eeb0` | OK (batch 15: `c8ec3d1`) | problems=0 | 84 passed |
| PR #21 head | `d1e7d0e` | OK | problems=0 | **81 passed**† |

\* Default slice: `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py`

† PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- Working tip moved off `1ea0ae8` → `340d98a` via PR #16 (docs) + PR #18 (PARTIAL/REFUSED STATUS vocab). **No new portable patch (0005) in batch 16** — known 0001–0004 defects still reproduce; no additional engineering defect found.
- Broad local pytest on tip+patches: many failures are **agent-host env** (`python` missing in bare bash; host CPython 3.12 vs CI-pinned 3.11), not tip defects. GHA `setup-python` supplies `python` + 3.11.16.
- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/`;
  portable **0002** remains necessary after that draft merges.
- PR #21 does not touch `math_console.py` / `PACKET.json`; no 0002 regen needed.
- Re-run this matrix when a merge edits `PACKET.json` or `math_console.py`.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
