# Mechanical findings on `d6g8k5htny-coder/main` (hardening tip)

Scientific effect: **NONE**. These are engineering / ResourceWarning hygiene notes only.

## After portable patches 0001–0004 + 0008–0016 on `9a56c30` (batch 57)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `9a56c30` (== BASE_TIP; no tip move) |
| `math_status_check` | problems=0 / lemma_closed=false |
| focused+claims+recovery | **173 passed** / **0 ResourceWarning** |
| frozen/dio/receipts/bridge/collision | **0 ResourceWarning** |
| RN suite | **438 passed** / **0 ResourceWarning** |
| tools `--help` | **0 ResourceWarning** |
| new portable **0017** | **none** (IDLE) — Path B automation shipped instead |

Default `main` @ `4fc1d7c` still **MISALIGNED**; Path B would-align via `path_b_dry_run.py`; write 403.

Tip residuals (not portable): `mirror_quotes` 3 + bridge AGENTS.md drift → open PR #35.

## After portable patches 0001–0004 + 0008–0016 on `580864c` (batch 53b)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `580864c` (PR #31; BASE_TIP refreshed) |
| Default `main` @ `4fc1d7c` | **MISALIGNED** after CoS PR #32; Path B preferred / still valid; write 403 |

Default `main` @ `4fc1d7c` is **MISALIGNED** after CoS PR #32 reverted PR #2. Path C apply target remains hardening BASE_TIP (`580864c` after PR #31).

## After portable patches 0001–0004 + 0008–0016 on `fbb4360` (batch 53)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK (0001–0004 + 0008–0016; 0005/0006/0007 dropped) |
| `math_status_check` | problems=0 / lemma_closed=false / 0 ResourceWarning |
| focused+claims+recovery+frozen/dio | **192 passed** / **0 ResourceWarning** |
| receipts + bridge | **541 passed** / **0 ResourceWarning** (was 24 before 0016) |
| collision checker/tests | **0 ResourceWarning** after 0014 |

Residual hunt: no further bare-open ResourceWarnings in receipts/bridge after 0016.

Default `main` @ `4fc1d7c` is **MISALIGNED** after CoS PR #32 reverted PR #2. Path C apply target was hardening BASE_TIP (`fbb4360` after PR #30; refreshed to `580864c` in batch 53b).

## After portable patches 0001–0004 + 0008–0015 on `8510874` (batch 52)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK (0001–0004 + 0008–0015; 0005/0006/0007 dropped) |
| `math_status_check` | problems=0 / lemma_closed=false / 0 ResourceWarning |
| focused+claims+recovery | **173 passed** / **0 ResourceWarning** |
| frozen + drive-index overlay | **19 passed** / **0 ResourceWarning** (was 9+1 before 0015) |
| collision checker/tests | **0 ResourceWarning** after 0014 |

Residual (shipped in batch 53 as **0016**): `tests/test_receipts.py` / `tests/test_bridge.py` bare-open ResourceWarnings.

Post-#2 default `main` @ `b040bf0c` is ALIGNED but a different tree (no `docs/math_status/PACKET.json`) — Path C apply target remains hardening BASE_TIP.

# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `bf1fde30c7fc04c9919bf9172ee8a13e234c7664`
(PR #27 probe-test isolation; prior #15/#16/#17/#18/#19/#20/#22/#23/#24/#25/#26).
Host: CPython 3.11 + pytest (tip batch 48).
**Scientific effect: NONE.**

## After portable patches 0001–0004 + 0008–0012 on `bf1fde3` (batch 48)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false`; **0 ResourceWarning** |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0004 + 0008–0012; 0005/0006/0007 dropped) |
| inventable-negative unclosed-file ResourceWarning | cleared by **0012** (was 6) |

## After portable patches 0001–0011 on `a8a5dd7` (batch 47)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false`; **0 ResourceWarning** |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0011) |
| math_status_check unclosed-file ResourceWarning | cleared by **0011** (was 30) |

## PR #27 merged `bf1fde3` (batch 48; prior head `20e31a1`)

| Check | Result |
|-------|--------|
| tip-cut 0005/0006/0007 | **dropped** from `apply_all.sh` (obsolete) |
| stack `0001–0004 + 0008–0012` | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery @ 3.11 | **173 passed**; **0 ResourceWarning** |


## After portable patches 0001–0010 on `a8a5dd7` (batch 46)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0010) |

## PR #27 head `20e31a1` + stack 0001–0004 + 0008 (+0009/0010/0011) (batch 46/47; prior `63b519f`)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` (+ optional 0009/0010/0011) | applies clean |
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
| `math_status_check` packet-reader unclosed-file ResourceWarning | `0011-…` (**in** `apply_all.sh` since batch 47) |
| inventable-negative unclosed-file ResourceWarning (post-#27) | `0012-…` (**in** `apply_all.sh` since batch 48; replaces obsolete 0007) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Path A potential merge commit README still would-align (q0 markers).
Write probe still 403. No `research.yml` schedule changes.
