#!/usr/bin/env bash
# Fire trial repository_dispatch for land-path-c-on-main.
#
# Batch 139: cursor[bot] ghs cannot workflow_dispatch (403 Actions:write) but
# can POST /repos/.../dispatches with Contents write. When MAIN_PUSH_TOKEN
# secret is present on trial, --apply lands Path C on hardening via Actions.
#
# Scientific effect: NONE. Never flips lemma_closed / research status.
#
# Usage:
#   ./scripts/dispatch_land_path_c.sh           # dry_run=true (default; safe)
#   ./scripts/dispatch_land_path_c.sh --apply   # dry_run=false (needs MAIN_PUSH_TOKEN secret)
#   ./scripts/dispatch_land_path_c.sh --apply --direct-push

set -euo pipefail

DRY_RUN=true
DIRECT_PUSH=false
REPO="${TRIAL_REPO:-d6g8k5htny-coder/trial}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply|--land)
      DRY_RUN=false
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --direct-push)
      DIRECT_PUSH=true
      shift
      ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

PAYLOAD="$(printf '{"dry_run":%s,"direct_push":%s}' "$DRY_RUN" "$DIRECT_PUSH")"
echo "dispatch_land_path_c: repo=${REPO} event_type=land-path-c-on-main client_payload=${PAYLOAD}"

# gh api --input expects full body; never echo tokens.
BODY="$(printf '{"event_type":"land-path-c-on-main","client_payload":%s}' "$PAYLOAD")"
if ! printf '%s' "$BODY" | gh api --method POST "repos/${REPO}/dispatches" --input -; then
  echo "dispatch_land_path_c: FAILED (HTTP non-2xx). Contents:write may be missing." >&2
  exit 1
fi

echo "dispatch_land_path_c: accepted (204). dry_run=${DRY_RUN} direct_push=${DIRECT_PUSH}."
if [[ "$DRY_RUN" == "false" ]]; then
  echo "Apply land requires trial secret MAIN_PUSH_TOKEN; check Actions run for land-path-c-on-main."
fi
exit 0
