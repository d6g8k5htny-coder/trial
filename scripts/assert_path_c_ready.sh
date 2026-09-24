#!/usr/bin/env bash
# assert_path_c_ready.sh — exit 0 only when Path C dry-apply readiness holds.
#
# Gates (all required):
#   1) portable/patches/BASE_TIP.txt SHA matches live hardening tip
#   2) apply_all --check OK — OR post-0019 idle skip when path_c_landed and no
#      pending follow-ons (Batch 246: catch 0020+ by re-running --check when a
#      00NN≥0018 patch lacks path_c_00NN_landed=true)
#   3) math_status_check reports lemma_closed=false
#
# Scientific effect: NONE. Never flips research / lemma / prize / premise status.
# Does not push. Safe for CI and local owner preflight.
#
# Usage:
#   ./scripts/assert_path_c_ready.sh
#   ./scripts/assert_path_c_ready.sh --workdir /path/to/main-checkout   # skip clone
#   ./scripts/assert_path_c_ready.sh --help
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HARDENING_REF="${HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
MAIN_REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
BASE_TIP_FILE="${BASE_TIP_FILE:-$ROOT/portable/patches/BASE_TIP.txt}"
APPLY_ALL="${APPLY_ALL:-$ROOT/portable/patches/apply_all.sh}"
WORKDIR=""
SKIP_APPLY=0
KEEP_WORKDIR=0

usage() {
  cat <<'EOF'
assert_path_c_ready.sh — exit 0 only when Path C dry-apply readiness holds.

Gates (all required):
  1) portable/patches/BASE_TIP.txt SHA matches live hardening tip
  2) apply_all --check OK, OR IDLE_PATH_C_DONE skip when path_c_landed
     through tip and no pending 0018+ follow-ons (re-check if 0020+ pending)
  3) math_status_check reports lemma_closed=false

Scientific effect: NONE. Never flips research status. Does not push.

Options:
  --workdir DIR   Use existing main checkout (must be at hardening tip)
  --skip-apply    Only tip-match + apply_all --check (no math_status apply)
  --keep-workdir  Do not rm temp clone on exit
  -h, --help      Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workdir)
      WORKDIR="${2:-}"
      shift 2
      ;;
    --skip-apply)
      SKIP_APPLY=1
      shift
      ;;
    --keep-workdir)
      KEEP_WORKDIR=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "assert_path_c_ready: unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

parse_base_tip_sha() {
  local line="$1"
  local sha
  sha="$(printf '%s' "$line" | python3 -c '
import re, sys
text = sys.stdin.read()
m = re.search(r"(?i)\b([0-9a-f]{40})\b", text)
if m:
    print(m.group(1).lower())
    raise SystemExit(0)
m = re.search(r"(?i)(?:^|[=:\s])([0-9a-f]{7,39})(?:\b|$)", text)
if m:
    print(m.group(1).lower())
    raise SystemExit(0)
raise SystemExit(1)
' 2>/dev/null)" || return 1
  [[ -n "$sha" ]] || return 1
  printf '%s\n' "$sha"
}

if [[ ! -f "$BASE_TIP_FILE" ]]; then
  echo "assert_path_c_ready: missing BASE_TIP.txt at $BASE_TIP_FILE" >&2
  exit 1
fi
if [[ ! -x "$APPLY_ALL" && ! -f "$APPLY_ALL" ]]; then
  echo "assert_path_c_ready: missing apply_all.sh at $APPLY_ALL" >&2
  exit 1
fi

BASE_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
BASE_SHA="$(parse_base_tip_sha "$BASE_LINE" || true)"
if [[ -z "$BASE_SHA" ]]; then
  echo "assert_path_c_ready: could not parse SHA from BASE_TIP.txt: $BASE_LINE" >&2
  exit 1
fi

CLEANUP_DIR=""
cleanup() {
  if [[ -n "$CLEANUP_DIR" && "$KEEP_WORKDIR" -eq 0 && -d "$CLEANUP_DIR" ]]; then
    rm -rf "$CLEANUP_DIR"
  fi
}
trap cleanup EXIT

if [[ -n "$WORKDIR" ]]; then
  if [[ ! -d "$WORKDIR/.git" ]]; then
    echo "assert_path_c_ready: --workdir is not a git checkout: $WORKDIR" >&2
    exit 1
  fi
  LIVE_SHA="$(git -C "$WORKDIR" rev-parse HEAD)"
