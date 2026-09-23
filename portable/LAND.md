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
# Then retarget / rebase hardening (chatgpt/drive-github-hardening-20260919) onto new main
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
git push -u origin HEAD
gh pr create --base main --title "docs: q0 redirect on default main" --body "Option-B notice. Scientific effect NONE. Prefer merging PR #2 when ready."
```

## Path C — engineering patches on working tip

Against `chatgpt/drive-github-hardening-20260919` (or PR #17 tip — patches apply cleanly):

```bash
git clone https://github.com/d6g8k5htny-coder/main.git && cd main
git fetch origin chatgpt/drive-github-hardening-20260919
git checkout -b cursor/portable-engineering-patches origin/chatgpt/drive-github-hardening-20260919
/path/to/trial/portable/patches/apply_all.sh
# or copy apply_all.sh + patches into the tree
python3 tools/math_status_check.py
python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py
git commit -am "fix: carriers pycache, math_console paths, gaussian parametrize"
git push -u origin HEAD
```

`lemma_closed` must stay false. Green checks ≠ obligation discharge.

## Stack hygiene

| PR | Role | Note |
|----|------|------|
| #2 | Port onto default `main` | Critical for alignment |
| #15 | Inventable REFUSED probes | Merged into hardening @ `1ea0ae8` |
| #16 | Cold-start nav docs | Independent |
| #17 | More inventable shortcut refusals | MERGEABLE; our patches still apply |
| #3, #12 | Older drafts | CONFLICTING after #15 — rebase or close |

## Re-launch agents

Point new cloud agents at `d6g8k5htny-coder/main` with write access and base
`chatgpt/drive-github-hardening-20260919` (or default `main` after Path A).


## Automation blocked for this agent

Attempts from the `trial` cloud token (2026-09-23):

| Action | Result |
|--------|--------|
| `git push` to `main` | 403 |
| `POST /git/refs` on `main` | 403 |
| `PUT .../pulls/2/merge` | 403 |
| GraphQL `markPullRequestReadyForReview` on PR #2 | FORBIDDEN |

Owner (or a write-enabled `main` agent) must run Path A/B/C.
