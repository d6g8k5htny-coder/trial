# Integration Lab

Engineering, portability, and adversarial integration workspace for the Universal Law research federation. **This is not the research repository, is not the canonical research home, and has no scientific-status authority.**

Start with [main](https://github.com/d6g8k5htny-coder/main) for the public research program, [Math-](https://github.com/d6g8k5htny-coder/Math-) for mathematics, and [Universal-Law-Workspace](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace) for the federation map.

| Repo | Role |
|------|------|
| [`d6g8k5htny-coder/main`](https://github.com/d6g8k5htny-coder/main) | q0 / SIDE24 research program (Drive → git). Governing intent lives there. |
| **this repo** | Integration, portability, and adversarial engineering tests. No scientific authority. |

## Path C — land engineering fixes on main

Engineering only — `lemma_closed` stays **false**. This README does **not** embed a perishable device user code.

1. Open **https://github.com/login/device** → enter the **current** user code from [`portable/GH_DEVICE_LOGIN.md`](portable/GH_DEVICE_LOGIN.md) (single source of truth; see that file for the live code)
2. Or: download release **`batch218-path-c-bundle` (prior `batch207-path-c-bundle` / `batch202-path-c-bundle`)`** (or latest `*-path-c-bundle`; prior `batch199-path-c-bundle`) → `./scripts/owner_path_c_oneshot.sh`
3. Or: grant **all** AI agents (Cursor + ChatGPT/Codex + Claude + Grok) Read/write on every owner repo → [`docs/MULTI_AGENT_ACCESS.md`](docs/MULTI_AGENT_ACCESS.md) / `./scripts/owner_grant_ai_agent_access.sh` → relaunch

## #1 unblock — multi-agent App access (all owner repos)

Install is **trial-only** (`GET /installation/repositories` → only `d6g8k5htny-coder/trial`; `install_has_main=false`). Batch 224: `.cursor/environment.json` lists **all 8** visible owner repos (`google-drive`, `governance-`, `main`, `Math-`, `meta-framework`, `query-`, **`sandbox`**, `trial`) under `repositoryDependencies`. One-shot: `./scripts/owner_grant_ai_agent_access.sh` prints official install URLs for **Cursor**, **ChatGPT Codex Connector**, and **Claude** with clear **select ALL repositories including sandbox**, plus Grok PAT fallback (no verified xAI GitHub App). Current App token cannot read `sandbox` (404) until install adds it. Path C needs at least `d6g8k5htny-coder/main` **Read and write**. Full guide: [`docs/MULTI_AGENT_ACCESS.md`](docs/MULTI_AGENT_ACCESS.md). Steps also: [`docs/OWNER_ACTIONS_MAIN.md`](docs/OWNER_ACTIONS_MAIN.md).

## Intent (this repository)

- Hold lightweight probes, agent smoke checks, and notes that must not touch research registers.
- Never promote, close, or discharge a claim from the q0 program.
- Never mirror `registers/`, frozen bodies, or Drive vault material here.

## What was wrong (and what this change fixes)

Agents often land here from mobile while the live work is on `main`. Default `main` on that repo
briefly carried the q0 program via [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2), then CoS [PR #32](https://github.com/d6g8k5htny-coder/main/pull/32) reverted default tip to pre-q0 (`audit_main_alignment` → **MISALIGNED**). Hardening tip `chatgpt/drive-github-hardening-20260919`
remains ahead with portable engineering patches under `portable/patches/`.

This repository now:

1. States that boundary in the README (above).
2. Records a full audit in [`docs/PROJECT_INTENT_AUDIT.md`](docs/PROJECT_INTENT_AUDIT.md).
3. Gives the owner an exact fix plan in [`docs/OWNER_ACTIONS_MAIN.md`](docs/OWNER_ACTIONS_MAIN.md).
4. Ships a tiny sanity suite so “testing” is executable, not a blank stub.

## Portable fixes for `main` (owner apply)

Default tip is **ALIGNED** @ `1c6e74b` (Batch 66; owner [PR #41](https://github.com/d6g8k5htny-coder/main/pull/41) renew after #32/`c2b0620`). **HOLD on PR #2 is VOID**. Path A OR Path B OK when misaligned; prefer **Path B**. `./scripts/restore_main_face.sh` short-circuits when already ALIGNED. Path C portable patches on hardening BASE_TIP `b89448d` (post-#44; **no 0017**; `owner_land_path_c --dry-run` → keep hardening; Batch 69 Actions: `land-path-c-on-main.yml` dry-run default; Batch 73 CI: `land-workflows-dry-run` validates land-option-b + land-path-c **without** `MAIN_PUSH_TOKEN`; Batch 68 `path_c_rebase_helper.sh --dry-run` for first-stop ours/theirs; Batch 70 `audit_research_stack_open.py` lists OPEN premises/lemmas/prizes without flipping status). Permanent window until owner intervenes. Trial write to `main` still **403**.

This sandbox cannot push to `d6g8k5htny-coder/main`. Ready-to-apply artifacts:

- [`scripts/restore_main_face.sh`](scripts/restore_main_face.sh) — **one-command** Path B restore (ALIGNED short-circuit → dry-run → write preflight → land; `--batch N`)
- [`portable/main-default-branch/`](portable/main-default-branch/) — Option-B redirect README + `AGENTS.md` + `APPLY.md`
- [`portable/BATCH66_TOKEN_SEARCH.json`](portable/BATCH66_TOKEN_SEARCH.json) — redacted token/write probe log
- [`portable/RESTORE_PLAN_66.json`](portable/RESTORE_PLAN_66.json) — live restore plan currency
- [`portable/pr2-landing/`](portable/pr2-landing/) — checklist + `VERIFY_AFTER_MERGE.sh` for MERGEABLE PR #2
- [`portable/LAND.md`](portable/LAND.md) — Path A/B/C one-page land instructions (needs write access to `main`)
- [`portable/OWNER_ONE_LINERS.md`](portable/OWNER_ONE_LINERS.md) — copy-paste Path A (`gh pr ready/merge 2`), Path B (Actions + token), Path C (`apply_all`)
- [`portable/CONFLICTING_PR_NOTES.md`](portable/CONFLICTING_PR_NOTES.md) — rebase/close guidance for dirty drafts #3/#12
- [`portable/patches/`](portable/patches/) — engineering patches 0001–0004 + 0008–0017 + [`COMPATIBILITY.md`](portable/patches/COMPATIBILITY.md) matrix (BASE_TIP `b89448d`; tip-cut 0005/0006/0007 dropped; post-#41 topology guard in `apply_all.sh`)
- [`scripts/audit_main_alignment.py`](scripts/audit_main_alignment.py) — read-only GitHub API check (exit 0 while default tip is ALIGNED)
- [`docs/DROPBOX_GAP_AUDIT_2026-09-27.md`](docs/DROPBOX_GAP_AUDIT_2026-09-27.md) + [`scripts/dropbox_gap_audit.py`](scripts/dropbox_gap_audit.py) — byte-level diff of Dylan's Dropbox share vs Drive export + all owner-repo branches (`portable/dropbox_gap_audit_2026-09-27/`; scientific effect NONE)
- [`scripts/audit_research_stack_open.py`](scripts/audit_research_stack_open.py) — read-only OPEN premises/lemmas/prizes/claims inventory (never flips status)
- [`scripts/alignment_status.py`](scripts/alignment_status.py) — combined alignment dashboard JSON (window + Path C tip + post-#41 critical_path)
- [`scripts/watch_main_alignment.py`](scripts/watch_main_alignment.py) — timer-friendly ALIGNED/MISALIGNED watcher (embeds permanent window + route)
- [`scripts/aligned_drift_watch.py`](scripts/aligned_drift_watch.py) — drift watch (exit 0/1/2; preferred restore B vs A; snapshot; `--restore-if-writable`)
- [`portable/ALIGNED_DRIFT_SNAPSHOT.json`](portable/ALIGNED_DRIFT_SNAPSHOT.json) — tip SHA + markers snapshot from drift watch
- [`scripts/check_autonomous_window.py`](scripts/check_autonomous_window.py) — permanent/finite autonomous window gate
- [`scripts/probe_main_write.py`](scripts/probe_main_write.py) — write probe (exit 0=writable, 1=denied, 2=transport)
- [`scripts/probe_main_write_vectors.py`](scripts/probe_main_write_vectors.py) — multi-vector Path B probe dashboard
- [`scripts/path_b_dry_run.py`](scripts/path_b_dry_run.py) — Path B dry-run certainty (ALREADY_ALIGNED / would-align JSON; no push)
- [`scripts/path_c_dry_run.py`](scripts/path_c_dry_run.py) — Path C dry-run certainty (apply_all --check + post-ALIGNED tip shape; no push)
- [`scripts/path_c_rebase_helper.sh`](scripts/path_c_rebase_helper.sh) — owner-safe first-stop ours/theirs staging (`--dry-run` / `--stage`; never invent research status)
- [`scripts/refresh_restore_plan.py`](scripts/refresh_restore_plan.py) — refresh `portable/RESTORE_PLAN_<N>.json` from live probes
- [`scripts/pack_portable.sh`](scripts/pack_portable.sh) — tarball; **Batch 64+** auto-globs `RESTORE_PLAN_*.json` + `BATCH*_TOKEN_SEARCH.json`
- [`scripts/print_owner_unblock.sh`](scripts/print_owner_unblock.sh) — dump OWNER_ONE_LINERS paths + live probe/audit one-liners (reads BASE_TIP.txt)

Agent rules: [`AGENTS.md`](AGENTS.md). Autonomous work log: [`docs/AUTONOMOUS_48H_LOG.md`](docs/AUTONOMOUS_48H_LOG.md).

## Agent handoff inbox — `needs_attention/`

Blocked agents drop a card in [`needs_attention/cards/`](needs_attention/README.md); helpers cycle the folder. `scripts/needs_attention_scan.py` (read-only) refreshes `needs_attention/SNAPSHOT.json` + `TRIAGE.md` with failing-check / conflicting / changes-requested PRs across all owner repos plus expired `governance-` leases; `scripts/needs_attention_check.py` validates cards fail-closed (runs in `trial-ci`). Coordination only — scientific effect **NONE**.

Tip-drift gate: one shared classifier, `scripts/tip_drift_class.py` (landed via PR #153). Once Path C is landed (`VERIFY.path_c_landed=true`) a live hardening tip that still descends from `BASE_TIP` is lag, not drift; `BEHIND` / `DIVERGED` / `UNKNOWN` still fail. `lemma_closed=false` / `problems=0` gates keep running on the live tip (cards NA-0001, NA-0007).

## Quick check

```bash
python3 -m pytest -q
python3 scripts/audit_main_alignment.py
./scripts/pack_portable.sh /tmp/trial-portable-main-fixes.tgz
```

## Non-claims

- Nothing here updates `lemma_closed`, prize status, or premise discharge on the research program.
- A green test in `trial` is not a certificate in `main`.
