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
#       # Batch 259: dual-vector — active gh token AND durable MAIN_PUSH_TOKEN
#       # (env / well-known files) across ALL repositoryDependencies (8 incl.
#       # sandbox). App/ghs often 404s private sandbox while device /
#       # MAIN_PUSH_TOKEN is 8/8 WRITABLE; report both so App 404 is not
#       # mistaken for durable-write failure. Never prints tokens.
#       # Batch 281: ls-remote must use the same token as gh api when set —
#       # unauthenticated HTTPS always 404s private sandbox while durable
#       # write=WRITABLE (false ls_remote=not_found_or_denied).
#       # Batch 285: /installation/repositories under a user/PAT/device token
#       # returns HTTP 403 *with a JSON error body*. Pre-285 treated any
#       # non-empty stdout as a listing → names=[] + install_missing_from_deps=
#       # all 8 (false App-scope alarm) while dual-vector write was 8/8
#       # WRITABLE. Require a real `repositories` array before listing.
#       # Batch 286: key present with null/non-list still used `(repos or [])`
#       # → false install_missing=all8; require isinstance(list).
#       # Batch 323: after dual-vector probe, refresh
#       # portable/AI_AGENT_ACCESS_INVENTORY.json tip_sha / pushed_at / write
#       # (and sandbox.tip) via refresh_ai_agent_access_inventory.py. Pre-323
#       # --check only printed a pointer while tip_sha drifted. Never flips
#       # lemma_closed / never prints tokens.
#       # Batch 329: when durable token is absent in-pod (coverage=no_token),
#       # tip-refresh preserves prior durable 8/8 push/admin/sandbox.readable
#       # — ambient App pull-only must not clobber the inventory. Do not open
#       # a false no_token grant-audit eng branch for that case.
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
# Batch 259: well-known durable MAIN_PUSH_TOKEN drops (same order as
# when_writable_land / owner_set_main_push_token). Values never printed.
DURABLE_TOKEN_PATHS=(
  "/cursor/stores/self/MAIN_PUSH_TOKEN"
  "/workspace/.secrets/MAIN_PUSH_TOKEN"
  "/tmp/gh-dylan-auth/access_token"
)

