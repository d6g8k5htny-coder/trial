#!/usr/bin/env bash
# Apply all portable engineering patches onto a writable checkout of
# d6g8k5htny-coder/main (working tip chatgpt/drive-github-hardening-20260919).
# See BASE_TIP.txt for the currently verified tip SHA (batch 65: 3d47d1b after #42).
#
# Scientific effect: NONE. Does not flip lemma_closed / discharge obligations.
# Usage (from a clean main checkout at the base tip, or a descendant):
#   /path/to/trial/portable/patches/apply_all.sh          # apply
#   /path/to/trial/portable/patches/apply_all.sh --check  # dry-run only
#
# Patches are checked/applied in order. After main PR #27 merged (batch 48),
# tip-cut 0005/0006/0007 are obsolete (isolation supersedes dirty-receipt
# restore + pre-isolation open shape). Stack is 0001–0004 + 0008–0016.
#
# Post-#41 tip topology (Path C):
#   - default main @ 1c6e74b (PR #41) is ALIGNED research *landing* but NOT
#     Path-C shaped (no docs/math_status/PACKET.json; body under history/;
#     tools/ are stubs). Never apply_all there; do not PATH_C_BASE=main.
#   - Path C stays on chatgpt/drive-github-hardening-20260919 (BASE_TIP).
#   - PATH_C_REBASE_ONTO_MAIN usually CONFLICTS after #41 (ci.yml / bridge).
# Apply against hardening BASE_TIP (or a descendant), NOT post-#41 default main
# and NOT the post-#32 pre-q0 face. --check uses a disposable worktree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CHECK_ONLY=0
if [[ "${1:-}" == "--check" ]]; then
  CHECK_ONLY=1
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--check]" >&2
  exit 2
fi

BASE_FILE="$ROOT/BASE_TIP.txt"
BASE_SHA=""
if [[ -f "$BASE_FILE" ]]; then
  BASE_LINE="$(tr -d '\r' <"$BASE_FILE" | head -n1)"
  echo "Patches cut against: $BASE_LINE"
  # Last whitespace-separated field is the verified SHA.
  BASE_SHA="${BASE_LINE##* }"
fi

# Fail closed on post-#41 / post-#32 default-main trees (ALIGNED landing ≠ hardening).
if [[ ! -f tools/carriers_verify.py || ! -f docs/math_status/PACKET.json ]]; then
  echo "error: run from a d6g8k5htny-coder/main hardening checkout root" >&2
  echo "error: need tools/carriers_verify.py + docs/math_status/PACKET.json" >&2
  if [[ -f AGENTS.md || -f README.md ]]; then
    echo "error: this tree looks like post-#41 default main (ALIGNED landing) or another non-hardening tip" >&2
    echo "error: Path C apply_all targets chatgpt/drive-github-hardening-20260919 (see BASE_TIP.txt)" >&2
    echo "error: do not set PATH_C_BASE=main; PATH_C_REBASE_ONTO_MAIN usually CONFLICTS after #41" >&2
  fi
  exit 2
fi

# Currency note: warn when HEAD is not the recorded BASE_TIP (descendant OK).
if [[ -n "$BASE_SHA" ]] && git rev-parse --verify "${BASE_SHA}^{commit}" >/dev/null 2>&1; then
  HEAD_SHA="$(git rev-parse HEAD)"
  if [[ "$HEAD_SHA" != "$BASE_SHA" ]]; then
    if git merge-base --is-ancestor "$BASE_SHA" HEAD 2>/dev/null; then
      echo "note: HEAD $(git rev-parse --short HEAD) is ahead of BASE_TIP ${BASE_SHA:0:7} (descendant OK; refresh BASE_TIP.txt when tip moves)"
    elif git merge-base --is-ancestor HEAD "$BASE_SHA" 2>/dev/null; then
      echo "warning: HEAD $(git rev-parse --short HEAD) is behind BASE_TIP ${BASE_SHA:0:7}" >&2
    else
      echo "warning: HEAD $(git rev-parse --short HEAD) and BASE_TIP ${BASE_SHA:0:7} have diverged — refresh BASE_TIP / re-cut patches" >&2
    fi
  fi
fi

PATCHES=(
  "$ROOT/0001-carriers-verify-ignore-bytecode-caches.patch"
  "$ROOT/0002-math-console-path-honesty.patch"
  "$ROOT/0003-gaussian-moments-parametrize-list.patch"
  "$ROOT/0004-git-fixture-timeout-60s.patch"
  # 0005/0006/0007 dropped after main PR #27 merge (bf1fde3); kept on disk for history
  "$ROOT/0008-carriers-math-status-close-file-handles.patch"
  "$ROOT/0009-claims-close-file-handles.patch"
  "$ROOT/0010-recovery-close-file-handles.patch"
  "$ROOT/0011-math-status-check-close-file-handles.patch"
  "$ROOT/0012-inventable-negative-tests-close-file-handles.patch"
  "$ROOT/0013-verify-quarantine-close-file-handles.patch"
  "$ROOT/0014-collision-close-file-handles.patch"
  "$ROOT/0015-frozen-drive-index-close-file-handles.patch"
  "$ROOT/0016-receipts-bridge-close-file-handles.patch"
)

apply_series() {
  local p
  for p in "${PATCHES[@]}"; do
    git apply --check "$p"
    git apply "$p"
  done
}

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  # Disposable worktree so sequential deps validate without dirtying the caller's tree.
  WT="$(mktemp -d "${TMPDIR:-/tmp}/trial-apply-all-check.XXXXXX")"
  cleanup() {
    git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  }
  trap cleanup EXIT
  git worktree add --detach "$WT" HEAD >/dev/null
  (
    cd "$WT"
    apply_series
  )
  trap - EXIT
  cleanup
  echo "Check OK (no changes applied)."
  exit 0
fi

apply_series
echo "Applied. Recommended verification:"
echo "  python3 tools/math_status_check.py"
echo "  python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py tests/test_claims.py tests/test_recovery.py"
echo "  # expect: problems=0, lemma_closed=false; 90 focused + 47 claims + 36 recovery passed; free of ResourceWarning"
echo "  # math_status_check 0 RW after 0011; inventable negatives 0 after 0012; verify_manifests/quarantine 0 after 0013"
echo "  # collision_proposal_check + tests/test_collision_proposal.py 0 RW after 0014"
echo "  # tests/test_frozen_check.py + test_drive_index_overlay.py 0 RW after 0015"
echo "  # tests/test_receipts.py + test_bridge.py 0 RW after 0016"
