# Rebase / close notes for CONFLICTING drafts on `main`

**Scientific effect: NONE.** Read-only conflict inventory from merge probes
on 2026-09-23. This agent cannot push to `main`.

## PR #12 — `cursor/math-status-open-hold-20260922-e340`

- Base: `chatgpt/drive-github-hardening-20260919`
- Status: **CONFLICTING / DIRTY**
- Cause: inventable PR #15 (and follow-ons) landed math_status files that PR #12
  also introduced as add/add.

Conflict paths:

```
docs/math_status/PACKET.json
docs/math_status/README.md
docs/math_status/STATUS.md
docs/math_status/STATUS_JETMOD.md
docs/math_status/STATUS_MATH_PUSH_2026-09-21.md
docs/math_status/math_console.py
tests/test_math_status.py
tools/math_status_check.py
```

**Recommendation:** Close PR #12 as superseded. Useful path-honesty for
`math_console` is carried by trial portable patch `0002-math-console-path-honesty.patch`
(includes PACKET digest refresh). Do not force-merge PR #12 over #15 receipts.

## PR #3 — `chatgpt/drive-github-hardening-20260919` → migration

- Base: `claude/drive-audit-github-migration-rrglpp`
- Head: hardening tip
- Status: **CONFLICTING / DIRTY** when merging head into the recorded base tip
  (probe: merge hardening into `b1335de`).

Conflict paths:

```
docs/OPEN_PROBLEMS.md
engine/lanes/A1.json
engine/lanes/A5.json
tools/drive_index.py
```

**Recommendation:** After Path A (merge PR #2 into default `main`), retarget
hardening as a PR onto the new `main` (or merge-migration-then-hardening in
order) and resolve these four files explicitly. Prefer hardening’s lane/driver
truth for A1/A5 unless a review says otherwise; reconcile OPEN_PROBLEMS and
`drive_index.py` with register byte-exactness rules (no silent register edits).

## Still clean / critical

| PR | State | Action |
|----|-------|--------|
| #2 | MERGEABLE/CLEAN onto default `main` | **Land this** (Path A) |
| #7, #8 | MERGEABLE/CLEAN onto hardening | Independent reviews |
| #17 | **Merged** @ `3e8f388` | Tip-cut portable **0005** applies on tip |
| #19 | **Merged** @ `ae7daf7` | AUTHOR_SIDE honesty banners; BASE_TIP → `ae7daf7` (batch 25); no status flip |
| #20 | **Merged** @ `1547ec4` | Instrumentation STATUS on tip; portable **0006**–**0008** now in `apply_all.sh` |
| #21 | Attestations + H3 salvage (`52bdd443`) | MERGEABLE/**UNSTABLE** onto hardening; not a status discharge |

## Merged since these notes started

| PR | Merge | Note |
|----|-------|------|
| #15 | inventable probes → hardening | Tip ancestors include receipts |
| #16 | cold-start nav docs | Docs-only |
| #18 | PARTIAL/REFUSED JETMOD STATUS vocab → hardening @ `340d98a` | Supersedes overlapping #12 math_status intent; **not** a discharge |
| #17 | Fail-closed inventable JETMOD shortcut refusals → hardening @ `3e8f388` | Expanded inventable EXPECTED/SHORTCUTS; tip-cut 0005 re-cut; **not** a discharge |
| #20 | PARTIAL/REFUSED_NOT_24JET instrumentation STATUS → hardening @ `1547ec4` | Promoted portable **0006**; **not** a discharge |
| #19 | AUTHOR_SIDE honesty banners → hardening @ `ae7daf7` | Digest-only PACKET refresh; flags stay false; **not** a discharge |

## Non-claims

Closing or rebasing these drafts does not discharge OBL-H5-JETMOD or
D3-LEMMA-RN-UNIF.