else
  CLEANUP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/assert-path-c-ready.XXXXXX")"
  WORKDIR="$CLEANUP_DIR/main"
  CLONE_URL="https://github.com/${MAIN_REPO}.git"
  if [[ -n "${GITHUB_TOKEN:-${GH_TOKEN:-${MAIN_PUSH_TOKEN:-}}}" ]]; then
    TOK="${GITHUB_TOKEN:-${GH_TOKEN:-${MAIN_PUSH_TOKEN}}}"
    CLONE_URL="https://x-access-token:${TOK}@github.com/${MAIN_REPO}.git"
  fi
  echo "assert_path_c_ready: shallow-clone ${MAIN_REPO}@${HARDENING_REF}"
  git clone --depth 1 --branch "$HARDENING_REF" "$CLONE_URL" "$WORKDIR"
  LIVE_SHA="$(git -C "$WORKDIR" rev-parse HEAD)"
fi

echo "assert_path_c_ready: BASE_TIP=$BASE_SHA live=$LIVE_SHA"
TIP_OK=0
if [[ ${#BASE_SHA} -eq 40 && "$LIVE_SHA" == "$BASE_SHA" ]]; then
  TIP_OK=1
elif [[ ${#BASE_SHA} -ge 7 && ${#BASE_SHA} -lt 40 && "${LIVE_SHA:0:${#BASE_SHA}}" == "$BASE_SHA" ]]; then
  TIP_OK=1
fi
if [[ "$TIP_OK" -ne 1 ]]; then
  echo "assert_path_c_ready: FAIL tip-drift live=$LIVE_SHA != BASE_TIP=$BASE_SHA" >&2
  echo "  refresh BASE_TIP + rebuild path-c-applied-bundle before land" >&2
  exit 1
fi
echo "assert_path_c_ready: tip match OK @ ${LIVE_SHA:0:7}"

# Batch 230: Path C already merged on hardening — patches are on tip; do not re-apply.
# Batch 246: post-0019 idle — skip redundant apply_all --check when landed+no pending
# follow-ons; if 0020+ appears on disk without a landed marker, run --check (catch 0020).
VERIFY_FILE="${ROOT}/portable/path-c-applied-bundle/VERIFY.json"
PATH_C_LANDED=0
if [[ -f "$VERIFY_FILE" ]]; then
  if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("path_c_landed") is True else 1)' "$VERIFY_FILE" 2>/dev/null; then
    PATH_C_LANDED=1
  fi
fi

# Pending follow-ons (0018+) with no path_c_00NN_landed=true → must not idle-skip.
FOLLOWON_EVAL="$(
  cd "$ROOT" && python3 - <<'PY'
import json
import sys
sys.path.insert(0, "scripts")
from when_writable_land import path_c_followon_pending

pending, detail = path_c_followon_pending()
pending_ids = list(detail.get("pending_ids") or [])
resolved = list(detail.get("resolved_ids") or [])
followons = list(detail.get("followon_patch_ids") or [])
stack_end = resolved[-1] if resolved else (followons[-1] if followons else None)
print(
    json.dumps(
        {
            "pending": bool(pending),
            "pending_ids": pending_ids,
            "resolved_ids": resolved,
            "followon_patch_ids": followons,
            "stack_end": stack_end,
        }
    )
)
PY
)"
PENDING_FOLLOWON="$(
  printf '%s' "$FOLLOWON_EVAL" | python3 -c 'import json,sys; print("1" if json.load(sys.stdin).get("pending") else "0")'
)"
PENDING_IDS="$(
  printf '%s' "$FOLLOWON_EVAL" | python3 -c 'import json,sys; print(",".join(json.load(sys.stdin).get("pending_ids") or []) or "[]")'
)"
STACK_END="$(
  printf '%s' "$FOLLOWON_EVAL" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("stack_end") or "none")'
)"
RESOLVED_IDS="$(
  printf '%s' "$FOLLOWON_EVAL" | python3 -c 'import json,sys; print(",".join(json.load(sys.stdin).get("resolved_ids") or []) or "[]")'
)"

