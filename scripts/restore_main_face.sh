#!/usr/bin/env bash
# One-command ALIGNED restore for d6g8k5htny-coder/main default tip (Path B).
#
# Wraps Option-B dry-run certainty + owner_land_path_b. Prefer this when the
# owner/agent has write creds on main and wants a single entrypoint.
#
# Usage:
#   ./scripts/restore_main_face.sh              # dry-run certainty, then branch+PR
#   ./scripts/restore_main_face.sh --dry-run    # certainty JSON only (no push)
#   ./scripts/restore_main_face.sh --direct-main
#   ./scripts/restore_main_face.sh --after-merge
#   ./scripts/restore_main_face.sh --plan       # refresh RESTORE_PLAN_58.json
#
# Scientific effect: NONE. Does not flip lemma_closed / prizes / premises.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
LAND="$TRIAL_ROOT/scripts/owner_land_path_b.sh"
REFRESH="$TRIAL_ROOT/scripts/refresh_restore_plan.py"
BATCH="${RESTORE_BATCH:-58}"

die() {
  echo "restore_main_face: ERROR: $*" >&2
  exit 1
}

[[ -x "$LAND" || -f "$LAND" ]] || die "missing $LAND"
[[ -f "$REFRESH" ]] || die "missing $REFRESH"

MODE="land"
for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE="dry-run" ;;
    --direct-main) MODE="direct-main" ;;
    --after-merge) MODE="after-merge" ;;
    --plan) MODE="plan" ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

echo "=== restore_main_face (Path B / Option-B) ==="
echo "trial_root=$TRIAL_ROOT mode=$MODE batch=$BATCH"
echo "scientific_effect=NONE"
echo

case "$MODE" in
  plan)
    python3 "$REFRESH" --batch "$BATCH"
    ;;
  dry-run)
    bash "$LAND" --dry-run
    ;;
  direct-main)
    bash "$LAND" --dry-run
    echo
    echo "--- dry-run OK; proceeding --direct-main ---"
    bash "$LAND" --direct-main
    ;;
  after-merge)
    bash "$LAND" --after-merge
    ;;
  land)
    bash "$LAND" --dry-run
    echo
    echo "--- dry-run OK; proceeding branch+PR land ---"
    bash "$LAND"
    ;;
esac

echo
echo "restore_main_face: done (mode=$MODE). Scientific effect: NONE."
