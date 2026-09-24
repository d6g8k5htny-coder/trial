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

echo "=== Batch 137 — PERMANENT window; ALIGNED @ 1c6e74b (PR #41); Path C BASE_TIP ${BASE_TIP_SHORT}; owner ONE-SHOT --from-bundle; unrestricted/auto-approve; HOLD VOID ==="
echo "Owner: NO restrictions; agents decide. HOLD on PR #2 is VOID."
echo "Dylan: 48h extended permanently until he intervenes — no 48h finale."
echo "Window: $ROOT/scripts/check_autonomous_window.py  # PERMANENT_UNTIL_OWNER_INTERVENES"
echo "Watch (embeds window+route): $ROOT/scripts/watch_main_alignment.py"
echo "ALIGNED drift watch: $ROOT/scripts/aligned_drift_watch.py  # exit 0/1/2; snapshot; --restore-if-writable"
echo "Background lander: $ROOT/scripts/when_writable_land.py  # poll 300s; Path C when writable+ALIGNED; Path B if MISALIGNED"
echo "  tmux: when-writable-land  |  status: /cursor/stores/self/when_writable_land.status.json"
echo "  log: /tmp/cursor/when_writable_land.log  |  STOP: /cursor/stores/self/when_writable_land.stop"
echo "  token: env MAIN_PUSH_TOKEN | /cursor/stores/self/MAIN_PUSH_TOKEN | /workspace/.secrets/MAIN_PUSH_TOKEN | /tmp/gh-dylan-auth/access_token"
echo "  once dry: python3 scripts/when_writable_land.py --once --dry-run"
echo "Device login (Dylan): $ROOT/portable/GH_DEVICE_LOGIN.md  # https://github.com/login/device + current user code"
if [[ -f "$ROOT/portable/GH_DEVICE_LOGIN.md" ]]; then
  echo "  $(grep -E '^\\| User code|^\\| Status|^\\| Verification' "$ROOT/portable/GH_DEVICE_LOGIN.md" | tr '\n' ' ')"
