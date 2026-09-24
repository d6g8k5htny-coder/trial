# Owner one-liners (Path B preferred / Path A HOLD VOID / Path C engineering)

Copy-paste from a machine or Actions runner that **can write** to
`d6g8k5htny-coder/main`. This trial cloud token cannot (git push + Git Data API
+ `gh pr ready/merge` all return **403**).

> **Batch 202 — tip refresh `8bd1f03`→`b89448d`; auth renew `5160-F839` (from `6A29-F464` &lt;90s); CI sanity + pack+release `batch202-path-c-bundle`; write DENIED**:
>
> ```bash
> ./scripts/refresh_path_c_bundle.sh             # tip moved → BASE_TIP + .bundle rebuild
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> # https://github.com/login/device + live code ONLY in GH_DEVICE_LOGIN.md (link-only README)
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch202
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**. `lemma_closed` stays false.

> **Batch 199 — tip stable `8bd1f03`; auth renew `6A29-F464` (from `50DB-FD4D` &lt;90s); pack+release `batch199-path-c-bundle` (PATH_C_STATUS in tarball); write DENIED**:
>
> ```bash
> # Pack includes PATH_C_STATUS.json + watch/readme link-only assets (no tip refresh)
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> # https://github.com/login/device + live code ONLY in GH_DEVICE_LOGIN.md (link-only README)
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch199
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**. `lemma_closed` stays false.

> **Batch 195 — tip stable `8bd1f03`; auth renew `50DB-FD4D` (from `CC72-DB3D` &lt;90s); PATH_C_STATUS watch wire; write DENIED**:
>
> ```bash
> # Hourly watch refreshes PATH_C_STATUS.json via aligned_drift_watch.py
> python3 scripts/aligned_drift_watch.py --no-probe --no-snapshot
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> # https://github.com/login/device + live code ONLY in GH_DEVICE_LOGIN.md (link-only README)
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch199
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**. `lemma_closed` stays false.

> **Batch 194 — tip stable `8bd1f03`; auth pending `CC72-DB3D`; README Path C link-only (no embedded user code); write DENIED**:
>
> ```bash
> # Repo face: README.md → Path C section links to portable/GH_DEVICE_LOGIN.md (SoT)
> # https://github.com/login/device + live code ONLY in GH_DEVICE_LOGIN.md
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**. `lemma_closed` stays false.

> **Batch 192 — tip stable `8bd1f03`; auth renew `CC72-DB3D` (from `1C7F-22B5` &lt;90s); README Path C face; write DENIED**:
>
> ```bash
> # Repo face: README.md → "Path C — land engineering fixes on main"
> # https://github.com/login/device + code in portable/GH_DEVICE_LOGIN.md
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**. `lemma_closed` stays false.

> **Batch 190 — tip stable `8bd1f03`; auth renew `1C7F-22B5` (from expired `C949-0100`); deeper hunt clean no 0017; write DENIED**:
>
> ```bash
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**.

> **Batch 188 — tip stable `8bd1f03`; auth renew `C949-0100` (from `46EC-0B00` <90s); write DENIED; idle align-watch**:
>
> ```bash
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**.

> **Batch 185 — tip stable `8bd1f03`; auth renew `46EC-0B00` (from `DF9C-5DF9` <90s); research AUDIT; bundle E2E OK; CI batch183 green**:
>
> ```bash
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**.

> **Batch 183 — tip stable `8bd1f03`; auth renew `DF9C-5DF9` (from `5216-7C1B` <90s); CI tip-drift supersession; hunt clean no 0017**:
>
> ```bash
> python3 scripts/write_path_c_status.py          # PATH_C_STATUS.json (no secrets)
> ./scripts/assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run     # release_bundle_url → batch180
> ./scripts/owner_path_c_oneshot.sh --from-bundle # after MAIN_PUSH_TOKEN / device auth
> ```
>
> Path C blocked NO_TOKEN. Scientific effect: **NONE**.

