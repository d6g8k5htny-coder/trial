#!/usr/bin/env bash
# Owner Path C land: apply portable engineering patches (0001–0004 + 0008–0016) onto the
# working tip of d6g8k5htny-coder/main, then push a branch / open a PR.
#
# === ONE-SHOT from release tarball (Batch 137; preferred for Dylan) ===
# Prerequisites (local machine / Codespace — NOT the trial Cloud Agent token):
#   1. git, python3, gh  (gh auth login with Contents:Write + PullRequests:Write on main)
#   2. Download latest Path C release on trial (batch169-path-c-bundle or newer):
#        gh release download batch169-path-c-bundle -R d6g8k5htny-coder/trial \
#          -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle'
#   3. Extract and land in ONE command:
#        mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
#        /tmp/path-c-land/scripts/owner_land_path_c.sh
#      Faster (pre-verified; same gates): add --from-bundle
#        /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
#      Batch 169+: --from-bundle prefers path-c-on-hardening.bundle (git fetch+merge)
#      when present; falls back to path-c-on-hardening.patch (git am).
# Cloud Agent mid-flight cannot gain main write — see portable/RELAUNCH_WITH_MAIN_SCOPE.md.
#
# Prerequisites (tree shape):
#   - Default tip may already be ALIGNED (owner PR #41 @ 1c6e74b, or historical PR #2).
#   - Apply target is still chatgpt/drive-github-hardening-20260919 (BASE_TIP).
#     Post-ALIGNED default main is a *different tree* (no docs/math_status/PACKET.json;
#     post-#41 relocates body under history/; tools/ are landing stubs).
#     do NOT point PATH_C_BASE=main unless that tip already carries the hardening
#     research tooling layout and `apply_all --check` passes.
#   - PATH_C_REBASE_ONTO_MAIN=1 is usually NOT advised after PR #41 (rebase CONFLICTS
#     on ci.yml / research.yml / bridge). Prefer land on hardening; merge later.
#   - Certainty without write: --dry-run → scripts/path_c_dry_run.py
#
# Default (safer): clone hardening tip, apply_all, push branch, open PR.
# Opt-in: --from-bundle uses portable/path-c-applied-bundle:
#   prefer path-c-on-hardening.bundle (git fetch + ff-merge) when present (Batch 169+);
#   else path-c-on-hardening.patch (git am).
# Opt-in: --direct-push pushes the patched tip branch straight (no PR).
#
# Intended to run on the owner's machine / Codespace with *owner* gh/git auth
# that has write on d6g8k5htny-coder/main. This trial cloud token cannot (403).
#
# Actions equivalent (trial secret MAIN_PUSH_TOKEN):
#   .github/workflows/land-path-c-on-main.yml
#   gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=true
#   gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false
# Default dry_run=true. Same gates: apply_all + lemma_closed=false + problems=0.
#
# Scientific effect: NONE. Engineering hygiene only; lemma_closed must stay false.
# Fail-closed: clear errors on missing patches, apply failure, write denial,
# lemma_closed!=false, or pytest failure.
#
# Usage:
#   ./scripts/owner_land_path_c.sh --dry-run
#   ./scripts/owner_land_path_c.sh
#   ./scripts/owner_land_path_c.sh --from-bundle
#   ./scripts/owner_land_path_c.sh --direct-push
#   TRIAL_ROOT=/path/to/trial ./scripts/owner_land_path_c.sh
#   PATH_C_REBASE_ONTO_MAIN=1 ./scripts/owner_land_path_c.sh   # usually conflicts post-#41
#   PATH_C_BASE=main ./scripts/owner_land_path_c.sh   # only if main tip is hardening-shaped
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
REPO="${MAIN_REPO:-d6g8k5htny-coder/main}"
HARDENING_REF="${PATH_C_HARDENING_REF:-chatgpt/drive-github-hardening-20260919}"
BRANCH="${PATH_C_BRANCH:-cursor/portable-engineering-patches}"
WORKDIR="${PATH_C_WORKDIR:-}"
DIRECT_PUSH=0
DRY_RUN=0
FROM_BUNDLE=0
# PATH_C_BASE: auto | hardening | main
# auto (post-ALIGNED): always prefer hardening — default main lacks PACKET.json / patch shape.
BASE_MODE="${PATH_C_BASE:-auto}"
REBASE_ONTO_MAIN="${PATH_C_REBASE_ONTO_MAIN:-0}"

