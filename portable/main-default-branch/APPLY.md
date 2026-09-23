# Apply: honest default-branch README (+ AGENTS) for `d6g8k5htny-coder/main`

**Effect:** documentation-only on default `main`. No claim status moves.
**Does not** enable `research.yml` schedules (respect R2-06).

## When to use this

Use when default `main` is **MISALIGNED** (complexity face, or Dylan’s
honest program-map at `c2b0620` that still fails the q0/notice auditor) and
you want Path B ALIGNED restore. **HOLD on PR #2 is VOID** — prefer this
notice over re-merging the full PR #2 stack; optional Path A is
`PATH_A_MODE=revert32`.

Batch **58** ships a stronger pack: Option-B README **and** root `AGENTS.md`
(notice-only; points at the hardening branch).

## Steps (owner / write-access agent on `main`)

### Fast path — one-command restore (preferred)

```bash
./scripts/restore_main_face.sh --dry-run   # certainty JSON
./scripts/restore_main_face.sh             # dry-run then branch+PR
# ./scripts/restore_main_face.sh --direct-main
```

### Fast path — owner script

```bash
./scripts/owner_land_path_b.sh --dry-run   # certainty JSON
./scripts/owner_land_path_b.sh             # branch + PR
```

### Fast path — apply the format-patch

Cut against default `main` @ `c2b0620289fde84d721670cf14037fd5673654b7`
(Batch 58 stronger pack: README + AGENTS.md + quarantine body):

```bash
git clone https://github.com/d6g8k5htny-coder/main.git
cd main
git checkout main
git checkout -b cursor/default-branch-notice-<suffix>
git am /path/to/trial/portable/main-default-branch/0001-option-b-default-branch-notice.patch
git push -u origin HEAD
# Open PR into main; merge when satisfied.
```

### Manual path

```bash
git clone https://github.com/d6g8k5htny-coder/main.git
cd main
git checkout main
git checkout -b cursor/default-branch-notice-<suffix>

cp /path/to/trial/portable/main-default-branch/README.md ./README.md
cp /path/to/trial/portable/main-default-branch/AGENTS.md ./AGENTS.md
mkdir -p quarantine/pre-q0-scaffolding
git mv body quarantine/pre-q0-scaffolding/body.js
printf '%s\n' \
  '# Pre-q0 scaffolding' \
  '' \
  'Moved off the repository root so default `main` is not mistaken for a' \
  'complexity-physics product. Zero evidentiary authority. Not part of the' \
  'q0 / SIDE24 research program.' \
  > quarantine/pre-q0-scaffolding/README.md
git add quarantine/pre-q0-scaffolding/README.md README.md AGENTS.md
git commit -m "docs: replace default main landing with q0 redirect (Option-B)"
git push -u origin HEAD
```

## Verification

- Root `README.md` mentions q0 / SIDE24 / working branch / PR #2.
- Root `AGENTS.md` present (Batch 58+).
- No complexity-physics face or withdrawal prose that still trips
  `complexity-physics-framework` on default `main`.
- No scientific registers or status labels changed.
- Local auditor (same markers as remote `audit_main_alignment.py`) exits **0**:

```bash
python3 /path/to/trial/scripts/audit_local_tree.py .
# expect: state=ALIGNED; q0_or_notice_markers_present includes
#   "q0 Research Program", "SIDE24", "chatgpt/drive-github-hardening-20260919", "PR #2"
# expect: complexity_markers_present == []; root_has_AGENTS_md=true
# or: python3 /path/to/trial/scripts/path_b_dry_run.py   # would_align=true
# or: ./scripts/restore_main_face.sh --dry-run
```

After the notice is on *remote* default `main`, `scripts/audit_main_alignment.py`
and `scripts/watch_main_alignment.py` should also exit **0** (ALIGNED).

Batch **58** dry-run (2026-09-23): tip still `c2b0620` (honest program map).
Stronger Option-B (README+AGENTS) → `git am` OK / local auditor **ALIGNED**
(`would-align=true`). Write still 403 from trial.

## Non-claims

Applying this notice is not a merge of the research tree and not a deployment
of scheduled GitHub Actions. Scientific effect: **NONE**.
