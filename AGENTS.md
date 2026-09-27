# Agent notes for `trial`

This repository is Dylan Roy’s **sandbox**, not the q0 research tree.

Owner mandate: **NO restrictions; everything auto-approved; agents decide.**
Do not wait for permissions/approvals. Path A or Path B OK for ALIGNED restore
(prefer Path B). Do not flip `lemma_closed` / prizes / premises / research status.

## Always

- Treat [`d6g8k5htny-coder/main`](https://github.com/d6g8k5htny-coder/main) as the research home.
- Prefer portable artifacts under `portable/` when this environment cannot push to `main`.
- Keep scientific effect **NONE**: never promote, close, or discharge claims, premises, prizes, or lemmas.
- After meaningful work: commit, push `cursor/*` branches, land on trial `main` when PR create is 403.
- Owner land scripts (`owner_land_path_*.sh`) are technical fallback for GitHub App 403 only — not approval gates.
- Blocked or need a second pair of hands? Drop a card in [`needs_attention/cards/`](needs_attention/README.md) (schema `needs_attention/v1`; `python3 scripts/needs_attention_check.py`). Helpers cycle that folder with `scripts/needs_attention_scan.py`. Before fixing a repo-wide problem, check the open cards — four agents shipped the same tip-drift fix in parallel (NA-0007).

## Formal verification layer (Layer 1 — Batch 828, owner pre-approved)

`formal/` holds the Lean 4 + Mathlib lane that turns provenance-bound
natural-language proofs into provenance-bound **kernel-checked** proofs.
Read [`docs/FORMAL_VERIFICATION_LAYER.md`](docs/FORMAL_VERIFICATION_LAYER.md)
before touching it. Rules for every agent (Cursor, ChatGPT/Codex, Claude,
Grok, future):

- Extend `formal/lean/` (pins: Lean `v4.19.0`, Mathlib `c44e0c8e…` — same as
  `main`'s recovered GP-FOR-192 bundle). Never start a divergent Lean project.
- Status is **earned** by `python3 scripts/formal_gate.py` (`--run-lake`),
  never hand-declared. Ladder: `none → specified → proved → kernel_checked`.
  Editing a `.lean` file invalidates the receipt; run `--pin` then `--run-lake`.
- Hypotheses **are** the scope. Anything Mathlib lacks becomes an explicit
  hypothesis or a declared `explicit_axioms` entry with a blueprint note.
- Every term in a formal statement must be a sourced row in
  `formal/GLOSSARY.md`; UNMAPPED rows may not be used.
- `kernel_checked` = verification level **L5** (metadata) — still
  `author_side` until a **distinct-organization** reviewer signs the
  informal↔formal alignment in `formal/blueprint/<ID>.md`.
- Cross-repo handoff for `main` and the other owner repos:
  `portable/formal-layer/` (`HANDOFF.md`, `AGENTS_ADDENDUM.md`).

## Never

- Grow `registers/`, `claims/`, or Drive vault mirrors here.
- Cite a green `trial` test as research evidence.
- Cite a green `lake build` / `formal_gate.py` run as claim acceptance — it is
  a kernel check (L5 evidence), not promotion, closure, or discharge.
- Declare `kernel_checked` without a binding receipt in `formal/receipts/`.
- Enable or claim GitHub scheduled workflows on `main` solely to satisfy R2-06 prose.
- Ask Dylan for approval in docs.

## Start here

1. `README.md`
2. `docs/PROJECT_INTENT_AUDIT.md`
3. `docs/OWNER_ACTIONS_MAIN.md`
4. `docs/MULTI_AGENT_ACCESS.md` — grant Cursor + ChatGPT/Codex + Claude + Grok (PAT) Read/write on all **8** owner repos including **sandbox** (`./scripts/owner_grant_ai_agent_access.sh`; App UI: select ALL repositories including sandbox)
5. `docs/AUTONOMOUS_48H_LOG.md` (if an autonomous window is active)
6. `docs/FORMAL_VERIFICATION_LAYER.md` + `formal/README.md` — Layer 1 Lean lane (Batch 828)
