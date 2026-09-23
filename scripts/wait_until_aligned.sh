#!/usr/bin/env bash
# Poll watch_main_alignment.py until default tip is ALIGNED (or give up).
#
# Exit codes:
#   0 — ALIGNED (optionally after VERIFY_AFTER_MERGE.sh when --verify)
#   1 — still MISALIGNED when max wait elapsed
#   2 — transport errors exhausted retries
#
# Scientific effect: NONE. Read-only polling of d6g8k5htny-coder/main.
#
# Usage:
#   ./scripts/wait_until_aligned.sh
#   ./scripts/wait_until_aligned.sh --interval 60 --max-wait 7200
#   ./scripts/wait_until_aligned.sh --verify
#   INTERVAL=30 MAX_WAIT=7200 TRANSPORT_RETRIES=3 ./scripts/wait_until_aligned.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL="${INTERVAL:-30}"
MAX_WAIT="${MAX_WAIT:-7200}"
TRANSPORT_RETRIES="${TRANSPORT_RETRIES:-3}"
VERIFY=0
WATCH="$ROOT/scripts/watch_main_alignment.py"
VERIFY_SCRIPT="$ROOT/portable/pr2-landing/VERIFY_AFTER_MERGE.sh"

usage() {
  cat <<'EOF'
Usage: wait_until_aligned.sh [options]

  Poll python3 scripts/watch_main_alignment.py until state is ALIGNED.

Options:
  --interval SEC     Seconds between polls (default: 30, or INTERVAL)
  --max-wait SEC     Max seconds to wait (default: 7200 = 2h, or MAX_WAIT)
  --transport-retries N
                     Consecutive transport failures before exit 2 (default: 3)
  --verify           After ALIGNED, run VERIFY_AFTER_MERGE.sh if present
  -h, --help         Show this help

Exit: 0=ALIGNED, 1=timeout still MISALIGNED, 2=transport after retries
Scientific effect: NONE
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      [[ $# -ge 2 ]] || { echo "wait_until_aligned: ERROR: --interval needs a value" >&2; exit 2; }
      INTERVAL="$2"
      shift 2
      ;;
    --max-wait)
      [[ $# -ge 2 ]] || { echo "wait_until_aligned: ERROR: --max-wait needs a value" >&2; exit 2; }
      MAX_WAIT="$2"
      shift 2
      ;;
    --transport-retries)
      [[ $# -ge 2 ]] || { echo "wait_until_aligned: ERROR: --transport-retries needs a value" >&2; exit 2; }
      TRANSPORT_RETRIES="$2"
      shift 2
      ;;
    --verify)
      VERIFY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "wait_until_aligned: ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -f "$WATCH" ]] || {
  echo "wait_until_aligned: ERROR: missing $WATCH" >&2
  exit 2
}

# Validate positive integers
for pair in "INTERVAL:$INTERVAL" "MAX_WAIT:$MAX_WAIT" "TRANSPORT_RETRIES:$TRANSPORT_RETRIES"; do
  name="${pair%%:*}"
  val="${pair#*:}"
  [[ "$val" =~ ^[0-9]+$ ]] || {
    echo "wait_until_aligned: ERROR: $name must be a non-negative integer (got: $val)" >&2
    exit 2
  }
done

echo "=== wait_until_aligned ==="
echo "watch=$WATCH"
echo "interval=${INTERVAL}s max_wait=${MAX_WAIT}s transport_retries=$TRANSPORT_RETRIES verify=$VERIFY"
echo "scientific_effect=NONE"
echo

started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
start_epoch="$(date +%s)"
poll=0
transport_streak=0
tmp_json="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_json" "$tmp_err"' EXIT

while true; do
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  if [[ "$elapsed" -ge "$MAX_WAIT" && "$poll" -gt 0 ]]; then
    echo "wait_until_aligned: TIMEOUT after ${elapsed}s (max_wait=${MAX_WAIT}s) — still MISALIGNED"
    echo "scientific_effect=NONE"
    exit 1
  fi

  poll=$((poll + 1))
  echo "--- poll #$poll elapsed=${elapsed}s @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"

  set +e
  python3 "$WATCH" >"$tmp_json" 2>"$tmp_err"
  watch_ec=$?
  set -e

  if [[ -s "$tmp_err" ]]; then
    # watch prints JSON on stdout; stderr usually empty, but show if present
    sed 's/^/watch_stderr: /' "$tmp_err" || true
  fi

  state="UNKNOWN"
  if [[ -s "$tmp_json" ]]; then
    state="$(python3 -c "import json,sys
try:
  print(json.load(open(sys.argv[1])).get('state','UNKNOWN'))
except Exception as e:
  print('PARSE_ERROR')
" "$tmp_json" 2>/dev/null || echo PARSE_ERROR)"
    # Keep status readable: one-line state + full JSON indented block
    echo "watch_exit=$watch_ec state=$state"
    cat "$tmp_json"
    echo
  else
    echo "watch_exit=$watch_ec state=$state (empty stdout)"
  fi

  if [[ "$watch_ec" -eq 0 && "$state" == "ALIGNED" ]]; then
    echo "wait_until_aligned: ALIGNED after ${elapsed}s (poll #$poll, started $started_at)"
    echo "scientific_effect=NONE"
    if [[ "$VERIFY" -eq 1 ]]; then
      if [[ -f "$VERIFY_SCRIPT" ]]; then
        echo
        echo "=== --verify: running VERIFY_AFTER_MERGE.sh ==="
        bash "$VERIFY_SCRIPT"
      else
        echo "wait_until_aligned: --verify set but missing $VERIFY_SCRIPT (skip)"
      fi
    fi
    exit 0
  fi

  if [[ "$watch_ec" -eq 2 || "$state" == "TRANSPORT_ERROR" ]]; then
    transport_streak=$((transport_streak + 1))
    echo "wait_until_aligned: transport error streak=$transport_streak/$TRANSPORT_RETRIES"
    if [[ "$transport_streak" -ge "$TRANSPORT_RETRIES" ]]; then
      echo "wait_until_aligned: TRANSPORT_ERROR after $TRANSPORT_RETRIES consecutive failures — exit 2"
      echo "scientific_effect=NONE"
      exit 2
    fi
  else
    transport_streak=0
  fi

  # Still MISALIGNED (or transient parse issue): check time budget before sleeping
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  remaining=$((MAX_WAIT - elapsed))
  if [[ "$remaining" -le 0 ]]; then
    echo "wait_until_aligned: TIMEOUT after ${elapsed}s (max_wait=${MAX_WAIT}s) — still MISALIGNED"
    echo "scientific_effect=NONE"
    exit 1
  fi

  sleep_for="$INTERVAL"
  if [[ "$sleep_for" -gt "$remaining" ]]; then
    sleep_for="$remaining"
  fi
  echo "status=MISALIGNED next_poll_in=${sleep_for}s remaining≈${remaining}s scientific_effect=NONE"
  echo
  sleep "$sleep_for"
done
