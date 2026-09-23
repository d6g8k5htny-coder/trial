#!/usr/bin/env python3
"""Path B dry-run certainty: clone default main, git am Option-B, local auditor.

Emits one JSON dashboard so agents/owners can trust would-align *before* any
push. Does not push, create refs, or open PRs.

Exit codes:
  0 — git am OK (or already post-Option-B) AND local auditor ALIGNED (would-align)
  1 — patch apply or auditor failed (would NOT align)
  2 — transport / missing inputs

Scientific effect: NONE.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = "d6g8k5htny-coder/main"
DEFAULT_BRANCH = "main"


def _trial_root() -> Path:
    env = os.environ.get("TRIAL_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workdir",
        default="",
        help="Reuse an existing empty-ish dir; default is a temp dir cleaned on exit",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Do not delete the workdir (for inspection)",
    )
    parser.add_argument(
        "--json-out",
        default="",
        help="Optional path to write the certainty JSON (also printed to stdout)",
    )
    args = parser.parse_args()

    trial = _trial_root()
    patch = trial / "portable/main-default-branch/0001-option-b-default-branch-notice.patch"
    audit_local = trial / "scripts/audit_local_tree.py"

    report: dict = {
        "probe": "path_b_dry_run_certainty",
        "repo": REPO,
        "scientific_effect": "NONE",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trial_root": str(trial),
        "patch": str(patch),
        "state": "UNKNOWN",
        "would_align": False,
        "git_am_exit": None,
        "git_am_skipped_already_post_option_b": False,
        "default_tip_sha": None,
        "local_auditor": None,
        "local_auditor_exit": None,
        "readme_head": [],
    }

    if not patch.is_file():
        report["state"] = "MISSING_PATCH"
        report["error"] = f"missing Option-B patch: {patch}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2
    if not audit_local.is_file():
        report["state"] = "MISSING_AUDITOR"
        report["error"] = f"missing {audit_local}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    cleanup = False
    if args.workdir:
        work = Path(args.workdir).resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        work = Path(tempfile.mkdtemp(prefix="path-b-dry-run."))
        cleanup = not args.keep

    clone_dir = work / "main"
    try:
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        clone = _run(
            [
                "git",
                "clone",
                "--depth",
                "20",
                f"https://github.com/{REPO}.git",
                str(clone_dir),
            ]
        )
        if clone.returncode != 0:
            report["state"] = "CLONE_FAILED"
            report["error"] = (clone.stderr or clone.stdout or "clone failed")[-500:]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2

        tip = _run(["git", "rev-parse", "HEAD"], cwd=clone_dir)
        report["default_tip_sha"] = tip.stdout.strip()

        _run(["git", "checkout", "-B", "cursor/option-b-dry-run"], cwd=clone_dir)

        readme = clone_dir / "README.md"
        readme_text = readme.read_text(encoding="utf-8", errors="replace") if readme.is_file() else ""
        # Require the Option-B *notice* itself — not Dylan's honest program-map
        # (which still contains complexity-physics-framework in withdrawal prose
        # and previously false-skipped git am via a loose drive-github-hardening match).
        already = (
            "q0 Research Program" in readme_text
            and ("SIDE24" in readme_text or "default branch notice" in readme_text)
            and "complexity-physics-framework" not in readme_text
            and "Multiscale Retrodiction Complexity" not in readme_text
        )

        if already:
            report["git_am_skipped_already_post_option_b"] = True
            report["git_am_exit"] = 0
        else:
            am = _run(["git", "am", str(patch)], cwd=clone_dir)
            report["git_am_exit"] = am.returncode
            if am.returncode != 0:
                _run(["git", "am", "--abort"], cwd=clone_dir)
                report["state"] = "AM_FAILED"
                report["error"] = (am.stderr or am.stdout or "git am failed")[-500:]
                report["would_align"] = False
                print(json.dumps(report, indent=2, sort_keys=True))
                if args.json_out:
                    Path(args.json_out).write_text(
                        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                    )
                return 1

        readme_text = readme.read_text(encoding="utf-8", errors="replace") if readme.is_file() else ""
        report["readme_head"] = readme_text.splitlines()[:8]

        audit = _run([sys.executable, str(audit_local), str(clone_dir)])
        report["local_auditor_exit"] = audit.returncode
        auditor_payload: dict = {}
        if audit.stdout.strip():
            text = audit.stdout.strip()
            try:
                # audit_local_tree prints pretty multi-line JSON on stdout
                auditor_payload = json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                if start >= 0:
                    try:
                        auditor_payload = json.loads(text[start:])
                    except json.JSONDecodeError:
                        auditor_payload = {"raw_stdout": text[-1000:]}
                else:
                    auditor_payload = {"raw_stdout": text[-1000:]}
        report["local_auditor"] = auditor_payload
        report["local_auditor_stderr"] = audit.stderr.strip()[-300:] if audit.stderr else ""

        would = audit.returncode == 0 and auditor_payload.get("state") == "ALIGNED"
        report["would_align"] = would
        report["state"] = "WOULD_ALIGN" if would else "WOULD_NOT_ALIGN"

        text = json.dumps(report, indent=2, sort_keys=True)
        print(text)
        if args.json_out:
            Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        return 0 if would else 1
    finally:
        if cleanup and work.exists():
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
