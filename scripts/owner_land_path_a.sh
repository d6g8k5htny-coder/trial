#!/usr/bin/env bash
# Owner Path A land: mark main PR #2 ready and merge it, then verify ALIGNED.
#
# *** HOLD (Dylan / CoS, 2026-09-23) ***
# PR #2 stays draft / untouched. Do not mark ready; do not merge; do not retarget.
# Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084
# This script hard-refuses unless OWNER_FORCE_PATH_A=1 (Dylan only).
# Preferred unblock under HOLD: Path B (./scripts/owner_land_path_b.sh).
#
# Intended to run on the owner's machine / Codespace with *owner* gh auth that
# has write on d6g8k5htny-coder/main. This trial cloud token cannot (403).
#
# Scientific effect: NONE. Packaging / default-branch face only.
# Fail-closed: any non-zero gh/audit step exits non-zero with a clear error.
#
# Usage:
#   ./scripts/owner_land_path_a.sh
#   OWNER_FORCE_PATH_A=1 ./scripts/owner_land_path_a.sh   # Dylan only, when HOLD lifted
#   TRIAL_ROOT=/path/to/trial ./scripts/owner_land_path_a.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
PR_NUMBER="${PATH_A_PR:-2}"

die() {
  echo "owner_land_path_a: ERROR: $*" >&2
  exit 1
}

# --- HOLD gate (Dylan/CoS) — fail closed before any gh pr ready/merge ---
if [[ "${OWNER_FORCE_PATH_A:-}" != "1" ]]; then
  cat >&2 <<EOF
owner_land_path_a: REFUSED — Path A (PR #${PR_NUMBER}) is on HOLD per Dylan/CoS order (2026-09-23).
  Stay draft / untouched. Do not mark ready; do not merge; do not retarget.
  Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084
  Preferred unblock: Path B → ./scripts/owner_land_path_b.sh
  (Option-B notice, or grant App write for Path B only.)
  Override (Dylan only, when HOLD explicitly lifted): OWNER_FORCE_PATH_A=1
  Scientific effect: NONE
EOF
  exit 1
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

need_cmd gh
need_cmd python3

AUDIT="$TRIAL_ROOT/scripts/audit_main_alignment.py"
WATCH="$TRIAL_ROOT/scripts/watch_main_alignment.py"
[[ -f "$AUDIT" ]] || die "missing $AUDIT (set TRIAL_ROOT to the trial checkout)"
[[ -f "$WATCH" ]] || die "missing $WATCH"

echo "=== owner_land_path_a ==="
echo "WARNING: OWNER_FORCE_PATH_A=1 set — proceeding despite HOLD gate (Dylan only)."
echo "repo=$REPO pr=#$PR_NUMBER trial_root=$TRIAL_ROOT"
echo "scientific_effect=NONE"
echo

# Confirm gh is authenticated as someone who can act on the repo.
if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated. Run: gh auth login  (use the owner account with write on $REPO)"
fi

LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-unknown}"

echo "--- preflight: PR #$PR_NUMBER ---"
if ! PR_JSON="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json number,state,isDraft,mergeable,mergeStateStatus,url 2>&1)"; then
  die "cannot view PR #$PR_NUMBER on $REPO: $PR_JSON"
fi
echo "$PR_JSON"
STATE="$(echo "$PR_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state"])')"
[[ "$STATE" == "OPEN" ]] || die "PR #$PR_NUMBER state=$STATE (need OPEN). Aborting."

echo
echo "--- gh pr ready $PR_NUMBER ---"
if ! gh pr ready "$PR_NUMBER" --repo "$REPO"; then
  die "gh pr ready failed (HTTP/GraphQL denial?). Confirm this account can mark PRs ready on $REPO. Trial cloud tokens get 403."
fi

echo
echo "--- gh pr merge $PR_NUMBER --merge ---"
if ! gh pr merge "$PR_NUMBER" --repo "$REPO" --merge; then
  die "gh pr merge failed. Confirm Contents:Write + merge rights on $REPO, and that the PR is still MERGEABLE."
fi

echo
echo "--- post-merge audit (expect ALIGNED / exit 0) ---"
set +e
python3 "$AUDIT"
audit_ec=$?
set -e
if [[ "$audit_ec" -ne 0 ]]; then
  die "audit_main_alignment exit=$audit_ec (expected 0=ALIGNED). Merge may still be propagating, or PR #$PR_NUMBER did not put q0/notice markers on default tip. Re-run: python3 $WATCH"
fi

echo
echo "--- watch_main_alignment (expect ALIGNED) ---"
set +e
python3 "$WATCH"
watch_ec=$?
set -e
if [[ "$watch_ec" -ne 0 ]]; then
  die "watch_main_alignment exit=$watch_ec (expected 0=ALIGNED)"
fi

echo
echo "owner_land_path_a: OK — default tip ALIGNED after Path A merge of PR #$PR_NUMBER."
echo "Scientific effect: NONE"
exit 0
