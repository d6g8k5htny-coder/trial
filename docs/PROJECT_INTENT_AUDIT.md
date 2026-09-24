# Project intent audit (2026-09-24 batch 80 refresh)

Audit of Dylan Roy’s public GitHub projects visible to this agent.
**Scientific effect: NONE.** This note does not move any claim, premise, or obligation.

> **Live status (batch 80):** Permanent autonomous window
> (`PERMANENT_UNTIL_OWNER_INTERVENES` / `goal_complete=false`).  
> `d6g8k5htny-coder/main` default tip **`1c6e74b`** is **ALIGNED**
> (`aligned_end=true`) after owner PR #41 (superseding #32/`c2b0620`).  
> Path B land **not needed**. Path C engineering stack is **apply-ready** on
> hardening `chatgpt/drive-github-hardening-20260919` @ **`ac33581`**;
> owner `git am` via trial release **`batch80-path-c-bundle`** (or
> `portable/path-c-applied-bundle/`).  
> Write to `main` remains **403 DENIED** (all Path B/C vectors).  
> See `portable/LAND.md` / `portable/RESTORE_PLAN_80.json`.  
> Historical sections below keep the original pre-#2/#32/#41 snapshot.

## Live facts (batch 80 probe)

| Fact | Value |
|------|-------|
| Autonomous window | `PERMANENT_OPEN` — stop only on owner intervene; no 48h finale |
| Default `main` tip | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` (**ALIGNED**) |
| Hardening tip / BASE_TIP | `ac335815b277ac0c076082ac6af2344261c2093a` (unchanged; no tip refresh) |
| Path B | Not needed while ALIGNED; restore ready if tip drifts |
| Path C | `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`; land blocked by write 403 |
| Path C owner bundle | `portable/path-c-applied-bundle/path-c-on-hardening.patch` (+ APPLY.md / VERIFY.json) |
| Write probe | **DENIED** (403) — W1–W5 incl. Path C `workflow_dispatch` |
| Research status | Unchanged — `lemma_closed=false`; no claim/premise/prize flips |
| Portable 0017 | **Not shipped** — deep ResourceWarning hunt idle after apply_all |

Deep hunt (CPython 3.11, after local `apply_all` 0001–0004+0008–0016 @ `ac33581`):
focused+claims+recovery **173**/0 RW; receipts/bridge **541**/0; frozen/dio **19**/0;
collision **189**/0; mirrors **105**/0; registers **53**/0; lean/frontier **21**/0;
cover **100**/0; drive **110**/0; ops **214**/0; RN sample **216**/0;
vault/quarantine **13**/0; collect-only **3188**/0; tools `--help` **0** RW.
`engine/` bare `open()` hits are only under content-addressed
`carriers/blobs/` + `rn_engine/frozen/` (not actionable for portable 0017).
Open-PR engine touch: #21 `work_order.py` (top-level list only; no bare open).

---

## Repositories (original audit snapshot — historical)

| Repo | Description field | Default branch tip (SHA) | What visitors actually see |
|------|-------------------|--------------------------|----------------------------|
| `d6g8k5htny-coder/trial` | testing | `4b056d7` (pre-this-PR) | Blank README “# trial / testing” + CC0 |
| `d6g8k5htny-coder/main` | universal law | `f25b04bb931df2eaee302b666db014913486166b` | Abandoned Dec 2025 “complexity physics” README + `body` (docx script) |

## Intent of `main` (governing)

On the live working branch `chatgpt/drive-github-hardening-20260919`
(batch 77 tip `ac33581`; original audit tip was `7dd6a141d90d5b3d8c670dcf847fd4fc1de1a83e`):

- **Program:** q0 / SIDE24 mathematics research (Drive shared drive → git home).
- **Discipline:** status labels are transcribed, never decided in git. Green CI ≠ obligation discharge.
- **Open blockers (must stay OPEN until licensed predicates fire):**
  - `OBL-H5-JETMOD` — OPEN
  - `D3-LEMMA-RN-UNIF` — OPEN (`lemma_closed: false`)
  - Prize track — `prizes_solved: false` / HOLD
- **Authority:** Drive is the governing record; GitHub is the execution workspace (`AGENTS.md` / `CLAUDE.md`).

Local verification on hardening after apply_all (this agent, Python 3.11 host):

```
math_status_check: problems=0 disposition=OPEN_HOLD lemma_closed=false prizes_solved=false independence_credit=0
```

## Intent of `trial`

Public description and README both say “testing”. There was no harness, no boundary statement, and no pointer to the research repo — so mobile / cloud agents landing here had no way to know they were off the research tree.

## Misalignment (historical — resolved on default tip by PR #41)

### 1. Default branch of `main` advertised the wrong project

Pre-#41 `origin/main` presented “A Reconstruction of Physics from Multiscale Retrodiction Complexity…” with fabricated-looking validation checkmarks. That content is not the active program. The complexity-physics setup PR ([#1](https://github.com/d6g8k5htny-coder/main/pull/1)) was closed in Dec 2025. **Live default tip is now ALIGNED @ `1c6e74b` (PR #41).**

### 2. The real tree’s landing path (topology note)

| PR | Role | Base ← Head | State (at original audit) |
|----|------|-------------|---------------------------|
| [#2](https://github.com/d6g8k5htny-coder/main/pull/2) | Port Drive program to git (~4.2k files) | `main` ← `claude/drive-audit-github-migration-rrglpp` | was DRAFT; later closed/superseded in #41 path |
| [#3](https://github.com/d6g8k5htny-coder/main/pull/3) | RN wedge / hardening | migration ← `chatgpt/drive-github-hardening-20260919` | DRAFT lineage |
| later work | math_status, JETMOD walls, etc. | hardening ← feature branches | some merged into hardening |

Post-#41: default `main` is an ALIGNED **landing** notice tree; Path C engineering (PACKET.json / carriers_verify shape) stays on hardening. Do not set `PATH_C_BASE=main`. Rebase hardening onto main usually **CONFLICTS** (ci.yml / research.yml / bridge README).

### 3. Documented deployment gap (already known in-repo)

`governance/rollout/FINDINGS_R2.json` finding **R2-06** (`CONFIRMED_SOURCE_DEPLOYMENT_GAP`): research schedule workflows exist on the working branch; observed default `main` historically lacked full research workflow deployment. Proposed response: do **not** claim scheduled deployment or activate workflows merely to make earlier prose true.

### 4. This cloud agent cannot write to `main` (still true)

Push / refs / contents / fork / GraphQL commit / pulls create / Path C dispatch to `d6g8k5htny-coder/main` return **403** (or workflow 404 on default for Option-B land workflow). Environment repos list only `github.com/d6g8k5htny-coder/trial`. Path C land on hardening needs owner write token or owner `git am` of `portable/path-c-applied-bundle/`.

## What must not be “fixed”

Fail-closed OPEN/HOLD walls (JETMOD REFUSED receipts, RN-UNIF absences, `lemma_closed=false`) are **correct**. Inventable probes that return REFUSED / EMPTY / ABSENT are doing their job. Do not promote them to discharged to make a dashboard green. **Never flip research status** in autonomous batches.

## What this agent fixed in `trial`

- Honest README + boundary table.
- This audit (kept current across batches; batch 77 live-facts refresh).
- Owner action checklist for `main` ([OWNER_ACTIONS_MAIN.md](OWNER_ACTIONS_MAIN.md)).
- Minimal pytest sanity suite so the “testing” intent is real.
- Portable Path C patches + `path-c-applied-bundle` for owner land without agent write token.

## SHAs frozen at original audit time

| Ref | SHA |
|-----|-----|
| `main` default | `f25b04bb931df2eaee302b666db014913486166b` |
| migration tip | `b1335def2615888463e2d134294ef451895b8d0d` |
| research working base | `7dd6a141d90d5b3d8c670dcf847fd4fc1de1a83e` |
| inventable JETMOD probes | `ae94270d5f48d4c171f134efcea5058997966d71` |

## Live tip refresh (2026-09-23 batch 3 — historical mid-window)

| Ref | SHA |
|-----|-----|
| research working base (post-#15) | `1ea0ae8183fb0459c6678243946295518fded1ba` |
| default `main` | still `f25b04bb931df2eaee302b666db014913486166b` (MISALIGNED at that time) |

## Live tip refresh (2026-09-24 batch 77)

| Ref | SHA / state |
|-----|-------------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` (**ALIGNED**, PR #41) |
| hardening / Path C BASE_TIP | `ac335815b277ac0c076082ac6af2344261c2093a` |
| write to `main` | **403 DENIED** |
| Path C applied bundle | ready under `portable/path-c-applied-bundle/` |
| autonomous window | **PERMANENT_OPEN** |
| `goal_complete` | **false** |
