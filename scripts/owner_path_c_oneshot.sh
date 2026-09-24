#!/usr/bin/env bash
# Owner Path C ONE-SHOT (Batch 165+): single entry that either lands Path C when a
# write token is present, or prints the unblock menu when it is not.
#
# Batch 168: PATH_C_RELEASE_TAG defaults to batch168-path-c-bundle (pack includes
# this script); unblock menu prefers oneshot --from-bundle from that release.
# Batch 169: PATH_C_RELEASE_TAG defaults to batch169-path-c-bundle; --from-bundle
# Batch 179: PATH_C_RELEASE_TAG defaults to batch179-path-c-bundle (pack+oneshot+refresh)
# Batch 180: PATH_C_RELEASE_TAG defaults to batch180-path-c-bundle (tip 8bd1f03 + PATH_C_STATUS)
# prefers path-c-on-hardening.bundle (git fetch) when present.
#
# Tries in order:
#   a) If MAIN_PUSH_TOKEN / GH_TOKEN env OR a dylan/device token file is present
#      → prefer scripts/owner_open_path_c_pr.sh; on failure fall through to
#        scripts/owner_land_path_c.sh (--from-bundle when requested).
#   b) Else print the unblock menu: device URL+code, set secret, App install,
#      local --from-bundle.
#
# Token discovery (value NEVER printed):
#   1. env MAIN_PUSH_TOKEN
#   2. env GH_TOKEN
#   3. /cursor/stores/self/MAIN_PUSH_TOKEN
#   4. /workspace/.secrets/MAIN_PUSH_TOKEN
#   5. /tmp/gh-dylan-auth/access_token
#
# Usage:
#   ./scripts/owner_path_c_oneshot.sh --dry-run
#   ./scripts/owner_path_c_oneshot.sh
#   ./scripts/owner_path_c_oneshot.sh --from-bundle
#   ./scripts/owner_path_c_oneshot.sh --help
#
# Scientific effect: NONE. lemma_closed stays false. No research promotion.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
# Release tag for local --from-bundle ONE-SHOT (Batch 169: .bundle preferred).
PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch180-path-c-bundle}"
DRY_RUN=0
FROM_BUNDLE=0
MENU_ONLY=0

die() {
  echo "owner_path_c_oneshot: ERROR: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage: owner_path_c_oneshot.sh [--dry-run] [--from-bundle] [--menu-only] [--help]

  --dry-run      Certainty only: report token presence (never the value), then
                 dry-run owner_open_path_c_pr / owner_land_path_c, OR print the
                 unblock menu when no token is available. No clone/push/PR.
  --from-bundle  Prefer owner_land_path_c.sh --from-bundle when landing (after
                 open-PR path fails or is skipped).
  --menu-only    Always print the unblock menu (ignore token presence).
  (default)      If token present → open Path C PR (or land); else unblock menu.

Token sources (first non-empty wins; never printed):
  MAIN_PUSH_TOKEN / GH_TOKEN env
  /cursor/stores/self/MAIN_PUSH_TOKEN
  /workspace/.secrets/MAIN_PUSH_TOKEN
  /tmp/gh-dylan-auth/access_token

Scientific effect: NONE. lemma_closed stays false.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --from-bundle) FROM_BUNDLE=1 ;;
    --menu-only) MENU_ONLY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

OPEN_PR="$TRIAL_ROOT/scripts/owner_open_path_c_pr.sh"
LAND_C="$TRIAL_ROOT/scripts/owner_land_path_c.sh"
UNBLOCK="$TRIAL_ROOT/scripts/print_owner_unblock.sh"
GH_LOGIN_MD="$TRIAL_ROOT/portable/GH_DEVICE_LOGIN.md"
BASE_TIP_FILE="$TRIAL_ROOT/portable/patches/BASE_TIP.txt"

[[ -f "$OPEN_PR" ]] || die "missing $OPEN_PR"
[[ -f "$LAND_C" ]] || die "missing $LAND_C"
[[ -x "$OPEN_PR" ]] || chmod +x "$OPEN_PR" || true
[[ -x "$LAND_C" ]] || chmod +x "$LAND_C" || true

