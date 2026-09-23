#!/usr/bin/env bash
# Owner Path C land: apply portable engineering patches (0001–0004 + 0008–0016) onto the
# working tip of d6g8k5htny-coder/main, then push a branch / open a PR.
#
# Prerequisites:
#   - Path A (PR #2) is MERGED @ b040bf0c — default tip ALIGNED.
#   - Apply target is still chatgpt/drive-github-hardening-20260919 (BASE_TIP).
#     Post-#2 default main is a *different tree* (no docs/math_status/PACKET.json);
#     do NOT point PATH_C_BASE=main unless that tip already carries the hardening
#     research tooling layout and `apply_all --check` passes.
#   - After Path A: optionally rebase hardening onto new main first
#     (PATH_C_REBASE_ONTO_MAIN=1), then apply patches on the rebased tip.
#
# Default (safer): clone hardening tip, apply_all, push branch, open PR.
# Opt-in: --direct-push pushes the patched tip branch straight (no PR).
#
# Intended to run on the owner's machine / Codespace with *owner* gh/git auth
# that has write on d6g8k5htny-coder/main. This trial cloud token cannot (403).
#
# Scientific effect: NONE. Engineering hygiene only; lemma_closed must stay false.
# Fail-closed: clear errors on missing patches, apply failure, write denial,
# lemma_closed!=false, or pytest failure.
#
# Usage:
#   ./scripts/owner_land_path_c.sh
#   ./scripts/owner_land_path_c.sh --direct-push
#   TRIAL_ROOT=/path/to/trial ./scripts/owner_land_path_c.sh
#   PATH_C_REBASE_ONTO_MAIN=1 ./scripts/owner_land_path_c.sh
#   PATH_C_BASE=main ./scripts/owner_land_path_c.sh   # only if main tip is hardening-shaped
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
HARDENING_REF="${PATH_C_HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
BRANCH="${PATH_C_BRANCH:-cursor/portable-engineering-patches}"
WORKDIR="${PATH_C_WORKDIR:-}"
DIRECT_PUSH=0
# PATH_C_BASE: auto | hardening | main
# auto (post-#2): always prefer hardening — default main lacks PACKET.json / patch shape.
BASE_MODE="${PATH_C_BASE:-auto}"
REBASE_ONTO_MAIN="${PATH_C_REBASE_ONTO_MAIN:-0}"

die() {
  echo "owner_land_path_c: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

usage() {
  cat <<'EOF'
Usage: owner_land_path_c.sh [--direct-push] [--help]

  (default)     Clone tip, apply_all 0001–0004 + 0008–0016, push branch, open PR.
  --direct-push Opt-in: push patched commits to PATH_C_BRANCH without opening a PR.

Env:
  TRIAL_ROOT            Path to trial checkout (default: repo containing this script)
  MAIN_REPO             Override target repo (default: d6g8k5htny-coder/main)
  PATH_C_BASE           auto|hardening|main (default: auto → hardening after Path A)
                        auto never picks post-#2 default main solely because it is
                        ALIGNED — that tip is a different tree from BASE_TIP.
  PATH_C_REBASE_ONTO_MAIN  1 → rebase hardening onto origin/main before apply_all
  PATH_C_HARDENING_REF  Hardening branch (default: chatgpt/drive-github-hardening-20260919)
  PATH_C_BRANCH         Feature branch name (default: cursor/portable-engineering-patches)
  PATH_C_WORKDIR        Existing clone dir to reuse (optional)
  MAIN_PUSH_TOKEN / GH_TOKEN — optional; gh/git use owner auth by default
EOF
}

for arg in "$@"; do
  case "$arg" in
    --direct-push) DIRECT_PUSH=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

need_cmd gh
need_cmd git
need_cmd python3

APPLY_ALL="$TRIAL_ROOT/portable/patches/apply_all.sh"
PROBE="$TRIAL_ROOT/scripts/probe_main_write.py"
BASE_TIP_FILE="$TRIAL_ROOT/portable/patches/BASE_TIP.txt"
[[ -f "$APPLY_ALL" ]] || die "missing $APPLY_ALL (set TRIAL_ROOT to the trial checkout)"
[[ -x "$APPLY_ALL" ]] || chmod +x "$APPLY_ALL" || true

