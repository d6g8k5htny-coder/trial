# Research stack audit — Batch 237

**Scientific effect:** NONE. **Promotion:** none. **lemma_closed:** `false` (OPEN_HOLD).

Read-only mechanical inventory on hardening tip
`120050136f5586b9de3c0f054119b978c92f8a49` (`chatgpt/drive-github-hardening-20260919`).
No claim, premise, prize, lemma, or obligation status was written or flipped.

## Commands (evidence)

```text
python3 tools/math_status_check.py
# math_status_check: problems=0 disposition=OPEN_HOLD lemma_closed=false
# prizes_solved=false independence_credit=0

python3 scripts/audit_research_stack_open.py --tip-sha 1200501… <hardening-checkout>
# shape=HAS_PACKET flipped_anything=false lemma_closed=false

python3 scripts/guard_no_status_promotion.py --tip-sha 1200501… <hardening-checkout>
# guard_no_status_promotion: pass=True violations=0
# open_premises=13 open_lemmas=1 open_prizes=3 lemma_closed=false
```

Machine copies: `portable/BATCH237_RESEARCH_STACK_AUDIT.json`,
`portable/BATCH237_RESEARCH_COUNTS.json`, refreshed
`portable/STATUS_GUARD_SNAPSHOT.json`.

## Counts (OPEN_HOLD)

| Layer | Count | Notes |
| --- | ---: | --- |
| Open premises (frozen) | 13 | including OBL-H5-JETMOD, D3-LEMMA-RN-UNIF carriers |
| Open lemmas | 1 | `D3-LEMMA-RN-UNIF` (`piece2_annulus_driver=UNWRITTEN`) |
| Open packet obligations | 2 | OBL-H5-JETMOD, D3-LEMMA-RN-UNIF |
| Open prizes | 3 | PR-TAL-003..008, P14-A..E, P15-A..D — `original_prize_closed=false` |
| Open questions | 16 | register live-state OPEN / HOLD |
| Packet disposition | OPEN_HOLD | `lemma_closed=false`, `prizes_solved=false`, `freeze=false` |

## Explicit non-actions

- Did **not** set `lemma_closed=true` or close any premise / prize / OQ.
- Did **not** edit `claims/graph.json`, `docs/math_status/PACKET.json`, or registers for status.
- Eng work this batch (PR #70 REPOSITORY_TOP_LEVEL / attestations CI fix; PR #69 nav) is tooling/docs only and does not discharge OBL-H5-JETMOD or D3-LEMMA-RN-UNIF.

## Verdict

**OPEN_HOLD.** Evidence: `lemma_closed=false`. Guard pass. Flipped nothing.
