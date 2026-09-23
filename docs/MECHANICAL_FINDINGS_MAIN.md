# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Clone tip audited: `cursor/inventable-jetmod-probes-4488` @ `ae94270d5f48d4c171f134efcea5058997966d71`
Host: CPython 3.11.16 (uv) + pytest 9.1.1
**Scientific effect: NONE.**

## Green

| Check | Result |
|-------|--------|
| `python tools/math_status_check.py` | `problems=0` disposition `OPEN_HOLD`; `lemma_closed=false` |
| inventable + math_status tests | 18 passed |
| Broad slice (claims/registers/bridge/ops/workflows/lanes/…) | **1012 passed**, 2 skipped, then 2 carrier failures before patch |
| After `0001` carriers patch + bytecode present | `carriers_verify` problems=0; **21** carrier tests passed |
| PR #2 | **MERGEABLE / CLEAN** with verify SUCCESS (read-only observation) |

## Engineering defects → portable patches

| ID | Symptom | Patch |
|----|---------|-------|
| carriers `__pycache__` false positive | Importing a blob makes `carriers_verify` exit 1 | `portable/patches/0001-…` |
| `math_console` points at missing `code_prototypes/` | Wrong usage/ROOT; PR #12 fixed a variant but is 10 commits behind hardening | `portable/patches/0002-…` |

## Environment flake (not patched)

`tests/test_run_checks.py` fixture `git commit` hit a 10s timeout once on this VM. Re-run before treating as product bug.

## Not bugs (do not “fix”)

- `OBL-H5-JETMOD` / `D3-LEMMA-RN-UNIF` OPEN and inventable REFUSED receipts — correct.
- Default-branch complexity-physics face — misalignment; see `portable/main-default-branch/` and `portable/pr2-landing/`.

## Write access

This agent still cannot push to `main` (`cursor[bot]` 403).
