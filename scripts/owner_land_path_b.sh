#!/usr/bin/env bash
# Owner Path B land: apply Option-B default-branch notice onto d6g8k5htny-coder/main.
#
# Default (safer): clone default main, git am the Option-B format-patch, push a
# notice branch, open a PR into main. Owner merges that PR, then this script
# (or a re-run with --after-merge) verifies remote ALIGNED.
#
# Opt-in: --direct-main pushes the notice commit straight onto default main
# (no PR). Use only when the owner explicitly wants that.
#
# Intended to run on the owner's machine / Codespace with *owner* gh/git auth
# that has write on d6g8k5htny-coder/main. This trial cloud token cannot (403).
#
# Scientific effect: NONE. Documentation-only redirect until Path A.
# Fail-closed: clear errors on missing patch, am failure, push denial, auditor fail.
#
# Usage:
#   ./scripts/owner_land_path_b.sh
#   ./scripts/owner_land_path_b.sh --dry-run      # certainty JSON; no push/PR
#   ./scripts/owner_land_path_b.sh --direct-main
#   ./scripts/owner_land_path_b.sh --after-merge   # remote audit/watch only
#   TRIAL_ROOT=/path/to/trial ./scripts/owner_land_path_b.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
BRANCH="${PATH_B_BRANCH:-cursor/option-b-notice-from-owner}"
WORKDIR="${PATH_B_WORKDIR:-}"
DIRECT_MAIN=0
AFTER_MERGE=0
DRY_RUN=0

die() {
  echo "owner_land_path_b: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

usage() {
  cat <<'EOF'
Usage: owner_land_path_b.sh [--dry-run | --direct-main | --after-merge] [--help]

  (default)     Clone default main, git am Option-B, push branch, open PR.
                Then print merge instruction + local auditor result.
  --dry-run     Certainty only: clone + git am + local auditor JSON via
                scripts/path_b_dry_run.py. No push, no PR, no gh auth required.
  --direct-main Opt-in: commit Option-B onto default main and push (no PR).
  --after-merge Skip land; run remote audit_main_alignment + watch (expect ALIGNED).

Env:
  TRIAL_ROOT     Path to trial checkout (default: repo containing this script)
  MAIN_REPO      Override target repo (default: d6g8k5htny-coder/main)
  PATH_B_BRANCH  Notice branch name (default: cursor/option-b-notice-from-owner)
  PATH_B_WORKDIR Existing clone dir to reuse (optional)
  MAIN_PUSH_TOKEN / GH_TOKEN — optional; gh/git use owner auth by default
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --direct-main) DIRECT_MAIN=1 ;;
    --after-merge) AFTER_MERGE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

MODE_COUNT=$((DRY_RUN + DIRECT_MAIN + AFTER_MERGE))
if [[ "$MODE_COUNT" -gt 1 ]]; then
  die "choose at most one of --dry-run / --direct-main / --after-merge"
fi

need_cmd git
need_cmd python3

PATCH="$TRIAL_ROOT/portable/main-default-branch/0001-option-b-default-branch-notice.patch"
AUDIT_LOCAL="$TRIAL_ROOT/scripts/audit_local_tree.py"
AUDIT_REMOTE="$TRIAL_ROOT/scripts/audit_main_alignment.py"
WATCH="$TRIAL_ROOT/scripts/watch_main_alignment.py"
DRY_RUN_PY="$TRIAL_ROOT/scripts/path_b_dry_run.py"

[[ -f "$PATCH" ]] || die "missing Option-B patch: $PATCH (set TRIAL_ROOT)"
[[ -f "$AUDIT_LOCAL" ]] || die "missing $AUDIT_LOCAL"
[[ -f "$AUDIT_REMOTE" ]] || die "missing $AUDIT_REMOTE"
[[ -f "$WATCH" ]] || die "missing $WATCH"
[[ -f "$DRY_RUN_PY" ]] || die "missing $DRY_RUN_PY"

echo "=== owner_land_path_b ==="
echo "repo=$REPO trial_root=$TRIAL_ROOT"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "mode=dry-run"
elif [[ "$AFTER_MERGE" -eq 1 ]]; then
  echo "mode=after-merge"
elif [[ "$DIRECT_MAIN" -eq 1 ]]; then
  echo "mode=direct-main"
else
  echo "mode=branch+PR"
