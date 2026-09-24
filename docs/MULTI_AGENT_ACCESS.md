# Multi-agent GitHub access (all Dylan repos)

**Scientific effect: NONE.** Granting AI agents Read/write does **not** flip
research status. `lemma_closed` stays **false**.

Dylan’s request: **every** AI agent he uses — ChatGPT/Codex, Claude, Grok Bot,
and Cursor (this agent) — should reach **all** `d6g8k5htny-coder` repos listed
in [`.cursor/environment.json`](../.cursor/environment.json)
`repositoryDependencies` (Batch 224: **8** repos including **`sandbox`**).

Owner one-shot (prints exact UI URLs + `gh` commands; default dry-run):

```bash
./scripts/owner_grant_ai_agent_access.sh          # dry-run (default)
./scripts/owner_grant_ai_agent_access.sh --check  # probe which apps/tokens see which repos
```

Access snapshot: [`portable/AI_AGENT_ACCESS_INVENTORY.json`](../portable/AI_AGENT_ACCESS_INVENTORY.json).

---

## Repos in scope

From `.cursor/environment.json` `repositoryDependencies` (Batch 224; keep **all 8**):

| Repo | Role |
|------|------|
| `d6g8k5htny-coder/main` | Research home (Path C target; Contents:Write required) |
| `d6g8k5htny-coder/trial` | Sandbox / this repo (Cloud Agent usually has push) |
| `d6g8k5htny-coder/sandbox` | New owner sandbox (Batch 224; add to App installs) |
| `d6g8k5htny-coder/google-drive` | Owner tooling |
| `d6g8k5htny-coder/governance-` | Owner tooling |
| `d6g8k5htny-coder/Math-` | Owner tooling |
| `d6g8k5htny-coder/meta-framework` | Owner tooling |
| `d6g8k5htny-coder/query-` | Owner tooling |

Grant **Read and write** (Contents + Metadata at minimum; Pull requests +
Workflows when agents open PRs or run Actions) on **every** row above.

When configuring each GitHub App: **select ALL repositories including sandbox**
(or “All repositories”).

---

## What each agent needs

### 1) Cursor (Cloud Agents / Bugbot) — official GitHub App

| Item | Value |
|------|--------|
| App page | https://github.com/apps/cursor |
| Install / configure | https://github.com/apps/cursor/installations/new |
| Installed apps list | https://github.com/settings/installations |
| Docs | https://cursor.com/docs/integrations/github |

**Owner steps**

1. Open the install/configure link → account `d6g8k5htny-coder`.
2. **Repository access** → add **all** eight repos (or “All repositories”) —
   **including `sandbox`**.
3. Permissions: **Read and write** on Contents (and PRs / Workflows as prompted).
4. Save. Confirm Cloud env `.cursor/environment.json` still lists all
   `repositoryDependencies`, then **RELAUNCH** a Cloud Agent from `trial`
   (mid-flight tokens stay trial-only). See
   [`portable/RELAUNCH_WITH_MAIN_SCOPE.md`](../portable/RELAUNCH_WITH_MAIN_SCOPE.md).

Live install today is often **trial-only** (`GET /installation/repositories`
→ `d6g8k5htny-coder/trial` only; `install_has_main=false`). `sandbox` is not
yet in install scope (current token gets 404 / not found on ls-remote).

### 2) ChatGPT / OpenAI Codex — official GitHub App

| Item | Value |
|------|--------|
| App page | https://github.com/apps/chatgpt-codex-connector |
| Install | https://github.com/apps/chatgpt-codex-connector/installations/new |
| Help | https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt |

**Owner steps**

1. Install **ChatGPT Codex Connector** on the personal account.
2. Select **all** eight `d6g8k5htny-coder/*` repos **including sandbox** (or all repositories).
3. In ChatGPT / Codex, connect GitHub (Apps/Plugins → GitHub) and finish OAuth.
4. Prefer **Codex** for push/edit; ChatGPT’s connector alone may be read-oriented.

Do **not** invent bot collaborator usernames. The App install is the supported path.

### 3) Anthropic Claude / Claude Code — official GitHub App

| Item | Value |
|------|--------|
| App page | https://github.com/apps/claude |
| Install | https://github.com/apps/claude/installations/new |
| Docs | https://code.claude.com/docs/en/github-actions |

**Owner steps**

1. Install **Claude** on the personal account with **all** eight repos R/W
   (**including sandbox**).
2. Optional local: in a clone, `claude` → `/install-github-app` (admin on the repo).
3. For Claude Code GitHub Action: add `ANTHROPIC_API_KEY` or
   `CLAUDE_CODE_OAUTH_TOKEN` as a repo secret (never paste into chat logs here).

### 4) Grok / xAI — **no verified official GitHub App** (as of Batch 224)

Checked and **not** used as official installs:

- `https://github.com/apps/grok` → 404
- `https://github.com/apps/xai` → 404
- `https://github.com/apps/xai-grok` → 404

Do **not** treat third-party or unverified marketplace slugs as xAI’s official App.
Grok Bot may use plugins/connectors that ask for a PAT — prefer a
**fine-grained PAT** or GitHub-hosted MCP/OAuth; **never** paste tokens into chat.

**Fallback (owner)**

1. Create a fine-grained PAT with Contents + Pull requests on **all** eight repos
   including **sandbox** (or classic `repo` + `workflow` if you accept broader scope).
2. Store it only in the agent/tool secret store (Grok Bot secret card, local env,
   Actions secret) — never in `trial` git history.
3. Optional collaborator invite **only** if Dylan sets documented bot usernames
   via env (see script). This repo does **not** invent bot logins.

Grok Build CLI (`https://docs.x.ai/build/overview`) works on a local clone;
it does not replace a GitHub App install for remote Cloud access.

### 5) Classic PAT / collaborator (generic fallback)

Use when an App path is missing or blocked:

```bash
# Owner laptop (token never printed by our scripts)
gh auth login   # repo + workflow
# or: MAIN_PUSH_TOKEN=<PAT> ./scripts/owner_set_main_push_token.sh --dispatch
```

Optional collaborator invites (script only if env provides usernames):

```bash
export AI_COLLAB_USERNAMES='login1,login2'   # owner-supplied only
./scripts/owner_grant_ai_agent_access.sh --invite-collaborators
```

---

## Current agent capability (this Cloud run)

| Capability | Status |
|------------|--------|
| Push `trial` | yes |
| Push `main` / other owner repos | **no** (403; install trial-only) |
| Read / clone `sandbox` | **no** (404 with current App token; not in install) |
| Topics / collaborators admin APIs | **no** (403 integration) |
| Device-flow user token | pending — see `portable/GH_DEVICE_LOGIN.md` |

Agents **cannot** finish App installs for you. The durable unblock is: run
`./scripts/owner_grant_ai_agent_access.sh`, complete each App UI selecting
**ALL repositories including sandbox**, then relaunch Cursor and reconnect
ChatGPT/Claude/Grok.

---

## Safety

- Never flip `lemma_closed` / prizes / premises / research status.
- Never print PATs, `ghs_`/`gho_` tokens, or device `device_code` secrets.
- Prefer docs + official App URLs over inventing bot accounts.
