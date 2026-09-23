# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `1ea0ae8183fb0459c6678243946295518fded1ba`
(PR #15 inventable probes merged). Host: CPython 3.11.16 + pytest 9.1.1.
**Scientific effect: NONE.**

## Full suite (inventable tip + incomplete 0002 without PACKET refresh)

Before regenerating 0002 with PACKET digests: **3065 passed**, 2 skipped, **3 failed**
(math_status digest drift), **2 errors** (git-commit fixture timeout on this VM).

## After complete portable patches on `1ea0ae8`

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable tests | **39 passed** |
| `apply --check` both patches | OK |

## Engineering defects → portable patches

| ID | Fix |
|----|-----|
| carriers `__pycache__` false positive | `0001-…` |
| math_console `code_prototypes` paths + PACKET sha/bytes | `0002-…` (digest refresh required) |

## Alignment

Default `main` still MISALIGNED. PR #2 still MERGEABLE/CLEAN. PR #15 merged into hardening only — not into default `main`.
