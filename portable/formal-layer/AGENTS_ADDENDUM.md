## Formal verification layer (Layer 1 — Lean 4 + Mathlib; adopted 2026-09-27, owner pre-approved)

A machine-checked lane now sits on top of the provenance / scope /
no-status-promotion stack. Canonical location: `d6g8k5htny-coder/trial`
→ `formal/` (until landed on `main`). Design + coordination:
`docs/FORMAL_VERIFICATION_LAYER.md`; handoff: `portable/formal-layer/HANDOFF.md`.

Rules for every agent (Cursor, ChatGPT/Codex, Claude, Grok, future):

- Pins are shared: Lean `leanprover/lean4:v4.19.0`, Mathlib
  `c44e0c8ee63ca166450922a373c7409c5d26b00b` (== recovered GP-FOR-192 bundle).
  Never start a divergent Lean project; extend `formal/lean/`.
- Formalization status is **earned** by `python3 scripts/formal_gate.py`
  (`--run-lake`), never hand-declared. Ladder:
  `none → specified → proved → kernel_checked`. Editing a `.lean` file
  invalidates the receipt (`--pin`, then `--run-lake`, commit receipt).
- Hypotheses **are** the scope. Anything Mathlib lacks becomes an explicit
  hypothesis or a declared `explicit_axioms` entry with a blueprint note.
- Every term in a formal statement must be a sourced row in
  `formal/GLOSSARY.md`; UNMAPPED rows may not be used.
- `kernel_checked` = verification level **L5** (evidence metadata only;
  `verification_level ≠ acceptance`). It stays `author_side` until a
  **distinct-organization** reviewer signs the informal↔formal alignment in
  `formal/blueprint/<ID>.md`. Same-provider review earns zero independence.
- Never cite a green `lake build` / gate run as claim acceptance, lemma
  closure, prize status or premise discharge. `lemma_closed` stays `false`.
- No `schedule:` triggers on formal workflows (R2-06 rule).
