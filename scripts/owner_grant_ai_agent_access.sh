#!/usr/bin/env bash
# Owner one-shot: grant Cursor / ChatGPT Codex / Claude / Grok(+PAT) access
# to ALL d6g8k5htny-coder repos listed in .cursor/environment.json.
#
# Scientific effect: NONE. lemma_closed stays false. Never prints tokens.
#
# Usage:
#   ./scripts/owner_grant_ai_agent_access.sh              # dry-run (default)
#   ./scripts/owner_grant_ai_agent_access.sh --dry-run     # same
#   ./scripts/owner_grant_ai_agent_access.sh --check       # probe install + pulls
#   ./scripts/owner_grant_ai_agent_access.sh --invite-collaborators
#       # only if AI_COLLAB_USERNAMES env lists real logins (comma-separated)
#   ./scripts/owner_grant_ai_agent_access.sh --help
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWNER="${OWNER:-d6g8k5htny-coder}"
ENV_JSON="${ENV_JSON:-$ROOT/.cursor/environment.json}"
DRY_RUN=1
DO_CHECK=0
DO_INVITE=0

die() { echo "owner_grant_ai_agent_access: ERROR: $*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: owner_grant_ai_agent_access.sh [--dry-run] [--check] [--invite-collaborators] [--help]

  (default) / --dry-run
      Print exact GitHub UI URLs + gh commands to grant Read/write on every
      repositoryDependency to Cursor, ChatGPT Codex Connector, Claude, and
      the Grok/xAI PAT fallback. No mutations.

  --check
      Probe current token: /installation/repositories, contents read, and
      create-ref write (probe refs deleted). Lists ALL repositoryDependencies
      (expect 8 including sandbox). Prints App install URLs with clear
      "select ALL repositories including sandbox". Never prints tokens.

  --invite-collaborators
      Invite collaborators ONLY when AI_COLLAB_USERNAMES is set to a
      comma-separated list of real GitHub logins Dylan provides.
      Does NOT invent bot usernames. Still dry-run unless
      AI_COLLAB_APPLY=1.

  -h / --help
      This help.

Official App install URLs (do not invent alternatives):
  Cursor:    https://github.com/apps/cursor/installations/new
  Codex:     https://github.com/apps/chatgpt-codex-connector/installations/new
  Claude:    https://github.com/apps/claude/installations/new
  Grok/xAI:  no verified official GitHub App → fine-grained PAT / optional collab

  On each install UI: select ALL repositories including sandbox.

Docs: docs/MULTI_AGENT_ACCESS.md
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --check) DO_CHECK=1; DRY_RUN=0; shift ;;
    --invite-collaborators) DO_INVITE=1; DRY_RUN=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown arg: $1 (try --help)" ;;
  esac
done

need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"; }
need_cmd python3

list_repos() {
  python3 - <<'PY' "$ENV_JSON" "$OWNER"
import json, re, sys
path, owner = sys.argv[1], sys.argv[2]
raw = open(path, encoding="utf-8").read()
# Strip // line comments for JSONC environment.json
lines = []
for line in raw.splitlines():
    if line.lstrip().startswith("//"):
        continue
    lines.append(line)
text = "\n".join(lines)
# Also strip trailing commas before ] or }
text = re.sub(r",\s*([}\]])", r"\1", text)
data = json.loads(text)
deps = data.get("repositoryDependencies") or []
repos = []
for d in deps:
    d = d.strip().rstrip("/")
    if d.startswith("github.com/"):
        d = d[len("github.com/"):]
    if d.startswith(owner + "/"):
        repos.append(d)
    else:
        repos.append(f"{owner}/{d.split('/')[-1]}")
# unique preserve order
seen = set()
out = []
for r in repos:
    if r not in seen:
        seen.add(r)
        out.append(r)
print("\n".join(out))
PY
}

