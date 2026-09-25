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
# Batch 276: read upload TAG *after* pack_portable stamps the living pin.
# Pre-276 captured TAG from LIVING_PATH_C_RELEASE_TAG before pack — a stale
# dirty pin (e.g. batch250 from the Batch 268 race class) made `gh release
# upload` target the wrong tag while pack rewrote the pin to VERIFY.release
# (batch241). Pack first → post-pack pin / VERIFY.release → upload.
#
# Batch 279: `gh release upload` names the asset from the local basename.
# `--out /tmp/foo.tgz` therefore created release asset `foo.tgz` and left
# living `trial-portable-main-fixes.tgz` stale (script still printed
# "uploaded OK"). Stage a canonical basename before upload, and verify the
# living release asset size+sha after --clobber (fail closed on mismatch).
#
# Batch 283: byte-growth-only TGZ_NEWER missed tip-only drift. After Batch 282
# tip-sync 3b3860d→7d13a88 (+ pack include grant), living release
# trial-portable-main-fixes.tgz still carried BASE_TIP 3b3860d and omitted
# owner_grant — while refresh --dry-run / assert_path_c_ready stayed green.
# Also compare release-pack BASE_TIP vs local BASE_TIP; tip mismatch ⇒
# tip_stale=1 / need_upload=1 even when pack bytes did not grow.
#
# Batch 286: tip_stale=0 still left living pack without Batch 285 grant fix
# (repositories-array gate). Compare sha256 of critical scripts inside the
# local pack vs the living release pack; any drift ⇒ script_stale=1 /
# need_upload=1 (independent of tip / byte growth). Also grant --check now
# requires isinstance(repositories, list) so null/non-list is not an empty
# install listing.
#
# Batch 288: Batch 287 fixed when_writable_land repositories-list parity with
# probe, but CRITICAL omitted when_writable_land.py — so a when_writable-only
# fix would leave living release script_stale=0 while the lander still shipped
# the pre-287 or [] false-empty install. Include when_writable in CRITICAL.
# Also living release still lacked the 287 probe/refresh bytes (script_stale=1).
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
      sed -n '2,30p' "$0"
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

# Snapshot pre-pack pin for mismatch diagnostics only (Batch 276). Never use as
# upload target — pack_portable validate-before-write may rewrite a dirty pin.
PRE_PACK_TAG=""
if [[ -f "$LIVING_TAG_FILE" ]]; then
  PRE_PACK_TAG="$(tr -d '[:space:]' <"$LIVING_TAG_FILE")"
fi

if [[ -z "$OUT" ]]; then
  OUT="${TMPDIR:-/tmp}/trial-portable-main-fixes.tgz"
fi

echo "republish_living_path_c_release: packing → ${OUT}"
bash "$ROOT/scripts/pack_portable.sh" "$OUT"

# Batch 276: upload target = post-pack living pin (Batch 268 stamp), else VERIFY.
TAG=""
if [[ -f "$LIVING_TAG_FILE" ]]; then
  TAG="$(tr -d '[:space:]' <"$LIVING_TAG_FILE")"
fi
if [[ -z "$TAG" || "$TAG" != *-path-c-bundle ]]; then
  if [[ -f "$VERIFY_JSON" ]]; then
    TAG="$(
      python3 -c '
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
rel = (d.get("release") or "").strip()
if rel.endswith("-path-c-bundle"):
    print(rel)
elif d.get("batch") is not None:
    print("batch{}-path-c-bundle".format(d["batch"]))
' "$VERIFY_JSON"
    )"
  fi
fi
if [[ -z "$TAG" || "$TAG" != *-path-c-bundle ]]; then
  echo "republish_living_path_c_release: invalid living tag '${TAG}' after pack" >&2
  exit 2
fi
if [[ -n "$PRE_PACK_TAG" && "$PRE_PACK_TAG" != "$TAG" ]]; then
  echo "republish_living_path_c_release: note: pre-pack pin '${PRE_PACK_TAG}' → post-pack '${TAG}' (Batch 276 post-pack tag; refuse stale upload target)" >&2