fi
echo "App install (Cursor): GitHub → Settings → Applications → Cursor → add d6g8k5htny-coder/main Read+write"
echo "  (until then install_has_main=false; device user token still can Path C — ignore install_has_main)"
echo "Relaunch / scope: $ROOT/portable/RELAUNCH_WITH_MAIN_SCOPE.md  # (a) App (b) device (c) MAIN_PUSH_TOKEN (d) RELAUNCH — mid-flight cannot gain main"
echo "Status guard (Batch 86; fail on OPEN→closed/promoted): $ROOT/scripts/guard_no_status_promotion.py <hardening-checkout>"
echo "  baseline: portable/BATCH70_RESEARCH_STACK_AUDIT.json or portable/STATUS_GUARD_SNAPSHOT.json"
echo "  CI job: research-stack-status-guard (continue-on-error; artifact STATUS_GUARD_SNAPSHOT)"
echo "Env write intent: .cursor/environment.json repositoryDependencies → main; relaunch Cloud Agent AFTER merge"
echo "  snapshot: portable/ALIGNED_DRIFT_SNAPSHOT.json  |  release: batch142-path-c-bundle"
echo "Path C ONE-SHOT (owner laptop): gh release download batch142-path-c-bundle -R d6g8k5htny-coder/trial -p 'trial-portable-main-fixes.tgz'"
echo "  then: tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land && /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle"
echo "Timer: re-arm permanent-autonomous-align-watch @ 10800s + gh-dylan-device-auth-check @ 300s (single; no gh-device-login-check dup)."
echo "PR #41 renewed default tip to 1c6e74b (ALIGNED). ALIGNED can revert (#32 history) — keep Path B ready."
echo "Path A OR Path B OK when MISALIGNED. Prefer Path B (Option-B README+AGENTS)."
echo "One-command: $ROOT/scripts/restore_main_face.sh  # short-circuits when already ALIGNED"
echo "Path C BASE_TIP file: $BASE_TIP_LINE"
echo "Path C owner git am (no agent write token): $ROOT/portable/path-c-applied-bundle/APPLY.md"
echo "  patch: $ROOT/portable/path-c-applied-bundle/path-c-on-hardening.patch"
echo "  verify: $ROOT/portable/path-c-applied-bundle/VERIFY.json  # problems=0 lemma_closed=false focused 90/0"
echo "Path C: $ROOT/scripts/owner_land_path_c.sh --dry-run  # APPLY_READY on hardening BASE_TIP ${BASE_TIP_SHORT}"
echo "Path C Actions: $ROOT/.github/workflows/land-path-c-on-main.yml  # dry_run default true; MAIN_PUSH_TOKEN for land"
echo "  gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=true"
echo "  gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo "CI (no token): land-workflows-dry-run job — validate_land_workflows.py + actionlint + owner --help/--dry-run"
echo "  $ROOT/scripts/validate_land_workflows.py  # dry_run default true; MAIN_PUSH_TOKEN not required"
echo "Path C stays on chatgpt/drive-github-hardening-20260919 (has PACKET.json; rebase onto main CONFLICTS)."
echo "Rebase conflict paths: portable/PATH_C_REBASE_CONFLICT_REPORT_67.json (ci.yml, research.yml, bridge README)."
echo "Rebase helper: $ROOT/scripts/path_c_rebase_helper.sh --dry-run  # prefer abort; never invent research status"
echo "Resolution notes: portable/PATH_C_REBASE_RESOLUTION_NOTES_68.json"
echo "Post-#41: do NOT PATH_C_BASE=main (ALIGNED landing lacks PACKET.json)."
echo "Batch 132: research audit OPEN premises=13 lemmas=1 prizes=3 @ c82c9357; when_writable_land loads dylan device token; write DENIED; no 0017."
echo "pack_portable.sh auto-globs RESTORE_PLAN_* + BATCH*_TOKEN_SEARCH + PATH_C_REBASE_* + BATCH*_RESEARCH_STACK_AUDIT + STATUS_GUARD_SNAPSHOT + ALIGNED_DRIFT_SNAPSHOT + validate_land_workflows (Batch 64+/67+/68+/70+/72+/73+/74+/86)."
echo "Research-stack OPEN audit (Batch 70/132; read-only; no flips): $ROOT/scripts/audit_research_stack_open.py <checkout>"
echo "  artifact: portable/BATCH132_RESEARCH_STACK_AUDIT.json  |  docs/MECHANICAL_FINDINGS_MAIN.md"
echo "Scientific effect: NONE"
echo

echo "=== OWNER_ONE_LINERS (paths) ==="
echo "  $ROOT/portable/OWNER_ONE_LINERS.md"
echo "  $ROOT/portable/LAND.md"
echo "  $ROOT/docs/OWNER_ACTIONS_MAIN.md"
echo "  $ROOT/.github/workflows/land-option-b-on-main.yml"
echo "  $ROOT/.github/workflows/land-path-c-on-main.yml"
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
echo "$ROOT/scripts/aligned_drift_watch.py  # exit 0/1/2; --restore-if-writable"
echo "$ROOT/scripts/when_writable_land.py --once --dry-run"
echo "$ROOT/scripts/when_writable_land.py  # background; tmux when-writable-land"
echo "# Path C — engineering: apply_all 0001–0004 + 0008–0016 on hardening tip:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh --from-bundle  # ONE-SHOT from release tarball"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Path A — HOLD VOID; default PATH_A_MODE=revert32 (or ready_merge for a fresh OPEN port PR):"
echo "$ROOT/scripts/owner_land_path_a.sh"
echo
echo "=== copy-paste Path C (needs write on main) ==="
echo "# dry-run first (no write); then land on hardening BASE_TIP — avoid PATH_C_REBASE_ONTO_MAIN post-#41:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh --from-bundle"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# or Actions (trial secret MAIN_PUSH_TOKEN):"
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-path-c-on-main → Run workflow → dry_run=false"
echo "gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=true"
echo "gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo "# or: $ROOT/portable/patches/apply_all.sh on a writable hardening tip checkout"
echo
echo "=== copy-paste Path B (optional) ==="
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "# 2) Actions → land-option-b-on-main → Run workflow → dry_run=false"
echo "gh workflow run land-option-b-on-main --repo d6g8k5htny-coder/trial -f dry_run=false"
echo
echo "Scientific effect: NONE"
