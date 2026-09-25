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

# Batch 257: header used to freeze Batch 169 / tip 1c6e74b / "write DENIED" while
# portable/PATH_C_STATUS.json already reported WRITABLE @ fa32d11. Prefer live status
# (never print tokens / raw device secrets beyond existing GH_DEVICE_LOGIN paths).
STATUS_FILE="$ROOT/portable/PATH_C_STATUS.json"
WRITE_STATE="UNKNOWN"
STATUS_TIP="$BASE_TIP_SHORT"
IDLE_STATUS=""
STATUS_GEN=""
if [[ -f "$STATUS_FILE" ]]; then
  eval "$(python3 -c '
import json,shlex,sys
from pathlib import Path
p=Path(sys.argv[1])
try:
    d=json.loads(p.read_text(encoding="utf-8"))
except Exception:
    d={}
def emit(k,v):
    if v is None:
        v=""
    print(f"{k}={shlex.quote(str(v))}")
emit("WRITE_STATE", d.get("write_state") or "UNKNOWN")
emit("STATUS_TIP", (d.get("tip") or d.get("base_tip") or "")[:7])
emit("IDLE_STATUS", d.get("idle_status") or "")
emit("STATUS_GEN", d.get("generated_at") or "")
' "$STATUS_FILE")"
fi
[[ -n "$STATUS_TIP" ]] || STATUS_TIP="$BASE_TIP_SHORT"

echo "=== Batch 353 — PERMANENT window; Path C BASE_TIP ${BASE_TIP_SHORT}; write ${WRITE_STATE}; tip ${STATUS_TIP}${IDLE_STATUS:+; idle ${IDLE_STATUS}}; unrestricted/auto-approve; HOLD VOID ==="
echo " Batch 353: inventory tip re-pin→HEAD after eng living republish (preserve_durable)"
echo " Batch 353: eng living script_stale republish after research-audit merge (batch241; script_stale 1→0)"
echo " Batch 353: research_stack_audit_watch — open stack 13/1/3; STATUS_GUARD living @e3cd7d4; no promotion"
echo " Batch 353: inventory tip re-pin→HEAD after living republish (preserve_durable)"
echo " Batch 353: living script_stale republish + inventory tip pin→HEAD @e3cd7d4"
echo " Batch 353: wake Path C peers (tip watch, eng hunt, inventory, research audit)"
echo " Batch 353: tip_sync_watch idle @e3cd7d4 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 353: inventory_preserve_durable_tip_pin @e3cd7d4 (trial→HEAD; never demote 8/8 on writable=0 DENIED)"
echo " Batch 352: ci_audit_watch idle — CI green @e3cd7d4 (INV_TIP soften + EARLY_FALLBACK isolate)"
echo " Batch 352: tip_or_eng inv tip re-pin + living script_stale republish @e3cd7d4"
echo " Batch 352: inventory_preserve_durable_tip_pin re-pin @e3cd7d4 (trial→HEAD; never demote 8/8 on writable=0)"
echo " Batch 352: MULTI_AGENT wake+assign stopped agents @e3cd7d4 (WAKE352; Dylan message-stopped-agents)"
echo " Batch 352: grant_check_dual_vector_8of8 tip refresh @e3cd7d4 (BATCH352_GRANT; preserve_durable)"
echo " Batch 352: living script_stale republish after inv tip-pin (batch241; script_stale 1→0)"
echo " Batch 352: unfreeze inventory/wake/REFRESH last-resort 351→352 (coordinator wake; tip stable @e3cd7d4)"

