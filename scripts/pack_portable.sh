#!/usr/bin/env bash
# Build a tarball of the portable main-alignment pack for owner download.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/../trial-portable-main-fixes.tgz}"
tar -czf "$OUT" -C "$ROOT" \
  portable/LAND.md \
  portable/OWNER_ONE_LINERS.md \
  portable/CONFLICTING_PR_NOTES.md \
  portable/EXPECTED_POST_ALIGNMENT.json \
  portable/RESTORE_PLAN_53b.json \
  portable/RESTORE_PLAN_54.json \
  portable/RESTORE_PLAN_55.json \
  portable/RESTORE_PLAN_56.json \
  portable/RESTORE_PLAN_57.json \
  portable/RESTORE_PLAN_58.json \
  portable/RESTORE_PLAN_59.json \
  portable/RESTORE_PLAN_60.json \
  portable/RESTORE_PLAN_61.json \
  portable/RESTORE_PLAN_62.json \
  portable/RESTORE_PLAN_63.json \
  portable/BATCH58_TOKEN_SEARCH.json \
  portable/BATCH59_TOKEN_SEARCH.json \
  portable/BATCH60_TOKEN_SEARCH.json \
  portable/BATCH61_TOKEN_SEARCH.json \
  portable/BATCH62_TOKEN_SEARCH.json \
  portable/BATCH63_TOKEN_SEARCH.json \
  portable/main-default-branch \
  portable/pr2-landing \
  portable/patches \
  scripts/audit_main_alignment.py \
  scripts/audit_local_tree.py \
  scripts/alignment_status.py \
  scripts/watch_main_alignment.py \
  scripts/check_autonomous_window.py \
  scripts/probe_main_write.py \
  scripts/probe_main_write_vectors.py \
  scripts/path_b_dry_run.py \
  scripts/path_c_dry_run.py \
  scripts/refresh_restore_plan.py \
  scripts/print_owner_unblock.sh \
  scripts/restore_main_face.sh \
  scripts/owner_land_path_a.sh \
  scripts/owner_land_path_b.sh \
  scripts/owner_land_path_c.sh \
  scripts/pack_portable.sh
echo "wrote $OUT ($(wc -c <"$OUT") bytes)"
