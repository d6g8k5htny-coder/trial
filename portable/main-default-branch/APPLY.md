# Apply: honest default-branch README for `d6g8k5htny-coder/main`

**Effect:** documentation-only on default `main`. No claim status moves.
**Does not** merge PR #2 or enable `research.yml` schedules (respect R2-06).

## When to use this

Use when you want visitors to stop seeing the abandoned complexity-physics
README **before** you are ready to merge the full Drive→git port (PR #2).

Prefer merging PR #2 (Option A in `docs/OWNER_ACTIONS_MAIN.md`) when ready.

## Steps (owner / write-access agent on `main`)

### Fast path — apply the format-patch (preferred)

Cut against default `main` @ `f25b04bb931df2eaee302b666db014913486166b`:

```bash
git clone https://github.com/d6g8k5htny-coder/main.git
cd main
git checkout main
git checkout -b cursor/default-branch-notice-<suffix>
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
# or: git apply … && git commit …
git push -u origin HEAD
# Open draft PR into main; merge when satisfied.
```

### Manual path

```bash
git clone https://github.com/d6g8k5htny-coder/main.git
cd main
git checkout main
git checkout -b cursor/default-branch-notice-<suffix>

cp /path/to/trial/portable/main-default-branch/README.md ./README.md
mkdir -p quarantine/pre-q0-scaffolding
git mv body quarantine/pre-q0-scaffolding/body.js
printf '%s\n' \
  '# Pre-q0 scaffolding' \
  '' \
  'Moved off the repository root so default `main` is not mistaken for a' \
  'complexity-physics product. Zero evidentiary authority.' \
  > quarantine/pre-q0-scaffolding/README.md
git add quarantine/pre-q0-scaffolding/README.md README.md
git commit -m "docs: replace abandoned complexity-physics README with q0 redirect"
git push -u origin HEAD
```

## Verification

- Root `README.md` mentions the working branch and PR #2.
- No “✅ Confirmed” complexity-physics validation table remains on default `main`.
- No scientific registers or status labels changed.

## Non-claims

Applying this notice is not a merge of the research tree and not a deployment
of scheduled GitHub Actions.
