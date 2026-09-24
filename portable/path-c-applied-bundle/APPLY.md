# Path C applied bundle — prefer `git fetch` of `.bundle` onto hardening @ BASE_TIP

**Effect:** engineering hygiene only on `chatgpt/drive-github-hardening-20260919`. Scientific effect: **NONE**. Does not flip `lemma_closed`.

**Batch 169:** tip still **`8ea3b5f`** (no tip move). Ships fetchable **`path-c-on-hardening.bundle`** (`BASE_TIP..HEAD`) plus legacy `.patch`. Release tag `batch169-path-c-bundle` on `d6g8k5htny-coder/trial`. Owner scripts prefer `.bundle` when present.

**Batch 168:** tip **`8ea3b5f`**. Pack included `scripts/owner_path_c_oneshot.sh`. Prior release `batch168-path-c-bundle`.

**Batch 162:** refreshed against hardening tip **`8ea3b5f`** (PR #53; prior BASE `10c077e` / PR #54). Prior release `batch162-path-c-bundle`.

## ONE-SHOT (owner / write token) — preferred

```bash
gh release download batch169-path-c-bundle -R d6g8k5htny-coder/trial \
  -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle' -p 'path-c-on-hardening.patch'
mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
/tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
# or: /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
```

Prerequisites: `git`, `python3`, `gh auth login` (Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`).

## Manual — git bundle fetch + merge (preferred; Batch 169+)

On a clone that already has BASE_TIP `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` (shallow OK — Batch 170 E2E verified `--depth 1` and `--depth 80`):

```bash
# Shallow clone hardening @ BASE_TIP (or deepen an existing clone):
git clone --depth 1 --branch chatgpt/drive-github-hardening-20260919 \
  https://github.com/d6g8k5htny-coder/main.git main && cd main
# If already cloned: git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -B cursor/portable-engineering-patches 8ea3b5fb9368a85e7f971d606b8f75c96c35c05a
# Prefer .bundle when present:
git fetch /path/to/path-c-on-hardening.bundle cursor/portable-engineering-patches
git merge --ff-only FETCH_HEAD
# equivalent pull form:
# git pull /path/to/path-c-on-hardening.bundle cursor/portable-engineering-patches
git push -u origin HEAD
```

Then open a PR into `chatgpt/drive-github-hardening-20260919`. Do **not** apply on post-#41 default `main` (no `PACKET.json`).

**Batch 170 E2E:** shallow clone @ `8ea3b5f` → `git fetch` `.bundle` → `merge --ff-only` → HEAD `81c09d6`; `math_status_check` problems=0 / OPEN_HOLD / **lemma_closed=false**; focused pytest **90** passed.

## Manual — legacy `git am` of `.patch`

```bash
git fetch origin chatgpt/drive-github-hardening-20260919 && git checkout -B cursor/portable-engineering-patches 8ea3b5fb9368a85e7f971d606b8f75c96c35c05a && git am /path/to/path-c-on-hardening.patch && git push -u origin HEAD
```

## Verify after fetch/merge or am

```bash
python3 tools/math_status_check.py   # expect problems=0 lemma_closed=false
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py
```

See `VERIFY.json` for Batch 169 recorded counts (`problems=0`, `lemma_closed=false`, focused 90 / 0 ResourceWarning) and bundle fields.
Cloud Agent mid-flight cannot gain main write — see `../RELAUNCH_WITH_MAIN_SCOPE.md`.
