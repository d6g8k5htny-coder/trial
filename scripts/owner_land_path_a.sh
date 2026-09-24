#!/usr/bin/env bash
# Owner Path A land: restore q0 default tip on d6g8k5htny-coder/main.
#
# *** Batch 54 OWNER OVERRIDE (Dylan Roy) ***
# HOLD on PR #2 is VOID. Agents may Path A OR Path B. Prefer Path B
# (./scripts/owner_land_path_b.sh) — minimal notice-only — over re-merging
# the full PR #2 stack unless Path B is impossible.
#
# Context: PR #2 MERGED @ b040bf0c, then CoS PR #32 REVERTED it @ 4fc1d7c
# (MISALIGNED pre-q0 face). `gh pr ready/merge 2` cannot revive a closed PR.
#
# Path A tactics (pick one; write creds required):
#   1) Prefer Path B instead (Option-B notice).
#   2) Revert PR #32 onto default main (restores post-#2 tree) — default here
#      when PATH_A_MODE=revert32 (default after #32).
#   3) Fresh Drive→git port as a new PR (PATH_A_MODE=fresh; manual).
#   4) Historical: PATH_A_MODE=ready_merge + PATH_A_PR=<open> for an OPEN port PR.
#
# Scientific effect: NONE. Packaging / default-branch face only.
# Fail-closed: any non-zero gh/audit step exits non-zero with a clear error.
# Never flips lemma_closed / prize / premise status.
#
# Batch 243: when default tip is already ALIGNED, exit 0 without revert/merge
# (no-op land). Reverting #32 on an ALIGNED Universal-law tip (e.g. ea41a30)
# is lander noise and can damage the restored face. Same contract as Path B
# Batch 242 ALIGNED no-op / restore_main_face short-circuit.
#
# Usage:
#   ./scripts/owner_land_path_a.sh                 # default: revert #32 (if MISALIGNED)
#   ./scripts/owner_land_path_a.sh --dry-run       # remote ALIGNED check only; no revert
#   ./scripts/owner_land_path_a.sh --help
#   PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
#   PATH_A_MODE=ready_merge PATH_A_PR=N ./scripts/owner_land_path_a.sh
#   TRIAL_ROOT=/path/to/trial ./scripts/owner_land_path_a.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
PR_NUMBER="${PATH_A_PR:-2}"
MODE="${PATH_A_MODE:-revert32}"
DRY_RUN=0

