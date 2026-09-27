# Dropbox gap audit — 2026-09-27 (Batch 791 sidecar)

Byte-level diff of Dylan's shared Dropbox folder against (a) the Google Drive
2026-09-17 export + deltas carried on `main@chatgpt/drive-github-hardening-20260919`
and (b) every branch of all 8 owner repos. Narrative and agent routing:
[`docs/DROPBOX_GAP_AUDIT_2026-09-27.md`](../../docs/DROPBOX_GAP_AUDIT_2026-09-27.md).

**Scientific effect: NONE.** `lemma_closed` stays false. Presence/absence of a
file is not a status.

| File | Rows | Meaning |
|---|---:|---|
| `SUMMARY.json` | — | tallies, per-top-dir missing counts, reference provenance |
| `MISSING_FROM_DRIVE.json` | 183 | distinct Dropbox files with **no** SHA-256/name/stem match in the Drive export or deltas |
| `MISSING_FROM_GITHUB.json` | 975 | distinct Dropbox files whose git blob SHA-1 is on **no** branch of any owner repo and whose name matches nothing |
| `MISSING_FROM_BOTH.json` | 166 | intersection |
| `REVISION_DIFFERS_DRIVE.json` | 26 | same title in Drive, different bytes (Drive IDs + digests included) |
| `ZIP_CARRIER_COVERAGE.json` | 37 | per-zip member coverage so a "missing" carrier is not over-read |
| `DROPBOX_INVENTORY.tsv` | 3,325 | every Dropbox file: path, bytes, sha256, drive_match, github_match, github_default_branch, first hit on each side |

Regenerate: `python3 scripts/dropbox_gap_audit.py` (docstring lists the fetch
steps; no Drive credentials required — the Drive side is the committed export).

Peer artifact: `portable/dropbox_intake_2026-09-27/` on trial PR #149
(`cursor/dropbox-intake-digest-309a`) indexes the same corpus; this directory
diffs it. Agent routing: `research` — A1/A2 receipts + revision drift are Drive
backfill candidates for a credentialed session; `tip_or_eng` — 530 matched files
live only on non-default `main` branches (Path C scope, unchanged);
`tip_sync` — awareness only.