# Resolve token without ever echoing its value.
TOKEN_SOURCE="none"
TOKEN_VALUE=""

read_file_token() {
  local path="$1"
  local label="$2"
  if [[ -f "$path" ]]; then
    # strip trailing newlines only; keep content private
    local val
    val="$(tr -d '\r' <"$path" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' | head -n1)"
    if [[ -n "$val" ]]; then
      TOKEN_VALUE="$val"
      TOKEN_SOURCE="$label"
      return 0
    fi
  fi
  return 1
}

if [[ -n "${MAIN_PUSH_TOKEN:-}" ]]; then
  TOKEN_VALUE="$MAIN_PUSH_TOKEN"
  TOKEN_SOURCE="env:MAIN_PUSH_TOKEN"
elif [[ -n "${GH_TOKEN:-}" ]]; then
  TOKEN_VALUE="$GH_TOKEN"
  TOKEN_SOURCE="env:GH_TOKEN"
elif read_file_token "/cursor/stores/self/MAIN_PUSH_TOKEN" "file:/cursor/stores/self/MAIN_PUSH_TOKEN"; then
  :
elif read_file_token "/workspace/.secrets/MAIN_PUSH_TOKEN" "file:/workspace/.secrets/MAIN_PUSH_TOKEN"; then
  :
elif read_file_token "/tmp/gh-dylan-auth/access_token" "file:/tmp/gh-dylan-auth/access_token"; then
  :
fi

HAS_TOKEN=0
if [[ -n "$TOKEN_VALUE" ]]; then
  HAS_TOKEN=1
fi

# Current device user code (public) for the unblock menu — never a secret token.
DEVICE_USER_CODE="(see portable/GH_DEVICE_LOGIN.md)"
DEVICE_URL="https://github.com/login/device"
if [[ -f "$GH_LOGIN_MD" ]]; then
  # Prefer the markdown table "User code | `XXXX-XXXX`" line.
  code_line="$(grep -E 'User code' "$GH_LOGIN_MD" | head -n1 || true)"
  if [[ -n "$code_line" ]]; then
    extracted="$(printf '%s' "$code_line" | grep -oE '[A-Z0-9]{4}-[A-Z0-9]{4}' | head -n1 || true)"
    [[ -n "$extracted" ]] && DEVICE_USER_CODE="$extracted"
  fi
fi
BASE_TIP_SHORT="unknown"
if [[ -f "$BASE_TIP_FILE" ]]; then
  BASE_TIP_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
  BASE_TIP_SHORT="${BASE_TIP_LINE##* }"
  BASE_TIP_SHORT="${BASE_TIP_SHORT:0:7}"
fi

print_unblock_menu() {
  echo "=== owner_path_c_oneshot — UNBLOCK MENU (no write token) ==="
  echo "token_source=none has_token=false"
  echo "scientific_effect=NONE lemma_closed=false"
  echo
  echo "Path C cannot land until Dylan (or an owner PAT) unblocks write on"
  echo "d6g8k5htny-coder/main. Pick ONE:"
  echo
  echo "1) Device login (preferred mid-flight):"
  echo "   Open: $DEVICE_URL"
  echo "   Enter code: $DEVICE_USER_CODE"
  echo "   Doc: $GH_LOGIN_MD"
  echo
  echo "2) Set trial Actions secret MAIN_PUSH_TOKEN + dispatch land:"
  echo "   $TRIAL_ROOT/scripts/owner_set_main_push_token.sh --dry-run"
  echo "   MAIN_PUSH_TOKEN=… $TRIAL_ROOT/scripts/owner_set_main_push_token.sh --dispatch"
  echo "   # or: $TRIAL_ROOT/scripts/owner_set_main_push_token.sh --from-gh --dispatch"
  echo
  echo "3) Cursor App install — add d6g8k5htny-coder/main (Contents:Write),"
  echo "   then relaunch Cloud Agent (mid-flight cannot gain main scope):"
  echo "   $TRIAL_ROOT/portable/RELAUNCH_WITH_MAIN_SCOPE.md"
  echo
  echo "4) Local ONE-SHOT from release tarball (--from-bundle; prefers .bundle):"
  echo "   gh release download ${PATH_C_RELEASE_TAG} -R d6g8k5htny-coder/trial \\"
  echo "     -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle'"
  echo "   mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land"
  echo "   /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle"
  echo "   # or: /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle"
  echo "   # git fetch path-c-on-hardening.bundle cursor/portable-engineering-patches && git merge"
  echo "   # BASE_TIP ${BASE_TIP_SHORT}; release ${PATH_C_RELEASE_TAG}; lemma_closed stays false"
  echo
  echo "Also: $TRIAL_ROOT/scripts/print_owner_unblock.sh"
  echo "      $TRIAL_ROOT/scripts/assert_path_c_ready.sh"
  echo "Scientific effect: NONE"
}

