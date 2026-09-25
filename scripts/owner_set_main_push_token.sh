#!/usr/bin/env bash
# Owner helper (Batch 160): set trial Actions secret MAIN_PUSH_TOKEN from a
# local write-capable PAT, optionally fire repository_dispatch land-path-c
# with dry_run=false.
#
# Token sources (first wins; value NEVER printed / never logged):
#   1) env MAIN_PUSH_TOKEN
#   2) env GH_TOKEN / GITHUB_TOKEN
#   3) well-known files: /cursor/stores/self/MAIN_PUSH_TOKEN,
#      /workspace/.secrets/MAIN_PUSH_TOKEN, /tmp/gh-dylan-auth/access_token
#   4) `gh auth token` (owner gh session) when --from-gh / interactive prompt
#
# Scientific effect: NONE. lemma_closed stays false. No research promotion.
#
# Usage:
#   ./scripts/owner_set_main_push_token.sh --dry-run
#   ./scripts/owner_set_main_push_token.sh --help
#   MAIN_PUSH_TOKEN=… ./scripts/owner_set_main_push_token.sh
#   ./scripts/owner_set_main_push_token.sh --from-gh
#   ./scripts/owner_set_main_push_token.sh --dispatch   # after secret set
#   ./scripts/owner_set_main_push_token.sh --from-gh --dispatch
#   ./scripts/owner_set_main_push_token.sh --also-sandbox
#       # Batch 259: also set MAIN_PUSH_TOKEN on d6g8k5htny-coder/sandbox
#   ./scripts/owner_set_main_push_token.sh --also-main
#       # also set on d6g8k5htny-coder/main (Path C Actions)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_REPO="${TRIAL_REPO:-d6g8k5htny-coder/trial}"
SECRET_NAME="${MAIN_PUSH_SECRET_NAME:-MAIN_PUSH_TOKEN}"
DRY_RUN=0
FROM_GH=0
DO_DISPATCH=0
DISPATCH_DIRECT_PUSH=0
ALSO_SANDBOX=0
ALSO_MAIN=0
SANDBOX_REPO="${SANDBOX_REPO:-d6g8k5htny-coder/sandbox}"
MAIN_REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"

die() {
  echo "owner_set_main_push_token: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

usage() {
  cat <<'EOF'
Usage: owner_set_main_push_token.sh [--dry-run] [--from-gh] [--dispatch] [--direct-push] [--also-sandbox] [--also-main] [--help]

  --dry-run      Certainty only: show trial repo, secret name, which token
                 source would be used (never prints the token), and whether
                 gh can reach the trial repo. No secret set / no dispatch.
  --from-gh      Prefer `gh auth token` as the MAIN_PUSH_TOKEN source
                 (after env / well-known files). Useful on an owner laptop
                 already logged into gh with Contents:Write on main.
  --dispatch     After setting the secret (or in --dry-run: show intent),
                 fire repository_dispatch land-path-c-on-main with
                 dry_run=false via scripts/dispatch_land_path_c.sh --apply.
  --direct-push  With --dispatch: also pass --direct-push to the lander.
  --also-sandbox Batch 259: also set MAIN_PUSH_TOKEN on sandbox repo
                 (durable Actions secret; App install often lacks sandbox).
  --also-main    Also set MAIN_PUSH_TOKEN on d6g8k5htny-coder/main.
  -h/--help      This help.

Token sources (first non-empty wins; NEVER printed):
  env MAIN_PUSH_TOKEN
  env GH_TOKEN / GITHUB_TOKEN
  /cursor/stores/self/MAIN_PUSH_TOKEN
  /workspace/.secrets/MAIN_PUSH_TOKEN
  /tmp/gh-dylan-auth/access_token
  `gh auth token` (when --from-gh, or when none of the above exist and
   stdin is a TTY — prompts "Use gh auth token? [y/N]")

Prerequisites: gh (owner auth with Secrets:Write on trial). Token must have
Contents:Write + PullRequests:Write on d6g8k5htny-coder/main for Path C land.

Env:
  TRIAL_REPO               default d6g8k5htny-coder/trial
  SANDBOX_REPO             default d6g8k5htny-coder/sandbox
  MAIN_REPO                default d6g8k5htny-coder/main
  MAIN_PUSH_SECRET_NAME    default MAIN_PUSH_TOKEN
  MAIN_PUSH_TOKEN / GH_TOKEN / GITHUB_TOKEN — optional; never printed

Scientific effect: NONE. lemma_closed stays false. No research promotion.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --from-gh) FROM_GH=1 ;;
    --dispatch|--land|--apply) DO_DISPATCH=1 ;;
    --direct-push) DISPATCH_DIRECT_PUSH=1 ;;
    --also-sandbox) ALSO_SANDBOX=1 ;;
    --also-main) ALSO_MAIN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

