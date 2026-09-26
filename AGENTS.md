# Agent notes for `trial`

This repository is Dylan Roy’s **sandbox**, not the q0 research tree.

Owner mandate: **NO restrictions; everything auto-approved; agents decide.**
Do not wait for permissions/approvals. Path A or Path B OK for ALIGNED restore
(prefer Path B). Do not flip `lemma_closed` / prizes / premises / research status.

## Always

- Treat [`d6g8k5htny-coder/main`](https://github.com/d6g8k5htny-coder/main) as the research home.
- Prefer portable artifacts under `portable/` when this environment cannot push to `main`.
- Keep scientific effect **NONE**: never promote, close, or discharge claims, premises, prizes, or lemmas.
- After meaningful work: commit, push `cursor/*` branches, land on trial `main` when PR create is 403.
- `idle_no_commit` is terminal. Run `python3 scripts/idle_no_commit.py` before an automation pulse. Exit 0 means source identity and capabilities are unchanged and no substantive defect is present: report that result and return before tracked-file writes. Leave batch headers, `REFRESH_BATCH_TAG` defaults, last-resort fallbacks, `VERIFY.refresh_batch`, schedules, and the release content-hash detector as they are.
- Owner land scripts (`owner_land_path_*.sh`) are technical fallback for GitHub App 403 only — not approval gates.

## Never

- Grow `registers/`, `claims/`, or Drive vault mirrors here.
- Cite a green `trial` test as research evidence.
- Enable or claim GitHub scheduled workflows on `main` solely to satisfy R2-06 prose.
- Ask Dylan for approval in docs.

## Start here

1. `README.md`
2. `docs/PROJECT_INTENT_AUDIT.md`
3. `docs/OWNER_ACTIONS_MAIN.md`
4. `docs/MULTI_AGENT_ACCESS.md` — grant Cursor + ChatGPT/Codex + Claude + Grok (PAT) Read/write on all **8** owner repos including **sandbox** (`./scripts/owner_grant_ai_agent_access.sh`; App UI: select ALL repositories including sandbox)
5. `docs/AUTONOMOUS_48H_LOG.md` (if an autonomous window is active)
