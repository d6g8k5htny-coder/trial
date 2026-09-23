#!/usr/bin/env bash
# Apply all portable engineering patches onto a writable checkout of
# d6g8k5htny-coder/main (working tip chatgpt/drive-github-hardening-20260919).
# See BASE_TIP.txt for the currently verified tip SHA (batch 53: fbb4360 after #30).
#
# Scientific effect: NONE. Does not flip lemma_closed / discharge obligations.
# Usage (from a clean main checkout at the base tip, or a descendant):
#   /path/to/trial/portable/patches/apply_all.sh          # apply
#   /path/to/trial/portable/patches/apply_all.sh --check  # dry-run only
#
# Patches are checked/applied in order. After main PR #27 merged (batch 48),
# tip-cut 0005/0006/0007 are obsolete (isolation supersedes dirty-receipt
# restore + pre-isolation open shape). Stack is 0001–0004 + 0008–0016.
# Apply against chatgpt/drive-github-hardening-20260919 (BASE_TIP), NOT the
# post-#2 default main tip (different tree; lacks docs/math_status/PACKET.json).
# --check uses a disposable worktree.
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
if [[ -f "$BASE_FILE" ]]; then
  echo "Patches cut against: $(cat "$BASE_FILE")"
fi

if [[ ! -f tools/carriers_verify.py || ! -f docs/math_status/PACKET.json ]]; then
  echo "error: run from a d6g8k5htny-coder/main checkout root" >&2
  exit 2
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