fi
echo "scientific_effect=NONE"
echo

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "--- path_b_dry_run certainty (no push) ---"
  set +e
  python3 "$DRY_RUN_PY"
  dry_ec=$?
  set -e
  if [[ "$dry_ec" -ne 0 ]]; then
    die "dry-run certainty failed (exit=$dry_ec). Patch may not would-align against live tip."
  fi
  echo
  echo "owner_land_path_b: dry-run OK — would-align=true. Re-run without --dry-run to land."
  echo "Scientific effect: NONE"
  exit 0
fi

# Batch 227: CI Intent flake — audit/watch can return exit 2 (transport /
# RemoteDisconnected / rate limit) even when tip is ALIGNED. Retry briefly
# like wait_until_aligned.sh; only fail-closed on persistent MISALIGNED/errors.
TRANSPORT_RETRIES="${PATH_B_TRANSPORT_RETRIES:-3}"
TRANSPORT_SLEEP_S="${PATH_B_TRANSPORT_SLEEP_S:-2}"

run_remote_audit() {
  local attempt=1
  local audit_ec=0
  local watch_ec=0
  while [[ "$attempt" -le "$TRANSPORT_RETRIES" ]]; do
    echo "--- remote audit_main_alignment (expect ALIGNED / exit 0; attempt $attempt/$TRANSPORT_RETRIES) ---"
    set +e
    python3 "$AUDIT_REMOTE"
    audit_ec=$?
    set -e
    if [[ "$audit_ec" -eq 2 ]]; then
      echo "owner_land_path_b: audit transport (exit=2); retrying in ${TRANSPORT_SLEEP_S}s..." >&2
      sleep "$TRANSPORT_SLEEP_S"
      attempt=$((attempt + 1))
      continue
    fi
    if [[ "$audit_ec" -ne 0 ]]; then
      die "audit_main_alignment exit=$audit_ec (expected 0=ALIGNED). If you just merged, wait a few seconds and re-run with --after-merge."
    fi
    echo
    echo "--- watch_main_alignment (expect ALIGNED; attempt $attempt/$TRANSPORT_RETRIES) ---"
    set +e
    python3 "$WATCH"
    watch_ec=$?
    set -e
    if [[ "$watch_ec" -eq 2 ]]; then
      echo "owner_land_path_b: watch transport (exit=2); retrying in ${TRANSPORT_SLEEP_S}s..." >&2
      sleep "$TRANSPORT_SLEEP_S"
      attempt=$((attempt + 1))
      continue
    fi
    if [[ "$watch_ec" -ne 0 ]]; then
      die "watch_main_alignment exit=$watch_ec (expected 0=ALIGNED)"
    fi
    echo
    echo "owner_land_path_b: OK — default tip ALIGNED."
    echo "Scientific effect: NONE"
    return 0
  done
  die "audit/watch transport exhausted after $TRANSPORT_RETRIES attempts (last audit=$audit_ec watch=$watch_ec)"
}

# --after-merge is read-only python audit/watch; no gh write auth required
# (Batch 74: Intent suite / anonymous CI must pass when tip is already ALIGNED).
if [[ "$AFTER_MERGE" -eq 1 ]]; then
  run_remote_audit
  exit 0
fi

need_cmd gh
if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated. Run: gh auth login  (owner account with write on $REPO)"
fi
LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-unknown}"

# --- land (branch+PR or direct-main) ---
if [[ -z "$WORKDIR" ]]; then
  WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/owner-path-b.XXXXXX")"
  CLEANUP_WORKDIR=1
else
  CLEANUP_WORKDIR=0
fi
cleanup() {
  if [[ "${CLEANUP_WORKDIR:-0}" -eq 1 && -n "${WORKDIR:-}" && -d "$WORKDIR" ]]; then
    rm -rf "$WORKDIR"
  fi
}
trap cleanup EXIT

echo "workdir=$WORKDIR"
echo "--- clone default main ---"
if ! git clone --depth 50 "https://github.com/${REPO}.git" "$WORKDIR/main"; then
  die "git clone failed for $REPO (transport). Check network / credentials."
fi
cd "$WORKDIR/main"
git config user.name "${GIT_AUTHOR_NAME:-owner-land-path-b}"
git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"

DEFAULT_TIP="$(git rev-parse HEAD)"
echo "default_tip=$DEFAULT_TIP"

# Prefer authenticated remote so push uses owner token via gh.
# gh auth setup-git configures https credential helper when available.
gh auth setup-git 2>/dev/null || true