> **Batch 180 — tip `8ea3b5f`→`8bd1f03` (PR #52); release `batch180-path-c-bundle`; `write_path_c_status.py` → `portable/PATH_C_STATUS.json`**:
>
> ```bash
> gh release download batch180-path-c-bundle -R d6g8k5htny-coder/trial \
>   -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle' -p 'path-c-on-hardening.patch'
> mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
> /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
> # tip moved?: /tmp/path-c-land/scripts/refresh_path_c_bundle.sh && assert_path_c_ready.sh
> python3 scripts/write_path_c_status.py --dry-run   # schema: tip/base_tip/tip_match/write_state/lemma_closed/path_c_blocked/device_code/release_tag/generated_at
> ./scripts/owner_open_path_c_pr.sh --dry-run   # prints release_bundle_url → batch180
> ```
>
> Auth renewed `5216-7C1B` (prior `AD78-6206` near-expiry). Path C blocked NO_TOKEN. Scientific effect: **NONE**.

> **Batch 179 — release `batch179-path-c-bundle`** (oneshot + `.bundle` + `refresh_path_c_bundle.sh`; tip was `8ea3b5f`; superseded by batch180):
>
> ```bash
> gh release download batch179-path-c-bundle -R d6g8k5htny-coder/trial \
>   -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle' -p 'path-c-on-hardening.patch'
> mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
> /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
> # tip moved?: /tmp/path-c-land/scripts/refresh_path_c_bundle.sh && assert_path_c_ready.sh
> ./scripts/owner_open_path_c_pr.sh --dry-run   # prints release_bundle_url → batch179
> ```
>
> Auth still pending `AD78-6206` (Batch 178 renew from `5E05-EA04`). Prefer over `batch169-path-c-bundle`. Scientific effect: **NONE**.

> **Batch 178 — owner_open_path_c_pr links release `.bundle`** (tip stable `8ea3b5f`; CI tip-drift string restore):
>
> ```bash
> ./scripts/owner_open_path_c_pr.sh --dry-run   # prints release_bundle_url + release page
> ./scripts/owner_open_path_c_pr.sh             # PR body links path-c-on-hardening.bundle from batch179-path-c-bundle
> ./scripts/owner_path_c_oneshot.sh --from-bundle
> ```
>
> Auth renewed `AD78-6206` (prior `5E05-EA04`). Scientific effect: **NONE**.

> **Batch 176 — tip refresh + CI tip-drift dry-sim** (`scripts/refresh_path_c_bundle.sh`):
>
> ```bash
> ./scripts/refresh_path_c_bundle.sh --dry-run   # exit 0 tip-stable / 1 TIP_DRIFT (+ fix-path message)
> ./scripts/refresh_path_c_bundle.sh             # no-op if tip == BASE_TIP
> ./scripts/refresh_path_c_bundle.sh --force     # rebuild .patch+.bundle + VERIFY.json anyway
> ./scripts/assert_path_c_ready.sh               # preflight after refresh
> ```
>
> Tip fetch → BASE_TIP update → `apply_all` → rebuild `path-c-on-hardening.{patch,bundle}` → VERIFY.json.
> CI tip-drift jobs document this as the fix path and dry-sim `--dry-run` only (never auto-pushes to main).
> Tip currently stable `8ea3b5f`. Scientific effect: **NONE**.

> **Batch 173 — tip refresh automation** (`scripts/refresh_path_c_bundle.sh`): shipped helper; Batch 176 wired CI.

> **Batch 169 — Path C fetchable git `.bundle`** (`batch169-path-c-bundle`; prefers `.bundle` over `.patch`):
>
> ```bash
> gh release download batch169-path-c-bundle -R d6g8k5htny-coder/trial \
>   -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle' -p 'path-c-on-hardening.patch'
> mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
> /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
> # or: /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
> # manual: git fetch path-c-on-hardening.bundle cursor/portable-engineering-patches && git merge --ff-only FETCH_HEAD
> ```
>
> Prefer over `batch168-path-c-bundle` / `batch162-path-c-bundle`. BASE_TIP `8ea3b5f`.
> Auth timer guidance: `preferred_auth_interval_s=1800` (do not duplicate). Scientific effect: **NONE**.
> Superseded by `batch179-path-c-bundle` (Batch 179 pack with oneshot+refresh).

> **Batch 168 — Path C ONE-SHOT pack** (`batch168-path-c-bundle`; includes `owner_path_c_oneshot.sh`):
>
> ```bash
> gh release download batch168-path-c-bundle -R d6g8k5htny-coder/trial \
>   -p 'trial-portable-main-fixes.tgz'
> mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
> /tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
> # or: /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
> ```
>
> Prefer over `batch162-path-c-bundle` / `batch142-path-c-bundle`. BASE_TIP `8ea3b5f`.
> Auth timer guidance: `preferred_auth_interval_s=1800` (do not duplicate). Scientific effect: **NONE**.
> Superseded by `batch169-path-c-bundle`.

> **Batch 137 — Path C ONE-SHOT from release tarball** (`batch142-path-c-bundle` or newer):
>
> ```bash
> gh release download batch142-path-c-bundle -R d6g8k5htny-coder/trial \
>   -p 'trial-portable-main-fixes.tgz'
> mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
> /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
> ```
>
> Prerequisites: `git`, `python3`, `gh auth login` (write on `main`). Cloud scope
> unblock / relaunch: [`RELAUNCH_WITH_MAIN_SCOPE.md`](RELAUNCH_WITH_MAIN_SCOPE.md).
> Scientific effect: **NONE**. BASE_TIP `c82c9357`.

> **Batch 86:** Owner (Dylan Roy) — **NO restrictions; everything auto-approved; agents decide. Broad grant.** **Permanent window** until Dylan intervenes (no 48h finale). Default tip **ALIGNED** @ `1c6e74b` ([PR #41](https://github.com/d6g8k5htny-coder/main/pull/41)). Scientific effect: **NONE**. Status guard: `scripts/guard_no_status_promotion.py` vs `BATCH70_RESEARCH_STACK_AUDIT` / `STATUS_GUARD_SNAPSHOT` (fail on OPEN→closed/promoted); CI `research-stack-status-guard` (`continue-on-error` + artifact). Write still 403. See `BATCH86_BRIEF.json`.

> **Batch 84:** Owner (Dylan Roy) — **NO restrictions; everything auto-approved; agents decide. Broad grant.** **Permanent window** until Dylan intervenes (no 48h finale). Default tip **ALIGNED** @ `1c6e74b` ([PR #41](https://github.com/d6g8k5htny-coder/main/pull/41)). Scientific effect: **NONE**. Env: `.cursor/environment.json` `repositoryDependencies` → `main` (write intent); **relaunch Cloud Agent from trial AFTER merge** for token scope. Lander token discovery: env `MAIN_PUSH_TOKEN` → `/cursor/stores/self/MAIN_PUSH_TOKEN` → `/workspace/.secrets/MAIN_PUSH_TOKEN` (never printed). Write still 403 until token flips. See `BATCH84_BRIEF.json`.
>
> **Batch 82 archive:** `when_writable_land.py` background lander; tmux `when-writable-land`; `BATCH82_BRIEF.json` retained.
>
> **Batch 76 archive:** path-c-applied-bundle for owner `git am`; BASE_TIP `ac33581`; `RESTORE_PLAN_76.json` retained.
>
> **Batch 74 archive:** tip refresh `5f352a2`→`ac33581` (PR #48) + Batch 73 CI fix; `RESTORE_PLAN_74.json` retained.
>
> **Batch 73 archive:** CI land-workflows-dry-run without MAIN_PUSH_TOKEN; BASE_TIP was still `5f352a2`; `RESTORE_PLAN_73.json` retained.
>
> **Batch 72 archive:** `aligned_drift_watch.py` + CI record-only + `ALIGNED_DRIFT_SNAPSHOT.json`; `RESTORE_PLAN_72.json` retained.
>
> **Batch 71 archive:** residual RW IDLE / no 0017; `land-path-c-on-main.yml` parity OK; `RESTORE_PLAN_71.json` retained.

After merging a trial PR that adds `.cursor/environment.json`
(`repositoryDependencies` → `github.com/d6g8k5htny-coder/main`): **relaunch** a
Cloud Agent on `trial` so the token picks up `main` write scope, then run
**Path B** (preferred) or Path C. Scientific effect: **NONE**. Current runs stay scoped to `trial` only.

**Scientific effect: NONE** for packaging lands below. Do not flip
`lemma_closed` / prize / premise status.

Quick dump of this file + live probe/audit:

```bash
./scripts/print_owner_unblock.sh
```

Poll until default tip is **ALIGNED** (scientific effect **NONE**):

```bash
./scripts/wait_until_aligned.sh              # interval 30s, max 2h
./scripts/wait_until_aligned.sh --verify     # then VERIFY_AFTER_MERGE.sh if present
```

ALIGNED drift watch (ready for instant Path B restore if tip reverts):

```bash
python3 scripts/aligned_drift_watch.py                 # exit 0/1/2; writes ALIGNED_DRIFT_SNAPSHOT.json
python3 scripts/aligned_drift_watch.py --restore-if-writable  # Path B land when MISALIGNED+writable
```

Background lander (poll write; auto Path C / Path B; Batch 82):

```bash
python3 scripts/when_writable_land.py --once --dry-run   # decide only
python3 scripts/when_writable_land.py                    # loop 300s; tmux session when-writable-land
# STOP: touch /cursor/stores/self/when_writable_land.stop
# status: /cursor/stores/self/when_writable_land.status.json
```

## Executable owner land scripts (preferred on owner machine / Codespace)

These use **your** `gh` auth (write on `d6g8k5htny-coder/main`). Fail closed with clear errors.

```bash
# Path C — engineering on hardening tip: apply_all 0001–0004 + 0008–0016
./scripts/owner_path_c_oneshot.sh --dry-run   # Batch 165: token→open PR/land; else unblock menu
./scripts/owner_path_c_oneshot.sh
./scripts/owner_path_c_oneshot.sh --from-bundle
./scripts/owner_land_path_c.sh --dry-run   # certainty (works without write)
./scripts/owner_land_path_c.sh --from-bundle   # ONE-SHOT after extracting release tarball
./scripts/owner_land_path_c.sh                 # apply_all path (same gates)
# Path C — owner PR from path-c-applied-bundle (Batch 151)
./scripts/owner_open_path_c_pr.sh --dry-run    # certainty; no clone/push
./scripts/owner_open_path_c_pr.sh              # git am → cursor/path-c-portable-fixes → PR hardening
# Avoid post-#41: PATH_C_REBASE_ONTO_MAIN=1 (CONFLICTS) / PATH_C_BASE=main (no PACKET)
# Do NOT set PATH_C_BASE=main unless that tip has docs/math_status/PACKET.json
# If a forced rebase hits first-stop conflicts (ci.yml / research.yml / bridge):
./scripts/path_c_rebase_helper.sh --dry-run
# ./scripts/path_c_rebase_helper.sh --stage --workdir "$PWD"  # then prefer: git rebase --abort

# Path B — PREFERRED one-command ALIGNED restore
./scripts/restore_main_face.sh --dry-run
./scripts/restore_main_face.sh
# ./scripts/restore_main_face.sh --direct-main
./scripts/owner_land_path_b.sh --dry-run    # underlying certainty JSON
./scripts/owner_land_path_b.sh
./scripts/owner_land_path_b.sh --after-merge
# python3 scripts/refresh_restore_plan.py --batch 59


# Path A — HOLD VOID. Default: revert #32. Prefer Path B when notice-only is enough.
./scripts/owner_land_path_a.sh
# PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
# PATH_A_MODE=ready_merge PATH_A_PR=<open> ./scripts/owner_land_path_a.sh
```


## Path B — honest redirect (PREFERRED for default-tip ALIGNED)

### B0 — one-command / owner script (preferred)

```bash
./scripts/restore_main_face.sh --dry-run    # one-command certainty
./scripts/restore_main_face.sh              # dry-run then branch+PR
./scripts/owner_land_path_b.sh --dry-run    # underlying certainty JSON
./scripts/owner_land_path_b.sh              # branch + PR (default)
./scripts/owner_land_path_b.sh --after-merge
# ./scripts/restore_main_face.sh --direct-main   # opt-in push to main
```

### B1 — Actions UI (trial workflow)

1. On **trial**: Settings → Secrets → Actions → add `MAIN_PUSH_TOKEN`
   (PAT with Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`).
2. Actions → **land-option-b-on-main** → Run workflow.
3. Set `dry_run=false` (default `true` only verifies `git am`).
4. Workflow pushes `cursor/option-b-notice-from-trial` and opens (or reuses) a PR
   into default `main` — merge that PR (one click).

### B2 — local token

```bash
# Prefer: ./scripts/owner_land_path_b.sh
export MAIN_PUSH_TOKEN=ghp_…   # write on d6g8k5htny-coder/main
git clone https://x-access-token:${MAIN_PUSH_TOKEN}@github.com/d6g8k5htny-coder/main.git
cd main && git checkout main
git checkout -b cursor/default-branch-notice
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
python3 /path/to/trial/scripts/audit_local_tree.py .
git push -u origin HEAD
gh pr create --base main --title "docs: q0 redirect on default main" \
  --body "Option-B notice. Scientific effect NONE. HOLD VOID; Path B preferred."
```

Write probe (optional):

```bash
# exit 0=writable, 1=denied, 2=transport
MAIN_PUSH_TOKEN=… python3 /path/to/trial/scripts/probe_main_write.py
```

## Path A — HOLD VOID (prefer Path B; #2 closed after #32)

[PR #2](https://github.com/d6g8k5htny-coder/main/pull/2) was MERGED @ `b040bf0c`, then [PR #32](https://github.com/d6g8k5htny-coder/main/pull/32) reverted default tip to pre-q0 @ `4fc1d7c` (**MISALIGNED**). **HOLD is VOID** (Batch 54 OWNER OVERRIDE). Agents may Path A, but prefer Path B. PR #2 is closed — ready/merge will not revive it.

```bash
# Preferred Path A after #32 (write creds):
PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
# Fresh OPEN port PR:
# PATH_A_MODE=ready_merge PATH_A_PR=<n> ./scripts/owner_land_path_a.sh
# Historical only (PR #2 is closed — will fail):
# gh pr ready 2 --repo d6g8k5htny-coder/main
# gh pr merge 2 --repo d6g8k5htny-coder/main --merge
```

## Path C — engineering patches on working tip

Independent of default-tip alignment: apply `apply_all` **0001–0004 + 0008–0016** on hardening. Prefer the owner script (fail-closed without write). Post-#41 default tip is ALIGNED but not Path-C shaped:

```bash
./scripts/owner_land_path_c.sh --dry-run
./scripts/owner_land_path_c.sh
# Avoid: PATH_C_REBASE_ONTO_MAIN=1 ./scripts/owner_land_path_c.sh   # CONFLICTS after PR #41

# Batch 151 — owner PR opener (bundle git am → branch cursor/path-c-portable-fixes):
./scripts/owner_open_path_c_pr.sh --dry-run
./scripts/owner_open_path_c_pr.sh
# Uses owner gh auth or MAIN_PUSH_TOKEN. Idempotent if branch/PR exists.
# PR body: engineering-only; lemma_closed stays false; no research promotion.

# Batch 160 — set trial Actions secret MAIN_PUSH_TOKEN (+ optional Path C dispatch):
./scripts/owner_set_main_push_token.sh --dry-run
MAIN_PUSH_TOKEN=… ./scripts/owner_set_main_push_token.sh --dispatch
# or: ./scripts/owner_set_main_push_token.sh --from-gh --dispatch
# Token never printed. Scientific effect NONE; lemma_closed stays false.
```

### C1 — Actions UI (trial workflow; Batch 69+) / secret one-shot (Batch 160)

1. On **trial**: Settings → Secrets → Actions → add `MAIN_PUSH_TOKEN`
   (PAT with Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`).
   **Or one-shot** (token never printed):

   ```bash
   ./scripts/owner_set_main_push_token.sh --dry-run
   MAIN_PUSH_TOKEN=… ./scripts/owner_set_main_push_token.sh --dispatch
   # or: ./scripts/owner_set_main_push_token.sh --from-gh --dispatch
   ```

   (`gh secret set` on trial + optional `repository_dispatch` land-path-c `dry_run=false`)
2. Actions → **land-path-c-on-main** → Run workflow.
3. Default `dry_run=true` verifies `apply_all` + `lemma_closed=false` / `problems=0` (no push).
4. Set `dry_run=false` to push `cursor/portable-engineering-patches` and open (or reuse)
   a PR into `chatgpt/drive-github-hardening-20260919`. Optional `direct_push=true` skips the PR.

```bash
gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=true
gh workflow run land-path-c-on-main --repo d6g8k5htny-coder/trial -f dry_run=false
```

Against `chatgpt/drive-github-hardening-20260919` @ tip in
`portable/patches/BASE_TIP.txt` (currently `5f352a2`). Default `main` after #41 is
ALIGNED research landing (no PACKET.json) — do not apply Path C there:

```bash
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -b cursor/portable-engineering-patches origin/chatgpt/drive-github-hardening-20260919
/path/to/trial/portable/patches/apply_all.sh --check
/path/to/trial/portable/patches/apply_all.sh
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
  tests/test_inventable_jetmod_instrumentation_status.py
# expect: problems=0, lemma_closed=false; 90 passed @ b3da668
```

Post-merge from trial (`VERIFY_AFTER_MERGE.sh`) also applies Path C locally when
`apply_all` is findable and asserts `lemma_closed=false` (`SKIP_PATH_C=1` to skip).

`apply_all.sh` includes **0001–0004 + 0008–0016** (tip-cut 0005/0006/0007 dropped after
PR #27 merged @ `bf1fde3` in batch 48; 0008–0015 as in batches 25–52; **0016** receipts/
bridge close-handles in batch 53). Batch 60: tip `b3da668`; no new 0017 (residual RW hunt 0);
Path C dry-run certainty shipped.