echo " Batch 352: tip_sync_watch idle @e3cd7d4 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 352: inventory_preserve_durable_tip_pin @e3cd7d4 (trial→HEAD; never demote 8/8 on writable=0 DENIED)"
echo " Batch 351: idle_no_commit tip-stable watch @e3cd7d4 (tip_match; NOT 077464e; living tip/script current; paper-trail tgz)"
echo " Batch 351: research_stack_audit_watch — STATUS_GUARD living @e3cd7d4; eng living script_stale republish"
echo " Batch 351: inventory_preserve_durable_tip_pin @e3cd7d4 (trial→HEAD; never demote 8/8 on writable=0 DENIED)"
echo " Batch 350: soften INV_TIP_PIN Intent action allowlist (peer re-pin rename)"
echo " Batch 351: inventory tip pin after Batch 350 idle (preserve_durable; batch322-soon timer)"
echo " Batch 350: idle_no_commit tip-stable watch @e3cd7d4 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 350: inventory tip pin after Batch 349 lands (preserve_durable; trial→HEAD)"
echo " Batch 349: eng_defect_hunt idle_no_commit @e3cd7d4 (tip_match; no concrete eng; lemma_closed=false)"
echo " Batch 349: CI Intent EARLY_FALLBACK isolate in rate-limit unit tests + soften GRANT345 action pin"
echo " Batch 349: inventory tip pin after Batch 348 lands (preserve_durable)"
echo " Batch 348: research_stack_audit_watch — STATUS_GUARD no lag @e3cd7d4; eng living script_stale republish + inv tip pin"
echo " Batch 348: idle_no_commit tip-stable watch @e3cd7d4 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 348: inventory tip pin after Batch 347 lands (preserve_durable; trial→HEAD f00459d)"
echo " Batch 348: research stack audit WITHOUT promotion @e3cd7d4 (open_premises=13; lemma_closed=false)"
echo " Batch 347: soften Batch 346 wake Intent live tip pin (e3cd7d4); tip stable @e3cd7d4"
echo " Batch 347: tip_sync_watch idle @e3cd7d4 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 347: inventory tip pin after Batch 346 lands (preserve_durable; trial→HEAD a136c2d)"
echo " Batch 346: living script_stale republish after tip-stable @e3cd7d4 (batch241; script_stale 1→0)"
echo " Batch 346: ci_audit_watch idle — early-fallback intact @e3cd7d4; no new CI eng class"
echo " Batch 346: inventory_preserve_durable_tip_pin @e3cd7d4 (trial→HEAD; ultimate fallback 346; never demote 8/8 on writable=0 DENIED)"
echo " Batch 346: STATUS_GUARD tip refresh fcad723→e3cd7d4 after tip-sync (guard pass; no promotion)"
echo " Batch 346: grant_check_dual_vector_8of8 tip refresh @e3cd7d4 (BATCH346_GRANT; preserve_durable)"
echo " Batch 346: MULTI_AGENT wake+assign stopped agents @e3cd7d4 (WAKE346; Dylan message-stopped-agents)"
echo " Batch 346: wake/inventory ultimate fallback return \"346\" (was frozen 345 after WAKE346)"
echo " Batch 346: soften Batch 345 tip_sync_watch Intent live BASE_TIP pin (e3cd7d4); tip stable @e3cd7d4"
echo " Batch 345: tip-sync fcad723→e3cd7d4 after main #105 CONTRIBUTION_PLAN retire (keep-prior; NOT promoted); REFRESH default 345"
echo " Batch 345: tip-sync fcad723→e3cd7d4 (keep-prior; inventable NOT promoted)"
echo " Batch 345: inventory tip pin after tip-sync e3cd7d4 (preserve_durable; trial→HEAD)"
echo " Batch 345: inventory ultimate fallback return \"345\" (was 343 after tip-sync REFRESH 345)"
echo " Batch 343: audit Intent timeout early-fallback (rate-limit reset sleep→raw; CI 36176016910)"
echo " Batch 345: wake ultimate fallback return \"345\" (was frozen 341); single living print_owner header (was dual 344+345)"
echo " Batch 345: MULTI_AGENT wake+assign stopped agents (WAKE345; batch329 timer)"
echo " Batch 343: audit Intent timeout early-fallback (rate-limit reset sleep→raw; CI 36176016910)"
echo " Batch 344: soften Batch 343 tip_sync_watch Intent live BASE_TIP pin (fcad723); tip stable @fcad723"
echo " Batch 344: tip_sync_watch idle @fcad723 (tip_match; living tip/script current; paper-trail tgz)"
echo " Batch 343: STATUS_GUARD tip refresh f244312→fcad723 after tip-sync (guard pass; no promotion)"
echo " Batch 344: idle_no_commit tip-stable watch @fcad723 (batch327 timer pulse)"
echo " Batch 343: inventory ultimate fallback return \"343\" (was frozen 340 after tip-sync REFRESH 343); soften Batch 340 Intent hard pin"
echo " Batch 343: grant inventory tip refresh batch 343 (preserve durable 8/8 on writable=0)"
echo " Batch 343: living script_stale republish after tip-stable watch @f244312"
echo " Batch 343: MULTI_AGENT wake+assign stopped agents (WAKE343)"
echo " Batch 343: WAKE343/340 living tip pins refreshed f244312→fcad723 (wake_tip_at_assign preserved)"
echo " Batch 342: inventory tip refresh batch 342 + soften wake-token Intent live tip pin"
echo " Batch 341: soften Batch 340 Intent living INV_BATCH hard pin after Batch 342 tip-refresh (CI red == \"340\" vs living 342)"
echo " Batch 341: grant inventory tip refresh @f244312 (BATCH341_GRANT; preserve_durable)"
echo "Owner: NO restrictions; agents decide. HOLD on PR #2 is VOID."
echo "Dylan: 48h extended permanently until he intervenes — no 48h finale."
echo "Live PATH_C_STATUS: write_state=${WRITE_STATE} tip=${STATUS_TIP} base_tip=${BASE_TIP_SHORT}${STATUS_GEN:+ generated_at=${STATUS_GEN}} (see portable/PATH_C_STATUS.json; never print tokens)"
echo "Window: $ROOT/scripts/check_autonomous_window.py  # PERMANENT_UNTIL_OWNER_INTERVENES"
echo "Path C ONE-SHOT (Batch 165+): $ROOT/scripts/owner_path_c_oneshot.sh --dry-run"
echo "  token → owner_open_path_c_pr.sh (else owner_land_path_c.sh); no token → unblock menu"
echo "  live: $ROOT/scripts/owner_path_c_oneshot.sh"
echo "  from-bundle: $ROOT/scripts/owner_path_c_oneshot.sh --from-bundle  # prefers .bundle fetch+merge"
echo "  release: batch241-path-c-bundle (prior batch239-path-c-bundle / batch236-path-c-bundle) (.bundle + .patch + oneshot+refresh+PATH_C_STATUS+watch/readme link-only; PATH_C_RELEASE_TAG override ok; prior batch223-path-c-bundle / batch218-path-c-bundle / batch199-path-c-bundle / batch180-path-c-bundle / batch179-path-c-bundle / batch169-path-c-bundle / batch168-path-c-bundle)"
echo "Tip refresh helper (Batch 173/176): $ROOT/scripts/refresh_path_c_bundle.sh  # tip fetch → BASE_TIP → apply_all → .patch+.bundle → VERIFY.json"
echo "  dry-run: $ROOT/scripts/refresh_path_c_bundle.sh --dry-run  # exit 0 tip-stable / 1 TIP_DRIFT (+ fix-path); CI tip-drift dry-sim"
echo "  force rebuild: $ROOT/scripts/refresh_path_c_bundle.sh --force"
echo "Ready assert: $ROOT/scripts/assert_path_c_ready.sh"
echo "Watch (embeds window+route): $ROOT/scripts/watch_main_alignment.py"
echo "ALIGNED drift watch: $ROOT/scripts/aligned_drift_watch.py  # exit 0/1/2; snapshot; --restore-if-writable"
echo "Background lander: $ROOT/scripts/when_writable_land.py  # poll 300s; Path C when writable+ALIGNED; Path B if MISALIGNED"
echo "  tmux: when-writable-land  |  status: /cursor/stores/self/when_writable_land.status.json"
echo "  once sidecar (Batch 267/270; when daemon lock held or lockfile pid= live): /cursor/stores/self/when_writable_land.once.status.json"
echo "  daemon lock: /cursor/stores/self/when_writable_land.status.json.daemon.lock  # second loop → exit 2 (flock or pid-liveness)"
echo "  log: /tmp/cursor/when_writable_land.log  |  STOP: /cursor/stores/self/when_writable_land.stop"
echo "  token: env MAIN_PUSH_TOKEN | /cursor/stores/self/MAIN_PUSH_TOKEN | /workspace/.secrets/MAIN_PUSH_TOKEN | /tmp/gh-dylan-auth/access_token"
echo "  set trial secret (Batch 160): $ROOT/scripts/owner_set_main_push_token.sh --dry-run"
echo "    then: MAIN_PUSH_TOKEN=… $ROOT/scripts/owner_set_main_push_token.sh --dispatch  # gh secret set + land-path-c dry_run=false"
echo "    or: $ROOT/scripts/owner_set_main_push_token.sh --from-gh --dispatch  # uses gh auth token (never printed)"
echo "  once dry: python3 scripts/when_writable_land.py --once --dry-run"
echo "Device login (Dylan): $ROOT/portable/GH_DEVICE_LOGIN.md  # https://github.com/login/device + current user code"
if [[ -f "$ROOT/portable/GH_DEVICE_LOGIN.md" ]]; then
  echo "  $(grep -E '^\\| User code|^\\| Status|^\\| Verification' "$ROOT/portable/GH_DEVICE_LOGIN.md" | tr '\n' ' ')"
