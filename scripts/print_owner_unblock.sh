#!/usr/bin/env bash
# Print Path B (preferred for ALIGNED) + Path C engineering + live probe/audit.
# Scientific effect: NONE. Read-only against d6g8k5htny-coder/main.
#
# Path A (#2) was MERGED then REVERTED by CoS PR #32 — default tip MISALIGNED @ 4fc1d7c.
# Preferred ALIGNED unblock: Path B. Path C = engineering on hardening (BASE_TIP).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Path A REVERTED (PR #32) — default tip MISALIGNED ==="
echo "PR #2 @ b040bf0c was reverted by PR #32 @ 4fc1d7c. Prefer Path B for ALIGNED."
echo "Path C stays on chatgpt/drive-github-hardening-20260919 (BASE_TIP 580864c after #31; has PACKET.json)."
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
echo "# Path B — PRIMARY for default-tip ALIGNED (Option-B notice):"
echo "$ROOT/scripts/owner_land_path_b.sh"
echo "$ROOT/scripts/owner_land_path_b.sh --after-merge"
echo "# Path C — engineering: apply_all 0001–0004 + 0008–0016 on hardening tip:"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Path A — REVERTED by PR #32; do not re-run without Dylan/CoS auth:"
echo "$ROOT/scripts/owner_land_path_a.sh"
echo
echo "=== copy-paste Path C (needs write on main) ==="
echo "# apply on hardening BASE_TIP; optional PATH_C_REBASE_ONTO_MAIN=1:"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# or: $ROOT/portable/patches/apply_all.sh on a writable hardening tip checkout"
echo
echo "=== copy-paste Path B (optional) ==="
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-option-b-on-main → Run workflow → dry_run=false"
echo "gh workflow run land-option-b-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo
echo "Scientific effect: NONE"
