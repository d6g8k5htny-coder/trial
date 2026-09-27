#!/usr/bin/env python3
"""Compare a Dropbox folder export against (a) the Google Drive inventory
snapshot + deltas carried on d6g8k5htny-coder/main hardening branch and
(b) every branch of all 8 d6g8k5htny-coder repos.

Batch 791 (2026-09-27). Scientific effect: NONE. Presence or absence of a
file is not a claim status; nothing here flips lemma_closed / prizes / premises.

Usage (defaults reproduce portable/dropbox_gap_audit_2026-09-27/):

  # 1. Dropbox shared-folder link resolves to a zip; extract it
  curl -sL -o /tmp/dropbox_folder.zip "<dropbox scl/fo link>&dl=1"
  python3 -c "import zipfile;zipfile.ZipFile('/tmp/dropbox_folder.zip').extractall('/tmp/dropbox')"
  # 2. Drive reference = 2026-09-17 export on main hardening branch (no Drive API creds needed)
  git clone --filter=blob:none https://github.com/d6g8k5htny-coder/main /tmp/gh/main
  H=origin/chatgpt/drive-github-hardening-20260919
  mkdir -p /tmp/drive/drive/source_map
  for f in inventory.jsonl source_map/Files.csv source_map/Archive_Members.csv source_map/Payloads.csv; do
    git -C /tmp/gh/main show $H:drive/$f > /tmp/drive/drive/$f; done
  # 3. other repos (blobless is enough: only tree blob-sha1s are compared)
  for r in google-drive governance- Math- meta-framework query- sandbox; do
    git clone --filter=blob:none https://github.com/d6g8k5htny-coder/$r /tmp/gh/$r; done
  # 4. run
  python3 scripts/dropbox_gap_audit.py --out /tmp/audit/out

Match classes (strongest first):
  drive : exact_sha256 | name_and_bytes | name_only | stem_only | none
  github: exact_blob (git blob sha1, any branch) | name_only | stem_only | none
Only `none` is reported as missing; name/stem-only rows are listed separately
as "revision differs / unverified" because native Google Docs carry no digest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--dropbox", default="/tmp/dropbox", help="extracted Dropbox folder")
_ap.add_argument("--drive", default="/tmp/drive/drive", help="dir holding inventory.jsonl + source_map/*.csv")
_ap.add_argument("--repos", default="/tmp/gh", help="dir holding clones of the 7 non-trial owner repos")
_ap.add_argument("--trial", default=str(Path(__file__).resolve().parents[1]), help="trial checkout")
_ap.add_argument("--hardening-ref", default="origin/chatgpt/drive-github-hardening-20260919")
_ap.add_argument("--out", default="/tmp/audit/out")
_args = _ap.parse_args()

DROPBOX = Path(_args.dropbox)
DRIVE = Path(_args.drive)
MAIN_CLONE = Path(_args.repos) / "main"
HARDENING = _args.hardening_ref
REPOS = {
    "main": Path(_args.repos) / "main",
    "google-drive": Path(_args.repos) / "google-drive",
    "governance-": Path(_args.repos) / "governance-",
    "Math-": Path(_args.repos) / "Math-",
    "meta-framework": Path(_args.repos) / "meta-framework",
    "query-": Path(_args.repos) / "query-",
    "sandbox": Path(_args.repos) / "sandbox",
    "trial": Path(_args.trial),
}
OUT = Path(_args.out)
OUT.mkdir(parents=True, exist_ok=True)

csv.field_size_limit(1 << 30)


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = os.path.basename(s)
    s = re.sub(r"\s\(\d+\)(?=\.[^.]+$|$)", "", s)  # "name (1).ext" -> "name.ext"
    s = s.lower().strip()
    return s


def stem(s: str) -> str:
    s = norm_name(s)
    for ext in (".export.txt", ".txt", ".md", ".docx", ".pdf", ".json", ".jsonl",
                ".csv", ".tsv", ".zip", ".py", ".sh", ".log", ".out", ".err",
                ".png", ".lean", ".gs", ".xml", ".toml", ".pkl", ".dmg", ".sha256"):
        if s.endswith(ext):
            s = s[: -len(ext)]
            break
    return s.strip()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_sha1(b: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- Dropbox
print("[1/4] hashing Dropbox export ...", file=sys.stderr)
dbx_files: list[dict] = []
dbx_members: list[dict] = []
for p in sorted(DROPBOX.rglob("*")):
    if p.is_dir():
        continue
    rel = str(p.relative_to(DROPBOX))
    b = p.read_bytes()
    rec = {
        "path": rel,
        "bytes": len(b),
        "sha256": sha256_bytes(b),
        "blob_sha1": git_blob_sha1(b),
        "name": norm_name(rel),
        "stem": stem(rel),
    }
    dbx_files.append(rec)
    if p.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                for zi in z.infolist():
                    if zi.is_dir():
                        continue
                    mb = z.read(zi)
                    dbx_members.append(
                        {
                            "carrier": rel,
                            "member": zi.filename,
                            "bytes": len(mb),
                            "sha256": sha256_bytes(mb),
                            "blob_sha1": git_blob_sha1(mb),
                            "name": norm_name(zi.filename),
                            "stem": stem(zi.filename),
                        }
                    )
        except zipfile.BadZipFile:
            rec["zip_error"] = "BadZipFile"

print(f"   files={len(dbx_files)} zip_members={len(dbx_members)}", file=sys.stderr)

# ---------------------------------------------------------------- Drive
print("[2/4] loading Drive inventory + archive members + deltas ...", file=sys.stderr)
drive_sha: dict[str, list[str]] = defaultdict(list)      # sha256 -> [where]
drive_names: dict[str, list[dict]] = defaultdict(list)   # norm name -> [item]
drive_stems: dict[str, list[dict]] = defaultdict(list)
drive_native_count = 0
drive_items = 0

with (DRIVE / "inventory.jsonl").open(encoding="utf-8") as fh:
    for line in fh:
        it = json.loads(line)
        if it.get("mimeType") == "application/vnd.google-apps.folder":
            continue
        drive_items += 1
        if it.get("mimeType", "").startswith("application/vnd.google-apps."):
            drive_native_count += 1
        entry = {
            "id": it["id"],
            "title": it["title"],
            "path": it["path"],
            "bytes": it.get("bytes"),
            "sha256": it.get("sha256"),
            "mime": it.get("mimeType"),
            "src": "inventory_2026-09-17",
        }
        if it.get("sha256"):
            drive_sha[it["sha256"]].append(f"drive:{it['path']}")
        drive_names[norm_name(it["title"])].append(entry)
        drive_stems[stem(it["title"])].append(entry)

with (DRIVE / "source_map" / "Archive_Members.csv").open(encoding="utf-8", newline="") as fh:
    for row in csv.DictReader(fh):
        d = (row.get("Payload SHA-256") or "").strip()
        if d:
            drive_sha[d].append(f"drive-archive:{row['Carrier title']}::{row['Member path']}")
        entry = {
            "title": row["Member path"],
            "path": f"{row['Carrier title']}::{row['Member path']}",
            "bytes": int(row["Bytes"]) if row.get("Bytes", "").isdigit() else None,
            "sha256": d or None,
            "src": "archive_members",
        }
        drive_names[norm_name(row["Member path"])].append(entry)
        drive_stems[stem(row["Member path"])].append(entry)

with (DRIVE / "source_map" / "Payloads.csv").open(encoding="utf-8", newline="") as fh:
    for row in csv.DictReader(fh):
        d = (row.get("SHA-256") or "").strip()
        if d:
            drive_sha[d].append(f"drive-payload:{row['Source name']}")

# deltas and mirrors manifests on the hardening branch
delta_rows = 0
ls_raw = subprocess.run(
    ["git", "-C", str(MAIN_CLONE), "ls-tree", "-r", "-z", HARDENING],
    capture_output=True, check=True,
).stdout.split(b"\0")
manifest_paths: list[str] = []
manifest_blobs: dict[str, str] = {}
for ent in ls_raw:
    if not ent:
        continue
    meta, _, fpath = ent.partition(b"\t")
    p = fpath.decode("utf-8", "replace")
    if p.startswith("drive/") and (p.endswith("_MANIFEST.jsonl") or p.endswith("CHANGED_SINCE_SNAPSHOT.jsonl")):
        manifest_paths.append(p)
        manifest_blobs[p] = meta.split()[2].decode()
# prefetch all manifest blobs in one batch (blobless clone)
subprocess.run(
    ["git", "-C", str(MAIN_CLONE), "cat-file", "--batch-check"],
    input="\n".join(manifest_blobs.values()).encode(), capture_output=True,
)
for mp in manifest_paths:
    blob = subprocess.run(
        ["git", "-C", str(MAIN_CLONE), "cat-file", "-p", manifest_blobs[mp]],
        capture_output=True, check=True,
    ).stdout.decode("utf-8", "replace")
    for line in blob.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            it = json.loads(line)
        except json.JSONDecodeError:
            continue
        delta_rows += 1
        title = it.get("title") or it.get("name") or ""
        d = it.get("sha256") or it.get("payload_sha256")
        entry = {
            "id": it.get("id"),
            "title": title,
            "path": it.get("path") or mp,
            "bytes": it.get("bytes_drive") or it.get("bytes"),
            "sha256": d,
            "src": f"manifest:{mp}",
        }
        if d:
            drive_sha[d].append(f"drive-delta:{mp}::{title}")
        if title:
            drive_names[norm_name(title)].append(entry)
            drive_stems[stem(title)].append(entry)

print(
    f"   drive_items={drive_items} native={drive_native_count} "
    f"sha256_keys={len(drive_sha)} manifest_rows={delta_rows} manifests={len(manifest_paths)}",
    file=sys.stderr,
)

# ---------------------------------------------------------------- GitHub
print("[3/4] indexing GitHub trees (all branches, 8 repos) ...", file=sys.stderr)
gh_blob: dict[str, set[str]] = defaultdict(set)     # blob sha1 -> {"repo:branch:path"}
gh_blob_default: dict[str, set[str]] = defaultdict(set)  # same, default branches only
gh_names: dict[str, set[str]] = defaultdict(set)
gh_stems: dict[str, set[str]] = defaultdict(set)
gh_stats = {}
for repo, path in REPOS.items():
    refs = subprocess.run(
        ["git", "-C", str(path), "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/", "refs/heads/"],
        capture_output=True, check=True,
    ).stdout.decode().split()
    refs = [r for r in refs if not r.endswith("/HEAD")]
    seen_paths = 0
    for ref in refs:
        out = subprocess.run(
            ["git", "-C", str(path), "ls-tree", "-r", "-z", ref],
            capture_output=True, check=True,
        ).stdout.decode("utf-8", "surrogateescape")
        for ent in out.split("\0"):
            if not ent:
                continue
            meta, _, fpath = ent.partition("\t")
            parts = meta.split()
            if len(parts) < 3 or parts[1] != "blob":
                continue
            sha1 = parts[2]
            loc = f"{repo}@{ref.replace('origin/', '')}:{fpath}"
            gh_blob[sha1].add(loc)
            if ref in ("origin/main", "main"):
                gh_blob_default[sha1].add(loc)
            gh_names[norm_name(fpath)].add(loc)
            gh_stems[stem(fpath)].add(loc)
            seen_paths += 1
    gh_stats[repo] = {"refs": len(refs), "tree_entries": seen_paths}
print(f"   blobs={len(gh_blob)} repos={gh_stats}", file=sys.stderr)


# ---------------------------------------------------------------- classify
def classify_drive(rec: dict) -> tuple[str, list[str]]:
    if rec["sha256"] in drive_sha:
        return "exact_sha256", sorted(set(drive_sha[rec["sha256"]]))[:5]
    cands = drive_names.get(rec["name"], [])
    same_bytes = [c for c in cands if c.get("bytes") == rec["bytes"]]
    if same_bytes:
        return "name_and_bytes", [c["path"] for c in same_bytes][:5]
    if cands:
        return "name_only", [c["path"] for c in cands][:5]
    scands = drive_stems.get(rec["stem"], [])
    if scands:
        return "stem_only", [c["path"] for c in scands][:5]
    return "none", []


def classify_github(rec: dict) -> tuple[str, list[str]]:
    if rec["blob_sha1"] in gh_blob:
        return "exact_blob", sorted(gh_blob[rec["blob_sha1"]])[:5]
    if rec["name"] in gh_names:
        return "name_only", sorted(gh_names[rec["name"]])[:5]
    if rec["stem"] in gh_stems:
        return "stem_only", sorted(gh_stems[rec["stem"]])[:5]
    return "none", []


print("[4/4] classifying ...", file=sys.stderr)
for rec in dbx_files + dbx_members:
    rec["drive"], rec["drive_where"] = classify_drive(rec)
    rec["github"], rec["github_where"] = classify_github(rec)
    rec["github_default_branch"] = rec["blob_sha1"] in gh_blob_default
    rec["github_default_where"] = sorted(gh_blob_default.get(rec["blob_sha1"], ()))[:3]

# Dropbox-internal duplicates: same sha256 at multiple paths (e.g. "(1)" copies)
by_sha: dict[str, list[str]] = defaultdict(list)
for rec in dbx_files:
    by_sha[rec["sha256"]].append(rec["path"])
distinct = len(by_sha)


def tally(records, key):
    t = defaultdict(int)
    for r in records:
        t[r[key]] += 1
    return dict(sorted(t.items()))


def top_dir(p: str) -> str:
    return p.split("/")[0] if "/" in p else "(root)"


def per_dir(records, key, wanted):
    t = defaultdict(lambda: [0, 0])
    for r in records:
        d = top_dir(r["path"])
        t[d][1] += 1
        if r[key] in wanted:
            t[d][0] += 1
    return {d: {"missing": v[0], "total": v[1]} for d, v in sorted(t.items())}


MISSING = {"none", "stem_only", "name_only"}
STRICT_MISSING = {"none"}

# Distinct-content view: collapse Dropbox duplicates so counts are honest.
distinct_recs = {}
for rec in dbx_files:
    distinct_recs.setdefault(rec["sha256"], rec)
distinct_list = list(distinct_recs.values())

summary = {
    "dropbox_files": len(dbx_files),
    "dropbox_distinct_sha256": distinct,
    "dropbox_bytes": sum(r["bytes"] for r in dbx_files),
    "dropbox_zip_members": len(dbx_members),
    "drive_reference": {
        "inventory": "main@chatgpt/drive-github-hardening-20260919:drive/inventory.jsonl (2026-09-17 export)",
        "archive_members_csv": "drive/source_map/Archive_Members.csv",
        "payloads_csv": "drive/source_map/Payloads.csv",
        "delta_and_mirror_manifests": len(manifest_paths),
        "drive_items_non_folder": drive_items,
        "drive_native_docs_no_digest": drive_native_count,
        "distinct_sha256_known": len(drive_sha),
        "caveat": "No Drive API credentials in this pod; live Drive (post 2026-09-20) may differ. Native Google Docs/Sheets carry no SHA-256 so they match by name only.",
    },
    "github_reference": gh_stats,
    "drive_match_tally_all_files": tally(dbx_files, "drive"),
    "drive_match_tally_distinct": tally(distinct_list, "drive"),
    "github_match_tally_all_files": tally(dbx_files, "github"),
    "github_match_tally_distinct": tally(distinct_list, "github"),
    "github_exact_on_default_branch_distinct": sum(1 for r in distinct_list if r["github_default_branch"]),
    "github_exact_only_on_non_default_branches_distinct": sum(
        1 for r in distinct_list if r["github"] == "exact_blob" and not r["github_default_branch"]
    ),
    "zip_members_drive_tally": tally(dbx_members, "drive"),
    "zip_members_github_tally": tally(dbx_members, "github"),
    "missing_from_drive_strict_by_top_dir": per_dir(distinct_list, "drive", STRICT_MISSING),
    "missing_from_github_strict_by_top_dir": per_dir(distinct_list, "github", STRICT_MISSING),
    "missing_from_both_strict_distinct": sum(
        1 for r in distinct_list if r["drive"] == "none" and r["github"] == "none"
    ),
    "missing_from_both_loose_distinct": sum(
        1 for r in distinct_list if r["drive"] in MISSING and r["github"] in MISSING
    ),
}

(OUT / "dropbox_inventory.jsonl").write_text(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dbx_files), encoding="utf-8"
)
(OUT / "dropbox_zip_members.jsonl").write_text(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dbx_members), encoding="utf-8"
)
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

missing_drive = [r for r in distinct_list if r["drive"] == "none"]
missing_github = [r for r in distinct_list if r["github"] == "none"]
missing_both = [r for r in distinct_list if r["drive"] == "none" and r["github"] == "none"]
weak_drive = [r for r in distinct_list if r["drive"] in ("name_only", "stem_only")]
weak_github = [r for r in distinct_list if r["github"] in ("name_only", "stem_only")]


def slim(r):
    out = {k: r[k] for k in ("path", "bytes", "sha256", "drive", "drive_where", "github", "github_where")}
    dups = [p for p in by_sha[r["sha256"]] if p != r["path"]]
    if dups:
        out["dropbox_duplicate_paths"] = dups
    return out


# zip carrier coverage (member-level), so a "missing" carrier is not over-read
carriers: dict[str, list[dict]] = defaultdict(list)
for m in dbx_members:
    carriers[m["carrier"]].append(m)
carrier_rows = []
for cpath, ms in sorted(carriers.items()):
    car = next(r for r in dbx_files if r["path"] == cpath)
    carrier_rows.append(
        {
            "carrier": cpath,
            "carrier_bytes": car["bytes"],
            "carrier_sha256": car["sha256"],
            "carrier_drive": car["drive"],
            "carrier_github": car["github"],
            "members": len(ms),
            "members_drive_exact": sum(1 for m in ms if m["drive"] == "exact_sha256"),
            "members_drive_none": sum(1 for m in ms if m["drive"] == "none"),
            "members_github_exact": sum(1 for m in ms if m["github"] == "exact_blob"),
            "members_github_none": sum(1 for m in ms if m["github"] == "none"),
        }
    )
(OUT / "zip_carrier_coverage.json").write_text(json.dumps(carrier_rows, indent=1, ensure_ascii=False), encoding="utf-8")
summary["zip_carriers"] = len(carrier_rows)


(OUT / "missing_from_drive.json").write_text(
    json.dumps([slim(r) for r in missing_drive], indent=1, ensure_ascii=False), encoding="utf-8")
(OUT / "missing_from_github.json").write_text(
    json.dumps([slim(r) for r in missing_github], indent=1, ensure_ascii=False), encoding="utf-8")
(OUT / "missing_from_both.json").write_text(
    json.dumps([slim(r) for r in missing_both], indent=1, ensure_ascii=False), encoding="utf-8")
(OUT / "weak_name_only_matches.json").write_text(
    json.dumps({"drive": [slim(r) for r in weak_drive], "github": [slim(r) for r in weak_github]},
               indent=1, ensure_ascii=False), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