fi
echo "App install (Cursor): GitHub → Settings → Applications → Cursor → add ALL owner repos Read+write"
echo "  Multi-agent oneshot (Batch 224): $ROOT/scripts/owner_grant_ai_agent_access.sh  # Cursor+Codex+Claude+Grok PAT; 8 repos incl. sandbox"
echo "  Docs: $ROOT/docs/MULTI_AGENT_ACCESS.md  |  Inventory: $ROOT/portable/AI_AGENT_ACCESS_INVENTORY.json"
echo "  On App UIs: select ALL repositories including sandbox"
echo "  (until then install_has_main=false; sandbox 404; device user token still can Path C — ignore install_has_main)"
echo "Relaunch / scope: $ROOT/portable/RELAUNCH_WITH_MAIN_SCOPE.md  # (a) App (b) device (c) MAIN_PUSH_TOKEN (d) RELAUNCH — mid-flight cannot gain main"
echo "Status guard (Batch 86/263; fail on OPEN→closed/promoted): $ROOT/scripts/guard_no_status_promotion.py <hardening-checkout>"
echo "  baseline: portable/BATCH70_RESEARCH_STACK_AUDIT.json or portable/STATUS_GUARD_SNAPSHOT.json"
echo "  Batch 263: NO_PACKET vs shape-stripped HAS_PACKET → exit 2 (usage), not false promotions"
echo "  Batch 264: Path B dry-run ALREADY_ALIGNED ⇒ land_needed=false; owner_land_path_b --dry-run idles (no re-run-to-land lie)"
echo "  Batch 265: Batch 262 live-ignore Intent CI-isolates Actions GITHUB_TOKEN (token_source≠env:GITHUB_TOKEN flake)"
echo "  Batch 266: path_c_dry_run IDLE ⇒ write_required_to_land=false; living stack prose 0008–0019 (not stale 0017)"
echo "  Batch 267: when_writable dual-daemon status race → daemon.lock flock + --once sidecar (no leftover --dry-run loop)"
echo "  Batch 324: print_owner Path C line follows PATH_C_LANDED_TIP_DRIFT → refresh_path_c_bundle (pre-324 fell through to APPLY_READY land lie; Batch 261 IDLE-only leftover)"
echo " Batch 327: VERIFY refresh_batch after keep-prior WORKDIR force; pack+CRITICAL include post_batch322_wake_comments.py"
echo "  Batch 329: republish CRITICAL includes print_owner_unblock.sh (Batch 324 tip-drift Path C line was pack-only; living release could stay APPLY_READY-stale with tip_stale=0)"
echo "  Batch 328: inventory refresh INV_BATCH derives from print_owner header (was frozen 323)"
echo "  Batch 329: living tip_refresh assert (Batch 289 CI red after non-tip refresh_batch); MULTI_AGENT_WAKE_BATCH329"
echo " Batch 330: no_token tip-refresh preserves durable 8/8 (DURABLE_SANDBOX_WRITE=n/a)"
echo " Batch 331: grant --check skips inventory refresh when durable_token_source=none"
echo " Batch 332: tip-sync 077464e→388a22c after main #97 inventable (keep-prior; NOT promoted)"
echo " Batch 333: republish release-view retry on rate-limit; STATUS_GUARD tip @388a22c"
echo " Batch 334: grant skip inventory refresh only when durable_token_source=none (not writable=0)"
echo " Batch 335: tip-sync 388a22c→eeebb28 after main #99/#100 (keep-prior; NOT promoted)"
echo " Batch 336: wake poster INTENT tip derives from BASE_TIP (was frozen @077464e); preserve durable inventory on writable=0 DENIED; inventory REFRESH_BATCH_TAG fallback; soften 335 live tip pins; MULTI_AGENT_WAKE"
echo " Batch 337: tip stable @eeebb28 tip_match=1; MULTI_AGENT wake assign; research stack audit open (lemma_closed=false); idle_no_commit"
echo " Batch 337: tip-sync eeebb28→848aea2 after main #101/#107/#102 (keep-prior; NOT promoted; supersedes idle pulse)"
echo " Batch 338: post-Path-C align watch idle @848aea2 tip_match=1; lemma_closed=false"
echo " Batch 338: wake poster skip gate keys off living BASE_TIP (was frozen Batch 329 wake → eng PRs stuck @077464e)"
echo " Batch 340: MULTI_AGENT wake+assign stopped agents @848aea2; Path C IDLE@0019; lemma_closed=false"
echo " Batch 339: living script_stale republish after tip-stable watch @848aea2"
echo " Batch 340: republish CRITICAL includes audit_main_alignment; audit rate-limit/raw fallback; inventory ultimate batch fallback unfrozen (was frozen 336); MULTI_AGENT wake+assign"
echo " Batch 340: audit_main_alignment 403 rate-limit backoff + raw/ls-remote fallback; CI soft-continue transport exit 2"
echo " Batch 341: soften Batch 340 tip-sync Intent live BASE_TIP pin (f244312); living tgz republish after tip-sync"
echo " Batch 341: wake _living_batch_n from print_owner (was frozen _WAKE_BATCH=340); STATUS_GUARD tip→f244312"
echo " Batch 341: grant inventory tip refresh @f244312 (BATCH341_GRANT; preserve_durable)"
echo " Batch 340: inventory ultimate fallback return \"340\" (was frozen 336); REFRESH default 340"
echo " Batch 340: wake poster loads durable MAIN_PUSH_TOKEN files (MAIN first + grant/when_writable drops; App ghs Issues:write)"
echo " Batch 340: tip-sync 848aea2→f244312 after main #108 inventable tip-observe (keep-prior; NOT promoted)"
echo " Batch 340: audit_main_alignment 403 rate-limit backoff; grant inventory tip refresh batch 340 (preserve durable 8/8)"
echo " Batch 341: research stack audit WITHOUT promotion @f244312 (open_premises=13; inventable drafts skipped; eng-only #36/#21/#12 noted; lemma_closed=false)"
echo " Batch 342: WAKE340 tip pins refreshed 848aea2→living f244312 (wake_tip_at_assign preserved)"
echo " Batch 342: inventory tip refresh batch 342 + soften wake-token Intent live tip pin"
echo " Batch 343: living script_stale republish after tip-stable watch @f244312 (print_owner drift after 341/342)"
echo " Batch 343: tip-sync f244312→fcad723 after main #109 (keep-prior; NOT promoted)"
echo " Batch 328: inventory refresh INV_BATCH derives from print_owner header (was frozen 323)"
echo "  Batch 323: grant --check refreshes AI_AGENT_ACCESS_INVENTORY via refresh_ai_agent_access_inventory.py (pre-323 pointer drifted; sandbox.tip vs details); pack+CRITICAL include helper"
echo "  Batch 321: soften Batch 317 live BASE_TIP/VERIFY/PATH_C tip Intent pins to _living_tip; refresh AI_AGENT_ACCESS_INVENTORY tip_sha from durable 8/8"
echo "  Batch 317: tip-sync 0adeb65→077464e after main #89 tip-observe mid-cycle; refresh keep-prior; living tip_stale republish; REFRESH default 317"
echo "  Batch 305: tip-sync 02cfbfd→0adeb65 after main #85 inventable mid-cycle; refresh keep-prior; living tip_stale republish; REFRESH default 305"
echo "  Batch 297: tip-sync 3a29f52→02cfbfd after main #84 tip-observe mid-cycle; refresh keep-prior; living tip_stale republish; REFRESH default 297"
echo "  Batch 289: tip-sync 7d13a88→3a29f52 after main #83 nav inventable mid-cycle; refresh keep-prior; living tip_stale republish; REFRESH default 289"
echo "  Batch 288: republish CRITICAL includes when_writable_land.py (287 fixed lander list-gate but CRITICAL could not detect when_writable-only drift; living release also still lacked 287 probe/refresh → script_stale=1); REFRESH default 288"
echo "  Batch 287: probe_main_write / when_writable require isinstance(repositories, list) (Batch 286 fixed grant only; null/non-list still collapsed via or [] → false empty install_has_main); REFRESH default 287"
echo "  Batch 286: grant --check requires isinstance(repositories, list) (null/non-list ≠ empty install); republish script_stale compares critical script sha256 vs living pack (post-285 tip_match left release without grant fix); Intent REFRESH_BATCH_TAG uses >= not allowlist"
echo "  Batch 285: grant --check treats user-token 403 JSON on /installation/repositories as unavailable (pre-285 empty listing → false install_missing_from_deps=all8 while 8/8 WRITABLE)"
echo "  Batch 283: republish tip_stale when living release BASE_TIP lags local (byte-growth-only missed tip-sync 3b3860d→7d13a88; release lacked grant)"
echo "  Batch 282: pack_portable includes owner_grant_ai_agent_access.sh + AI_AGENT_ACCESS_INVENTORY.json (OWNER_ONE_LINERS referenced grant 8× but tarball omitted it post-281)"
echo "  Batch 281: grant --check durable ls-remote uses token (pre-281 bare https → private sandbox ls_remote=not_found_or_denied while write=WRITABLE)"
echo "  Batch 280: probe_main_write_vectors W2 contents PUT creates throwaway ref first (pre-280 PUT-only → false DENIED 404 Branch not found while W1 WRITABLE)"
echo "  Batch 279: republish stages canonical trial-portable-main-fixes.tgz basename + post-upload size/sha verify (pre-279 --out foo.tgz left living pack stale while printing uploaded OK)"
echo "  Batch 278: pack_portable -h/--help not OUT; refresh APPLY soft-update <<'PY' (Batch 273 leftover); tip-sync bfb7c38→3b3860d"
echo "  Batch 277: owner oneshot/open_pr VERIFY.release-first (Batch 276 leftover preferred dirty living pin → wrong PR release URL)"
echo "  Batch 276: republish living-tag post-pack (pre-pack stale pin → wrong upload target); write_path_c_status VERIFY.release-first"
echo "  Batch 275: refresh MANIFEST.verified_batch release-align from VERIFY.batch (Batch 269 leftover stamped BATCH_TAG); refresh_batch=automation; default tag 275"
echo "  Batch 273: refresh keep-prior APPLY living-tip soft-update + VERIFY pytest preserve (Batch 272 left 542e6ec==(BASE_TIP) lie + focused 0)"
echo "  Batch 272: land-workflows-dry-run Path C idle must match on path-c-dry-run.out alone (union grep only saw Path B ALREADY_ALIGNED)"
echo "  Batch 271: probe_main_write_vectors W3a–W3e dry_run ⇒ DISPATCH_OK_DRY_RUN false_positive; path_b_keys=W1/W2/W4* only (Batch 141 W3f-only leftover)"
echo "  Batch 270: when_writable --once pid-liveness when flock misses live lockfile pid= (sidecar; no shared-status clobber)"
echo "  Batch 269: refresh_path_c_bundle VERIFY.batch aligned to release (was stale 250 vs batch241); refresh_batch automation stamp; no 0020"
echo "  Batch 268: pack_portable living-tag validate-before-write + tip refresh fa32d11→8e359e5 (no 0020; no dirty pin on mismatch)"
echo "  CI job: research-stack-status-guard (continue-on-error; artifact STATUS_GUARD_SNAPSHOT)"
echo "Env write intent: .cursor/environment.json repositoryDependencies → main; relaunch Cloud Agent AFTER merge"
echo "  snapshot: portable/ALIGNED_DRIFT_SNAPSHOT.json  |  release: batch241-path-c-bundle"
echo "Path C ONE-SHOT (owner laptop): gh release download batch241-path-c-bundle -R d6g8k5htny-coder/trial -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle'"
echo "  then: tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land && /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle"
echo "Timer: re-arm permanent-autonomous-align-watch @ 10800s + gh-dylan-device-auth-check @ 1800s (preferred_auth_interval_s=1800; single; no dup)."
echo "PR #41 renewed default tip (ALIGNED). Current default tip may be newer — keep Path B ready if ALIGNED reverts (#32 history)."
echo "Path A OR Path B OK when MISALIGNED. Prefer Path B (Option-B README+AGENTS)."
echo "One-command: $ROOT/scripts/restore_main_face.sh  # short-circuits when already ALIGNED"
echo "Path C BASE_TIP file: $BASE_TIP_LINE"
echo "Path C owner git am (no agent write token): $ROOT/portable/path-c-applied-bundle/APPLY.md"
echo "  patch: $ROOT/portable/path-c-applied-bundle/path-c-on-hardening.patch"
echo "  git bundle (Batch 169 preferred): $ROOT/portable/path-c-applied-bundle/path-c-on-hardening.bundle"
echo "    git fetch …/path-c-on-hardening.bundle cursor/portable-engineering-patches && git merge --ff-only FETCH_HEAD"
# Batch 282: focused count from VERIFY.json (pre-282 hardcoded 90/0 while living tip recount is 92).
VERIFY_FOCUSED="?"
VERIFY_JSON="$ROOT/portable/path-c-applied-bundle/VERIFY.json"
if [[ -f "$VERIFY_JSON" ]]; then
  VERIFY_FOCUSED="$(
    python3 -c '
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
p = d.get("pytest") or {}
fp = p.get("focused_passed")
rw = p.get("focused_resource_warnings")
fp_s = "?" if fp is None else str(fp)
rw_s = "?" if rw is None else str(rw)
print(f"{fp_s}/{rw_s}")
' "$VERIFY_JSON" 2>/dev/null || echo '?/?'
  )"
