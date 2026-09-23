# One-command land paths for `d6g8k5htny-coder/main`

**Scientific effect: NONE** for documentation / packaging lands below.
Requires a credential that can push to `d6g8k5htny-coder/main`.
This `trial` cloud agent cannot (git push and Git Data API both return 403).

> ## Path A — ON HOLD (Dylan / CoS, 2026-09-23)
>
> **HOLD — stay draft / untouched.** Do **not** mark ready; do **not** merge; do **not** retarget. Fail-closed.  
> Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084  
> Preferred unblock is now **Path B** (Option-B notice), or grant App write for Path B only.  
> `scripts/owner_land_path_a.sh` hard-refuses unless `OWNER_FORCE_PATH_A=1` (Dylan only).  
> Agents must never call `gh pr ready` / `gh pr merge` on PR #2 unless Dylan explicitly lifts HOLD.

## Path B — honest redirect (PRIMARY while Path A on HOLD)

```bash
# Preferred owner script:
./scripts/owner_land_path_b.sh
# or:
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git checkout main
git checkout -b cursor/default-branch-notice
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
python3 /path/to/trial/scripts/audit_local_tree.py .   # expect ALIGNED (would-align)
git push -u origin HEAD
gh pr create --base main --title "docs: q0 redirect on default main" --body "Option-B notice. Scientific effect NONE. Path A (PR #2) on HOLD per Dylan/CoS."
```

Batch **22** local dry-run on default tip `f25b04bb`: `git am` OK; local auditor
**ALIGNED** (all four q0/notice markers; complexity markers cleared; `body`
quarantined). Path B content is sufficient — landing blocked only by write/token.

## Path A — land the real tree (INACTIVE — HOLD)

~~Preferred~~ **On HOLD.** PR #2 is the Drive→git port onto default `main` (historically MERGEABLE/CLEAN) but must stay **draft / untouched** until Dylan lifts HOLD.

```bash
# Do NOT run while HOLD is active:
# gh pr ready 2 --repo d6g8k5htny-coder/main
# gh pr merge 2 --repo d6g8k5htny-coder/main --merge
# ./scripts/owner_land_path_a.sh   # exits 1 unless OWNER_FORCE_PATH_A=1 (Dylan only)
```

Do **not** enable `research.yml` schedules solely for R2-06 prose.
## Path C — engineering patches on working tip

