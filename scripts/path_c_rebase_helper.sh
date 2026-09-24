#!/usr/bin/env bash
# Path C rebase helper (Batch 68): document + optionally stage owner-safe
# ours/theirs choices for the known post-#41 first-stop conflicts.
#
# Context (see portable/PATH_C_REBASE_CONFLICT_REPORT_67.json):
#   Rebasing chatgpt/drive-github-hardening-20260919 onto origin/main CONFLICTS on:
#     .github/workflows/ci.yml          (content)
#     .github/workflows/research.yml    (modify/delete: deleted on main)
#     engine/bridge/README.md           (modify/delete: deleted on main)
#
# Primary advice: DO NOT rebase. Keep Path C on hardening BASE_TIP.
# This helper exists for owners who still need a mechanical resolve step.
#
# During `git rebase origin/main` (hardening commits replayed onto main):
#   ours   = onto (main / HEAD)
#   theirs = commit being applied (hardening)
#
# Scientific effect: NONE.
# Never flip lemma_closed / prizes / premises / research status.
# Never edit docs/math_status/PACKET.json, registers/, or claims/.
#
# Usage:
#   ./scripts/path_c_rebase_helper.sh --dry-run
#   ./scripts/path_c_rebase_helper.sh --notes
#   ./scripts/path_c_rebase_helper.sh --stage --profile keep-hardening-engineering
#   ./scripts/path_c_rebase_helper.sh --stage --profile preserve-main-face
#   PATH_C_REBASE_WORKDIR=/path/to/rebase-wt ./scripts/path_c_rebase_helper.sh --dry-run
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRIAL_ROOT="${TRIAL_ROOT:-$ROOT}"
WORKDIR="${PATH_C_REBASE_WORKDIR:-}"
PROFILE="${PATH_C_REBASE_PROFILE:-keep-hardening-engineering}"
MODE="notes"
JSON_OUT=""
ABORT_ADVICE=1

# Known first-stop conflict paths (Batch 67 probe; re-check with path_c_dry_run).
CI_YML=".github/workflows/ci.yml"
RESEARCH_YML=".github/workflows/research.yml"
BRIDGE_README="engine/bridge/README.md"

# Paths this helper must never invent / rewrite (research status surface).
FORBIDDEN_TOUCH=(
  "docs/math_status/PACKET.json"
  "docs/math_status/STATUS.json"
  "registers"
  "claims"
)

die() {
  echo "path_c_rebase_helper: ERROR: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage: path_c_rebase_helper.sh [--dry-run|--notes|--stage] [--profile NAME] [options]

Modes:
  --dry-run   Print the resolution strategy + what would be staged (default-ish; no git writes).
  --notes     Print owner-safe resolution notes only (same as dry-run without workdir checks).
  --stage     Stage ours/theirs choices in an in-progress rebase worktree (requires CONFLICTS).

Profiles (PATH_C_REBASE_PROFILE / --profile):
  keep-hardening-engineering  (default)
      During rebase onto main: take hardening (theirs) for ci.yml + keep
      research.yml + bridge README as left in tree (git add). Engineering only —
      does not enable schedules, does not edit PACKET/lemma_closed.
  preserve-main-face
      Take main (ours) for ci.yml; git rm research.yml + bridge README
      (keep post-#41 ALIGNED landing deletions). Still does not touch research status.

Options:
  --workdir DIR     Rebase worktree (or set PATH_C_REBASE_WORKDIR)
  --json-out PATH   Write strategy JSON to PATH
  --no-abort-advice Suppress the "prefer abort; keep hardening" banner
  -h, --help        Show this help

Env:
  TRIAL_ROOT              Trial checkout (default: repo containing this script)
  PATH_C_REBASE_WORKDIR   In-progress rebase worktree
  PATH_C_REBASE_PROFILE   keep-hardening-engineering | preserve-main-face

Exit:
  0  dry-run/notes OK, or stage completed
  1  stage failed / bad state
  2  usage / missing inputs

Scientific effect: NONE. Prefer NOT rebasing — use owner_land_path_c on hardening.
EOF
}

print_banner() {
  if [[ "$ABORT_ADVICE" -eq 1 ]]; then
    cat <<'EOF'
=== Path C rebase helper — owner-safe conflict strategy ===
PRIMARY: do NOT rebase hardening onto main after PR #41.
  Recommended: git rebase --abort
  Keep Path C on chatgpt/drive-github-hardening-20260919 (BASE_TIP).
  Land: ./scripts/owner_land_path_c.sh --dry-run && ./scripts/owner_land_path_c.sh
  Certainty: ./scripts/path_c_dry_run.py
  Report: portable/PATH_C_REBASE_CONFLICT_REPORT_67.json

If you still resolve the first-stop conflicts, use a profile below.
Scientific effect: NONE. Never flip lemma_closed / research status.
EOF
    echo
  fi
}

strategy_rows() {
  local profile="$1"
  case "$profile" in
    keep-hardening-engineering)
      cat <<EOF
path	conflict_kind	choice	git_action	rationale
$CI_YML	content	theirs (hardening)	git checkout --theirs -- $CI_YML && git add -- $CI_YML	Keep hardening CI pins/coverage; engineering only
$RESEARCH_YML	modify/delete	keep hardening file	git add -- $RESEARCH_YML	File deleted on main; version left in tree is hardening — stage as-is; do NOT edit cron/schedules; do NOT invent status
$BRIDGE_README	modify/delete	keep hardening file	git add -- $BRIDGE_README	Docs/agents bridge README from hardening; no research status fields
EOF
      ;;
    preserve-main-face)
      cat <<EOF