fi
echo "  verify: $ROOT/portable/path-c-applied-bundle/VERIFY.json  # problems=0 lemma_closed=false focused ${VERIFY_FOCUSED}"
# Batch 261: do not hardcode APPLY_READY when PATH_C_STATUS already idle.
# Batch 324: PATH_C_LANDED_TIP_DRIFT is also not APPLY_READY — Path C already
# landed; operators need tip-refresh (refresh_path_c_bundle), not land. Pre-324
# only matched IDLE_PATH_C_DONE and fell through to APPLY_READY on tip drift.
if [[ "${IDLE_STATUS}" == "IDLE_PATH_C_DONE" ]]; then
  echo "Path C: $ROOT/scripts/owner_land_path_c.sh --dry-run  # already-on-tip idle (IDLE_PATH_C_DONE) @ ${BASE_TIP_SHORT}; path_c_dry_run → idle not APPLY_READY"
elif [[ "${IDLE_STATUS}" == "PATH_C_LANDED_TIP_DRIFT" ]]; then
  echo "Path C: $ROOT/scripts/refresh_path_c_bundle.sh  # tip-drift (PATH_C_LANDED_TIP_DRIFT) BASE_TIP ${BASE_TIP_SHORT} != live tip ${STATUS_TIP}; refresh keep-prior — not APPLY_READY land"
