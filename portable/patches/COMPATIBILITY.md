# Portable patch compatibility matrix

Checked 2026-09-24 ~19:50 UTC (batch 239: PERMANENT window; tip `62f955a` post-#70; #69 CI pending; cut **0019** attestations close-handles; when_writable future-delta gate).
**Scientific effect: NONE.** `lemma_closed` stayed false on every tip.

## Post-#41 tip topology (Path C)

| Tip | Role | Path-C shaped? | apply_all |
|-----|------|----------------|-----------|
| default `main` @ `1c6e74b` (PR #41) | ALIGNED research **landing** (README + `AGENTS.md` + `.github`; `body` under `history/`) | **No** — missing `PACKET.json` / `carriers_verify` | **Refuse** (`PATH_C_BASE=main` blocked) |
| hardening `chatgpt/drive-github-hardening-20260919` @ BASE_TIP | Engineering working tip | **Yes** | **0001–0004 + 0008–0019** |
| rebase hardening → `main` | Integration attempt | — | Usually **CONFLICTING** after #41 (`ci.yml` / bridge / history relocation) |

Keep Path C on hardening. Certainty: `./scripts/owner_land_path_c.sh --dry-run` → `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`.
If a forced rebase hits first-stop conflicts: `./scripts/path_c_rebase_helper.sh --dry-run` (prefer abort; `--stage` profiles stage ours/theirs without touching PACKET / lemma_closed).

| Tip | SHA | apply stack | `math_status_check` | Focused tests* |
|-----|-----|-------------|---------------------|----------------|
| hardening (post-#70) | `62f955a` | **0001–0004 + 0008–0018** (+**0019** pending) | problems=0 | **BASE_TIP batch 239** (0019 attestations RW; followon gate) |
| hardening (post-#51) | `b89448d` | **0001–0004 + 0008–0017** | problems=0 | **BASE_TIP batch 207** (+0017 pinned_sources RW; path-c-applied-bundle rebuilt) |
| hardening (post-#53) | `8ea3b5f` | **0001–0004 + 0008–0016** | problems=0 | **BASE_TIP batch 162** (apply_all OK; focused 90/0 RW; path-c-applied-bundle rebuilt) |
| hardening (post-#54) | `10c077e` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 142–161) |
| hardening (post-#50) | `c82c9357` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 125–141) |
| hardening (post-#48) | `ac33581` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 74–124) |
| hardening (post-#44) | `5f352a2` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 70–73) |
| hardening (post-#45) | `74c082e` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 66–69) |
| hardening (post-#42) | `3d47d1b` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 65) |
| hardening (post-#43) | `6f0f061` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 63–64) |
| hardening (post-#34) | `b3da668` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 60–62) |
| hardening (post-#35) | `036a6bc` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 59) |
| hardening (post-governance) | `9a56c30` | **0001–0004 + 0008–0016** | problems=0 | (BASE_TIP batch 54–58) |
| hardening (post-#31) | `580864c` | **0001–0004 + 0008–0016** | `--check` OK | (BASE_TIP batch 53b) |
| hardening (post-#30) | `fbb4360` | **0001–0004 + 0008–0016** | problems=0 | **90+47+36 + frozen/dio 19 + receipts/bridge 541** |
| hardening (post-#28) | `890bb81` | **0001–0004 + 0008–0016** | problems=0 | **90+47+36 + frozen/dio 19 + receipts/bridge 541** |
| hardening (post-#29 / batch 52) | `8510874` | **0001–0004 + 0008–0015** | problems=0 | **90+47+36 + frozen/dio 19** |
| hardening (post-#29 / batch 50) | `8510874` | **0001–0004 + 0008–0014** | problems=0 | **90+47+36 recovery** |
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
| PR #28 (merged) | STATUS_JETMOD inventable honesty → `890bb81` | **0001–0004 + 0008–0016** | problems=0 | **90+47+36 + receipts/bridge 541** @ 3.11 |

\* Default slice @ `890bb81`: carriers + math_status + inventable probes + gaussian + instrumentation STATUS + claims + recovery.

† Pre-#19 tips: **0008** still applies on `1547ec4` (same carriers/math_status open patterns).

‡ Pre-#20 tips lack `tests/test_inventable_jetmod_instrumentation_status.py`; omit 0006–0008 or use an older `apply_all` listing.

§ Tip moved: PR #17 merged @ `3e8f388`. Batch 17 re-cut **0005** for the expanded inventable EXPECTED/SHORTCUTS assertions. Pre-#17 tips need `0005-pre17-…` (not in `apply_all.sh`).

¶ PR #21 is based on PR #3 (pre-inventable); inventable probe tests are absent. Head moved; mergeStateStatus CLEAN (batch 31).

## Post-#30 stack (`fbb43601369b19ecb12447d4cc02ed44340dce60`) — batch 53

```bash
# From a clean hardening tip checkout — use apply_all.sh (0001–0004 + 0008–0016)
# NOT default main (MISALIGNED after #32; pre-q0 face; no PACKET.json).
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
Batch 52: `test_frozen_check` + `test_drive_index_overlay` bare opens → cleared by **0015**.
Batch 53: `test_receipts` + `test_bridge` bare opens → cleared by **0016**.

Notes:

- Batch **74** (PERMANENT; ALIGNED @ 1c6e74b; tip move; Batch 73 CI fix): hardening **`5f352a2` → `ac33581`** ([PR #48](https://github.com/d6g8k5htny-coder/main/pull/48) checked accounting in inner-wedge RN verifier); BASE_TIP refreshed; `apply_all --check`/apply OK; math_status problems=0 / lemma_closed=false; focused **90**/0. CI fixes: Intent suite exports `GITHUB_TOKEN`; Option-B apply check skips when default tip already ALIGNED; `owner_land_path_b --after-merge` no longer requires `gh auth`; write-vector tip GET falls back to anonymous urllib. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_74.json`.
- Batch **73** (PERMANENT; ALIGNED @ 1c6e74b; no tip move; CI land-workflows-dry-run): hardening still **`5f352a2`** (== BASE_TIP; no commits past tip → **no 0017**). Shipped `scripts/validate_land_workflows.py` + CI job `land-workflows-dry-run` (actionlint + owner `--help`/`--dry-run`) so `land-option-b-on-main` + `land-path-c-on-main` are validated **without** `MAIN_PUSH_TOKEN`. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_73.json`.
- Batch **70** (PERMANENT; ALIGNED @ 1c6e74b; tip move; research-stack OPEN audit): hardening **`74c082e` → `5f352a2`** ([PR #44](https://github.com/d6g8k5htny-coder/main/pull/44) fail-closed vault path map); BASE_TIP refreshed; `apply_all --check` OK; `math_status_check` problems=0 / lemma_closed=false; OPEN inventory (13 premises / 1 lemma / 3 prizes / 16 OQs) via `scripts/audit_research_stack_open.py` — **flipped nothing**. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_70.json`. Artifact: `portable/BATCH70_RESEARCH_STACK_AUDIT.json`.
- Batch **68** (PERMANENT; ALIGNED @ 1c6e74b; no tip move; Path C rebase helper): hardening still **`74c082e`** (== BASE_TIP); **no 0017** / **IDLE**. Shipped `scripts/path_c_rebase_helper.sh` (`--dry-run` / `--stage` ours/theirs for first-stop `ci.yml` / `research.yml` / bridge README; never invent research status) + `portable/PATH_C_REBASE_RESOLUTION_NOTES_68.json`. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_68.json`.
- Batch **67** (PERMANENT; ALIGNED @ 1c6e74b; no tip move; Path C readiness artifact): hardening still **`74c082e`** (== BASE_TIP); `apply_all --check`/apply OK @ 3.11; PACKET transcription digests **6/6 OK**; pytest collection **3172**/0; residual RW hunt focused **173**/0 + receipts/bridge **541**/0 + frozen/dio/collision/registers/mirrors/ops/lean/cover/RN/new-files **~1800**/0 + tools `--help` **0** → **no 0017** / **IDLE**. New-since-0016-era files (cover audit / registers preflight / rn_side24_spatial) use `with open` / `Path.read_*` — no missing closes. Shipped `portable/PATH_C_REBASE_CONFLICT_REPORT_67.json` (rebase onto main first-stop: `ci.yml`, `research.yml`, `engine/bridge/README.md`); `path_c_dry_run` now emits `rebase_conflict_paths`. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_67.json`.
- Batch **66** (PERMANENT; ALIGNED @ 1c6e74b; tip move; old 48h-stop override ignored): hardening **`3d47d1b` → `74c082e`** ([PR #45](https://github.com/d6g8k5htny-coder/main/pull/45) checked cover-accounting boundary for RN replay); BASE_TIP refreshed; `apply_all --check`/apply OK @ 3.11; residual RW hunt focused **173**/0 + receipts/bridge **541**/0 → **no 0017** / **IDLE**. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_66.json`.
- Batch **65** (PERMANENT; ALIGNED @ 1c6e74b; tip move): hardening **`6f0f061` → `3d47d1b`** ([PR #42](https://github.com/d6g8k5htny-coder/main/pull/42) SIDE24 nav/prep honesty deepen); BASE_TIP refreshed; `apply_all --check`/apply OK @ 3.11; residual RW hunt focused **173**/0 + receipts/bridge **541**/0 + tools `--help` **0** → **no 0017** / **IDLE**. Write vectors still **DENIED**. Restore plan: `portable/RESTORE_PLAN_65.json`.
- Batch **63** (PERMANENT; ALIGNED @ 1c6e74b; tip move + post-#41 topology docs): hardening **`b3da668` → `6f0f061`** ([PR #43](https://github.com/d6g8k5htny-coder/main/pull/43) inventable REFUSED/EMPTY/ABSENT honesty walls); BASE_TIP refreshed; `apply_all --check`/apply OK @ 3.11; residual RW hunt focused+receipts/bridge/collision/frozen/registers/mirrors/ops/lean/RN/drive **~1600**/0 → **no 0017** / **IDLE**. Meaningful: `apply_all.sh` post-#41 topology fail-closed message + BASE_TIP currency note; `print_owner_unblock.sh` reads `BASE_TIP.txt` (no hardcoded SHA). Restore plan: `portable/RESTORE_PLAN_63.json`.
- Batch **62** (PERMANENT; ALIGNED; Path C dry-run; watch embeds window): BASE_TIP still **`b3da668`**; residual RW **0** → **no 0017**; `watch_main_alignment.py` embeds window+route. Restore plan: `portable/RESTORE_PLAN_62.json`.
- Batch **60** (ALIGNED @ 1c6e74b; Path C post-ALIGNED landing): hardening **`036a6bc` → `b3da668`** ([PR #34](https://github.com/d6g8k5htny-coder/main/pull/34) inventable probe index tip provenance); BASE_TIP refreshed; `apply_all --check`/apply OK; residual RW hunt **922**/0 → **no 0017**. Shipped `scripts/path_c_dry_run.py` + `owner_land_path_c.sh --dry-run`: default tip ALIGNED but not Path-C shaped; rebase onto main **CONFLICTING**; keep Path C on hardening. Restore plan: `portable/RESTORE_PLAN_60.json`.
- Batch **59** (ALIGNED via owner PR #41; Path B N/A; Path C IDLE): default tip **`c2b0620` → `1c6e74b`** **ALIGNED**; Option-B classic patch AM_FAILED on renewed tip; `path_b_dry_run` **ALREADY_ALIGNED**; write vectors **DENIED**; hardening **`9a56c30` → `036a6bc`** ([PR #35](https://github.com/d6g8k5htny-coder/main/pull/35)); BASE_TIP refreshed; residual RW hunt **0** → **no 0017** / **IDLE**. Shipped restore ALIGNED short-circuit + write preflight + `--batch`. Restore plan: `portable/RESTORE_PLAN_59.json`.
- Batch **58** (MISALIGNED; stronger Option-B + restore_main_face): default tip still **`c2b0620`** **MISALIGNED**; Option-B stronger `git am` OK / would-align; **all Path-B-capable write vectors DENIED**; hardening tip then `9a56c30` (live later moved to `036a6bc`); residual RW **0** → **no 0017**. Restore plan: `portable/RESTORE_PLAN_58.json`.
- Batch **57** (MISALIGNED; tip move + Option-B RECUT; Path B DENIED; Path C IDLE): default tip **`4fc1d7c` → `c2b0620`** (Dylan honest program-map) still **MISALIGNED**; Option-B **recut** `git am` OK / would-align (`path_b_dry_run` + `owner_land_path_b --dry-run`); **all Path-B-capable write vectors DENIED**; hardening tip **unchanged** `9a56c30`; residual RW hunt **0** → **no 0017** / **IDLE**. Shipped Path B dry-run certainty + `refresh_restore_plan.py` + tightened already-Option-B heuristic. Open stack #34/#35/#36 (#36 MERGEABLE/CLEAN). Restore plan: `portable/RESTORE_PLAN_57.json`.
- Batch **56** (MISALIGNED; Path C IDLE): default tip still **`4fc1d7c`** **MISALIGNED**; Option-B `git am` OK / would-align; **all Path-B-capable write vectors DENIED**; hardening tip **unchanged** `9a56c30`; residual RW hunt (focused+registers/mirrors/ops+RN+drive + tools `--help`) **0** → **no 0017** / **IDLE**. Tip residuals (not portable): `mirror_quotes` 3 problems → open [PR #35](https://github.com/d6g8k5htny-coder/main/pull/35); bridge AGENTS.md expectation drift after OP-AUTONOMY v2.0. Open stack +#34/#36. Restore plan: `portable/RESTORE_PLAN_56.json`.
- Batch **55** (unrestricted / auto-approve recorded; HOLD VOID; Path A or B OK): default tip still **`4fc1d7c`** **MISALIGNED**; Option-B `git am` OK / would-align; **all Path-B-capable write vectors DENIED** (git push / contents / workflow_dispatch / fork / create-ref / GraphQL commit / PR create); `issues:create` once succeeded (probe issue **#37**, not Path-B-capable). Hardening tip **unchanged** `9a56c30`; residual RW hunt **0** → **no 0017**. Path C harden: `scripts/probe_main_write_vectors.py`. Restore plan: `portable/RESTORE_PLAN_55.json`.
- Batch **54** (OWNER OVERRIDE): HOLD on PR #2 **VOID**; agents may Path A OR Path B (prefer B); default tip **`4fc1d7c`** **MISALIGNED**; Option-B `git am` OK / would-align; all write vectors **DENIED** (git push / contents / workflow_dispatch / fork / create-ref); hardening **`580864c` → `9a56c30`**; BASE_TIP refreshed; `apply_all --check` OK; no new 0017 (residual RW hunt 0). Restore plan: `portable/RESTORE_PLAN_54.json`.
- Batch **53b** (CRITICAL misalign after #32): default tip **`4fc1d7c`** **MISALIGNED** (`aligned_end=false`); Option-B `git am` OK / would-align; probe **DENIED** → Path B not applied; hardening **`fbb4360` → `580864c`** ([PR #31](https://github.com/d6g8k5htny-coder/main/pull/31)); BASE_TIP refreshed; `apply_all --check` OK. Restore plan: `portable/RESTORE_PLAN_53b.json`.
- Batch **53** (tip #28→#30 + portable **0016** + mid-batch #32 revert): tip **`8510874` → `890bb81` → `fbb4360`** ([PR #28](https://github.com/d6g8k5htny-coder/main/pull/28) then [PR #30](https://github.com/d6g8k5htny-coder/main/pull/30); docs-only). BASE_TIP refreshed. Start-of-batch default tip **ALIGNED** @ `b040bf0c`; CoS [PR #32](https://github.com/d6g8k5htny-coder/main/pull/32) **reverted** → end-of-batch **MISALIGNED** @ `4fc1d7c`. Probe **DENIED** → Path C not applied to remote. Shipped **0016**. Tip `apply_all` 0001–0004+0008–0016 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery+frozen/dio **192** / **0 ResourceWarning**; receipts+bridge **541 passed** / **0 ResourceWarning** (was 24). Path B again preferred for ALIGNED.
- Batch **52** (ALIGNED confirm + Path C landing + portable **0015**): tip still **`8510874`** (== BASE_TIP; no pack tip refresh). Default tip **ALIGNED** @ `b040bf0c`. Probe **DENIED** → Path C not applied to remote. Hardening ~53 behind / 1 ahead of post-#2 `main`. `owner_land_path_c` auto now stays on hardening (not post-#2 default main); adds `PATH_C_REBASE_ONTO_MAIN=1`. Shipped **0015**. Tip `apply_all` 0001–0004+0008–0015 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**; frozen+drive-index overlay **19 passed** / **0 ResourceWarning** (was 9+1). Residual hunt: `test_receipts` / `test_bridge` still emit bare-open ResourceWarnings (shipped in batch 53 as **0016**).
- Batch **50** (Path B probe + tip #29 + portable **0014**): tip **`bf1fde3` → `8510874`** ([PR #29](https://github.com/d6g8k5htny-coder/main/pull/29) R1 exact-byte custody merged). BASE_TIP refreshed. Probe **DENIED** / audit **MISALIGNED** → Path B skipped. Main PRs: #2 HOLD draft CLEAN; #28/#30 docs drafts; #29 already merged (no portable drop). Shipped **0014** (collision_proposal_check + test_collision_proposal close-file-handles). Tip `apply_all` 0001–0004+0008–0014 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; collision checker **0 ResourceWarning** (was 2); collision tests **189 passed** / **0 ResourceWarning** (was 51). Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **49** (Path B probe + portable **0013**): tip then **`bf1fde3`** (== BASE_TIP). Probe **DENIED** / audit **MISALIGNED** → Path B skipped. Main PRs open: #2 HOLD draft CLEAN; #28/#30 docs drafts; #29 register export OPEN; #27 already merged (no further drops). Shipped **0013** (verify_manifests + quarantine_check close-file-handles). Tip `apply_all` 0001–0004+0008–0013 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; `verify_manifests` + `quarantine_check` **0 ResourceWarning** (was 828 each) with stdout parity. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **48** (PR #27 merged + drop 0005/0006/0007 + portable **0012**): tip **`a8a5dd7` → `bf1fde3`**. Probe **DENIED** / watch **MISALIGNED** → Path B skipped. Dropped tip-cut 0005/0006/0007 from `apply_all.sh`. Shipped **0012** (inventable-negative close-file-handles). Tip `apply_all` 0001–0004+0008–0012 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. Hunt note (shipped in batch 49 as **0013**): `tools/verify_manifests.py` / `quarantine_check.py` had **828** unclosed-file ResourceWarnings. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **47** (Path B probe + portable **0011**): tip then **`a8a5dd7`**. Probe **DENIED** / watch **MISALIGNED** → Path B skipped. PR #27 still OPEN @ `20e31a1` → **did not** drop tip-cut 0005/0006. Broader hunt: `tools/math_status_check.py` had **30** unclosed-file ResourceWarnings → shipped **0011**. Tip `apply_all` 0001–0011 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**; `math_status_check` itself **0 ResourceWarning**. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Batch **46** (PR #27 sync + tip #26): tip **`46af1ca` → `a8a5dd7`** ([PR #26](https://github.com/d6g8k5htny-coder/main/pull/26) math_status README inventable probes honesty pointer merged; docs-only; no scientific status change). BASE_TIP refreshed. Tip `apply_all` 0001–0010 @ CPython **3.11**: problems=0 / lemma_closed=false / focused+claims+recovery **173 passed** / **0 ResourceWarning**. PR **#27** head **`63b519f` → `20e31a1`** (merge hardening post-#26): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009/0010**) @ 3.11 → problems=0 / lemma_closed=false / focused **90 passed** / probes clean / residual **6** ResourceWarning; claims+recovery **83** / **0 ResourceWarning**. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD. Default tip still MISALIGNED.
- Broad local pytest host failures remain agent-env (`python` missing in bare bash for some `test_ci_pins` / workflow integrity cases), not tip defects.
- Default `main` alignment is independent (Path A/B); these patches are Path C.
- Trial CI: portable-patches job includes the instrumentation STATUS test.
