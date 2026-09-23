#!/usr/bin/env bash
# Print Path A/B/C owner one-liners + live probe/audit status.
# Scientific effect: NONE. Read-only against d6g8k5htny-coder/main.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

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
echo "=== copy-paste Path A (needs write on main) ==="
echo "gh pr ready 2 --repo d6g8k5htny-coder/main"
echo "gh pr merge 2 --repo d6g8k5htny-coder/main --merge"
echo
echo "=== copy-paste Path B (trial Actions + MAIN_PUSH_TOKEN) ==="
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-option-b-on-main → Run workflow → dry_run=false"
echo "# 3) Merge the opened PR (or branch cursor/option-b-notice-from-trial) into default main"
echo "gh workflow run land-option-b-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo
echo "Scientific effect: NONE"