verify_math_on_tip() {
  local label="$1"
  STATUS_OUT="$(cd "$WORKDIR" && python3 tools/math_status_check.py 2>&1)" || {
    echo "assert_path_c_ready: FAIL math_status_check exited non-zero ($label)" >&2
    echo "$STATUS_OUT" >&2
    exit 1
  }
  echo "$STATUS_OUT"
  if ! echo "$STATUS_OUT" | grep -q 'lemma_closed=false'; then
    echo "assert_path_c_ready: FAIL lemma_closed is not false ($label)" >&2
    exit 1
  fi
  if echo "$STATUS_OUT" | grep -Eq 'problems[=:][[:space:]]*[1-9]'; then
    echo "assert_path_c_ready: FAIL math_status_check reported problems>0 ($label)" >&2
    exit 1
  fi
}

if [[ "$PATH_C_LANDED" -eq 1 && "$PENDING_FOLLOWON" -eq 0 ]]; then
  echo "assert_path_c_ready: IDLE_PATH_C_DONE tip=${LIVE_SHA:0:7} stack_end=${STACK_END} resolved=${RESOLVED_IDS} pending=[]"
  echo "assert_path_c_ready: path_c_landed through tip patches — apply_all --check SKIPPED (redundant; catch 0020 when pending)"
  verify_math_on_tip "landed idle tip"
  echo "assert_path_c_ready: OK tip=${LIVE_SHA:0:7} idle_status=IDLE_PATH_C_DONE apply_all_check=skipped_redundant stack_end=${STACK_END} path_c_landed=true lemma_closed=false scientific_effect=NONE"
elif [[ "$PATH_C_LANDED" -eq 1 && "$PENDING_FOLLOWON" -eq 1 ]]; then
  echo "assert_path_c_ready: path_c_landed=true but pending follow-ons [${PENDING_IDS}] — run apply_all --check (catch 0020+)"
  echo "assert_path_c_ready: apply_all --check"
  if ! (cd "$WORKDIR" && bash "$APPLY_ALL" --check); then
    echo "assert_path_c_ready: FAIL apply_all --check (pending follow-ons [${PENDING_IDS}])" >&2
    exit 1
  fi
  echo "assert_path_c_ready: apply_all --check OK (pending=[${PENDING_IDS}])"
  if [[ "$SKIP_APPLY" -eq 1 ]]; then
    echo "assert_path_c_ready: --skip-apply set; skipping math_status lemma gate"
    echo "assert_path_c_ready: OK tip=${LIVE_SHA:0:7} idle_status=PENDING_FOLLOWON pending=[${PENDING_IDS}] apply_all_check=ok lemma_closed gate skipped"
    exit 0
  fi
  echo "assert_path_c_ready: apply_all + math_status_check (lemma_closed=false; pending=[${PENDING_IDS}])"
  (cd "$WORKDIR" && bash "$APPLY_ALL")
  verify_math_on_tip "pending follow-on apply"
  echo "assert_path_c_ready: OK tip=${LIVE_SHA:0:7} idle_status=PENDING_FOLLOWON pending=[${PENDING_IDS}] apply_all=check+apply lemma_closed=false scientific_effect=NONE"
else
  echo "assert_path_c_ready: apply_all --check"
  if ! (cd "$WORKDIR" && bash "$APPLY_ALL" --check); then
    echo "assert_path_c_ready: FAIL apply_all --check" >&2
    exit 1
  fi
  echo "assert_path_c_ready: apply_all --check OK"

  if [[ "$SKIP_APPLY" -eq 1 ]]; then
    echo "assert_path_c_ready: --skip-apply set; skipping math_status lemma gate"
    echo "assert_path_c_ready: OK (tip match + apply_all --check); lemma_closed gate skipped"
    exit 0
  fi

  echo "assert_path_c_ready: apply_all + math_status_check (lemma_closed=false)"
  (cd "$WORKDIR" && bash "$APPLY_ALL")
  verify_math_on_tip "apply_all"
  echo "assert_path_c_ready: OK tip=${LIVE_SHA:0:7} apply_all=check+apply lemma_closed=false scientific_effect=NONE"
fi

# Batch 180/246: emit portable/PATH_C_STATUS.json (no secrets; lemma_closed stays false).
# Idle fields (idle_status / apply_all_check / stack_end / pending_ids) come from
# write_path_c_status follow-on scan — same catch-0020 gate used above.
STATUS_PY="${ROOT}/scripts/write_path_c_status.py"
if [[ -f "$STATUS_PY" ]]; then
  echo "assert_path_c_ready: writing PATH_C_STATUS.json"
  python3 "$STATUS_PY" --skip-write-probe || echo "assert_path_c_ready: warn PATH_C_STATUS write soft-failed" >&2
fi

exit 0
