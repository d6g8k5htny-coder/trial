#!/usr/bin/env bash
# Owner Path C land: apply portable engineering patches (0001–0009) onto the
# working tip of d6g8k5htny-coder/main, then push a branch / open a PR.
#
# Prerequisites:
#   - Path A (PR #2) ideally already merged so default main is ALIGNED, OR
#     you are landing onto chatgpt/drive-github-hardening-20260919 while #2
#     is still open (patches still apply; default tip alignment is separate).
#   - After Path A merges: rebase hardening onto new main first, then run this
#     (or set PATH_C_BASE=main if the port is already on default main).
#
# Default (safer): clone base tip, apply_all, push branch, open PR.
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
#   PATH_C_BASE=main ./scripts/owner_land_path_c.sh   # post-#2 default tip
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
HARDENING_REF="${PATH_C_HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
BRANCH="${PATH_C_BRANCH:-cursor/portable-engineering-patches}"
WORKDIR="${PATH_C_WORKDIR:-}"
DIRECT_PUSH=0
# PATH_C_BASE: auto | hardening | main
BASE_MODE="${PATH_C_BASE:-auto}"

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

  (default)     Clone tip, apply_all 0001–0009, push branch, open PR.
  --direct-push Opt-in: push patched commits to PATH_C_BRANCH without opening a PR.

Env:
  TRIAL_ROOT            Path to trial checkout (default: repo containing this script)
  MAIN_REPO             Override target repo (default: d6g8k5htny-coder/main)
  PATH_C_BASE           auto|hardening|main (default: auto)
                        auto → main if default tip looks post-Path-A / q0; else hardening
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
[[ -f "$APPLY_ALL" ]] || die "missing $APPLY_ALL (set TRIAL_ROOT to the trial checkout)"
[[ -x "$APPLY_ALL" ]] || chmod +x "$APPLY_ALL" || true

echo "=== owner_land_path_c ==="
echo "repo=$REPO trial_root=$TRIAL_ROOT"
echo "mode=$([ "$DIRECT_PUSH" -eq 1 ] && echo direct-push || echo branch+PR)"
echo "base_mode=$BASE_MODE"
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

looks_post_path_a() {
  # q0 / notice face on default main (Path A or Option-B).
  local tree="$1"
  if [[ ! -f "$tree/README.md" ]]; then
    return 1
  fi
  if grep -qE 'q0|option-b|drive-github-hardening|quarantine/pre-q0' "$tree/README.md" 2>/dev/null \
     && ! grep -q 'Multiscale Retrodiction Complexity' "$tree/README.md" 2>/dev/null; then
    return 0
  fi
  # Full Path A port usually brings tools/ + AGENTS.md.
  if [[ -f "$tree/AGENTS.md" && -f "$tree/tools/math_status_check.py" ]]; then
    return 0
  fi
  return 1
}

resolve_base() {
  case "$BASE_MODE" in
    hardening)
      echo "$HARDENING_REF"
      ;;
    main)
      echo "main"
      ;;
    auto)
      # Prefer hardening tip for apply_all (BASE_TIP); after Path A, owner should
      # rebase hardening onto new main then still land patches on that tip.
      # If default main already has the research tree (post-#2 port), use main.
      git show "origin/main:README.md" >/tmp/path_c_main_readme.md 2>/dev/null || true
      if [[ -f /tmp/path_c_main_readme.md ]] \
         && grep -qE 'q0 Research Program|drive-github-hardening|quarantine/pre-q0' /tmp/path_c_main_readme.md 2>/dev/null \
         && ! grep -q 'Multiscale Retrodiction Complexity' /tmp/path_c_main_readme.md 2>/dev/null \
         && git cat-file -e "origin/main:tools/math_status_check.py" 2>/dev/null; then
        echo "main"
      else
        echo "$HARDENING_REF"
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
  die "cannot checkout origin/${BASE_REF}. After PR #2 merges, rebase hardening onto new main first, then re-run (or PATH_C_BASE=main if already ported)."
fi

echo "tip=$(git rev-parse HEAD)"

# Idempotent: skip apply if patches already present (heuristic: carriers pycache ignore).
if grep -q '__pycache__' tools/carriers_verify.py 2>/dev/null \
   && grep -q 'ResourceWarning\|read_bytes\|close-file' tests/test_inventable_jetmod_probes.py 2>/dev/null; then
  echo "Tree already looks patched; running apply_all --check only."
  if ! "$APPLY_ALL" --check; then
    die "apply_all --check failed on apparently-patched tree. Resolve conflicts or reset to a clean tip."
  fi
else
  echo "--- apply_all 0001–0009 ---"
  if ! "$APPLY_ALL"; then
    die "apply_all failed. Tip may have moved past BASE_TIP; refresh portable/patches or rebase hardening onto post-#2 main first."
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
  git commit -m "fix: portable engineering patches 0001-0009 (Path C)

carriers pycache ignore, math_console paths, gaussian parametrize,
git fixture timeout, inventable/instrumentation receipt restores,
close-file-handles (inventable + carriers/math_status).

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

# PR base: prefer the same base we branched from.
PR_BASE="$BASE_REF"
if [[ "$PR_BASE" == "$HARDENING_REF" ]]; then
  PR_BASE="$HARDENING_REF"
else
  PR_BASE="main"
fi

TITLE="fix: portable engineering patches 0001-0009 (Path C)"
BODY="$(cat <<EOF
Path C via \`scripts/owner_land_path_c.sh\`.

Applies trial \`portable/patches/apply_all.sh\` (**0001–0009**) onto \`${BASE_REF}\`.

Scientific effect: **NONE**. \`lemma_closed\` stays false. Green checks ≠ obligation discharge.

After Path A (PR #2) merges: rebase hardening onto new main, then re-apply / land this branch.

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
