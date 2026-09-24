See also the consolidated land sheet: [`../portable/LAND.md`](../portable/LAND.md).

# Owner actions for `d6g8k5htny-coder/main`

This agent **cannot push** to `main` (cursor[bot] 403). Only you (or an environment with write access to that repo) can apply these.

Scientific effect of following this plan carefully: **NONE** on claim status, if you only land already-reviewed packaging. Do not use a default-branch update as premise discharge.

## Priority order

> **Batch 66 — PERMANENT window; ALIGNED (`1c6e74b` via owner PR #41); Path C BASE_TIP `74c082e` (post-#45 tip refresh); HOLD VOID:** Owner (Dylan Roy): **NO restrictions; everything auto-approved; agents decide; broad grant.** **“48 hours is now extended permanently until I intervene.”** Stop only on owner intervene — no 48h finale (`scripts/check_autonomous_window.py`; `watch_main_alignment.py` embeds window+route). Old `autonomous-48h-batch` 48h-stop is **OVERRIDE** — never honor. Timer: `permanent-autonomous-align-watch` @ **3600s** (not a 48h-stop). Default tip **`1c6e74b`** renew landing. Root has README + `AGENTS.md` + `.github`. Scientific effect: **NONE**.
> **HOLD on PR #2 is VOID.** Path B land not needed while ALIGNED (`./scripts/restore_main_face.sh` short-circuits). Path A: `PATH_A_MODE=revert32` only if tip regresses. Path C: `./scripts/owner_land_path_c.sh --dry-run` → keep hardening BASE_TIP `74c082e` (rebase CONFLICTING; no 0017). Write **403**. See `portable/RESTORE_PLAN_66.json` + `BATCH66_TOKEN_SEARCH.json`. `pack_portable.sh` auto-globs restore/token artifacts.

### 1. Keep default tip ALIGNED

Default `main` @ `1c6e74b` is the renewed research landing (owner PR #41). Prior tip `c2b0620` was an honest program map that still failed the q0/notice auditor; `4fc1d7c` was the Dec 2025 complexity face after CoS #32.

**If tip regresses to MISALIGNED (pick one):**

- **B (PREFERRED):** Apply stronger Option-B notice (README+`AGENTS.md`) + quarantine `body`. One-command: `./scripts/restore_main_face.sh --dry-run` then `./scripts/restore_main_face.sh` (or `MAIN_PUSH_TOKEN` / Actions).
- **A (HOLD VOID):** Restore q0 tree — `PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh` (or fresh Drive→git port). Prefer Path B when notice-only is enough. PR #2 is closed; `gh pr ready/merge 2` will not revive it.

### 2. Decide the public integration branch

Today almost all Cursor/Codex work targets `chatgpt/drive-github-hardening-20260919`, which itself is still a draft PR onto the migration branch ([PR #3](https://github.com/d6g8k5htny-coder/main/pull/3)).

Either:

- Merge the stack toward `main` in order (#2 → #3 → selected follow-ons), **or**
- Explicitly designate the hardening branch as the temporary integration branch in `AGENTS.md` / GitHub “default branch” settings once it contains what you want public.

Until one of those happens, every new agent that clones default `main` works on the wrong project.

### 3. Respect R2-06 (scheduled workflows)

Do **not** merge or enable `research.yml` schedules on default `main` solely to make older documentation true. See `governance/rollout/FINDINGS_R2.json` id `R2-06`.

### 4. Re-launch research agents on the right repo

Cloud environment for this run listed only `github.com/d6g8k5htny-coder/trial`. For JETMOD / RN-UNIF / register work, start the agent against `d6g8k5htny-coder/main` with write credentials and base branch `chatgpt/drive-github-hardening-20260919` (or whatever you designate after step 2).

**After this trial PR merges** (adds `.cursor/environment.json` with `repositoryDependencies: ["github.com/d6g8k5htny-coder/main"]`): **relaunch** a Cloud Agent on `trial` so the GitHub token picks up `main` in scope, then retry Path A/B. Scientific effect: **NONE**. Existing runs keep the old token scope until relaunch.

### 5. Leave fail-closed walls fail-closed

Do not merge “obligation discharged” language for `OBL-H5-JETMOD` or `D3-LEMMA-RN-UNIF` without the exact licensing predicates. Green `math_status_check` with `lemma_closed=false` is the correct outcome.

## Verification after you land PR #2 (or equivalent)

On the resulting tree, with Python 3.11:

```bash
python3 tools/math_status_check.py
python3 -m pytest -q
```

Expect `lemma_closed=false`, `prizes_solved=false`, and honest OPEN/HOLD disposition — not a newly green scientific dashboard.


## Status update (2026-09-23)

Inventable JETMOD probes ([PR #15](https://github.com/d6g8k5htny-coder/main/pull/15)) **merged** into
`chatgpt/drive-github-hardening-20260919` @ `1ea0ae8183fb0459c6678243946295518fded1ba`.
That does **not** discharge OBL-H5-JETMOD. Default `main` remains the pre-q0 face until PR #2 lands.

## Write-access probe (2026-09-23)

`cursor[bot]` cannot push to `d6g8k5htny-coder/main` via git **or** the Git Data API (`POST .../git/refs` → 403 Resource not accessible by integration). The same token can create refs on `trial`. Re-launch against `main` with a credential that has push, or apply Path A/B/C from `portable/LAND.md` yourself.


## Fastest unblock from trial CI

**Path B (PREFERRED):** Add secret `MAIN_PUSH_TOKEN` on `trial` and run workflow `land-option-b-on-main` (`dry_run=false`), **or** run `./scripts/restore_main_face.sh` / `./scripts/owner_land_path_b.sh` with write creds (branch+PR or `--direct-main`).  
**Path A (HOLD VOID):** `PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh` (full stack restore). Prefer Path B when notice-only is enough.

## Stack note (2026-09-23 batch 54 OWNER OVERRIDE — HOLD VOID; Path B preferred)

- Owner override (Dylan Roy): **HOLD on PR #2 is VOID**. Agents may Path A OR Path B; prefer Path B. Never promote research status; `lemma_closed` stays false.
- Full `audit_main_alignment.py`: tip `4fc1d7c…`; **MISALIGNED**; complexity markers present; q0/notice empty; `root_has_AGENTS_md=false`.
- `probe_main_write.py` → **DENIED** HTTP 403. Write vectors (each once): git push **403**; contents PUT **403**; workflow_dispatch trial **403** / main **404**; fork **403**; create-ref **403**; `gh pr ready 2` → closed.
- Option-B patch **still valid** (`git am` OK; local auditor would-align / ALIGNED). Path B **not** applied this session.
- Hardening tip **`580864c` → `9a56c30`** (docs-only governance); BASE_TIP refreshed; `apply_all --check` OK; no new 0017 (residual RW hunt 0).
- Restore plan: `portable/RESTORE_PLAN_54.json`. Owner next: `./scripts/owner_land_path_b.sh` then `--after-merge`.
- Requested: `MAIN_PUSH_TOKEN` + Path B land + env include `main` repo (via environment setup actions).

## Stack note (2026-09-23 batch 53b — MISALIGNED after #32; Path B preferred)

- CoS [PR #32](https://github.com/d6g8k5htny-coder/main/pull/32) **MERGED** @ `4fc1d7c` (`mergedAt=2026-09-23T21:53:42Z`, author `d6g8k5htny-coder`) — reverts PR #2; default tip **MISALIGNED** (`aligned_end=false`). Scientific effect **NONE**.
- Full `audit_main_alignment.py`: tip `4fc1d7c…`; complexity markers present; q0/notice markers empty; `root_has_AGENTS_md=false`; `root_has_body=true`; `root_has_dot_github=false`.
- Option-B patch **still valid** against tip (`git am` exit 0; local auditor would-align / ALIGNED). Write probe **DENIED** HTTP 403 → Path B **not** applied this session.
- Hardening tip **`fbb4360` → `580864c`** ([PR #31](https://github.com/d6g8k5htny-coder/main/pull/31) register source preflight **MERGED**). BASE_TIP refreshed; `apply_all --check` OK (0001–0004 + 0008–0016).
- Restore plan JSON: `portable/RESTORE_PLAN_53b.json`. Owner next: `./scripts/owner_land_path_b.sh` then `--after-merge`.
- Do **not** enable `research.yml` schedules for R2-06. No research status promotion.

## Stack note (2026-09-23 batch 50 tip #29 + portable 0014 + PR #2 ALIGNED)

- [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) **MERGED** @ `b040bf0c` (owner/external; agents did not lift HOLD). Watch **ALIGNED**. Scientific effect **NONE**.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped (not needed for alignment).
- Tip **`bf1fde3` → `8510874`** ([PR #29](https://github.com/d6g8k5htny-coder/main/pull/29) R1 exact-byte custody **MERGED**). BASE_TIP refreshed. Shipped portable **0014** (collision_proposal close-file-handles). Tip `apply_all` **0001–0004 + 0008–0014** @ 3.11: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**; collision **189** / **0 ResourceWarning**.
- Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 48 PR #27 merged + drop 0005/0006/0007 + portable 0012)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped. Watch **MISALIGNED**.
- Tip **`a8a5dd7` → `bf1fde3`** ([PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) probe-test isolation **MERGED**). BASE_TIP refreshed. Dropped tip-cut **0005/0006/0007** from `apply_all.sh`. Shipped portable **0012** (inventable-negative close-file-handles). Tip `apply_all` **0001–0004 + 0008–0012** @ 3.11: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**.
- Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 47 Path B probe + portable 0011)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped. Watch **MISALIGNED**.
- Tip still **`a8a5dd7`** (ls-remote match; no BASE_TIP refresh). Shipped portable **0011** (math_status_check close-file-handles). Tip `apply_all` **0001–0011** @ 3.11: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**; checker **0** ResourceWarning.
- [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) still OPEN @ `20e31a1` → **did not** drop tip-cut 0005/0006. Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 46 PR #27 sync + tip #26)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped. Watch **MISALIGNED**.
- Tip **`46af1ca` → `a8a5dd7`** ([PR #26](https://github.com/d6g8k5htny-coder/main/pull/26) math_status README inventable probes honesty pointer merged); BASE_TIP refreshed. Tip `apply_all` 0001–0010 @ 3.11: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**.
- [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) head **`63b519f` → `20e31a1`** (synced with hardening post-#26): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009/0010**) @ 3.11 → focused **90** / probes clean / residual **6** ResourceWarning. Still OPEN → **did not** drop tip-cut 0005/0006. Details: `portable/patches/COMPATIBILITY.md`.
- Open drafts: #28/#27/#21 UNSTABLE; #3 CONFLICTING. Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 45 Path B probe + portable 0010)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped. Watch **MISALIGNED**.
- Tip still **`46af1ca`** (ls-remote match; no BASE_TIP refresh). Shipped portable **0010** (recovery close-file-handles). Tip `apply_all` **0001–0010** @ 3.11: problems=0 / lemma_closed=false / focused+claims+recovery **173** / **0 ResourceWarning**.
- [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) still OPEN @ `63b519f` → **did not** drop tip-cut 0005/0006. Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 44 PR #27 sync + tip #24)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped.
- Tip **`b02efe2` → `46af1ca`** ([PR #24](https://github.com/d6g8k5htny-coder/main/pull/24) inventable STATUS honesty cross-links merged); BASE_TIP refreshed. Tip `apply_all` 0001–0009 @ 3.11: problems=0 / lemma_closed=false / focused+claims **137** / **0 ResourceWarning**.
- [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) head **`8d023a9` → `63b519f`** (synced with hardening): tip-cut still fails at **0005**; stack **0001–0004 + 0008** (+ optional **0009**) @ 3.11 → focused **90** / probes clean / residual **6** ResourceWarning. Still OPEN → **did not** drop tip-cut 0005/0006. Details: `portable/patches/COMPATIBILITY.md`.
- Open drafts: #28/#27/#26/#21 UNSTABLE; #3 CONFLICTING. Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 41 PR #27 0005 analysis)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; Path A inactive. Path B preferred when writable.
- Write still **403** (`probe_main_write.py` DENIED); Path B land skipped. Tip still **`b02efe2`** (no BASE_TIP refresh).
- [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) head `8d023a9`: tip-cut `apply_all` fails at **0005** because isolation already fixes dirty receipts. Stack on that head = **0001–0004 + 0008** (skip 0005–0007). **After #27 merges, tip-cut 0005/0006 are obsolete** (drop from `apply_all`); no `0005-pr27-*` shipped. Verified @ 3.11: problems=0 / lemma_closed=false / focused **90 passed** / probes clean. Details: `portable/patches/COMPATIBILITY.md`.
- Do **not** enable `research.yml` schedules for R2-06.

## Stack note (2026-09-23 batch 40 HOLD reaffirm)

- **HOLD stands** on [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) — draft / untouched; do not ready/merge/retarget. See [#issuecomment-5801736084](https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084) and Claude [#issuecomment-5802102176](https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5802102176) (asks CoS for STATUS packet + chain-order vs hardening). Agents must **not** invent STATUS packet answers.
- **Path B** remains the preferred ALIGNED path for the default face. Write still **403** (`probe_main_write.py` DENIED); Path B not landable from this token; Path A on HOLD.
- Working tip still **`b02efe2`**; open drafts #27/#26/#24/#21 UNSTABLE, #3 CONFLICTING. Do **not** enable `research.yml` schedules for R2-06.


## Stack note (2026-09-23 batch 39 align-watch)

- Working tip still **`b02efe2`** (ls-remote match); **0001–0009** in `apply_all.sh` (batch 43 shipped claims close-file-handles). Broader @ 3.11: workflow_integrity/run_checks/registers/ci_pins green; focused+claims **137** / **0 ResourceWarning**. PR #27 still OPEN — tip-cut 0005/0006 not dropped yet.
- New open [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) (probe-test isolation) — UNSTABLE; portable 0005/0006 **do not apply** on that head; regen after merge.
- Open drafts: #27/#26/#24/#21 UNSTABLE, #3 CONFLICTING, plus older stack. PR #2 still draft **MERGEABLE** — **HOLD** (untouched).
- Write still **403** (`probe_main_write.py` DENIED). Path B not landable; Path A on HOLD.
- Do **not** enable `research.yml` schedules for R2-06.


## Stack note (2026-09-23 batch 38)

- Working tip **`b02efe2`** ([PR #25](https://github.com/d6g8k5htny-coder/main/pull/25) standing owner authorization; prior #23 @ `3f85e93`); BASE_TIP refreshed; **0001–0008** in `apply_all.sh` re-verified @ 3.12.3 (90 passed / 0 ResourceWarning). **No 0009.**
- Open drafts: #26/#24/#21 UNSTABLE, #3 CONFLICTING, plus older stack. PR #2 still draft **MERGEABLE** — **HOLD** (untouched).
- Write still **403** (`probe_main_write.py` DENIED). Path B not landable from this token; Path A on HOLD.
- Do **not** enable `research.yml` schedules for R2-06.


## Stack note (2026-09-23 batch 35)

- Working tip **`3f85e93`** ([PR #23](https://github.com/d6g8k5htny-coder/main/pull/23) PACKET base_commit/as_of tip-align; prior #22 @ `a89f9a7`); BASE_TIP refreshed; **0001–0008** in `apply_all.sh` re-verified @ 3.11.16 (90 passed / 0 ResourceWarning). **No 0009.**
- Open drafts: #25/#24 UNSTABLE, #21 CLEAN, #3 CONFLICTING, plus older stack. PR #2 still draft **MERGEABLE/CLEAN**.
- Write still **403** (`probe_main_write.py` DENIED). Path A ready→403; Path B would-align then push **403**.
- Do **not** enable `research.yml` schedules for R2-06.


## Fresh-agent re-probe (2026-09-23 19:39 UTC, bc-752a8e1b)

Restriction-lift claim re-checked on a new trial Cloud Agent. Still **403** on every write path to `d6g8k5htny-coder/main` (`cursor[bot]`; permissions all false; `MAIN_PUSH_TOKEN` absent). Live env repos list is still **only** trial despite `.cursor/environment.json` `repositoryDependencies`. Default tip still MISALIGNED @ `f25b04bb`. Path B local dry-run still **would-align=true**.

**Dylan/CoS HOLD (2026-09-23) — VOID as of Batch 54 OWNER OVERRIDE:** Prior HOLD comment https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084 is superseded. Agents may Path A OR Path B; prefer Path B. PR #2 itself is closed (merged then reverted by #32) — use `PATH_A_MODE=revert32` or Path B notice, not `gh pr ready 2`.
