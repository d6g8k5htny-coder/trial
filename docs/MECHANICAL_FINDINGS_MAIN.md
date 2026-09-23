# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `a89f9a703739aed9d290c94d68f80bf4e8bd9d62`
(PR #22 docs STATUS honesty cross-links; prior #15/#16/#17/#18/#19/#20).
Host: CPython 3.12.3 + pytest.
**Scientific effect: NONE.**

## After portable patches 0001–0008 on `a89f9a7` (batch 31)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian + instrumentation | **90 passed** |
| `apply_all.sh --check` | OK |
| focused slice ResourceWarning | **0** (after 0007+0008) |
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
| inventable tests unclosed-file ResourceWarning | `0007-…` (**in** `apply_all.sh` since batch 24) |
| carriers + math_status + `carriers_verify` unclosed-file ResourceWarning | `0008-…` (**in** `apply_all.sh` since batch 25) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Path A potential merge commit README still would-align (q0 markers).
Write probe still 403. No `research.yml` schedule changes.