elif [[ "${IDLE_STATUS}" == "PATH_C_LANDED" ]]; then
  echo "Path C: $ROOT/scripts/owner_land_path_c.sh --dry-run  # path_c_landed (PATH_C_LANDED) @ ${BASE_TIP_SHORT}; not APPLY_READY"
else
  echo "Path C: $ROOT/scripts/owner_land_path_c.sh --dry-run  # APPLY_READY on hardening BASE_TIP ${BASE_TIP_SHORT} (or idle when landed)"
fi
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
echo "Write live: ${WRITE_STATE} (from PATH_C_STATUS; probe below may confirm). Research audit stays OPEN; lemma_closed=false; no status flips."
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

echo "=== live probe / audit (durable file-token discovery; never prints secrets) ==="
echo "# Batch 262: probe_main_write(+vectors) load env OR well-known file tokens"
echo "#   (MAIN_PUSH_TOKEN / .secrets / /tmp/gh-dylan-auth/access_token) so live"
echo "#   section matches PATH_C_STATUS WRITABLE; PATH_C_IGNORE_FILE_TOKENS=1 skips files."
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
echo "# Path C — Batch 165 ONE-SHOT (token→open PR / land; else unblock menu):"
echo "$ROOT/scripts/owner_path_c_oneshot.sh --dry-run"
echo "$ROOT/scripts/owner_path_c_oneshot.sh"
echo "$ROOT/scripts/owner_path_c_oneshot.sh --from-bundle"
echo "# Path C — engineering: apply_all 0001–0004 + 0008–0019 on hardening tip:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh --from-bundle  # ONE-SHOT from release tarball"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Path C — owner PR from path-c-applied-bundle (Batch 151; branch cursor/path-c-portable-fixes):"
echo "$ROOT/scripts/owner_open_path_c_pr.sh --dry-run"
echo "$ROOT/scripts/owner_open_path_c_pr.sh  # git am bundle → push → PR into hardening"
echo "# Path A — HOLD VOID; default PATH_A_MODE=revert32 (or ready_merge for a fresh OPEN port PR):"
echo "$ROOT/scripts/owner_land_path_a.sh"
echo
echo "=== copy-paste Path C (needs write on main) ==="
echo "# Batch 165 ONE-SHOT (preferred entry):"
echo "$ROOT/scripts/owner_path_c_oneshot.sh --dry-run"
echo "$ROOT/scripts/owner_path_c_oneshot.sh"
echo "# dry-run first (no write); then land on hardening BASE_TIP — avoid PATH_C_REBASE_ONTO_MAIN post-#41:"
echo "$ROOT/scripts/owner_land_path_c.sh --dry-run"
echo "$ROOT/scripts/owner_land_path_c.sh --from-bundle"
echo "$ROOT/scripts/owner_land_path_c.sh"
echo "# Batch 151 owner PR (bundle am → cursor/path-c-portable-fixes → PR hardening):"
echo "$ROOT/scripts/owner_open_path_c_pr.sh --dry-run"
echo "$ROOT/scripts/owner_open_path_c_pr.sh"
echo "# or Actions (trial secret MAIN_PUSH_TOKEN):"
echo "# 1) Settings → Secrets → Actions → MAIN_PUSH_TOKEN (Contents:Write on main)"
echo "#    ONE-SHOT: $ROOT/scripts/owner_set_main_push_token.sh --dry-run"
echo "#             MAIN_PUSH_TOKEN=… $ROOT/scripts/owner_set_main_push_token.sh --dispatch"
echo "#             # or: $ROOT/scripts/owner_set_main_push_token.sh --from-gh --dispatch"
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
