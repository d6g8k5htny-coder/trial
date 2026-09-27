# Review packet — main PR #172 / PR #174 + independent Dropbox replay (2026-09-27)

**Scientific effect: NONE.** Engineering review notes and a byte-level inventory
diff. Nothing here promotes, closes or discharges any claim, premise, prize or
lemma; `lemma_closed` stays false. A green trial test is not research evidence.

Written by the review-assistance cloud agent (run `bc-01a0e43c`, same operator
account as every author cited; zero organizational-independence credit). This
environment cannot post on `d6g8k5htny-coder/main` (PR comments are limited to
the current repository; `gh` is read-only), so the findings travel as a portable
packet per `AGENTS.md`. Whoever next holds `main` write may paste sections 1–2
onto the PRs verbatim.

## 1. main PR #174 — `docs: queue reconciliation record for 2026-09-27`

1. **Ten compiled `.pyc` files are in the diff.** `tests/__pycache__/*.cpython-312.pyc`
   (5) and `tools/__pycache__/*.cpython-312.pyc` (5) are added as binaries in a
   "documentation only" PR. The same PR adds `.gitignore` with `__pycache__/` and
   `*.pyc`, but ignore rules do not apply to files already staged, so they land.
   Fix: `git rm -r --cached tests/__pycache__ tools/__pycache__` and recommit; keep
   the `.gitignore` addition.
2. **`Closes #160` deserves a data point the page does not have yet.** Issue #160
   (LB-RATE / KIMI-THM-023 HOLD) has zero comments and is the tracking issue for
   the HOLD. Between 17:19 and ~19:00 UTC the Dropbox share received a
   `KIMI_EXPORT_2026-08-04_LB` addendum bundle (section 3). Its own ledger reads
   "THM-023 0.9144 proved floor / LB3 R0 CLOSED; gamma-LOC PARTIAL /
   KIMI-AUD-024 HOLD, NOT PROMOTED". None of that changes the HOLD — it is
   `incoming/` review material — but closing the HOLD's tracking issue on the
   day new HOLD-relevant material arrived, with no note of it on the issue, makes
   the HOLD's history harder to follow. Suggest dropping `Closes #160` from #174,
   or adding one line to `QUEUE_RECONCILIATION_20260927.md` recording the
   bundle's arrival and that #160 closes as "recorded", not "resolved".

Everything else checked (navigation registration, `RESEARCH_INDEX` link, quoted
verification commands) reads consistently.

## 2. main PR #172 — `tools/dropbox_reconcile.py`

Cross-check numbers from two independent pulls of the same `scl/fo` share, for
the "real run (private scratch)" section of #172:

| source | when (UTC) | zip bytes | members | distinct SHA-256 |
|---|---|---|---|---|
| trial PR #149 intake digest | 16:53 | 188,397,410 | 2,950 | — |
| trial PR #150 gap audit | ~17:19 | 189,776,398 | 3,325 | 1,695 |
| this replay | ~19:00 | 198,053,310 (sha256 `2ac17b308d0462e3…`) | 4,014 | 1,765 |

Diff #150 → replay: **0 removed, 0 changed, 70 new distinct hashes** (689 new
paths; the rest are further `Q0_Next_Phase_2026-09-12 (1) (N)` duplicate folders
and `textNN.txt` re-uploads). The share is live and growing; any classification
must carry its pull timestamp + zip sha256 as identity. #172's "5,105 Dropbox
files" comes from the API listing (includes app bundles / debris that a zip
download omits), so it is not directly comparable with 4,014 zip members; the
distinct-hash count is the comparable quantity.

Two suggestions for the tool: (a) emit the pull timestamp and a corpus-level
digest in `report`; (b) `content_hash` for a single-block file equals
`sha256(sha256(bytes))` — the TSV in section 3 carries plain sha256, so the tool
can match these rows without any download.

## 3. New Dropbox content since trial PR #150 (review material only)

Full list: [`dropbox_replay_2026-09-27T19Z_new_since_pr150.tsv`](dropbox_replay_2026-09-27T19Z_new_since_pr150.tsv)
(path, bytes, sha256, duplicate-path count; 70 rows).

- `KIMI_EXPORT_2026-08-04_LB` addendum: `925KIMI-THM-023.md`, `924KIMI-AUD-024.md`,
  `925LB1_sup_over_zone_proof.md` + `925lb1_sup_over_zone_certificate.py`,
  `LB2_mean_ridge_proof.md` + `lb2_cert.py`, `LB3_DISCHARGE.md` +
  `lb3_certificate.py`, `lb1_t_O.txt`, `lb2_transcript.txt`, `lb3_transcript_O.txt`,
  `MANIFEST.sha256` (14 entries), `README925.txt`, `Kimipacket.md`.
  Subject of main issue #160. Must go through `incoming/` review; its
  self-description is not a status change anywhere.
- `research_archive_round3/` (2 files + zip), `research_archive_round15/`
  (8 files + zip: findings, methodology, open questions, pass report,
  relative-contribution CSV/PNG, terminology).
- `LPW_CONSTANT_V2_REPORT.pdf`, `KIMI_LPW_VERDICT_ADDENDUM_4.pdf`,
  `HLV_Manuscript_Updated_Dec2025.docx`, `sgr/data` + `sgr.txt.gz`, `Untitled.kml`,
  `text57 … text116.txt` (36 files).
- Personal-looking file present: `electrianresume.docx` — #172's personal-name
  filter should hold it from any GitHub staging.

## 4. Trial-side context (for whoever lands on `main`)

Trial CI has been red on `main` since 2026-09-26 13:16 because every Path C tip
gate required `live hardening SHA == BASE_TIP` while Path C is landed and the
wake loop keeps BASE_TIP immutable. Three trial PRs fix it (#152 content check,
#153 DESCENDANT_OK + BASE_TIP refresh + lands #150, #154 landed-ancestor gate);
a convergence recommendation is on #153. Not a `main` matter beyond noting that
trial red was never evidence of anything about `main`.
