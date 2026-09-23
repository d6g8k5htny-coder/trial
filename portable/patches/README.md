# Portable patches for `d6g8k5htny-coder/main`

Base tip these were cut against:
`cursor/inventable-jetmod-probes-4488` @ `ae94270d5f48d4c171f134efcea5058997966d71`
(also applies cleanly on `chatgpt/drive-github-hardening-20260919` for #0001).

**Scientific effect: NONE.** No claim/premise/lemma status moves.

## 0001 — `carriers_verify` ignores bytecode caches

**Bug:** Importing any stored blob under `engine/carriers/blobs/` creates
`__pycache__/`. `tools/carriers_verify.py` then reports
`blobs/__pycache__: stored but no manifest record references it` and exits 1,
even though `.gitignore` already ignores `__pycache__/`.

**Fix:** Skip non-files, `__pycache__`, and `*.pyc` when scanning `blobs/`.
Adds `tests/test_carriers.py::test_pycache_in_blobs_is_ignored`.

**Verify on a writable checkout:**

```bash
git apply portable/patches/0001-carriers-verify-ignore-bytecode-caches.patch
python3 -c "import py_compile; py_compile.compile('engine/carriers/blobs/bd3074fd900fc80b__rnu_ds3.py', doraise=True)"
python3 tools/carriers_verify.py    # problems=0
python3 -m pytest -q tests/test_carriers.py
```

## 0002 — `math_console` path honesty

**Bug:** On the hardening/inventable tips, `docs/math_status/math_console.py`
documents and recommends `python3 code_prototypes/...`, but this repository
does not carry `code_prototypes/`. `ROOT` was also `parents[1]` (`docs/`)
instead of the repository root. Draft PR #12 corrected some of this but is
**10 commits behind** the current hardening tip and was never merged.

**Fix:** Point usage/commands at `docs/math_status/math_console.py` and set
`ROOT` to the repository root. Console remains fail-closed / non-discharging.

```bash
git apply portable/patches/0002-math-console-path-honesty.patch
python3 docs/math_status/math_console.py --json
```
