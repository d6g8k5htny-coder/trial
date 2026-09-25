#!/usr/bin/env bash
# Poll watch_main_alignment.py until default tip is ALIGNED (or give up).
#
# Exit codes:
#   0 — ALIGNED (optionally after VERIFY_AFTER_MERGE.sh when --verify)
#   1 — still MISALIGNED when max wait elapsed (saw MISALIGNED; not mid-transport)
#   2 — transport errors exhausted retries OR max-wait hit while only
#       TRANSPORT_ERROR polls were observed (Batch 258: do not misreport as
#       MISALIGNED — that flake sent Path B / "still red" automation down the
#       wrong path under API rate-limits)
#
# Scientific effect: NONE. Read-only polling of d6g8k5htny-coder/main.
#
# Autonomous batches: this script's --max-wait is a *poll budget*, not the
# 48h work window. For the autonomous work window, run
#   python3 scripts/check_autonomous_window.py
# first. When store mode is PERMANENT_UNTIL_OWNER_INTERVENES, do not treat
# elapsed wall-clock since autonomous_48h_started_at as a hard-stop / finale.
#
# Usage:
#   ./scripts/wait_until_aligned.sh
#   ./scripts/wait_until_aligned.sh --interval 60 --max-wait 7200
#   ./scripts/wait_until_aligned.sh --verify
#   INTERVAL=30 MAX_WAIT=7200 TRANSPORT_RETRIES=3 ./scripts/wait_until_aligned.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Optional: honor permanent autonomous window (Batch 61+). When
# CHECK_AUTONOMOUS_WINDOW=1 (default for autonomous timers), refuse to start
# a "finale / expired" disposition — permanent mode always continues.
if [[ "${CHECK_AUTONOMOUS_WINDOW:-0}" == "1" ]]; then
  if [[ -f "$ROOT/scripts/check_autonomous_window.py" ]]; then
    set +e
    python3 "$ROOT/scripts/check_autonomous_window.py"
    win_ec=$?
    set -e
    if [[ "$win_ec" -eq 1 ]]; then
      echo "wait_until_aligned: autonomous window EXPIRED (finite mode) — hard-stop" >&2
      exit 1
    fi
    if [[ "$win_ec" -eq 2 ]]; then
      echo "wait_until_aligned: autonomous window store error (exit 2)" >&2
      exit 2
    fi
  fi
fi

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

Exit: 0=ALIGNED, 1=timeout still MISALIGNED, 2=transport (retries or
     max-wait with only TRANSPORT_ERROR polls — never lie as MISALIGNED)
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
saw_misaligned=0
tmp_json="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_json" "$tmp_err"' EXIT

# Batch 258: max-wait during a pure TRANSPORT_ERROR streak must exit 2, not
# pretend the tip is still MISALIGNED (exit 1). Callers that treat exit 1 as
# "run Path B / tip is red" flake under API rate-limits while tip is ALIGNED.
timeout_exit() {
  local elapsed_now="$1"
  # Pure or trailing transport under max-wait → exit 2 (never lie as MISALIGNED).
  if [[ "$transport_streak" -gt 0 ]]; then
    if [[ "$saw_misaligned" -eq 0 ]]; then
      echo "wait_until_aligned: TIMEOUT after ${elapsed_now}s (max_wait=${MAX_WAIT}s) — TRANSPORT_ERROR (no MISALIGNED poll; not exit 1)"
    else
      echo "wait_until_aligned: TIMEOUT after ${elapsed_now}s (max_wait=${MAX_WAIT}s) — TRANSPORT_ERROR after earlier MISALIGNED (exit 2)"
    fi
    echo "scientific_effect=NONE"
    exit 2
  fi
  echo "wait_until_aligned: TIMEOUT after ${elapsed_now}s (max_wait=${MAX_WAIT}s) — still MISALIGNED"
  echo "scientific_effect=NONE"
  exit 1
}

while true; do
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  if [[ "$elapsed" -ge "$MAX_WAIT" && "$poll" -gt 0 ]]; then
    timeout_exit "$elapsed"
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
    status_line="TRANSPORT_ERROR"
  else
    transport_streak=0
    if [[ "$state" == "MISALIGNED" || "$watch_ec" -eq 1 ]]; then
      saw_misaligned=1
      status_line="MISALIGNED"
    else
      status_line="$state"
    fi
  fi

  # Still waiting (MISALIGNED or transient transport): check time budget before sleeping
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  remaining=$((MAX_WAIT - elapsed))
  if [[ "$remaining" -le 0 ]]; then
    timeout_exit "$elapsed"
  fi

  sleep_for="$INTERVAL"
  if [[ "$sleep_for" -gt "$remaining" ]]; then
    sleep_for="$remaining"
  fi
  echo "status=${status_line} next_poll_in=${sleep_for}s remaining≈${remaining}s scientific_effect=NONE"
  echo
  sleep "$sleep_for"
done
