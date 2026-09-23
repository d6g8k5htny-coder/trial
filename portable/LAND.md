# One-command land paths for `d6g8k5htny-coder/main`

**Scientific effect: NONE** for documentation / packaging lands below.
Requires a credential that can push to `d6g8k5htny-coder/main`.
This `trial` cloud agent cannot (git push and Git Data API both return 403).

## Path A — land the real tree (preferred)

PR #2 is the Drive→git port onto default `main` (historically MERGEABLE/CLEAN).

```bash
# As repo owner / write-enabled agent:
gh pr ready 2 --repo d6g8k5htny-coder/main
gh pr merge 2 --repo d6g8k5htny-coder/main --merge  # or --squash per your policy
# Predicted merge commit (2026-09-23): 2a960674… — README becomes q0 program; AGENTS.md present.
# Then retarget / rebase hardening (chatgpt/drive-github-hardening-20260919) onto new main
python3 /path/to/trial/portable/pr2-landing/VERIFY_AFTER_MERGE.sh
```

Verify visitors no longer see complexity-physics:

```bash
curl -sL https://raw.githubusercontent.com/d6g8k5htny-coder/main/main/README.md | head
python3 /path/to/trial/scripts/audit_main_alignment.py   # expect exit 0
```

Do **not** enable `research.yml` schedules solely for R2-06 prose.

## Path B — honest redirect until Path A

```bash
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git checkout main
git checkout -b cursor/default-branch-notice
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
python3 /path/to/trial/scripts/audit_local_tree.py .   # expect ALIGNED (would-align)
git push -u origin HEAD
gh pr create --base main --title "docs: q0 redirect on default main" --body "Option-B notice. Scientific effect NONE. Prefer merging PR #2 when ready."
```

Batch **22** local dry-run on default tip `f25b04bb`: `git am` OK; local auditor
**ALIGNED** (all four q0/notice markers; complexity markers cleared; `body`
quarantined). Path B content is sufficient — landing blocked only by write/token.
## Path C — engineering patches on working tip

Against `chatgpt/drive-github-hardening-20260919` (BASE_TIP `1547ec4` — patches apply cleanly):

```bash
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -b cursor/portable-engineering-patches origin/chatgpt/drive-github-hardening-20260919
/path/to/trial/portable/patches/apply_all.sh
# or copy apply_all.sh + patches into the tree
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py \
  tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py \
  tests/test_inventable_jetmod_instrumentation_status.py
git commit -am "fix: carriers pycache, math_console paths, gaussian parametrize, probe restores"
git push -u origin HEAD
```

`lemma_closed` must stay false. Green checks ≠ obligation discharge.

## Stack hygiene

| PR | Role | Note |
|----|------|------|
| #2 | Port onto default `main` | Critical for alignment |
| #15 | Inventable REFUSED probes | Merged into hardening @ `1ea0ae8` |
| #16 | Cold-start nav docs | **Merged** (docs-only) |
| #17 | Fail-closed inventable shortcut refusals | **Merged** @ `3e8f388`; tip-cut 0005 re-cut in batch 17 |
| #18 | PARTIAL/REFUSED STATUS vocab | **Merged** @ `340d98a` (ancestor of `1547ec4`) |
| #19 | Docs AUTHOR_SIDE honesty banners | OPEN draft `dcc0157` **UNSTABLE** (verify pending) onto hardening |
| #20 | Instrumentation PARTIAL/REFUSED_NOT_24JET STATUS | **Merged** @ `1547ec4`; promoted portable **0006** into `apply_all.sh` |
| #21 | Attestations + H3 salvage | MERGEABLE/**CLEAN** onto hardening (base OID `1ea0ae8`, ancestor of tip); patches 0001–0004 apply; inventable tests absent on that base |
| #3, #12 | Older drafts | CONFLICTING after #15 — see [`CONFLICTING_PR_NOTES.md`](CONFLICTING_PR_NOTES.md) |

## Re-launch agents

Point new cloud agents at `d6g8k5htny-coder/main` with write access and base
`chatgpt/drive-github-hardening-20260919` (or default `main` after Path A).


## Automation blocked for this agent

Attempts from the `trial` cloud token (2026-09-23):

| Action | Result |
|--------|--------|
| `git push` to `main` | 403 — denied to cursor[bot] |
| `POST /git/refs` on `main` | 403 — Resource not accessible by integration |
| `gh pr ready 2` / GraphQL markReady | 403 — Resource not accessible by integration |
| `gh pr merge 2` / GraphQL mergePullRequest | 403 — Resource not accessible by integration |
| trial `workflow_dispatch` land-option-b-on-main | 403 — Resource not accessible by integration |

Owner (or a write-enabled `main` agent) must run Path A/B/C.


## Patch regeneration watch

Working tip is **`1547ec4`** (PR #20 merged). Open drafts **#19 / #21** (plus older stack).
Batch **22**: tip still `1547ec4`; `apply_all` 0001–0006 @ 3.11 → focused **90 passed**;
**no tip-level 0007**. Path B dry-run **would-align=true** (local auditor ALIGNED).
Write still 403 from this token. Copy-paste owner commands:
[`OWNER_ONE_LINERS.md`](OWNER_ONE_LINERS.md) or `./scripts/print_owner_unblock.sh`.
Write probe: `scripts/probe_main_write.py`. After further PACKET/`math_console`
merges, re-run `apply_all.sh --check` + focused tests; regenerate **0002** only if
digests drift. PR #21 does not edit PACKET/`math_console`.


## Path B via trial Actions (token secret)

Workflow [`.github/workflows/land-option-b-on-main.yml`](../.github/workflows/land-option-b-on-main.yml):

1. Add Actions secret `MAIN_PUSH_TOKEN` on **trial** (Contents:Write + PullRequests:Write on `main`).
2. Run workflow `land-option-b-on-main` with `dry_run=false`.
3. Workflow `git am`s Option-B, runs `scripts/audit_local_tree.py` (must exit 0 /
   would-align), pushes `cursor/option-b-notice-from-trial` **and opens a PR**
   into default `main` — merge that PR (or Path A).

Default `dry_run=true` verifies `git am` + local auditor (no push).