echo "=== owner_path_c_oneshot ==="
echo "trial_root=$TRIAL_ROOT"
echo "mode=$([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo live) from_bundle=$FROM_BUNDLE menu_only=$MENU_ONLY"
echo "token_source=$TOKEN_SOURCE has_token=$HAS_TOKEN"
echo "scientific_effect=NONE lemma_closed=false"
echo

if [[ "$MENU_ONLY" -eq 1 ]]; then
  print_unblock_menu
  exit 0
fi

if [[ "$HAS_TOKEN" -eq 0 ]]; then
  print_unblock_menu
  # Still offer live print_owner_unblock when available (richer probe/audit).
  if [[ "$DRY_RUN" -eq 0 && -f "$UNBLOCK" ]]; then
    echo
    echo "--- print_owner_unblock (live probe/audit) ---"
    bash "$UNBLOCK" || true
  fi
  exit 0
fi

# Token present — never print TOKEN_VALUE.
export MAIN_PUSH_TOKEN="$TOKEN_VALUE"
export GH_TOKEN="$TOKEN_VALUE"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "--- dry-run: owner_open_path_c_pr.sh --dry-run ---"
  set +e
  bash "$OPEN_PR" --dry-run
  open_ec=$?
  set -e
  echo "owner_open_path_c_pr dry-run exit=$open_ec"
  echo
  if [[ "$FROM_BUNDLE" -eq 1 ]]; then
    echo "--- dry-run: owner_land_path_c.sh --from-bundle --dry-run ---"
    set +e
    bash "$LAND_C" --from-bundle --dry-run
    land_ec=$?
    set -e
  else
    echo "--- dry-run: owner_land_path_c.sh --dry-run ---"
    set +e
    bash "$LAND_C" --dry-run
    land_ec=$?
    set -e
  fi
  echo "owner_land_path_c dry-run exit=$land_ec"
  if [[ "$open_ec" -eq 0 || "$land_ec" -eq 0 ]]; then
    echo "owner_path_c_oneshot: dry-run OK (token_source=$TOKEN_SOURCE; value not printed)."
    echo "Scientific effect: NONE"
    exit 0
  fi
  echo "owner_path_c_oneshot: ERROR: both dry-runs failed (open=$open_ec land=$land_ec)." >&2
  exit 1
fi

echo "--- live: prefer owner_open_path_c_pr.sh ---"
set +e
bash "$OPEN_PR"
open_ec=$?
set -e
if [[ "$open_ec" -eq 0 ]]; then
  echo "owner_path_c_oneshot: Path C PR path OK via owner_open_path_c_pr.sh"
  echo "Scientific effect: NONE"
  exit 0
fi
echo "owner_open_path_c_pr exit=$open_ec — falling through to owner_land_path_c.sh"

if [[ "$FROM_BUNDLE" -eq 1 ]]; then
  echo "--- live: owner_land_path_c.sh --from-bundle ---"
  bash "$LAND_C" --from-bundle
else
  echo "--- live: owner_land_path_c.sh ---"
  bash "$LAND_C"
fi
echo "owner_path_c_oneshot: Path C land path OK via owner_land_path_c.sh"
echo "Scientific effect: NONE"
exit 0
