See also the consolidated land sheet: [`../portable/LAND.md`](../portable/LAND.md).

# Owner actions for `d6g8k5htny-coder/main`

This agent **cannot push** to `main` (cursor[bot] 403). Only you (or an environment with write access to that repo) can apply these.

Scientific effect of following this plan carefully: **NONE** on claim status, if you only land already-reviewed packaging. Do not use a default-branch update as premise discharge.

## Priority order

### 1. Stop advertising the abandoned complexity-physics README

Default `main` @ `f25b04bb` still shows the Dec 2025 complexity framework with “✅ Confirmed” rows. That is false for the active program.

**Options (pick one):**

- **A (preferred):** Mark [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) ready, review, and merge when you accept the Drive→git port as the repository’s public face. That replaces the misleading root with the q0 README and ~4.2k files.
- **B (minimal):** On default `main` only, replace `README.md` with a short redirect to the working branch / PR #2 (“research lives on branch X; default branch pending merge”) and remove or quarantine the `body` manuscript generator so visitors are not misled. Do not invent new scientific claims in that stub.

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

Add secret `MAIN_PUSH_TOKEN` on `trial` and run workflow `land-option-b-on-main`
(`dry_run=false`), **or** merge PR #2 on `main`. Either aligns the default tip.

## Stack note (2026-09-23 batch 26)

- Working tip still **`ae7daf7`** ([PR #19](https://github.com/d6g8k5htny-coder/main/pull/19)); BASE_TIP unchanged; **0001–0008** in `apply_all.sh` re-verified @ 3.11.16 (90 passed / 0 ResourceWarning). **No 0009.**
- Open drafts: #22 UNSTABLE, #21 UNSTABLE, #3 CONFLICTING, plus older stack. PR #2 still draft **MERGEABLE/CLEAN**.
- Write still **403** (`probe_main_write.py` DENIED). `MAIN_PUSH_TOKEN` absent in agent env. Path A ready→403; Path B would-align then push **403**; trial `land-option-b-on-main` workflow_dispatch **403**.
- Trial [PR #8](https://github.com/d6g8k5htny-coder/trial/pull/8) **merged** (batch 25 portable 0008 on trial main).
- Do **not** enable `research.yml` schedules for R2-06.
