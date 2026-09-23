# trial

Owner sandbox for Dylan Roy. **Not** the research repository.

| Repo | Role |
|------|------|
| [`d6g8k5htny-coder/main`](https://github.com/d6g8k5htny-coder/main) | q0 / SIDE24 research program (Drive → git). Governing intent lives there. |
| **this repo** | Empty-by-design testing / agent landing pad. CC0. No scientific authority. |

## Intent (this repository)

- Hold lightweight probes, agent smoke checks, and notes that must not touch research registers.
- Never promote, close, or discharge a claim from the q0 program.
- Never mirror `registers/`, frozen bodies, or Drive vault material here.

## What was wrong (and what this change fixes)

Agents often land here from mobile while the live work is on `main`. Default `main` on that repo still shows an abandoned December 2025 “complexity physics” README, while the real program (4,200+ files) sits on unmerged working branches rooted at draft [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2).

This repository now:

1. States that boundary in the README (above).
2. Records a full audit in [`docs/PROJECT_INTENT_AUDIT.md`](docs/PROJECT_INTENT_AUDIT.md).
3. Gives the owner an exact fix plan in [`docs/OWNER_ACTIONS_MAIN.md`](docs/OWNER_ACTIONS_MAIN.md).
4. Ships a tiny sanity suite so “testing” is executable, not a blank stub.

## Portable fixes for `main` (owner apply)

This sandbox cannot push to `d6g8k5htny-coder/main`. Ready-to-apply artifacts:

- [`portable/main-default-branch/`](portable/main-default-branch/) — Option-B redirect README + `APPLY.md`
- [`scripts/audit_main_alignment.py`](scripts/audit_main_alignment.py) — read-only GitHub API check (exit 1 while default tip is still the pre-q0 face)

Agent rules: [`AGENTS.md`](AGENTS.md). Autonomous work log: [`docs/AUTONOMOUS_48H_LOG.md`](docs/AUTONOMOUS_48H_LOG.md).

## Quick check

```bash
python3 -m pytest -q
python3 scripts/audit_main_alignment.py
```

## Non-claims

- Nothing here updates `lemma_closed`, prize status, or premise discharge on the research program.
- A green test in `trial` is not a certificate in `main`.
