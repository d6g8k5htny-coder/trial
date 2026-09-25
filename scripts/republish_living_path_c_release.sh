#!/usr/bin/env bash
# Republish living Path C release assets when the local pack is newer than the
# GitHub release on trial.
#
# Batch 255 evidence: release batch241-path-c-bundle tgz was 268996 bytes /
# sha256 4e13dc46… while a fresh pack was 343611 bytes / sha256 9275f21b… and
# carried Batch 245–254 script fixes (probe unique-ref, when_writable install
# fallback, pack TMPDIR/living-tag, …) that the release tarball still lacked.
# Bundle/patch digests can match (keep-prior) while the pack tarball is stale.
#
# Scientific effect: NONE. Never flips lemma_closed / research status.
# Never prints tokens / secrets.
#
# Usage:
#   ./scripts/republish_living_path_c_release.sh           # pack + upload if newer
#   ./scripts/republish_living_path_c_release.sh --dry-run  # pack + compare only
#   ./scripts/republish_living_path_c_release.sh --force    # upload even if same
#   ./scripts/republish_living_path_c_release.sh --help

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="${TRIAL_REPO:-d6g8k5htny-coder/trial}"
DRY_RUN=0
FORCE=0
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --out)
      OUT="${2:-}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,22p' "$0"
      exit 0
      ;;
    *)
      echo "republish_living_path_c_release: unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

LIVING_TAG_FILE="$ROOT/portable/LIVING_PATH_C_RELEASE_TAG"
VERIFY_JSON="$ROOT/portable/path-c-applied-bundle/VERIFY.json"
BUNDLE="$ROOT/portable/path-c-applied-bundle/path-c-on-hardening.bundle"
PATCH="$ROOT/portable/path-c-applied-bundle/path-c-on-hardening.patch"

if [[ -f "$LIVING_TAG_FILE" ]]; then
  TAG="$(tr -d '[:space:]' <"$LIVING_TAG_FILE")"
elif [[ -f "$VERIFY_JSON" ]]; then
  TAG="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1],encoding="utf-8")); print((d.get("release") or "").strip())' "$VERIFY_JSON")"
else
  echo "republish_living_path_c_release: missing living tag / VERIFY.json" >&2
  exit 2
fi
if [[ -z "$TAG" || "$TAG" != *-path-c-bundle ]]; then
  echo "republish_living_path_c_release: invalid living tag '${TAG}'" >&2
  exit 2
fi

if [[ -z "$OUT" ]]; then
  OUT="${TMPDIR:-/tmp}/trial-portable-main-fixes.tgz"
fi

echo "republish_living_path_c_release: packing → ${OUT} (tag=${TAG})"
bash "$ROOT/scripts/pack_portable.sh" "$OUT"

sha256_file() {
  python3 -c 'import hashlib,sys; h=hashlib.sha256();
f=open(sys.argv[1],"rb")
while True:
  b=f.read(1<<20)
  if not b: break
  h.update(b)
print(h.hexdigest())' "$1"
}

pack_bytes="$(wc -c <"$OUT" | tr -d ' ')"
pack_sha="$(sha256_file "$OUT")"
bundle_sha=""
patch_sha=""
[[ -f "$BUNDLE" ]] && bundle_sha="$(sha256_file "$BUNDLE")"
[[ -f "$PATCH" ]] && patch_sha="$(sha256_file "$PATCH")"

echo "republish_living_path_c_release: local pack bytes=${pack_bytes} sha256=${pack_sha}"

# Fetch live release asset metadata (no tokens printed).
REL_JSON="$(gh release view "$TAG" --repo "$REPO" --json tagName,assets 2>/dev/null)" || {
  echo "republish_living_path_c_release: cannot view release ${TAG} on ${REPO}" >&2
  exit 1
}

eval "$(
  REL_JSON="$REL_JSON" python3 - <<'PY'
import json, os, shlex
data = json.loads(os.environ["REL_JSON"])
assets = {a["name"]: a for a in (data.get("assets") or []) if isinstance(a, dict)}
tgz = assets.get("trial-portable-main-fixes.tgz") or {}
bundle = assets.get("path-c-on-hardening.bundle") or {}
patch = assets.get("path-c-on-hardening.patch") or {}

