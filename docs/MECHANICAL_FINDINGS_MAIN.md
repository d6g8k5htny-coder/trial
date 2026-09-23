# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `a8a5dd775aa685d1616cbda874429952aa5fbf9c`
(PR #26 math_status README inventable probes honesty; prior #15/#16/#17/#18/#19/#20/#22/#23/#24/#25).
Host: CPython 3.11 + pytest (tip batch 46); PR #27 head also verified @ 3.11.
**Scientific effect: NONE.**

## After portable patches 0001–0010 on `a8a5dd7` (batch 46)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0010) |

## PR #27 head `20e31a1` + stack 0001–0004 + 0008 (+0009/0010) (batch 46; prior `63b519f`)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` (+ optional 0009/0010) | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`); #27 still OPEN → not dropped |

## After portable patches 0001–0010 on `46af1ca` (batch 45)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0010) |
| recovery unclosed-file ResourceWarning | cleared by **0010** (was 234) |

## After portable patches 0001–0009 on `46af1ca` (batch 44)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims | **137 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0009) |

## PR #27 head `63b519f` + stack 0001–0004 + 0008 (batch 44; prior `8d023a9` @ batch 41)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` (+ optional 0009) | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`); #27 still OPEN → not dropped |

## After portable patches 0001–0009 on `b02efe2` (batch 43)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims | **137 passed**; **0 ResourceWarning** |
| broader: workflow_integrity / run_checks / registers / ci_pins | **110 / 45 / 53 / 25** passed |
| `apply_all.sh --check` | OK (0001–0009) |
| claims unclosed-file ResourceWarning | cleared by **0009** (was 19) |

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
| claims register-binding unclosed-file ResourceWarning | `0009-…` (**in** `apply_all.sh` since batch 43) |
| recovery + recovery_check unclosed-file ResourceWarning | `0010-…` (**in** `apply_all.sh` since batch 45) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Path A potential merge commit README still would-align (q0 markers).
Write probe still 403. No `research.yml` schedule changes.
