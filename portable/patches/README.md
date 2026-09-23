# Portable patches for `d6g8k5htny-coder/main`

Base tip (see `BASE_TIP.txt`):
`chatgpt/drive-github-hardening-20260919` @ `340d98a2371bf181214c431f18f5c53945ee9d79`
(includes merged inventable PR #15, cold-start nav #16, and math_status PARTIAL/REFUSED #18).
Patches were originally cut against `1ea0ae8` and still apply cleanly on this descendant
(0005 is tip-shaped; see COMPATIBILITY for PR #17).

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
# expect: problems=0, lemma_closed=false; 86 passed on that slice @ 340d98a
# and docs/math_status_probes/ stays clean in git status after the inventable test
```

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
(including the index). No scientific change; `lemma_closed` stays false.