path	conflict_kind	choice	git_action	rationale
$CI_YML	content	ours (main)	git checkout --ours -- $CI_YML && git add -- $CI_YML	Preserve ALIGNED landing CI face
$RESEARCH_YML	modify/delete	delete (ours)	git rm -f -- $RESEARCH_YML	Keep main deletion; do not reintroduce research workflow on landing tip
$BRIDGE_README	modify/delete	delete (ours)	git rm -f -- $BRIDGE_README	Keep main deletion of relocated bridge docs
EOF
      ;;
    *)
      die "unknown profile: $profile (want keep-hardening-engineering|preserve-main-face)"
      ;;
  esac
}

emit_json() {
  local profile="$1"
  local mode="$2"
  local workdir_state="$3"
  python3 - "$profile" "$mode" "$workdir_state" "$JSON_OUT" <<'PY'
import json, sys
from datetime import datetime, timezone

profile, mode, workdir_state, out = sys.argv[1:5]
rows = {
    "keep-hardening-engineering": [
        {
            "path": ".github/workflows/ci.yml",
            "conflict_kind": "content",
            "choice": "theirs",
            "side_meaning": "hardening commit being replayed",
            "git": ["git checkout --theirs -- .github/workflows/ci.yml", "git add -- .github/workflows/ci.yml"],
        },
        {
            "path": ".github/workflows/research.yml",
            "conflict_kind": "modify/delete",
            "choice": "keep_theirs_file",
            "side_meaning": "hardening version left in tree after modify/delete",
            "git": ["git add -- .github/workflows/research.yml"],
            "guard": "Do not edit on:/schedule:; do not claim R2-06; never flip lemma_closed",
        },
        {
            "path": "engine/bridge/README.md",
            "conflict_kind": "modify/delete",
            "choice": "keep_theirs_file",
            "side_meaning": "hardening version left in tree",
            "git": ["git add -- engine/bridge/README.md"],
        },
    ],
    "preserve-main-face": [
        {
            "path": ".github/workflows/ci.yml",
            "conflict_kind": "content",
            "choice": "ours",
            "side_meaning": "main (rebase onto)",
            "git": ["git checkout --ours -- .github/workflows/ci.yml", "git add -- .github/workflows/ci.yml"],
        },
        {
            "path": ".github/workflows/research.yml",
            "conflict_kind": "modify/delete",
            "choice": "delete_ours",
            "side_meaning": "keep main deletion",
            "git": ["git rm -f -- .github/workflows/research.yml"],
        },
        {
            "path": "engine/bridge/README.md",
            "conflict_kind": "modify/delete",
            "choice": "delete_ours",
            "side_meaning": "keep main deletion",
            "git": ["git rm -f -- engine/bridge/README.md"],
        },
    ],
}
payload = {
    "artifact": "PATH_C_REBASE_RESOLUTION_NOTES",
    "batch": "68",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "scientific_effect": "NONE",
    "lemma_closed": False,
    "goal_complete": False,
    "mode": mode,
    "profile": profile,
    "workdir_state": workdir_state,
    "primary_advice": "DO_NOT_REBASE — keep Path C on chatgpt/drive-github-hardening-20260919",
    "do_not_set_path_c_rebase_onto_main": True,
    "do_not_set_path_c_base_main": True,
    "ours_theirs_note": (
        "During git rebase onto main: ours=main (onto), theirs=hardening commit being applied. "
        "modify/delete leaves the hardening file in tree until git add (keep) or git rm (delete)."
    ),
    "never_touch": [
        "docs/math_status/PACKET.json",
        "docs/math_status/STATUS.json",
        "registers/",
        "claims/",
        "lemma_closed",
        "prize/premise discharge",
    ],
    "known_first_stop_paths": [
        ".github/workflows/ci.yml",
        ".github/workflows/research.yml",
        "engine/bridge/README.md",
    ],
    "source_conflict_report": "portable/PATH_C_REBASE_CONFLICT_REPORT_67.json",
    "resolutions": rows[profile],
    "after_stage": [
        "git status  # confirm only the three paths resolved; no PACKET edits",
        "git rebase --continue   # expect further commits; re-run helper if new conflicts",
        "OR: git rebase --abort  # preferred — return to hardening tip",
    ],
    "owner_land": "./scripts/owner_land_path_c.sh --dry-run && ./scripts/owner_land_path_c.sh",
}
text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
print(text, end="")
if out:
    open(out, "w", encoding="utf-8").write(text)
PY
}

