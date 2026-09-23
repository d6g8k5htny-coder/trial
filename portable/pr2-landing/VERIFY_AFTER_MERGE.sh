#!/usr/bin/env bash
# Run after Path A (PR #2 merge) or Path B (Option-B notice) on default main.
# Scientific effect: NONE.
#
# After ALIGNED: when TRIAL_ROOT is set or this script is run from a trial
# checkout (apply_all findable), optionally apply Path C portable patches
# 0001–0009, run math_status_check + focused pytest, and assert
# lemma_closed=false. Set SKIP_PATH_C=1 for alignment-only.
#
# Usage:
#   ./portable/pr2-landing/VERIFY_AFTER_MERGE.sh
#   SKIP_PATH_C=1 ./portable/pr2-landing/VERIFY_AFTER_MERGE.sh
#   MAIN_CHECKOUT=/path/to/main ./portable/pr2-landing/VERIFY_AFTER_MERGE.sh
#   TRIAL_ROOT=/path/to/trial ./portable/pr2-landing/VERIFY_AFTER_MERGE.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
SKIP_PATH_C="${SKIP_PATH_C:-0}"
MAIN_CHECKOUT="${MAIN_CHECKOUT:-}"
HARDENING_REF="${PATH_C_HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"

for arg in "${@:-}"; do
  case "${arg:-}" in
    "") ;;
    --skip-path-c) SKIP_PATH_C=1 ;;
    --apply-path-c) SKIP_PATH_C=0 ;;
    -h|--help)
      cat <<'EOF'
Usage: VERIFY_AFTER_MERGE.sh [--apply-path-c | --skip-path-c]

  After remote tip is ALIGNED:
    If trial apply_all.sh is findable (TRIAL_ROOT set or script in trial),
    clone/use MAIN_CHECKOUT, apply_all 0001–0009, math_status + focused
    pytest, assert lemma_closed=false.
  --skip-path-c   Alignment check only (never apply).
  --apply-path-c  Force Path C local verify (default when apply_all findable).

Env: TRIAL_ROOT, SKIP_PATH_C=1, MAIN_CHECKOUT, PATH_C_HARDENING_REF, MAIN_REPO
EOF
      exit 0
      ;;
    *)
      echo "unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

echo "trial root: $TRIAL_ROOT"

python3 "$TRIAL_ROOT/scripts/watch_main_alignment.py" | tee /tmp/watch_main_alignment.json
state="$(python3 -c "import json;print(json.load(open('/tmp/watch_main_alignment.json'))['state'])")"
echo "state=$state"
if [[ "$state" != "ALIGNED" ]]; then
  echo "Default tip is still MISALIGNED. Land Path A or B first (see portable/LAND.md)." >&2
  exit 1
fi

echo "Aligned."

APPLY_ALL="$TRIAL_ROOT/portable/patches/apply_all.sh"
if [[ ! -f "$APPLY_ALL" ]]; then
  echo "No apply_all at $APPLY_ALL — skip Path C local verify."
  echo "Remember: lemma_closed must stay false; green ≠ discharge."
  exit 0
fi

if [[ "$SKIP_PATH_C" == "1" ]]; then
  echo "SKIP_PATH_C=1 — not applying Path C."
  echo "Next after PR #2: rebase hardening onto new main, then apply_all 0001–0009:"
  echo "  $TRIAL_ROOT/scripts/owner_land_path_c.sh"
  echo "Remember: lemma_closed must stay false; green ≠ discharge."
  exit 0
fi

echo "=== Path C local verify (apply_all + math_status + focused pytest) ==="
echo "apply_all=$APPLY_ALL"
echo "scientific_effect=NONE"

CLEANUP_MAIN=0
if [[ -n "$MAIN_CHECKOUT" ]]; then
  [[ -d "$MAIN_CHECKOUT" ]] || { echo "MAIN_CHECKOUT not a directory: $MAIN_CHECKOUT" >&2; exit 2; }
  cd "$MAIN_CHECKOUT"
else
  MAIN_CHECKOUT="$(mktemp -d "${TMPDIR:-/tmp}/verify-path-c.XXXXXX")"
  CLEANUP_MAIN=1
  cleanup() {
    if [[ "${CLEANUP_MAIN:-0}" -eq 1 && -n "${MAIN_CHECKOUT:-}" && -d "$MAIN_CHECKOUT" ]]; then
      rm -rf "$MAIN_CHECKOUT"
    fi
  }
  trap cleanup EXIT
  echo "--- clone $REPO @ $HARDENING_REF ---"
  if ! git clone --depth 50 --branch "$HARDENING_REF" \
      "https://github.com/${REPO}.git" "$MAIN_CHECKOUT/main"; then
    echo "git clone failed for hardening tip" >&2
    exit 2
  fi
  cd "$MAIN_CHECKOUT/main"
fi

if [[ ! -f tools/math_status_check.py ]]; then
  echo "error: $PWD is not a main research checkout (missing tools/math_status_check.py)" >&2
  exit 2
fi

echo "checkout=$(git rev-parse --short HEAD 2>/dev/null || echo unknown) cwd=$PWD"
if ! "$APPLY_ALL"; then
  echo "apply_all failed — after PR #2 merges, rebase hardening onto new main then re-run; see portable/LAND.md Path C." >&2
  exit 1
fi

STATUS_OUT="$(python3 tools/math_status_check.py 2>&1)" || {
  echo "$STATUS_OUT" >&2
  echo "math_status_check failed" >&2
  exit 1
}
echo "$STATUS_OUT"
if ! echo "$STATUS_OUT" | grep -q 'lemma_closed=false'; then
  echo "ASSERT FAILED: lemma_closed must be false (got unexpected status)." >&2
  exit 1
fi
if ! echo "$STATUS_OUT" | grep -q 'problems=0'; then
  echo "ASSERT FAILED: math_status_check problems!=0." >&2
  exit 1
fi
echo "assert ok: lemma_closed=false problems=0"

FOCUSED=(
  tests/test_carriers.py
  tests/test_math_status.py
  tests/test_inventable_jetmod_probes.py
  tests/test_gaussian_moments.py
  tests/test_inventable_jetmod_instrumentation_status.py
)
python3 -m pytest -q "${FOCUSED[@]}"
echo "Path C local verify OK. lemma_closed=false; focused pytest green."
echo "To land on main with write creds: $TRIAL_ROOT/scripts/owner_land_path_c.sh"
echo "Scientific effect: NONE"
exit 0
