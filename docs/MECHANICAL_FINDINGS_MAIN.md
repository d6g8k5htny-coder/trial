# Mechanical findings on `d6g8k5htny-coder/main` (hardening tip)

Scientific effect: **NONE**. These are engineering / ResourceWarning hygiene notes only.
**Never** promote / close / discharge research status. `lemma_closed=false` stays false.

## Batch 185 — tip stable 8bd1f03; auth renew 46EC; research AUDIT counts refresh; bundle E2E OK; no research flips @ tips `1c6e74b` / `8bd1f03`

Mechanical inventory **refreshed** (audit only) on tip `8bd1f03`. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**. Obsolescence on tip WITHOUT patches: **0** of 0001–0004/0008–0016 already present (no drops).

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8bd1f03cc2bb10c59b08b852ca2775dac27e28e9` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165/185 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening (clean == patched) | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| research counts | premises=13 lemmas=1 prizes=3 obligations=2 claims=26 OQ=16 |
| write / Path C | **DENIED** (403); device auth renewed `46EC-0B00` (prior `DF9C-5DF9`) |
| E2E `.bundle` | shallow clone → fetch → ff-merge → `b6a1ff3`; focused **90**/0; claims+recovery **83**/0 |
| pack / release | still **`batch180-path-c-bundle`** |
| CI batch183 | **success** |
| preferred auth timer | **`preferred_auth_interval_s=1800`** |
| new portable **0017** | **none** |

Artifacts: `portable/BATCH185_BRIEF.json` + `BATCH185_RESEARCH_COUNTS.json`. Scientific effect: **NONE**.

## Batch 178 — tip stable; auth pending 5E05; owner_open_path_c_pr release-bundle link; CI tip-drift string restore; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**. Obsolescence on tip WITHOUT patches: **0** of 0001–0004/0008–0016 already present (no drops).

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth renewed `AD78-6206` (prior `5E05-EA04`) |
| pack / release | still **`batch169-path-c-bundle`**; `owner_open_path_c_pr.sh` PR body links `.bundle` download |
| CI tip-drift | restore exact `refresh BASE_TIP` + `rebuild path-c-applied-bundle` strings (Batch 147) |
| preferred auth timer | **`preferred_auth_interval_s=1800`** |
| new portable **0017** | **none** |

Artifacts: `portable/BATCH178_BRIEF.json`. Scientific effect: **NONE**.

## Batch 176 — tip stable; auth renew 5E05; refresh fetch+CI tip-drift dry-sim; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth renewed `5E05-EA04` (prior `9671-4918`) |
| pack / release | still **`batch169-path-c-bundle`** (tip/bundle unchanged); tip-move helper `scripts/refresh_path_c_bundle.sh` |
| CI tip-drift | fail + fix-path message + `--dry-run` dry-sim (no auto-push to main) |
| preferred auth timer | **`preferred_auth_interval_s=1800`** |
| new portable **0017** | **none** |

Artifacts: `portable/BATCH176_BRIEF.json`. Scientific effect: **NONE**.

## Batch 173 — tip stable; auth renew 9671; refresh_path_c_bundle.sh; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth renewed `9671-4918` (prior `7BCB-0057`) |
| pack / release | still **`batch169-path-c-bundle`** (tip/bundle unchanged); tip-move helper `scripts/refresh_path_c_bundle.sh` |
| issue hygiene | canonical **[#34](https://github.com/d6g8k5htny-coder/trial/issues/34)**; App cannot comment/edit #33 |
| preferred auth timer | **`preferred_auth_interval_s=1800`** |
| new portable **0017** | **none** |

Artifacts: `portable/BATCH173_BRIEF.json`. Scientific effect: **NONE**.

## Batch 172 — tip stable; issue hygiene #33; non-RW hunt clean; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth pending `7BCB-0057` (seconds_left≥90; no renew) |
| pack / release | still **`batch169-path-c-bundle`** (tip/bundle unchanged) |
| issue hygiene | canonical **[#33](https://github.com/d6g8k5htny-coder/trial/issues/33)**; close duplicates **DENIED** (App 403) |
| preferred auth timer | **`preferred_auth_interval_s=1800`** |
| new portable **0017** | **none** (non-RW hunt clean after patches) |

Artifacts: `portable/BATCH172_BRIEF.json` + `BATCH172_HUNT.json`. Scientific effect: **NONE**.

## Batch 170 — tip stable; E2E `.bundle` verify; CI intent fix; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening (post `.bundle` merge) | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| E2E `.bundle` | shallow clone → fetch → ff-merge → `81c09d6`; focused **90**/0; claims+recovery **83**/0 |
| write / Path C | **DENIED** (403); device auth renewed `7BCB-0057` (prior `EC83-CFC2`) |
| pack / release | still **`batch169-path-c-bundle`** (tip/bundle unchanged) |
| preferred auth timer | **`preferred_auth_interval_s=1800`** (no duplicate) |
| new portable **0017** | **none** (hunt clean after patches) |

Artifacts: `portable/BATCH170_BRIEF.json` + `BATCH170_HUNT.json` + `portable/path-c-applied-bundle/{APPLY.md,VERIFY.json}`. Scientific effect: **NONE**.

## Batch 169 — tip stable; fetchable git `.bundle`; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth pending `831C-CB1C` |
| pack / release | **`batch169-path-c-bundle`** ships `path-c-on-hardening.bundle` + `.patch` |
| owner apply | `--from-bundle` prefers `git fetch` `.bundle` + ff-merge |
| preferred auth timer | **`preferred_auth_interval_s=1800`** (no duplicate) |
| new portable **0017** | **none** (tip==BASE_TIP) |

Artifacts: `portable/BATCH169_BRIEF.json` + `portable/path-c-applied-bundle/{path-c-on-hardening.bundle,APPLY.md,VERIFY.json}`. Scientific effect: **NONE**.

## Batch 168 — tip stable; oneshot pack release; no research flips @ tips `1c6e74b` / `8ea3b5f`

Mechanical inventory unchanged from Batch 165 refresh. Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory (Batch 165 counts) |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** |
| write / Path C | **DENIED** (403); device auth renewed `831C-CB1C` (prior `905D-02F4`) |
| pack / release | **`batch168-path-c-bundle`** includes `owner_path_c_oneshot.sh` |
| preferred auth timer | **`preferred_auth_interval_s=1800`** (no duplicate) |
| new portable **0017** | **none** (tip==BASE_TIP) |

Artifacts: `portable/BATCH168_BRIEF.json` (counts: Batch 165 research files). Scientific effect: **NONE**.

## Batch 165 — research-stack OPEN audit refresh (no status flips) @ tips `1c6e74b` / `8ea3b5f`


Mechanical inventory only (`scripts/audit_research_stack_open.py` + `tools/math_status_check.py` on live hardening tip `8ea3b5f`). Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `8ea3b5fb9368a85e7f971d606b8f75c96c35c05a` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory below |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** / prizes_solved=false |
| open premises (frozen) | **13** |
| open lemmas | **1** (`D3-LEMMA-RN-UNIF`) |
| open packet obligations | **2** (`OBL-H5-JETMOD`, `D3-LEMMA-RN-UNIF`) |
| open prizes (FW-NO-PRIZE-CLOSURE) | **3** |
| claims inventory | **26** (not promoted) |
| open questions | **16** mechanically OPEN/HOLD/REBASED |
| write / Path C | **DENIED** (403; `install_has_main=false`); device auth renewed `905D-02F4` |
| new portable **0017** | **none** (tip==BASE_TIP; hunt_skipped_stable) |
| owner entry | `scripts/owner_path_c_oneshot.sh` (Batch 165) |

Packet: disposition=`OPEN_HOLD`; `prizes_solved=false`; `original_prize_closed=false`; bridge=`PROPOSED_NOT_DEPLOYED`; freeze=false.

Artifacts: `portable/BATCH165_RESEARCH_STACK_AUDIT.json`, `portable/BATCH165_RESEARCH_COUNTS.json`. Scientific effect: **NONE**.

## Batch 149 — research-stack OPEN audit (no status flips) @ tips `1c6e74b` / `10c077e`

Mechanical inventory only (`scripts/audit_research_stack_open.py` + `tools/math_status_check.py` on live hardening tip). Flipped nothing. `lemma_closed=false`. Disposition **OPEN_HOLD**.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `10c077e08261fa3d07317e290826604a749d4e49` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory below |

| Check | clean tip (no patches) | after `apply_all` 0001–0004+0008–0016 |
|-------|------------------------|----------------------------------------|
| `math_status_check` | problems=0 / `OPEN_HOLD` / **lemma_closed=false** | **same** (no differ) |
| `guard_no_status_promotion` | **pass** — 0 violations | **pass** |
| open premises (frozen) | **13** | **13** |
| open lemmas | **1** (`D3-LEMMA-RN-UNIF`) | **1** |
| open packet obligations | **2** (`OBL-H5-JETMOD`, `D3-LEMMA-RN-UNIF`) | **2** |
| open prizes (FW-NO-PRIZE-CLOSURE) | **3** | **3** |
| claims inventory | **26** (not promoted) | **26** |
| open questions | **16** mechanically OPEN/HOLD/REBASED | **16** |

Packet: disposition=`OPEN_HOLD`; `prizes_solved=false`; `original_prize_closed=false`; bridge=`PROPOSED_NOT_DEPLOYED`; freeze=false.

Artifacts: `portable/BATCH149_RESEARCH_STACK_AUDIT.json`, `portable/BATCH149_RESEARCH_COUNTS.json`. Scientific effect: **NONE**.

## Batch 132 — research-stack OPEN audit (no status flips) @ tips `1c6e74b` / `c82c9357`

Mechanical inventory only (`scripts/audit_research_stack_open.py` + `tools/math_status_check.py` on live hardening tip). Flipped nothing.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face) | **ALIGNED**; Path B not needed |
| hardening | `c82c9357db381e8fd60d939a7243dab4cc863118` | **HAS_PACKET** (== BASE_TIP; no tip refresh) | OPEN inventory below |

| Check | Result |
|-------|--------|
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** / prizes_solved=false |
| `guard_no_status_promotion` | **pass** — 0 violations vs `STATUS_GUARD_SNAPSHOT` |
| open premises (frozen) | **13** |
| open lemmas | **1** (`D3-LEMMA-RN-UNIF`) |
| open packet obligations | **2** (`OBL-H5-JETMOD`, `D3-LEMMA-RN-UNIF`) |
| open prizes (FW-NO-PRIZE-CLOSURE) | **3** (`PR-TAL-003..008`, `P14-A..E`, `P15-A..D`) |
| claims inventory | **26** (not promoted) |
| open questions | **16** mechanically OPEN/HOLD/REBASED |
| write / Path C | **DENIED** (403; `install_has_main=false`); device auth pending |
| new portable **0017** | **none** (tip==BASE_TIP; hunt_skipped_stable) |

### OPEN premises (frozen layer) — `claims/graph.json` @ `c82c9357`

`OBL-D1-PROMOTE`, `OBL-H5-JETMOD`, `OBL-H5-ZBAND`, `OBL-H5-REMOTE-THRESHOLD`, `D3-LEMMA-RN-UNIF` (NOT_CLOSED), `PERC-DECAY`, `PD-CONN`, `OBL-B1-BRANCH(loop|B1)`, `B4.loc-damline`, `H5-RIM`, `H5-AXIS`, `H-B3`, `LM013-JOINT-STACK`.

Packet: disposition=`OPEN_HOLD`; `prizes_solved=false`; `original_prize_closed=false`; bridge=`PROPOSED_NOT_DEPLOYED`; freeze=false.

Artifact: `portable/BATCH132_RESEARCH_STACK_AUDIT.json`. Scientific effect: **NONE**.

## Batch 86 — no-status-promotion guard @ tips `1c6e74b` / `ac33581`

Mechanical compare only (`scripts/guard_no_status_promotion.py`). Flipped nothing.

| Check | Result |
|-------|--------|
| baseline | `portable/BATCH70_RESEARCH_STACK_AUDIT.json` (hardening inventory) |
| live tip | hardening `ac335815b277ac0c076082ac6af2344261c2093a` (**HAS_PACKET**) |
| guard | **pass** — 0 violations; open premises **13** / lemmas **1** / prizes **3** unchanged |
| snapshot | `portable/STATUS_GUARD_SNAPSHOT.json` |
| CI | `research-stack-status-guard` (`continue-on-error: true` + artifact) |
| `lemma_closed` | **false** (nothing flipped) |

## Batch 70 — research-stack OPEN audit (no status flips) @ tips `1c6e74b` / `5f352a2`

Mechanical inventory only (`scripts/audit_research_stack_open.py`). Flipped nothing.

| Tip | SHA | Shape | Result |
|-----|-----|-------|--------|
| default `main` | `1c6e74bbc212198d51502ae3f6088ce1bc8cdb76` | **NO_PACKET** (post-#41 face; body under `history/`) | ALIGNED face; no live PACKET/claims at root |
| hardening | `5f352a2d16aeb260defabffb6154e0ebca8bd23a` | **HAS_PACKET** (BASE_TIP refreshed `74c082e`→`5f352a2` via PR #44) | OPEN inventory below |

| Check | Result |
|-------|--------|
| `watch_main_alignment` / `audit_main_alignment` | **ALIGNED**; `EXPECTED_POST_ALIGNMENT` **MATCHES** |
| write / Path B·C land | **DENIED** (403); Path B not needed |
| Tip refresh | hardening **`74c082e` → `5f352a2`** ([PR #44](https://github.com/d6g8k5htny-coder/main/pull/44) fail-closed vault path map); `apply_all --check` **OK** |
| `math_status_check` @ hardening | problems=0 / disposition=`OPEN_HOLD` / **lemma_closed=false** / prizes_solved=false |
| `lemma_closed` confirmation | **false** (PACKET + audit script; nothing flipped) |
| new portable **0017** | **none** (audit objective; tip-match after refresh) |

### OPEN premises (frozen layer) — `claims/graph.json` @ hardening

All 13 premises remain mechanically open at `status_frozen_v2_2` ∈ {OPEN, NOT_CLOSED, NAMED_HYPOTHESIS}:

`OBL-D1-PROMOTE`, `OBL-H5-JETMOD`, `OBL-H5-ZBAND`, `OBL-H5-REMOTE-THRESHOLD`, `D3-LEMMA-RN-UNIF` (NOT_CLOSED), `PERC-DECAY`, `PD-CONN`, `OBL-B1-BRANCH(loop|B1)`, `B4.loc-damline`, `H5-RIM`, `H5-AXIS`, `H-B3`, `LM013-JOINT-STACK`.

### OPEN lemmas / packet obligations — `docs/math_status/PACKET.json`

| ID | status | lemma_closed | notes |
|----|--------|--------------|-------|
| `OBL-H5-JETMOD` | OPEN | false | grade=display_only; does not discharge |
| `D3-LEMMA-RN-UNIF` | OPEN | false | piece2_annulus_driver=**UNWRITTEN** |

Packet: disposition=`OPEN_HOLD`; `prizes_solved=false`; `original_prize_closed=false`; bridge=`PROPOSED_NOT_DEPLOYED`; freeze=false.

### OPEN prizes (FW-NO-PRIZE-CLOSURE) — NUMBER_THEORY track

`PR-TAL-003..008`, `P14-A..E`, `P15-A..D` — each carries `original_prize_closed: false`.

### OPEN claims / questions (inventory, not promotion)

- Claims graph: **26** claims inventoried (grades CONDITIONAL / PROPOSED / AUTHOR_SIDE_* / FROZEN_CERTIFICATE / …); D1-v2.2(2) still names validity premises `OBL-D1-PROMOTE`, `D3-LEMMA-RN-UNIF`, `PERC-DECAY`, `OBL-B1-BRANCH(loop|B1)`, `B4.loc-damline`.
- Register open questions mechanically OPEN/HOLD/REBASED: **16** (`OQ-005`…`OQ-016`, `OQ-014-U1`, `OQ-015-U1`, `OQ-016-U1`, `OQ-016-U2`). Closed terminal rows (`OQ-001`…`OQ-004`) not listed as OPEN.

### Evidence paths

- Hardening: `docs/math_status/PACKET.json`, `STATUS.md`, `STATUS_JETMOD.md`, `STATUS_RN_UNIF.md`, `math_console_snapshot.json`, `claims/graph.json`, `registers/json/open_questions.json`
- Default tip: `README.md`, `AGENTS.md`, `history/` (no PACKET)
- Artifact: `portable/BATCH70_RESEARCH_STACK_AUDIT.json`

Default `main` @ `1c6e74b` **ALIGNED** (PR #41); write **DENIED**. Scientific effect: **NONE**. `goal_complete=false`.

## After portable patches 0001–0004 + 0008–0016 on `6f0f061` (batch 64)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `6f0f061` (== BASE_TIP; no tip move since Batch 63 / PR #43) |
| Path C dry-run | `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`; rebase **CONFLICTING** |
| new portable **0017** | **none** (IDLE; tip-match) |
| `pack_portable.sh` | auto-globs restore plans + token search logs |

Default `main` @ `1c6e74b` **ALIGNED** (PR #41); write **DENIED**. Scientific effect: **NONE**.

## After portable patches 0001–0004 + 0008–0016 on `6f0f061` (batch 63)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `6f0f061` (PR #43; BASE_TIP refreshed from `b3da668`) |
| `apply_all` on default `main` @ `1c6e74b` | **exit 2** — post-#41 topology refuse (no PACKET.json) |
| `math_status_check` | problems=0 / lemma_closed=false |
| focused+receipts/bridge/collision/frozen/registers/mirrors/ops/lean/RN/drive | **~1600 passed** / **0 ResourceWarning** |
| tools `--help` | **0 ResourceWarning** |
| new portable **0017** | **none** (IDLE) |
| Path C dry-run | `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`; rebase **CONFLICTING** |

Default `main` @ `1c6e74b` **ALIGNED** (PR #41); Path C stays on hardening. `print_owner_unblock.sh` reads `BASE_TIP.txt`.

## After portable patches 0001–0004 + 0008–0016 on `b3da668` (batch 60)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `b3da668` (PR #34; BASE_TIP refreshed from `036a6bc`) |
| `math_status_check` | problems=0 / lemma_closed=false |
| focused+receipts/bridge/collision/frozen | **922 passed** / **0 ResourceWarning** |
| new portable **0017** | **none** |
| Path C dry-run | `APPLY_READY_POST_ALIGNED_KEEP_HARDENING`; default tip not Path-C shaped; rebase **CONFLICTING** |

Default `main` @ `1c6e74b` **ALIGNED** (PR #41); Path C stays on hardening.

## After portable patches 0001–0004 + 0008–0016 on `9a56c30` (batch 57)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `9a56c30` (== BASE_TIP; no tip move) |
| `math_status_check` | problems=0 / lemma_closed=false |
| focused+claims+recovery | **173 passed** / **0 ResourceWarning** |
| frozen/dio/receipts/bridge/collision | **0 ResourceWarning** |
| RN suite | **438 passed** / **0 ResourceWarning** |
| tools `--help` | **0 ResourceWarning** |
| new portable **0017** | **none** (IDLE) — Path B automation shipped instead |

Default `main` @ `4fc1d7c` still **MISALIGNED**; Path B would-align via `path_b_dry_run.py`; write 403.

Tip residuals (not portable): `mirror_quotes` 3 + bridge AGENTS.md drift → open PR #35.

## After portable patches 0001–0004 + 0008–0016 on `580864c` (batch 53b)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK on tip `580864c` (PR #31; BASE_TIP refreshed) |
| Default `main` @ `4fc1d7c` | **MISALIGNED** after CoS PR #32; Path B preferred / still valid; write 403 |

Default `main` @ `4fc1d7c` is **MISALIGNED** after CoS PR #32 reverted PR #2. Path C apply target remains hardening BASE_TIP (`580864c` after PR #31).

## After portable patches 0001–0004 + 0008–0016 on `fbb4360` (batch 53)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK (0001–0004 + 0008–0016; 0005/0006/0007 dropped) |
| `math_status_check` | problems=0 / lemma_closed=false / 0 ResourceWarning |
| focused+claims+recovery+frozen/dio | **192 passed** / **0 ResourceWarning** |
| receipts + bridge | **541 passed** / **0 ResourceWarning** (was 24 before 0016) |
| collision checker/tests | **0 ResourceWarning** after 0014 |

Residual hunt: no further bare-open ResourceWarnings in receipts/bridge after 0016.

Default `main` @ `4fc1d7c` is **MISALIGNED** after CoS PR #32 reverted PR #2. Path C apply target was hardening BASE_TIP (`fbb4360` after PR #30; refreshed to `580864c` in batch 53b).

## After portable patches 0001–0004 + 0008–0015 on `8510874` (batch 52)

| Check | Result |
|-------|--------|
| `apply_all.sh --check` | OK (0001–0004 + 0008–0015; 0005/0006/0007 dropped) |
| `math_status_check` | problems=0 / lemma_closed=false / 0 ResourceWarning |
| focused+claims+recovery | **173 passed** / **0 ResourceWarning** |
| frozen + drive-index overlay | **19 passed** / **0 ResourceWarning** (was 9+1 before 0015) |
| collision checker/tests | **0 ResourceWarning** after 0014 |

Residual (shipped in batch 53 as **0016**): `tests/test_receipts.py` / `tests/test_bridge.py` bare-open ResourceWarnings.

Post-#2 default `main` @ `b040bf0c` is ALIGNED but a different tree (no `docs/math_status/PACKET.json`) — Path C apply target remains hardening BASE_TIP.

# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Working tip audited: `chatgpt/drive-github-hardening-20260919` @ `bf1fde30c7fc04c9919bf9172ee8a13e234c7664`
(PR #27 probe-test isolation; prior #15/#16/#17/#18/#19/#20/#22/#23/#24/#25/#26).
Host: CPython 3.11 + pytest (tip batch 48).
**Scientific effect: NONE.**

## After portable patches 0001–0004 + 0008–0012 on `bf1fde3` (batch 48)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false`; **0 ResourceWarning** |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0004 + 0008–0012; 0005/0006/0007 dropped) |
| inventable-negative unclosed-file ResourceWarning | cleared by **0012** (was 6) |

