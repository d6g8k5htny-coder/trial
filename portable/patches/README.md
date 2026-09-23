# Portable patches for `d6g8k5htny-coder/main`

Base tip (see `BASE_TIP.txt`):
`chatgpt/drive-github-hardening-20260919` @ `3e8f38845cb350f43a64b8784400338c8e9a78f6`
(includes merged inventable PR #15, docs #16, math_status PARTIAL/REFUSED #18, and
fail-closed JETMOD shortcut refusals #17).

**Scientific effect: NONE.** No claim/premise/lemma status moves.

## Apply

From a clean checkout of that tip (or a descendant):

```bash
# From a clean checkout of d6g8k5htny-coder/main at the base tip:
/path/to/trial/portable/patches/apply_all.sh --check   # dry-run only
/path/to/trial/portable/patches/apply_all.sh           # apply 0001–0005
# or apply individually:
git apply /path/to/trial/portable/patches/0001-carriers-verify-ignore-bytecode-caches.patch
git apply /path/to/trial/portable/patches/0002-math-console-path-honesty.patch
git apply /path/to/trial/portable/patches/0003-gaussian-moments-parametrize-list.patch
git apply /path/to/trial/portable/patches/0004-git-fixture-timeout-60s.patch
git apply /path/to/trial/portable/patches/0005-inventable-probes-restore-receipts-after-test.patch
```

Verify:

```bash
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py
# expect: problems=0, lemma_closed=false; 86 passed on that slice @ 3e8f388
# and docs/math_status_probes/ stays clean in git status after the inventable test
```

## Optional (not in `apply_all.sh`)

- `0005-pre17-inventable-probes-restore-receipts-after-test.patch` — pre-#17 inventable test shape (older SHAs before tip-cut 0005). Prefer tip-cut **0005** on current PR #20 (`4103ee1`+) when it applies.
- `0006-instrumentation-status-restore-receipts-after-test.patch` — same dirty-digest fix for PR #20 instrumentation STATUS tests (`tests/test_inventable_jetmod_instrumentation_status.py`).

### When to promote **0006** into `apply_all.sh`

Promote **0006** into `apply_all.sh` **only after** PR #20 (or equivalent) merges so that `tests/test_inventable_jetmod_instrumentation_status.py` exists on the hardening tip. Until then:

1. Keep 0006 optional (not listed in `apply_all.sh`).
2. On PR #20 heads: apply tip `0001–0005` (or `0001–0004` + `0005-pre17` on older heads) then **0006**.
3. After merge: add the 0006 path to `PATCHES=(…)` in `apply_all.sh`, refresh `BASE_TIP.txt`, and re-run focused tests including the instrumentation file.

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

## 0006 — instrumentation STATUS test restores receipts (optional)

Same class as 0005 for `tests/test_inventable_jetmod_instrumentation_status.py`
on PR #20. Not in `apply_all.sh` until that file exists on the hardening tip.
