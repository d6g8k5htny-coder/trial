# Portable patch compatibility matrix

Checked 2026-09-23 ~20:58 UTC (batch 47 Path B probe + portable 0011).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply 0001–0011 (tip-cut) | `math_status_check` | Focused tests* |
|-----|-----|---------------------------|---------------------|----------------|
| hardening (post-#26) | `a8a5dd7` | OK (+0011) | problems=0 | **90+47+36 recovery** |
| hardening (post-#24) | `46af1ca` | OK (+0010) | problems=0 | **90+47+36 recovery** |
| hardening (post-#25) | `b02efe2` | OK (+0009) | problems=0 | **90+47 claims** |
| hardening (post-#23) | `3f85e93` | OK | problems=0 | **90 passed** |
| hardening (post-#22) | `a89f9a7` | OK | problems=0 | **90 passed** |
| hardening (post-#19) | `ae7daf7` | OK | problems=0 | **90 passed** |
| hardening (post-#20) | `1547ec4` | OK 0001–0007; **0008 OK**† | problems=0 | **90 passed** |
| hardening (post-#17) | `3e8f388` | OK for 0001–0005; **0006–0008 N/A**‡ | problems=0 | **86 passed** |
| hardening (post-#18) | `340d98a` | **0005 tip-cut fails**§ | — | use `0005-pre17-…` |
| PR #19 (merged) | `dcc0157` → tip | OK | problems=0 | **90 passed** |
| PR #20 (merged) | `4103ee1` → tip | OK | problems=0 | **90 passed** |
| PR #21 head | `5c453b1` | OK for 0001–0004; 0005 tip-cut N/A shape | problems=0 | inventable absent¶ |
| PR #22 (merged) | docs cross-links → `a89f9a7` | OK | problems=0 | **90 passed** |
| PR #23 (merged) | PACKET tip-align → `3f85e93` | OK | problems=0 | **90 passed** |
| PR #25 (merged) | standing owner authorization → `b02efe2` | OK | problems=0 | **90 passed** |
| PR #24 (merged) | inventable STATUS honesty cross-links → `46af1ca` | OK (+0010) | problems=0 | **90+47+36 recovery** |
| PR #26 (merged) | math_status README inventable probes honesty → `a8a5dd7` | OK (+0010) | problems=0 | **90+47+36 recovery** |
| PR #27 head | `20e31a1` | **0001–0004 + 0008 only**‖ | problems=0 | **90 passed** @ 3.11 |

\* Default slice @ `a8a5dd7`: carriers + math_status + inventable probes + gaussian + instrumentation STATUS + claims; batch 45/46 also verifies recovery.

† Pre-#19 tips: **0008** still applies on `1547ec4` (same carriers/math_status open patterns).

‡ Pre-#20 tips lack `tests/test_inventable_jetmod_instrumentation_status.py`; omit 0006–0008 or use an older `apply_all` listing.

§ Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-…` (not in `apply_all.sh`).

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Head moved; mergeStateStatus CLEAN (batch 31).

‖ See stack recipe below. Tip-cut `apply_all.sh` fails at 0005 on this head.

## PR #27 stack recipe (`chatgpt/probe-test-isolation-20260923` @ `20e31a13b426868c9a8c721ffdeef4a3efa19a60`)

Prior heads: `8d023a9` (isolation only) → `63b519f` (merge hardening post-#24) → `20e31a1` (merge hardening post-#26).

```bash
# From a clean PR #27 head checkout — do NOT run tip-cut apply_all.sh
git apply …/0001-carriers-verify-ignore-bytecode-caches.patch
git apply …/0002-math-console-path-honesty.patch
git apply …/0003-gaussian-moments-parametrize-list.patch
git apply …/0004-git-fixture-timeout-60s.patch
# SKIP tip-cut 0005 / 0006 / 0007 — see below
git apply …/0008-carriers-math-status-close-file-handles.patch
# optional: 0009/0010/0011 also apply (claims/recovery/math_status_check close-file-handles; independent of 0005–0007)
```

Why `apply_all` fails at **0005**: tip-cut 0005 expects the pre-isolation
`test_runner_writes_refused_receipts_only` body (in-tree snapshot/`before` + no
`tmp_path`). PR #27 already rewrote that test to run the probe runner under
`tmp_path` and assert `_probe_snapshot()` unchanged on source receipts — so the
dirty-receipt defect is **already fixed**, and tip-cut 0005/0006/0007 (which
patch the restore/`open().read()` shape) cannot apply.

**After #27 merges into hardening:** tip-cut **0005 and 0006 become obsolete**
(drop from `apply_all.sh` or replace with no-ops). Tip-cut **0007** also needs
regen/drop (it depends on the 0005/0006 restore shape). Residual on #27 head
only: **6** `ResourceWarning` from bare `open()` in negative inventable/
instrumentation tests (tmp_path copies — not tracked-receipt drift). No
alternate `0005-pr27-*.patch` shipped — defect gone; stack is **0001–0004 + 0008**.

Notes:

- Batch **47** (Path B probe + portable **0011**): tip still **`a8a5dd7`** (ls-remote match; no BASE_TIP refresh). Probe **DENIED** / watch **MISALIGNED** → Path B skipped. PR #27 still OPEN @ `20e31a1` → **did not** drop tip-cut 0005/0006. Broader hunt: `tools/math_status_check.py` had **30** unclosed-file ResourceWarnings → shipped **0011**. Tip `apply_all` 0001–0011 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; `math_status_check` itself **0 ResourceWarning**. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **46** (PR #27 sync + tip #26): tip **`46af1ca` → `a8a5dd7`** ([PR #26](https://github.com/d6g8k5htny-coder/main/pull/26) math_status README inventable probes honesty pointer merged; docs-only; no scientific status change). BASE_TIP refreshed. Tip `apply_all` 0001–0010 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. PR **#27** head **`63b519f` → `20e31a1`** (merge hardening post-#26): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009/0010**) @ 3.11 → problems=0 / lemma_closed=false / focused **90 passed** / probes clean / residual **6** ResourceWarning; claims+recovery **83** / **0 ResourceWarning**. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **45** (Path B probe + portable **0010**): tip then **`46af1ca`** (ls-remote match; no BASE_TIP refresh). Probe **DENIED** / watch **MISALIGNED** → Path B skipped. PR #27 still OPEN → **did not** drop 0005/0006. Broader hunt: recovery had **234** unclosed-file ResourceWarnings → shipped **0010**. Tip `apply_all` 0001–0010 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **44** (PR #27 sync): tip **`b02efe2` → `46af1ca`** (PR #24 merged — inventable REFUSED/EMPTY/ABSENT STATUS honesty cross-links; no scientific status change). BASE_TIP refreshed. Tip `apply_all` 0001–0009 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims **137 passed** / **0 ResourceWarning**. PR **#27** head **`8d023a9` → `63b519f`** (merge hardening into probe-isolation branch): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009**) @ 3.11 → problems=0 / lemma_closed=false / focused **90 passed** / probes clean / residual **6** ResourceWarning. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **43** (portable **0009**): tip still **`b02efe2`**. Broader hunt @ CPython **3.11**: workflow_integrity **110**, run_checks **45**, registers **53**, ci_pins **25** all green; **claims** had **19** unclosed-file ResourceWarnings → shipped **0009**. `apply_all` 0001–0009: problems=0 / lemma_closed=false / focused+claims **137 passed** / **0 ResourceWarning**. Write/Path B still 403; PR #2 HOLD; PR #27 still OPEN (0005/0006 not dropped). Default tip still MISALIGNED.
- Batch **41** (PR #27 0005 analysis): tip still **`b02efe2`** (ls-remote match; no BASE_TIP refresh). Tip `apply_all` 0001–0008 `--check` OK. PR **#27** @ `8d023a9` + **0001–0004 + 0008** @ CPython **3.11**: problems=0 / lemma_closed=false / focused **90 passed** / probes clean; **no** alternate 0005 (isolation supersedes). Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **39** (align-watch): tip still **`b02efe2`** (ls-remote match). Re-verified `apply_all` 0001–0008 @ 3.12.3: problems=0 / lemma_closed=false / focused **90 passed** / **0 ResourceWarning**. **No 0009.** PR **#27** head fails 0005 apply (test isolation rewrite) — batch 41 documents obsolescence + stack recipe above. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **38**: tip **`3f85e93` → `b02efe2`** (PR #25 merged — standing owner authorization for all research agents; no scientific status change). BASE_TIP refreshed. Re-verified `apply_all` 0001–0008 @ 3.12.3: problems=0 / lemma_closed=false / focused **90 passed** / **0 ResourceWarning**. **No 0009.** Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **35**: tip **`a89f9a7` → `3f85e93`** (PR #23 merged — docs tip-align PACKET base_commit/as_of). BASE_TIP refreshed. Re-verified `apply_all` 0001–0008 @ 3.11.16: problems=0 / lemma_closed=false / focused **90 passed** / **0 ResourceWarning**. **No 0009.** Write/Path A/B still 403. Default tip still MISALIGNED.
- Batch **31**: tip **`ae7daf7` → `a89f9a7`** (PR #22 merged — docs only). BASE_TIP refreshed. Re-verified `apply_all` 0001–0008 @ 3.12.3: problems=0 / lemma_closed=false / focused **90 passed** / **0 ResourceWarning**. **No 0009.** Write/Path A/B/workflow_dispatch still 403. Default tip still MISALIGNED.
- Batch **26**: tip still **`ae7daf7`**. Re-verified `apply_all` 0001–0008 @ 3.11.16: problems=0 / lemma_closed=false / focused **90 passed** / **0 ResourceWarning**. **No 0009.** Write/Path A/B/workflow_dispatch still 403. Trial PR #8 merged. Default tip still MISALIGNED.
- Batch **25**: tip **`1547ec4` → `ae7daf7`** (PR #19 merged). BASE_TIP refreshed. Shipped **0008** (carriers/math_status/carriers_verify close-file-handles). CPython 3.11.16 after `apply_all` 0001–0008: problems=0 / lemma_closed=false / focused **90 passed** / focused slice **0 ResourceWarning**. Path A merge preview still would-align. Stack: #19 MERGED; #21 `52bdd443` UNSTABLE; #3 CONFLICTING; #2 draft MERGEABLE/CLEAN. Trial PR #7 merged.
- Batch **24**: tip still **`1547ec4`**. Shipped **0007** (inventable close-file-handles).
- Batch **22**: tip still **`1547ec4`**. Path B dry-run **would-align=true**.
- Batch **21**: BASE_TIP → **`1547ec4`** (PR #20 merge). Promoted **0006** into `apply_all.sh`.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` / workflow integrity cases), not tip defects.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
- Trial CI: portable-patches job includes the instrumentation STATUS test.