need_cmd gh
need_cmd python3

TOKEN_SOURCE="none"
TOKEN=""

read_file_token() {
  local path="$1"
  if [[ -f "$path" ]]; then
    # strip trailing newlines only; never echo
    TOKEN="$(tr -d '\r' <"$path" | sed -e 's/[[:space:]]*$//' )"
    if [[ -n "$TOKEN" ]]; then
      TOKEN_SOURCE="file:$path"
      return 0
    fi
  fi
  return 1
}

if [[ -n "${MAIN_PUSH_TOKEN:-}" ]]; then
  TOKEN="$MAIN_PUSH_TOKEN"
  TOKEN_SOURCE="env:MAIN_PUSH_TOKEN"
elif [[ -n "${GH_TOKEN:-}" ]]; then
  TOKEN="$GH_TOKEN"
  TOKEN_SOURCE="env:GH_TOKEN"
elif [[ -n "${GITHUB_TOKEN:-}" ]]; then
  TOKEN="$GITHUB_TOKEN"
  TOKEN_SOURCE="env:GITHUB_TOKEN"
elif read_file_token "/cursor/stores/self/MAIN_PUSH_TOKEN"; then
  :
elif read_file_token "/workspace/.secrets/MAIN_PUSH_TOKEN"; then
  :
elif read_file_token "/tmp/gh-dylan-auth/access_token"; then
  :
fi

maybe_gh_auth_token() {
  local t
  t="$(gh auth token 2>/dev/null || true)"
  if [[ -n "$t" ]]; then
    TOKEN="$t"
    TOKEN_SOURCE="gh:auth_token"
    return 0
  fi
  return 1
}

if [[ -z "$TOKEN" ]]; then
  if [[ "$FROM_GH" -eq 1 ]]; then
    maybe_gh_auth_token || die "gh auth token returned empty (run: gh auth login)"
  elif [[ -t 0 ]]; then
    # Interactive prompt — never echo the token itself
    read -r -p "No MAIN_PUSH_TOKEN found. Use \`gh auth token\`? [y/N] " ans || true
    case "${ans:-}" in
      y|Y|yes|YES)
        maybe_gh_auth_token || die "gh auth token returned empty (run: gh auth login)"
        ;;
      *)
        die "no token source. Set MAIN_PUSH_TOKEN, drop a file, or pass --from-gh"
        ;;
    esac
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    TOKEN_SOURCE="none (dry-run; would need env/file/--from-gh)"
  else
    die "no token source (non-interactive). Set MAIN_PUSH_TOKEN, drop a file, or pass --from-gh"
  fi
elif [[ "$FROM_GH" -eq 1 && "$TOKEN_SOURCE" != "gh:auth_token" ]]; then
  # --from-gh forces gh auth token even if env/file present (owner intent)
  maybe_gh_auth_token || die "gh auth token returned empty (run: gh auth login)"
fi

# Redact helper for any accidental leak paths — never print TOKEN.
token_present=0
[[ -n "$TOKEN" ]] && token_present=1

echo "=== owner_set_main_push_token ==="
echo "trial_repo=$TRIAL_REPO"
echo "secret_name=$SECRET_NAME"
echo "mode=$([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo set-secret$([ "$DO_DISPATCH" -eq 1 ] && echo '+dispatch' || true))"
echo "token_source=$TOKEN_SOURCE"
echo "token_present=$token_present"
echo "dispatch=$([ "$DO_DISPATCH" -eq 1 ] && echo yes || echo no)"
echo "direct_push=$([ "$DISPATCH_DIRECT_PUSH" -eq 1 ] && echo yes || echo no)"
echo "also_sandbox=$([ "$ALSO_SANDBOX" -eq 1 ] && echo yes || echo no) ($SANDBOX_REPO)"
echo "also_main=$([ "$ALSO_MAIN" -eq 1 ] && echo yes || echo no) ($MAIN_REPO)"
echo "scientific_effect=NONE lemma_closed=false"

# Can we see the trial repo? (does not require Secrets:Write yet)
if gh api "repos/${TRIAL_REPO}" --jq .full_name >/tmp/owner_set_main_push_token.repo 2>/tmp/owner_set_main_push_token.repo.err; then
  echo "trial_repo_reachable=$(cat /tmp/owner_set_main_push_token.repo)"
