#!/usr/bin/env bash
# path_c_tip_drift_tolerance.sh — decide whether BASE_TIP lagging the live
# hardening tip is tolerable for the Path C gates.
#
# Background: Path C landed on chatgpt/drive-github-hardening-20260919 (VERIFY
# path_c_landed=true). The hardening tip keeps moving (peer agents merge PRs
# several times per hour) while the coordinator loop keeps BASE_TIP pinned
# ("keep-prior"). The pure `live == BASE_TIP` gates therefore stay red forever
# although nothing is wrong: every portable patch is still on the tree.
#
# Tolerance rule (fail-closed):
#   tolerated  <=>  VERIFY.json path_c_landed is true
#               AND apply_all.sh --check on the LIVE tip exits 0
#               AND its summary reports already_on_tip=1
#                   (no patch needed a forward apply; each one already-applied
#                    or intentionally skipped).
# Anything else (patch missing, forward apply needed, apply failure, transport
# failure) is NOT tolerated and the caller keeps its original hard failure.
#
# Set PATH_C_STRICT_TIP=1 to disable tolerance (always exit 1 on drift).
#
# Usage:
#   path_c_tip_drift_tolerance.sh [--workdir DIR] [--live-sha SHA]
#     --workdir DIR       existing checkout of the live hardening tip (no clone)
#     --live-sha SHA      informational; printed in the verdict
#     --verify-file PATH  VERIFY.json to read path_c_landed from (tests)
#     --help
# Without --workdir a shallow clone of the live hardening tip is made in a
# temp dir (GITHUB_TOKEN / GH_TOKEN / MAIN_PUSH_TOKEN used if present; never
# printed).
#
# Output: one verdict line
#   path_c_tip_drift: tolerated=1|0 live=<sha> base_tip=<sha> reason=<code> ...
# Exit: 0 tolerated, 1 not tolerated, 2 transport / missing inputs.
# Scientific effect: NONE — read-only checks; never flips lemma_closed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAIN_REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
HARDENING_REF="${HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
APPLY_ALL="${ROOT}/portable/patches/apply_all.sh"
VERIFY_FILE="${ROOT}/portable/path-c-applied-bundle/VERIFY.json"
BASE_TIP_FILE="${ROOT}/portable/patches/BASE_TIP.txt"

WORKDIR=""
LIVE_SHA=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workdir) WORKDIR="${2:-}"; shift 2 ;;
    --live-sha) LIVE_SHA="${2:-}"; shift 2 ;;
    --verify-file) VERIFY_FILE="${2:-}"; shift 2 ;;
    --help|-h)
      sed -n '2,34p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "path_c_tip_drift: unknown arg $1" >&2; exit 2 ;;
  esac
done

BASE_SHA=""
if [[ -f "$BASE_TIP_FILE" ]]; then
  # Prefer a full 40-hex SHA; the branch name carries a date (20260919) that a
  # loose 7+-hex match would catch first.
  BASE_SHA="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1 | python3 -c 'import re,sys; t=sys.stdin.read(); m=re.search(r"(?i)\b([0-9a-f]{40})\b", t) or re.search(r"(?i)\b(?=[0-9a-f]*[a-f])([0-9a-f]{7,39})\b", t); print(m.group(1).lower() if m else "")')"
fi

verdict() {
  # $1 tolerated 0/1, $2 reason, $3 extra
  echo "path_c_tip_drift: tolerated=$1 live=${LIVE_SHA:-unknown} base_tip=${BASE_SHA:-unknown} reason=$2 ${3:-}scientific_effect=NONE"
}

if [[ "${PATH_C_STRICT_TIP:-0}" == "1" ]]; then
  verdict 0 strict_tip_requested
  exit 1
fi

if [[ ! -f "$APPLY_ALL" ]]; then
  verdict 0 missing_apply_all
  exit 2
fi

LANDED=0
if [[ -f "$VERIFY_FILE" ]] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("path_c_landed") is True else 1)' "$VERIFY_FILE" 2>/dev/null; then
  LANDED=1
fi
if [[ "$LANDED" -ne 1 ]]; then
  verdict 0 path_c_not_landed
  exit 1
fi

CLEANUP_DIR=""
cleanup() {
  if [[ -n "$CLEANUP_DIR" && -d "$CLEANUP_DIR" ]]; then
    rm -rf "$CLEANUP_DIR"
  fi
}
trap cleanup EXIT

if [[ -z "$WORKDIR" ]]; then
  CLEANUP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/path-c-tip-drift.XXXXXX")"
  WORKDIR="$CLEANUP_DIR/main"
  CLONE_URL="https://github.com/${MAIN_REPO}.git"
  TOK="${GITHUB_TOKEN:-${GH_TOKEN:-${MAIN_PUSH_TOKEN:-}}}"
  if [[ -n "$TOK" ]]; then
    CLONE_URL="https://x-access-token:${TOK}@github.com/${MAIN_REPO}.git"
  fi
  if ! git clone -q --depth 1 --branch "$HARDENING_REF" "$CLONE_URL" "$WORKDIR" 2>/dev/null; then
    verdict 0 clone_failed
    exit 2
  fi
elif [[ ! -d "$WORKDIR/.git" && ! -f "$WORKDIR/.git" ]]; then
  verdict 0 workdir_not_git
  exit 2
fi

HEAD_SHA="$(git -C "$WORKDIR" rev-parse HEAD 2>/dev/null || true)"
if [[ -z "$LIVE_SHA" ]]; then
  LIVE_SHA="$HEAD_SHA"
elif [[ -n "$HEAD_SHA" && "$HEAD_SHA" != "$LIVE_SHA" && "$HEAD_SHA" != "${LIVE_SHA}"* && "$LIVE_SHA" != "${HEAD_SHA}"* ]]; then
  verdict 0 workdir_head_mismatch "workdir_head=${HEAD_SHA} "
  exit 1
fi

set +e
CHECK_OUT="$(cd "$WORKDIR" && bash "$APPLY_ALL" --check 2>&1)"
CHECK_EC=$?
set -e
SUMMARY="$(printf '%s\n' "$CHECK_OUT" | grep -E '^apply_all: summary ' | tail -n1 || true)"
if [[ "$CHECK_EC" -ne 0 ]]; then
  printf '%s\n' "$CHECK_OUT" | grep -E '^(error|warning):' >&2 || true
  verdict 0 apply_all_check_failed "apply_all_exit=${CHECK_EC} "
  exit 1
fi
if [[ -z "$SUMMARY" ]]; then
  verdict 0 apply_all_no_summary
  exit 1
fi
FORWARD="$(printf '%s' "$SUMMARY" | sed -n 's/.*forward=\([0-9]*\).*/\1/p')"
ALREADY="$(printf '%s' "$SUMMARY" | sed -n 's/.*already_applied=\([0-9]*\).*/\1/p')"
SKIPPED="$(printf '%s' "$SUMMARY" | sed -n 's/.*skipped=\([0-9]*\).*/\1/p')"
ON_TIP="$(printf '%s' "$SUMMARY" | sed -n 's/.*already_on_tip=\([01]\).*/\1/p')"
EXTRA="forward=${FORWARD:-?} already_applied=${ALREADY:-?} skipped=${SKIPPED:-?} "
if [[ "$ON_TIP" == "1" ]]; then
  verdict 1 landed_stack_already_on_live_tip "$EXTRA"
  exit 0
fi
verdict 0 stack_not_fully_on_tip "$EXTRA"
exit 1
