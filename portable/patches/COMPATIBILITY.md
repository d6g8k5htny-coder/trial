# Portable patch compatibility matrix

Checked 2026-09-23 ~17:50 UTC (batch 16b).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0005 | `math_status_check` | Focused tests* |
|-----|-----|-----------------|---------------------|----------------|
| hardening (post-#18) | `340d98a` | OK | problems=0 | **86 passed** |
| hardening (post-#15) | `1ea0ae8` | OK† | problems=0 | 84 passed |
| PR #18 head (pre-merge) | `278822e` | OK† | problems=0 | **86 passed** |
| PR #19 head | `837a2b4` | OK | problems=0 | 86 passed |
| PR #20 head | `c46463b` | OK | problems=0 | **90 passed**‡ |
| PR #17 head | `833ca55` | **0001–0004 OK; 0005 fails**§ | problems=0 | 86+ with 0001–0004 |
| PR #21 head | `d1e7d0e` | OK† (no inventable test file) | problems=0 | **81 passed**¶ |

\* Default slice: `tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py`

† Pre-#18 / older tips: 0005 applies when `tests/test_inventable_jetmod_probes.py` matches tip shape.

‡ PR #20 adds instrumentation status tests (same in-tree rewrite pattern as inventable probes; not covered by 0005).

§ PR #17 expands `EXPECTED` / assertions in the inventable test; 0005 hunk does not apply. Re-cut 0005 after #17 merges or lands its own restore.

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Slice used: carriers + math_status + gaussian.

Notes:

- Batch **16b** ships portable **0005** (inventable probe test restore). Tip still `340d98a`.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash; CPython 3.12 vs CI-pinned 3.11), not tip defects.
- PR #20 still ships `math_console.py` pointing at missing `code_prototypes/`;
  portable **0002** remains necessary after that draft merges.
- PR #18 **merged** into hardening @ `340d98a` (PARTIAL/REFUSED vocab). Open #20 is a follow-on instrumentation pack on that tip.
- PR #21 does not touch `math_console.py` / `PACKET.json`; no 0002 regen needed.
- Re-run this matrix when a merge edits `PACKET.json`, `math_console.py`, or inventable probe tests.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
