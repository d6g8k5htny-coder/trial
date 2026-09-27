#!/usr/bin/env bash
# Apply all portable engineering patches onto a writable checkout of
# d6g8k5htny-coder/main (working tip chatgpt/drive-github-hardening-20260919).
# See BASE_TIP.txt for the currently verified tip SHA (batch 162: 8ea3b5f after #53).
#
# Scientific effect: NONE. Does not flip lemma_closed / discharge obligations.
# Usage (from a clean main checkout at the base tip, or a descendant):
#   /path/to/trial/portable/patches/apply_all.sh          # apply
#   /path/to/trial/portable/patches/apply_all.sh --check  # dry-run only
#
# Patches are checked/applied in order. After main PR #27 merged (batch 48),
# tip-cut 0005/0006/0007 are obsolete (isolation supersedes dirty-receipt
# restore + pre-isolation open shape). Stack is 0001–0004 + 0008–0019.
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
  "$ROOT/0017-pinned-sources-close-file-handles.patch"
  # 0018: REPOSITORY_TOP_LEVEL += attestations (main PR #70). Requires attestations/;
  # skipped when that top-level dir is absent so pre-#70 tips stay green.
  "$ROOT/0018-repository-top-level-attestations.patch"
  # 0019: attestations_check + test_attestations close file handles (tip @ 62f955a).
  "$ROOT/0019-attestations-close-file-handles.patch"
)

# Content-level already-applied test for a unified diff against the current
# tree: for every target file, all '+' lines must be present and all '-' lines
# (that are not re-added) must be absent. Whitespace-stripped line matching;
# a patch that deletes or creates files never qualifies.
semantic_already_applied() {
  python3 - "$1" <<'PY'
import sys
from pathlib import Path

patch = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
files = {}
target = None
for line in patch:
    if line.startswith("+++ "):
        name = line[4:].split("\t")[0].strip()
        if name == "/dev/null":
            sys.exit(1)
        target = name[2:] if name.startswith("b/") else name
        files.setdefault(target, ([], []))
    elif line.startswith("--- "):
        if line[4:].split("\t")[0].strip() == "/dev/null":
            sys.exit(1)
    elif target is not None and line.startswith("+") and not line.startswith("+++"):
        files[target][0].append(line[1:].strip())
    elif target is not None and line.startswith("-") and not line.startswith("---"):
        files[target][1].append(line[1:].strip())

if not files:
    sys.exit(1)
for name, (added, removed) in files.items():
    path = Path(name)
    if not path.is_file():
        sys.exit(1)
    tree = {ln.strip() for ln in path.read_text(encoding="utf-8", errors="replace").splitlines()}
    added_set = {ln for ln in added if ln}
    removed_only = {ln for ln in removed if ln} - added_set
    if not added_set and not removed_only:
        sys.exit(1)
    if not added_set <= tree:
        sys.exit(1)
    if removed_only & tree:
        sys.exit(1)
sys.exit(0)
PY
}

# Batch 231: idempotent apply — if a patch is already on the tree (Path C landed
# @ 93a4ecd / PR #64), skip it via reverse --check. Fail only when neither
# forward nor reverse applies (real conflict / tip drift).
# Outcome counters (summary line lets callers decide whether the whole stack is
# already on the tree — the tip-drift tolerance signal — without parsing echoes).
N_FORWARD=0
N_ALREADY=0
N_SKIPPED=0

