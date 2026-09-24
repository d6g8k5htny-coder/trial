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
BATCH_TAG="${REFRESH_BATCH_TAG:-176}"

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
  REFRESH_BATCH_TAG   recorded in VERIFY.json (default 176)
  GITHUB_TOKEN / GH_TOKEN / MAIN_PUSH_TOKEN  optional clone auth (never printed)

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
AUTH_HDR=()
TOK="${GITHUB_TOKEN:-${GH_TOKEN:-${MAIN_PUSH_TOKEN:-}}}"
if [[ -n "$TOK" ]]; then
  AUTH_HDR=(-H "Authorization: Bearer ${TOK}")
fi
echo "refresh_path_c_bundle: fetching live tip ${MAIN_REPO}@${HARDENING_REF}"
# -f: treat HTTP >=400 as failure (404 repo/ref, 403 rate-limit, etc.)
HTTP_CODE=0
LIVE_JSON="$(curl -sS -w '\n%{http_code}' "${AUTH_HDR[@]}" -H 'Accept: application/vnd.github+json' "$API_URL")" || die "tip fetch failed (curl transport)"
HTTP_CODE="$(printf '%s' "$LIVE_JSON" | tail -n1)"
LIVE_JSON="$(printf '%s' "$LIVE_JSON" | sed '$d')"
if [[ "$HTTP_CODE" != "200" ]]; then
  API_MSG="$(printf '%s' "$LIVE_JSON" | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print("non-json body"); raise SystemExit(0)
print(d.get("message") or d.get("error") or d.get("documentation_url") or "unknown")
' 2>/dev/null || echo "unparseable")"
  die "tip fetch HTTP ${HTTP_CODE}: ${API_MSG}"
fi
LIVE_SHA="$(printf '%s' "$LIVE_JSON" | python3 -c '
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
')" || die "could not parse live tip sha from API JSON"
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
  commit -m "portable engineering patches (apply_all 0001-0004+0008-0016) on ${LIVE_SHORT}" \
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
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - <<PY
import json
from pathlib import Path
# Batch 232: preserve Path C land evidence across tip-refresh rewrites.
prior = {}
prior_path = Path("$VERIFY_OUT")
if prior_path.is_file():
    try:
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        prior = {}
verify = {
  "batch": str("$BATCH_TAG"),
  "generated_at_utc": "$GENERATED_AT",
  "base_tip_sha": "$LIVE_SHA",
  "applied_commit_sha": "$APPLIED_SHA",
  "hardening_ref": "$HARDENING_REF",
  "prior_base_tip_sha": "$PRIOR_SHA" if "$TIP_MATCH" == "0" else "$LIVE_SHA",
  "tip_refresh": bool(int("$TIP_MATCH") == 0),
  "tip_refresh_via": "refresh_path_c_bundle.sh",
  "bundle_refresh": True,
  "git_bundle": True,
  "bundle_file": "path-c-on-hardening.bundle",
  "bundle_branch": "$BRANCH",
  "bundle_range": "${LIVE_SHA}..${APPLIED_SHA}",
  "bundle_requires_ref": "$LIVE_SHA",
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
  "note": f"Batch $BATCH_TAG: refresh_path_c_bundle.sh rebuilt @ ${LIVE_SHORT}; apply_all OK; lemma_closed=false; problems=$PROBLEMS",
  "force": bool(int("$FORCE")),
}
# Preserve land evidence (PR #64 @ 93a4ecd) when tip moves past Path C land.
for key in (
    "path_c_landed",
    "path_c_pr_url",
    "merge_commit_sha",
    "write_vector",
    "path_c_applied_sha",
    "release",
    "release_tag",
):
    if key in verify and verify[key] not in (None, "", False):
        continue
    val = prior.get(key)
    if val not in (None, "", False):
        verify[key] = val
# If prior said Path C landed and this tip is a descendant of that land, keep true.
if prior.get("path_c_landed") is True:
    verify["path_c_landed"] = True
    if not verify.get("path_c_pr_url") and prior.get("path_c_pr_url"):
        verify["path_c_pr_url"] = prior["path_c_pr_url"]
    if not verify.get("merge_commit_sha") and prior.get("merge_commit_sha"):
        verify["merge_commit_sha"] = prior["merge_commit_sha"]
# Default release label when tip-refresh wiped it (Intent living-release contract).
if not verify.get("release"):
    verify["release"] = prior.get("release") or "batch223-path-c-bundle"
Path("$VERIFY_OUT").write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
print("refresh_path_c_bundle: wrote VERIFY.json")
PY

# Keep APPLY.md tip SHA current without rewriting the whole playbook.
if [[ -f "$APPLY_MD" ]]; then
  python3 - <<PY
from pathlib import Path
import re
p = Path("$APPLY_MD")
text = p.read_text(encoding="utf-8")
# Soft-update BASE_TIP / checkout SHA mentions; leave narrative intact.
text2, n = re.subn(
    r"(BASE_TIP\s+[\\\`*]*)([0-9a-f]{7,40})",
    lambda m: m.group(1) + "${LIVE_SHORT}",
    text,
    count=5,
    flags=re.I,
)
# Also refresh the explicit checkout SHA used in Manual section when present.
text2, n2 = re.subn(
    r"(git checkout -B cursor/portable-engineering-patches\s+)([0-9a-f]{40})",
    r"\g<1>${LIVE_SHA}",
    text2,
    count=2,
)
if n or n2:
    p.write_text(text2, encoding="utf-8")
    print(f"refresh_path_c_bundle: soft-updated APPLY.md tip mentions (n={n}+{n2})")
else:
    print("refresh_path_c_bundle: APPLY.md tip mentions unchanged (manual review OK)")
PY
fi

# Soft-update MANIFEST verified_on_tip when present.
MANIFEST="$ROOT/portable/patches/MANIFEST.json"
if [[ -f "$MANIFEST" ]]; then
  python3 - <<PY
import json
from pathlib import Path
from datetime import datetime, timezone
p = Path("$MANIFEST")
data = json.loads(p.read_text(encoding="utf-8"))
data["base_tip_ref"] = "$HARDENING_REF $LIVE_SHA"
data["verified_on_tip"] = "$LIVE_SHA"
data["generated_at_utc"] = "$GENERATED_AT"
data["lemma_closed"] = False
data["scientific_effect"] = "NONE"
data["goal_complete"] = False
data["verified_batch"] = str("$BATCH_TAG")
data["tip_refresh_via"] = "refresh_path_c_bundle.sh"
for item in data.get("patches", []):
    if item.get("in_apply_all"):
        item["verified_on_tip"] = "$LIVE_SHA"
p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("refresh_path_c_bundle: updated MANIFEST.json verified_on_tip")
PY
fi

echo "refresh_path_c_bundle: OK tip=${LIVE_SHORT} applied=${APPLIED_SHORT} patch=$(wc -c <"$PATCH_OUT")B bundle=$(wc -c <"$BUNDLE_OUT")B lemma_closed=false scientific_effect=NONE"
exit 0
