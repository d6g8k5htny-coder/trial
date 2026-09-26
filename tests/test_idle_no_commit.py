"""idle_no_commit returns before tracked-file writes."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts" / "idle_no_commit.py"
    spec = importlib.util.spec_from_file_location("idle_no_commit", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pair():
    mod = _load()
    files = {
        rel: (ROOT / rel).read_text(encoding="utf-8") for rel in mod.SOURCE_FILES
    }
    inventory = json.loads((ROOT / mod.INVENTORY).read_text(encoding="utf-8"))
    return mod, files, inventory


def test_unchanged_identity_is_terminal_idle() -> None:
    mod, files, inventory = _pair()
    report = mod.decide(
        current_files=files,
        baseline_files=files,
        current_inventory=inventory,
        baseline_inventory=inventory,
        defect="no defect",
    )
    assert report["action"] == "idle_no_commit"
    assert report["write_tracked_files"] is False
    assert report["lemma_closed"] is False
    assert report["scientific_effect"] == "NONE"
    assert report["reasons"] == []


def test_pulse_stamps_are_not_source_identity() -> None:
    mod, files, inventory = _pair()
    current = dict(files)
    current["scripts/refresh_path_c_bundle.sh"] = current[
        "scripts/refresh_path_c_bundle.sh"
    ].replace("REFRESH_BATCH_TAG:-389", "REFRESH_BATCH_TAG:-390", 1)
    current["scripts/refresh_ai_agent_access_inventory.py"] = current[
        "scripts/refresh_ai_agent_access_inventory.py"
    ].replace('return "389"', 'return "390"', 1)
    current["scripts/post_batch322_wake_comments.py"] = current[
        "scripts/post_batch322_wake_comments.py"
    ].replace('return "389"', 'return "390"', 1)
    current["scripts/print_owner_unblock.sh"] = current[
        "scripts/print_owner_unblock.sh"
    ].replace("=== Batch 389", "=== Batch 390", 1)
    current["scripts/print_owner_unblock.sh"] += (
        '\necho " Batch 390: idle_no_commit pulse"\n'
    )
    current["portable/path-c-applied-bundle/VERIFY.json"] = current[
        "portable/path-c-applied-bundle/VERIFY.json"
    ].replace('"refresh_batch": 389', '"refresh_batch": 390', 1)
    report = mod.decide(
        current_files=current,
        baseline_files=files,
        current_inventory=inventory,
        baseline_inventory=inventory,
        defect="hunt negative",
    )
    assert report["action"] == "idle_no_commit"
    assert report["write_tracked_files"] is False
    assert report["source_identity_unchanged"] is True


def test_real_source_drift_allows_repair() -> None:
    mod, files, inventory = _pair()
    current = dict(files)
    current["scripts/refresh_path_c_bundle.sh"] += "\n# substantive drift marker\n"
    report = mod.decide(
        current_files=current,
        baseline_files=files,
        current_inventory=inventory,
        baseline_inventory=inventory,
    )
    assert report["action"] == "substantive_source_change"
    assert report["write_tracked_files"] is True
    assert "source_identity" in report["reasons"]


def test_base_tip_move_is_source_identity() -> None:
    mod, files, inventory = _pair()
    current = dict(files)
    current["portable/patches/BASE_TIP.txt"] = (
        "chatgpt/drive-github-hardening-20260919 "
        "0000000000000000000000000000000000000000\n"
    )
    report = mod.decide(
        current_files=current,
        baseline_files=files,
        current_inventory=inventory,
        baseline_inventory=inventory,
    )
    assert report["write_tracked_files"] is True
    assert report["source_identity_unchanged"] is False


def test_capability_change_allows_repair() -> None:
    mod, files, inventory = _pair()
    changed = json.loads(json.dumps(inventory))
    changed["durable_sibling_coverage"] = "0/8"
    report = mod.decide(
        current_files=files,
        baseline_files=files,
        current_inventory=changed,
        baseline_inventory=inventory,
    )
    assert report["action"] == "substantive_capability_change"
    assert report["write_tracked_files"] is True


def test_explicit_defect_allows_repair() -> None:
    mod, files, inventory = _pair()
    report = mod.decide(
        current_files=files,
        baseline_files=files,
        current_inventory=inventory,
        baseline_inventory=inventory,
        defect="living_release_missing_grant_gate",
    )
    assert report["action"] == "substantive_defect"
    assert report["write_tracked_files"] is True
    assert report["substantive_defect"] == "living_release_missing_grant_gate"


def test_cli_on_head_is_idle_and_writes_nothing() -> None:
    before = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "idle_no_commit.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    assert before == after
    assert proc.returncode == 0, proc.stderr
    assert "idle_no_commit:" in proc.stderr
    assert "return before tracked-file writes" in proc.stderr
    report = json.loads(proc.stdout)
    assert report["action"] == "idle_no_commit"
    assert report["write_tracked_files"] is False


def test_content_hash_detector_and_schedule_remain() -> None:
    republish = (ROOT / "scripts" / "republish_living_path_c_release.sh").read_text(
        encoding="utf-8"
    )
    assert "hashlib.sha256()" in republish
    assert "if a != b:" in republish
    for name in (
        "scripts/refresh_ai_agent_access_inventory.py",
        "scripts/print_owner_unblock.sh",
        "scripts/post_batch322_wake_comments.py",
        "scripts/refresh_path_c_bundle.sh",
    ):
        assert name in republish
    watch = (ROOT / ".github" / "workflows" / "watch-main-alignment.yml").read_text(
        encoding="utf-8"
    )
    assert 'cron: "0 * * * *"' in watch
