#!/usr/bin/env bash
# Copy the Layer 1 formal-verification lane from this trial checkout into
# another owner repo clone (typically d6g8k5htny-coder/main hardening) and
# optionally append the agent addendum to that repo's AGENTS.md / CLAUDE.md.
#
# Owner tool. It commits nothing and pushes nothing; it stages files and runs
# the static gate so the receiving tree is verified before the owner commits.
#
# Scientific effect: NONE. Never touches registers/, claims/, PACKET.json,
# math_status, lemma_closed, prizes, premises, or review ledgers.
#
# Usage:
#   ./portable/formal-layer/apply_to_repo.sh /path/to/target-clone [--agents] [--dry-run]

set -euo pipefail

TARGET="${1:-}"
shift || true
APPEND_AGENTS=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --agents) APPEND_AGENTS=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

if [[ -z "$TARGET" || ! -d "$TARGET/.git" ]]; then
  echo "apply_to_repo: need a git clone path as first argument" >&2
  exit 2
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET="$(cd "$TARGET" && pwd)"

# Refuse to write into research-status trees.
for forbidden in registers claims PACKET.json; do
  if [[ "$TARGET" == *"/$forbidden"* ]]; then
    echo "apply_to_repo: refusing target inside $forbidden" >&2
    exit 2
  fi
done

FILES=(
  formal/README.md
  formal/GLOSSARY.md
  formal/formalization_status.json
  formal/formalization_status.schema.json
  formal/blueprint
  formal/receipts
  formal/lean/lakefile.toml
  formal/lean/lean-toolchain
  formal/lean/lake-manifest.json
  formal/lean/Side24Formal.lean
  formal/lean/Side24Formal
  formal/lean/tools
  formal/lean/controls
  scripts/formal_gate.py
  tests/test_formal_gate.py
  .github/workflows/formal-gate.yml
  docs/FORMAL_VERIFICATION_LAYER.md
  portable/formal-layer/HANDOFF.md
  portable/formal-layer/AGENTS_ADDENDUM.md
)

echo "apply_to_repo: source=$HERE target=$TARGET dry_run=$DRY_RUN append_agents=$APPEND_AGENTS"
for rel in "${FILES[@]}"; do
  src="$HERE/$rel"
  dst="$TARGET/$rel"
  if [[ ! -e "$src" ]]; then
    echo "  MISSING in source: $rel" >&2
    exit 2
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  would copy $rel"
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  if [[ -d "$src" ]]; then
    rm -rf "$dst"
    cp -R "$src" "$dst"
  else
    cp "$src" "$dst"
  fi
  echo "  copied $rel"
done

if [[ "$APPEND_AGENTS" == "1" && "$DRY_RUN" == "0" ]]; then
  for f in AGENTS.md CLAUDE.md; do
    if [[ -f "$TARGET/$f" ]] && ! grep -q "Formal verification layer (Layer 1" "$TARGET/$f"; then
      printf '\n' >> "$TARGET/$f"
      cat "$HERE/portable/formal-layer/AGENTS_ADDENDUM.md" >> "$TARGET/$f"
      echo "  appended addendum to $f"
    fi
  done
fi

if [[ "$DRY_RUN" == "0" ]]; then
  # .gitignore for Lake build outputs.
  if [[ -f "$TARGET/.gitignore" ]] && ! grep -q '^formal/lean/.lake/' "$TARGET/.gitignore"; then
    printf '\n# Lean/Lake build outputs (formal layer)\nformal/lean/.lake/\n' >> "$TARGET/.gitignore"
    echo "  updated .gitignore"
  fi
  echo "apply_to_repo: running static formal gate in target"
  python3 "$TARGET/scripts/formal_gate.py" --root "$TARGET"
  echo "apply_to_repo: staged nothing, committed nothing. Review with: git -C '$TARGET' status"
  echo "apply_to_repo: lemma_closed=false scientific_effect=NONE"
fi