if [[ "$DIRECT_MAIN" -eq 1 ]]; then
  echo "--- --direct-main: staying on default branch ---"
  git checkout main 2>/dev/null || git checkout -B main
else
  echo "--- checkout notice branch: $BRANCH ---"
  git checkout -B "$BRANCH"
fi

# Idempotent: skip am only when tip already carries the Option-B *notice*
# (not Dylan's honest program-map, which still trips complexity markers).
already_option_b() {
  local readme="${1:-README.md}"
  [[ -f "$readme" ]] || return 1
  grep -q 'q0 Research Program' "$readme" 2>/dev/null \
    && grep -qE 'SIDE24|default branch notice' "$readme" 2>/dev/null \
    && ! grep -q 'complexity-physics-framework' "$readme" 2>/dev/null \
    && ! grep -q 'Multiscale Retrodiction Complexity' "$readme" 2>/dev/null
}

if already_option_b README.md; then
  echo "README already looks post-Option-B / q0 notice; skipping git am."
else
  echo "--- git am Option-B format-patch ---"
  if ! git am "$PATCH"; then
    git am --abort 2>/dev/null || true
    die "git am failed for $PATCH. Default tip may have moved; regenerate portable/main-default-branch/0001-*.patch against current main."
  fi
fi

echo "README head:"
head -8 README.md || true

echo
echo "--- local auditor (must ALIGNED / would-align) ---"
if ! python3 "$AUDIT_LOCAL" .; then
  die "audit_local_tree failed — post-Option-B tree would NOT satisfy remote audit. Fix the patch before pushing."
fi
echo "Local auditor: would-align=true"

if [[ "$DIRECT_MAIN" -eq 1 ]]; then
  echo
  echo "--- push default main (opt-in --direct-main) ---"
  if ! git push origin HEAD:main; then
    die "git push to main denied. Confirm this account has Contents:Write on $REPO (trial cloud tokens get 403)."
  fi
  echo "Pushed Option-B onto default main."
  echo
  # Brief pause for GitHub raw/API tip propagation
  sleep 2
  run_remote_audit
  exit 0
fi

echo
echo "--- push notice branch $BRANCH ---"
if ! git push -u origin "HEAD:refs/heads/${BRANCH}"; then
  if ! git push -u --force origin "HEAD:refs/heads/${BRANCH}"; then
    die "git push denied for branch $BRANCH. Confirm Contents:Write on $REPO (expected 403 without owner auth)."
  fi
  echo "Pushed $BRANCH with --force (non-ff)."
fi
echo "Pushed branch $BRANCH."

TITLE="docs: q0 redirect on default main (Option-B from owner script)"
BODY="$(cat <<'EOF'
Option-B default-branch notice via `scripts/owner_land_path_b.sh`.

Scientific effect: **NONE**. Documentation-only redirect on default `main`
(MISALIGNED after CoS PR #32 reverted PR #2). HOLD on PR #2 is **VOID**.

Path B is preferred for ALIGNED. Optional full-stack Path A:
```bash
PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
```

After merging this notice PR, verify:
```bash
./scripts/owner_land_path_b.sh --after-merge
```
EOF
)"

echo
echo "--- open or reuse PR into default main ---"
EXISTING="$(gh pr list --repo "$REPO" --head "$BRANCH" --base main --state open --json number,url --jq '.[0].url // empty' || true)"
if [[ -n "$EXISTING" ]]; then
  PR_URL="$EXISTING"
  echo "Reusing open PR: $PR_URL"
else
  if ! PR_URL="$(gh pr create --repo "$REPO" --base main --head "$BRANCH" --title "$TITLE" --body "$BODY")"; then
    die "gh pr create failed (need PullRequests:Write). Branch is pushed: $BRANCH — open manually: https://github.com/${REPO}/compare/main...${BRANCH}"
  fi
  echo "Opened notice PR: $PR_URL"
fi

echo
echo "=== NEXT (owner) ==="
echo "1. Review and merge: $PR_URL"
echo "2. Verify ALIGNED:"
echo "     $TRIAL_ROOT/scripts/owner_land_path_b.sh --after-merge"
echo
echo "owner_land_path_b: branch+PR ready (not yet on default tip)."
echo "Local would-align=true. Remote ALIGNED after you merge the PR."
echo "Scientific effect: NONE"
exit 0