echo "=== owner_land_path_c ==="
echo "repo=$REPO trial_root=$TRIAL_ROOT"
echo "mode=$([ "$DIRECT_PUSH" -eq 1 ] && echo direct-push || echo branch+PR)"
echo "base_mode=$BASE_MODE rebase_onto_main=$REBASE_ONTO_MAIN"
if [[ -f "$BASE_TIP_FILE" ]]; then
  echo "base_tip_file=$(cat "$BASE_TIP_FILE")"
fi
echo "scientific_effect=NONE"
echo

if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated. Run: gh auth login  (owner account with write on $REPO)"
fi
LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-unknown}"

# Fail closed early if this credential cannot write.
if [[ -f "$PROBE" ]]; then
  echo "--- write probe (expect writable / exit 0) ---"
  set +e
  python3 "$PROBE"
  probe_ec=$?
  set -e
  if [[ "$probe_ec" -ne 0 ]]; then
    die "write probe exit=$probe_ec (expected 0=writable). Path C requires Contents:Write on $REPO. Trial cloud tokens get 403 — re-run with owner auth or MAIN_PUSH_TOKEN."
  fi
else
  echo "warn: missing $PROBE; will fail closed on git push if denied."
fi

if [[ -z "$WORKDIR" ]]; then
  WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/owner-path-c.XXXXXX")"
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
echo "--- clone $REPO ---"
if ! git clone --depth 80 "https://github.com/${REPO}.git" "$WORKDIR/main"; then
  die "git clone failed for $REPO (transport). Check network / credentials."
fi
cd "$WORKDIR/main"
git config user.name "${GIT_AUTHOR_NAME:-owner-land-path-c}"
git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"
gh auth setup-git 2>/dev/null || true

git fetch origin "$HARDENING_REF" 2>/dev/null || true
git fetch origin main 2>/dev/null || true

DEFAULT_TIP="$(git rev-parse origin/main 2>/dev/null || git rev-parse HEAD)"
echo "default_tip=$DEFAULT_TIP"

tree_accepts_path_c() {
  # Hardening-shaped tree required by apply_all root guard + patch hunks.
  local tip_ref="$1"
  git cat-file -e "${tip_ref}:docs/math_status/PACKET.json" 2>/dev/null \
    && git cat-file -e "${tip_ref}:tools/carriers_verify.py" 2>/dev/null \
    && git cat-file -e "${tip_ref}:tools/math_status_check.py" 2>/dev/null
}

resolve_base() {
  case "$BASE_MODE" in
    hardening)
      echo "$HARDENING_REF"
      ;;
    main)
      if ! tree_accepts_path_c "origin/main"; then
        die "PATH_C_BASE=main but origin/main lacks hardening Path-C shape (need docs/math_status/PACKET.json + tools). After PR #2, default main is ALIGNED but a different tree — use PATH_C_BASE=hardening (default) and optionally PATH_C_REBASE_ONTO_MAIN=1."
      fi
      echo "main"
      ;;
    auto)
      # Post-#2: default tip is ALIGNED (q0) but NOT the portable-patch apply target.
      # Prefer hardening unless main already has the hardening tooling layout.
      if tree_accepts_path_c "origin/${HARDENING_REF}"; then
        echo "$HARDENING_REF"
      elif tree_accepts_path_c "origin/main"; then
        echo "main"
      else
        die "neither origin/${HARDENING_REF} nor origin/main looks Path-C-ready (missing PACKET.json / tools)."
      fi
      ;;
    *)
      die "PATH_C_BASE must be auto|hardening|main (got: $BASE_MODE)"
      ;;
  esac
}

BASE_REF="$(resolve_base)"
echo "resolved_base=$BASE_REF"

echo "--- checkout feature branch $BRANCH from origin/$BASE_REF ---"
if ! git checkout -B "$BRANCH" "origin/${BASE_REF}"; then
  die "cannot checkout origin/${BASE_REF}."
fi

echo "tip=$(git rev-parse HEAD)"

if [[ "$REBASE_ONTO_MAIN" == "1" ]]; then
  if [[ "$BASE_REF" == "main" ]]; then
    echo "PATH_C_REBASE_ONTO_MAIN=1 ignored (already on main)."
  else
    echo "--- PATH_C_REBASE_ONTO_MAIN=1: rebase $BASE_REF onto origin/main ---"
    if ! git rebase "origin/main"; then
      git rebase --abort 2>/dev/null || true
      die "rebase onto origin/main failed. Resolve conflicts on hardening locally, push the rebased tip, refresh BASE_TIP, then re-run Path C."
    fi
    echo "rebased_tip=$(git rev-parse HEAD)"
  fi
