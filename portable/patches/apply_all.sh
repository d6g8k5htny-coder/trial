#!/usr/bin/env bash
# Apply all portable engineering patches onto a writable checkout of
# d6g8k5htny-coder/main (working tip chatgpt/drive-github-hardening-20260919).
# See BASE_TIP.txt for the currently verified tip SHA (batch 16: 340d98a).
#
# Scientific effect: NONE. Does not flip lemma_closed / discharge obligations.
# Usage (from a clean main checkout at the base tip, or a descendant):
#   /path/to/trial/portable/patches/apply_all.sh          # apply
#   /path/to/trial/portable/patches/apply_all.sh --check  # dry-run only
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CHECK_ONLY=0
if [[ "${1:-}" == "--check" ]]; then
  CHECK_ONLY=1
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--check]" >&2
  exit 2
fi

BASE_FILE="$ROOT/BASE_TIP.txt"
if [[ -f "$BASE_FILE" ]]; then
  echo "Patches cut against: $(cat "$BASE_FILE")"
fi

if [[ ! -f tools/carriers_verify.py || ! -f docs/math_status/PACKET.json ]]; then
  echo "error: run from a d6g8k5htny-coder/main checkout root" >&2
  exit 2
fi

PATCHES=(
  "$ROOT/0001-carriers-verify-ignore-bytecode-caches.patch"
  "$ROOT/0002-math-console-path-honesty.patch"
  "$ROOT/0003-gaussian-moments-parametrize-list.patch"
  "$ROOT/0004-git-fixture-timeout-60s.patch"
)

for p in "${PATCHES[@]}"; do
  git apply --check "$p"
done

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo "Check OK (no changes applied)."
  exit 0
fi

for p in "${PATCHES[@]}"; do
  git apply "$p"
done

echo "Applied. Recommended verification:"
echo "  python3 tools/math_status_check.py"
echo "  python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py"
