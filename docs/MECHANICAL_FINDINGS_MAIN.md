# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `1547ec4abea9552b17d0d7eecb901266081e4721`
(PR #20 instrumentation STATUS vocab merged; prior #15/#16/#17/#18).
Host: CPython 3.11.16 + pytest.
**Scientific effect: NONE.**

## After portable patches 0001–0006 on `1547ec4` (batch 21)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian + instrumentation | **90 passed** |
| `apply_all.sh --check` | OK |
| `docs/math_status_probes/` after tests | clean |

## Engineering defects → portable patches

| ID | Fix |
|----|-----|
| carriers `__pycache__` false positive | `0001-…` |
| math_console `code_prototypes` paths + PACKET sha/bytes | `0002-…` |
| gaussian moments parametrize iterator | `0003-…` |
| git fixture timeout 10s → 60s | `0004-…` |
| inventable probe test dirty digests (re-cut post-#17) | `0005-…` |
| instrumentation STATUS dirty digests (post-#20) | `0006-…` (**in** `apply_all.sh` since batch 21) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Write probe still 403. No `research.yml` schedule changes. No tip-level **0007**.
