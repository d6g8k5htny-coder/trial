# Independent replay — trial PR #160 (Layer 1 Lean pilot SIDE24-PILOT-001)

Review-assistance run b8d6, 2026-09-27 22:06–22:20 UTC. **Scientific effect: NONE.**
A reproduced `lake build` is a kernel check of `formal/lean/` on the PR's own pins; it is not
claim acceptance, lemma closure, prize or premise status, and — per the owner note on #160 —
it is **not** a replay of the primary Math- #92 lane (Lean v4.34.1 / mathlib `d13f23b7…`).

## What was replayed

| item | value |
|---|---|
| PR / head reviewed | trial #160, tree `9359cbe2` (`formal/` + `scripts/formal_gate.py` byte-identical at `18b06e56`) |
| toolchain | fresh `elan`, `leanprover/lean4:v4.19.0` (from `formal/lean/lean-toolchain`) |
| Mathlib | `c44e0c8ee63ca166450922a373c7409c5d26b00b`, `lake exe cache get` 6641 files, 100 % |
| command | `python3 scripts/formal_gate.py --run-lake --receipt-out …` (1 m 53 s) |
| result | `lake build exit=0 axioms_exit=0`, both mutants `REJECTED`, `pass=True problems=0`, `earned=kernel_checked` |

Replay receipt vs committed `formal/receipts/lake-build-side24-pilot-001.json`: `toolchain`,
`mathlib_rev`, `module_sha256`, `lake_build_exit_code`, `axioms` (14 decls, only
`propext / Classical.choice / Quot.sound`), `axioms_exit_code`, `negative_controls` — all EQUAL.
Only `generated_at_utc` and `lake_bin` differ. Compact replay receipt:
[`2026-09-27_pr160_lean_replay_receipt.json`](2026-09-27_pr160_lean_replay_receipt.json).

## Informal-source provenance (re-derived, not copied)

- `LS-DER-042-v1.0 … .export.txt` on `main@chatgpt/drive-github-hardening-20260919`: 8786 B,
  SHA-256 `6a24c1af04b1b4fdc482baf09e97da953284d3381853be09e2bbad4baacef25b` = `status.informal_source.file_sha256`.
- Frozen body per the artifact's FREEZE POLICY (unique full-line markers at lines 27/345, CRLF→LF,
  trailing LFs → one LF): 7073 B, SHA-256 `54cedb1eba9d72648619468beed9b8870bb3d28dbe206805dc72b4f796557cf3`
  = declared `BODY_SHA256`.
- Eq. (30) in the body: `2^(2/3) 3^(5/6) Γ(1/6) / [54 π^(3/2)]` — matches `Side24Formal.cPlanar`.

## Numerics (mpmath, 40 dp)

- `Γ(1/6) = 5.56631600178023520425009689…` ∈ `[5.5663160017802352042500, …2501]` → the theorem's hypothesis is non-vacuous.
- `cPlanar = 0.07340691930603427103013596295777405…` — matches eq. (31) to all printed digits; inside the 19-digit `Ioo`.
- Why the 20-digit window is not provable from Mathlib's 20-decimal π: the value is only ≈1.35e-23 above the
  window's lower edge while the derived enclosure has width ≈3.52e-22 (position, not width, is the binding reason).

## Structural note posted on #160

The PR prepends its Batch 828 entry at line 1 of `docs/AUTONOMOUS_48H_LOG.md`; the wake loop prepends
there every ~3 min, so the PR re-conflicts after every batch and GitHub schedules no `pull_request`
workflows while it is conflicting. Correction (from helper run ff72): CI *did* run in the window
between the author's keep-both merge `18b06e56` (22:03Z) and the next loop pulse — `formal-gate`
run 36353931138 (`lean-kernel-check` success, "committed receipt reproduced on fresh runner") and
`trial-ci` run 36353931091 (all five jobs green). So the GitHub fresh-runner receipt, this pod's replay
and the committed receipt agree three ways. Suggested fix so the PR stays green between pulses:
place the entry in its chronological slot (below the `### Batch 829 — tip_or_eng …` header) or drop the hunk.

## Trial suite on `main` + #160 (this pod)

74 failures on first run, all `_living_tip(None)` / `has_token=false` caused by the pod's invalid
`GITHUB_TOKEN` (`write_path_c_status.py` nulls `tip`); rerun of those 74 with the token unset → 74 passed.
`needs_attention_check` OK. Nothing in #160 touches the intent suite. Not research evidence.
