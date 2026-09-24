# Path C applied bundle — `git am` onto hardening @ BASE_TIP

**Effect:** engineering hygiene only on `chatgpt/drive-github-hardening-20260919`. Scientific effect: **NONE**. Does not flip `lemma_closed`.

**Batch 142:** refreshed against hardening tip **`10c077e`** (PR #54; prior BASE `c82c9357` / PR #50). Also shipped as GitHub Release tag `batch142-path-c-bundle` on `d6g8k5htny-coder/trial` (attach `path-c-on-hardening.patch` + `docs/trial-portable-main-fixes.tgz`).

**Batch 137:** preferred owner path is **one command** via `scripts/owner_land_path_c.sh --from-bundle` after extracting the release tarball (same patch + lemma gates + branch/PR).

## ONE-SHOT (owner / write token) — preferred

```bash
gh release download batch142-path-c-bundle -R d6g8k5htny-coder/trial \
  -p 'trial-portable-main-fixes.tgz'
mkdir -p /tmp/path-c-land && tar -xzf trial-portable-main-fixes.tgz -C /tmp/path-c-land
/tmp/path-c-land/scripts/owner_land_path_c.sh --from-bundle
```

Prerequisites: `git`, `python3`, `gh auth login` (Contents:Write + PullRequests:Write on `d6g8k5htny-coder/main`).

## Manual one-liner (`git am` only)

```bash
git fetch origin chatgpt/drive-github-hardening-20260919 && git checkout -B cursor/portable-engineering-patches 10c077e08261fa3d07317e290826604a749d4e49 && git am /path/to/path-c-on-hardening.patch && git push -u origin HEAD
```

Then open a PR into `chatgpt/drive-github-hardening-20260919` (or `--direct-push` equivalent). Do **not** apply on post-#41 default `main` (no `PACKET.json`).

## Verify after am

```bash
python3 tools/math_status_check.py   # expect problems=0 lemma_closed=false
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py
```

See `VERIFY.json` for Batch 142 recorded counts (`problems=0`, `lemma_closed=false`, focused 90 / 0 ResourceWarning).
Cloud Agent mid-flight cannot gain main write — see `../RELAUNCH_WITH_MAIN_SCOPE.md`.
