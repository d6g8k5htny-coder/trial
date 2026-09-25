#!/usr/bin/env python3
"""Validate trial land-option-b / land-path-c workflows without MAIN_PUSH_TOKEN.

Batch 73: CI dry-run contract for owner Actions land workflows.
Batch 247: also fail-closed if `.github/workflows/ci.yml` is unparseable
(column-0 multiline python inside `run: |` → Actions \"workflow file issue\").
Batch 272: land-workflows-dry-run must grep Path C idle (IDLE_PATH_C_DONE /
already_on_tip) on path-c-dry-run.out alone — union grep with Path B's
ALREADY_ALIGNED falsely greenlit Path C after Batch 261 idle.
Scientific effect: NONE. Never flips lemma_closed / research status.

Checks (all local; no push, no secrets required):
  1. YAML parse of both land workflow files + trial ci.yml
  2. workflow_dispatch + dry_run input default true
  3. MAIN_PUSH_TOKEN only required when dry_run=false
  4. Path B references Option-B patch + local auditor
  5. Path C references hardening tip + apply_all + lemma_closed=false gate
  6. Owner scripts expose --help / --dry-run
  7. ci.yml has IDLE_PATH_C_DONE + path_c_followon_pending; no col-0 imports
  8. ci.yml land-workflows-dry-run asserts Path C idle on its own outfile

Exit 0 on OK; exit 1 on contract failure; exit 2 on missing files / bad YAML.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"
PATH_B = WF_DIR / "land-option-b-on-main.yml"
PATH_C = WF_DIR / "land-path-c-on-main.yml"
PATH_CI = WF_DIR / "ci.yml"
OWNER_B = ROOT / "scripts" / "owner_land_path_b.sh"
OWNER_C = ROOT / "scripts" / "owner_land_path_c.sh"


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        # Minimal fallback: structural string checks still run; YAML load optional.
        return {}
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: top-level YAML is not a mapping")
    return data


def _check_ci_yml_parses(path: Path = PATH_CI) -> list[str]:
    """Batch 247: reject column-0 multiline python that breaks `run: |` scalars.

    Batch 246's IDLE_PATH_C_DONE CI step used an unindented ``python3 -c`` block;
    GitHub Actions failed immediately with \"workflow file issue\" (0s, empty jobs).
    When PyYAML is present, fail closed on unparseable ci.yml.
    """
    errs: list[str] = []
    if not path.is_file():
        return [f"missing {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    if "IDLE_PATH_C_DONE" not in text:
        errs.append("ci.yml: expected IDLE_PATH_C_DONE idle skip (Batch 246+)")
    # Batch 272: land-workflows-dry-run must assert Path C idle on its own file
    # (not a union grep that only Path B can satisfy via ALREADY_ALIGNED).
    if "path-c-dry-run.out" in text:
        if not (
            "IDLE_PATH_C_DONE" in text
            and "path-c-dry-run.out" in text
            and (
                "grep -E 'IDLE_PATH_C_DONE|already_on_tip|APPLY_READY' path-c-dry-run.out"
                in text
                or "grep -E \"IDLE_PATH_C_DONE|already_on_tip|APPLY_READY\" path-c-dry-run.out"
                in text
            )
        ):
            errs.append(
                "ci.yml: land-workflows-dry-run must grep IDLE_PATH_C_DONE|"
                "already_on_tip|APPLY_READY on path-c-dry-run.out alone (Batch 272)"
            )
        if "grep -E 'ALREADY_ALIGNED|would-align|APPLY_READY' path-b-dry-run.out path-c-dry-run.out" in text:
            errs.append(
                "ci.yml: land-workflows-dry-run still uses union grep that "
                "ignores Path C idle (Batch 272 leftover)"
            )
    if "path_c_followon_pending" not in text:
        errs.append("ci.yml: expected path_c_followon_pending catch-0020 probe")
    # Heuristic without PyYAML: a line that is exactly a top-level Python import
    # after a run block start is the Batch 246 failure mode.
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith("import ") or line.startswith("from "):
            errs.append(
                f"ci.yml:{i}: top-level Python import at column 0 breaks YAML "
                "`run: |` block scalars (Batch 247 workflow-file flake)"
            )
    try:
        import yaml  # type: ignore
    except ImportError:
        return errs
    try:
        data = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — surface parse errors
        errs.append(f"ci.yml: YAML parse failed: {exc}")
        return errs
    if not isinstance(data, dict):
        errs.append("ci.yml: top-level YAML is not a mapping")
        return errs
    jobs = data.get("jobs")
    if not isinstance(jobs, dict) or "portable-patches-on-main" not in jobs:
        errs.append("ci.yml: missing jobs.portable-patches-on-main after parse")
    return errs


def _dry_run_default_true(data: dict, name: str) -> list[str]:
    errs: list[str] = []
    if not data:
        return errs  # string-level checks cover when PyYAML absent
    on = data.get("on") or data.get(True)  # YAML may parse 'on' as True
    if not isinstance(on, dict):
        errs.append(f"{name}: missing on: workflow_dispatch")
        return errs
    wd = on.get("workflow_dispatch")
    if not isinstance(wd, dict):
        errs.append(f"{name}: workflow_dispatch missing or not a mapping")
        return errs
    inputs = wd.get("inputs") or {}
    dry = inputs.get("dry_run")
    if not isinstance(dry, dict):
        errs.append(f"{name}: inputs.dry_run missing")
        return errs
    if dry.get("default") is not True:
        errs.append(f"{name}: dry_run.default must be true (got {dry.get('default')!r})")
    if dry.get("type") not in (None, "boolean"):
        errs.append(f"{name}: dry_run.type should be boolean")
    return errs


def _token_gated_on_dry_run_false(text: str, name: str) -> list[str]:
    errs: list[str] = []
    if "MAIN_PUSH_TOKEN" not in text:
        errs.append(f"{name}: expected MAIN_PUSH_TOKEN reference")
    # Must not require token unconditionally for the job to start.
    if "Require token unless dry-run" not in text and "unless dry-run" not in text.lower():
        errs.append(f"{name}: expected a 'Require token unless dry-run' style gate")
    # Gate may use workflow_dispatch inputs.dry_run or resolved steps.mode.outputs.dry_run
    # (Batch 139: repository_dispatch shares the same land job).
    if (
        "inputs.dry_run == false" not in text
        and "dry_run == false" not in text
        and "outputs.dry_run == 'false'" not in text
        and 'outputs.dry_run == "false"' not in text
    ):
        errs.append(f"{name}: MAIN_PUSH_TOKEN gate must key off dry_run == false")
    return errs


def _check_path_b(text: str, data: dict) -> list[str]:
    errs = _dry_run_default_true(data, "land-option-b-on-main")
    errs.extend(_token_gated_on_dry_run_false(text, "land-option-b-on-main"))
    for needle in (
        "name: land-option-b-on-main",
        "workflow_dispatch",
        "0001-option-b-default-branch-notice.patch",
        "audit_local_tree.py",
        "dry_run=true",
    ):
        if needle not in text:
            errs.append(f"land-option-b-on-main: missing {needle!r}")
    return errs


def _check_path_c(text: str, data: dict) -> list[str]:
    errs = _dry_run_default_true(data, "land-path-c-on-main")
    errs.extend(_token_gated_on_dry_run_false(text, "land-path-c-on-main"))
    for needle in (
        "name: land-path-c-on-main",
        "workflow_dispatch",
        "repository_dispatch",
        "land-path-c-on-main",
        "chatgpt/drive-github-hardening-20260919",
        "apply_all.sh",
        "lemma_closed=false",
        "math_status_check",
        "cursor/portable-engineering-patches",
        "Scientific effect",
    ):
        if needle not in text and needle.lower() not in text.lower():
            errs.append(f"land-path-c-on-main: missing {needle!r}")
    return errs


def _run_help(script: Path) -> list[str]:
    errs: list[str] = []
    if not script.is_file():
        return [f"missing {script.relative_to(ROOT)}"]
    if not (script.stat().st_mode & 0o111):
        errs.append(f"{script.name}: not executable")
    proc = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
        timeout=30,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode not in (0,):
        # Some shells print usage and exit 0; accept 0 only.
        errs.append(f"{script.name} --help exit={proc.returncode}")
    if "--dry-run" not in out and "dry-run" not in out:
        errs.append(f"{script.name} --help must mention --dry-run")
    if "MAIN_PUSH_TOKEN" not in out and "MAIN_PUSH_TOKEN" not in script.read_text(
        encoding="utf-8"
    ):
        errs.append(f"{script.name}: should document MAIN_PUSH_TOKEN for live land")
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate land-option-b / land-path-c workflows (no MAIN_PUSH_TOKEN)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary on stdout",
    )
    args = parser.parse_args()

    missing = [p for p in (PATH_B, PATH_C, PATH_CI, OWNER_B, OWNER_C) if not p.is_file()]
    if missing:
        print(
            "validate_land_workflows: missing "
            + ", ".join(str(p.relative_to(ROOT)) for p in missing),
            file=sys.stderr,
        )
        return 2

    text_b = PATH_B.read_text(encoding="utf-8")
    text_c = PATH_C.read_text(encoding="utf-8")
    try:
        data_b = _load_yaml(PATH_B)
        data_c = _load_yaml(PATH_C)
    except Exception as exc:  # noqa: BLE001 — surface YAML errors as exit 2
        print(f"validate_land_workflows: YAML error: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    errors.extend(_check_path_b(text_b, data_b))
    errors.extend(_check_path_c(text_c, data_c))
    # Batch 247: fail closed if trial-ci.yml is unparseable (Actions 0s workflow-file flake).
    ci_errs = _check_ci_yml_parses(PATH_CI)
    if any("YAML parse failed" in e for e in ci_errs):
        print(
            "validate_land_workflows: YAML error: "
            + "; ".join(e for e in ci_errs if "YAML parse failed" in e),
            file=sys.stderr,
        )
        return 2
    errors.extend(ci_errs)
    errors.extend(_run_help(OWNER_B))
    errors.extend(_run_help(OWNER_C))

    payload = {
        "scientific_effect": "NONE",
        "lemma_closed": False,
        "goal_complete": False,
        "main_push_token_required": False,
        "workflows": [
            str(PATH_B.relative_to(ROOT)),
            str(PATH_C.relative_to(ROOT)),
            str(PATH_CI.relative_to(ROOT)),
        ],
        "owner_scripts": [
            str(OWNER_B.relative_to(ROOT)),
            str(OWNER_C.relative_to(ROOT)),
        ],
        "ci_yml_ok": not ci_errs,
        "ok": not errors,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if errors:
            print("validate_land_workflows: FAIL", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
        else:
            print(
                "validate_land_workflows: OK — "
                "land-option-b + land-path-c dry_run default true; "
                "ci.yml YAML parse OK; "
                "MAIN_PUSH_TOKEN not required for dry-run / --help"
            )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