apply_one() {
  local p="$1"
  local check_only="${2:-0}"
  # 0018/0019 couple to top-level attestations/ (added by main PR #70). Skip on
  # older tips so REPOSITORY_TOP_LEVEL / attestations close-handles do not
  # fail when that directory is missing.
  bn="$(basename "$p")"
  if [[ ( "$bn" == 0018-* || "$bn" == 0019-* ) && ! -d attestations ]]; then
    echo "skip (attestations/ absent): ${bn}"
    N_SKIPPED=$((N_SKIPPED + 1))
    return 0
  fi
  # Batch 378 tip-sync @ebedb78: 0018/0019 already on tip but context drifted
  # (architecture joined REPOSITORY_TOP_LEVEL; close-handles already present).
  # Treat semantic already-applied as success so keep-prior refresh can proceed.
  if [[ "$bn" == 0018-* ]] && grep -q '"attestations"' engine/bridge/work_order.py 2>/dev/null; then
    echo "already-applied (semantic): ${bn}"
    N_ALREADY=$((N_ALREADY + 1))
    return 0
  fi
  if [[ "$bn" == 0019-* ]] && grep -q 'with open(candidate' tools/attestations_check.py 2>/dev/null; then
    echo "already-applied (semantic): ${bn}"
    N_ALREADY=$((N_ALREADY + 1))
    return 0
  fi
  # 0017 (tip @e7652a1: third-hunk context drifted survey → full_survey while the
  # close-handles change itself is on tip) is covered by the generic
  # semantic_already_applied() fallback below — no per-patch grep needed.
  if git apply --check "$p" >/dev/null 2>&1; then
    if [[ "$check_only" -eq 0 ]]; then
      git apply "$p"
      echo "applied: $(basename "$p")"
    else
      # In --check mode, still apply into the disposable worktree so later
      # patches in the stack see the expected sequential base.
      git apply "$p"
      echo "check-ok: $(basename "$p")"
    fi
    N_FORWARD=$((N_FORWARD + 1))
    return 0
  fi
  if git apply --reverse --check "$p" >/dev/null 2>&1; then
    echo "already-applied: $(basename "$p")"
    N_ALREADY=$((N_ALREADY + 1))
    return 0
  fi
  # Batch 810 tip-sync @e7652a1: landed patches whose surrounding context later
  # drifted (e.g. 0017 after main #140 grew tests/test_pinned_sources.py) fail
  # both forward and reverse --check although every hunk is on the tree. Generic
  # semantic check: every added line present and every removed line absent in
  # each target file ⇒ already-applied. Anything else still fails closed.
  if semantic_already_applied "$p"; then
    echo "already-applied (semantic): ${bn}"
    N_ALREADY=$((N_ALREADY + 1))
    return 0
  fi
  echo "error: patch does not apply (forward or reverse): $(basename "$p")" >&2
  git apply --check "$p" 2>&1 | tail -n 20 >&2 || true
  return 1
}

apply_series() {
  local p
  local check_only="${1:-0}"
  for p in "${PATCHES[@]}"; do
    apply_one "$p" "$check_only" || return 1
  done
}

# Machine-readable stack summary. already_on_tip=1 iff no patch needed a forward
# apply (every patch already-applied or intentionally skipped) — this is the
# signal tip-drift gates use to tolerate BASE_TIP lagging a moved hardening tip
# once Path C has landed. Any forward apply or failure keeps it 0.
print_summary() {
  local on_tip=0
  if [[ "$N_FORWARD" -eq 0 && "$N_ALREADY" -gt 0 ]]; then
    on_tip=1
  fi
  echo "apply_all: summary forward=${N_FORWARD} already_applied=${N_ALREADY} skipped=${N_SKIPPED} already_on_tip=${on_tip} head=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
}

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  # Disposable worktree so sequential deps validate without dirtying the caller's tree.
  WT="$(mktemp -d "${TMPDIR:-/tmp}/trial-apply-all-check.XXXXXX")"
  cleanup() {
    git worktree remove --force "$WT" 2>/dev/null || rm -rf "$WT"
  }
  trap cleanup EXIT
  git worktree add --detach "$WT" HEAD >/dev/null
  # pushd (not a subshell) so the outcome counters survive for print_summary.
  pushd "$WT" >/dev/null
  if ! apply_series 1; then
    popd >/dev/null
    exit 1
  fi
  popd >/dev/null
  trap - EXIT
  cleanup
  print_summary
  echo "Check OK (no changes applied; already-applied patches skipped)."
  exit 0
fi

apply_series 0
print_summary
echo "Applied (or already on tip). Recommended verification:"
echo "  python3 tools/math_status_check.py"
echo "  python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py tests/test_claims.py tests/test_recovery.py"
echo "  # expect: problems=0, lemma_closed=false; 90 focused + 47 claims + 36 recovery passed; free of ResourceWarning"
echo "  # math_status_check 0 RW after 0011; inventable negatives 0 after 0012; verify_manifests/quarantine 0 after 0013"
echo "  # collision_proposal_check + tests/test_collision_proposal.py 0 RW after 0014"
echo "  # tests/test_frozen_check.py + test_drive_index_overlay.py 0 RW after 0015"
echo "  # tests/test_receipts.py + test_bridge.py 0 RW after 0016"
echo "  # tests/test_pinned_sources.py 0 RW after 0017"
echo "  # tools/attestations_check.py + tests/test_attestations.py 0 RW after 0019"