## After portable patches 0001–0011 on `a8a5dd7` (batch 47)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false`; **0 ResourceWarning** |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0011) |
| math_status_check unclosed-file ResourceWarning | cleared by **0011** (was 30) |

## PR #27 merged `bf1fde3` (batch 48; prior head `20e31a1`)

| Check | Result |
|-------|--------|
| tip-cut 0005/0006/0007 | **dropped** from `apply_all.sh` (obsolete) |
| stack `0001–0004 + 0008–0012` | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery @ 3.11 | **173 passed**; **0 ResourceWarning** |


## After portable patches 0001–0010 on `a8a5dd7` (batch 46)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0010) |

## PR #27 head `20e31a1` + stack 0001–0004 + 0008 (+0009/0010/0011) (batch 46/47; prior `63b519f`)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` (+ optional 0009/0010/0011) | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`); #27 still OPEN → not dropped |

## After portable patches 0001–0010 on `46af1ca` (batch 45)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims + recovery | **173 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0010) |
| recovery unclosed-file ResourceWarning | cleared by **0010** (was 234) |

## After portable patches 0001–0009 on `46af1ca` (batch 44)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims | **137 passed**; **0 ResourceWarning** |
| `apply_all.sh --check` | OK (0001–0009) |

## PR #27 head `63b519f` + stack 0001–0004 + 0008 (batch 44; prior `8d023a9` @ batch 41)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` (+ optional 0009) | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`); #27 still OPEN → not dropped |

