"""Shape checks for the 2026-09-27 Dropbox gap-audit artifacts.

Repository-intent only: these assert the committed audit is internally
consistent and carries no research-status language. They are not evidence
about Drive, GitHub or any claim.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "portable" / "dropbox_gap_audit_2026-09-27"


def _load(name: str):
    return json.loads((AUDIT / name).read_text(encoding="utf-8"))


def test_artifacts_present():
    for name in (
        "SUMMARY.json",
        "MISSING_FROM_DRIVE.json",
        "MISSING_FROM_GITHUB.json",
        "MISSING_FROM_BOTH.json",
        "REVISION_DIFFERS_DRIVE.json",
        "ZIP_CARRIER_COVERAGE.json",
        "DROPBOX_INVENTORY.tsv",
        "README.md",
    ):
        assert (AUDIT / name).is_file(), name
    assert (ROOT / "docs" / "DROPBOX_GAP_AUDIT_2026-09-27.md").is_file()
    assert (ROOT / "scripts" / "dropbox_gap_audit.py").is_file()


def test_summary_counts_match_lists():
    summary = _load("SUMMARY.json")
    drive = _load("MISSING_FROM_DRIVE.json")
    github = _load("MISSING_FROM_GITHUB.json")
    both = _load("MISSING_FROM_BOTH.json")
    assert len(drive) == summary["drive_match_tally_distinct"]["none"]
    assert len(github) == summary["github_match_tally_distinct"]["none"]
    assert len(both) == summary["missing_from_both_strict_distinct"]
    both_paths = {r["path"] for r in both}
    assert both_paths <= {r["path"] for r in drive}
    assert both_paths <= {r["path"] for r in github}
    assert all(r["drive"] == "none" for r in drive)
    assert all(r["github"] == "none" for r in github)


def test_inventory_tsv_is_distinct_consistent():
    summary = _load("SUMMARY.json")
    with (AUDIT / "DROPBOX_INVENTORY.tsv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == summary["dropbox_files"]
    assert len({r["sha256"] for r in rows}) == summary["dropbox_distinct_sha256"]
    assert all(len(r["sha256"]) == 64 for r in rows)
    on_default = {r["sha256"] for r in rows if r["github_default_branch"] == "true"}
    assert len(on_default) == summary["github_exact_on_default_branch_distinct"]


def test_zip_carrier_coverage_is_bounded():
    for row in _load("ZIP_CARRIER_COVERAGE.json"):
        assert 0 <= row["members_drive_exact"] + row["members_drive_none"] <= row["members"]
        assert 0 <= row["members_github_exact"] + row["members_github_none"] <= row["members"]


def test_no_status_promotion_language():
    doc = (ROOT / "docs" / "DROPBOX_GAP_AUDIT_2026-09-27.md").read_text(encoding="utf-8")
    readme = (AUDIT / "README.md").read_text(encoding="utf-8")
    for text in (doc, readme):
        assert "Scientific effect: NONE" in text
        assert "lemma_closed: true" not in text
        assert "lemma_closed=true" not in text
