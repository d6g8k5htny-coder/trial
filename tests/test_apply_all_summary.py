"""apply_all.sh: generic semantic already-applied check + machine-readable summary.

A landed portable patch whose surrounding context later drifted on the
hardening tip (0017 after main #140: ``survey -> full_survey``) fails both
forward and reverse ``git apply --check`` although every hunk is on the tree.
``semantic_already_applied()`` recognises that case generically, and
``apply_all: summary ... already_on_tip=0|1`` tells callers whether the whole
stack is on the tree without parsing echoes.

Repository-intent only. Not evidence about any claim; scientific effect NONE.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLY_ALL = ROOT / "portable" / "patches" / "apply_all.sh"


def _extract_semantic_check() -> str:
    """Pull the python body of semantic_already_applied() out of the bash file."""
    text = APPLY_ALL.read_text(encoding="utf-8")
    m = re.search(r"semantic_already_applied\(\) \{\n  python3 - \"\$1\" <<'PY'\n(.*?)\nPY\n\}", text, re.S)
    assert m, "semantic_already_applied() heredoc not found"
    return m.group(1)


def _semantic(patch_text: str, tree: dict[str, str]) -> int:
    """Run the extracted check against a temp tree; return its exit code."""
    body = _extract_semantic_check()
    with tempfile.TemporaryDirectory(prefix="apply-all-sem-") as td:
        root = Path(td)
        for rel, content in tree.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        patch = root / "x.patch"
        patch.write_text(patch_text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-", str(patch)],
            input=body,
            capture_output=True,
            text=True,
            cwd=str(root),
            check=False,
        )
        return proc.returncode


PATCH = """\
diff --git a/pkg/mod.py b/pkg/mod.py
--- a/pkg/mod.py
+++ b/pkg/mod.py
@@ -1,4 +1,5 @@
 import os
-data = open(path).read()
+with open(path, encoding="utf-8") as fh:
+    data = fh.read()
 print(data)
"""


def test_script_has_summary_and_generic_check() -> None:
    text = APPLY_ALL.read_text(encoding="utf-8")
    assert "semantic_already_applied()" in text
    assert 'semantic_already_applied "$p"' in text
    assert "apply_all: summary forward=" in text
    assert "already_on_tip=" in text
    # Counters must survive the --check worktree (pushd, not a subshell).
    assert 'pushd "$WT"' in text
    # No per-patch grep for 0017 any more; the generic fallback covers it.
    assert '"$bn" == 0017-*' not in text
    assert subprocess.run(["bash", "-n", str(APPLY_ALL)], check=False).returncode == 0


def test_semantic_check_accepts_applied_with_drifted_context() -> None:
    tree = {
        "pkg/mod.py": (
            "import os\n"
            "# context drifted after landing\n"
            "with open(path, encoding=\"utf-8\") as fh:\n"
            "    data = fh.read()\n"
            "print(data)  # also drifted\n"
        )
    }
    assert _semantic(PATCH, tree) == 0


def test_semantic_check_rejects_unapplied_tree() -> None:
    tree = {"pkg/mod.py": "import os\ndata = open(path).read()\nprint(data)\n"}
    assert _semantic(PATCH, tree) == 1


def test_semantic_check_rejects_partial_apply() -> None:
    # '+' lines present but the removed line is still there → not applied.
    tree = {
        "pkg/mod.py": (
            "import os\n"
            "data = open(path).read()\n"
            "with open(path, encoding=\"utf-8\") as fh:\n"
            "    data = fh.read()\n"
            "print(data)\n"
        )
    }
    assert _semantic(PATCH, tree) == 1


def test_semantic_check_rejects_missing_target_and_create_delete() -> None:
    assert _semantic(PATCH, {}) == 1
    create = PATCH.replace("--- a/pkg/mod.py", "--- /dev/null")
    assert _semantic(create, {"pkg/mod.py": "x\n"}) == 1
    delete = PATCH.replace("+++ b/pkg/mod.py", "+++ /dev/null")
    assert _semantic(delete, {"pkg/mod.py": "x\n"}) == 1


def test_check_refuses_non_hardening_tree_before_summary() -> None:
    with tempfile.TemporaryDirectory(prefix="apply-all-shape-") as td:
        subprocess.run(["git", "init", "-q", td], check=True)
        (Path(td) / "README.md").write_text("not hardening\n", encoding="utf-8")
        subprocess.run(["git", "-C", td, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
            check=True,
        )
        proc = subprocess.run(
            ["bash", str(APPLY_ALL), "--check"], cwd=td, capture_output=True, text=True, check=False
        )
    assert proc.returncode == 2
    assert "apply_all: summary" not in proc.stdout


def test_live_tip_summary_is_consistent() -> None:
    """Live: on the current hardening tip the summary must be self-consistent
    (already_on_tip=1 iff forward=0 and already_applied>0). Skipped on transport."""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    with tempfile.TemporaryDirectory(prefix="apply-all-live-") as td:
        clone = subprocess.run(
            [
                "git", "clone", "-q", "--depth", "1", "--branch",
                "chatgpt/drive-github-hardening-20260919",
                "https://github.com/d6g8k5htny-coder/main.git", td,
            ],
            capture_output=True, text=True, env=env, check=False, timeout=300,
        )
        if clone.returncode != 0:
            return
        proc = subprocess.run(
            ["bash", str(APPLY_ALL), "--check"], cwd=td, capture_output=True, text=True, check=False, timeout=300
        )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    m = re.search(
        r"^apply_all: summary forward=(\d+) already_applied=(\d+) skipped=(\d+) already_on_tip=([01])",
        proc.stdout, re.M,
    )
    assert m, proc.stdout
    forward, already, _skipped, on_tip = (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4))
    assert (on_tip == "1") == (forward == 0 and already > 0)
    assert "Check OK" in proc.stdout