## After portable patches 0001–0009 on `b02efe2` (batch 43)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused + claims | **137 passed**; **0 ResourceWarning** |
| broader: workflow_integrity / run_checks / registers / ci_pins | **110 / 45 / 53 / 25** passed |
| `apply_all.sh --check` | OK (0001–0009) |
| claims unclosed-file ResourceWarning | cleared by **0009** (was 19) |

## PR #27 head `8d023a9` + stack 0001–0004 + 0008 (batch 41)

| Check | Result |
|-------|--------|
| tip-cut `apply_all.sh --check` | **fails at 0005** (isolation rewrite) |
| recipe `0001–0004 + 0008` | applies clean |
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| focused slice @ 3.11 | **90 passed**; probes clean |
| ResourceWarning | **6** on negative inventable/instrumentation bare `open()` only |
| tip-cut 0005/0006 | **obsolete after #27 merges** (no `0005-pr27-*`) |

## After portable patches 0001–0008 on `b02efe2` (batch 38)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian + instrumentation | **90 passed** |
| `apply_all.sh --check` | OK |
| focused slice ResourceWarning | **0** (after 0007+0008) |
| `docs/math_status_probes/` after tests | clean |

## After portable patches 0001–0008 on `3f85e93` (batch 35)

| Check | Result |
|-------|--------|
| `math_status_check.py` | `problems=0`, `OPEN_HOLD`, `lemma_closed=false` |
| carriers + math_status + inventable + gaussian + instrumentation | **90 passed** |
| `apply_all.sh --check` | OK |
| focused slice ResourceWarning | **0** (after 0007+0008) |
| `docs/math_status_probes/` after tests | clean |

