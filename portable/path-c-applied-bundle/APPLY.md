# Path C applied bundle — `git am` onto hardening @ BASE_TIP

**Effect:** engineering hygiene only on `chatgpt/drive-github-hardening-20260919`. Scientific effect: **NONE**. Does not flip `lemma_closed`.

**Batch 80:** also shipped as GitHub Release tag `batch80-path-c-bundle` on `d6g8k5htny-coder/trial` (attach `path-c-on-hardening.patch` + `docs/trial-portable-main-fixes.tgz`). Tip SHA still **`ac33581`**.

## One-liner (owner / write token)

```bash
git fetch origin chatgpt/drive-github-hardening-20260919 && git checkout -B cursor/portable-engineering-patches ac335815b277ac0c076082ac6af2344261c2093a && git am /path/to/path-c-on-hardening.patch && git push -u origin HEAD
```

Then open a PR into `chatgpt/drive-github-hardening-20260919` (or `--direct-push` equivalent). Do **not** apply on post-#41 default `main` (no `PACKET.json`).

## Verify after am

```bash
python3 tools/math_status_check.py   # expect problems=0 lemma_closed=false
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py tests/test_inventable_jetmod_instrumentation_status.py
```

See `VERIFY.json` for Batch 76 recorded counts (`problems=0`, `lemma_closed=false`).