REPOS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && REPOS+=("$line")
done < <(list_repos)
[[ ${#REPOS[@]} -gt 0 ]] || die "no repositoryDependencies in $ENV_JSON"

HAS_SANDBOX=0
for r in "${REPOS[@]}"; do
  [[ "$r" == "$OWNER/sandbox" ]] && HAS_SANDBOX=1
done

echo "=== Multi-agent GitHub access (Batch 224) ==="
echo "Scientific effect: NONE. lemma_closed stays false. Never print tokens."
echo "Owner: $OWNER"
echo "Repos (${#REPOS[@]}; expect 8 including sandbox):"
for r in "${REPOS[@]}"; do
  if [[ "$r" == "$OWNER/sandbox" ]]; then
    echo "  - $r   ← NEW (Batch 224); must be on every App install"
  else
    echo "  - $r"
  fi
done
if [[ "$HAS_SANDBOX" -ne 1 ]]; then
  echo "WARNING: sandbox missing from repositoryDependencies — add github.com/$OWNER/sandbox"
fi
if [[ ${#REPOS[@]} -lt 8 ]]; then
  echo "WARNING: expected 8 repos, got ${#REPOS[@]}"
fi
echo

echo "=== App install URLs — select ALL repositories including sandbox ==="
echo "  CRITICAL: On each install UI below, choose Repository access →"
echo "            All repositories  OR  select every row listed above"
echo "            (must include $OWNER/sandbox)."
echo
echo "  1) Cursor"
echo "       App:     https://github.com/apps/cursor"
echo "       Install: https://github.com/apps/cursor/installations/new"
echo "       Config:  https://github.com/settings/installations"
echo "       → select ALL repositories including sandbox"
echo
echo "  2) ChatGPT / Codex (ChatGPT Codex Connector)"
echo "       App:     https://github.com/apps/chatgpt-codex-connector"
echo "       Install: https://github.com/apps/chatgpt-codex-connector/installations/new"
echo "       → select ALL repositories including sandbox"
echo
echo "  3) Claude"
echo "       App:     https://github.com/apps/claude"
echo "       Install: https://github.com/apps/claude/installations/new"
echo "       → select ALL repositories including sandbox"
echo
echo "  4) Grok / xAI — no verified official GitHub App (PAT fallback)"
echo "       Fine-grained PAT: https://github.com/settings/personal-access-tokens"
echo "       → grant Contents + Pull requests on ALL ${#REPOS[@]} repos including sandbox"
echo

echo "=== 1) Cursor GitHub App — add ALL repos Read/write ==="
echo "  App page:     https://github.com/apps/cursor"
echo "  Install/new:  https://github.com/apps/cursor/installations/new"
echo "  Configure:    https://github.com/settings/installations"
echo "  Docs:         https://cursor.com/docs/integrations/github"
echo "  Steps:"
echo "    1. Open Install/new → select account $OWNER"
echo "    2. Repository access → All repositories OR select ALL including sandbox:"
for r in "${REPOS[@]}"; do echo "         • $r"; done
echo "    3. Permissions: Contents Read/write (+ PRs / Workflows as prompted)"
echo "    4. Save → RELAUNCH Cloud Agent from trial (see portable/RELAUNCH_WITH_MAIN_SCOPE.md)"
echo "  gh (owner laptop, after App install — list what Cursor install sees):"
echo "    gh api /installation/repositories --jq '{total_count,names:[.repositories[].full_name]}'"
echo

echo "=== 2) OpenAI ChatGPT / Codex — ChatGPT Codex Connector ==="
echo "  App page:     https://github.com/apps/chatgpt-codex-connector"
echo "  Install/new:  https://github.com/apps/chatgpt-codex-connector/installations/new"
echo "  Help:         https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt"
echo "  Steps:"
echo "    1. Install App on $OWNER — select ALL repositories including sandbox (R/W for Codex push)"
echo "    2. In ChatGPT/Codex: Apps/Plugins → GitHub → connect + authorize"
echo "    3. Prefer Codex for generate/edit/push; ChatGPT connector may be read-oriented"
echo "  Do not invent OpenAI bot collaborator usernames — use the App."
echo

echo "=== 3) Anthropic Claude / Claude Code — Claude GitHub App ==="
echo "  App page:     https://github.com/apps/claude"
echo "  Install/new:  https://github.com/apps/claude/installations/new"
echo "  Docs:         https://code.claude.com/docs/en/github-actions"
echo "  Steps:"
echo "    1. Install App on $OWNER — select ALL repositories including sandbox (Contents/Issues/PRs R/W)"
echo "    2. Optional: in a local clone run claude → /install-github-app"
echo "    3. Optional Actions: add ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN secret"
echo "  Do not invent Claude bot collaborator usernames — use the App."
echo

echo "=== 4) Grok / xAI — no verified official GitHub App ==="
echo "  Checked (not official installs): /apps/grok /apps/xai /apps/xai-grok → 404"
echo "  Fallback: fine-grained PAT with Contents + Pull requests on ALL repos including sandbox"
echo "    https://github.com/settings/personal-access-tokens"
echo "  Store PAT only in the tool secret store / env — never paste into chat."
echo "  Grok Build CLI (local clone): https://docs.x.ai/build/overview"
echo "  Optional collaborator path: set AI_COLLAB_USERNAMES then --invite-collaborators"
echo

echo "=== 5) Generic PAT / device / MAIN_PUSH_TOKEN (any agent) ==="
echo "  Device: https://github.com/login/device  (live code: portable/GH_DEVICE_LOGIN.md)"
echo "  Trial secret: ./scripts/owner_set_main_push_token.sh --dry-run"
echo "  Path C after write: ./scripts/owner_path_c_oneshot.sh --from-bundle"
echo

if [[ "$DO_CHECK" -eq 1 ]]; then
  need_cmd gh
  echo "=== --check probe (current gh token; no secrets printed) ==="
  echo "Expected repos (${#REPOS[@]}):"
  n=0
  for r in "${REPOS[@]}"; do
    n=$((n + 1))
    mark=""
    [[ "$r" == "$OWNER/sandbox" ]] && mark=" [sandbox — must appear on App installs]"
    echo "  $n. $r$mark"
  done
  echo
  echo "App install URLs (re-print for owner):"
  echo "  Cursor → https://github.com/apps/cursor/installations/new"
  echo "           select ALL repositories including sandbox"
  echo "  Codex  → https://github.com/apps/chatgpt-codex-connector/installations/new"
  echo "           select ALL repositories including sandbox"
  echo "  Claude → https://github.com/apps/claude/installations/new"
  echo "           select ALL repositories including sandbox"
  echo
  install_json="$(gh api /installation/repositories 2>/dev/null || true)"
  if [[ -n "$install_json" ]]; then
    echo "$install_json" | python3 -c 'import json,sys
d=json.load(sys.stdin)
names=[r.get("full_name") for r in d.get("repositories") or []]
print("installation:", json.dumps({"total_count":d.get("total_count"),"repository_selection":d.get("repository_selection"),"names":names}, indent=2))
print("install_has_main:", any(n=="'"$OWNER"'/main" for n in names))
print("install_has_sandbox:", any(n=="'"$OWNER"'/sandbox" for n in names))
missing=[r for r in """'"$(printf '%s\n' "${REPOS[@]}")"'""".strip().splitlines() if r and r not in names]
print("install_missing_from_deps:", missing)'
  else
    echo "installation: unavailable (not an App installation token, or 403)"
  fi
  TS="$(date +%s)"
  echo
  echo "Per-repo probe (all ${#REPOS[@]} deps):"
  for r in "${REPOS[@]}"; do
    # Avoid SIGPIPE under pipefail: do not pipe gh into head.
    read_http="$(gh api -i "/repos/$r/contents/README.md" 2>/dev/null | awk 'NR==1{print $2; exit}' || true)"
    tip="$(gh api "/repos/$r/git/ref/heads/main" --jq .object.sha 2>/dev/null || true)"
    # Reject non-SHA junk (e.g. JSON error bodies when repo is 404)
    if [[ ! "$tip" =~ ^[0-9a-f]{7,40}$ ]]; then
      tip=""
    fi
    if [[ -z "$tip" ]]; then
      def="$(gh api "/repos/$r" --jq .default_branch 2>/dev/null || echo main)"
      tip="$(gh api "/repos/$r/git/ref/heads/$def" --jq .object.sha 2>/dev/null || true)"
      if [[ ! "$tip" =~ ^[0-9a-f]{7,40}$ ]]; then
        tip=""
      fi
    fi
    # Also try ls-remote readability for private/out-of-scope (no token printed)
    ls_remote="ok"
    if ! git ls-remote "https://github.com/$r.git" HEAD >/dev/null 2>&1; then
      ls_remote="not_found_or_denied"
    fi
    write="DENIED"
    if [[ -n "$tip" ]]; then
      if gh api -X POST "/repos/$r/git/refs" -f "ref=refs/heads/cursor-grant-probe-$TS" -f "sha=$tip" >/dev/null 2>&1; then
        write="WRITABLE"
        gh api -X DELETE "/repos/$r/git/refs/heads/cursor-grant-probe-$TS" >/dev/null 2>&1 || true
      fi
    fi
    tip_short="${tip:0:7}"
    [[ -z "$tip_short" ]] && tip_short="?"
    echo "repo=$r read_http=${read_http:-?} write=$write tip=$tip_short ls_remote=$ls_remote"
  done
  echo
  echo "Apps are not enumerable from a ghs installation token without owner OAuth."
  echo "After installing each App (ALL repos including sandbox), re-run --check from an owner laptop gh session."
  echo
fi

if [[ "$DO_INVITE" -eq 1 ]]; then
  need_cmd gh
  USERS_RAW="${AI_COLLAB_USERNAMES:-}"
  if [[ -z "$USERS_RAW" ]]; then
    echo "=== --invite-collaborators SKIPPED ==="
    echo "  Set AI_COLLAB_USERNAMES='login1,login2' with real GitHub logins Dylan provides."
    echo "  This script refuses to invent bot usernames."
    echo "  Example dry print:"
    for r in "${REPOS[@]}"; do
      echo "    # gh api -X PUT /repos/$r/collaborators/LOGIN -f permission=push"
    done
  else
    APPLY="${AI_COLLAB_APPLY:-0}"
    IFS=',' read -r -a USERS <<< "$USERS_RAW"
    echo "=== --invite-collaborators (AI_COLLAB_APPLY=$APPLY) ==="
    for login in "${USERS[@]}"; do
      login="$(echo "$login" | tr -d '[:space:]')"
      [[ -z "$login" ]] && continue
      for r in "${REPOS[@]}"; do
        cmd=(gh api -X PUT "/repos/$r/collaborators/$login" -f permission=push)
        if [[ "$APPLY" == "1" ]]; then
          echo "APPLY: ${cmd[*]}"
          "${cmd[@]}" >/dev/null && echo "  invited $login → $r" || echo "  FAILED $login → $r"
        else
          echo "DRY: ${cmd[*]}   # set AI_COLLAB_APPLY=1 to execute"
        fi
      done
    done
  fi
  echo
fi

if [[ "$DRY_RUN" -eq 1 && "$DO_CHECK" -eq 0 && "$DO_INVITE" -eq 0 ]]; then
  echo "=== dry-run complete (default) ==="
  echo "No mutations. Owner: open the three App install URLs,"
  echo "select ALL repositories including sandbox (R/W),"
  echo "then PAT/device for Grok + Path C. Re-run with --check after installs."
fi

echo
echo "See: docs/MULTI_AGENT_ACCESS.md"
echo "Inventory: portable/AI_AGENT_ACCESS_INVENTORY.json"
echo "Relaunch: portable/RELAUNCH_WITH_MAIN_SCOPE.md"
exit 0
