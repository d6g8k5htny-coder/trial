#!/usr/bin/env bash
# Run after Path A (PR #2 merge) or Path B (Option-B notice) on default main.
# Scientific effect: NONE.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "trial root: $ROOT"

python3 "$ROOT/scripts/watch_main_alignment.py" | tee /tmp/watch_main_alignment.json
state="$(python3 -c "import json;print(json.load(open('/tmp/watch_main_alignment.json'))['state'])")"
echo "state=$state"
if [[ "$state" != "ALIGNED" ]]; then
  echo "Default tip is still MISALIGNED. Land Path A or B first (see portable/LAND.md)." >&2
  exit 1
fi

echo "Aligned. Optional: clone working tip and apply engineering patches (Path C)."
echo "  git clone https://github.com/d6g8k5htny-coder/main.git && cd main"
echo "  git checkout chatgpt/drive-github-hardening-20260919"
echo "  $ROOT/portable/patches/apply_all.sh"
echo "Remember: lemma_closed must stay false; green ≠ discharge."
