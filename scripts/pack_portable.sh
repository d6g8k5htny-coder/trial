#!/usr/bin/env bash
# Build a tarball of the portable main-alignment pack for owner download.
#
# Batch 64+: auto-includes every portable/RESTORE_PLAN_*.json and
# portable/BATCH*_TOKEN_SEARCH.json so each batch need not edit this list.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/../trial-portable-main-fixes.tgz}"

mapfile -t RESTORE_PLANS < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'RESTORE_PLAN_*.json' | sort)
mapfile -t TOKEN_SEARCHES < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'BATCH*_TOKEN_SEARCH.json' | sort)
# Batch 67+: conflict-aware Path C rebase reports (concrete readiness, not RESTORE fluff).
mapfile -t REBASE_REPORTS < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'PATH_C_REBASE_CONFLICT_REPORT_*.json' | sort)
# Batch 68+: owner-safe resolution notes for first-stop ours/theirs staging.
mapfile -t REBASE_NOTES < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'PATH_C_REBASE_RESOLUTION_NOTES_*.json' | sort)
# Batch 70+: mechanical research-stack OPEN audits (no status flips).
mapfile -t STACK_AUDITS < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'BATCH*_RESEARCH_STACK_AUDIT.json' | sort)
# Batch 86+: no-status-promotion guard snapshot (OPEN→closed detection).
mapfile -t STATUS_GUARD < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'STATUS_GUARD_SNAPSHOT.json' | sort)
# Batch 83+: requirement-by-requirement autonomous objective evidence.
mapfile -t OBJECTIVE_EVIDENCE < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'OBJECTIVE_EVIDENCE_*.json' | sort)
# Batch 134+: tiny batch briefs + residual RW hunt reports (portable readiness).
mapfile -t BATCH_BRIEFS < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'BATCH*_BRIEF.json' | sort)
mapfile -t BATCH_HUNTS < <(find "$ROOT/portable" -maxdepth 1 -type f -name 'BATCH*_HUNT.json' | sort)

# Batch 89+: patches MANIFEST (apply_all ids + headers; also under portable/patches/).
PATCHES_MANIFEST="$ROOT/portable/patches/MANIFEST.json"

if [[ ${#RESTORE_PLANS[@]} -eq 0 ]]; then
  echo "pack_portable: ERROR: no portable/RESTORE_PLAN_*.json found" >&2
  exit 2
fi
if [[ ${#TOKEN_SEARCHES[@]} -eq 0 ]]; then
  echo "pack_portable: ERROR: no portable/BATCH*_TOKEN_SEARCH.json found" >&2
  exit 2
fi
if [[ ! -f "$PATCHES_MANIFEST" ]]; then
  echo "pack_portable: ERROR: missing portable/patches/MANIFEST.json" >&2
  exit 2
fi

# Relativize paths for tar -C "$ROOT"
rel_restore=()
for p in "${RESTORE_PLANS[@]}"; do
  rel_restore+=("${p#"$ROOT"/}")
done
rel_tokens=()
for p in "${TOKEN_SEARCHES[@]}"; do
  rel_tokens+=("${p#"$ROOT"/}")
done
rel_rebase=()
for p in "${REBASE_REPORTS[@]}"; do
  rel_rebase+=("${p#"$ROOT"/}")
done
rel_rebase_notes=()
for p in "${REBASE_NOTES[@]}"; do
  rel_rebase_notes+=("${p#"$ROOT"/}")
done
rel_stack_audits=()
for p in "${STACK_AUDITS[@]}"; do
  rel_stack_audits+=("${p#"$ROOT"/}")
done
rel_objective_evidence=()
for p in "${OBJECTIVE_EVIDENCE[@]}"; do
  rel_objective_evidence+=("${p#"$ROOT"/}")
done
rel_status_guard=()
for p in "${STATUS_GUARD[@]}"; do
  rel_status_guard+=("${p#"$ROOT"/}")
done
rel_batch_briefs=()
for p in "${BATCH_BRIEFS[@]}"; do
  rel_batch_briefs+=("${p#"$ROOT"/}")
done
rel_batch_hunts=()
for p in "${BATCH_HUNTS[@]}"; do
  rel_batch_hunts+=("${p#"$ROOT"/}")
done

tar -czf "$OUT" -C "$ROOT" \
  portable/LAND.md \
  portable/OWNER_ONE_LINERS.md \
  portable/CONFLICTING_PR_NOTES.md \
  portable/EXPECTED_POST_ALIGNMENT.json \
  portable/ALIGNED_DRIFT_SNAPSHOT.json \
  portable/GH_DEVICE_LOGIN.md \
  "${rel_restore[@]}" \
  "${rel_tokens[@]}" \
  ${rel_rebase[@]+"${rel_rebase[@]}"} \
  ${rel_rebase_notes[@]+"${rel_rebase_notes[@]}"} \
  ${rel_stack_audits[@]+"${rel_stack_audits[@]}"} \
  ${rel_status_guard[@]+"${rel_status_guard[@]}"} \
  ${rel_objective_evidence[@]+"${rel_objective_evidence[@]}"} \
  ${rel_batch_briefs[@]+"${rel_batch_briefs[@]}"} \
  ${rel_batch_hunts[@]+"${rel_batch_hunts[@]}"} \
  portable/main-default-branch \
  portable/path-c-applied-bundle \
  portable/pr2-landing \
  portable/patches/MANIFEST.json \
  portable/patches \
  scripts/audit_main_alignment.py \
  scripts/audit_local_tree.py \
  scripts/audit_research_stack_open.py \
  scripts/guard_no_status_promotion.py \
  scripts/alignment_status.py \
  scripts/watch_main_alignment.py \
  scripts/aligned_drift_watch.py \
  scripts/when_writable_land.py \
  scripts/validate_land_workflows.py \
  scripts/check_autonomous_window.py \
  scripts/probe_main_write.py \
  scripts/probe_main_write_vectors.py \
  scripts/path_b_dry_run.py \
  scripts/path_c_dry_run.py \
  scripts/path_c_rebase_helper.sh \
  scripts/refresh_restore_plan.py \
  scripts/print_owner_unblock.sh \
  scripts/restore_main_face.sh \
  scripts/owner_land_path_a.sh \
  scripts/owner_land_path_b.sh \
  scripts/owner_land_path_c.sh \
  scripts/pack_portable.sh \
  scripts/wait_until_aligned.sh
echo "wrote $OUT ($(wc -c <"$OUT") bytes; ${#rel_restore[@]} restore plans; ${#rel_tokens[@]} token logs; ${#rel_rebase[@]} rebase reports; ${#rel_rebase_notes[@]} rebase notes; ${#rel_stack_audits[@]} stack audits; ${#rel_status_guard[@]} status guards; ${#rel_objective_evidence[@]} objective evidence; ${#rel_batch_briefs[@]} briefs; ${#rel_batch_hunts[@]} hunts)"
