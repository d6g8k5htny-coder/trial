#!/usr/bin/env bash
# Print Path C (primary remaining) + Path A MERGED notice + live probe/audit status.
# Scientific effect: NONE. Read-only against d6g8k5htny-coder/main.
#
# Path A MERGED 2026-09-23 @ b040bf0c — default tip ALIGNED.
# Remaining owner land: Path C on hardening tip (BASE_TIP). Path B optional.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Path A MERGED — default tip ALIGNED ==="
echo "PR #2 merged @ b040bf0c. Remaining: Path C on chatgpt/drive-github-hardening-20260919."
echo "Post-#2 default main is a different tree — do not apply Path C there without PACKET.json."
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
echo "# Path C — PRIMARY remaining: apply_all 0001–0004 + 0008–0016 on hardening tip:"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Optional rebase hardening onto post-#2 main first:"
echo "# PATH_C_REBASE_ONTO_MAIN=1 $ROOT/scripts/owner_land_path_c.sh"
echo "# Path B — optional (default tip already ALIGNED):"
echo "$ROOT/scripts/owner_land_path_b.sh"
echo "$ROOT/scripts/owner_land_path_b.sh --after-merge"
echo "# Path A — DONE (PR #2 merged @ b040bf0c); historical script:"
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