die() { echo "owner_grant_ai_agent_access: ERROR: $*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: owner_grant_ai_agent_access.sh [--dry-run] [--check] [--invite-collaborators] [--help]

  (default) / --dry-run
      Print exact GitHub UI URLs + gh commands to grant Read/write on every
      repositoryDependency to Cursor, ChatGPT Codex Connector, Claude, and
      the Grok/xAI PAT fallback. No mutations.

  --check
      Probe active gh token AND durable MAIN_PUSH_TOKEN (env / well-known
      files; Batch 259 dual-vector). /installation/repositories, contents
      read, and create-ref write (probe refs deleted). Lists ALL
      repositoryDependencies (expect 8 including sandbox). Prints App
      install URLs with clear "select ALL repositories including sandbox".
      Batch 285/286: user-token 403 JSON or repositories null/non-list on
      /installation/repositories is not treated as an empty install listing
      (no false install_missing_from_deps). Batch 323: refreshes
      portable/AI_AGENT_ACCESS_INVENTORY.json tip_sha/pushed_at/write from
      the durable vector (never flips lemma_closed). Never prints tokens.

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

# Batch 259: probe one auth vector across all deps. Never prints token values.
# Args: vector_label  probe_ref_suffix
# Uses ambient GH_TOKEN / gh auth. Prints one line per repo + summary vars via
# globals: _PROBE_WRITABLE_COUNT _PROBE_SANDBOX_READ _PROBE_SANDBOX_WRITE
probe_repos_vector() {
  local vector_label="$1"
  local ref_suffix="$2"
  local r read_http tip tip_short def ls_remote write ls_url _ls_tok
  _PROBE_WRITABLE_COUNT=0
  _PROBE_SANDBOX_READ="?"
  _PROBE_SANDBOX_WRITE="DENIED"
  echo "Per-repo probe vector=${vector_label} (all ${#REPOS[@]} deps; secrets redacted):"
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
    # Also try ls-remote readability for private/out-of-scope (no token printed).
    # Batch 281: authenticate when GH_TOKEN / GITHUB_TOKEN / MAIN_PUSH_TOKEN is
    # set (durable vector exports these). Pre-281 always used bare
    # https://github.com/$r.git → private sandbox always
    # ls_remote=not_found_or_denied while gh api read=200 + write=WRITABLE.
    ls_remote="ok"
    ls_url="https://github.com/$r.git"
    _ls_tok="${GH_TOKEN:-${GITHUB_TOKEN:-${MAIN_PUSH_TOKEN:-}}}"
    if [[ -n "$_ls_tok" ]]; then
      ls_url="https://x-access-token:${_ls_tok}@github.com/$r.git"
    fi
    if ! git ls-remote "$ls_url" HEAD >/dev/null 2>&1; then
      ls_remote="not_found_or_denied"
    fi
    unset _ls_tok
    write="DENIED"
    if [[ -n "$tip" ]]; then
      # Unique per-repo probe ref (Batch 259) — avoids cross-repo reuse collisions
      # under concurrent sibling grant --check runs.
      local probe_ref="cursor-grant-probe-${ref_suffix}-${r##*/}"
      # GitHub ref names: strip trailing hyphens from short repo names like "governance-"
      probe_ref="${probe_ref%-}"
      if gh api -X POST "/repos/$r/git/refs" -f "ref=refs/heads/${probe_ref}" -f "sha=$tip" >/dev/null 2>&1; then
        write="WRITABLE"
        gh api -X DELETE "/repos/$r/git/refs/heads/${probe_ref}" >/dev/null 2>&1 || true
        _PROBE_WRITABLE_COUNT=$((_PROBE_WRITABLE_COUNT + 1))
      fi
    fi
    tip_short="${tip:0:7}"
    [[ -z "$tip_short" ]] && tip_short="?"
    echo "repo=$r read_http=${read_http:-?} write=$write tip=$tip_short ls_remote=$ls_remote"
    if [[ "$r" == "$OWNER/sandbox" ]]; then
      _PROBE_SANDBOX_READ="${read_http:-?}"
      _PROBE_SANDBOX_WRITE="$write"
    fi
  done
  echo "vector_summary=${vector_label} writable_count=${_PROBE_WRITABLE_COUNT}/${#REPOS[@]} sandbox_read=${_PROBE_SANDBOX_READ} sandbox_write=${_PROBE_SANDBOX_WRITE}"
}

discover_durable_main_push_token() {
  # Sets DURABLE_TOKEN / DURABLE_TOKEN_SOURCE. Never echoes token value.
  DURABLE_TOKEN=""
  DURABLE_TOKEN_SOURCE="none"
  if [[ -n "${MAIN_PUSH_TOKEN:-}" ]]; then
    DURABLE_TOKEN="$MAIN_PUSH_TOKEN"
    DURABLE_TOKEN_SOURCE="env:MAIN_PUSH_TOKEN"
    return 0
  fi
  if [[ -n "${GH_TOKEN:-}" ]]; then
    # Only treat GH_TOKEN as durable when it is not the Cursor App ghs token
    # that --check already used as the active vector.
    case "${GH_TOKEN}" in
      ghs_*) ;;
      *)
        DURABLE_TOKEN="$GH_TOKEN"
        DURABLE_TOKEN_SOURCE="env:GH_TOKEN"
        return 0
        ;;
    esac
  fi
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    case "${GITHUB_TOKEN}" in
      ghs_*) ;;
      *)
        DURABLE_TOKEN="$GITHUB_TOKEN"
        DURABLE_TOKEN_SOURCE="env:GITHUB_TOKEN"
        return 0
        ;;
    esac
  fi
  local path
  for path in "${DURABLE_TOKEN_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
      # strip trailing whitespace/newlines only; never echo
      DURABLE_TOKEN="$(tr -d '\r' <"$path" | sed -e 's/[[:space:]]*$//' )"
      if [[ -n "$DURABLE_TOKEN" ]]; then
        DURABLE_TOKEN_SOURCE="file:$path"
        return 0
      fi
    fi
  done
  return 1
}

if [[ "$DO_CHECK" -eq 1 ]]; then
  need_cmd gh
  need_cmd git
  echo "=== --check probe (dual-vector; no secrets printed) ==="
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
  # Batch 285: user/PAT/device tokens get HTTP 403 *with a JSON error body*
  # on /installation/repositories. Pre-285 `[[ -n "$install_json" ]]` treated
  # that body as a successful empty listing → install_has_*=False and
  # install_missing_from_deps=<all repositoryDependencies> (false App-scope
  # alarm) while dual-vector probes were 8/8 WRITABLE. Only parse when the
  # payload actually carries a repositories array.
  # Batch 286: `"repositories": null` (or a non-list) still passed the key
  # check; `(d.get("repositories") or [])` then looked like an empty App
  # install → false install_missing_from_deps=all8. Require a real list.
  install_json="$(gh api /installation/repositories 2>/dev/null || true)"
  if [[ -n "$install_json" ]]; then
    echo "$install_json" | python3 -c 'import json,sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except json.JSONDecodeError:
    print("installation: unavailable (not an App installation token, or 403)")
    raise SystemExit(0)