fi
echo "republish_living_path_c_release: upload target tag=${TAG} (post-pack)"

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

# Batch 283: tip-currency gate. Byte-growth alone misses tip-sync packs that stay
# same-or-smaller while BASE_TIP advanced (or release still lacks post-tip fixes).
# Batch 286: tip_match + byte-growth-only still missed critical *script* drift —
# post-285 living release kept tip 7d13a88 (tip_stale=0) while owner_grant lacked
# the repositories-array gate (and repositories null/non-list still false-missing).
# Compare sha256 of critical scripts inside local pack vs release pack.
TIP_STALE=0
SCRIPT_STALE=0
LOCAL_TIP=""
REL_PACK_TIP=""
BASE_TIP_FILE="$ROOT/portable/patches/BASE_TIP.txt"
parse_tip_sha() {
  python3 -c '
import re, sys
text = sys.stdin.read()
m = re.search(r"(?i)\b([0-9a-f]{40})\b", text)
if m:
    print(m.group(1).lower())
    raise SystemExit(0)
m = re.search(r"(?i)(?:^|[=:\s])([0-9a-f]{7,40})(?:\b|$)", text)
if m:
    print(m.group(1).lower()[:40])
    raise SystemExit(0)
raise SystemExit(1)
' 2>/dev/null || true
}
if [[ -f "$BASE_TIP_FILE" ]]; then
  LOCAL_TIP="$(tr -d '\r' <"$BASE_TIP_FILE" | head -n1 | parse_tip_sha || true)"
fi
# Prefer tip stamped inside the pack we just built (post-pack truth).
if [[ -f "$OUT" ]]; then
  PACK_TIP_LINE="$(tar -xOf "$OUT" portable/patches/BASE_TIP.txt 2>/dev/null | head -n1 || true)"
  if [[ -n "$PACK_TIP_LINE" ]]; then
    LOCAL_TIP="$(printf '%s\n' "$PACK_TIP_LINE" | parse_tip_sha || true)"
  fi
fi
TIP_PROBE_DIR=""
REL_PACK_TGZ=""
if [[ -n "$LOCAL_TIP" || -f "$OUT" ]]; then
  TIP_PROBE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/republish-tip-probe.XXXXXX")"
  if gh release download "$TAG" --repo "$REPO" -p 'trial-portable-main-fixes.tgz' -D "$TIP_PROBE_DIR" --clobber >/dev/null 2>&1; then
    REL_PACK_TGZ="$TIP_PROBE_DIR/trial-portable-main-fixes.tgz"
    REL_TIP_LINE="$(tar -xOf "$REL_PACK_TGZ" portable/patches/BASE_TIP.txt 2>/dev/null | head -n1 || true)"
    if [[ -n "$REL_TIP_LINE" ]]; then
      REL_PACK_TIP="$(printf '%s\n' "$REL_TIP_LINE" | parse_tip_sha || true)"
    fi
  else
    echo "republish_living_path_c_release: note: could not download living pack for tip/script probe (network/auth); tip_stale/script_stale check skipped" >&2
  fi
fi
# Normalize to 7-char prefix compare when lengths differ (short vs full SHA).
if [[ -n "$LOCAL_TIP" && -n "$REL_PACK_TIP" ]]; then
  local_cmp="${LOCAL_TIP:0:7}"
  rel_cmp="${REL_PACK_TIP:0:7}"
  if [[ "$local_cmp" != "$rel_cmp" ]]; then
    TIP_STALE=1
  fi
fi
echo "republish_living_path_c_release: local_tip=${LOCAL_TIP:-?} release_pack_tip=${REL_PACK_TIP:-?} tip_stale=${TIP_STALE}"

# Batch 286: critical-script content drift (independent of tip / byte growth).
if [[ -n "${REL_PACK_TGZ:-}" && -f "$OUT" && -f "$REL_PACK_TGZ" ]]; then
  SCRIPT_STALE="$(
    OUT="$OUT" REL_PACK_TGZ="$REL_PACK_TGZ" python3 - <<'PY'
