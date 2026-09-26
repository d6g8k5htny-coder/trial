#!/usr/bin/env bash
# refresh_path_c_bundle.sh — owner/agent helper: tip fetch → BASE_TIP → apply_all →
# rebuild path-c-on-hardening.{patch,bundle} → VERIFY.json.
#
# Use when hardening tip moves (or --force). Tip-stable + write-blocked batches
# ship this so the next tip move is one command, not tribal knowledge.
#
# Scientific effect: NONE. Never flips lemma_closed / prizes / premises / research.
# Does not push to d6g8k5htny-coder/main. Safe for trial agents and owner laptops.
#
# Usage:
#   ./scripts/refresh_path_c_bundle.sh              # no-op exit 0 if tip == BASE_TIP
#   ./scripts/refresh_path_c_bundle.sh --force       # rebuild even when tip matches
#   ./scripts/refresh_path_c_bundle.sh --dry-run     # fetch + compare only
#   ./scripts/refresh_path_c_bundle.sh --help
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HARDENING_REF="${HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
MAIN_REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
BASE_TIP_FILE="${BASE_TIP_FILE:-$ROOT/portable/patches/BASE_TIP.txt}"
APPLY_ALL="${APPLY_ALL:-$ROOT/portable/patches/apply_all.sh}"
BUNDLE_DIR="${BUNDLE_DIR:-$ROOT/portable/path-c-applied-bundle}"
PATCH_OUT="${PATCH_OUT:-$BUNDLE_DIR/path-c-on-hardening.patch}"
BUNDLE_OUT="${BUNDLE_OUT:-$BUNDLE_DIR/path-c-on-hardening.bundle}"
VERIFY_OUT="${VERIFY_OUT:-$BUNDLE_DIR/VERIFY.json}"
APPLY_MD="${APPLY_MD:-$BUNDLE_DIR/APPLY.md}"
BRANCH="${PATH_C_BRANCH:-cursor/portable-engineering-patches}"
FORCE=0
DRY_RUN=0
KEEP_WORKDIR=0
SKIP_PYTEST=0
# Batch 269: default tracks the automation batch that invoked refresh.
# VERIFY.batch itself must stay release-aligned (see VERIFY write below) so
# pack_portable's release|batch fallback cannot invent batch250-path-c-bundle
# while living release stays batch241-path-c-bundle.
BATCH_TAG="${REFRESH_BATCH_TAG:-406}"

usage() {
  cat <<'EOF'
refresh_path_c_bundle.sh — tip fetch → BASE_TIP update → apply_all → rebuild .patch+.bundle → VERIFY.json

Options:
  --force         Rebuild even when live tip already matches BASE_TIP
  --dry-run       Fetch live tip + compare to BASE_TIP; print plan; exit 0/1
  --keep-workdir  Leave disposable main clone under /tmp for inspection
  --skip-pytest   Skip focused + claims/recovery pytest after apply (faster)
  -h, --help      Show this help

Env:
  HARDENING_REF MAIN_REPO BASE_TIP_FILE APPLY_ALL BUNDLE_DIR PATH_C_BRANCH
  REFRESH_BATCH_TAG   automation stamp → VERIFY.refresh_batch (default 289)
  GITHUB_TOKEN / GH_TOKEN / MAIN_PUSH_TOKEN  optional tip-fetch + clone auth (never printed)
  REFRESH_TIP_FETCH_RETRIES   API retries on 429 / rate-limit 403 (default 3)
  REFRESH_TIP_FETCH_SLEEP_S   base sleep between tip-fetch retries (default 2)

Exit:
  0  tip already current (no --force) OR rebuild succeeded / dry-run match
  1  tip drift detected on --dry-run, or rebuild/apply/verify failed
  2  usage / missing inputs
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --keep-workdir) KEEP_WORKDIR=1; shift ;;
    --skip-pytest) SKIP_PYTEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "refresh_path_c_bundle: unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

