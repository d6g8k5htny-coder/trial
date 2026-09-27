# Dropbox → Drive / GitHub gap audit (2026-09-27)

**Scientific effect: NONE.** This is a byte-level presence audit. A file being
missing from Drive or GitHub says nothing about any claim, premise, prize or
lemma. `lemma_closed` stays **false**.

Source: Dylan's shared Dropbox folder
`https://www.dropbox.com/scl/fo/9h5229ryu5pecpje7xgdh/APr763YsXKpEuYaQ1Idd1HY?rlkey=rr8v0tet6e5i31o6gkup83tqf`
(the `scl/fo` link resolves to one 188,945,044-byte zip; extracted 3,325 files,
**1,695 distinct SHA-256** — the folder carries many `(1)`/`(2)` duplicates and
zip-of-folder copies — plus 2,975 members inside 37 zip carriers).

Machine-readable results: [`portable/dropbox_gap_audit_2026-09-27/`](../portable/dropbox_gap_audit_2026-09-27/)
(`SUMMARY.json`, `MISSING_FROM_DRIVE.json`, `MISSING_FROM_GITHUB.json`,
`MISSING_FROM_BOTH.json`, `REVISION_DIFFERS_DRIVE.json`,
`ZIP_CARRIER_COVERAGE.json`, `DROPBOX_INVENTORY.tsv`). Reproduce with
[`scripts/dropbox_gap_audit.py`](../scripts/dropbox_gap_audit.py).
Companion intake digest by a peer agent: `cursor/dropbox-intake-digest-309a`
(`portable/dropbox_intake_2026-09-27/`) — that branch indexes the corpus; this
one diffs it.

## How the comparison was done

| Side | Reference used | Match rule |
|---|---|---|
| Google Drive | `main@chatgpt/drive-github-hardening-20260919:drive/inventory.jsonl` (2026-09-17 export, 3,714 files, 2,059 with SHA-256), `drive/source_map/Archive_Members.csv` (11,649 zip members with payload SHA-256), `Payloads.csv`, plus all 414 `_MANIFEST.jsonl` delta/mirror manifests (Drive changes through 2026-09-20) | SHA-256 → name+bytes → name → stem |
| GitHub | every branch of all 8 owner repos (`main` 145 refs, `Math-` 70, `trial` 1,399, `google-drive`, `governance-`, `meta-framework`, `query-`, `sandbox`) | git blob SHA-1 of the Dropbox bytes vs `git ls-tree -r` → name → stem |

Only a **`none`** result is counted as missing. `name_only` / `stem_only` rows
are reported separately as "revision differs / unverified" (native Google Docs
carry no digest, so a same-title Doc cannot be byte-confirmed).

**Caveat.** This pod has no Drive credentials. "Drive" here is the 09-17 export +
deltas to 09-20 that live on the hardening branch. Anything Dylan uploaded to
Drive after 2026-09-20 will still show as missing below; the PKG-01…05 peer
review folders (2026-09-16) *are* in the export.

## Headline numbers (distinct content, 1,695 files)

| | in Drive (exact SHA-256) | missing from Drive | in GitHub (exact blob, any branch) | missing from GitHub |
|---|---:|---:|---:|---:|
| Dropbox files | 1,476 (87%) | **183** | 589 (35%) | **975** |
| zip members (2,975) | 2,821 | 125 | 958 | 1,764 |

- Missing from **both**: **166** distinct files.
- Of the 589 GitHub hits, only **59** are on a default branch (58 on
  `Math-@main` under `imports/upper2d_*`, 1 trivial). The other **530** exist
  only on `main`'s non-default branches (`chatgpt/drive-github-hardening-20260919`,
  `agent3/jetmod-rnunif-status-open-hold`, …) under `drive/mirrors/`. Default
  `main@main` (116 files) holds essentially none of this corpus.

## A. What the Dropbox has that Google Drive does not (183 distinct)

