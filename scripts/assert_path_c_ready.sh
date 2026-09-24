#!/usr/bin/env bash
# assert_path_c_ready.sh — exit 0 only when Path C dry-apply readiness holds.
#
# Gates (all required):
#   1) portable/patches/BASE_TIP.txt SHA matches live hardening tip
#   2) portable/patches/apply_all.sh --check OK on that tip
#   3) math_status_check after apply reports lemma_closed=false
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
  2) portable/patches/apply_all.sh --check OK on that tip
  3) math_status_check after apply reports lemma_closed=false

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
STATUS_OUT="$(cd "$WORKDIR" && python3 tools/math_status_check.py 2>&1)" || {
  echo "assert_path_c_ready: FAIL math_status_check exited non-zero" >&2
  echo "$STATUS_OUT" >&2
  exit 1
}
echo "$STATUS_OUT"
if ! echo "$STATUS_OUT" | grep -q 'lemma_closed=false'; then
  echo "assert_path_c_ready: FAIL lemma_closed is not false after apply_all" >&2
  exit 1
fi
if echo "$STATUS_OUT" | grep -Eq 'problems[=:][[:space:]]*[1-9]'; then
  echo "assert_path_c_ready: FAIL math_status_check reported problems>0" >&2
  exit 1
fi

echo "assert_path_c_ready: OK tip=${LIVE_SHA:0:7} apply_all=check+apply lemma_closed=false scientific_effect=NONE"

# Batch 180: emit portable/PATH_C_STATUS.json (no secrets; lemma_closed stays false).
STATUS_PY="${ROOT}/scripts/write_path_c_status.py"
if [[ -f "$STATUS_PY" ]]; then
  echo "assert_path_c_ready: writing PATH_C_STATUS.json"
  python3 "$STATUS_PY" --skip-write-probe || echo "assert_path_c_ready: warn PATH_C_STATUS write soft-failed" >&2
fi

exit 0