repos = d.get("repositories") if isinstance(d, dict) else None
if not isinstance(d, dict) or not isinstance(repos, list):
    # Error body / null / non-list — not an install listing.
    print("installation: unavailable (not an App installation token, or 403)")
    msg = d.get("message") if isinstance(d, dict) else None
    if isinstance(msg, str) and msg.strip():
        print("installation_note:", msg.strip()[:240])
    raise SystemExit(0)
names=[r.get("full_name") for r in repos if isinstance(r, dict)]
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
  echo "--- vector 1: active gh auth (often Cursor App ghs / trial-only) ---"
  probe_repos_vector "active_gh" "${TS}-a"
  ACTIVE_WRITABLE="$_PROBE_WRITABLE_COUNT"
  ACTIVE_SANDBOX_READ="$_PROBE_SANDBOX_READ"
  ACTIVE_SANDBOX_WRITE="$_PROBE_SANDBOX_WRITE"

  echo
  echo "--- vector 2: durable MAIN_PUSH_TOKEN (env / well-known files) ---"
  DURABLE_TOKEN=""
  DURABLE_TOKEN_SOURCE="none"
  if discover_durable_main_push_token; then
    echo "durable_token_source=${DURABLE_TOKEN_SOURCE} durable_token_present=1"
    # Prefer durable token for this vector only; App hosts.yml returns after unset.
    _PREV_GH_TOKEN="${GH_TOKEN:-}"
    _PREV_MAIN_PUSH_TOKEN="${MAIN_PUSH_TOKEN:-}"
    _PREV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
    export GH_TOKEN="$DURABLE_TOKEN"
    export MAIN_PUSH_TOKEN="$DURABLE_TOKEN"
    export GITHUB_TOKEN="$DURABLE_TOKEN"
    probe_repos_vector "durable_MAIN_PUSH_TOKEN" "${TS}-d"
    DURABLE_WRITABLE="$_PROBE_WRITABLE_COUNT"
    DURABLE_SANDBOX_READ="$_PROBE_SANDBOX_READ"
    DURABLE_SANDBOX_WRITE="$_PROBE_SANDBOX_WRITE"
    # Drop durable token from this shell after probe; restore prior env if any.
    unset GH_TOKEN MAIN_PUSH_TOKEN GITHUB_TOKEN DURABLE_TOKEN || true
    [[ -n "${_PREV_GH_TOKEN}" ]] && export GH_TOKEN="${_PREV_GH_TOKEN}"
    [[ -n "${_PREV_MAIN_PUSH_TOKEN}" ]] && export MAIN_PUSH_TOKEN="${_PREV_MAIN_PUSH_TOKEN}"
    [[ -n "${_PREV_GITHUB_TOKEN}" ]] && export GITHUB_TOKEN="${_PREV_GITHUB_TOKEN}"
    unset _PREV_GH_TOKEN _PREV_MAIN_PUSH_TOKEN _PREV_GITHUB_TOKEN || true
  else
    echo "durable_token_source=none durable_token_present=0"
    echo "durable_probe=skipped (no env MAIN_PUSH_TOKEN / GH_TOKEN / well-known file)"
    echo "well_known_paths: ${DURABLE_TOKEN_PATHS[*]}"
    DURABLE_WRITABLE=0
    DURABLE_SANDBOX_READ="n/a"
    DURABLE_SANDBOX_WRITE="n/a"
  fi

  echo
  echo "=== dual-vector summary (Batch 259) ==="
  echo "active_writable=${ACTIVE_WRITABLE}/${#REPOS[@]} active_sandbox_read=${ACTIVE_SANDBOX_READ} active_sandbox_write=${ACTIVE_SANDBOX_WRITE}"
  echo "durable_writable=${DURABLE_WRITABLE}/${#REPOS[@]} durable_sandbox_read=${DURABLE_SANDBOX_READ} durable_sandbox_write=${DURABLE_SANDBOX_WRITE} durable_token_source=${DURABLE_TOKEN_SOURCE}"
  if [[ "$ACTIVE_SANDBOX_READ" == "404" && "$DURABLE_SANDBOX_WRITE" == "WRITABLE" ]]; then
    echo "NOTE: App/ghs sandbox 404 while durable MAIN_PUSH_TOKEN sandbox WRITABLE — install lacks sandbox; durable write is OK. Do not treat App 404 as Path C / sibling DENIED."
  fi
  if [[ "$DURABLE_WRITABLE" -eq "${#REPOS[@]}" ]]; then
    echo "durable_sibling_coverage=8/8_WRITABLE"
  elif [[ "$DURABLE_TOKEN_SOURCE" != "none" ]]; then
    echo "durable_sibling_coverage=${DURABLE_WRITABLE}/${#REPOS[@]}"
  else
    echo "durable_sibling_coverage=no_token"
  fi
  echo
  # Batch 323: refresh living inventory tip_sha/pushed_at/write so agents do
  # not read a stale pointer file. Prefer durable token.
  # Batch 329: ambient tip-refresh preserves durable 8/8 when probe is n/a.
  # Batch 331: NEVER refresh from App/ambient when durable_token_source=none —
  # VM-local no_token would corrupt connected perm→pull + sandbox.readable
  # while live durable remains 8/8 (Batch 322 false-negative class). Skip
  # instead of relying only on writer preserve. Do not open a false no_token
  # grant-audit eng branch.
  # Writer: scripts/refresh_ai_agent_access_inventory.py (pack + CRITICAL).
  # Never flips lemma_closed / scientific_effect / flipped_anything.
  INV_PATH="$ROOT/portable/AI_AGENT_ACCESS_INVENTORY.json"
  if [[ ! -f "$INV_PATH" ]]; then
    echo "inventory_refresh=skip missing=$INV_PATH"
  elif [[ "$DURABLE_TOKEN_SOURCE" == "none" || "$DURABLE_WRITABLE" -eq 0 ]]; then
    echo "inventory_refresh=skip durable_token_source=${DURABLE_TOKEN_SOURCE} durable_writable=${DURABLE_WRITABLE} (retain living 8/8; do not App-corrupt)"
  else
    _INV_TOKEN=""
    if discover_durable_main_push_token; then
      _INV_TOKEN="$DURABLE_TOKEN"
    fi
    _PREV_GH_TOKEN="${GH_TOKEN:-}"
    _PREV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
    if [[ -n "$_INV_TOKEN" ]]; then
      export GH_TOKEN="$_INV_TOKEN"
      export GITHUB_TOKEN="$_INV_TOKEN"
    fi
    # Batch 328: do not freeze INV_BATCH at 323 — omit so the writer derives
    # living Batch N from print_owner_unblock.sh (or INV_BATCH env override).
    INV_REFRESH_OUT="$(
      INV_PATH="$INV_PATH" OWNER="$OWNER" REPOS_CSV="$(IFS=,; echo "${REPOS[*]}")" \
      DURABLE_WRITABLE="$DURABLE_WRITABLE" DURABLE_SANDBOX_READ="$DURABLE_SANDBOX_READ" \
      DURABLE_SANDBOX_WRITE="$DURABLE_SANDBOX_WRITE" ACTIVE_SANDBOX_READ="$ACTIVE_SANDBOX_READ" \
      python3 "$ROOT/scripts/refresh_ai_agent_access_inventory.py" 2>/dev/null \
        || echo "inventory_refresh=fail"
    )"
    echo "$INV_REFRESH_OUT"
    unset GH_TOKEN GITHUB_TOKEN DURABLE_TOKEN _INV_TOKEN || true
    [[ -n "${_PREV_GH_TOKEN}" ]] && export GH_TOKEN="${_PREV_GH_TOKEN}"
    [[ -n "${_PREV_GITHUB_TOKEN}" ]] && export GITHUB_TOKEN="${_PREV_GITHUB_TOKEN}"
    unset _PREV_GH_TOKEN _PREV_GITHUB_TOKEN || true
  fi
  echo
  echo "Apps are not enumerable from a ghs installation token without owner OAuth."
  echo "After installing each App (ALL repos including sandbox), re-run --check from an owner laptop gh session."
  echo "Durable Actions secret: ./scripts/owner_set_main_push_token.sh [--also-sandbox] (never prints token)."
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