Grouped; full rows in `MISSING_FROM_DRIVE.json`.

| # | Group | Files | Notes |
|---|---|---:|---|
| A1 | **Review-run artifacts** `master-final-v1/` and `rn-sector-review-master-20260921/` | 42 | Local CI replay of `d6g8k5htny-coder/main` @ `d107ab12` (dirty tree) on Dylan's Mac, 2026-09-22 01:04–02:45 UTC: `report.json` (status **PASS**, pytest 2890 passed / 2 skipped, `tools/registers_import.py --check` … `manifest_integrity_check`), `pytest.xml`, `01.log`–`41.log`. Not in Drive, not in any repo. `rn-sector-review` run had `research/campaigns/rn_fullmark_sector_20260921_v1/*` staged (`A`) in its tree; `master-final-v1` had `governance/REPOSITORY_VISIBILITY_20260922.md` staged. |
| A2 | **`LPW_Return_05_Archive_Audit_2026-09-12/`** tree | 33 | `01_ARCHIVE_AND_REPLAY_AUDIT.md`, `02_CONSTANT_FINDINGS_AND_REPAIR.md`, `03_CURRENT_STATE_AND_AUTHORIZED_UPDATE.md`, `receipts/*` (ARCHIVE_INTAKE, FINAL_EXECUTION_RECEIPT, FINDINGS_NORMAL, W8_RECOVERED_PREFLIGHT, 14 `replay_logs/*`), `source_excerpts/*.numbered.txt`, `tools/check_findings.py`. Drive has the *received* KIMI packages and the R04 operator fold (all 4 `received_archives/*.zip` match Drive exactly) but **not this Return-05 audit layer**. Of the other 20 files in the tree, 6 match Drive byte-exactly and 14 match only by name with different bytes (see C). |
| A3 | **MPV3 / Master Prompt series** | 14 | `MPV3 MASTER/MANIFEST/START HERE/TORSIO PROPOSAL/GRAMMATICA/LEXICON/LINGUA` (.md + .pdf), `MASTER PROMPT AI DISCOVERY V2` (.md/.pdf), `Master Prompt AI Discovery.pdf`, `MASTER BACKUP March2026*.pdf`. No Drive title match at all. |
| A4 | **Other root documents** | 38 | AI-research PDFs (`ARCHITECTURE FOR LONG HORIZON RESEARCH`, `MECHANICAL ARCHITECTURE …`, `Algebraic Structures from Global Traditions…`, `Seven Bridges…`, `Three Bridges…13M+`, `Cross-Disciplinary Connections…13m`, `Topological Fingerprint for Random Fields…`, `Novelty Confirmation Sweep…`, `Running Computations on Quijote…`, `030726 Bibliographic and Mathematical Verification Report…`, `070326claufe.pdf`, `deep analysis.pdf`, `generative-reasoning-protocol.pdf`, `gpt2 simulator.pdf`, `lambda loop benchmark*.pdf`, `public presentation self contained.pdf`), `Drive manifest (condensed, all 964 files…) — Part 01 of 13.pdf` (only part 1 of 13 is present), figures `fig B/C/D …13M+.png`, small JSON/MD notes (`c033 resolution.json` (2 bytes), `correction ledger.json`, `deep analysis results.json`, `synthetic results.json`, `master_findings.md`, `methodology_playbook (1).md`, `connections_map (1).md`, `terminology_dictionary.md`, `open_questions.md`, `pass_report_2025-12-18_round3.md`), `001claude.txt.txt`, `Claude.txt.txt`, `Claudebreakdown13M+.txt.txt`, `Science 2026.txt`, `Scientific explanation.txt (1).txt`, `Protocol .txt`. |
| A5 | `textNN.txt` scratch notes | 21 | `text53…text140 (.txt)`. |
| A6 | psi / apoha papers | 8 | `psi dashboard*.pdf`, `psi experiment*.pdf`, `psi stream.pdf`, `psi paper v2 corrected.docx`, `apoha contrastive paper.docx`. |
| A7 | Git-mirror manifests | 13 | `_MANIFEST.jsonl`, `_MANIFEST.json`, `*.zip.members.txt` inside `00/`, `05_MASTER_SETUP/`, `T2 — SARD-G Transversality/`, `64_FORMAL_CORE…/`, `00_MASTER_INDEX_AND_ROUTING/`, `01_TIER-2…/`. These are GitHub-native (`drive/mirrors/**/_MANIFEST.jsonl`) and all match GitHub exactly; they are not expected on Drive. |
| A8 | Zip carriers | 12 | `K3_SIDE24_LB.zip`, `UPPER2D.zip`, `05_MASTER_SETUP.zip`, `00_MASTER_INDEX_AND_ROUTING.zip`, `64_FORMAL_CORE…zip`, `T2 — SARD-G Transversality.zip`, `01_TIER-2…zip`, `LPW_Return_04_Operator_2026-09-12.zip`, `LPW_Return_05_Archive_Audit_2026-09-12.zip`, `LPW_Review_Reconciliation_2026-09-12.zip`, `master-final-v1.zip`, `rn-sector-review-master-20260921.zip`. The **carrier bytes** are Dropbox-local zips; their **members** are covered above (e.g. every one of the 1,324 `K3_SIDE24_LB.zip` members and 656 `UPPER2D.zip` members is byte-present in Drive inside `09152026OKComputer_Project_Gap_Closure.zip`). See `ZIP_CARRIER_COVERAGE.json`. |
| A9 | Noise | 2 | `ChatGPT.dmg` (59 MB installer), `uts46data.cpython-311.pyc`. |

