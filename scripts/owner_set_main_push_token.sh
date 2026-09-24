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
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_REPO="${TRIAL_REPO:-d6g8k5htny-coder/trial}"
SECRET_NAME="${MAIN_PUSH_SECRET_NAME:-MAIN_PUSH_TOKEN}"
DRY_RUN=0
FROM_GH=0
DO_DISPATCH=0
DISPATCH_DIRECT_PUSH=0

die() {
  echo "owner_set_main_push_token: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

usage() {
  cat <<'EOF'
Usage: owner_set_main_push_token.sh [--dry-run] [--from-gh] [--dispatch] [--direct-push] [--help]

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
  echo "dry-run: would run: gh secret set ${SECRET_NAME} --repo ${TRIAL_REPO} --body <redacted>"
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

# Pipe token to gh secret set via stdin — never argv, never log.
# `gh secret set NAME --repo R --body -` reads body from stdin when body is `-`
# (gh >=2); fall back to env-body via process substitution if needed.
echo "setting secret ${SECRET_NAME} on ${TRIAL_REPO} (body redacted)…"
if printf '%s' "$TOKEN" | gh secret set "$SECRET_NAME" --repo "$TRIAL_REPO" --body -; then
  echo "secret_set=ok"
else
  # Older gh: --body - may not work; try without printing via env file fd
  if printf '%s' "$TOKEN" | gh secret set "$SECRET_NAME" --repo "$TRIAL_REPO"; then
    echo "secret_set=ok"
  else
    die "gh secret set failed (need admin/Secrets:Write on ${TRIAL_REPO})"
  fi
fi

# Drop token from shell memory as best-effort
TOKEN=""
unset TOKEN MAIN_PUSH_TOKEN || true

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
