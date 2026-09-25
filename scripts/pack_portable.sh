#!/usr/bin/env bash
# Build a tarball of the portable main-alignment pack for owner download.
#
# Batch 64+: auto-includes every portable/RESTORE_PLAN_*.json and
# portable/BATCH*_TOKEN_SEARCH.json so each batch need not edit this list.
#
# Batch 245+: living Path C release-tag automation — sync
# portable/LIVING_PATH_C_RELEASE_TAG from path-c-applied-bundle/VERIFY.json
# "release", fail closed if owner oneshot/open_pr :-defaults drift, and pack
# the living-tag file so downstream ONE-SHOT consumers share one tip pin.
#
# Batch 268: validate oneshot/open_pr :-defaults BEFORE writing the living pin.
# Pre-268 order wrote LIVING_PATH_C_RELEASE_TAG then fail-closed — a VERIFY.batch
# without matching release left the pin dirty (e.g. batch250) on exit 2, racing
# oneshot / write_path_c_status / republish readers. Never republish here.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Batch 251: default OUT must land somewhere writable. Local clones often use
# $ROOT/../trial-portable-main-fixes.tgz (sibling of the repo). Cloud Agent
# mounts the tree at /workspace, so $ROOT/.. is / and bare `./scripts/pack_portable.sh`
# failed with Permission denied (exit 2) — release publish blocked. Prefer the
# sibling when the parent dir is writable; otherwise ${TMPDIR:-/tmp}/….
_PACK_PARENT="$(cd "$ROOT/.." && pwd)"
if [[ -n "${1:-}" ]]; then
  OUT="$1"
elif [[ -w "$_PACK_PARENT" ]]; then
  OUT="$_PACK_PARENT/trial-portable-main-fixes.tgz"
else
  OUT="${TMPDIR:-/tmp}/trial-portable-main-fixes.tgz"
  echo "pack_portable: note: parent ${_PACK_PARENT} not writable; defaulting OUT=${OUT}" >&2
fi
mkdir -p "$(dirname "$OUT")"

# --- living release tag (Batch 245 + Batch 268 validate-before-write) --------
VERIFY_JSON="$ROOT/portable/path-c-applied-bundle/VERIFY.json"
LIVING_TAG_FILE="$ROOT/portable/LIVING_PATH_C_RELEASE_TAG"
# Derive only — do not mutate the pin yet (Batch 268).
LIVING_TAG="$(
  VERIFY_JSON="$VERIFY_JSON" LIVING_TAG_FILE="$LIVING_TAG_FILE" python3 - <<'PY'
import json, os, sys
from pathlib import Path

verify = Path(os.environ["VERIFY_JSON"])
living = Path(os.environ["LIVING_TAG_FILE"])
tag = None
if verify.is_file():
    try:
        data = json.loads(verify.read_text(encoding="utf-8"))
        rel = data.get("release")
        if isinstance(rel, str) and rel.endswith("-path-c-bundle"):
            tag = rel.strip()
        elif data.get("batch") is not None:
            tag = f"batch{data['batch']}-path-c-bundle"
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        tag = None
if not tag and living.is_file():
    try:
        cand = living.read_text(encoding="utf-8").strip()
        if cand.endswith("-path-c-bundle"):
            tag = cand
    except OSError:
        tag = None
if not tag:
    sys.stderr.write(
        "pack_portable: ERROR: cannot derive living Path C release tag "
        "from VERIFY.json (release|batch) or LIVING_PATH_C_RELEASE_TAG\n"
    )
    raise SystemExit(2)
print(tag)
PY
)" || exit $?

for _script in \
  "$ROOT/scripts/owner_path_c_oneshot.sh" \
  "$ROOT/scripts/owner_open_path_c_pr.sh"
do
  if [[ -f "$_script" ]]; then
    if ! grep -q "PATH_C_RELEASE_TAG=\"\${PATH_C_RELEASE_TAG:-${LIVING_TAG}}\"" "$_script"; then
      echo "pack_portable: ERROR: $_script :-default != living tag ${LIVING_TAG}" >&2
      echo "pack_portable: bump PATH_C_RELEASE_TAG fallback (and VERIFY.release) together" >&2
      echo "pack_portable: living pin NOT written (Batch 268 validate-before-write)" >&2
      exit 2
    fi
  fi
done

# Stamp living pin only after fail-closed defaults match (atomic replace).
LIVING_TAG="$LIVING_TAG" LIVING_TAG_FILE="$LIVING_TAG_FILE" python3 - <<'PY' || exit $?
import os
from pathlib import Path

tag = os.environ["LIVING_TAG"]
living = Path(os.environ["LIVING_TAG_FILE"])
living.parent.mkdir(parents=True, exist_ok=True)
tmp = living.with_name(living.name + ".tmp")
tmp.write_text(tag + "\n", encoding="utf-8")
tmp.replace(living)
PY
# ---------------------------------------------------------------------------

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
  portable/RELAUNCH_WITH_MAIN_SCOPE.md \
  portable/OWNER_ONE_LINERS.md \
  portable/CONFLICTING_PR_NOTES.md \
  portable/EXPECTED_POST_ALIGNMENT.json \
  portable/ALIGNED_DRIFT_SNAPSHOT.json \
  portable/PATH_C_STATUS.json \
  portable/LIVING_PATH_C_RELEASE_TAG \
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
  scripts/owner_open_path_c_pr.sh \
  scripts/owner_path_c_oneshot.sh \
  scripts/owner_set_main_push_token.sh \
  scripts/assert_path_c_ready.sh \
  scripts/write_path_c_status.py \
  scripts/refresh_path_c_bundle.sh \
  scripts/dispatch_land_path_c.sh \
  scripts/pack_portable.sh \
  scripts/republish_living_path_c_release.sh \
  scripts/wait_until_aligned.sh
echo "wrote $OUT ($(wc -c <"$OUT") bytes; living_tag=${LIVING_TAG}; ${#rel_restore[@]} restore plans; ${#rel_tokens[@]} token logs; ${#rel_rebase[@]} rebase reports; ${#rel_rebase_notes[@]} rebase notes; ${#rel_stack_audits[@]} stack audits; ${#rel_status_guard[@]} status guards; ${#rel_objective_evidence[@]} objective evidence; ${#rel_batch_briefs[@]} briefs; ${#rel_batch_hunts[@]} hunts)"