## Engineering defects → portable patches

| ID | Fix |
|----|-----|
| carriers `__pycache__` false positive | `0001-…` |
| math_console `code_prototypes` paths + PACKET sha/bytes | `0002-…` |
| gaussian moments parametrize iterator | `0003-…` |
| git fixture timeout 10s → 60s | `0004-…` |
| inventable probe test dirty digests (re-cut post-#17) | `0005-…` |
| instrumentation STATUS dirty digests (post-#20) | `0006-…` (**in** `apply_all.sh` since batch 21) |
| inventable tests unclosed-file ResourceWarning | `0007-…` (**in** `apply_all.sh` since batch 24) |
| carriers + math_status + `carriers_verify` unclosed-file ResourceWarning | `0008-…` (**in** `apply_all.sh` since batch 25) |
| claims register-binding unclosed-file ResourceWarning | `0009-…` (**in** `apply_all.sh` since batch 43) |
| recovery + recovery_check unclosed-file ResourceWarning | `0010-…` (**in** `apply_all.sh` since batch 45) |
| `math_status_check` packet-reader unclosed-file ResourceWarning | `0011-…` (**in** `apply_all.sh` since batch 47) |
| inventable-negative unclosed-file ResourceWarning (post-#27) | `0012-…` (**in** `apply_all.sh` since batch 48; replaces obsolete 0007) |

## Alignment

Default `main` still MISALIGNED (`f25b04bb`). PR #2 still draft MERGEABLE/CLEAN.
Path A potential merge commit README still would-align (q0 markers).
Write probe still 403. No `research.yml` schedule changes.