die() {
  echo "owner_land_path_a: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

usage() {
  cat <<'EOF'
Usage: owner_land_path_a.sh [--dry-run] [--help]

  (default)     If default tip is ALIGNED → exit 0 (no revert/merge).
                If MISALIGNED → PATH_A_MODE (default revert32).
  --dry-run     Remote ALIGNED audit only; never revert / ready / merge.
  --help        Show this help.

Env:
  PATH_A_MODE=revert32|ready_merge|fresh   (default: revert32)
  PATH_A_PR=<n>                            (ready_merge only; default 2)
  TRIAL_ROOT / MAIN_REPO

Prefer Path B: ./scripts/owner_land_path_b.sh
Scientific effect: NONE. lemma_closed stays false.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

need_cmd gh
need_cmd python3

AUDIT="$TRIAL_ROOT/scripts/audit_main_alignment.py"
WATCH="$TRIAL_ROOT/scripts/watch_main_alignment.py"
[[ -f "$AUDIT" ]] || die "missing $AUDIT (set TRIAL_ROOT to the trial checkout)"
[[ -f "$WATCH" ]] || die "missing $WATCH"

echo "=== owner_land_path_a ==="
echo "HOLD on PR #2 is VOID (Batch 54 OWNER OVERRIDE). Prefer Path B when possible."
echo "repo=$REPO mode=$MODE path_a_pr=#$PR_NUMBER trial_root=$TRIAL_ROOT dry_run=$DRY_RUN"
echo "scientific_effect=NONE"
echo "hint: ./scripts/owner_land_path_b.sh  # preferred ALIGNED restore"
echo

# Batch 243: ALIGNED no-op before any auth-gated revert/merge. Prefer Path B
# for restore; Path A must not fire gh pr revert 32 on an already-ALIGNED tip.
echo "--- remote audit_main_alignment (ALIGNED? short-circuit) ---"
set +e
python3 "$AUDIT"
AUDIT_EC=$?
set -e
if [[ "$AUDIT_EC" -eq 0 ]]; then
  echo "owner_land_path_a: already ALIGNED — Path A land not needed (no revert/merge)."
  echo "Scientific effect: NONE"
  exit 0
fi
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "owner_land_path_a: --dry-run — tip not ALIGNED (audit exit=$AUDIT_EC); would run PATH_A_MODE=$MODE (no write)."
  echo "Prefer Path B: $TRIAL_ROOT/scripts/owner_land_path_b.sh --dry-run"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated. Run: gh auth login  (use the owner account with write on $REPO)"
fi

LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-unknown}"

run_post_audit() {
  echo
  echo "--- post-land audit (expect ALIGNED / exit 0) ---"
  set +e
  python3 "$AUDIT"
  local audit_ec=$?
  set -e
  if [[ "$audit_ec" -ne 0 ]]; then
    die "audit_main_alignment exit=$audit_ec (expected 0=ALIGNED). Merge may still be propagating. Re-run: python3 $WATCH"
  fi
  echo
  echo "--- watch_main_alignment (expect ALIGNED) ---"
  set +e
  python3 "$WATCH"
  local watch_ec=$?
  set -e
  if [[ "$watch_ec" -ne 0 ]]; then
    die "watch_main_alignment exit=$watch_ec (expected 0=ALIGNED)"
  fi
  echo
  echo "owner_land_path_a: OK — default tip ALIGNED after Path A ($MODE)."
  echo "Scientific effect: NONE"
}

case "$MODE" in
  revert32)
    echo "--- Path A: revert CoS PR #32 (restores post-#2 q0 tree on default main) ---"
    echo "If this fails (403 / already reverted), prefer Path B: $TRIAL_ROOT/scripts/owner_land_path_b.sh"
    if ! gh pr view 32 --repo "$REPO" --json number,state,mergedAt,title >/dev/null 2>&1; then
      die "cannot view PR #32 on $REPO (need read). Aborting."
    fi
    # gh pr revert creates a revert PR; --delete-branch cleans up after merge when supported.
    set +e
    REVERT_OUT="$(gh pr revert 32 --repo "$REPO" --title "Revert \"Revert PR #2\" (Path A restore)" --body "Path A: restore q0 default tip after CoS #32. HOLD on #2 is VOID (Batch 54 OWNER OVERRIDE). Prefer Path B when notice-only is enough. Scientific effect: NONE." 2>&1)"
    REVERT_EC=$?
    set -e
    if [[ "$REVERT_EC" -ne 0 ]]; then
      die "gh pr revert 32 failed (exit=$REVERT_EC): $REVERT_OUT
Prefer Path B: $TRIAL_ROOT/scripts/owner_land_path_b.sh
Or open a fresh Drive→git port PR and: PATH_A_MODE=ready_merge PATH_A_PR=<n> $0"
    fi
    echo "$REVERT_OUT"
    # Extract PR URL/number if present and merge it.
    REVERT_PR="$(echo "$REVERT_OUT" | grep -Eo 'pull/[0-9]+' | head -1 | grep -Eo '[0-9]+' || true)"
    if [[ -z "$REVERT_PR" ]]; then
      REVERT_PR="$(gh pr list --repo "$REPO" --search 'Revert Revert PR #2' --state open --json number --jq '.[0].number // empty' 2>/dev/null || true)"
    fi
    if [[ -n "$REVERT_PR" ]]; then
      echo "--- merging revert PR #$REVERT_PR ---"
      if ! gh pr merge "$REVERT_PR" --repo "$REPO" --merge; then
        die "gh pr merge #$REVERT_PR failed. Merge manually, then: python3 $AUDIT"
      fi
    else
      echo "Revert PR opened (parse number manually if needed); waiting for tip propagation."
    fi
    sleep 2
    run_post_audit
    exit 0
    ;;

  ready_merge)
    echo "--- preflight: PR #$PR_NUMBER ---"
    if ! PR_JSON="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json number,state,isDraft,mergeable,mergeStateStatus,url 2>&1)"; then
      die "cannot view PR #$PR_NUMBER on $REPO: $PR_JSON"
    fi
    echo "$PR_JSON"
    STATE="$(echo "$PR_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["state"])')"
    [[ "$STATE" == "OPEN" ]] || die "PR #$PR_NUMBER state=$STATE (need OPEN). For closed #2 after #32, use PATH_A_MODE=revert32 or Path B."

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
    sleep 2
    run_post_audit
    exit 0
    ;;

  fresh)
    die "PATH_A_MODE=fresh is manual: open a new Drive→git port PR onto default main, then PATH_A_MODE=ready_merge PATH_A_PR=<n> $0. Prefer Path B: $TRIAL_ROOT/scripts/owner_land_path_b.sh"
    ;;

  *)
    die "unknown PATH_A_MODE=$MODE (use revert32 | ready_merge | fresh). Prefer Path B: $TRIAL_ROOT/scripts/owner_land_path_b.sh"
    ;;
esac