fi

# Fail closed before apply if tree lost Path-C shape after rebase.
if [[ ! -f docs/math_status/PACKET.json || ! -f tools/carriers_verify.py ]]; then
  die "checkout lacks docs/math_status/PACKET.json or tools/carriers_verify.py — wrong base for apply_all (post-#2 default main is not BASE_TIP)."
fi

# Idempotent: skip apply if patches already present (heuristic: carriers pycache ignore).
if grep -q '__pycache__' tools/carriers_verify.py 2>/dev/null \
   && grep -q 'ResourceWarning\|read_bytes\|close-file' tests/test_inventable_jetmod_probes.py 2>/dev/null; then
  echo "Tree already looks patched; running apply_all --check only."
  if ! "$APPLY_ALL" --check; then
    die "apply_all --check failed on apparently-patched tree. Resolve conflicts or reset to a clean tip."
  fi
else
  echo "--- apply_all 0001–0004 + 0008–0016 ---"
  if ! "$APPLY_ALL"; then
    die "apply_all failed. Tip may have moved past BASE_TIP; refresh portable/patches or rebase hardening onto post-#2 main first (PATH_C_REBASE_ONTO_MAIN=1)."
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
  die "focused pytest failed after apply_all."
fi

if git diff --quiet && git diff --cached --quiet; then
  echo "No uncommitted patch diffs (already applied upstream?)."
else
  git add -A
  git commit -m "fix: portable engineering patches 0001-0004+0008-0016 (Path C)

carriers pycache ignore, math_console paths, gaussian parametrize,
git fixture timeout, close-file-handles through receipts/bridge tests.

Scientific effect: NONE. lemma_closed stays false."
fi

echo
if [[ "$DIRECT_PUSH" -eq 1 ]]; then
  echo "--- --direct-push: push $BRANCH ---"
  if ! git push -u origin "HEAD:refs/heads/${BRANCH}"; then
    die "git push denied for $BRANCH. Confirm Contents:Write on $REPO (trial cloud tokens get 403)."
  fi
  echo "Pushed $BRANCH (no PR opened)."
  echo "owner_land_path_c: OK — patches on $BRANCH."
  echo "Scientific effect: NONE"
  exit 0
fi

echo "--- push branch $BRANCH ---"
if ! git push -u origin "HEAD:refs/heads/${BRANCH}"; then
  if ! git push -u --force origin "HEAD:refs/heads/${BRANCH}"; then
    die "git push denied for branch $BRANCH. Confirm Contents:Write on $REPO (expected 403 without owner auth)."
  fi
  echo "Pushed $BRANCH with --force (non-ff)."
fi
echo "Pushed branch $BRANCH."

# PR base: prefer the same base we branched from (hardening tip after optional rebase).
PR_BASE="$BASE_REF"
if [[ "$PR_BASE" != "main" ]]; then
  PR_BASE="$HARDENING_REF"
else
  PR_BASE="main"
fi

TITLE="fix: portable engineering patches 0001-0004+0008-0016 (Path C)"
BODY="$(cat <<EOF
Path C via \`scripts/owner_land_path_c.sh\`.

Applies trial \`portable/patches/apply_all.sh\` (**0001–0004 + 0008–0016**) onto \`${BASE_REF}\`$( [[ "$REBASE_ONTO_MAIN" == "1" ]] && echo " (rebased onto main first)" ).

Scientific effect: **NONE**. \`lemma_closed\` stays false. Green checks ≠ obligation discharge.

After Path A (PR #2) @ \`b040bf0c\`: default tip is ALIGNED but a different tree — keep Path C on hardening (BASE_TIP) unless that tip has been rebased/merged onto main.

Verify:
\`\`\`bash
python3 tools/math_status_check.py   # lemma_closed=false
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
  if ! PR_URL="$(gh pr create --repo "$REPO" --base "$PR_BASE" --head "$BRANCH" --title "$TITLE" --body "$BODY")"; then
    die "gh pr create failed (need PullRequests:Write). Branch is pushed: $BRANCH — open manually: https://github.com/${REPO}/compare/${PR_BASE}...${BRANCH}"
  fi
  echo "Opened Path C PR: $PR_URL"
fi

echo
echo "=== NEXT (owner) ==="
echo "1. Review and merge: $PR_URL"
echo "2. Confirm lemma_closed=false on the merged tip"
echo
echo "owner_land_path_c: branch+PR ready."
echo "Scientific effect: NONE"
exit 0
