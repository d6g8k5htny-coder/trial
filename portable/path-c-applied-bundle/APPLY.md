# Path C applied bundle — prefer `git fetch` of `.bundle` onto hardening @ BASE_TIP

**Batch 244 (living tip / pack sync):** hardening tip **`1ae02b9`** (== BASE_TIP; [PR #71](https://github.com/d6g8k5htny-coder/main/pull/71) 0019 attestations RW @ `542e6ec`). Living release **`batch241-path-c-bundle`**. Patches **0001–0004+0008–0019** are **already on tip** — `owner_land_path_c.sh --from-bundle` dry-run exits 0 with `already_applied_on_tip=true` (`.bundle` ff-only may diverge; apply_all `--check` is the authority). Do **not** re-land Path C onto `1ae02b9`. `when_writable_land` → `idle_path_c_done` (0018+0019 markers true). `lemma_closed=false`. Scientific effect: **NONE**.

**Batch 232 (tip refresh):** hardening tip **`93a4ecd`→`377201c`** ([PR #62](https://github.com/d6g8k5htny-coder/main/pull/62) inventable campaign; PACKET kept; flags unflipped). Path C eng stack **already on tip** (ancestor [PR #64](https://github.com/d6g8k5htny-coder/main/pull/64)). Historical `.bundle`+`.patch` retained for pre-land tips. `lemma_closed=false`. Scientific effect: **NONE**.

**Batch 230 (LANDED):** Path C **merged** on main hardening via [PR #64](https://github.com/d6g8k5htny-coder/main/pull/64). Tip **`93a4ecd`** (merge of applied `fb3ffe6` from `.bundle` on prior BASE `cbaa056`). Patches **0001–0004+0008–0017** are **already on tip**. `lemma_closed=false` / OPEN_HOLD verified. Scientific effect: **NONE**.

**Batch 218:** tip **`1d0dceb`** (refreshed from `b89448d`). Release **`batch218-path-c-bundle`** (superseded by `batch241-path-c-bundle`).

**Batch 207:** tip still **`b89448d`**. Release **`batch207-path-c-bundle`** (superseded; included **0017** pinned_sources RW).

**Effect:** engineering hygiene only on `chatgpt/drive-github-hardening-20260919`. Scientific effect: **NONE**. Does not flip `lemma_closed`.

## ONE-SHOT (owner / write token) — preferred

```bash
gh release download batch241-path-c-bundle -R d6g8k5htny-coder/trial \
  -p 'trial-portable-main-fixes.tgz' -p 'path-c-on-hardening.bundle' -p 'path-c-on-hardening.patch'
mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
/tmp/path-c-land/scripts/owner_path_c_oneshot.sh --from-bundle
# or: /tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
```

On tip **`1ae02b9`** expect dry-run / land to report **`already_applied_on_tip=true`** (no new commits). Prior release tags (`batch239` / `batch218` / `batch207` / …) are historical only — do not download them for new lands.

Prerequisites: `git`, `python3`, `gh auth login` (Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`).

## Manual — git bundle fetch + merge (preferred; Batch 169+)

On a clone that already has BASE_TIP `1ae02b9` (shallow OK — Batch 170 E2E verified `--depth 1` and `--depth 80`):

```bash
# Shallow clone hardening @ BASE_TIP (or deepen an existing clone):
git clone --depth 1 --branch chatgpt/drive-github-hardening-20260919 \
  https://github.com/d6g8k5htny-coder/main.git main && cd main
# If already cloned: git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -B cursor/portable-engineering-patches 1ae02b9ab759fe5edb31ad04f2a47992a5dee2c5
# Prefer .bundle when present:
git fetch /path/to/path-c-on-hardening.bundle cursor/portable-engineering-patches
git merge --ff-only FETCH_HEAD
# equivalent pull form:
# git pull /path/to/path-c-on-hardening.bundle cursor/portable-engineering-patches
git push -u origin HEAD
```

Then open a PR into `chatgpt/drive-github-hardening-20260919`. Do **not** apply on post-#41 default `main` (no `PACKET.json`).

**Living tip note:** at `1ae02b9` the merge may refuse ff-only (historical applied range diverged); that is expected — patches are already on tip. Prefer `apply_all.sh --check` / `owner_land_path_c.sh --from-bundle --dry-run`.

**Batch 170 E2E:** shallow clone @ `8ea3b5f` → `git fetch` `.bundle` → `merge --ff-only` → HEAD `81c09d6`; `math_status_check` problems=0 / OPEN_HOLD / **lemma_closed=false**; focused pytest **90** passed.

## Manual — legacy `git am` of `.patch`

```bash
git fetch origin chatgpt/drive-github-hardening-20260919 && git checkout -B cursor/portable-engineering-patches 1ae02b9ab759fe5edb31ad04f2a47992a5dee2c5 && git am /path/to/path-c-on-hardening.patch && git push -u origin HEAD
```

## Verify after fetch/merge or am

```bash
python3 tools/math_status_check.py   # expect problems=0 lemma_closed=false
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py
```

See `VERIFY.json` for Batch 241 recorded counts (`problems=0`, `lemma_closed=false`, focused 90 / 0 ResourceWarning) and bundle fields.
Cloud Agent mid-flight cannot gain main write — see `../RELAUNCH_WITH_MAIN_SCOPE.md`.
