"""Tip-drift tolerance for the Path C gates (engineering only).

Once Path C landed on the hardening branch, BASE_TIP lagging the moving live
tip is tolerated iff every portable patch is already on the live tree. These
tests pin the fail-closed shape of that rule. They encode repository intent
only and must never be cited as scientific evidence.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "path_c_tip_drift_tolerance.sh"
APPLY_ALL = ROOT / "portable" / "patches" / "apply_all.sh"


def _run(args: list[str], **kw) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("PATH_C_STRICT_TIP", None)
    env.update(kw.pop("env", {}))
    return subprocess.run(
        args, capture_output=True, text=True, check=False, cwd=str(ROOT), env=env, **kw
    )


def _verdict(out: str) -> dict[str, str]:
    lines = [ln for ln in out.splitlines() if ln.startswith("path_c_tip_drift: ")]
    assert lines, out
    fields = {}
    for tok in lines[-1].split()[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            fields[k] = v
    return fields


def test_helper_exists_and_help() -> None:
    assert HELPER.is_file()
    assert HELPER.stat().st_mode & 0o111
    p = _run(["bash", str(HELPER), "--help"])
    assert p.returncode == 0, p.stderr
    assert "tolerated" in p.stdout
    assert "already_on_tip=1" in p.stdout
    assert "PATH_C_STRICT_TIP" in p.stdout
    text = HELPER.read_text(encoding="utf-8")
    assert "scientific_effect=NONE" in text
    assert "lemma_closed" in text


def test_apply_all_emits_stack_summary() -> None:
    text = APPLY_ALL.read_text(encoding="utf-8")
    assert "apply_all: summary forward=" in text
    assert "already_on_tip=" in text
    assert "semantic_already_applied" in text
    # Counters must survive the --check worktree (pushd, not a subshell).
    assert 'pushd "$WT"' in text


def test_strict_env_disables_tolerance() -> None:
    p = _run(["bash", str(HELPER), "--workdir", str(ROOT)], env={"PATH_C_STRICT_TIP": "1"})
    assert p.returncode == 1, p.stdout + p.stderr
    v = _verdict(p.stdout)
    assert v["tolerated"] == "0"
    assert v["reason"] == "strict_tip_requested"


def test_not_landed_is_never_tolerated() -> None:
    with tempfile.TemporaryDirectory(prefix="drift-notlanded-") as td:
        verify = Path(td) / "VERIFY.json"
        verify.write_text(json.dumps({"path_c_landed": False}), encoding="utf-8")
        p = _run(["bash", str(HELPER), "--workdir", str(ROOT), "--verify-file", str(verify)])
    assert p.returncode == 1, p.stdout + p.stderr
    v = _verdict(p.stdout)
    assert v["tolerated"] == "0"
    assert v["reason"] == "path_c_not_landed"


def test_non_git_workdir_is_transport_error() -> None:
    with tempfile.TemporaryDirectory(prefix="drift-nongit-") as td:
        p = _run(["bash", str(HELPER), "--workdir", td])
    assert p.returncode == 2, p.stdout + p.stderr
    v = _verdict(p.stdout)
    assert v["tolerated"] == "0"
    assert v["reason"] == "workdir_not_git"


def test_non_hardening_tree_fails_closed() -> None:
    """apply_all refuses a tree without the hardening shape → not tolerated."""
    with tempfile.TemporaryDirectory(prefix="drift-shape-") as td:
        subprocess.run(["git", "init", "-q", td], check=True)
        (Path(td) / "README.md").write_text("not hardening\n", encoding="utf-8")
        subprocess.run(["git", "-C", td, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
            check=True,
        )
        p = _run(["bash", str(HELPER), "--workdir", td])
    assert p.returncode == 1, p.stdout + p.stderr
    v = _verdict(p.stdout)
    assert v["tolerated"] == "0"
    assert v["reason"] == "apply_all_check_failed"


def test_gates_consult_the_helper() -> None:
    """Every SHA-equality gate must consult the helper before failing on drift."""
    for rel in (
        "scripts/assert_path_c_ready.sh",
        "scripts/owner_open_path_c_pr.sh",
        "scripts/owner_land_path_c.sh",
        "scripts/refresh_path_c_bundle.sh",
        ".github/workflows/ci.yml",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "path_c_tip_drift_tolerance.sh" in text, rel
    dry = (ROOT / "scripts" / "path_c_dry_run.py").read_text(encoding="utf-8")
    assert "tip_drift_tolerated" in dry
    assert "apply_all_already_on_tip" in dry
    assert "PATH_C_STRICT_TIP" in dry
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    # Both clone-based gates pass their own checkout; hard failure retained.
    assert "--workdir main-work" in ci
    assert "--workdir main-bundle" in ci
    assert ci.count("::error::tip-drift: live hardening SHA") >= 2


def test_live_tip_verdict_is_consistent() -> None:
    """Live: on the current hardening tip the helper either tolerates (landed
    stack fully on tip) or fails closed with a known reason. Skipped on transport."""
    p = _run(["bash", str(HELPER)], timeout=300)
    if p.returncode == 2:
        return
    v = _verdict(p.stdout)
    assert v["tolerated"] in ("0", "1")
    if v["tolerated"] == "1":
        assert p.returncode == 0
        assert v["reason"] == "landed_stack_already_on_live_tip"
        assert v["forward"] == "0"
        assert int(v["already_applied"]) > 0
    else:
        assert p.returncode == 1
        assert v["reason"] in {
            "path_c_not_landed",
            "stack_not_fully_on_tip",
            "apply_all_check_failed",
        }
    base = (ROOT / "portable" / "patches" / "BASE_TIP.txt").read_text(encoding="utf-8")
    assert v["base_tip"] in base
    assert v["scientific_effect"] == "NONE"


if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q", __file__]))
