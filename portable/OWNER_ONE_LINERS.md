# Owner one-liners (Path B preferred / Path A HOLD VOID / Path C engineering)

Copy-paste from a machine or Actions runner that **can write** to
`d6g8k5htny-coder/main`. This trial cloud token cannot (git push + Git Data API
+ `gh pr ready/merge` all return **403**).

> **Batch 54 OWNER OVERRIDE:** Default tip **MISALIGNED** @ `4fc1d7c` after CoS [PR #32](https://github.com/d6g8k5htny-coder/main/pull/32) reverted [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2). `aligned_end=false`. Scientific effect: **NONE**.
>
> **HOLD on PR #2 is VOID.** Agents may **Path A OR Path B**. Prefer **Path B** (Option-B patch still valid — `git am` OK / would-align). Path A = `PATH_A_MODE=revert32` (or fresh OPEN port). Path C = portable engineering on hardening (BASE_TIP `9a56c30`).
> Trial cloud tokens still cannot write to `main` (403) → Path B not applied from trial. All write vectors DENIED this batch (see `RESTORE_PLAN_54.json`).

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

## Executable owner land scripts (preferred on owner machine / Codespace)

These use **your** `gh` auth (write on `d6g8k5htny-coder/main`). Fail closed with clear errors.

```bash
# Path C — engineering on hardening tip: apply_all 0001–0004 + 0008–0016
./scripts/owner_land_path_c.sh
# Optional: rebase hardening onto post-#2 main, then apply:
# PATH_C_REBASE_ONTO_MAIN=1 ./scripts/owner_land_path_c.sh
# Do NOT set PATH_C_BASE=main unless that tip has docs/math_status/PACKET.json

# Path B — PREFERRED for default-tip ALIGNED (Option-B notice)
./scripts/owner_land_path_b.sh
./scripts/owner_land_path_b.sh --after-merge
# ./scripts/owner_land_path_b.sh --direct-main

# Path A — HOLD VOID. Default: revert #32. Prefer Path B when notice-only is enough.
./scripts/owner_land_path_a.sh
# PATH_A_MODE=revert32 ./scripts/owner_land_path_a.sh
# PATH_A_MODE=ready_merge PATH_A_PR=<open> ./scripts/owner_land_path_a.sh
```


## Path B — honest redirect (PREFERRED for default-tip ALIGNED)

### B0 — owner script (preferred)

```bash
./scripts/owner_land_path_b.sh              # branch + PR (default)
./scripts/owner_land_path_b.sh --after-merge
# ./scripts/owner_land_path_b.sh --direct-main   # opt-in push to main
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

Independent of default-tip alignment: apply `apply_all` **0001–0004 + 0008–0016** on hardening. Prefer the owner script (fail-closed without write):

```bash
./scripts/owner_land_path_c.sh
# PATH_C_REBASE_ONTO_MAIN=1 ./scripts/owner_land_path_c.sh   # rebase hardening onto post-#2 main first
```

Against `chatgpt/drive-github-hardening-20260919` @ tip in
`portable/patches/BASE_TIP.txt` (currently `9a56c30`). Default `main` after #32 is the
pre-q0 face — do not apply Path C there (no PACKET.json):

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
# expect: problems=0, lemma_closed=false; 90 passed @ 9a56c30
```

Post-merge from trial (`VERIFY_AFTER_MERGE.sh`) also applies Path C locally when
`apply_all` is findable and asserts `lemma_closed=false` (`SKIP_PATH_C=1` to skip).

`apply_all.sh` includes **0001–0004 + 0008–0016** (tip-cut 0005/0006/0007 dropped after
PR #27 merged @ `bf1fde3` in batch 48; 0008–0015 as in batches 25–52; **0016** receipts/
bridge close-handles in batch 53). Batch 54: no new 0017 (residual RW hunt 0).
