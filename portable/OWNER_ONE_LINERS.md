# Owner one-liners (Path A / B / C)

Copy-paste from a machine or Actions runner that **can write** to
`d6g8k5htny-coder/main`. This trial cloud token cannot (git push + Git Data API
+ `gh pr ready/merge` all return **403**).

**Scientific effect: NONE** for packaging lands below. Do not flip
`lemma_closed` / prize / premise status.

Quick dump of this file + live probe/audit:

```bash
./scripts/print_owner_unblock.sh
```

## Executable owner land scripts (preferred on owner machine / Codespace)

These use **your** `gh` auth (write on `d6g8k5htny-coder/main`). Fail closed with clear errors.

```bash
# Path A — mark PR #2 ready, merge, then audit/watch until ALIGNED
./scripts/owner_land_path_a.sh

# Path B — default safer: git am Option-B → push branch → open PR
./scripts/owner_land_path_b.sh
# after you merge that PR:
./scripts/owner_land_path_b.sh --after-merge
# opt-in only: push Option-B straight onto default main (no PR)
./scripts/owner_land_path_b.sh --direct-main
```

## Path A — land the real tree (manual one-liners)

PR #2 is historically **MERGEABLE / CLEAN** (Drive→git port onto default `main`).

```bash
# Prefer: ./scripts/owner_land_path_a.sh
gh pr ready 2 --repo d6g8k5htny-coder/main
gh pr merge 2 --repo d6g8k5htny-coder/main --merge
# optional verify:
curl -sL https://raw.githubusercontent.com/d6g8k5htny-coder/main/main/README.md | head
python3 /path/to/trial/scripts/audit_main_alignment.py   # expect exit 0
python3 /path/to/trial/scripts/watch_main_alignment.py    # expect ALIGNED
```

## Path B — honest redirect until Path A

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
git push -u origin HEAD
gh pr create --repo d6g8k5htny-coder/main --base main \
  --title "docs: q0 redirect on default main" \
  --body "Option-B notice. Scientific effect NONE. Prefer merging PR #2 when ready."
```

### Probe before spending time

```bash
# exit 0=writable, 1=denied, 2=transport
MAIN_PUSH_TOKEN=… python3 /path/to/trial/scripts/probe_main_write.py
```

## Path C — engineering patches on working tip

Against `chatgpt/drive-github-hardening-20260919` @ tip in
`portable/patches/BASE_TIP.txt` (currently `1547ec4`):

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
# expect: problems=0, lemma_closed=false; 90 passed @ 1547ec4
```

`apply_all.sh` now includes **0001–0006** (0006 promoted after PR #20 merge).
