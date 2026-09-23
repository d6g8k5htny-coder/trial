# Portable patch compatibility matrix

Checked 2026-09-23 ~21:35 UTC (batch 50: Path B probe; tip #29; ship 0014 collision close-handles).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

| Tip | SHA | apply stack | `math_status_check` | Focused tests* |
|-----|-----|-------------|---------------------|----------------|
| hardening (post-#29) | `8510874` | **0001–0004 + 0008–0014** | problems=0 | **90+47+36 recovery** |
| hardening (post-#27) | `bf1fde3` | **0001–0004 + 0008–0013** | problems=0 | **90+47+36 recovery** |
| hardening (post-#26) | `a8a5dd7` | OK 0001–0011 (pre-drop) | problems=0 | **90+47+36 recovery** |
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
| PR #27 (merged) | probe-test isolation → `bf1fde3` | **0001–0004 + 0008–0012** | problems=0 | **90+47+36** @ 3.11 |
| PR #29 (merged) | R1 exact-byte custody → `8510874` | **0001–0004 + 0008–0014** | problems=0 | **90+47+36 + 189 collision** @ 3.11 |

\* Default slice @ `8510874`: carriers + math_status + inventable probes + gaussian + instrumentation STATUS + claims + recovery.

† Pre-#19 tips: **0008** still applies on `1547ec4` (same carriers/math_status open patterns).

‡ Pre-#20 tips lack `tests/test_inventable_jetmod_instrumentation_status.py`; omit 0006–0008 or use an older `apply_all` listing.

§ Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-…` (not in `apply_all.sh`).

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Head moved; mergeStateStatus CLEAN (batch 31).

## Post-#29 stack (`85108745ed4444adb838c53ae79cd603ed90f6fc`)

```bash
# From a clean hardening tip checkout — use apply_all.sh (0001–0004 + 0008–0014)
/path/to/trial/portable/patches/apply_all.sh --check
/path/to/trial/portable/patches/apply_all.sh
# tip-cut 0005/0006/0007 are NOT applied (obsolete; kept on disk for history)
```

Why tip-cut **0005/0006/0007** were dropped: PR #27 rewrote inventable/instrumentation
runners to use `tmp_path` + `_probe_snapshot()` (dirty-receipt defect fixed upstream).
Tip-cut 0005/0006 restore shape and 0007 (which patched that shape) cannot apply.
Post-merge residual: **6** `ResourceWarning` from bare `open()` in negative inventable/
instrumentation tests → cleared by **0012**. Broader residual: **828** unclosed-file
warnings from `verify_manifests` / `quarantine_check` → cleared by **0013**.
Batch 50: `collision_proposal_check` + `test_collision_proposal` bare opens → cleared by **0014**.

Notes:

- Batch **50** (Path B probe + tip #29 + portable **0014**): tip **`bf1fde3` → `8510874`** ([PR #29](https://github.com/d6g8k5htny-coder/main/pull/29) R1 exact-byte custody merged). BASE_TIP refreshed. Probe **DENIED** / audit **MISALIGNED** → Path B skipped. Main PRs: #2 HOLD draft CLEAN; #28/#30 docs drafts; #29 already merged (no portable drop). Shipped **0014** (collision_proposal_check + test_collision_proposal close-file-handles). Tip `apply_all` 0001–0004+0008–0014 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; collision checker **0 ResourceWarning** (was 2); collision tests **189 passed** / **0 ResourceWarning** (was 51). Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **49** (Path B probe + portable **0013**): tip then **`bf1fde3`** (== BASE_TIP). Probe **DENIED** / audit **MISALIGNED** → Path B skipped. Main PRs open: #2 HOLD draft CLEAN; #28/#30 docs drafts; #29 register export OPEN; #27 already merged (no further drops). Shipped **0013** (verify_manifests + quarantine_check close-file-handles). Tip `apply_all` 0001–0004+0008–0013 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; `verify_manifests` + `quarantine_check` **0 ResourceWarning** (was 828 each) with stdout parity. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **48** (PR #27 merged + drop 0005/0006/0007 + portable **0012**): tip **`a8a5dd7` → `bf1fde3`**. Probe **DENIED** / watch **MISALIGNED** → Path B skipped. Dropped tip-cut 0005/0006/0007 from `apply_all.sh`. Shipped **0012** (inventable-negative close-file-handles). Tip `apply_all` 0001–0004+0008–0012 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. Hunt note (shipped in batch 49 as **0013**): `tools/verify_manifests.py` / `quarantine_check.py` had **828** unclosed-file ResourceWarnings. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **47** (Path B probe + portable **0011**): tip then **`a8a5dd7`**. Probe **DENIED** / watch **MISALIGNED** → Path B skipped. PR #27 still OPEN @ `20e31a1` → **did not** drop tip-cut 0005/0006. Broader hunt: `tools/math_status_check.py` had **30** unclosed-file ResourceWarnings → shipped **0011**. Tip `apply_all` 0001–0011 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; `math_status_check` itself **0 ResourceWarning**. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **46** (PR #27 sync + tip #26): tip **`46af1ca` → `a8a5dd7`** ([PR #26](https://github.com/d6g8k5htny-coder/main/pull/26) math_status README inventable probes honesty pointer merged; docs-only; no scientific status change). BASE_TIP refreshed. Tip `apply_all` 0001–0010 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. PR **#27** head **`63b519f` → `20e31a1`** (merge hardening post-#26): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009/0010**) @ 3.11 → problems=0 / lemma_closed=false / focused **90 passed** / probes clean / residual **6** ResourceWarning; claims+recovery **83** / **0 ResourceWarning**. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` / workflow integrity cases), not tip defects.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
- Trial CI: portable-patches job includes the instrumentation STATUS test.