def dig(a):
    d = (a.get("digest") or "")
    if isinstance(d, str) and d.startswith("sha256:"):
        return d.split(":", 1)[1]
    return ""

print("REL_TGZ_BYTES=" + shlex.quote(str(tgz.get("size") or "")))
print("REL_TGZ_SHA=" + shlex.quote(dig(tgz)))
print("REL_BUNDLE_SHA=" + shlex.quote(dig(bundle)))
print("REL_PATCH_SHA=" + shlex.quote(dig(patch)))
PY
)"

echo "republish_living_path_c_release: release tgz bytes=${REL_TGZ_BYTES:-?} sha256=${REL_TGZ_SHA:-?}"

TGZ_NEWER=0
# Prefer byte-growth as the "pack newer" signal. Equal-or-smaller sha churn after a
# successful republish (brief/evidence touch) must not thrash --clobber uploads.
if [[ -z "${REL_TGZ_SHA:-}" && -z "${REL_TGZ_BYTES:-}" ]]; then
  TGZ_NEWER=1
elif [[ -n "${REL_TGZ_BYTES:-}" && "$pack_bytes" -gt "${REL_TGZ_BYTES}" ]]; then
  TGZ_NEWER=1
elif [[ -n "${REL_TGZ_SHA:-}" && "$pack_sha" != "$REL_TGZ_SHA" && -n "${REL_TGZ_BYTES:-}" && "$pack_bytes" -gt "${REL_TGZ_BYTES}" ]]; then
  TGZ_NEWER=1
fi

BUNDLE_NEWER=0
PATCH_NEWER=0
if [[ -n "$bundle_sha" && -n "${REL_BUNDLE_SHA:-}" && "$bundle_sha" != "$REL_BUNDLE_SHA" ]]; then
  BUNDLE_NEWER=1
elif [[ -n "$bundle_sha" && -z "${REL_BUNDLE_SHA:-}" ]]; then
  BUNDLE_NEWER=1
fi
if [[ -n "$patch_sha" && -n "${REL_PATCH_SHA:-}" && "$patch_sha" != "$REL_PATCH_SHA" ]]; then
  PATCH_NEWER=1
elif [[ -n "$patch_sha" && -z "${REL_PATCH_SHA:-}" ]]; then
  PATCH_NEWER=1
fi

NEED_UPLOAD=0
if [[ "$FORCE" -eq 1 || "$TGZ_NEWER" -eq 1 || "$BUNDLE_NEWER" -eq 1 || "$PATCH_NEWER" -eq 1 ]]; then
  NEED_UPLOAD=1
fi

echo "republish_living_path_c_release: tgz_newer=${TGZ_NEWER} bundle_newer=${BUNDLE_NEWER} patch_newer=${PATCH_NEWER} force=${FORCE} need_upload=${NEED_UPLOAD} dry_run=${DRY_RUN}"

if [[ "$NEED_UPLOAD" -eq 0 ]]; then
  echo "republish_living_path_c_release: OK — release assets already current (no upload)."
  exit 0
fi

UPLOAD_ARGS=("$OUT")
[[ -f "$BUNDLE" ]] && UPLOAD_ARGS+=("$BUNDLE")
[[ -f "$PATCH" ]] && UPLOAD_ARGS+=("$PATCH")

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "republish_living_path_c_release: dry-run — would: gh release upload ${TAG} --repo ${REPO} --clobber ${UPLOAD_ARGS[*]}"
  exit 0
fi

echo "republish_living_path_c_release: uploading ${#UPLOAD_ARGS[@]} asset(s) to ${TAG} (--clobber)"
gh release upload "$TAG" "${UPLOAD_ARGS[@]}" --repo "$REPO" --clobber
echo "republish_living_path_c_release: uploaded OK tag=${TAG} pack_sha256=${pack_sha} lemma_closed=false scientific_effect=NONE"
exit 0