import hashlib, os, tarfile, sys

CRITICAL = (
    "scripts/owner_grant_ai_agent_access.sh",
    # Batch 323: grant --check inventory tip refresh helper (pack+CRITICAL).
    "scripts/refresh_ai_agent_access_inventory.py",
    # Batch 329: print_owner was pack-included but absent from CRITICAL.
    # Needed for (a) INV_BATCH living header stamp (Batch 328) and (b) Batch 324
    # tip-drift≠APPLY_READY Path C line — else living script_stale=0 while those
    # fixes stay off the release (same class as when_writable 288).
    "scripts/print_owner_unblock.sh",
    # Batch 327: wake-comment poster paired with wake-batch322 workflow.
    "scripts/post_batch322_wake_comments.py",
    "scripts/refresh_path_c_bundle.sh",
    "scripts/pack_portable.sh",
    "scripts/probe_main_write.py",
    "scripts/probe_main_write_vectors.py",
    # Batch 288: peer of probe install-list gate — 287 fixed when_writable but
    # CRITICAL could not detect when_writable-only drift.
    "scripts/when_writable_land.py",
    "scripts/republish_living_path_c_release.sh",
)

def member_sha(tgz: str, name: str) -> str:
    try:
        with tarfile.open(tgz, "r:gz") as tf:
            try:
                m = tf.getmember(name)
            except KeyError:
                return ""
            f = tf.extractfile(m)
            if f is None:
                return ""
            h = hashlib.sha256()
            while True:
                chunk = f.read(1 << 16)
                if not chunk:
                    break
                h.update(chunk)
            return h.hexdigest()
    except OSError:
        return ""

local = os.environ["OUT"]
rel = os.environ["REL_PACK_TGZ"]
stale = 0
for name in CRITICAL:
    a = member_sha(local, name)
    b = member_sha(rel, name)
    if a != b:
        stale = 1
        print(f"script_drift {name} local={a[:12] or 'MISSING'} release={b[:12] or 'MISSING'}", file=sys.stderr)
print(stale)
PY
  )"
  SCRIPT_STALE="${SCRIPT_STALE//$'\n'/}"
  SCRIPT_STALE="${SCRIPT_STALE:-0}"
fi
if [[ -n "${TIP_PROBE_DIR:-}" ]]; then
  rm -rf "$TIP_PROBE_DIR"
  TIP_PROBE_DIR=""
fi
echo "republish_living_path_c_release: script_stale=${SCRIPT_STALE}"

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
if [[ "$FORCE" -eq 1 || "$TGZ_NEWER" -eq 1 || "$BUNDLE_NEWER" -eq 1 || "$PATCH_NEWER" -eq 1 || "$TIP_STALE" -eq 1 || "$SCRIPT_STALE" -eq 1 ]]; then
  NEED_UPLOAD=1
fi

echo "republish_living_path_c_release: tgz_newer=${TGZ_NEWER} tip_stale=${TIP_STALE} script_stale=${SCRIPT_STALE} bundle_newer=${BUNDLE_NEWER} patch_newer=${PATCH_NEWER} force=${FORCE} need_upload=${NEED_UPLOAD} dry_run=${DRY_RUN}"

if [[ "$NEED_UPLOAD" -eq 0 ]]; then
  echo "republish_living_path_c_release: OK — release assets already current (no upload)."
  exit 0
fi

# Batch 279: gh release upload uses the local basename as the asset name.
# Always stage the pack as trial-portable-main-fixes.tgz so --out cannot
# create a sibling asset (e.g. batch279-upload.tgz) while leaving the living
# pack stale.
CANON_NAME="trial-portable-main-fixes.tgz"
STAGE_DIR=""
UPLOAD_PACK="$OUT"
if [[ "$(basename -- "$OUT")" != "$CANON_NAME" ]]; then
  STAGE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/republish-canon.XXXXXX")"
  UPLOAD_PACK="$STAGE_DIR/$CANON_NAME"
  cp -f "$OUT" "$UPLOAD_PACK"
  echo "republish_living_path_c_release: staged canonical pack basename ${CANON_NAME} (from $(basename -- "$OUT"))"
