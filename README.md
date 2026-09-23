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

Agents often land here from mobile while the live work is on `main`. Default `main` on that repo
now carries the q0 program via merged [PR #2](https://github.com/d6g8k5htny-coder/main/pull/2)
(`audit_main_alignment` → **ALIGNED**). Hardening tip `chatgpt/drive-github-hardening-20260919`
remains ahead with portable engineering patches under `portable/patches/`.

This repository now:

1. States that boundary in the README (above).
2. Records a full audit in [`docs/PROJECT_INTENT_AUDIT.md`](docs/PROJECT_INTENT_AUDIT.md).
3. Gives the owner an exact fix plan in [`docs/OWNER_ACTIONS_MAIN.md`](docs/OWNER_ACTIONS_MAIN.md).
4. Ships a tiny sanity suite so “testing” is executable, not a blank stub.

## Portable fixes for `main` (owner apply)

After PR #2 merged (default tip ALIGNED), run **Actions → `land-option-b-on-main`** only if you still want the Option-B notice, or apply Path C portable patches with write access / `MAIN_PUSH_TOKEN`.

This sandbox cannot push to `d6g8k5htny-coder/main`. Ready-to-apply artifacts:

- [`portable/main-default-branch/`](portable/main-default-branch/) — Option-B redirect README + `APPLY.md`
- [`portable/pr2-landing/`](portable/pr2-landing/) — checklist + `VERIFY_AFTER_MERGE.sh` for MERGEABLE PR #2
- [`portable/LAND.md`](portable/LAND.md) — Path A/B/C one-page land instructions (needs write access to `main`)
- [`portable/OWNER_ONE_LINERS.md`](portable/OWNER_ONE_LINERS.md) — copy-paste Path A (`gh pr ready/merge 2`), Path B (Actions + token), Path C (`apply_all`)
- [`portable/CONFLICTING_PR_NOTES.md`](portable/CONFLICTING_PR_NOTES.md) — rebase/close guidance for dirty drafts #3/#12
- [`portable/patches/`](portable/patches/) — engineering patches 0001–0004 + 0008–0016 + [`COMPATIBILITY.md`](portable/patches/COMPATIBILITY.md) matrix (BASE_TIP `890bb81` after PR #28; tip-cut 0005/0006/0007 dropped)
- [`scripts/audit_main_alignment.py`](scripts/audit_main_alignment.py) — read-only GitHub API check (exit 1 while default tip is still the pre-q0 face)
- [`scripts/alignment_status.py`](scripts/alignment_status.py) — combined alignment dashboard JSON
- [`scripts/watch_main_alignment.py`](scripts/watch_main_alignment.py) — timer-friendly ALIGNED/MISALIGNED watcher
- [`scripts/probe_main_write.py`](scripts/probe_main_write.py) — write probe (exit 0=writable, 1=denied, 2=transport)
- [`scripts/print_owner_unblock.sh`](scripts/print_owner_unblock.sh) — dump OWNER_ONE_LINERS paths + live probe/audit one-liners

Agent rules: [`AGENTS.md`](AGENTS.md). Autonomous work log: [`docs/AUTONOMOUS_48H_LOG.md`](docs/AUTONOMOUS_48H_LOG.md).

## Quick check

```bash
python3 -m pytest -q
python3 scripts/audit_main_alignment.py
./scripts/pack_portable.sh /tmp/trial-portable-main-fixes.tgz
```

## Non-claims

- Nothing here updates `lemma_closed`, prize status, or premise discharge on the research program.
- A green test in `trial` is not a certificate in `main`.