Everything else in the Dropbox (1,476 distinct files: the q0 Master Set,
`Q0_MASTER.md`, `q0_verify.py`, `q0_machine.json`, KIMI packages, LPW Return 03/04,
K3_SIDE24_LB / UPPER2D trees, 20 cold-review DOCX packets, `AClaude …` PDFs,
External Review Package `00_READ_ME_FIRST.md` … `06_REVIEW_RESPONSE_FORM.md`)
is byte-identical to something already in the Drive export.

## B. What the Dropbox has that GitHub does not (975 distinct; 166 also absent from Drive)

| # | Group | Files | Where it *is* |
|---|---|---:|---|
| B1 | `K3_SIDE24_LB/UPPER2D/**` (H5_closure bulk, H3_closure, H1_v2_hardening, B1/C1/H2 …) | 350 | Drive: inside `09152026OKComputer_Project_Gap_Closure.zip`. GitHub only has the `imports/upper2d_h5_ledgers_20260926` + `imports/upper2d_stage_e_20260926` subsets on `Math-@main` (58 files) and hardening-branch mirrors. |
| B2 | `K3_SIDE24_LB/LPW_CONSTANT/{v3,v4}`, `W3_numerics`, `W6_uniform_r`, `W8_lambda`, `W4_independent`, `RETURN_06`, `REVIEW_LPW`, `QC_RETURN03_REVIEW`, `INBOX_LPW_Return_03/04`, `INBOX_LPW_Reconciliation` | 201 | Drive (same carrier zip). Not in any repo. |
| B3 | Root-level `*.json` (108), `*.md` (83), `*.pdf` (74), `*.txt` (27), `*.py` (10), `*.png` (9), `*.docx` (4), `*.gs` (2) | 317 | Mostly Drive (`Payloads.csv` / `Peer_Review_Packets_20_COMPLETE.zip` / `09152026OKComputer…zip`); the A3–A6 subset is nowhere. |
| B4 | `LPW_Return_05_Archive_Audit_2026-09-12/` | 37 | 33 nowhere (A2); 3 in Drive by name only; 1 in Drive byte-exact. |
| B5 | `master-final-v1/`, `rn-sector-review-master-20260921/` | 45 | Nowhere (A1). `report.json` name-collides with `sandbox` `experiments/d7_drift_scan_20260925/REPORT.json` but is unrelated. |
| B6 | `64_FORMAL_CORE_R2_P02_LM008_LM009/**` | 6 | 6 members of `GP-FOR-192-v1.0_research-formal-core-r2.zip` are in Drive; only 1 member reached GitHub. |
| B7 | zip carriers | 14 | as A8. |

