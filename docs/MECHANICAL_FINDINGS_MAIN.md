# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `3e8f38845cb350f43a64b8784400338c8e9a78f6`
(PR #17 fail-closed inventable JETMOD shortcut refusals merged; prior #15/#16/#18).
Host: CPython 3.11.16 + pytest 9.1.1.
**Scientific effect: NONE.**

## After portable patches 0001–0005 on `3e8f388` (batch 17)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian | **86 passed** |
| inventable + claims + registers + consumers | **134 passed** |
| + ci_pins (deselecting `python`-missing host flakes) | **153 passed** |
| `apply_all.sh --check` | OK |

## Engineering defects → portable patches

| ID | Fix |
|----|-----|
| carriers `__pycache__` false positive | `0001-…` |
| math_console `code_prototypes` paths + PACKET sha/bytes | `0002-…` |
| gaussian moments parametrize iterator | `0003-…` |
| git fixture timeout 10s → 60s | `0004-…` |
| inventable probe test dirty digests (re-cut post-#17) | `0005-…` |
| instrumentation STATUS dirty digests (PR #20 only) | optional `0006-…` (not in `apply_all`) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Write probe still 403. No `research.yml` schedule changes.