die() {
  echo "owner_land_path_c: ERROR: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

# Batch 153: extract a real commit SHA from BASE_TIP.txt (hex, not $NF / last field).
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
Usage: owner_land_path_c.sh [--dry-run] [--from-bundle] [--direct-push] [--help]

  --dry-run     Certainty only: path_c_dry_run.py (apply_all --check + tip shape; no push).
                With --from-bundle: tip-drift + local git am of path-c-applied-bundle
                (no push); exit 0/1/2.
                Exit codes match path_c_dry_run: 0=ready, 1=not ready, 2=transport.
  (default)     Clone tip, apply_all 0001–0004 + 0008–0016, push branch, open PR.
  --from-bundle Prefer portable/path-c-applied-bundle/path-c-on-hardening.bundle
                (git fetch + ff-merge) when present; else .patch via git am.
                Preferred one-shot after extracting the release tarball
                (batch169-path-c-bundle or newer; prior batch142-path-c-bundle / batch142+ had patch-only).
  --direct-push Opt-in: push patched commits to PATH_C_BRANCH without opening a PR.

ONE-SHOT from release tarball (owner machine with write on main):
  gh release download batch169-path-c-bundle -R d6g8k5htny-coder/trial \
    -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle'
  mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
  /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle

Prerequisites: git, python3, gh (authenticated with Contents:Write + PullRequests:Write
on d6g8k5htny-coder/main). Trial Cloud Agent tokens get 403 — see
portable/RELAUNCH_WITH_MAIN_SCOPE.md.

Env:
  TRIAL_ROOT            Path to trial checkout (default: repo containing this script)
  MAIN_REPO             Override target repo (default: d6g8k5htny-coder/main)
  PATH_C_BASE           auto|hardening|main (default: auto → hardening after ALIGNED)
                        auto never picks post-ALIGNED default main solely because it is
                        ALIGNED — that tip is a different tree from BASE_TIP (PR #41 /
                        post-#2 both lack PACKET.json).
  PATH_C_REBASE_ONTO_MAIN  1 → rebase hardening onto origin/main before apply_all
                        (usually CONFLICTS after PR #41; path_c_dry_run reports state)
  PATH_C_HARDENING_REF  Hardening branch (default: chatgpt/drive-github-hardening-20260919)
  PATH_C_BRANCH         Feature branch name (default: cursor/portable-engineering-patches)
  PATH_C_WORKDIR        Existing clone dir to reuse (optional)
  MAIN_PUSH_TOKEN / GH_TOKEN — optional; gh/git use owner auth by default

Actions (trial):
  .github/workflows/land-path-c-on-main.yml  # workflow_dispatch; dry_run default true
  gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=true
  # dry_run=false needs MAIN_PUSH_TOKEN secret on trial
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --from-bundle) FROM_BUNDLE=1 ;;
    --direct-push) DIRECT_PUSH=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $arg (see --help)" ;;
  esac
done

need_cmd git
need_cmd python3

APPLY_ALL="$TRIAL_ROOT/portable/patches/apply_all.sh"
BUNDLE_DIR="$TRIAL_ROOT/portable/path-c-applied-bundle"
BUNDLE_GIT="$BUNDLE_DIR/path-c-on-hardening.bundle"
BUNDLE_PATCH="$BUNDLE_DIR/path-c-on-hardening.patch"
BUNDLE_BRANCH="${PATH_C_BUNDLE_BRANCH:-cursor/portable-engineering-patches}"
PROBE="$TRIAL_ROOT/scripts/probe_main_write.py"
DRY_RUN_PY="$TRIAL_ROOT/scripts/path_c_dry_run.py"
BASE_TIP_FILE="$TRIAL_ROOT/portable/patches/BASE_TIP.txt"
[[ -f "$APPLY_ALL" ]] || die "missing $APPLY_ALL (set TRIAL_ROOT to the trial checkout / extracted release tarball)"
[[ -x "$APPLY_ALL" ]] || chmod +x "$APPLY_ALL" || true
# Batch 169: prefer .bundle when present; else require .patch.
USE_GIT_BUNDLE=0
if [[ "$FROM_BUNDLE" -eq 1 ]]; then
  if [[ -f "$BUNDLE_GIT" ]]; then
    USE_GIT_BUNDLE=1
  elif [[ -f "$BUNDLE_PATCH" ]]; then
    USE_GIT_BUNDLE=0
  else
    die "missing $BUNDLE_GIT and $BUNDLE_PATCH (need path-c-applied-bundle from batch169-path-c-bundle or newer)"
  fi
fi

# Apply Path C commits from release artifacts onto current HEAD (must be BASE_TIP).
# Prefers git bundle fetch+ff-merge; falls back to git am of the format-patch.
apply_from_bundle_artifact() {
  if [[ "$USE_GIT_BUNDLE" -eq 1 ]]; then
    echo "--- --from-bundle: git fetch $BUNDLE_GIT $BUNDLE_BRANCH (prefer .bundle) ---"
    if ! git fetch "$BUNDLE_GIT" "$BUNDLE_BRANCH"; then
      die "git fetch from $BUNDLE_GIT failed (need BASE_TIP present in this clone)."
    fi
    if ! git merge --ff-only FETCH_HEAD; then
      die "git merge --ff-only from bundle failed (HEAD must be BASE_TIP; tip may have moved)."
    fi
    return 0
  fi
  echo "--- --from-bundle: git am path-c-on-hardening.patch (no .bundle) ---"
  if ! git am --3way "$BUNDLE_PATCH"; then
    git am --abort 2>/dev/null || true
    die "git am --from-bundle failed. Tip may have moved past BASE_TIP; refresh release bundle or use $0 (apply_all) instead."
  fi
}

echo "=== owner_land_path_c ==="
echo "repo=$REPO trial_root=$TRIAL_ROOT"
if [[ "$DRY_RUN" -eq 1 && "$FROM_BUNDLE" -eq 1 ]]; then
  echo "mode=from-bundle+dry-run"
elif [[ "$DRY_RUN" -eq 1 ]]; then
  echo "mode=dry-run"
elif [[ "$FROM_BUNDLE" -eq 1 ]]; then
  echo "mode=from-bundle+$([ "$DIRECT_PUSH" -eq 1 ] && echo direct-push || echo branch+PR)"
else
  echo "mode=$([ "$DIRECT_PUSH" -eq 1 ] && echo direct-push || echo branch+PR)"
fi
echo "base_mode=$BASE_MODE rebase_onto_main=$REBASE_ONTO_MAIN from_bundle=$FROM_BUNDLE use_git_bundle=$USE_GIT_BUNDLE"
BASE_TIP_LINE=""
BASE_TIP_SHA=""
if [[ -f "$BASE_TIP_FILE" ]]; then
  BASE_TIP_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
  echo "base_tip_file=$BASE_TIP_LINE"
  if BASE_TIP_SHA="$(parse_base_tip_sha "$BASE_TIP_LINE")"; then
    echo "base_tip_sha=$BASE_TIP_SHA"
  else
    echo "warn: could not parse BASE_TIP SHA from $BASE_TIP_FILE"
  fi
fi
echo "prerequisites: git+python3+gh auth with Contents:Write on $REPO"
echo "cloud_agent_midflight_cannot_gain_main_write: see portable/RELAUNCH_WITH_MAIN_SCOPE.md"
echo "scientific_effect=NONE"
echo

# --dry-run: certainty only (no write probe, no push). Works with trial 403 tokens.
# Exit codes (Batch 138): pass through path_c_dry_run.py — 0=ready, 1=not ready,
# 2=transport/missing inputs. Do not collapse transport into generic die(1).
# Batch 153: --from-bundle --dry-run verifies tip-drift + local bundle apply (not only apply_all).
# Batch 169: prefer .bundle fetch+merge when present.
if [[ "$DRY_RUN" -eq 1 ]]; then
  if [[ "$FROM_BUNDLE" -eq 1 ]]; then
    if [[ "$USE_GIT_BUNDLE" -eq 1 ]]; then
      [[ -f "$BUNDLE_GIT" ]] || die "missing $BUNDLE_GIT"
    else
      [[ -f "$BUNDLE_PATCH" ]] || die "missing $BUNDLE_PATCH"
    fi
    [[ -n "$BASE_TIP_SHA" ]] || die "could not parse BASE_TIP SHA (need hex in $BASE_TIP_FILE)"
    VERIFY_JSON="$TRIAL_ROOT/portable/path-c-applied-bundle/VERIFY.json"
    VERIFY_SHA=""
    if [[ -f "$VERIFY_JSON" ]]; then
      VERIFY_SHA="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('base_tip_sha') or '')" "$VERIFY_JSON" 2>/dev/null || true)"
      echo "verify_base_tip_sha=$VERIFY_SHA"
      if [[ -n "$VERIFY_SHA" && "$VERIFY_SHA" != "$BASE_TIP_SHA" && "$VERIFY_SHA" != "${BASE_TIP_SHA}"* && "$BASE_TIP_SHA" != "${VERIFY_SHA}"* ]]; then
        echo "owner_land_path_c: ERROR: tip-drift BASE_TIP $BASE_TIP_SHA != VERIFY $VERIFY_SHA" >&2
        exit 1
      fi
    fi
    echo "--- from-bundle dry-run: tip-drift + $([ "$USE_GIT_BUNDLE" -eq 1 ] && echo 'git fetch .bundle' || echo 'git am .patch') (no push) ---"
    FB_WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/owner-path-c-from-bundle-dry.XXXXXX")"
    cleanup_fb() { rm -rf "$FB_WORKDIR"; }
    trap cleanup_fb EXIT
    set +e
    git clone --filter=blob:none --no-checkout "https://github.com/${REPO}.git" "$FB_WORKDIR/main" \
      || git clone --depth 80 "https://github.com/${REPO}.git" "$FB_WORKDIR/main"
    clone_ec=$?
    set -e
    if [[ "$clone_ec" -ne 0 ]]; then
      echo "owner_land_path_c: ERROR: clone failed (exit=2 transport)." >&2
      exit 2
    fi
    cd "$FB_WORKDIR/main"
    # Pin remote-tracking ref (plain `git fetch origin <branch>` after shallow clone
    # often leaves origin/<hardening> unresolved as a literal name, not a SHA).
    if ! git fetch --depth 80 origin "+refs/heads/${HARDENING_REF}:refs/remotes/origin/${HARDENING_REF}"; then
      echo "owner_land_path_c: ERROR: fetch hardening failed (exit=2)." >&2
      exit 2
    fi
    LIVE_SHA="$(git rev-parse --verify "refs/remotes/origin/${HARDENING_REF}^{commit}" 2>/dev/null || true)"
    if [[ -z "$LIVE_SHA" || "$LIVE_SHA" == origin/* || "$LIVE_SHA" != [0-9a-f]* ]]; then
      # Fallback: ls-remote
      LIVE_SHA="$(git ls-remote origin "refs/heads/${HARDENING_REF}" 2>/dev/null | awk '{print $1}' | head -n1 || true)"
    fi
    if [[ -z "$LIVE_SHA" || ! "$LIVE_SHA" =~ ^[0-9a-f]{40}$ ]]; then
      echo "owner_land_path_c: ERROR: cannot resolve live hardening SHA (got: ${LIVE_SHA:-empty}) (exit=2)." >&2
      exit 2
    fi
    echo "live_hardening_sha=$LIVE_SHA"
    if [[ "$LIVE_SHA" != "$BASE_TIP_SHA" && "$LIVE_SHA" != "${BASE_TIP_SHA}"* && "$BASE_TIP_SHA" != "${LIVE_SHA}"* ]]; then
      echo "owner_land_path_c: ERROR: tip-drift live $LIVE_SHA != BASE_TIP $BASE_TIP_SHA — refresh bundle." >&2
      exit 1
    fi
    echo "tip_matches_base=true"
    git config user.name "owner-land-path-c-dry"
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    if ! git checkout --detach "$LIVE_SHA" 2>/dev/null; then
      git fetch --depth 80 origin "$LIVE_SHA" 2>/dev/null || true
      git checkout --detach "$LIVE_SHA" || die "cannot checkout live hardening $LIVE_SHA"
    fi
    # Need BASE_TIP object for bundle prerequisite; LIVE_SHA == BASE_TIP when tip_matches.
    if [[ "$USE_GIT_BUNDLE" -eq 1 ]]; then
      if ! git fetch "$BUNDLE_GIT" "$BUNDLE_BRANCH"; then
        echo "owner_land_path_c: ERROR: git fetch from .bundle failed on BASE_TIP (exit=1)." >&2
        exit 1
      fi
      if ! git merge --ff-only FETCH_HEAD; then
        echo "owner_land_path_c: ERROR: git merge --ff-only from .bundle failed (exit=1)." >&2
        exit 1
      fi
    else
      if ! git am --3way "$BUNDLE_PATCH"; then
        git am --abort 2>/dev/null || true
        echo "owner_land_path_c: ERROR: git am --from-bundle failed on BASE_TIP (exit=1)." >&2
        exit 1
      fi
    fi
    STATUS_OUT="$(python3 tools/math_status_check.py 2>&1)" || {
      echo "owner_land_path_c: ERROR: math_status_check failed after bundle apply." >&2
      echo "$STATUS_OUT" >&2
      exit 1
    }
    echo "$STATUS_OUT"
    if ! echo "$STATUS_OUT" | grep -q 'lemma_closed=false'; then
      echo "owner_land_path_c: ERROR: lemma_closed is not false after bundle apply." >&2
      exit 1
    fi
    if ! echo "$STATUS_OUT" | grep -q 'problems=0'; then
      echo "owner_land_path_c: ERROR: math_status problems!=0 after bundle apply." >&2
      exit 1
    fi
    echo "owner_land_path_c: from-bundle dry-run OK — tip-drift clean; $([ "$USE_GIT_BUNDLE" -eq 1 ] && echo 'git bundle fetch' || echo 'git am') OK; lemma_closed=false."
    echo "Land with write creds: $0 --from-bundle"
    echo "Scientific effect: NONE"
    exit 0
  fi
  [[ -f "$DRY_RUN_PY" ]] || die "missing $DRY_RUN_PY"
  echo "--- path_c_dry_run (apply_all --check + post-ALIGNED tip shape) ---"
  set +e
  python3 "$DRY_RUN_PY"
  dry_ec=$?
  set -e
  if [[ "$dry_ec" -eq 0 ]]; then
    echo "owner_land_path_c: dry-run OK — apply_ready on hardening BASE_TIP."
    echo "Land with write creds: $0   (or $0 --from-bundle after extracting release tarball)"
    echo "Do NOT PATH_C_BASE=main on post-#41 tip."
    echo "Scientific effect: NONE"
    exit 0
  fi
  if [[ "$dry_ec" -eq 2 ]]; then
    echo "owner_land_path_c: ERROR: path_c_dry_run transport/missing inputs (exit=2). See JSON above." >&2
    exit 2
  fi
  echo "owner_land_path_c: ERROR: path_c_dry_run exit=$dry_ec (apply not ready). See JSON above." >&2
  exit 1
fi

need_cmd gh

# Batch 153: prefer MAIN_PUSH_TOKEN / GH_TOKEN for git+gh (same as owner_open_path_c_pr).
# Without this, MAIN_PUSH_TOKEN=… alone leaves the Cursor gh hosts.yml token active.
if [[ -n "${MAIN_PUSH_TOKEN:-}" ]]; then
  export GH_TOKEN="$MAIN_PUSH_TOKEN"
elif [[ -n "${GH_TOKEN:-}" ]]; then
  export MAIN_PUSH_TOKEN="$GH_TOKEN"
fi

if ! gh auth status >/dev/null 2>&1; then
  if [[ -z "${GH_TOKEN:-}" ]]; then
    die "gh is not authenticated and MAIN_PUSH_TOKEN/GH_TOKEN unset. Prerequisites: gh auth login (owner account with write on $REPO) or export MAIN_PUSH_TOKEN. Trial Cloud Agent tokens get 403 — see portable/RELAUNCH_WITH_MAIN_SCOPE.md. Certainty without write: $0 --dry-run"
  fi
fi
LOGIN="$(gh api user --jq .login 2>/dev/null || true)"
echo "gh login: ${LOGIN:-token-env}"

# Fail closed early if this credential cannot write.
if [[ -f "$PROBE" ]]; then
  echo "--- write probe (expect writable / exit 0) ---"
  set +e
  python3 "$PROBE"
  probe_ec=$?
  set -e
  if [[ "$probe_ec" -ne 0 ]]; then
    die "write probe exit=$probe_ec (expected 0=writable). Path C requires Contents:Write on $REPO. Trial cloud tokens get 403 — re-run with owner auth or MAIN_PUSH_TOKEN. Certainty without write: $0 --dry-run"
  fi
else
  echo "warn: missing $PROBE; will fail closed on git push if denied."
fi

# Preflight: if operator forced rebase, warn that post-#41 usually CONFLICTS.
if [[ "$REBASE_ONTO_MAIN" == "1" && -f "$DRY_RUN_PY" ]]; then
  echo "--- PATH_C_REBASE_ONTO_MAIN=1 preflight (path_c_dry_run) ---"
  set +e
  REBASE_JSON="$(python3 "$DRY_RUN_PY" --skip-apply-check 2>/dev/null)"
  set -e
  if echo "$REBASE_JSON" | grep -q '"rebase_onto_main_state": "CONFLICTING"'; then
    die "PATH_C_REBASE_ONTO_MAIN=1 would CONFLICT on post-ALIGNED tip (PR #41 history layout). Unset PATH_C_REBASE_ONTO_MAIN and land on hardening, or resolve rebase locally first. Certainty: $0 --dry-run"
  fi
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
        die "PATH_C_BASE=main but origin/main lacks hardening Path-C shape (need docs/math_status/PACKET.json + tools/carriers_verify.py). Post-ALIGNED tips (PR #41 @ 1c6e74b / historical PR #2) are ALIGNED but a different tree — use PATH_C_BASE=hardening (default). PATH_C_REBASE_ONTO_MAIN usually CONFLICTS after #41; see --dry-run."
      fi
      echo "main"
      ;;
    auto)
      # Post-ALIGNED (PR #41 / post-#2): default tip may be ALIGNED but NOT the
      # portable-patch apply target (no PACKET.json). Prefer hardening.
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
  die "checkout lacks docs/math_status/PACKET.json or tools/carriers_verify.py — wrong base for apply_all (post-ALIGNED default main / PR #41 is not BASE_TIP)."
fi

# Idempotent: skip apply if patches already present (heuristic: carriers pycache ignore).
if grep -q '__pycache__' tools/carriers_verify.py 2>/dev/null \
   && grep -q 'ResourceWarning\|read_bytes\|close-file' tests/test_inventable_jetmod_probes.py 2>/dev/null; then
  echo "Tree already looks patched; running apply_all --check only."
  if ! "$APPLY_ALL" --check; then
    die "apply_all --check failed on apparently-patched tree. Resolve conflicts or reset to a clean tip."
  fi
elif [[ "$FROM_BUNDLE" -eq 1 ]]; then
  echo "--- --from-bundle: prefer .bundle fetch+merge when present ---"
  # Pin to BASE_TIP SHA when file lists it (release bundle is cut against that tip).
  if [[ -f "$BASE_TIP_FILE" ]]; then
    if [[ -z "$BASE_TIP_SHA" ]]; then
      BASE_TIP_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
      BASE_TIP_SHA="$(parse_base_tip_sha "$BASE_TIP_LINE" || true)"
    fi
    if [[ -n "$BASE_TIP_SHA" ]] && git cat-file -e "${BASE_TIP_SHA}^{commit}" 2>/dev/null; then
      HEAD_NOW="$(git rev-parse HEAD)"
      if [[ "$HEAD_NOW" != "$BASE_TIP_SHA" && "$HEAD_NOW" != "${BASE_TIP_SHA}"* ]]; then
        echo "warn: HEAD=$HEAD_NOW != BASE_TIP=$BASE_TIP_SHA; attempting bundle apply anyway (may fail if tip moved)."
      fi
    fi
  fi
  apply_from_bundle_artifact
else
  echo "--- apply_all 0001–0004 + 0008–0016 ---"
  if ! "$APPLY_ALL"; then
    die "apply_all failed. Tip may have moved past BASE_TIP; refresh portable/patches. Do not PATH_C_BASE=main on post-#41 tip; PATH_C_REBASE_ONTO_MAIN usually CONFLICTS — see --dry-run."
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

Post-ALIGNED default tip (owner [PR #41](https://github.com/d6g8k5htny-coder/main/pull/41) @ \`1c6e74b\`, or historical PR #2): ALIGNED but a different tree (no \`PACKET.json\`; post-#41 \`body\` under \`history/\`). Keep Path C on hardening (BASE_TIP). \`PATH_C_REBASE_ONTO_MAIN\` usually CONFLICTS after #41 — certainty: \`./scripts/owner_land_path_c.sh --dry-run\`.

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
echo "Actions alternative (trial secret MAIN_PUSH_TOKEN):"
echo "  gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo "  # workflow: .github/workflows/land-path-c-on-main.yml (dry_run default true)"
echo
echo "owner_land_path_c: branch+PR ready."
echo "Scientific effect: NONE"
exit 0
