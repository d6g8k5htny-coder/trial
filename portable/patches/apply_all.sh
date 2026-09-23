#!/usr/bin/env bash
# Apply all portable engineering patches onto a writable checkout of
# d6g8k5htny-coder/main (working tip chatgpt/drive-github-hardening-20260919).
#
# Scientific effect: NONE. Does not flip lemma_closed / discharge obligations.
# Usage (from a clean main checkout at the base tip, or a descendant):
#   /path/to/trial/portable/patches/apply_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE_FILE="$ROOT/BASE_TIP.txt"
if [[ -f "$BASE_FILE" ]]; then
  echo "Patches cut against: $(cat "$BASE_FILE")"
fi

if [[ ! -f tools/carriers_verify.py || ! -f docs/math_status/PACKET.json ]]; then
  echo "error: run from a d6g8k5htny-coder/main checkout root" >&2
  exit 2
fi

git apply --check "$ROOT/0001-carriers-verify-ignore-bytecode-caches.patch"
git apply --check "$ROOT/0002-math-console-path-honesty.patch"
git apply --check "$ROOT/0003-gaussian-moments-parametrize-list.patch"
git apply --check "$ROOT/0004-git-fixture-timeout-60s.patch"
git apply "$ROOT/0001-carriers-verify-ignore-bytecode-caches.patch"
git apply "$ROOT/0002-math-console-path-honesty.patch"
git apply "$ROOT/0003-gaussian-moments-parametrize-list.patch"
git apply "$ROOT/0004-git-fixture-timeout-60s.patch"

echo "Applied. Recommended verification:"
echo "  python3 tools/math_status_check.py"
echo "  python3 -m pytest -q tests/test_carriers.py tests/test_math_status.py tests/test_inventable_jetmod_probes.py tests/test_gaussian_moments.py"
