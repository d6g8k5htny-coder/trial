#!/usr/bin/env bash
# Owner Path C PR opener (Batch 151): apply path-c-applied-bundle onto hardening
# BASE_TIP, push branch cursor/path-c-portable-fixes, open/reuse PR into hardening.
#
# Uses owner's gh auth by default, or MAIN_PUSH_TOKEN / GH_TOKEN env (never printed).
# Scientific effect: NONE. lemma_closed stays false. No research promotion.
#
# Usage:
#   ./scripts/owner_open_path_c_pr.sh --dry-run
#   ./scripts/owner_open_path_c_pr.sh --help
#   ./scripts/owner_open_path_c_pr.sh
#   MAIN_PUSH_TOKEN=… ./scripts/owner_open_path_c_pr.sh
#
# Idempotent: if branch/PR already exist with the same tip+patch, reuses them.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
HARDENING_REF="${PATH_C_HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
BRANCH="${PATH_C_PR_BRANCH:-cursor/path-c-portable-fixes}"
WORKDIR="${PATH_C_PR_WORKDIR:-}"
DRY_RUN=0

die() {
  echo "owner_open_path_c_pr: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

# Batch 153: extract a real commit SHA from BASE_TIP.txt (never take $NF / last
# whitespace field — trailing comments or KEY=value spoil awk/##* parses).
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

usage() {
  cat <<'EOF'
Usage: owner_open_path_c_pr.sh [--dry-run] [--help]

  --dry-run   Certainty only: show BASE_TIP (hex-SHA parse), VERIFY cross-check,
              tip-drift vs live hardening, bundle path, merge target, and
              whether gh/MAIN_PUSH_TOKEN auth looks present. No clone/push/PR.
  (default)   Clone/fetch hardening @ BASE_TIP, git am path-c-applied-bundle,
              push branch cursor/path-c-portable-fixes, open/reuse PR into
              hardening (or that branch's default merge target).

Prerequisites: git, python3, gh (owner auth) OR MAIN_PUSH_TOKEN / GH_TOKEN env
with Contents:Write + PullRequests:Write on d6g8k5htny-coder/main.

Env:
  TRIAL_ROOT            Path to trial checkout / extracted release tarball
  MAIN_REPO             Override target repo (default: d6g8k5htny-coder/main)
  PATH_C_HARDENING_REF  Hardening branch (default: chatgpt/drive-github-hardening-20260919)
  PATH_C_PR_BRANCH      Feature branch (default: cursor/path-c-portable-fixes)
  PATH_C_PR_WORKDIR     Existing clone dir to reuse (optional)
  PATH_C_RELEASE_TAG    Prefer this trial release for .bundle link (default: batch218-path-c-bundle)
  TRIAL_REPO            Trial repo slug for release lookup (default: d6g8k5htny-coder/trial)
  MAIN_PUSH_TOKEN / GH_TOKEN — optional; never printed

Scientific effect: NONE. lemma_closed stays false. No research promotion.
Batch 178+: PR body attaches/links path-c-on-hardening.bundle from the latest
matching trial release (download URL + release page). --dry-run prints the link.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

need_cmd git
need_cmd python3

BUNDLE_PATCH="$TRIAL_ROOT/portable/path-c-applied-bundle/path-c-on-hardening.patch"
BUNDLE_GIT="$TRIAL_ROOT/portable/path-c-applied-bundle/path-c-on-hardening.bundle"
BASE_TIP_FILE="$TRIAL_ROOT/portable/patches/BASE_TIP.txt"
APPLY_MD="$TRIAL_ROOT/portable/path-c-applied-bundle/APPLY.md"
VERIFY_JSON="$TRIAL_ROOT/portable/path-c-applied-bundle/VERIFY.json"
# Batch 178+: prefer linking the fetchable .bundle from the latest Path C release in the PR body.
# Batch 199: default release tag batch199-path-c-bundle (supersedes batch180-path-c-bundle / batch179 / batch169).
# Batch 207: default release tag batch218-path-c-bundle (tip b89448d refresh; supersedes batch202-path-c-bundle).
PATH_C_RELEASE_TAG="${PATH_C_RELEASE_TAG:-batch241-path-c-bundle}"
TRIAL_REPO_SLUG="${TRIAL_REPO:-d6g8k5htny-coder/trial}"

resolve_path_c_bundle_release_url() {
  # Prints: TAG<TAB>BROWSER_DOWNLOAD_URL. Never prints tokens.
  local tag="$PATH_C_RELEASE_TAG"
  local asset_name="path-c-on-hardening.bundle"
  local url=""
  local discovered=""
  local cand=""
  if command -v gh >/dev/null 2>&1; then
    if [[ -n "$tag" ]]; then
      url="$(gh api -H 'Accept: application/vnd.github+json' \
        "/repos/${TRIAL_REPO_SLUG}/releases/tags/${tag}" \
        --jq ".assets[] | select(.name==\"${asset_name}\") | .browser_download_url" 2>/dev/null | head -n1 || true)"
    fi
    if [[ -z "$url" ]]; then
      discovered="$(gh release list --repo "$TRIAL_REPO_SLUG" --limit 20 --json tagName \
        --jq '.[].tagName' 2>/dev/null || true)"
      while IFS= read -r cand; do
        [[ -z "$cand" ]] && continue
        url="$(gh api -H 'Accept: application/vnd.github+json' \
          "/repos/${TRIAL_REPO_SLUG}/releases/tags/${cand}" \
          --jq ".assets[] | select(.name==\"${asset_name}\") | .browser_download_url" 2>/dev/null | head -n1 || true)"
        if [[ -n "$url" ]]; then
          tag="$cand"
          break
        fi
      done <<<"$discovered"
    fi
  fi
  if [[ -z "$url" ]]; then
    # Public download URL fallback (works for public releases without auth).
    url="https://github.com/${TRIAL_REPO_SLUG}/releases/download/${tag}/${asset_name}"
  fi
  printf '%s\t%s\n' "$tag" "$url"
}

[[ -f "$BUNDLE_PATCH" ]] || die "missing $BUNDLE_PATCH (need path-c-applied-bundle from batch142-path-c-bundle or newer)"
[[ -f "$BASE_TIP_FILE" ]] || die "missing $BASE_TIP_FILE"

BASE_TIP_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
BASE_TIP_SHA="$(parse_base_tip_sha "$BASE_TIP_LINE")" \
  || die "could not parse BASE_TIP SHA from $BASE_TIP_FILE (need 7–40 hex chars; got: ${BASE_TIP_LINE:0:120})"
# Prefer full 40-char when present; reject obvious garbage (non-hex already filtered).
if [[ ! "$BASE_TIP_SHA" =~ ^[0-9a-f]{7,40}$ ]]; then
  die "BASE_TIP SHA failed hex validation: $BASE_TIP_SHA"
fi

VERIFY_SHA=""
if [[ -f "$VERIFY_JSON" ]]; then
  VERIFY_SHA="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('base_tip_sha') or '')" "$VERIFY_JSON" 2>/dev/null || true)"
fi

# Merge target: hardening ref (Path C apply tree). Default main is ALIGNED landing ≠ BASE_TIP.
PR_BASE="$HARDENING_REF"

RELEASE_RESOLVE="$(resolve_path_c_bundle_release_url)"
RELEASE_TAG="${RELEASE_RESOLVE%%$'\t'*}"
RELEASE_BUNDLE_URL="${RELEASE_RESOLVE#*$'\t'}"
RELEASE_PAGE_URL="https://github.com/${TRIAL_REPO_SLUG}/releases/tag/${RELEASE_TAG}"

echo "=== owner_open_path_c_pr ==="
echo "repo=$REPO trial_root=$TRIAL_ROOT"
echo "mode=$([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo clone+am+push+PR)"
echo "base_tip_file=$BASE_TIP_LINE"
echo "base_tip_sha=$BASE_TIP_SHA"
echo "hardening_ref=$HARDENING_REF"
echo "branch=$BRANCH"
echo "pr_base=$PR_BASE"
echo "bundle_patch=$BUNDLE_PATCH"
[[ -f "$BUNDLE_GIT" ]] && echo "bundle_git=$BUNDLE_GIT"
echo "release_tag=$RELEASE_TAG"
echo "release_bundle_url=$RELEASE_BUNDLE_URL"
echo "release_page_url=$RELEASE_PAGE_URL"
[[ -f "$APPLY_MD" ]] && echo "apply_md=$APPLY_MD"
[[ -f "$VERIFY_JSON" ]] && echo "verify_json=$VERIFY_JSON"
[[ -n "$VERIFY_SHA" ]] && echo "verify_base_tip_sha=$VERIFY_SHA"
echo "scientific_effect=NONE lemma_closed=false no_research_promotion=true"
echo

# Detect auth presence without printing secrets.
AUTH_MODE="none"
if [[ -n "${MAIN_PUSH_TOKEN:-}" || -n "${GH_TOKEN:-}" ]]; then
  AUTH_MODE="env_token"
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  AUTH_MODE="gh_auth"
fi
echo "auth_mode=$AUTH_MODE"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "--- dry-run tip-drift / VERIFY ---"
  if [[ -n "$VERIFY_SHA" && "$VERIFY_SHA" != "$BASE_TIP_SHA" && "$VERIFY_SHA" != "${BASE_TIP_SHA}"* && "$BASE_TIP_SHA" != "${VERIFY_SHA}"* ]]; then
    die "tip-drift: BASE_TIP $BASE_TIP_SHA != VERIFY.json base_tip_sha $VERIFY_SHA — rebuild path-c-applied-bundle"
  fi
  LIVE_SHA=""
  set +e
  LIVE_SHA="$(git ls-remote "https://github.com/${REPO}.git" "refs/heads/${HARDENING_REF}" 2>/dev/null | awk '{print $1}' | head -n1)"
  set -e
  if [[ -n "$LIVE_SHA" ]]; then
    echo "live_hardening_sha=$LIVE_SHA"
    if [[ "$LIVE_SHA" != "$BASE_TIP_SHA" && "$LIVE_SHA" != "${BASE_TIP_SHA}"* && "$BASE_TIP_SHA" != "${LIVE_SHA}"* ]]; then
      die "tip-drift: live hardening $LIVE_SHA != BASE_TIP $BASE_TIP_SHA — refresh BASE_TIP + rebuild path-c-applied-bundle"
    fi
    echo "tip_matches_base=true"
  else
    echo "warn: could not ls-remote live hardening tip (transport); skipping live tip-drift"
  fi
  echo "--- dry-run summary ---"
  echo "would: clone $REPO; checkout $BRANCH from $HARDENING_REF @ $BASE_TIP_SHA"
  echo "would: git am $BUNDLE_PATCH (local patch; PR body also links release .bundle)"
  echo "would: assert math_status lemma_closed=false problems=0"
  echo "would: push origin $BRANCH (idempotent if exists)"
  echo "would: gh pr create --repo $REPO --base $PR_BASE --head $BRANCH (reuse if open)"
  echo "PR body would attach/link: $RELEASE_BUNDLE_URL"
  echo "PR body would link release page: $RELEASE_PAGE_URL"
  echo "PR body would state: engineering-only; lemma_closed stays false; no research promotion"
  if [[ "$AUTH_MODE" == "none" ]]; then
    echo "owner_open_path_c_pr: dry-run OK (auth not required for certainty)."
    echo "Land needs: gh auth login OR MAIN_PUSH_TOKEN env."
  else
    echo "owner_open_path_c_pr: dry-run OK (auth_mode=$AUTH_MODE present)."
  fi
  echo "Scientific effect: NONE"
  exit 0
fi

need_cmd gh

# Prefer MAIN_PUSH_TOKEN / GH_TOKEN for git+gh without printing.
if [[ -n "${MAIN_PUSH_TOKEN:-}" ]]; then
  export GH_TOKEN="$MAIN_PUSH_TOKEN"
elif [[ -n "${GH_TOKEN:-}" ]]; then
  export MAIN_PUSH_TOKEN="$GH_TOKEN"
fi

if ! gh auth status >/dev/null 2>&1; then
  if [[ -z "${GH_TOKEN:-}" ]]; then
    die "gh is not authenticated and MAIN_PUSH_TOKEN/GH_TOKEN unset. Run: gh auth login (owner) or export MAIN_PUSH_TOKEN. Certainty: $0 --dry-run"
  fi
fi

LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-token-env}"

PROBE="$TRIAL_ROOT/scripts/probe_main_write.py"
if [[ -f "$PROBE" ]]; then
  echo "--- write probe (expect writable / exit 0) ---"
  set +e
  python3 "$PROBE"
  probe_ec=$?
  set -e
  if [[ "$probe_ec" -ne 0 ]]; then
    die "write probe exit=$probe_ec (expected 0=writable). Need Contents:Write on $REPO. Certainty: $0 --dry-run"
  fi
fi

if [[ -z "$WORKDIR" ]]; then
  WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/owner-open-path-c-pr.XXXXXX")"
  CLEANUP_WORKDIR=1
else
  CLEANUP_WORKDIR=0
fi
cleanup() {
  if [[ "${CLEANUP_WORKDIR:-0}" -eq 1 && -n "${WORKDIR:-}" && -d "$WORKDIR" ]]; then
    rm -rf "$WORKDIR"
  fi
}
trap cleanup EXIT

echo "workdir=$WORKDIR"
echo "--- clone/fetch $REPO ---"
if [[ -d "$WORKDIR/main/.git" ]]; then
  cd "$WORKDIR/main"
  git fetch origin "$HARDENING_REF" --depth 80
else
  if ! git clone --depth 80 "https://github.com/${REPO}.git" "$WORKDIR/main"; then
    die "git clone failed for $REPO (transport)."
  fi
  cd "$WORKDIR/main"
  git fetch origin "$HARDENING_REF" 2>/dev/null || true
fi

git config user.name "${GIT_AUTHOR_NAME:-owner-open-path-c-pr}"
git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"
gh auth setup-git 2>/dev/null || true

# Prefer exact BASE_TIP SHA when present; else hardening tip.
if git cat-file -e "${BASE_TIP_SHA}^{commit}" 2>/dev/null; then
  TIP_REF="$BASE_TIP_SHA"
else
  echo "warn: BASE_TIP $BASE_TIP_SHA not in shallow clone; fetching explicitly"
  git fetch --depth 80 origin "$BASE_TIP_SHA" 2>/dev/null || git fetch origin "$HARDENING_REF"
  if git cat-file -e "${BASE_TIP_SHA}^{commit}" 2>/dev/null; then
    TIP_REF="$BASE_TIP_SHA"
  else
    TIP_REF="origin/${HARDENING_REF}"
    echo "warn: falling back to $TIP_REF (may am-fail if tip moved past BASE_TIP)"
  fi
fi

echo "--- checkout $BRANCH from $TIP_REF ---"
# Idempotent: reuse remote branch tip if it already contains our patch tip.
REMOTE_EXISTS=0
if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
  REMOTE_EXISTS=1
  echo "remote branch $BRANCH exists (will update idempotently)"
fi

git checkout -B "$BRANCH" "$TIP_REF"
echo "tip=$(git rev-parse HEAD)"

# Fail closed: hardening-shaped tree required.
if [[ ! -f docs/math_status/PACKET.json || ! -f tools/carriers_verify.py ]]; then
  die "checkout lacks PACKET.json / carriers_verify.py — wrong base (do not use post-#41 default main)."
fi

ALREADY_PATCHED=0
if grep -q '__pycache__' tools/carriers_verify.py 2>/dev/null \
   && grep -q 'ResourceWarning\|read_bytes\|close-file' tests/test_inventable_jetmod_probes.py 2>/dev/null; then
  ALREADY_PATCHED=1
fi

if [[ "$ALREADY_PATCHED" -eq 1 ]]; then
  echo "Tree already looks Path-C patched; skipping git am (idempotent)."
else
  echo "--- git am path-c-applied-bundle ---"
  if ! git am --3way "$BUNDLE_PATCH"; then
    git am --abort 2>/dev/null || true
    die "git am failed. Tip may have moved past BASE_TIP; refresh path-c-applied-bundle / BASE_TIP."
  fi
fi

echo
echo "--- math_status_check (assert lemma_closed=false) ---"
STATUS_OUT="$(python3 tools/math_status_check.py 2>&1)" || die "math_status_check failed"
echo "$STATUS_OUT"
if ! echo "$STATUS_OUT" | grep -q 'lemma_closed=false'; then
  die "lemma_closed is not false after Path C patches. Aborting (no status promotion)."
fi
if ! echo "$STATUS_OUT" | grep -q 'problems=0'; then
  die "math_status_check problems!=0 after Path C patches."
fi

FOCUSED=(
  tests/test_carriers.py
  tests/test_math_status.py
  tests/test_inventable_jetmod_probes.py
  tests/test_gaussian_moments.py
  tests/test_inventable_jetmod_instrumentation_status.py
)
echo
echo "--- focused pytest ---"
if ! python3 -m pytest -q "${FOCUSED[@]}"; then
  die "focused pytest failed after git am."
fi

# Commit only if am left uncommitted state (normally am creates commits).
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  git commit -m "fix: path-c-applied-bundle on hardening (Path C PR)

Engineering hygiene only via path-c-on-hardening.patch.
Scientific effect: NONE. lemma_closed stays false. No research promotion."
fi

echo
echo "--- push branch $BRANCH ---"
if git push -u origin "HEAD:refs/heads/${BRANCH}"; then
  echo "Pushed $BRANCH."
elif [[ "$REMOTE_EXISTS" -eq 1 ]] && git push -u --force-with-lease origin "HEAD:refs/heads/${BRANCH}"; then
  echo "Updated $BRANCH with --force-with-lease (idempotent refresh)."
else
  die "git push denied for $BRANCH. Confirm Contents:Write on $REPO."
fi

TITLE="fix: path-c portable fixes on hardening (Path C)"
BODY="$(cat <<EOF
Path C via \`scripts/owner_open_path_c_pr.sh\` (Batch 151; Batch 178 release-bundle link).

Applies trial \`portable/path-c-applied-bundle/path-c-on-hardening.patch\` (\`git am\`) onto \`${HARDENING_REF}\` @ BASE_TIP \`${BASE_TIP_SHA:0:7}\`.

**Release artifact (fetchable git bundle):**
- Tag: [\`${RELEASE_TAG}\`](${RELEASE_PAGE_URL})
- Download: [\`path-c-on-hardening.bundle\`](${RELEASE_BUNDLE_URL})
- Local land without PAT wait: \`./scripts/owner_path_c_oneshot.sh --from-bundle\` (prefers \`.bundle\` fetch+merge)

**Engineering only.** Scientific effect: **NONE**.
- \`lemma_closed\` stays **false**
- **No research promotion** (premises / lemmas / prizes / packet obligations untouched)
- Green checks ≠ obligation discharge

Do **not** merge onto post-ALIGNED default \`main\` solely for Path C (no \`PACKET.json\` there). Merge target is hardening.

Verify:
\`\`\`bash
python3 tools/math_status_check.py   # lemma_closed=false problems=0
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \\
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \\
  tests/test_inventable_jetmod_instrumentation_status.py
\`\`\`
EOF
)"

echo
echo "--- open or reuse PR into $PR_BASE ---"
EXISTING="$(gh pr list --repo "$REPO" --head "$BRANCH" --base "$PR_BASE" --state open --json number,url --jq '.[0].url // empty' || true)"
if [[ -n "$EXISTING" ]]; then
  PR_URL="$EXISTING"
  echo "Reusing open PR: $PR_URL"
else
  # Also accept an open PR with this head regardless of base (idempotent).
  EXISTING_ANY="$(gh pr list --repo "$REPO" --head "$BRANCH" --state open --json number,url,baseRefName --jq '.[0].url // empty' || true)"
  if [[ -n "$EXISTING_ANY" ]]; then
    PR_URL="$EXISTING_ANY"
    echo "Reusing open PR (head match): $PR_URL"
  else
    if ! PR_URL="$(gh pr create --repo "$REPO" --base "$PR_BASE" --head "$BRANCH" --title "$TITLE" --body "$BODY")"; then
      die "gh pr create failed (need PullRequests:Write). Branch pushed: $BRANCH — open manually: https://github.com/${REPO}/compare/${PR_BASE}...${BRANCH}"
    fi
    echo "Opened Path C PR: $PR_URL"
  fi
fi

echo
echo "=== NEXT (owner) ==="
echo "1. Review and merge: $PR_URL"
echo "2. Confirm lemma_closed=false on the merged tip (no research promotion)"
echo
echo "owner_open_path_c_pr: branch+PR ready."
echo "Scientific effect: NONE"
exit 0
