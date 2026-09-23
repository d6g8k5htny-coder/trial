# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `b02efe21d8d7475ac9b4aa25b3dcc26a5b6f4bf4`
(PR #25 standing owner authorization; prior #15/#16/#17/#18/#19/#20/#22/#23).
Host: CPython 3.12.3 + pytest (tip); PR #27 head also verified @ 3.11.
**Scientific effect: NONE.**

## PR #27 head `8d023a9` + stack 0001–0004 + 0008 (batch 41)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`) |

## After portable patches 0001–0008 on `b02efe2` (batch 38)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian + instrumentation | **90 passed** |
| `apply_all.sh --check` | OK |
| focused slice ResourceWarning | **0** (after 0007+0008) |
| `docs/math_status_probes/` after tests | clean |

## After portable patches 0001–0008 on `3f85e93` (batch 35)

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
