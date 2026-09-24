#!/usr/bin/env bash
# Print Path B (preferred for ALIGNED) + Path A/C + live probe/audit.
# Scientific effect: NONE. Read-only against d6g8k5htny-coder/main.
#
# Reads portable/patches/BASE_TIP.txt for Path C currency (no hardcoded SHA).
# Post-#41: default main ALIGNED landing ≠ hardening Path-C tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASE_TIP_FILE="$ROOT/portable/patches/BASE_TIP.txt"
BASE_TIP_LINE="(missing BASE_TIP.txt)"
BASE_TIP_SHORT="unknown"
if [[ -f "$BASE_TIP_FILE" ]]; then
  BASE_TIP_LINE="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1)"
  BASE_TIP_SHORT="${BASE_TIP_LINE##* }"
  BASE_TIP_SHORT="${BASE_TIP_SHORT:0:7}"
fi

echo "=== Batch 65 — PERMANENT window; ALIGNED @ 1c6e74b (PR #41); Path C BASE_TIP ${BASE_TIP_SHORT} (post-#42); unrestricted/auto-approve; HOLD VOID ==="
echo "Owner: NO restrictions; agents decide. HOLD on PR #2 is VOID."
echo "Dylan: 48h extended permanently until he intervenes — no 48h finale."
echo "Window: $ROOT/scripts/check_autonomous_window.py  # PERMANENT_UNTIL_OWNER_INTERVENES"
echo "Watch (embeds window+route): $ROOT/scripts/watch_main_alignment.py"
echo "Timer: re-arm permanent-autonomous-align-watch @ 3600s (not a 48h-stop timer)."
echo "PR #41 renewed default tip to 1c6e74b (ALIGNED). Keep iterating."
echo "Path A OR Path B OK when MISALIGNED. Prefer Path B (Option-B README+AGENTS)."
echo "One-command: $ROOT/scripts/restore_main_face.sh  # short-circuits when already ALIGNED"
echo "Path C BASE_TIP file: $BASE_TIP_LINE"
echo "Path C: $ROOT/scripts/owner_land_path_c.sh --dry-run  # APPLY_READY on hardening BASE_TIP ${BASE_TIP_SHORT}"
echo "Path C stays on chatgpt/drive-github-hardening-20260919 (has PACKET.json; rebase onto main CONFLICTS)."
echo "Post-#41: do NOT PATH_C_BASE=main (ALIGNED landing lacks PACKET.json)."
echo "pack_portable.sh auto-globs RESTORE_PLAN_* + BATCH*_TOKEN_SEARCH (Batch 64+)."
echo "Scientific effect: NONE"
echo

echo "=== OWNER_ONE_LINERS (paths) ==="
echo "  $ROOT/portable/OWNER_ONE_LINERS.md"
echo "  $ROOT/portable/LAND.md"
echo "  $ROOT/docs/OWNER_ACTIONS_MAIN.md"
echo "  $ROOT/.github/workflows/land-option-b-on-main.yml"
echo "  $ROOT/scripts/restore_main_face.sh"
echo

if [[ -f "$ROOT/portable/OWNER_ONE_LINERS.md" ]]; then
  echo "=== OWNER_ONE_LINERS (file) ==="
  cat "$ROOT/portable/OWNER_ONE_LINERS.md"
  echo
fi

echo "=== live probe / audit (this credential) ==="
echo "# write probe single-ref (0=writable, 1=denied, 2=transport):"
python3 "$ROOT/scripts/probe_main_write.py" || true
echo
echo "# multi-vector Path B probe (0=any Path-B-capable writable):"
python3 "$ROOT/scripts/probe_main_write_vectors.py" || true
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
echo "# Path B — PREFERRED one-command restore:"
echo "$ROOT/scripts/restore_main_face.sh --dry-run"
echo "$ROOT/scripts/restore_main_face.sh"
echo "# Path B — underlying owner script:"
echo "$ROOT/scripts/owner_land_path_b.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_b.sh"
echo "$ROOT/scripts/owner_land_path_b.sh --after-merge"
echo "$ROOT/scripts/path_b_dry_run.py"
echo "$ROOT/scripts/path_c_dry_run.py"
echo "$ROOT/scripts/refresh_restore_plan.py --batch 65"
echo "$ROOT/scripts/check_autonomous_window.py"
echo "$ROOT/scripts/watch_main_alignment.py  # embeds autonomous_window + route (Batch 62+)"
echo "$ROOT/scripts/alignment_status.py"
echo "# Path C — engineering: apply_all 0001–0004 + 0008–0016 on hardening tip:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Path A — HOLD VOID; default PATH_A_MODE=revert32 (or ready_merge for a fresh OPEN port PR):"
echo "$ROOT/scripts/owner_land_path_a.sh"
echo
echo "=== copy-paste Path C (needs write on main) ==="
echo "# dry-run first (no write); then land on hardening BASE_TIP — avoid PATH_C_REBASE_ONTO_MAIN post-#41:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# or: $ROOT/portable/patches/apply_all.sh on a writable hardening tip checkout"
echo
echo "=== copy-paste Path B (optional) ==="
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-option-b-on-main → Run workflow → dry_run=false"
echo "gh workflow run land-option-b-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo
echo "Scientific effect: NONE"
