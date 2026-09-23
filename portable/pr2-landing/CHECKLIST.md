# Landing checklist: merge Drive→git port onto default `main`

**Scientific effect: NONE** if you only merge already-reviewed packaging.
Do **not** enable `research.yml` schedules solely to satisfy R2-06 prose.

## Why this is the critical path

Default `main` @ `f25b04bb931df2eaee302b666db014913486166b` still advertises the
abandoned complexity-physics README. The live program is the unmerged stack:

```
main
  ↑ PR #2 (MERGEABLE, CLEAN, draft)  claude/drive-audit-github-migration-rrglpp @ b1335def
      ↑ PR #3 (draft)  chatgpt/drive-github-hardening-20260919 @ 1ea0ae8 (includes merged #15)
          ↑ feature PRs (inventable #15, etc.)
```

Observed 2026-09-23 (this agent, read-only):

| PR | mergeable | mergeStateStatus | notes |
|----|-----------|------------------|-------|
| [#2](https://github.com/d6g8k5htny-coder/main/pull/2) | **MERGEABLE** | **CLEAN** | 3879 files; CI verify SUCCESS |
| [#3](https://github.com/d6g8k5htny-coder/main/pull/3) | (draft onto migration) | | RN wedge / hardening |
| [#15](https://github.com/d6g8k5htny-coder/main/pull/15) | **MERGED** into hardening @ `1ea0ae8` | — | inventable REFUSED receipts only; obligations stay OPEN |

## Recommended owner sequence

1. **Review PR #2** as the public face of the repository (registers, tools, docs).
2. Mark ready → merge into `main` when satisfied (or temporarily switch GitHub default branch to the migration tip — same visitor outcome).
3. Then land PR #3 / hardening onto the new `main` (or retarget after #2 merges).
4. Then consider inventable #15 (fail-closed REFUSED probes; does **not** discharge OBL-H5-JETMOD).
5. Apply portable engineering patches from `../patches/` on the integration tip if not already present:
   - `0001-carriers-verify-ignore-bytecode-caches.patch`
   - `0002-math-console-path-honesty.patch` (includes PACKET.json digest refresh)
   - or run `portable/patches/apply_all.sh` on a writable checkout

## Verification after #2 lands

```bash
python3 tools/math_status_check.py   # expect lemma_closed=false, OPEN_HOLD
python3 -m pytest -q
python3 docs/math_status/math_console.py --json
```

Expect obligations still OPEN. A green run is not premise discharge.

## If you are not ready to merge #2

Apply Option-B redirect README from `../main-default-branch/` so visitors are not
misled, without claiming scheduled workflows are deployed.

## Agent write access

Cloud agents on the `trial` environment currently receive **403** when pushing to
`d6g8k5htny-coder/main`. Re-launch against `main` with write credentials to apply
patches or open PRs there directly.
