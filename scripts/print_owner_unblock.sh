#!/usr/bin/env bash
# Print Path B/C (primary) + Path A HOLD notice + live probe/audit status.
# Scientific effect: NONE. Read-only against d6g8k5htny-coder/main.
#
# HOLD (Dylan/CoS 2026-09-23): Path A inactive; Path B preferred.
# Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== HOLD — Path A inactive (Dylan/CoS) ==="
echo "PR #2 stays draft / untouched. Do not ready/merge/retarget."
echo "Comment: https://github.com/d6g8k5htny-coder/main/pull/2#issuecomment-5801736084"
echo "Preferred unblock: Path B (Option-B notice) or grant App write for Path B only."
echo "Scientific effect: NONE"
echo

echo "=== OWNER_ONE_LINERS (paths) ==="
echo "  $ROOT/portable/OWNER_ONE_LINERS.md"
echo "  $ROOT/portable/LAND.md"
echo "  $ROOT/docs/OWNER_ACTIONS_MAIN.md"
echo "  $ROOT/.github/workflows/land-option-b-on-main.yml"
echo

if [[ -f "$ROOT/portable/OWNER_ONE_LINERS.md" ]]; then
  echo "=== OWNER_ONE_LINERS (file) ==="
  cat "$ROOT/portable/OWNER_ONE_LINERS.md"
  echo
fi

echo "=== live probe / audit (this credential) ==="
echo "# write probe (0=writable, 1=denied, 2=transport):"
python3 "$ROOT/scripts/probe_main_write.py" || true
echo
echo "# alignment audit (0=ALIGNED, 1=MISALIGNED, 2=transport):"
set +e
python3 "$ROOT/scripts/audit_main_alignment.py"
audit_ec=$?
set -e
echo "(audit exit=$audit_ec)"
echo
echo "# watch one-liner:"
python3 "$ROOT/scripts/watch_main_alignment.py" || true
echo
echo "# wait until ALIGNED (poll watch; default 30s / max 2h; --verify runs VERIFY_AFTER_MERGE):"
echo "$ROOT/scripts/wait_until_aligned.sh"
echo "$ROOT/scripts/wait_until_aligned.sh --verify"
echo
echo "=== owner land scripts (run with *owner* gh auth / write on main) ==="
echo "# Path B — PRIMARY under HOLD: Option-B branch + PR; then --after-merge:"
echo "$ROOT/scripts/owner_land_path_b.sh"
echo "$ROOT/scripts/owner_land_path_b.sh --after-merge"
echo "# Path B opt-in direct push to default main:"
echo "$ROOT/scripts/owner_land_path_b.sh --direct-main"
echo "# Path A — ON HOLD (hard-refuses unless OWNER_FORCE_PATH_A=1 for Dylan only):"
echo "# $ROOT/scripts/owner_land_path_a.sh   # exits 1 under HOLD"
echo "# Path C — after default tip ALIGNED (Path B preferred): apply_all 0001–0004 + 0008–0012:"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# PATH_C_BASE=main $ROOT/scripts/owner_land_path_c.sh   # post-alignment research tree on default tip"
echo
echo "=== copy-paste Path B FIRST (trial Actions + MAIN_PUSH_TOKEN) ==="
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-option-b-on-main → Run workflow → dry_run=false"
echo "# 3) Merge the opened PR (or branch cursor/option-b-notice-from-trial) into default main"
echo "gh workflow run land-option-b-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo
echo "=== copy-paste Path A (ON HOLD — do not run unless Dylan lifts HOLD) ==="
echo "# REFUSED under HOLD. Script exits 1 unless OWNER_FORCE_PATH_A=1 (Dylan only)."
echo "# gh pr ready 2 --repo d6g8k5htny-coder/main"
echo "# gh pr merge 2 --repo d6g8k5htny-coder/main --merge"
echo
echo "=== copy-paste Path C (after Path B / post-HOLD Path A; needs write on main) ==="
echo "# rebase hardening onto new main if needed, then:"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# or: $ROOT/portable/patches/apply_all.sh on a writable tip checkout"
echo
echo "Scientific effect: NONE"
