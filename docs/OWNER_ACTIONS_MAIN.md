See also the consolidated land sheet: [`../portable/LAND.md`](../portable/LAND.md).

# Owner actions for `d6g8k5htny-coder/main`

This agent **cannot push** to `main` (cursor[bot] 403). Only you (or an environment with write access to that repo) can apply these.

Scientific effect of following this plan carefully: **NONE** on claim status, if you only land already-reviewed packaging. Do not use a default-branch update as premise discharge.

## Priority order

> **HOLD (Dylan / CoS, 2026-09-23):** [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) stays **draft / untouched**. Do **not** mark ready; do **not** merge; do **not** retarget. Fail-closed. Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084  
> **Path A is on HOLD.** Preferred unblock is now **Path B** (Option-B notice), or grant App write for Path B only. Agents must never call `gh pr ready` / `gh pr merge` on PR #2 unless Dylan explicitly lifts HOLD. Scientific effect: **NONE**.

### 1. Stop advertising the abandoned complexity-physics README

Default `main` @ `f25b04bb` still shows the Dec 2025 complexity framework with “✅ Confirmed” rows. That is false for the active program.

**Options (pick one):**

- **B (preferred while Path A is on HOLD):** On default `main` only, replace `README.md` with a short redirect to the working branch / PR #2 (“research lives on branch X; default branch pending merge”) and remove or quarantine the `body` manuscript generator so visitors are not misled. Do not invent new scientific claims in that stub. Owner script: `./scripts/owner_land_path_b.sh` (or grant App write / `MAIN_PUSH_TOKEN` for Path B only).
- **A (ON HOLD — Dylan/CoS):** Mark [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) ready and merge when (and only when) Dylan lifts HOLD. That would replace the misleading root with the q0 README and ~4.2k files. Until then: stay draft; `scripts/owner_land_path_a.sh` hard-refuses unless `OWNER_FORCE_PATH_A=1` (Dylan only).

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

**Path B (preferred under HOLD):** Add secret `MAIN_PUSH_TOKEN` on `trial` and run workflow `land-option-b-on-main` (`dry_run=false`), **or** run `./scripts/owner_land_path_b.sh` with write creds (branch+PR or `--direct-main`).  
**Path A:** ON HOLD — do **not** merge PR #2 until Dylan lifts HOLD.

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

**Dylan/CoS HOLD (2026-09-23):** PR #2 stays draft — https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084. Preferred unblock: **Path B** (Option-B notice) or grant App write for Path B only. Do not ready/merge #2.
