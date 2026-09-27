# Dropbox gap hunt — 2026-09-27

Scientific effect: **NONE**. `lemma_closed=false`. Nothing here promotes, closes,
reopens or relabels any claim, premise, prize, lemma or OPEN_PROBLEMS row.
This folder is a portable evidence record, not a vault mirror.

## Task

Download the Dropbox shared folder, open every archive recursively, read every
item, and keep **only** the information the program has been looking for and does
not already hold.

## What was searched

| Item | Value |
|---|---|
| Dropbox folder zip | 198,053,310 B, sha256 `2ac17b308d0462e30508470c9b5e1d5f0b02cc08032d1bb934fd0e5be9711214` |
| Files after recursive extraction | 8,498 (65 nested archives opened: zip / gz / dmg) |
| Distinct byte objects | 2,583 (1,764 outside the stock `ChatGPT.dmg` installer) |
| Text conversion | every file converted (pdftotext, python-docx, tesseract OCR, `dis` for pyc, pickletools, `strings` for binaries); 1,049,614 corpus lines grepped |

"Already held" was decided against, in order:

1. exact git-blob SHA-1 match against **every blob on all 128 branches** of
   `d6g8k5htny-coder/main`, plus this repo;
2. exact SHA-256 match against the members of **all 161 archive blobs** committed in
   `main` (downloaded and expanded recursively);
3. SHA-256 cited anywhere in `main` text — `drive/inventory.jsonl` (the 4,456-item
   Drive vault inventory), `drive/source_map/*.csv` (11,649 archive members),
   registers, recovery, docs, research, claims (7,523 digests harvested).

Result: 917 objects held by exact bytes, 592 more held by Drive-inventory digest,
**255 not held anywhere** (`NEW_UNSOUGHT_INVENTORY.json`, metadata only).

## What was wanted

The wanted list was taken from `main`'s own gap records: `recovery/LEDGER.json`
(UNRECOVERABLE / CANDIDATE digests), `recovery/SOURCE_RECOVERY.json`
`still_unresolved`, `docs/math_status/STATUS_RN_UNIF.md` ABSENT objects,
`docs/math_status/STATUS_JETMOD.md` missing objects, `OPEN_PROBLEMS.md` OQ-016 /
U1 / U2, `drive/source_map/Exceptions.csv` (EMPTY_NATIVE_BODY, READ_FAILED,
ARCHIVE_READ_FAILURE, ENCODED_BLOCK_FAILURE, BINARY_UNRENDERED), the AO48-AUD-065
ferry list, and this repo's `portable/BATCH*_HUNT*.json` (engineering tokens).
Every item is listed with its outcome in `WANTED_LIST_RESULTS.json`.

## Findings

- **No digest-bound wanted object is in the Dropbox.** All nine digest-bound
  targets (cl_der_239_verify.py, cl_dq001_verifier.py, both LS-DATA-015 TB-G2
  payloads, GP-DATA-114 source, TRC-EC020 manifest, Module I §3 extraction,
  V3.3/V5 adjudication checkpoint zip, C022 Observed Update.json) are absent;
  where their digests occur at all it is as citations inside already-held
  documents or inside execution-record inventories of `main`'s own tree.
- **No named absent object is in the Dropbox** (`rnu_env.py`,
  `CL_ANTHROPIC_BUNDLE_*`, `allcell_fdz_enclosures.json`, 24-jet roster / `p_J`,
  `explicit_interval_map_F_G12box_to_Rplus`, `cancelled_detgg_s_t2`, φ bridge,
  V3.3 eigenfloor table, readable `SIDE24_AUDIT_EVIDENCE_2026-08-01.zip`,
  LS-DER-030 native, any credential).
- **Several OQ-016 "not delivered / nowhere in the archive" items are in the
  Dropbox but are already held**: the whole `KIMI_W8_V3_PACKAGE.zip` (transcript_O,
  identity stamp, S6 excerpt, HASHES, mutation receipts), the W2/W3/W4 freeze
  receipts, the K3 Phase-0 raw carriers and the entire 866-member `K3_SIDE24_LB`
  tree are byte-identical to, or digest-listed in, `main`'s mirrors and Drive
  inventory. The OQ-016 wording predates that intake; this sandbox does not edit it.
- **One new, relevant cluster** — saved under
  `NEW_RELEVANT/LPW_Return_05_Archive_Audit_2026-09-12/` (47 files, 185,429 B):
  a parallel, never-published edition of LPW Return 05 whose top-level documents
  and receipts exist nowhere on the project side. Its unique content is the
  **W8 recovered-input preflight**: `verify_lambda_grid_v3.py` run against the
  Drive-recovered `c027 sweep core40.json` (hash gate passed, P0 kernel moments,
  DEN closed form, 12-station cross-validation at max rel diff 1.438e-07, then a
  30 s controlled timeout before the grid sweep), the original missing-input
  `FileNotFoundError` stop, a 247/266 historical K3 root-manifest check (vs the
  264/266 AO48-AUD-065 recorded against a different container), and this edition's
  write-up of the 6.239e-44 constant defect. The author's own label is kept:
  *"source-exact input preflight only; no new W8 mathematical verdict"*.
  The 398 KB `receipts/MANIFEST_AUDIT.json` of that edition is pointer-only
  (sha256 in `NEW_RELEVANT/SAVED_FILES.json`); everything else unique was saved.
- The other 207 not-held objects (RUFT essays, MPV3 documents, prompt texts,
  persistence-thermodynamics / psi side-project papers, Dec-2025 literature-pass
  notes, Codex execution records of `main`, re-rendered PDFs of held packets,
  repacked containers, a résumé, a KML, a pyc) match no recorded hunt target.
  Their paths, sizes and digests are inventoried; their bytes were not saved.

## Files

| File | Content |
|---|---|
| `WANTED_LIST_RESULTS.json` | every wanted object → ABSENT_FROM_DROPBOX / ALREADY_HELD / NEW_RELEVANT, with evidence |
| `NEW_RELEVANT/LPW_Return_05_Archive_Audit_2026-09-12/` | the saved new bytes (unchanged from Dropbox; per-file SHA-256 in `SAVED_FILES.json`) |
| `NEW_UNSOUGHT_INVENTORY.json` | the 255 not-held objects, metadata only |
| `METHOD_SUMMARY.json` | counts, digests and the `main` tip used |
