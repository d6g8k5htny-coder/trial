# Portable patches for `d6g8k5htny-coder/main`

Base tip (see `BASE_TIP.txt`):
`chatgpt/drive-github-hardening-20260919` @ `85108745ed4444adb838c53ae79cd603ed90f6fc`
(includes merged inventable PR #15, docs #16, math_status PARTIAL/REFUSED #18,
fail-closed JETMOD shortcut refusals #17, instrumentation STATUS vocab #20,
AUTHOR_SIDE honesty banners #19, docs STATUS honesty cross-links #22,
PACKET base_commit/as_of tip-align #23, standing owner authorization #25,
inventable STATUS honesty cross-links #24, math_status README inventable
probes honesty pointer #26, probe-test isolation #27, and register R1
exact-byte custody #29).

**Scientific effect: NONE.** No claim/premise/lemma status moves.

## Apply

From a clean checkout of that tip (or a descendant):

```bash
# From a clean checkout of d6g8k5htny-coder/main at the base tip:
/path/to/trial/portable/patches/apply_all.sh --check   # dry-run only
/path/to/trial/portable/patches/apply_all.sh           # apply 0001–0004 + 0008–0015
# or apply individually:
git apply /path/to/trial/portable/patches/0001-carriers-verify-ignore-bytecode-caches.patch
git apply /path/to/trial/portable/patches/0002-math-console-path-honesty.patch
git apply /path/to/trial/portable/patches/0003-gaussian-moments-parametrize-list.patch
git apply /path/to/trial/portable/patches/0004-git-fixture-timeout-60s.patch
# SKIP tip-cut 0005/0006/0007 after PR #27 (obsolete; kept on disk for history)
git apply /path/to/trial/portable/patches/0008-carriers-math-status-close-file-handles.patch
git apply /path/to/trial/portable/patches/0009-claims-close-file-handles.patch
git apply /path/to/trial/portable/patches/0010-recovery-close-file-handles.patch
git apply /path/to/trial/portable/patches/0011-math-status-check-close-file-handles.patch
git apply /path/to/trial/portable/patches/0012-inventable-negative-tests-close-file-handles.patch
git apply /path/to/trial/portable/patches/0013-verify-quarantine-close-file-handles.patch
git apply /path/to/trial/portable/patches/0014-collision-close-file-handles.patch
```

Verify:

```bash
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
  tests/test_inventable_jetmod_instrumentation_status.py tests/test_claims.py \
  tests/test_recovery.py
# expect: problems=0, lemma_closed=false; 90 focused + 47 claims + 36 recovery @ 8510874
# and docs/math_status_probes/ stays clean in git status after inventable tests
# focused+claims+recovery emit no ResourceWarning (unclosed file) after 0008–0015
# math_status_check itself emits 0 ResourceWarning after 0011
# verify_manifests + quarantine_check emit 0 ResourceWarning after 0013
# collision_proposal_check + tests/test_collision_proposal.py emit 0 ResourceWarning after 0014
```

## Historical / optional

- `0005-pre17-inventable-probes-restore-receipts-after-test.patch` — pre-#17 inventable test shape (older SHAs before tip-cut 0005).
- Tip-cut **0005** / **0006** / **0007** — pre-#27 dirty-receipt restore + close-handles. **Dropped from `apply_all.sh` after PR #27 merged** @ `bf1fde3` (batch 48). Isolation already restores the dirty-receipt contract via `tmp_path` + `_probe_snapshot()`; post-#27 residual bare `open()` in negative inventable/instrumentation tests is covered by **0012**. Files kept on disk for history only.

### When 0006 was promoted

PR #20 merged into hardening @ `1547ec4` (batch 21). `tests/test_inventable_jetmod_instrumentation_status.py` exists on the tip, so **0006** was listed in `apply_all.sh` alongside 0001–0005 until batch 48 dropped it after #27.

## 0001 — `carriers_verify` ignores bytecode caches

Importing a stored blob creates `blobs/__pycache__/`. Without this patch,
`carriers_verify` reports an unreferenced “blob” and exits 1 even though
`.gitignore` already ignores `__pycache__/`.

## 0002 — `math_console` path honesty + PACKET digest

Usage/commands pointed at missing `code_prototypes/`; `ROOT` was `docs/` not
the repo root. Editing `math_console.py` **requires** refreshing
`docs/math_status/PACKET.json` transcription digests; otherwise
`math_status_check` fails closed on sha256/bytes drift (observed: 3 tests fail
if the digest is omitted). Status flags in PACKET stay false/OPEN_HOLD.

## 0003 — gaussian moments parametrize list

`tests/test_gaussian_moments.py` passed a lazy `product(...)` iterator to
`pytest.mark.parametrize`, which pytest 9 warns will break. Convert to
`list(product(...))`. No scientific change.


## 0004 — git fixture timeout 60s

`tests/test_run_checks.py` and `tests/test_workflow_integrity_hardening.py` git
helpers used a 10s timeout around `git commit` (both kwarg orderings). On loaded VMs this intermittently
raises `TimeoutExpired` during setup (observed twice). Raise to 60s. No
scientific change.

## 0005 — inventable probe test restores receipts

`tests/test_inventable_jetmod_probes.py::test_runner_writes_refused_receipts_only`
runs `inventable_jetmod_probes.py`, which rewrites `generated_at_*` and refreshes
`INVENTABLE_PROBES_INDEX.json` digests in-tree. The test already snapshotted
`before` bytes but never restored them, so every pytest leave dirty
sha256/timestamp drift under `docs/math_status_probes/`. Restore in `finally`
(including the index). Batch 17 re-cut against post-#17 EXPECTED/SHORTCUTS.
No scientific change; `lemma_closed` stays false.

**Obsolescence (PR #27):** open main PR #27 rewrites the same test to run under
`tmp_path` and assert source receipts unchanged. After #27 merges into the
hardening tip, tip-cut **0005 is obsolete** (drop from `apply_all.sh`); do not
keep a parallel `0005-pr27-*` restore patch.

## 0006 — instrumentation STATUS test restores receipts

Same class as 0005 for `tests/test_inventable_jetmod_instrumentation_status.py`
(landed with PR #20 @ `1547ec4`). Now included in `apply_all.sh`.

## 0007 — inventable tests close file handles

After 0005/0006 restore logic, inventable probe + instrumentation STATUS tests
still used bare `open(...).read()` / `json.load(open(...))` / `json.dump(..., open(...))`
without closing handles. Under CPython 3.11 this emits many `ResourceWarning:
unclosed file` lines on the inventable slice (observed: 34 warnings across the
registers/inventable/ci/workflow audit). Use `Path.read_bytes()` for snapshots
and `with open(...)` for JSON IO. No scientific change; `lemma_closed` stays false.

## 0008 — carriers + math_status close file handles

Same class as 0007 for `tests/test_carriers.py`, `tests/test_math_status.py`, and
`tools/carriers_verify.py`. After 0001–0007 on tip `ae7daf7`, the focused slice
still emitted **63** `ResourceWarning: unclosed file` lines (22 carriers test +
41 math_status; plus ~22 from `carriers_verify` under `-W default`). Use
`with open(...)` for blob hashing and status mutation helpers. No scientific
change; `lemma_closed` stays false.

## 0009 — claims tests close file handles

Same class as 0007/0008 for `tests/test_claims.py` register-binding helpers.
After 0001–0008 on tip `b02efe2` @ CPython 3.11, `test_claims` still emitted
**19** `ResourceWarning: unclosed file` lines from bare
`json.load(open(...))` / `open(...).read()` on register JSON + mirror bytes
(workflow_integrity / run_checks / registers / ci_pins slices were otherwise
clean). Use `with open(...)`. No scientific change; `lemma_closed` stays false.

## 0010 — recovery tests + checker close file handles

Same class as 0007–0009 for `tests/test_recovery.py` and `tools/recovery_check.py`.
After 0001–0009 on tip `46af1ca` @ CPython 3.11, `test_recovery` still emitted
**234** `ResourceWarning: unclosed file` lines from bare
`open(...).read()` / `json.load(open(...))` / `json.dump(..., open(...))` in
fixture writers, ledger readers, and `quarantined_digests` / `check` / `main`.
Use `with open(...)`. No scientific change; `lemma_closed` stays false.

## 0011 — math_status_check close file handles

Same class as 0008/0010 for `tools/math_status_check.py` packet readers.
After 0001–0010 on tip `a8a5dd7` @ CPython 3.11, running
`python3 -W default::ResourceWarning tools/math_status_check.py` still emitted
**30** `ResourceWarning: unclosed file` lines from bare `open(...).read()` on
transcription digests, STATUS prose, `math_console.py`, snapshot, and
`PACKET.json`. Use `with open(...)`. No scientific change; `lemma_closed`
stays false.

## 0012 — inventable negative tests close file handles (post-#27)

After main [PR #27](https://github.com/d6g8k5htny-coder/main/pull/27) merged @
`bf1fde3`, tip-cut 0005/0006/0007 no longer apply. Isolation already covers the
dirty-receipt contract, but negative inventable/instrumentation tests still used
bare `json.load(open(...))` / `json.dump(..., open(...))` on tmp_path copies —
**6** `ResourceWarning: unclosed file` on the focused slice. **0012** closes those
handles. Use `with open(...)`. No scientific change; `lemma_closed` stays false.

## 0013 — verify_manifests + quarantine_check close file handles

Same class as 0008–0015 for `tools/verify_manifests.py` and
`tools/quarantine_check.py`. On tip `bf1fde3` @ CPython 3.11, each tool still
emitted **828** `ResourceWarning: unclosed file` lines from bare
`for line in open(...)` over manifest `.jsonl` / `.sha256` files. Use
`with open(...) as handle`. Output parity preserved (`problems=0`). No scientific
change; `lemma_closed` stays false.

## 0014 — collision_proposal_check + tests close file handles

Same class as 0008–0013 for `tools/collision_proposal_check.py` and
`tests/test_collision_proposal.py`. On tip `8510874` @ CPython 3.11 (also on
prior `bf1fde3`), the checker emitted **2** `ResourceWarning: unclosed file`
from bare `open(...).read()` on the default proposal path, and the test module
emitted **51** from helpers / digest asserts / sandbox overrides. Use
`with open(...) as handle`. Output parity preserved (`failures=0` /
**189 passed**). No scientific change; `lemma_closed` stays false.

## 0015 — frozen / drive-index overlay close-file-handles (batch 52)

Same class as 0008–0014 for `tests/test_frozen_check.py` and
`tests/test_drive_index_overlay.py` bare `open()` calls that emit
`ResourceWarning: unclosed file` under CPython 3.11 `-Wdefault`.
Scientific effect: NONE.
