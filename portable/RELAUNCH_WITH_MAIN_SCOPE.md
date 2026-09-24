# Relaunch Cloud Agent with `main` write scope

**Scientific effect: NONE.** This only unblocks Path C/B engineering lands.
**Current run cannot gain `main` write mid-flight** — env repos stay trial-only until relaunch.

Committed `.cursor/environment.json` already declares
`repositoryDependencies` → all **eight** `d6g8k5htny-coder/*` URLs (Batch 224 adds
`sandbox`; Batch 219 had seven), but a **personal**
Cloud Agent environment that booted before that merge (or without picking up the
repo-file env) still issues a **trial-only** token (`install_has_main=false`).

Pick **one** of (a)/(b)/(c), then do (d).

## (a) Cursor GitHub App — add `main` Read/Write

1. GitHub → **Settings** → **Applications** → **Cursor** → Configure  
   (https://github.com/settings/installations)  
   or install: https://github.com/apps/cursor/installations/new
2. Under **Repository access** → **Only select repositories** (or All)
3. **Add** `d6g8k5htny-coder/main` with **Read and write** (prefer **all eight** owner repos
   **including sandbox**)
4. Save

**Batch 224 — all AI agents + sandbox:** also install ChatGPT Codex Connector + Claude Apps
(and Grok via PAT) on the same **8-repo** set. On each App UI:
**select ALL repositories including sandbox**. One-shot:

```bash
./scripts/owner_grant_ai_agent_access.sh          # dry-run URLs + gh
./scripts/owner_grant_ai_agent_access.sh --check  # after installs (lists all 8)
```

Guide: [`docs/MULTI_AGENT_ACCESS.md`](../docs/MULTI_AGENT_ACCESS.md).
Inventory: [`portable/AI_AGENT_ACCESS_INVENTORY.json`](AI_AGENT_ACCESS_INVENTORY.json).

`when_writable_land.py` polls `/installation/repositories`; when
`install_has_main` flips true it attempts Path C immediately (still needs
Contents:Write). App install alone may suffice without relaunch for the App
token — but if this agent’s env `repos` list is still `[trial]`, do (d) too.

## (b) Authorize device-flow user code

1. Open https://github.com/login/device
2. Enter the **User code** from `portable/GH_DEVICE_LOGIN.md` (agent renews when expired)
3. Approve GitHub CLI with **repo** + **workflow** scopes

Poller tmux `gh-device-login` writes `/tmp/gh-dylan-auth/access_token`.
`when_writable_land.py` loads that path and lands Path C (ignore
`install_has_main`). No App install required for this path.

## (c) Trial Actions secret `MAIN_PUSH_TOKEN`

1. On **trial**: Settings → Secrets → Actions → `MAIN_PUSH_TOKEN`
   (PAT with Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`)
   **Batch 160 one-shot** (owner laptop / Codespace; token never printed):

   ```bash
   ./scripts/owner_set_main_push_token.sh --dry-run
   MAIN_PUSH_TOKEN=… ./scripts/owner_set_main_push_token.sh --dispatch
   # or reuse logged-in gh:
   ./scripts/owner_set_main_push_token.sh --from-gh --dispatch
   ```

   That runs `gh secret set MAIN_PUSH_TOKEN` on trial, then optionally
   `repository_dispatch` `land-path-c-on-main` with `dry_run=false`.
2. Either:
   - `gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false`
   - Or drop the same token into env / `/cursor/stores/self/MAIN_PUSH_TOKEN` /
     `/workspace/.secrets/MAIN_PUSH_TOKEN` for `when_writable_land.py` (never print it)

### Batch 235 — write durability (Cursor/install)

**`MAIN_PUSH_TOKEN` is now set** on `d6g8k5htny-coder/trial` (and mirrored on
`d6g8k5htny-coder/main` Actions secrets). Value never logged / never committed.

- **Cursor App install** may still be trial-only (`install_has_main=false`) mid-flight —
  that does **not** undo write durability for Path C: `land-path-c-on-main` reads the
  trial secret (not the Cloud Agent ghs token) when `dry_run=false`.
- Device-file path `/tmp/gh-dylan-auth/access_token` remains a live local vector; the
  Actions secret outlives ephemeral device sessions.
- Probe (Batch 235): `repository_dispatch` `land-path-c-on-main` `dry_run=true`
  succeeded; Actions env shows secret present (masked `***`); `owner_land_path_c.sh
  --dry-run` OK. `PATH_C_STATUS.write_durable=true`.
- Prefer **not** pushing tip keepalives solely for health when tip is already ALIGNED.

## (d) RELAUNCH Cloud Agent from `trial` (required for env token scope)

After (a) and/or after merging `.cursor/environment.json` with
`repositoryDependencies` → `main` onto trial default:

1. Start a **new** Cloud Agent from `d6g8k5htny-coder/trial`
2. Confirm env `repos` includes `github.com/d6g8k5htny-coder/main`
3. Path C/B can then use the agent GitHub token (not trial-only)


## Batch 219 — connect ALL visible owner repos

Committed `.cursor/environment.json` `repositoryDependencies` now includes **every**
public `d6g8k5htny-coder` repo visible to this auth:

- `github.com/d6g8k5htny-coder/google-drive`
- `github.com/d6g8k5htny-coder/governance-`
- `github.com/d6g8k5htny-coder/main`
- `github.com/d6g8k5htny-coder/Math-`
- `github.com/d6g8k5htny-coder/meta-framework`
- `github.com/d6g8k5htny-coder/query-`
- `github.com/d6g8k5htny-coder/trial`

**Live install** is still trial-only until (a) Cursor App repository access adds them
and (d) you **RELAUNCH**. Path C still needs Contents:Write on `main` (App R/W, device
token, or `MAIN_PUSH_TOKEN`). Scientific effect: **NONE**. `lemma_closed=false`.

## Batch 223 — multi-agent access (Cursor + Codex + Claude + Grok)

Same seven `repositoryDependencies` (pre-sandbox). Owner grants **every** agent Read/write via
official Apps (Cursor / ChatGPT Codex Connector / Claude) plus Grok PAT fallback
(no verified xAI GitHub App). See `docs/MULTI_AGENT_ACCESS.md` and
`scripts/owner_grant_ai_agent_access.sh`. After App installs: **RELAUNCH**.

## Batch 224 — add `sandbox` (8 repos)

`.cursor/environment.json` now includes `github.com/d6g8k5htny-coder/sandbox`
(owner screenshot NEW). Keep **all 8**. Live App install still trial-only;
`sandbox` returns 404 to this token until App repository access adds it.
On Cursor / Codex / Claude install UIs: **select ALL repositories including sandbox**.
Then **RELAUNCH**.


**This running agent cannot pick up `main` mid-flight.** Repositories in the
personal env stay `[trial]` until relaunch.

## Owner local one-shot (no Cloud Agent write needed)

If you prefer not to wait on Cloud scope, land Path C from your laptop using the
release tarball (`batch142-path-c-bundle` or newer):

```bash
gh release download batch142-path-c-bundle -R d6g8k5htny-coder/trial \
  -p 'trial-portable-main-fixes.tgz'
mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
/tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
```

Prerequisites: `git`, `python3`, `gh auth login` with write on `main`.
See `portable/LAND.md` and `scripts/owner_land_path_c.sh --help`.