**After Path A (PR #2) merges:** rebase hardening onto the new `main`, then
apply portable `apply_all` **0001–0004 + 0008–0012**. Do not land Path C onto the abandoned
pre-q0 default tip.

Against `chatgpt/drive-github-hardening-20260919` (BASE_TIP `bf1fde3` — patches apply cleanly), or post-#2 `main` once the port is present:

```bash
# Preferred (owner write creds):
./scripts/owner_land_path_c.sh
# After #2: PATH_C_BASE=main ./scripts/owner_land_path_c.sh   # if default tip already has the research tree

# Manual:
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git fetch origin chatgpt/drive-github-hardening-20260919
# After #2 merges first: git rebase origin/main   (on hardening) — then continue
git checkout -b cursor/portable-engineering-patches origin/chatgpt/drive-github-hardening-20260919
/path/to/trial/portable/patches/apply_all.sh   # 0001–0004 + 0008–0012
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
| #2 | Port onto default `main` | **HOLD** — draft/untouched (Dylan/CoS); Path B preferred |
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
| #27 | Isolate probe tests from tracked receipts | **Merged** @ `bf1fde3` (batch 48); tip-cut **0005/0006/0007 dropped** from `apply_all`; stack **0001–0004 + 0008–0012** |
| #28 | STATUS_JETMOD inventable merge+promote REFUSED honesty | OPEN draft UNSTABLE |
| #3, #12 | Older drafts | CONFLICTING after #15 — see [`CONFLICTING_PR_NOTES.md`](CONFLICTING_PR_NOTES.md) |

## Re-launch agents

Point new cloud agents at `d6g8k5htny-coder/main` with write access and base
`chatgpt/drive-github-hardening-20260919` (or default `main` after Path B / post-HOLD Path A).


## Automation blocked for this agent

Attempts from the `trial` cloud token (2026-09-23):

| Action | Result |
|--------|--------|
| `git push` to `main` | 403 — denied to cursor[bot] |
| `POST /git/refs` on `main` | 403 — Resource not accessible by integration |
| `gh pr ready 2` / GraphQL markReady | 403 — Resource not accessible by integration |
| `gh pr merge 2` / GraphQL mergePullRequest | 403 — Resource not accessible by integration |
| trial `workflow_dispatch` land-option-b-on-main | 403 — Resource not accessible by integration |

Owner (or a write-enabled `main` agent) must run **Path B** (preferred under HOLD) or Path C after alignment. Path A is on HOLD.


## Patch regeneration watch

Working tip is **`bf1fde3`** (PR #27 merged; batch 48). Open drafts **#28**/**#21** (plus older stack).
Batch **48** (PR #27 merged + drop 0005/0006/0007 + portable **0012**): tip **`a8a5dd7` → `bf1fde3`**; probe DENIED / MISALIGNED → Path B skipped; dropped tip-cut 0005/0006/0007; inventable-negative ResourceWarnings → shipped **0012**; tip `apply_all` 0001–0004+0008–0012 @ 3.11 → **173** / **0 ResourceWarning**.
Batch **47** (Path B probe + portable **0011**): tip still **`a8a5dd7`**; probe DENIED / MISALIGNED → Path B skipped; PR #27 still OPEN → did **not** drop 0005/0006; `math_status_check` ResourceWarnings → shipped **0011**; tip `apply_all` 0001–0011 @ 3.11 → **173** / **0 ResourceWarning** (+ checker **0** ResourceWarning).
Batch **45** (Path B probe + portable **0010**): tip then **`46af1ca`**; probe DENIED / MISALIGNED → Path B skipped; PR #27 still OPEN → did **not** drop 0005/0006; recovery ResourceWarnings → shipped **0010**; tip `apply_all` 0001–0010 @ 3.11 → **173** / **0 ResourceWarning**.
Batch **44** (PR #27 sync): tip **`b02efe2` → `46af1ca`**; BASE_TIP refreshed; tip `apply_all` 0001–0009 @ 3.11 → **137** / **0 ResourceWarning**. PR #27 head **`8d023a9` → `63b519f`**: tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009**) → focused **90** / probes clean / residual **6** ResourceWarning. #27 still OPEN → **did not** drop 0005/0006. Write/Path B still 403; PR #2 HOLD.
Batch **43** (portable **0009**): tip was **`b02efe2`**; broader hunt @ 3.11 found claims unclosed-file ResourceWarnings → shipped **0009** into `apply_all`. workflow_integrity/run_checks/registers/ci_pins green.
Batch **41** (PR #27 0005 analysis): tip then **`b02efe2`**; tip `apply_all` 0001–0008 `--check` OK.
PR **#27** **MERGED** @ `bf1fde3` (batch 48). Tip-cut **0005/0006/0007 dropped** from `apply_all.sh`; residual inventable-negative ResourceWarnings cleared by **0012**. Live stack: **0001–0004 + 0008–0012** → focused+claims+recovery **173 passed** @ 3.11 / **0 ResourceWarning** (see `patches/COMPATIBILITY.md`).
Stack: #24/#25/#26/#27 **MERGED**; #28/#21 UNSTABLE; #3 CONFLICTING; #2 draft MERGEABLE/CLEAN (HOLD).
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
| `scripts/owner_land_path_b.sh` | **PRIMARY under HOLD.** Clone + `git am` Option-B → push branch + open PR (default). `--direct-main` opt-in. `--after-merge` remote verify. |
| `scripts/owner_land_path_a.sh` | **ON HOLD** — hard-refuses unless `OWNER_FORCE_PATH_A=1` (Dylan only). Would ready+merge PR #2. |
| `scripts/owner_land_path_c.sh` | Write probe → clone hardening (or post-alignment main) → `apply_all` 0001–0004 + 0008–0012 → assert `lemma_closed=false` → push branch + open PR. Fail-closed without write. |

Also listed in [`OWNER_ONE_LINERS.md`](OWNER_ONE_LINERS.md) and `./scripts/print_owner_unblock.sh`.

## Path B via trial Actions (token secret)

Workflow [`.github/workflows/land-option-b-on-main.yml`](../.github/workflows/land-option-b-on-main.yml):

1. Add Actions secret `MAIN_PUSH_TOKEN` on **trial** (Contents:Write + PullRequests:Write on `main`).
2. Run workflow `land-option-b-on-main` with `dry_run=false`.
3. Workflow `git am`s Option-B, runs `scripts/audit_local_tree.py` (must exit 0 /
   would-align), pushes `cursor/option-b-notice-from-trial` **and opens a PR**
   into default `main` — merge that PR. (Path A remains on HOLD.)

Default `dry_run=true` verifies `git am` + local auditor (no push).