else
  echo "trial_repo_reachable=false"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    die "cannot reach repos/${TRIAL_REPO} (gh auth / network). See /tmp/owner_set_main_push_token.repo.err"
  fi
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  # IMPORTANT: omit --body so gh reads stdin. `--body -` would set the literal
  # string "-" (gh secret set: "reads from standard input if not specified").
  echo "dry-run: would run: printf '%s' <redacted> | gh secret set ${SECRET_NAME} --repo ${TRIAL_REPO}"
  if [[ "$ALSO_SANDBOX" -eq 1 ]]; then
    echo "dry-run: would also: printf '%s' <redacted> | gh secret set ${SECRET_NAME} --repo ${SANDBOX_REPO}"
  fi
  if [[ "$ALSO_MAIN" -eq 1 ]]; then
    echo "dry-run: would also: printf '%s' <redacted> | gh secret set ${SECRET_NAME} --repo ${MAIN_REPO}"
  fi
  echo "dry-run: note: do NOT pass --body - (that stores literal hyphen, not stdin)"
  if [[ "$DO_DISPATCH" -eq 1 ]]; then
    if [[ "$DISPATCH_DIRECT_PUSH" -eq 1 ]]; then
      echo "dry-run: would run: $ROOT/scripts/dispatch_land_path_c.sh --apply --direct-push"
    else
      echo "dry-run: would run: $ROOT/scripts/dispatch_land_path_c.sh --apply"
    fi
    echo "dry-run: repository_dispatch land-path-c-on-main dry_run=false"
  fi
  echo "dry-run: OK (no secret written; no dispatch fired)"
  echo "Scientific effect: NONE. lemma_closed stays false. No research promotion."
  exit 0
fi

[[ "$token_present" -eq 1 ]] || die "refusing to set empty secret"

# Batch 259: gh secret set authenticates as the ambient gh host token
# (often Cursor App ghs with Secrets:Write 403). Prefer the discovered
# write-capable TOKEN as GH_TOKEN for the API calls — same value that is
# being stored as the Actions secret body. Never print it.
_PREV_GH_TOKEN="${GH_TOKEN:-}"
_PREV_GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export GH_TOKEN="$TOKEN"
export GITHUB_TOKEN="$TOKEN"

set_secret_on_repo() {
  local repo="$1"
  echo "setting secret ${SECRET_NAME} on ${repo} (body redacted; auth=discovered_token)…"
  if printf '%s' "$TOKEN" | gh secret set "$SECRET_NAME" --repo "$repo"; then
    echo "secret_set=ok repo=${repo}"
  else
    # restore prior auth before die so caller shell is not left poisoned
    unset GH_TOKEN GITHUB_TOKEN || true
    [[ -n "${_PREV_GH_TOKEN}" ]] && export GH_TOKEN="${_PREV_GH_TOKEN}"
    [[ -n "${_PREV_GITHUB_TOKEN}" ]] && export GITHUB_TOKEN="${_PREV_GITHUB_TOKEN}"
    die "gh secret set failed on ${repo} (need admin/Secrets:Write)"
  fi
}

# Pipe token to gh secret set via stdin — never argv, never log.
# gh secret set: "--body reads from standard input if not specified".
# Do NOT pass `--body -` — that stores the literal string "-" as the secret.
set_secret_on_repo "$TRIAL_REPO"
if [[ "$ALSO_SANDBOX" -eq 1 ]]; then
  set_secret_on_repo "$SANDBOX_REPO"
fi
if [[ "$ALSO_MAIN" -eq 1 ]]; then
  set_secret_on_repo "$MAIN_REPO"
fi

# Drop token from shell memory as best-effort; restore prior gh auth.
TOKEN=""
unset TOKEN MAIN_PUSH_TOKEN GH_TOKEN GITHUB_TOKEN || true
[[ -n "${_PREV_GH_TOKEN}" ]] && export GH_TOKEN="${_PREV_GH_TOKEN}"
[[ -n "${_PREV_GITHUB_TOKEN}" ]] && export GITHUB_TOKEN="${_PREV_GITHUB_TOKEN}"
unset _PREV_GH_TOKEN _PREV_GITHUB_TOKEN || true

if [[ "$DO_DISPATCH" -eq 1 ]]; then
  echo "dispatching land-path-c-on-main dry_run=false…"
  DISPATCH_ARGS=(--apply)
  if [[ "$DISPATCH_DIRECT_PUSH" -eq 1 ]]; then
    DISPATCH_ARGS+=(--direct-push)
  fi
  "$ROOT/scripts/dispatch_land_path_c.sh" "${DISPATCH_ARGS[@]}"
  echo "dispatch=ok"
else
  echo "dispatch=skipped (pass --dispatch to fire land-path-c dry_run=false)"
  echo "next: gh workflow run land-path-c-on-main --repo ${TRIAL_REPO} -f dry_run=false"
  echo "  or: $ROOT/scripts/dispatch_land_path_c.sh --apply"
fi

echo "owner_set_main_push_token: DONE"
echo "Scientific effect: NONE. lemma_closed stays false. No research promotion."
exit 0
