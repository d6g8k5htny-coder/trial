#!/usr/bin/env bash
# One-command ALIGNED restore for d6g8k5htny-coder/main default tip (Path B).
#
# Wraps remote ALIGNED short-circuit + Option-B dry-run certainty + multi-vector
# write preflight + owner_land_path_b. Prefer this when the owner/agent has write
# creds on main and wants a single entrypoint.
#
# Usage:
#   ./scripts/restore_main_face.sh              # audit → dry-run → write preflight → land
#   ./scripts/restore_main_face.sh --dry-run    # certainty JSON only (no push)
#   ./scripts/restore_main_face.sh --direct-main
#   ./scripts/restore_main_face.sh --after-merge
#   ./scripts/restore_main_face.sh --plan       # refresh RESTORE_PLAN_<batch>.json
#   ./scripts/restore_main_face.sh --batch 59   # set restore-plan batch id
#   RESTORE_BATCH=59 ./scripts/restore_main_face.sh --plan
#
# Land modes: if remote tip is already ALIGNED, exit 0 (no push). Else dry-run,
# then probe_main_write_vectors; if no Path-B-capable vector is WRITABLE, exit 1
# after dry-run (no doomed push). If WRITABLE, proceed to land.
#
# Scientific effect: NONE. Does not flip lemma_closed / prizes / premises.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
LAND="$TRIAL_ROOT/scripts/owner_land_path_b.sh"
REFRESH="$TRIAL_ROOT/scripts/refresh_restore_plan.py"
VECTORS="$TRIAL_ROOT/scripts/probe_main_write_vectors.py"
AUDIT="$TRIAL_ROOT/scripts/audit_main_alignment.py"
WATCH="$TRIAL_ROOT/scripts/watch_main_alignment.py"
BATCH="${RESTORE_BATCH:-59}"

die() {
  echo "restore_main_face: ERROR: $*" >&2
  exit 1
}

[[ -x "$LAND" || -f "$LAND" ]] || die "missing $LAND"
[[ -f "$REFRESH" ]] || die "missing $REFRESH"
[[ -f "$VECTORS" ]] || die "missing $VECTORS"
[[ -f "$AUDIT" ]] || die "missing $AUDIT"

MODE="land"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run" ;;
    --direct-main) MODE="direct-main" ;;
    --after-merge) MODE="after-merge" ;;
    --plan) MODE="plan" ;;
    --batch)
      shift
      [[ $# -gt 0 ]] || die "--batch requires a value"
      BATCH="$1"
      ;;
    --batch=*)
      BATCH="${1#--batch=}"
      ;;
    -h|--help)
      sed -n '2,24p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) die "unknown argument: $1 (see --help)" ;;
  esac
  shift
done

echo "=== restore_main_face (Path B / Option-B) ==="
echo "trial_root=$TRIAL_ROOT mode=$MODE batch=$BATCH"
echo "scientific_effect=NONE"
echo

remote_already_aligned() {
  echo "--- remote audit short-circuit (ALIGNED? ) ---"
  set +e
  local out
  out="$(python3 "$AUDIT" 2>&1)"
  local ec=$?
  set -e
  echo "$out"
  if [[ "$ec" -eq 0 ]]; then
    echo
    echo "restore_main_face: default tip already ALIGNED — Path B land not needed."
    if [[ -f "$WATCH" ]]; then
      python3 "$WATCH" || true
    fi
    echo "Scientific effect: NONE"
    return 0
  fi
  return 1
}

preflight_writable() {
  echo "--- write-vector preflight (all Path-B-capable vectors) ---"
  set +e
  local out
  out="$(python3 "$VECTORS" 2>&1)"
  local ec=$?
  set -e
  echo "$out"
  if [[ "$ec" -eq 0 ]] && echo "$out" | grep -q '"path_b_ready": true'; then
    echo "restore_main_face: Path-B-capable vector WRITABLE — proceeding to land."
    return 0
  fi
  echo
  echo "restore_main_face: Path B NOT applied — no Path-B-capable write vector (DENIED)."
  echo "  would-align dry-run already passed; owner next:"
  echo "    MAIN_PUSH_TOKEN / owner gh auth with Contents:Write on main"
  echo "    then re-run: ./scripts/restore_main_face.sh --batch $BATCH"
  echo "  or: ./scripts/restore_main_face.sh --plan --batch $BATCH"
  return 1
}

case "$MODE" in
  plan)
    python3 "$REFRESH" --batch "$BATCH"
    ;;
  dry-run)
    bash "$LAND" --dry-run
    ;;
  direct-main)
    if remote_already_aligned; then
      echo
      echo "restore_main_face: done (mode=$MODE batch=$BATCH). Scientific effect: NONE."
      exit 0
    fi
    bash "$LAND" --dry-run
    echo
    preflight_writable || exit 1
    echo
    echo "--- dry-run + write preflight OK; proceeding --direct-main ---"
    bash "$LAND" --direct-main
    ;;
  after-merge)
    bash "$LAND" --after-merge
    ;;
  land)
    if remote_already_aligned; then
      echo
      echo "restore_main_face: done (mode=$MODE batch=$BATCH). Scientific effect: NONE."
      exit 0
    fi
    bash "$LAND" --dry-run
    echo
    preflight_writable || exit 1
    echo
    echo "--- dry-run + write preflight OK; proceeding branch+PR land ---"
    bash "$LAND"
    ;;
esac

echo
echo "restore_main_face: done (mode=$MODE batch=$BATCH). Scientific effect: NONE."