detect_workdir_state() {
  local wd="$1"
  if [[ -z "$wd" ]]; then
    echo "no_workdir"
    return 0
  fi
  if [[ ! -d "$wd/.git" && ! -f "$wd/.git" ]]; then
    echo "missing_git"
    return 0
  fi
  if [[ ! -d "$wd/.git/rebase-merge" && ! -d "$wd/.git/rebase-apply" ]]; then
    # worktree: .git may be a file; check common rebase dirs via git
    if ! git -C "$wd" rev-parse --git-path rebase-merge >/dev/null 2>&1; then
      echo "not_rebasing"
      return 0
    fi
    local rm_path ra_path
    rm_path="$(git -C "$wd" rev-parse --git-path rebase-merge 2>/dev/null || true)"
    ra_path="$(git -C "$wd" rev-parse --git-path rebase-apply 2>/dev/null || true)"
    if [[ ! -d "${rm_path:-/__nope__}" && ! -d "${ra_path:-/__nope__}" ]]; then
      echo "not_rebasing"
      return 0
    fi
  fi
  local unmerged
  unmerged="$(git -C "$wd" diff --name-only --diff-filter=U 2>/dev/null || true)"
  if [[ -z "$unmerged" ]]; then
    # modify/delete may show in status porcelain without UU
    if git -C "$wd" status --porcelain 2>/dev/null | grep -qE '^(DU|UD|UA|AU|AA|UU) '; then
      echo "rebasing_conflicts"
      return 0
    fi
    echo "rebasing_clean_or_unrelated"
    return 0
  fi
  echo "rebasing_conflicts"
}

assert_no_forbidden_staged() {
  local wd="$1"
  local staged
  staged="$(git -C "$wd" diff --cached --name-only 2>/dev/null || true)"
  local f
  for f in "${FORBIDDEN_TOUCH[@]}"; do
    if printf '%s\n' "$staged" | grep -qE "^${f}(/|$)"; then
      die "refusing to proceed: forbidden research-status path staged: $f"
    fi
  done
}

