# Project intent audit (2026-09-23)

Audit of Dylan Roy’s public GitHub projects visible to this agent.
**Scientific effect: NONE.** This note does not move any claim, premise, or obligation.

> **Batch 59 live status:** `d6g8k5htny-coder/main` default tip **`1c6e74b`** is **ALIGNED**
> (`aligned_end=true`) after owner PR #41 renewed the landing (superseding #32/`c2b0620`).
> Path B land not needed. See `portable/LAND.md` / `portable/RESTORE_PLAN_59.json`.
> Historical table below is the original audit snapshot (pre-#2/#32/#41 churn).

## Repositories

| Repo | Description field | Default branch tip (SHA) | What visitors actually see |
|------|-------------------|--------------------------|----------------------------|
| `d6g8k5htny-coder/trial` | testing | `4b056d7` (pre-this-PR) | Blank README “# trial / testing” + CC0 |
| `d6g8k5htny-coder/main` | universal law | `f25b04bb931df2eaee302b666db014913486166b` | Abandoned Dec 2025 “complexity physics” README + `body` (docx script) |

## Intent of `main` (governing)

On the live working branch `chatgpt/drive-github-hardening-20260919` @ `7dd6a141d90d5b3d8c670dcf847fd4fc1de1a83e`:

- **Program:** q0 / SIDE24 mathematics research (Drive shared drive → git home).
- **Discipline:** status labels are transcribed, never decided in git. Green CI ≠ obligation discharge.
- **Open blockers (must stay OPEN until licensed predicates fire):**
  - `OBL-H5-JETMOD` — OPEN
  - `D3-LEMMA-RN-UNIF` — OPEN (`lemma_closed: false`)
  - Prize track — `prizes_solved: false` / HOLD
- **Authority:** Drive is the governing record; GitHub is the execution workspace (`AGENTS.md` / `CLAUDE.md`).

Local verification on that tip (this agent, Python 3.12 host):

```
math_status_check: problems=0 disposition=OPEN_HOLD lemma_closed=false prizes_solved=false independence_credit=0
```

## Intent of `trial`

Public description and README both say “testing”. There was no harness, no boundary statement, and no pointer to the research repo — so mobile / cloud agents landing here had no way to know they were off the research tree.

## Misalignment (the real breakage)

### 1. Default branch of `main` advertises the wrong project

`origin/main` still presents “A Reconstruction of Physics from Multiscale Retrodiction Complexity…” with fabricated-looking validation checkmarks. That content is not the active program. The complexity-physics setup PR ([#1](https://github.com/d6g8k5htny-coder/main/pull/1)) was closed in Dec 2025.

### 2. The real tree never landed on `main`

| PR | Role | Base ← Head | State |
|----|------|-------------|-------|
| [#2](https://github.com/d6g8k5htny-coder/main/pull/2) | Port Drive program to git (~4.2k files) | `main` ← `claude/drive-audit-github-migration-rrglpp` | **DRAFT, open** |
| [#3](https://github.com/d6g8k5htny-coder/main/pull/3) | RN wedge / hardening | migration ← `chatgpt/drive-github-hardening-20260919` | DRAFT, open |
| later work | math_status, JETMOD walls, etc. | hardening ← feature branches | some merged into hardening, not into `main` |

`git rev-list --count origin/main..origin/chatgpt/drive-github-hardening-20260919` → **116** commits ahead of default `main`, **4207** files changed vs default.

### 3. Documented deployment gap (already known in-repo)

`governance/rollout/FINDINGS_R2.json` finding **R2-06** (`CONFIRMED_SOURCE_DEPLOYMENT_GAP`): research schedule workflows exist on the working branch; observed default `main` has no `.github/workflows`. Proposed response: do **not** claim scheduled deployment or activate workflows merely to make earlier prose true.

### 4. This cloud agent cannot write to `main`

Push to `d6g8k5htny-coder/main` returns `403 Permission denied to cursor[bot]`. Environment repos list only `github.com/d6g8k5htny-coder/trial`. Fixes that belong on `main` require an agent/environment with write access to that repo, or owner action on the open drafts.

## What must not be “fixed”

Fail-closed OPEN/HOLD walls (JETMOD REFUSED receipts, RN-UNIF absences, `lemma_closed=false`) are **correct**. Inventable probes that return REFUSED / EMPTY / ABSENT are doing their job. Do not promote them to discharged to make a dashboard green.

## What this agent fixed in `trial`

- Honest README + boundary table.
- This audit.
- Owner action checklist for `main` ([OWNER_ACTIONS_MAIN.md](OWNER_ACTIONS_MAIN.md)).
- Minimal pytest sanity suite so the “testing” intent is real.

## SHAs frozen at audit time

| Ref | SHA |
|-----|-----|
| `main` default | `f25b04bb931df2eaee302b666db014913486166b` |
| migration tip | `b1335def2615888463e2d134294ef451895b8d0d` |
| research working base | `7dd6a141d90d5b3d8c670dcf847fd4fc1de1a83e` |
| inventable JETMOD probes | `ae94270d5f48d4c171f134efcea5058997966d71` |


## Live tip refresh (2026-09-23 batch 3)

| Ref | SHA |
|-----|-----|
| research working base (post-#15) | `1ea0ae8183fb0459c6678243946295518fded1ba` |
| default `main` | still `f25b04bb931df2eaee302b666db014913486166b` (MISALIGNED) |
