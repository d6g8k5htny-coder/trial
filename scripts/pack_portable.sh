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
  portable/main-default-branch \
  portable/pr2-landing \
  portable/patches \
  scripts/audit_main_alignment.py \
  scripts/audit_local_tree.py \
  scripts/alignment_status.py \
  scripts/watch_main_alignment.py \
  scripts/probe_main_write.py \
  scripts/print_owner_unblock.sh \
  scripts/owner_land_path_a.sh \
  scripts/owner_land_path_b.sh \
  scripts/owner_land_path_c.sh \
  scripts/pack_portable.sh
echo "wrote $OUT ($(wc -c <"$OUT") bytes)"
