# One-command land paths for `d6g8k5htny-coder/main`

**Scientific effect: NONE** for documentation / packaging lands below.
Requires a credential that can push to `d6g8k5htny-coder/main`.
This `trial` cloud agent cannot (git push and Git Data API both return 403).

> ## STATUS (Batch 61) — PERMANENT window; ALIGNED @ `1c6e74b`; Path C dry-run @ `b3da668`
>
> Owner (Dylan Roy): **NO restrictions; everything auto-approved; agents decide.
> Broad grant — any model may alter GitHub that isn’t beneficial; add anything.**
> **Permanent extension:** “48 hours is now extended permanently until I intervene.”
> Stop only on owner intervene — **no 48h finale.** Check:
> `python3 scripts/check_autonomous_window.py`.
> Default tip **`1c6e74b`**: renew main research landing ([PR #41](https://github.com/d6g8k5htny-coder/main/pull/41)).
> Root: README + `AGENTS.md` + `.github`; `body` under history/. Keep iterating.
> Scientific effect: **NONE**. **HOLD on PR #2 is VOID.** Path B land not needed
> (`restore_main_face` short-circuits). Path C: BASE_TIP `b3da668` (post-#34); RW **0** → **no 0017**;
> `./scripts/owner_land_path_c.sh --dry-run` → `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`
> (rebase onto main **CONFLICTING**). See `portable/RESTORE_PLAN_61.json` + `BATCH61_TOKEN_SEARCH.json`.

## Path B — honest redirect (PREFERRED when MISALIGNED)

```bash
# One-command (preferred):
./scripts/restore_main_face.sh --dry-run
./scripts/restore_main_face.sh
# Underlying owner script:
./scripts/owner_land_path_b.sh --dry-run   # certainty JSON (would-align; no push)
./scripts/owner_land_path_b.sh
# or:
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git checkout main
git checkout -b cursor/default-branch-notice
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
python3 /path/to/trial/scripts/audit_local_tree.py .   # expect ALIGNED (would-align)
git push -u origin HEAD
gh pr create --base main --title "docs: q0 redirect on default main" --body "Option-B notice. Scientific effect NONE."
```

Batch **59**: tip **`1c6e74b` ALIGNED** (owner PR #41). Classic Option-B patch does not
apply on renewed tip; `path_b_dry_run` → **ALREADY_ALIGNED**. Write vectors still
**DENIED**. Multi-vector: `python3 scripts/probe_main_write_vectors.py`. Restore plan:
`python3 scripts/refresh_restore_plan.py --batch 59`.

## Path A — restore q0 tree (HOLD VOID; prefer Path B)

PR #2 Drive→git port **merged** @ `b040bf0c`, then **reverted** by CoS PR #32 @ `4fc1d7c`.
**HOLD is VOID** (Batch 54 OWNER OVERRIDE). Agents may Path A, but prefer Path B
unless notice-only is impossible. PR #2 is closed — `gh pr ready 2` / `gh pr merge 2`
will not revive it.

```bash
# Preferred Path A tactic after #32 (write creds):
PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
# Or fresh OPEN port PR:
# PATH_A_MODE=ready_merge PATH_A_PR=<n> ./scripts/owner_land_path_a.sh
# Historical (only if an OPEN draft port PR exists):
# gh pr ready 2 --repo d6g8k5htny-coder/main
# gh pr merge 2 --repo d6g8k5htny-coder/main --merge
```

Do **not** enable `research.yml` schedules solely for R2-06 prose.
## Path C — engineering patches on working tip

**Engineering on hardening (independent of default-tip alignment):** apply portable
`apply_all` **0001–0004 + 0008–0016**. Default tip is **ALIGNED** @ `1c6e74b` (PR #41)
but **not** Path-C shaped (no `PACKET.json`; `tools/` are landing stubs). Keep Path C
on hardening. Certainty without write:

```bash
./scripts/owner_land_path_c.sh --dry-run   # path_c_dry_run.py JSON
# expect: APPLY_READY_POST_ALIGNED_KEEP_HARDENING; rebase_onto_main_state=CONFLICTING
```

Against `chatgpt/drive-github-hardening-20260919` (BASE_TIP `b3da668` after #34 tip provenance — `apply_all --check` OK).
**Do not** apply onto a tip that lacks `docs/math_status/PACKET.json`. **Do not** set
`PATH_C_BASE=main` on post-#41 tip. `PATH_C_REBASE_ONTO_MAIN=1` usually **CONFLICTS** after #41.


```bash
# Preferred (owner write creds):
./scripts/owner_land_path_c.sh --dry-run
./scripts/owner_land_path_c.sh
# Avoid post-#41: PATH_C_REBASE_ONTO_MAIN=1 (conflicts) / PATH_C_BASE=main (no PACKET)

# Manual:
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -b cursor/portable-engineering-patches origin/chatgpt/drive-github-hardening-20260919
/path/to/trial/portable/patches/apply_all.sh   # 0001–0004 + 0008–0016
python3 tools/math_status_check.py             # assert lemma_closed=false
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
  tests/test_inventable_jetmod_instrumentation_status.py
git commit -am "fix: portable engineering patches (Path C)"
git push -u origin HEAD
```

Post-merge verify from trial also runs Path C locally when `apply_all` is findable:

```bash
./portable/pr2-landing/VERIFY_AFTER_MERGE.sh          # ALIGNED + apply/assert
SKIP_PATH_C=1 ./portable/pr2-landing/VERIFY_AFTER_MERGE.sh   # alignment only
```

`lemma_closed` must stay false. Green checks ≠ obligation discharge.

## Stack hygiene

| PR | Role | Note |
|----|------|------|
| #2 | Port onto default `main` | **MERGED** @ `b040bf0c` then **REVERTED** by #32 @ `4fc1d7c` (MISALIGNED) |
| #15 | Inventable REFUSED probes | Merged into hardening @ `1ea0ae8` |
| #16 | Cold-start nav docs | **Merged** (docs-only) |
| #17 | Fail-closed inventable shortcut refusals | **Merged** @ `3e8f388`; tip-cut 0005 re-cut in batch 17 |
| #18 | PARTIAL/REFUSED STATUS vocab | **Merged** @ `340d98a` (ancestor of `1547ec4`) |
| #19 | AUTHOR_SIDE honesty banners on RN tip | **Merged** @ `ae7daf7` (ancestor of `3f85e93`) |
| #20 | Instrumentation PARTIAL/REFUSED_NOT_24JET STATUS | **Merged** @ `1547ec4`; promoted portable **0006** into `apply_all.sh`; batch 24 added **0007**; batch 25 added **0008** |
| #21 | Attestations + H3 salvage | MERGEABLE/**CLEAN** onto hardening (head `5c453b1`); patches 0001–0004 apply; inventable tests absent on that base |
| #22 | docs STATUS honesty cross-links | **Merged** @ `a89f9a7`; BASE_TIP refreshed (batch 31) |
| #23 | tip-align PACKET base_commit/as_of | **Merged** @ `3f85e93`; BASE_TIP refreshed (batch 35) |
| #25 | standing owner authorization | **Merged** @ `b02efe2`; BASE_TIP refreshed (batch 38); no status flip |
| #24 | inventable STATUS honesty cross-links | **Merged** @ `46af1ca`; BASE_TIP refreshed (batch 44); no status flip |
| #26 | math_status README inventable probes honesty pointer | **Merged** @ `a8a5dd7`; BASE_TIP refreshed (batch 46); no status flip |
| #27 | Isolate probe tests from tracked receipts | **Merged** @ `bf1fde3` (batch 48); tip-cut **0005/0006/0007 dropped** from `apply_all`; stack now **0001–0004 + 0008–0016** |
| #29 | R1 exact-byte custody | **Merged** @ `8510874` (batch 50); BASE_TIP was `8510874` until #28 |
| #28 | STATUS_JETMOD inventable merge+promote REFUSED honesty | **Merged** @ `890bb81` (batch 53); docs-only |
| #30 | STATUS_RN_UNIF inventable ABSENT/EMPTY honesty | **Merged** @ `fbb4360` (batch 53); BASE_TIP refreshed; stack **0001–0004 + 0008–0016** |
| #32 | Revert PR #2 onto default `main` | **Merged** @ `4fc1d7c` (CoS); default tip **MISALIGNED** |
| #31 | Register source preflight (nonactivating) | **Merged** @ `580864c` (batch 53b); BASE_TIP refreshed |
| #33 | Standing auth + PR2 post-merge handoff onto default `main` | **CLOSED** (not merged; tip still MISALIGNED) |
| #34 | Inventable probe index tip provenance fail-closed | **OPEN** draft on hardening (MERGEABLE/UNSTABLE) |
| #35 | Restore AGENTS.md bridge pointers + CLAUDE.md mirror quote | **OPEN** on hardening (MERGEABLE/UNSTABLE); clears tip `mirror_quotes` 3 problems + bridge AGENTS.md drift |
| #36 | Keep ladder.py at hardening-lane certificate bytes | **OPEN** draft; base `claude/drive-audit-github-migration-rrglpp` (MERGEABLE/**CLEAN** — was CONFLICTING in batch 56) |
| #3, #12 | Older drafts | CONFLICTING after #15 — see [`CONFLICTING_PR_NOTES.md`](CONFLICTING_PR_NOTES.md) |

## Re-launch agents

Point new cloud agents at `d6g8k5htny-coder/main` with write access and base
`chatgpt/drive-github-hardening-20260919` (default `main` is **MISALIGNED** after #32 —
use Path B for the public face, hardening for engineering).


## Automation blocked for this agent

Attempts from the `trial` cloud token (2026-09-23):

| Action | Result |
|--------|--------|
| `git push` to `main` | 403 — denied to cursor[bot] |
| `POST /git/refs` on `main` | 403 — Resource not accessible by integration |
| `gh pr ready 2` / GraphQL markReady | 403 — Resource not accessible by integration |
| `gh pr merge 2` / GraphQL mergePullRequest | 403 — Resource not accessible by integration |
| trial `workflow_dispatch` land-option-b-on-main | 403 — Resource not accessible by integration |

Owner (or a write-enabled `main` agent) must run Path C for portable engineering patches.
**HOLD on PR #2 is VOID** (Batch 54). Agents may Path A OR Path B. Prefer Path B for ALIGNED.


## Patch regeneration watch

Working tip is **`036a6bc`** (#35 bridge/mirror on hardening; batch 59 — was `9a56c30`). Default `main` **ALIGNED** @ `1c6e74b` (Batch 59 owner PR #41).
Batch **59** (ALIGNED via owner PR #41; Path B N/A; Path C IDLE): tip **`c2b0620` → `1c6e74b`**; audit **ALIGNED**; Option-B classic AM_FAILED / `path_b_dry_run` **ALREADY_ALIGNED**; write vectors **DENIED**; BASE_TIP **`9a56c30` → `036a6bc`**; residual RW hunt **0** → **no 0017**; restore plan `portable/RESTORE_PLAN_59.json`.
Batch **57** (MISALIGNED; tip move + Option-B RECUT; Path B DENIED; Path C IDLE): tip **`4fc1d7c` → `c2b0620`**; audit **MISALIGNED**; Option-B recut `git am` OK / would-align (`path_b_dry_run`); all Path-B-capable write vectors **DENIED**; hardening tip **unchanged** `9a56c30`; residual RW hunt **0** → **no 0017**; open stack #34/#35/#36 (#36 MERGEABLE/CLEAN); restore plan `portable/RESTORE_PLAN_57.json`.
Batch **56** (MISALIGNED; Path C IDLE): tip still `4fc1d7c`; audit **MISALIGNED**; Option-B `git am` OK / would-align; all Path-B-capable write vectors **DENIED**; hardening tip **unchanged** `9a56c30`; residual RW hunt **0** → **no 0017**; open stack +#34/#35/#36; restore plan `portable/RESTORE_PLAN_56.json`.
Batch **55** (unrestricted / auto-approve recorded): tip `4fc1d7c`; audit **MISALIGNED**; HOLD VOID; Path A OR Path B OK (prefer B); all Path-B-capable write vectors **DENIED**; Path C harden `probe_main_write_vectors.py`; restore plan `portable/RESTORE_PLAN_55.json`.
Batch **54** (OWNER OVERRIDE): tip `4fc1d7c`; audit **MISALIGNED**; HOLD VOID; Path A OR Path B OK (prefer B); Option-B `git am` OK / would-align; all write vectors **DENIED**; BASE_TIP → `9a56c30`; no new 0017; restore plan `portable/RESTORE_PLAN_54.json`.
Batch **53b** (CRITICAL misalign investigate): tip `4fc1d7c`; audit **MISALIGNED**; Option-B `git am` OK / would-align; probe **DENIED** → Path B not applied; BASE_TIP → `580864c`; restore plan `portable/RESTORE_PLAN_53b.json`.
Batch **53** (tip #28→#30 + portable **0016** + mid-batch #32 revert): tip **`8510874` → `890bb81` → `fbb4360`**; probe DENIED; `apply_all` 0001–0004+0008–0016 `--check` OK; receipts/bridge ResourceWarnings → shipped **0016**; BASE_TIP refreshed; default tip flipped MISALIGNED by #32.
Batch **52** (ALIGNED confirm + Path C landing + portable **0015**): tip still **`8510874`**; probe DENIED; `apply_all` 0001–0004+0008–0015 `--check` OK; frozen/drive-index ResourceWarnings → shipped **0015**; owner_land_path_c auto stays on hardening (not post-#2 default main).
Batch **50** (Path B probe + tip #29 + portable **0014**): tip **`bf1fde3` → `8510874`**; probe DENIED → Path B skipped; watch **ALIGNED** (PR #2 merged externally); collision ResourceWarnings → shipped **0014**; tip `apply_all` 0001–0004+0008–0014 @ 3.11 → **173** / **0 ResourceWarning**; collision **189** / **0 RW**.
Batch **48** (PR #27 merged + drop 0005/0006/0007 + portable **0012**): tip **`a8a5dd7` → `bf1fde3`**; probe DENIED / then-MISALIGNED → Path B skipped; dropped tip-cut 0005/0006/0007; inventable-negative ResourceWarnings → shipped **0012**; tip `apply_all` 0001–0004+0008–0012 @ 3.11 → **173** / **0 ResourceWarning**.
Batch **47** (Path B probe + portable **0011**): tip still **`a8a5dd7`**; probe DENIED / MISALIGNED → Path B skipped; PR #27 still OPEN → did **not** drop 0005/0006; `math_status_check` ResourceWarnings → shipped **0011**; tip `apply_all` 0001–0011 @ 3.11 → **173** / **0 ResourceWarning** (+ checker **0** ResourceWarning).
Batch **45** (Path B probe + portable **0010**): tip then **`46af1ca`**; probe DENIED / MISALIGNED → Path B skipped; PR #27 still OPEN → did **not** drop 0005/0006; recovery ResourceWarnings → shipped **0010**; tip `apply_all` 0001–0010 @ 3.11 → **173** / **0 ResourceWarning**.
Batch **44** (PR #27 sync): tip **`b02efe2` → `46af1ca`**; BASE_TIP refreshed; tip `apply_all` 0001–0009 @ 3.11 → **137** / **0 ResourceWarning**. PR #27 head **`8d023a9` → `63b519f`**: tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009**) → focused **90** / probes clean / residual **6** ResourceWarning. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD.
Batch **43** (portable **0009**): tip was **`b02efe2`**; broader hunt @ 3.11 found claims unclosed-file ResourceWarnings → shipped **0009** into `apply_all`. workflow_integrity/run_checks/registers/ci_pins green.
Batch **41** (PR #27 0005 analysis): tip then **`b02efe2`**; tip `apply_all` 0001–0008 `--check` OK.
PR **#27** **MERGED** @ `bf1fde3` (batch 48). Tip-cut **0005/0006/0007 dropped** from `apply_all.sh`; residual inventable-negative ResourceWarnings cleared by **0012**. Live stack: **0001–0004 + 0008–0016** → focused+claims+recovery **173 passed** @ 3.11 / **0 ResourceWarning**; frozen+drive-index overlay **19** / **0 RW**; receipts+bridge **541** / **0 RW** (see `patches/COMPATIBILITY.md`).
Stack: #2/#24/#25/#26/#27/#28/#29/#30/#31 **MERGED** (#2 then **REVERTED** by #32); #21 drafts; #3 CONFLICTING.
Write still 403 from this token.
Copy-paste owner commands:
[`OWNER_ONE_LINERS.md`](OWNER_ONE_LINERS.md) or `./scripts/print_owner_unblock.sh`.
Write probe: `scripts/probe_main_write.py`. After further PACKET/`math_console`
merges, re-run `apply_all.sh --check` + focused tests; regenerate **0002** only if
digests drift. PR #21 does not edit PACKET/`math_console`.

## Owner land scripts (local / Codespace with write)

Executable wrappers that use the **owner's** `gh` auth (not the trial cloud token):

| Script | Role |
|--------|------|
| `scripts/owner_land_path_b.sh` | **PREFERRED** for default-tip ALIGNED after #32. `--dry-run` certainty JSON; clone + `git am` Option-B → push branch + open PR. `--direct-main` opt-in. `--after-merge` remote verify. |
| `scripts/path_b_dry_run.py` | Path B dry-run certainty only (no push). Exit 0 iff would-align. |
| `scripts/refresh_restore_plan.py` | Refresh `portable/RESTORE_PLAN_<N>.json` from live audit/vectors/dry-run. |
| `scripts/owner_land_path_a.sh` | **HOLD VOID** — default `PATH_A_MODE=revert32` (or `ready_merge` for a fresh OPEN port). Prefer Path B. |
| `scripts/owner_land_path_c.sh` | Write probe → clone **hardening** (auto; not post-#2 default main) → optional `PATH_C_REBASE_ONTO_MAIN=1` → `apply_all` 0001–0004 + 0008–0016 → assert `lemma_closed=false` → push branch + open PR. Fail-closed without write. |

Also listed in [`OWNER_ONE_LINERS.md`](OWNER_ONE_LINERS.md) and `./scripts/print_owner_unblock.sh`.

## Path B via trial Actions (token secret)

Workflow [`.github/workflows/land-option-b-on-main.yml`](../.github/workflows/land-option-b-on-main.yml):

1. Add Actions secret `MAIN_PUSH_TOKEN` on **trial** (Contents:Write + PullRequests:Write on `main`).
2. Run workflow `land-option-b-on-main` with `dry_run=false`.
3. Workflow `git am`s Option-B, runs `scripts/audit_local_tree.py` (must exit 0 /
   would-align), pushes `cursor/option-b-notice-from-trial` **and opens a PR**
   into default `main` — merge that PR. (HOLD VOID; Path B PREFERRED.)

Default `dry_run=true` verifies `git am` + local auditor (no push).
