#!/usr/bin/env python3
"""Post Path-C eng wake comments on eng PRs in d6g8k5htny-coder/main.

Skips research drafts. Skips only when a wake comment already advertises the
*living* BASE_TIP (not a frozen batch marker). Uses GH_TOKEN / MAIN_PUSH_TOKEN
(App ghs lacks Issues:write). Triggered via trial workflow
wake-batch322-pr-comments (repository_dispatch).

Batch 336: INTENT tip is derived from portable/patches/BASE_TIP.txt (living),
not a frozen SHA (Batch 329 left @077464e while tip moved 388a22c→eeebb28).

Batch 338: BATCH_MARKER was frozen at \"Batch 329 wake\" so tip-sync never
re-posted — eng PRs #92/#93/#87/#36/#21/#12 still carried Intent @077464e while
BASE_TIP lived at 848aea2. Marker + skip gate now key off living tip.
TRIAL link is the trial repo (not merged PR #112).

Scientific effect: NONE. lemma_closed stays false.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "d6g8k5htny-coder/main"
COORD = "https://cursor.com/agents/bc-01a0cf1e-ebff-78a8-8a7a-9140fd59309a"
# Batch 338: do not freeze a merged trial PR number (#112).
TRIAL_REPO = "https://github.com/d6g8k5htny-coder/trial"
_ROOT = Path(__file__).resolve().parents[1]
_BASE_TIP_FILE = _ROOT / "portable" / "patches" / "BASE_TIP.txt"
_HARDENING_REF = "chatgpt/drive-github-hardening-20260919"
_PRINT_OWNER = _ROOT / "scripts" / "print_owner_unblock.sh"


def _living_tip_short() -> str:
    """Batch 336: wake INTENT tip follows BASE_TIP (not a frozen SHA)."""
    try:
        line = _BASE_TIP_FILE.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return "unknown"
    # Prefer full 40-char SHA so ref dates like 20260919 are not mistaken for tips.
    m = re.search(r"(?i)\b([0-9a-f]{40})\b", line)
    if m:
        return m.group(1)[:7].lower()
    # Fallback: last whitespace token that looks like a short SHA.
    for tok in reversed(line.split()):
        if re.fullmatch(r"(?i)[0-9a-f]{7,40}", tok):
            return tok[:7].lower()
    return "unknown"


def _living_batch_n() -> str:
    """Batch 338: automation batch from print_owner header (no freeze at 329)."""
    try:
        text = _PRINT_OWNER.read_text(encoding="utf-8")
    except OSError:
        text = ""
    m = re.search(r"=== Batch (\d+)\b", text)
    if m:
        return m.group(1)
    return "338"


def batch_marker() -> str:
    """Living wake marker — tip move unlocks re-post (Batch 338)."""
    return f"Batch {_living_batch_n()} wake @{_living_tip_short()}"


# Back-compat alias for Intent / importers that still read BATCH_MARKER.
# Must not be a frozen \"Batch 329 wake\" string.
BATCH_MARKER = batch_marker  # callable; see also batch_marker()


def intent_line() -> str:
    return (
        f"Intent: tip {_HARDENING_REF} @ {_living_tip_short()}; "
        "Path C IDLE@0019; lemma_closed=false; scientific effect NONE; "
        "no claim promotion"
    )


def _wake_body_has_living_tip(body: str, tip: str | None = None) -> bool:
    """True when a prior wake comment already advertises the living tip."""
    tip = tip or _living_tip_short()
    if not tip or tip == "unknown":
        return False
    b = body or ""
    if "wake" not in b.lower():
        return False
    # Match Intent line tip pin produced by intent_line().
    if f"@ {tip}" in b:
        return True
    # Marker form: Batch N wake @<tip>
    if f"wake @{tip}" in b.lower():
        return True
    return False


TASKS: dict[int, str] = {
    92: (
        "Crosswalk eng — keep RN downstream crosswalk outside the closed "
        "`docs/math_status/` packet (`EXPECTED_NAMES`); land nav/RESEARCH_INDEX/"
        "NAVIGATION pointers + packet-placement regression; green "
        "`math_status_check`/`navigation_check`; coordinate with #87/#93; do not "
        "edit byte-pinned OPEN_PROBLEMS or discharge obligations."
    ),
    93: (
        "Crosswalk eng — surface the hardening-lane RN downstream crosswalk + "
        "Math- #7 mesoscopic draft from default home once #92 path resolves; "
        "run navigation/workspace landing checks only; do not retarget research "
        "tree into default `main` or discharge OBL-H5-JETMOD / D3-LEMMA-RN-UNIF."
    ),
    87: (
        "Crosswalk eng — resume downstream RN crosswalk honesty (historical "
        "ABSENT carriers vs current blockers). Prefer #92 placement fix (file "
        "outside closed math_status packet) over re-landing inside the packet; "
        "keep lemma_closed=false / certified_C_H false; no frozen proof/register/"
        "Boolean edits."
    ),
    36: (
        "@claude — resume eng: keep `research/bands/ladder.py` at the exact bytes "
        "hardening-lane certificates pin (twelve_project_check source identity). "
        "Give way / reconcile on migration base — do not re-pin certificates or "
        "promote claims; leave research status untouched."
    ),
    21: (
        "@claude — resume eng: architectural admission attestations + salvaged H3 "
        "review artifacts on a live tip (not orphaned stack). Keep DRAFT until "
        "reviewed; additive-only; no obligation/claim discharge; tip-align if "
        "base drifted."
    ),
    12: (
        "Fail-closed OPEN/HOLD eng — keep JETMOD/RN-UNIF `math_status` + "
        "math_console mirrors fail-closed (tools refuse flag moves). "
        "HOLD/NEVER-MERGE per owner order; green CI ≠ discharge; do not close "
        "OPEN obligations or flip lemma_closed; prefer close-as-superseded "
        "hygiene only if still conflicting with tip receipts — no status promotion."
    ),
}

ENG = (92, 93, 87, 36, 21, 12)
SKIP_DRAFTS = (47, 46, 38, 8, 7)


def token() -> str:
    t = (os.environ.get("GH_TOKEN") or os.environ.get("MAIN_PUSH_TOKEN") or "").strip()
    if not t:
        raise SystemExit("GH_TOKEN / MAIN_PUSH_TOKEN missing")
    return t


def api(method: str, path: str, body: dict | None = None) -> object:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "trial-batch338-wake",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode() if e.fp else ""
        raise SystemExit(f"HTTP {e.code} {path}: {err[:400]}") from e


def list_comments(n: int) -> list[dict]:
    out: list[dict] = []
    page = 1
    while True:
        chunk = api(
            "GET",
            f"/repos/{REPO}/issues/{n}/comments?per_page=100&page={page}",
        )
        assert isinstance(chunk, list)
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def wake_body(n: int) -> str:
    marker = batch_marker()
    return (
        f"**{marker}** — project-intent eng resume (not research flip)\n"
        "\n"
        f"Coordinator: {COORD}\n"
        "\n"
        f"{intent_line()}\n"
        "\n"
        f"**Eng resume task:** {TASKS[n]}\n"
        "\n"
        "Path C intent advance only. Keep DRAFT discipline where applicable; "
        "never promote claims/premises/prizes/lemmas. "
        f"Trial wake path: [{TRIAL_REPO}]({TRIAL_REPO}) / workflow "
        "`wake-batch322-pr-comments`.\n"
    )


def main() -> int:
    commented: list[dict] = []
    skipped: list[dict] = []
    tip = _living_tip_short()
    marker = batch_marker()

    for n in SKIP_DRAFTS:
        skipped.append({"pr": n, "reason": "research_draft"})

    urls: list[str] = []
    for n in ENG:
        comments = list_comments(n)
        existing = [
            c for c in comments if _wake_body_has_living_tip(c.get("body") or "", tip)
        ]
        if existing:
            print(f"SKIP #{n}: living tip @{tip} already present in wake comment")
            for c in existing:
                u = c.get("html_url") or ""
                print(u)
                if u:
                    urls.append(u)
            skipped.append(
                {
                    "pr": n,
                    "reason": "identical_living_tip_wake",
                    "tip": tip,
                    "urls": [
                        c.get("html_url") for c in existing if c.get("html_url")
                    ],
                }
            )
            continue
        print(f"POST #{n} marker={marker}...")
        created = api(
            "POST",
            f"/repos/{REPO}/issues/{n}/comments",
            {"body": wake_body(n)},
        )
        assert isinstance(created, dict)
        u = created.get("html_url") or ""
        print(u)
        if u:
            urls.append(u)
        commented.append({"pr": n, "url": u})

    result = {
        "batch": int(_living_batch_n()),
        "marker": marker,
        "tip": tip,
        "commented": commented,
        "skipped": skipped,
        "lemma_closed": False,
        "flipped_anything": False,
        "scientific_effect": "NONE",
    }
    print("=== RESULT JSON ===")
    print(json.dumps(result, indent=2))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## {marker} comment URLs\n")
            for u in urls:
                f.write(f"- {u}\n")
            f.write("\n```json\n")
            f.write(json.dumps(result, indent=2))
            f.write("\n```\n")
    print("=== COMMENT URLS ===")
    for u in urls:
        print(u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