stage_profile() {
  local wd="$1"
  local profile="$2"
  local state
  state="$(detect_workdir_state "$wd")"
  [[ "$state" == "rebasing_conflicts" || "$state" == "rebasing_clean_or_unrelated" ]] || \
    die "workdir not in rebase conflict state (got $state). Set PATH_C_REBASE_WORKDIR to the conflicted tree."

  case "$profile" in
    keep-hardening-engineering)
      # Content conflict: take hardening (theirs during rebase).
      if git -C "$wd" ls-files -u -- "$CI_YML" | grep -q .; then
        git -C "$wd" checkout --theirs -- "$CI_YML"
        git -C "$wd" add -- "$CI_YML"
      elif [[ -f "$wd/$CI_YML" ]]; then
        git -C "$wd" add -- "$CI_YML" || true
      fi
      # modify/delete: hardening file left in tree → keep via add
      if [[ -e "$wd/$RESEARCH_YML" ]]; then
        git -C "$wd" add -- "$RESEARCH_YML"
      else
        die "expected $RESEARCH_YML present (modify/delete left hardening version); aborting"
      fi
      if [[ -e "$wd/$BRIDGE_README" ]]; then
        git -C "$wd" add -- "$BRIDGE_README"
      else
        die "expected $BRIDGE_README present (modify/delete left hardening version); aborting"
      fi
      ;;
    preserve-main-face)
      if git -C "$wd" ls-files -u -- "$CI_YML" | grep -q .; then
        git -C "$wd" checkout --ours -- "$CI_YML"
        git -C "$wd" add -- "$CI_YML"
      fi
      git -C "$wd" rm -f -- "$RESEARCH_YML" 2>/dev/null || true
      git -C "$wd" rm -f -- "$BRIDGE_README" 2>/dev/null || true
      ;;
    *)
      die "unknown profile: $profile"
      ;;
  esac

  assert_no_forbidden_staged "$wd"
  echo "path_c_rebase_helper: staged profile=$profile in $wd"
  echo "path_c_rebase_helper: next: inspect with git status; then git rebase --continue"
  echo "path_c_rebase_helper: or prefer: git rebase --abort  # keep Path C on hardening"
  git -C "$wd" status --short -- "$CI_YML" "$RESEARCH_YML" "$BRIDGE_README" || true
}

# --- args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --notes) MODE="notes"; shift ;;
    --stage) MODE="stage"; shift ;;
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --workdir) WORKDIR="${2:-}"; shift 2 ;;
    --json-out) JSON_OUT="${2:-}"; shift 2 ;;
    --no-abort-advice) ABORT_ADVICE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown arg: $1 (see --help)" ;;
  esac
done

case "$PROFILE" in
  keep-hardening-engineering|preserve-main-face) ;;
  *) die "unknown profile: $PROFILE" ;;
esac

print_banner
echo "profile: $PROFILE"
echo "mode: $MODE"
echo
echo "=== resolution table ==="
strategy_rows "$PROFILE" | column -t -s $'\t' 2>/dev/null || strategy_rows "$PROFILE"
echo

WD_STATE="no_workdir"
if [[ -n "$WORKDIR" ]]; then
  WD_STATE="$(detect_workdir_state "$WORKDIR")"
  echo "workdir: $WORKDIR ($WD_STATE)"
fi

# Always emit notes JSON to stdout when --json-out or dry-run/notes
if [[ "$MODE" == "dry-run" || "$MODE" == "notes" || -n "$JSON_OUT" ]]; then
  echo "=== resolution notes JSON ==="
  emit_json "$PROFILE" "$MODE" "$WD_STATE"
fi

if [[ "$MODE" == "stage" ]]; then
  [[ -n "$WORKDIR" ]] || die "--stage requires --workdir / PATH_C_REBASE_WORKDIR"
  stage_profile "$WORKDIR" "$PROFILE"
fi

echo "path_c_rebase_helper: done (scientific_effect=NONE; lemma_closed untouched)"
exit 0
