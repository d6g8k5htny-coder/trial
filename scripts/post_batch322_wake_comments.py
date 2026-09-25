#!/usr/bin/env python3
"""Post Batch 329 wake comments on eng PRs in d6g8k5htny-coder/main.

Skips research drafts. Skips if an identical Batch 329 wake comment already
exists. Uses GH_TOKEN / MAIN_PUSH_TOKEN (App ghs lacks Issues:write).
Triggered via trial workflow wake-batch322-pr-comments (repository_dispatch).

Scientific effect: NONE. lemma_closed stays false.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

REPO = "d6g8k5htny-coder/main"
BATCH_MARKER = "Batch 329 wake"
COORD = "https://cursor.com/agents/bc-01a0cf1e-ebff-78a8-8a7a-9140fd59309a"
INTENT = (
    "Intent: tip chatgpt/drive-github-hardening-20260919 @ 077464e; "
    "Path C IDLE@0019; lemma_closed=false; scientific effect NONE; no claim promotion"
)
TRIAL_PR = "https://github.com/d6g8k5htny-coder/trial/pull/112"

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
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "trial-batch329-wake",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise SystemExit(f"HTTP {e.code} {method} {path}: {err}") from e


def list_comments(n: int) -> list[dict]:
    out: list[dict] = []
    page = 1
    while True:
        chunk = api(
            "GET",
            f"/repos/{REPO}/issues/{n}/comments?per_page=100&page={page}",
        )
        assert isinstance(chunk, list)
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def wake_body(n: int) -> str:
    return (
        f"**{BATCH_MARKER}** — project-intent eng resume (not research flip)\n"
        "\n"
        f"Coordinator: {COORD}\n"
        "\n"
        f"{INTENT}\n"
        "\n"
        f"**Eng resume task:** {TASKS[n]}\n"
        "\n"
        "Path C intent advance only. Keep DRAFT discipline where applicable; "
        "never promote claims/premises/prizes/lemmas. "
        f"Trial wake path: [PR #112]({TRIAL_PR}) / workflow `wake-batch322-pr-comments`.\n"
    )


def main() -> int:
    commented: list[dict] = []
    skipped: list[dict] = []

    for n in SKIP_DRAFTS:
        skipped.append({"pr": n, "reason": "research_draft"})

    urls: list[str] = []
    for n in ENG:
        existing = [
            c for c in list_comments(n) if BATCH_MARKER in (c.get("body") or "")
        ]
        if existing:
            print(f"SKIP #{n}: identical {BATCH_MARKER} already present")
            for c in existing:
                u = c.get("html_url") or ""
                print(u)
                if u:
                    urls.append(u)
            skipped.append({"pr": n, "reason": "identical_batch329_wake", "urls": [
                c.get("html_url") for c in existing if c.get("html_url")
            ]})
            continue
        print(f"POST #{n}...")
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
        "batch": 329,
        "commented": commented,
        "skipped": skipped,
        "lemma_closed": False,
        "flipped_anything": False,
    }
    print("=== RESULT JSON ===")
    print(json.dumps(result, indent=2))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Batch 329 wake comment URLs\n")
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