## C. Same name, different bytes (revision drift) — 26 rows, `REVISION_DIFFERS_DRIVE.json`

- The Dropbox root carries a **SIDE24 pre-review package** (`00_READ_ME_FIRST.pdf`
  208,953 B, `01_COVER_LETTER.txt`, `02_PRE_REVIEW_DOSSIER.pdf`,
  `03_SIDE24_MANUSCRIPT.pdf`, `04_TECHNICAL_APPENDIX.pdf`, `05_REPRODUCTION_GUIDE.pdf`,
  `07_REVIEW_RESPONSE_FORM.docx`, `09_PACKAGE_MANIFEST.csv`,
  `11_COMPLETE_PRE_REVIEW_PACKET.pdf`) whose names match Drive's
  `15_REVIEWS_RESPONSES_AND_CLOSURES/THEOREM_B — STATUS RETRACTION AND REPAIR PROGRAM/PKG-SIDE24-001 — External Peer-Review Capsule/SIDE24_PROFESSOR_PRE_REVIEW_PACKAGE_2026-07-31/*`
  but **not their bytes**. One side is a later revision; the Drive IDs and
  digests for each candidate are in the JSON so a credentialed agent can
  resolve direction.
- `00/00.2_CANONICAL_MASTER/*/README.md` (3) differ from the Drive
  `02_FORMAL_AND_LEAN_RESEARCH_SYSTEM` READMEs of the same name (expected —
  different folders, same generic filename).
- `LPW_Return_05_Archive_Audit_2026-09-12/{00_READ_FIRST.md, 04_RETURN_TO_KIMI.md, 05_MATCHING_2D_UPPER_WORK_ORDER.md, CURRENT_STATE.json, MANIFEST.sha256, receipts/BODY_HASH_AUDIT.json, receipts/MANIFEST_AUDIT.json, receipts/REPLAY_RECEIPT.json, tools/replay_received.py, tools/verify_bundle.py, …}` differ from the Drive `LPW — RAW ARCHIVE INTAKE R05` / `LPW — OPERATOR FOLD R04` copies — Return-05 was revised after what Drive holds.

## D. What this means for the agents (no status change)

1. **Drive backfill candidates (Dylan / credentialed Drive session only — this pod cannot write Drive):**
   A1 review-run receipts (they are the only execution record of the 2026-09-22 CI replay of `main@d107ab12`),
   A2 `LPW_Return_05_Archive_Audit` layer, and the revision-drifted Return-05 + SIDE24 pre-review files in C.
   A3–A6 are personal / non-q0 material; route only if Dylan wants them in the research Drive.
2. **GitHub:** the default branch of `main` carries almost none of the corpus;
   530 files exist only on hardening/agent3 branches. Whether to promote
   `drive/mirrors/` to default is the standing Path C question — nothing here
   changes it. Do **not** copy Dropbox research bodies into `trial` (AGENTS.md:
   no vault mirrors here); the inventory TSV (paths + digests) is the artifact.
3. **Nothing in the Dropbox contradicts the open stack.** `Q0_MASTER.md`,
   `q0_verify.py`, the External Review Package and the KIMI packages are
   byte-identical to Drive; the peer digest's `lemma_closed:false` /
   `OBL-D1-PROMOTE OPEN` reading stands.
4. Re-run after any Drive re-export: `python3 scripts/dropbox_gap_audit.py`
   (docstring has the exact fetch steps).
