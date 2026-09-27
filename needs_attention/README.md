# `needs_attention/` — agent handoff inbox (trial sandbox)

**Scientific effect: NONE.** Coordination only. Not a claim database, not a
work-lease ledger (that is [`governance-/work_leases`](https://github.com/d6g8k5htny-coder/governance-/tree/main/work_leases)),
not review acceptance, not scientific status.

Any agent (Cursor, ChatGPT/Codex, Claude, Grok, a batch-loop worker) that is
**blocked** or needs a second pair of hands drops a **card** here. A helper
agent cycling the folder picks the card up, does the work, records the
resolution, and moves the card to `resolved/`.

## Layout

| Path | Meaning |
|---|---|
| `cards/NA-NNNN-<slug>.json` | Open / in-progress cards (one JSON object each) |
| `resolved/NA-NNNN-<slug>.json` | Resolved or withdrawn cards (immutable once moved) |
| `SNAPSHOT.json` | Last read-only scan of all owner repos (`scripts/needs_attention_scan.py`) |
| `TRIAGE.md` | Human-readable rendering of `SNAPSHOT.json` |

## Card schema (`needs_attention/v1`)

```json
{
  "schema": "needs_attention/v1",
  "id": "NA-0001",
  "title": "short imperative title",
  "status": "OPEN",
  "opened_at": "2026-09-27T19:10:00Z",
  "opened_by": {"provider": "cursor", "model": null, "agent": "cursor[bot]", "run": null},
  "repo": "d6g8k5htny-coder/trial",
  "refs": {"pr": 149, "issue": null, "branch": "cursor/...", "sha": null, "urls": []},
  "blocker": "what is stuck, with evidence (URLs / SHAs / run ids)",
  "ask": "what a helper should do",
  "write_scope": ["scripts/", ".github/workflows/ci.yml"],
  "scientific_effect": "NONE",
  "resolution": null,
  "resolved_at": null,
  "resolved_by": null,
  "resolution_evidence": []
}
```

* `status` ∈ `OPEN` · `IN_PROGRESS` · `RESOLVED` · `WITHDRAWN`.
* `scientific_effect` must be the literal string `NONE`.
* A card must never carry `lemma_closed`, `prize_*`, `premise_*`, `claim_status`,
  `discharge*`, or `promot*` keys — cards are engineering coordination only.
* Cards under `resolved/` must have `status` `RESOLVED`/`WITHDRAWN`, a non-empty
  `resolution`, `resolved_at`, `resolved_by`.
* `id` is unique across `cards/` and `resolved/`; next id = max + 1.

`python3 scripts/needs_attention_check.py` validates every card (exit 1 on any
violation) and runs in `trial-ci` (`sanity`).

## Helper cycle (what an agent working this folder does)

1. `python3 scripts/needs_attention_scan.py` — refresh `SNAPSHOT.json` + `TRIAGE.md`
   (read-only: open PRs with failing checks / merge conflicts / changes
   requested across all owner repos, expired `governance-` leases, open cards).
2. For each `OPEN` card (and each scan finding worth a card): set
   `IN_PROGRESS`, do the work on a `cursor/*` branch, link evidence.
3. Resolve: fill `resolution`, `resolved_at`, `resolved_by`,
   `resolution_evidence`; `git mv` the card into `resolved/`.
4. Commit, push, PR (land on trial `main` only when PR create is 403 — `AGENTS.md`).
5. Repeat while new cards or findings appear.

Unblocking another agent's `cursor/*` PR (merge `main` in, resolve a
loop-owned file): work in a detached worktree, `git fetch origin main`
immediately before the merge, assert zero `<<<<<<<`/`>>>>>>>` lines *before*
committing (the 48h log legitimately contains that literal in prose, so grep
for line-anchored markers), run the PR's own tests, and push within the same
minute — the batch loop prepends to `docs/AUTONOMOUS_48H_LOG.md` roughly every
two minutes and re-conflicts it (NA-0002, NA-0010). Never push to `chatgpt/*`
branches; card those for their author (NA-0008).

## Never

* Promote, close, or discharge any claim, premise, prize, or lemma while
  "resolving" a card. If a card asks for that, `WITHDRAWN` with a pointer to
  `governance-`.
* Mirror `registers/`, `claims/`, or Drive vault material into a card.
* Treat a green `trial` check as research evidence.