fi
cleanup_stage() {
  if [[ -n "$STAGE_DIR" && -d "$STAGE_DIR" ]]; then
    rm -rf "$STAGE_DIR"
  fi
}
trap cleanup_stage EXIT

UPLOAD_ARGS=("$UPLOAD_PACK")
[[ -f "$BUNDLE" ]] && UPLOAD_ARGS+=("$BUNDLE")
[[ -f "$PATCH" ]] && UPLOAD_ARGS+=("$PATCH")

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "republish_living_path_c_release: dry-run — would: gh release upload ${TAG} --repo ${REPO} --clobber ${UPLOAD_ARGS[*]}"
  exit 0
fi

echo "republish_living_path_c_release: uploading ${#UPLOAD_ARGS[@]} asset(s) to ${TAG} (--clobber)"
# Prefer durable dylan device token when present (App/ghs may lack release write).
if [[ -z "${GH_TOKEN:-}" && -z "${GITHUB_TOKEN:-}" && -f /tmp/gh-dylan-auth/access_token ]]; then
  export GH_TOKEN
  GH_TOKEN="$(tr -d '[:space:]' </tmp/gh-dylan-auth/access_token)"
fi
gh release upload "$TAG" "${UPLOAD_ARGS[@]}" --repo "$REPO" --clobber

# Post-upload verify: living asset must match the pack we just uploaded.
REL_AFTER="$(gh release view "$TAG" --repo "$REPO" --json assets 2>/dev/null)" || {
  echo "republish_living_path_c_release: ERROR: cannot re-view release ${TAG} after upload" >&2
  exit 1
}
eval "$(
  REL_JSON="$REL_AFTER" CANON_NAME="$CANON_NAME" python3 - <<'PY'
import json, os, shlex
data = json.loads(os.environ["REL_JSON"])
name = os.environ["CANON_NAME"]
assets = {a["name"]: a for a in (data.get("assets") or []) if isinstance(a, dict)}
tgz = assets.get(name) or {}

def dig(a):
    d = (a.get("digest") or "")
    if isinstance(d, str) and d.startswith("sha256:"):
        return d.split(":", 1)[1]
    return ""

print("REL_AFTER_BYTES=" + shlex.quote(str(tgz.get("size") or "")))
print("REL_AFTER_SHA=" + shlex.quote(dig(tgz)))
print("REL_AFTER_HAS_CANON=" + ("1" if name in assets else "0"))
# Flag accidental basename-leak assets from pre-279 --out misuse.
leaks = sorted(
    n for n in assets
    if n.endswith(".tgz") and n != name
)
print("REL_AFTER_TGZ_LEAKS=" + shlex.quote(",".join(leaks)))
PY
)"

if [[ "${REL_AFTER_HAS_CANON:-0}" != "1" ]]; then
  echo "republish_living_path_c_release: ERROR: living asset ${CANON_NAME} missing after upload" >&2
  exit 1
fi
if [[ "${REL_AFTER_BYTES:-}" != "$pack_bytes" || "${REL_AFTER_SHA:-}" != "$pack_sha" ]]; then
  echo "republish_living_path_c_release: ERROR: post-upload mismatch living bytes=${REL_AFTER_BYTES:-?} sha=${REL_AFTER_SHA:-?} != pack bytes=${pack_bytes} sha=${pack_sha}" >&2
  exit 1
fi
if [[ -n "${REL_AFTER_TGZ_LEAKS:-}" ]]; then
  echo "republish_living_path_c_release: note: extra release .tgz assets present (pre-279 basename leak?): ${REL_AFTER_TGZ_LEAKS}" >&2
fi

echo "republish_living_path_c_release: uploaded OK tag=${TAG} pack_sha256=${pack_sha} living_bytes=${REL_AFTER_BYTES} living_sha256=${REL_AFTER_SHA} lemma_closed=false scientific_effect=NONE"
exit 0