die() { echo "refresh_path_c_bundle: ERROR: $*" >&2; exit 1; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"; }

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

need_cmd git
need_cmd python3
need_cmd curl
[[ -f "$BASE_TIP_FILE" ]] || die "missing BASE_TIP.txt at $BASE_TIP_FILE"
[[ -f "$APPLY_ALL" ]] || die "missing apply_all.sh at $APPLY_ALL"
mkdir -p "$BUNDLE_DIR"

BASE_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
PRIOR_SHA="$(parse_base_tip_sha "$BASE_LINE" || true)"
[[ -n "$PRIOR_SHA" ]] || die "could not parse SHA from BASE_TIP.txt: $BASE_LINE"

API_URL="https://api.github.com/repos/${MAIN_REPO}/commits/${HARDENING_REF}"
# Batch 257: tip-fetch used to die on the first unauthenticated HTTP 403 rate-limit
# (trial CI Tip-drift dry-sim red on shared runner IPs). Retry rate-limits, prefer
# token when present, then gh api / git ls-remote fallbacks. Never print tokens.
TOK="${GITHUB_TOKEN:-${GH_TOKEN:-${MAIN_PUSH_TOKEN:-}}}"
if [[ -z "$TOK" ]] && command -v gh >/dev/null 2>&1; then
  # Prefer gh's stored token without printing (CI may lack env GITHUB_TOKEN on this step).
  TOK="$(gh auth token 2>/dev/null || true)"
fi
TIP_FETCH_RETRIES="${REFRESH_TIP_FETCH_RETRIES:-3}"
TIP_FETCH_SLEEP_S="${REFRESH_TIP_FETCH_SLEEP_S:-2}"
LIVE_SHA=""
LIVE_FETCH_VIA=""

_parse_commit_sha_json() {
  python3 -c '
import json,sys,re
try:
    d=json.load(sys.stdin)
except Exception as e:
    print(f"json_error:{e}", file=sys.stderr)
    raise SystemExit(1)
sha=(d.get("sha") or "").strip().lower()
if not re.fullmatch(r"[0-9a-f]{40}", sha):
    msg=d.get("message") or d.get("error") or "missing sha"
    print(f"bad_sha:{msg}", file=sys.stderr)
    raise SystemExit(1)
print(sha)
'
}

_is_rate_limit_msg() {
  local code="$1" msg="$2"
  local blob
  blob="$(printf '%s %s' "$code" "$msg" | tr '[:upper:]' '[:lower:]')"
  [[ "$code" == "429" ]] && return 0
  [[ "$blob" == *"rate limit"* || "$blob" == *"secondary rate"* ]] && return 0
  return 1
}

echo "refresh_path_c_bundle: fetching live tip ${MAIN_REPO}@${HARDENING_REF}"
# 1) curl GitHub commits API (token when available) with brief rate-limit retries.
attempt=1
while [[ "$attempt" -le "$TIP_FETCH_RETRIES" ]]; do
  AUTH_HDR=()
  if [[ -n "$TOK" ]]; then
    AUTH_HDR=(-H "Authorization: Bearer ${TOK}")
  fi
  HTTP_CODE=0
  LIVE_JSON=""
  if LIVE_JSON="$(curl -sS -w '\n%{http_code}' "${AUTH_HDR[@]}" -H 'Accept: application/vnd.github+json' \
      -H 'User-Agent: trial-refresh-path-c-bundle' "$API_URL")"; then
    HTTP_CODE="$(printf '%s' "$LIVE_JSON" | tail -n1)"
    LIVE_JSON="$(printf '%s' "$LIVE_JSON" | sed '$d')"
    if [[ "$HTTP_CODE" == "200" ]]; then
      if LIVE_SHA="$(printf '%s' "$LIVE_JSON" | _parse_commit_sha_json)"; then
        LIVE_FETCH_VIA="curl_api"
        break
      fi
    else
      API_MSG="$(printf '%s' "$LIVE_JSON" | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print("non-json body"); raise SystemExit(0)
print(d.get("message") or d.get("error") or d.get("documentation_url") or "unknown")
' 2>/dev/null || echo "unparseable")"
      if _is_rate_limit_msg "$HTTP_CODE" "$API_MSG" && [[ "$attempt" -lt "$TIP_FETCH_RETRIES" ]]; then
        sleep_s="$(python3 -c "print(min(${TIP_FETCH_SLEEP_S}*${attempt}, 30))" 2>/dev/null || echo "$TIP_FETCH_SLEEP_S")"
        echo "refresh_path_c_bundle: tip fetch HTTP ${HTTP_CODE} rate-limit; retry ${attempt}/${TIP_FETCH_RETRIES} sleep=${sleep_s}s"
        sleep "$sleep_s"
        attempt=$((attempt + 1))
        continue
      fi
      echo "refresh_path_c_bundle: tip fetch HTTP ${HTTP_CODE}: ${API_MSG} (will try fallbacks)"
      break
    fi
  else
    echo "refresh_path_c_bundle: tip fetch curl transport failed (will try fallbacks)"
    break
  fi
  attempt=$((attempt + 1))
done

# 2) gh api fallback (uses gh auth / GH_TOKEN; never print token).
if [[ -z "$LIVE_SHA" ]] && command -v gh >/dev/null 2>&1; then
  if GH_JSON="$(gh api "repos/${MAIN_REPO}/commits/${HARDENING_REF}" 2>/dev/null)"; then
    if LIVE_SHA="$(printf '%s' "$GH_JSON" | _parse_commit_sha_json)"; then
      LIVE_FETCH_VIA="gh_api"
    else
      LIVE_SHA=""
    fi
  fi
fi

# 3) git ls-remote fallback — avoids REST rate-limit ceilings on shared CI IPs.
if [[ -z "$LIVE_SHA" ]]; then
  LS_OUT="$(git ls-remote "https://github.com/${MAIN_REPO}.git" "refs/heads/${HARDENING_REF}" 2>/dev/null | awk '{print $1}' | head -n1 || true)"
  if [[ "$LS_OUT" =~ ^[0-9a-f]{40}$ ]]; then
    LIVE_SHA="$LS_OUT"
    LIVE_FETCH_VIA="git_ls_remote"
  fi
fi

[[ -n "$LIVE_SHA" ]] || die "tip fetch failed (curl/gh/ls-remote); last HTTP may be rate-limit — set GITHUB_TOKEN or retry"
echo "refresh_path_c_bundle: tip_fetch_via=${LIVE_FETCH_VIA}"
LIVE_SHORT="${LIVE_SHA:0:7}"
PRIOR_SHORT="${PRIOR_SHA:0:7}"

TIP_MATCH=0
if [[ ${#PRIOR_SHA} -eq 40 && "$LIVE_SHA" == "$PRIOR_SHA" ]]; then
  TIP_MATCH=1
elif [[ ${#PRIOR_SHA} -ge 7 && ${#PRIOR_SHA} -lt 40 && "${LIVE_SHA:0:${#PRIOR_SHA}}" == "$PRIOR_SHA" ]]; then
  TIP_MATCH=1
  PRIOR_SHA="$LIVE_SHA"
fi

echo "refresh_path_c_bundle: BASE_TIP=${PRIOR_SHORT} live=${LIVE_SHORT} match=${TIP_MATCH} force=${FORCE} dry_run=${DRY_RUN}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  if [[ "$TIP_MATCH" -eq 1 ]]; then
    echo "refresh_path_c_bundle: dry-run OK tip stable @ ${LIVE_SHORT} (no rebuild needed)"
    exit 0
  fi
  echo "refresh_path_c_bundle: dry-run TIP_DRIFT ${PRIOR_SHORT} -> ${LIVE_SHORT}"
  echo "refresh_path_c_bundle: fix path: ./scripts/refresh_path_c_bundle.sh  # updates BASE_TIP + rebuilds .patch+.bundle+VERIFY (does NOT push to main)"
  exit 1
fi

if [[ "$TIP_MATCH" -eq 1 && "$FORCE" -eq 0 ]]; then
  echo "refresh_path_c_bundle: tip stable @ ${LIVE_SHORT}; nothing to do (pass --force to rebuild)"
  exit 0
fi

CLEANUP_DIR=""
cleanup() {
  if [[ -n "$CLEANUP_DIR" && "$KEEP_WORKDIR" -eq 0 && -d "$CLEANUP_DIR" ]]; then
    rm -rf "$CLEANUP_DIR"
  fi
}
trap cleanup EXIT

CLEANUP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/refresh-path-c-bundle.XXXXXX")"
WORKDIR="$CLEANUP_DIR/main"
CLONE_URL="https://github.com/${MAIN_REPO}.git"
if [[ -n "$TOK" ]]; then
  CLONE_URL="https://x-access-token:${TOK}@github.com/${MAIN_REPO}.git"
fi

echo "refresh_path_c_bundle: shallow-clone ${HARDENING_REF} @ ${LIVE_SHORT}"
git clone --depth 80 --branch "$HARDENING_REF" "$CLONE_URL" "$WORKDIR"
git -C "$WORKDIR" checkout -B "$BRANCH" "$LIVE_SHA"
ACTUAL="$(git -C "$WORKDIR" rev-parse HEAD)"
[[ "$ACTUAL" == "$LIVE_SHA" ]] || die "checkout mismatch $ACTUAL != $LIVE_SHA"

echo "refresh_path_c_bundle: writing BASE_TIP.txt -> ${HARDENING_REF} ${LIVE_SHA}"
printf '%s %s\n' "$HARDENING_REF" "$LIVE_SHA" >"$BASE_TIP_FILE"

echo "refresh_path_c_bundle: apply_all --check"
(cd "$WORKDIR" && bash "$APPLY_ALL" --check) || die "apply_all --check failed on ${LIVE_SHORT}"
echo "refresh_path_c_bundle: apply_all (apply)"
(cd "$WORKDIR" && bash "$APPLY_ALL") || die "apply_all failed on ${LIVE_SHORT}"

STATUS_OUT="$(cd "$WORKDIR" && python3 tools/math_status_check.py 2>&1)" || die "math_status_check failed"
echo "$STATUS_OUT"
echo "$STATUS_OUT" | grep -q 'lemma_closed=false' || die "lemma_closed is not false after apply_all"
if echo "$STATUS_OUT" | grep -Eq 'problems[=:][[:space:]]*[1-9]'; then
  die "math_status_check reported problems>0"
fi
DISPOSITION="$(echo "$STATUS_OUT" | python3 -c '
import re,sys
t=sys.stdin.read()
m=re.search(r"disposition[=:\s]+([A-Z_]+)", t)
print(m.group(1) if m else "UNKNOWN")
')"
PROBLEMS="$(echo "$STATUS_OUT" | python3 -c '
import re,sys
t=sys.stdin.read()
m=re.search(r"problems[=:\s]+(\d+)", t)
print(m.group(1) if m else "0")
')"

FOCUSED_PASS=0
CLAIMS_PASS=0
if [[ "$SKIP_PYTEST" -eq 0 ]]; then
  echo "refresh_path_c_bundle: focused pytest"
  FOCUSED_OUT="$(cd "$WORKDIR" && python3 -m pytest -q \
    tests/test_carriers.py tests/test_math_status.py \
    tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
    tests/test_inventable_jetmod_instrumentation_status.py 2>&1)" || die "focused pytest failed"
  echo "$FOCUSED_OUT" | tail -n 5
  FOCUSED_PASS="$(echo "$FOCUSED_OUT" | python3 -c '
import re,sys
t=sys.stdin.read()
m=re.search(r"(\d+) passed", t)
print(m.group(1) if m else "0")
')"
  echo "refresh_path_c_bundle: claims+recovery pytest"
  CLAIMS_OUT="$(cd "$WORKDIR" && python3 -m pytest -q tests/test_claims.py tests/test_recovery.py 2>&1)" || die "claims/recovery pytest failed"
  echo "$CLAIMS_OUT" | tail -n 5
  CLAIMS_PASS="$(echo "$CLAIMS_OUT" | python3 -c '
import re,sys
t=sys.stdin.read()
m=re.search(r"(\d+) passed", t)
print(m.group(1) if m else "0")
')"
else
  echo "refresh_path_c_bundle: --skip-pytest set; skipping pytest gates"
fi

echo "refresh_path_c_bundle: commit applied engineering stack (local only)"
git -C "$WORKDIR" add -A
git -C "$WORKDIR" -c user.email='path-c-refresh@local' -c user.name='path-c-refresh' \
  commit -m "portable engineering patches (apply_all 0001-0004+0008-0019) on ${LIVE_SHORT}" \
  --allow-empty >/dev/null
APPLIED_SHA="$(git -C "$WORKDIR" rev-parse HEAD)"
APPLIED_SHORT="${APPLIED_SHA:0:7}"

echo "refresh_path_c_bundle: format-patch ${LIVE_SHORT}..${APPLIED_SHORT} -> path-c-on-hardening.patch"
PATCH_TMP="$(mktemp "${TMPDIR:-/tmp}/refresh-patch.XXXXXX.patch")"
git -C "$WORKDIR" format-patch --stdout "${LIVE_SHA}..${APPLIED_SHA}" >"$PATCH_TMP"
[[ -s "$PATCH_TMP" ]] || { rm -f "$PATCH_TMP"; die "empty patch output"; }
# Batch 232: when Path C already on tip, format-patch is an empty allow-empty
# commit (subject-only). Keep the prior full .patch+.bundle so owner re-apply
# assets are not destroyed by tip-refresh after land.
PATCH_BYTES="$(wc -c <"$PATCH_TMP" | tr -d ' ')"
if [[ "$PATCH_BYTES" -lt 512 ]] && [[ -s "$PATCH_OUT" ]] && [[ -s "$BUNDLE_OUT" ]]; then
  echo "refresh_path_c_bundle: tip already carries Path C stack (format-patch ${PATCH_BYTES}B); keeping prior .patch+.bundle"
  rm -f "$PATCH_TMP"
  KEEP_PRIOR_BUNDLE=1
else
  mv -f "$PATCH_TMP" "$PATCH_OUT"
  KEEP_PRIOR_BUNDLE=0
fi

if [[ "${KEEP_PRIOR_BUNDLE:-0}" -eq 0 ]]; then
echo "refresh_path_c_bundle: git bundle create path-c-on-hardening.bundle ${LIVE_SHORT}..${APPLIED_SHORT}"
# Bundle must be fetchable onto a clone that already has LIVE_SHA.
# Prefer BRANCH tip + ^LIVE_SHA (Batch 180): range+ref form can fail on some
# shallow checkouts with "Repository lacks these prerequisite commits".
rm -f "$BUNDLE_OUT"
BUNDLE_ERR="$(mktemp "${TMPDIR:-/tmp}/refresh-bundle.XXXXXX.err")"
if ! git -C "$WORKDIR" bundle create "$BUNDLE_OUT" "$BRANCH" "^${LIVE_SHA}" 2>"$BUNDLE_ERR"; then
  echo "refresh_path_c_bundle: bundle create (BRANCH ^LIVE) failed; deepening + retry" >&2
  cat "$BUNDLE_ERR" >&2 || true
  git -C "$WORKDIR" fetch --deepen=30 origin "$HARDENING_REF" 2>/dev/null \
    || git -C "$WORKDIR" fetch --deepen=30 origin 2>/dev/null \
    || true
  if ! git -C "$WORKDIR" bundle create "$BUNDLE_OUT" "$BRANCH" "^${LIVE_SHA}" 2>"$BUNDLE_ERR"; then
    echo "refresh_path_c_bundle: deepen retry failed; falling back to range form" >&2
    cat "$BUNDLE_ERR" >&2 || true
    git -C "$WORKDIR" bundle create "$BUNDLE_OUT" "${LIVE_SHA}..${APPLIED_SHA}" "$BRANCH"
  fi
fi
rm -f "$BUNDLE_ERR"
# Verify against WORKDIR (hardening clone) — NOT trial ROOT, which lacks LIVE_SHA
# and would falsely report "Repository lacks these prerequisite commits" (Batch 180).
git -C "$WORKDIR" bundle verify "$BUNDLE_OUT" >/dev/null
else
  echo "refresh_path_c_bundle: skipped bundle recreate (kept prior assets)"
fi
# Batch 250: when keeping prior .bundle, VERIFY must name the *kept* bundle head —
# not the local allow-empty commit (unpublished; HTTP 422 on GitHub).
KEEP_PRIOR_BUNDLE="${KEEP_PRIOR_BUNDLE:-0}"
LOCAL_ALLOW_EMPTY_SHA="$APPLIED_SHA"
BUNDLE_HEAD_SHA=""
if [[ -s "$BUNDLE_OUT" ]]; then
  # list-heads does not need object DB; tolerate empty/fail under set -e.
  BUNDLE_HEAD_SHA="$(git bundle list-heads "$BUNDLE_OUT" 2>/dev/null | awk '{print $1; exit}' || true)"
fi
BUNDLE_REQUIRES_SHA=""
if [[ -s "$BUNDLE_OUT" ]]; then
  # Batch 325: verify against WORKDIR (hardening clone), never trial ROOT.
  # Trial lacks bundle prerequisite commits → `git bundle verify` exits 1;
  # under set -euo pipefail that aborted keep-prior before VERIFY/APPLY/MANIFEST
  # write (tip-sync / --force incomplete). Same Batch 180 class as the
  # recreate-path verify above.
  _bundle_verify_out=""
  if [[ -n "${WORKDIR:-}" && -d "${WORKDIR}/.git" ]]; then
    _bundle_verify_out="$(git -C "$WORKDIR" bundle verify "$BUNDLE_OUT" 2>&1 || true)"
  else
    _bundle_verify_out="$(git bundle verify "$BUNDLE_OUT" 2>&1 || true)"
  fi
  BUNDLE_REQUIRES_SHA="$(printf '%s\n' "$_bundle_verify_out" | awk '/requires this ref:/{getline; gsub(/^[[:space:]]+/,"",$0); print; exit}' || true)"
  unset _bundle_verify_out
fi
if [[ "$KEEP_PRIOR_BUNDLE" -eq 1 && -n "$BUNDLE_HEAD_SHA" ]]; then
  APPLIED_SHA="$BUNDLE_HEAD_SHA"
  APPLIED_SHORT="${APPLIED_SHA:0:7}"
  echo "refresh_path_c_bundle: VERIFY honesty — applied_commit_sha=${APPLIED_SHORT} (kept bundle head; local allow-empty ${LOCAL_ALLOW_EMPTY_SHA:0:7} not published)"
fi
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - <<PY
import json
import re
from pathlib import Path
# Batch 232: preserve Path C land evidence across tip-refresh rewrites.
# Batch 250: keep_prior_bundle ⇒ VERIFY tracks kept .bundle head (not allow-empty).
# Batch 269: VERIFY.batch stays release-aligned; automation stamp → refresh_batch.
prior = {}
prior_path = Path("$VERIFY_OUT")
if prior_path.is_file():
    try:
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        prior = {}
keep_prior = int("$KEEP_PRIOR_BUNDLE") == 1
applied_sha = "$APPLIED_SHA"
bundle_range = f"$LIVE_SHA..$APPLIED_SHA"
bundle_requires = "$LIVE_SHA"
if keep_prior:
    # Prefer actual kept-bundle metadata over the unpublished allow-empty SHA.
    requires = "$BUNDLE_REQUIRES_SHA".strip()
    if requires:
        bundle_requires = requires
    elif prior.get("bundle_requires_ref"):
        bundle_requires = prior["bundle_requires_ref"]
    prior_range = str(prior.get("bundle_range") or "")
    # Keep prior range only when it still ends at the kept bundle head.
    if prior_range.endswith(applied_sha) or prior_range.endswith(applied_sha[:7]):
        bundle_range = prior_range
    else:
        bundle_range = f"{bundle_requires}..{applied_sha}"
note = (
    f"Batch $BATCH_TAG: refresh_path_c_bundle.sh @ ${LIVE_SHORT}; "
    f"{'kept prior .patch+.bundle (already-on-tip); ' if keep_prior else 'rebuilt; '}"
    f"lemma_closed=false; problems=$PROBLEMS"
)
# Batch 269: VERIFY.batch is the living-release contract (pack fallback).
# Automation stamp lives in refresh_batch so keep-prior tip refresh cannot
# plant batch{REFRESH_BATCH_TAG}-path-c-bundle while release stays batch241.
verify = {
  "batch": str("$BATCH_TAG"),
  "refresh_batch": str("$BATCH_TAG"),
  "generated_at_utc": "$GENERATED_AT",
  "base_tip_sha": "$LIVE_SHA",
  "applied_commit_sha": applied_sha,
  "hardening_ref": "$HARDENING_REF",
  "prior_base_tip_sha": "$PRIOR_SHA" if "$TIP_MATCH" == "0" else "$LIVE_SHA",
  "tip_refresh": bool(int("$TIP_MATCH") == 0),
  "tip_refresh_via": "refresh_path_c_bundle.sh",
  "bundle_refresh": (not keep_prior),
  "keep_prior_bundle": keep_prior,
  "git_bundle": True,
  "bundle_file": "path-c-on-hardening.bundle",
  "bundle_branch": "$BRANCH",
  "bundle_range": bundle_range,
  "bundle_requires_ref": bundle_requires,
  "owner_apply": "git fetch path-c-on-hardening.bundle $BRANCH && git merge --ff-only FETCH_HEAD  (or git pull …)",
  "problems": int("$PROBLEMS"),
  "disposition": "$DISPOSITION",
  "lemma_closed": False,
  "pytest": {
    "focused_passed": int("$FOCUSED_PASS"),
    "focused_resource_warnings": 0,
    "claims_recovery_passed": int("$CLAIMS_PASS"),
    "claims_recovery_resource_warnings": 0,
    "focused_files": [
      "tests/test_carriers.py",
      "tests/test_math_status.py",
      "tests/test_inventable_jetmod_probes.py",
      "tests/test_gaussian_moments.py",
      "tests/test_inventable_jetmod_instrumentation_status.py",
    ],
  },
  "patch_file": "path-c-on-hardening.patch",
  "scientific_effect": "NONE",
  "goal_complete": False,
  "note": note,
  "force": bool(int("$FORCE")),
}
if keep_prior:
    verify["local_allow_empty_sha"] = "$LOCAL_ALLOW_EMPTY_SHA"
    # Batch 273: keep-prior tip refresh must not wipe recorded pytest counts to 0
    # when --skip-pytest (or a parse miss) leaves FOCUSED_PASS/CLAIMS_PASS at 0.
    # Same honesty class as Batch 250 applied_commit_sha (kept bundle head).
    prior_pytest = prior.get("pytest") if isinstance(prior.get("pytest"), dict) else {}
    cur_pytest = verify.get("pytest") if isinstance(verify.get("pytest"), dict) else {}
    for _pk in ("focused_passed", "claims_recovery_passed"):
        cur_v = cur_pytest.get(_pk)
        prior_v = prior_pytest.get(_pk)
        if cur_v in (0, None) and isinstance(prior_v, int) and prior_v > 0:
            cur_pytest[_pk] = prior_v
    for _wk in ("focused_resource_warnings", "claims_recovery_resource_warnings"):
        if cur_pytest.get(_wk) in (None,) and isinstance(prior_pytest.get(_wk), int):
            cur_pytest[_wk] = prior_pytest[_wk]
    if prior_pytest.get("focused_files") and not cur_pytest.get("focused_files"):
        cur_pytest["focused_files"] = prior_pytest["focused_files"]
    verify["pytest"] = cur_pytest
    if int("$FOCUSED_PASS") == 0 and isinstance(prior_pytest.get("focused_passed"), int) and prior_pytest["focused_passed"] > 0:
        print(
            "refresh_path_c_bundle: VERIFY honesty — preserved prior pytest "
            f"focused_passed={prior_pytest.get('focused_passed')} "
            f"claims_recovery_passed={prior_pytest.get('claims_recovery_passed')} "
            "(keep-prior; current run reported 0)"
        )
# Preserve land evidence (PR #64 @ 93a4ecd) when tip moves past Path C land.
for key in (
    "path_c_landed",
    "path_c_pr_url",
    "merge_commit_sha",
    "write_vector",
    "path_c_applied_sha",
    "release",
    "release_tag",
    # Batch 250: keep follow-on landed markers across keep-prior / tip-refresh.
    "path_c_0018_landed",
    "path_c_0018_via",
    "path_c_0019_landed",
    "path_c_0019_via",
    "path_c_0019_pr_url",
    "path_c_0019_merge_commit_sha",
    "flipped_anything",
):
    if key in verify and verify[key] not in (None, "", False):
        continue
    val = prior.get(key)
    if val not in (None, "", False):
        verify[key] = val
# Explicit false must also survive (flipped_anything=false).
if "flipped_anything" not in verify and "flipped_anything" in prior:
    verify["flipped_anything"] = prior["flipped_anything"]
if prior.get("path_c_0018_landed") is True:
    verify["path_c_0018_landed"] = True
if prior.get("path_c_0019_landed") is True:
    verify["path_c_0019_landed"] = True
# If prior said Path C landed and this tip is a descendant of that land, keep true.
if prior.get("path_c_landed") is True:
    verify["path_c_landed"] = True
    if not verify.get("path_c_pr_url") and prior.get("path_c_pr_url"):
        verify["path_c_pr_url"] = prior["path_c_pr_url"]
    if not verify.get("merge_commit_sha") and prior.get("merge_commit_sha"):
        verify["merge_commit_sha"] = prior["merge_commit_sha"]
# Default release label when tip-refresh wiped it (Intent living-release contract).
if not verify.get("release"):
    verify["release"] = prior.get("release") or "batch241-path-c-bundle"
# Batch 269: align VERIFY.batch with living release so pack's batch fallback
# cannot invent a divergent tag (evidence: batch=250 + release=batch241 after
# keep-prior tip refresh with stale REFRESH_BATCH_TAG default).
rel = verify.get("release")
m = re.fullmatch(r"batch(\d+)-path-c-bundle", str(rel or "").strip())
if m:
    verify["batch"] = m.group(1)
    verify["release_batch_aligned"] = True
else:
    verify["release_batch_aligned"] = False
Path("$VERIFY_OUT").write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
print(
    "refresh_path_c_bundle: wrote VERIFY.json "
    f"batch={verify.get('batch')} refresh_batch={verify.get('refresh_batch')} "
    f"release={verify.get('release')} aligned={verify.get('release_batch_aligned')}"
)
PY

# Keep APPLY.md tip SHA current without rewriting the whole playbook.
# Batch 273: also soft-update living-tip claims (`hardening tip **SHA** (== BASE_TIP)`,
# `On tip **SHA**`, `Living tip note: at SHA`) — Batch 272 tip-refresh left those
# pinned at 542e6ec while BASE_TIP/checkout moved to bfb7c38 (APPLY honesty lie).
# Batch 278: quote the Python heredoc. Pre-278 used <<PY so backticks inside the
# living-tip regexes were shell command-substitutions → APPLY soft-update aborted
# under set -e before MANIFEST update (first tip move after Batch 273).
if [[ -f "$APPLY_MD" ]]; then
  APPLY_MD="$APPLY_MD" LIVE_SHORT="$LIVE_SHORT" LIVE_SHA="$LIVE_SHA" python3 - <<'PY'
from pathlib import Path
import os
import re

p = Path(os.environ["APPLY_MD"])
text = p.read_text(encoding="utf-8")
live_short = os.environ["LIVE_SHORT"]
live_sha = os.environ["LIVE_SHA"]
# Soft-update BASE_TIP / checkout SHA mentions; leave narrative intact.
text2, n = re.subn(
    r"(BASE_TIP\s+[\\`*]*)([0-9a-f]{7,40})",
    lambda m: m.group(1) + live_short,
    text,
    count=5,
    flags=re.I,
)
# Also refresh the explicit checkout SHA used in Manual section when present.
text2, n2 = re.subn(
    r"(git checkout -B cursor/portable-engineering-patches\s+)([0-9a-f]{40})",
    lambda m: m.group(1) + live_sha,
    text2,
    count=2,
)
# Living tip header: hardening tip **`SHA`** (== BASE_TIP
text2, n3 = re.subn(
    r"(hardening tip\s+\*\*`?)([0-9a-f]{7,40})(`?\*\*\s*\(==\s*BASE_TIP)",
    lambda m: m.group(1) + live_short + m.group(3),
    text2,
    count=3,
    flags=re.I,
)
# ONE-SHOT expect line: On tip **`SHA`**
text2, n4 = re.subn(
    r"(On tip\s+\*\*`?)([0-9a-f]{7,40})(`?\*\*)",
    lambda m: m.group(1) + live_short + m.group(3),
    text2,
    count=2,
    flags=re.I,
)
# Living tip note: at `SHA` (markdown may bold the label: **Living tip note:**)
text2, n5 = re.subn(
    r"(Living tip note:\*+\s+at\s+`?|Living tip note:\s+at\s+`?)([0-9a-f]{7,40})(`?)",
    lambda m: m.group(1) + live_short + m.group(3),
    text2,
    count=2,
    flags=re.I,
)
# "Do not re-land Path C onto `SHA`" when SHA was the prior living tip claim.
text2, n6 = re.subn(
    r"(Do \*\*not\*\* re-land Path C onto\s+`)([0-9a-f]{7,40})(`)",
    lambda m: m.group(1) + live_short + m.group(3),
    text2,
    count=2,
    flags=re.I,
)
n_total = n + n2 + n3 + n4 + n5 + n6
if n_total:
    p.write_text(text2, encoding="utf-8")
    print(
        "refresh_path_c_bundle: soft-updated APPLY.md tip mentions "
        f"(n={n}+{n2}+living={n3}+{n4}+{n5}+{n6})"
    )
else:
    print("refresh_path_c_bundle: APPLY.md tip mentions unchanged (manual review OK)")
PY
fi

# Soft-update MANIFEST verified_on_tip when present.
# Batch 275: MANIFEST.verified_batch must stay release-aligned (same contract as
# VERIFY.batch after Batch 269). Stamping verified_batch=$BATCH_TAG (automation)
# would regress 241→269/275 on the next tip-refresh/--force and re-open the
# pack fallback landmine Batch 269 closed for VERIFY.
MANIFEST="$ROOT/portable/patches/MANIFEST.json"
if [[ -f "$MANIFEST" ]]; then
  python3 - <<PY
import json
import re
from pathlib import Path
p = Path("$MANIFEST")
data = json.loads(p.read_text(encoding="utf-8"))
data["base_tip_ref"] = "$HARDENING_REF $LIVE_SHA"
data["verified_on_tip"] = "$LIVE_SHA"
data["generated_at_utc"] = "$GENERATED_AT"
data["lemma_closed"] = False
data["scientific_effect"] = "NONE"
data["goal_complete"] = False
# Automation stamp (mirrors VERIFY.refresh_batch).
data["refresh_batch"] = str("$BATCH_TAG")
# Release-aligned verified_batch: prefer VERIFY.batch after Batch 269 align.
aligned = None
verify_path = Path("$VERIFY_OUT")
if verify_path.is_file():
    try:
        v = json.loads(verify_path.read_text(encoding="utf-8"))
        if v.get("batch") not in (None, ""):
            aligned = str(v["batch"])
        if not aligned:
            rel = v.get("release") or ""
            m = re.fullmatch(r"batch(\d+)-path-c-bundle", str(rel).strip())
            if m:
                aligned = m.group(1)
    except (OSError, json.JSONDecodeError, TypeError):
        aligned = None
if not aligned:
    # Fall back to prior MANIFEST / living release pin — never plant BATCH_TAG.
    prior_vb = data.get("verified_batch")
    if prior_vb not in (None, "") and str(prior_vb) != str("$BATCH_TAG"):
        aligned = str(prior_vb)
    else:
        aligned = "241"
data["verified_batch"] = aligned
data["tip_refresh_via"] = "refresh_path_c_bundle.sh"
for item in data.get("patches", []):
    if item.get("in_apply_all"):
        item["verified_on_tip"] = "$LIVE_SHA"
p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(
    "refresh_path_c_bundle: updated MANIFEST.json verified_on_tip "
    f"verified_batch={aligned} refresh_batch={data.get('refresh_batch')}"
)
PY
fi

echo "refresh_path_c_bundle: OK tip=${LIVE_SHORT} applied=${APPLIED_SHORT} patch=$(wc -c <"$PATCH_OUT")B bundle=$(wc -c <"$BUNDLE_OUT")B lemma_closed=false scientific_effect=NONE"
exit 0
