# Portable patches for `d6g8k5htny-coder/main`

Base tip (see `BASE_TIP.txt`):
`chatgpt/drive-github-hardening-20260919` @ `5f352a2d16aeb260defabffb6154e0ebca8bd23a`
(batch 73: BASE_TIP unchanged; CI land-workflows-dry-run without MAIN_PUSH_TOKEN; no 0017;
batch 71: BASE_TIP confirmed == live hardening; re-verify apply_all + residual RW IDLE / no 0017;
batch 70: tip refresh via PR #44 fail-closed vault path map; prior BASE_TIP `74c082e` / #45)
(includes merged inventable PR #15, docs #16, math_status PARTIAL/REFUSED #18,
fail-closed JETMOD shortcut refusals #17, instrumentation STATUS vocab #20,
AUTHOR_SIDE honesty banners #19, docs STATUS honesty cross-links #22,
PACKET base_commit/as_of tip-align #23, standing owner authorization #25,
inventable STATUS honesty cross-links #24, math_status README inventable
probes honesty pointer #26, probe-test isolation #27, register R1
exact-byte custody #29, STATUS_JETMOD inventable merge+promote REFUSED
honesty #28, STATUS_RN_UNIF inventable ABSENT/EMPTY honesty #30,
register source preflight #31, agent-decided governance delegation,
AGENTS.md bridge / CLAUDE.md mirror-quote fix #35, inventable probe
index tip provenance fail-closed #34, inventable REFUSED/EMPTY/ABSENT
honesty walls tip provenance #43, SIDE24 nav/prep honesty deepen #42,
and checked cover-accounting boundary for RN replay #45).

**Post-#41 tip topology:** default `main` @ `1c6e74b` is ALIGNED landing
(not Path-C shaped). Apply these patches only on hardening BASE_TIP.
Do not `PATH_C_BASE=main`. See [`COMPATIBILITY.md`](COMPATIBILITY.md).

**Scientific effect: NONE.** No claim/premise/lemma status moves.

## Apply

From a clean checkout of that tip (or a descendant):

```bash
# From a clean checkout of d6g8k5htny-coder/main at the base tip:
/path/to/trial/portable/patches/apply_all.sh --check   # dry-run only
/path/to/trial/portable/patches/apply_all.sh           # apply 0001–0004 + 0008–0016
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
git apply /path/to/trial/portable/patches/0015-frozen-drive-index-close-file-handles.patch
git apply /path/to/trial/portable/patches/0016-receipts-bridge-close-file-handles.patch
```

Verify:

```bash
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
  tests/test_inventable_jetmod_instrumentation_status.py tests/test_claims.py \
  tests/test_recovery.py
# expect: problems=0, lemma_closed=false; 90 focused + 47 claims + 36 recovery @ 580864c
# and docs/math_status_probes/ stays clean in git status after inventable tests
# focused+claims+recovery emit no ResourceWarning (unclosed file) after 0008–0016
# math_status_check itself emits 0 ResourceWarning after 0011
# verify_manifests + quarantine_check emit 0 ResourceWarning after 0013
# collision_proposal_check + tests/test_collision_proposal.py emit 0 ResourceWarning after 0014
# tests/test_frozen_check.py + test_drive_index_overlay.py emit 0 ResourceWarning after 0015
# tests/test_receipts.py + test_bridge.py emit 0 ResourceWarning after 0016
```

## Historical / optional

- `0005-pre17-inventable-probes-restore-receipts-after-test.patch` — pre-#17 inventable test shape (older SHAs before tip-cut 0005).
- Tip-cut **0005** / **0006** / **0007** — pre-#27 dirty-receipt restore + close-handles. **Dropped from `apply_all.sh` after PR #27 merged** @ `bf1fde3` (batch 48). Isolation already restores the dirty-receipt contract via `tmp_path` + `_probe_snapshot()`; post-#27 residual bare `open()` in negative inventable/instrumentation tests is covered by **0012**. Files kept on disk for history only.

### When 0006 was promoted

Instrumentation STATUS vocab landed via main PR #20; 0006 was promoted into
`apply_all` then later dropped with tip-cut 0005 after PR #27.

## Patch list (live stack)

| Patch | Role |
|-------|------|
| 0001 | carriers_verify ignore `__pycache__` / bytecode |
| 0002 | math_console path honesty + PACKET digests |
| 0003 | gaussian moments parametrize list |
| 0004 | git fixture timeout 60s |
| 0008 | carriers + math_status close file handles |
| 0009 | claims close file handles |
| 0010 | recovery close file handles |
| 0011 | math_status_check close file handles |
| 0012 | inventable-negative tests close file handles |
| 0013 | verify_manifests + quarantine_check close file handles |
| 0014 | collision_proposal_check + tests close file handles |
| 0015 | frozen_check + drive_index_overlay close file handles |
| 0016 | receipts + bridge tests close file handles |

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for tip × stack matrix.
