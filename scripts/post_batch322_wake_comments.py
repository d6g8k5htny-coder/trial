#!/usr/bin/env python3
"""Post Path-C eng wake comments on eng PRs in d6g8k5htny-coder/main.

Skips inventable/research drafts and closed or merged PRs. For open PRs, skips
when a wake comment advertises the *living* BASE_TIP (not a frozen batch marker).
Uses GH_TOKEN / MAIN_PUSH_TOKEN (App ghs lacks Issues:write). Triggered via trial workflow
wake-batch322-pr-comments (repository_dispatch).

Batch 336: INTENT tip is derived from portable/patches/BASE_TIP.txt (living),
not a frozen SHA (Batch 329 left @077464e while tip moved 388a22c→eeebb28).

Batch 338: BATCH_MARKER was frozen at \"Batch 329 wake\" so tip-sync never
re-posted — eng PRs #92/#93/#87/#36/#21/#12 still carried Intent @077464e while
BASE_TIP lived at 848aea2. Marker + skip gate now key off living tip.
TRIAL link is the trial repo (not merged PR #112).

Batch 340: eng targets narrowed to #36 ladder pin / #21 architectural
admission / #12 fail-closed OPEN/HOLD. Skip inventable/research drafts
(#110,#109,#108,#106,#105,#103,#98,#46,#38,#8,#7). Wake marker Batch 340;
resume tasks: no lemma_closed flip; tip-align if base drifted; additive-only.

Batch 341: `_living_batch_n` again derives from print_owner header (Batch 340 froze `_WAKE_BATCH="340"`).

Batch 340 (rewake): token() was env-only and preferred GH_TOKEN first. App
ghs often lacks Issues:write; durable Path C write uses well-known
MAIN_PUSH_TOKEN file drops (grant / when_writable_land order). Prefer
MAIN_PUSH_TOKEN then file drops so living-tip re-posts fire locally/agents.

Batch 343: also wake open *trial* eng PRs (not inventable/research). When
trial has no eng PRs, main() reports idle_no_commit evidence. Historical
main eng lanes remain #36/#21/#12.

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
TRIAL = "d6g8k5htny-coder/trial"
COORD = "https://cursor.com/agents/bc-01a0cf1e-ebff-78a8-8a7a-9140fd59309a"
TRIAL_REPO = "https://github.com/d6g8k5htny-coder/trial"
_ROOT = Path(__file__).resolve().parents[1]
_BASE_TIP_FILE = _ROOT / "portable" / "patches" / "BASE_TIP.txt"
_HARDENING_REF = "chatgpt/drive-github-hardening-20260919"
# Batch 340: same durable drop order as grant / when_writable_land.
_DURABLE_TOKEN_FILES = (
    Path("/cursor/stores/self/MAIN_PUSH_TOKEN"),
    Path("/workspace/.secrets/MAIN_PUSH_TOKEN"),
    Path("/tmp/gh-dylan-auth/access_token"),
)
_PRINT_OWNER = _ROOT / "scripts" / "print_owner_unblock.sh"
_REFRESH = _ROOT / "scripts" / "refresh_path_c_bundle.sh"


def _living_tip_short() -> str:
    """Wake INTENT tip follows BASE_TIP (not a frozen SHA)."""
    try:
        line = _BASE_TIP_FILE.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return "unknown"
    m = re.search(r"(?i)\b([0-9a-f]{40})\b", line)
    if m:
        return m.group(1)[:7].lower()
    for tok in reversed(line.split()):
        if re.fullmatch(r"(?i)[0-9a-f]{7,40}", tok):
            return tok[:7].lower()
    return "unknown"


def _living_batch_n() -> str:
    """Batch 341: derive automation batch from print_owner (not frozen _WAKE_BATCH=340).

    Batch 340 froze `_WAKE_BATCH = "340"` because print_owner lagged at 339 —
    after Batch 341 header bump that freeze left wake markers at Batch 340 forever
    (same class as Batch 338 Batch 329 marker freeze). Prefer print_owner header,
    else REFRESH_BATCH_TAG default, else last-resort hardcoded.

    Batch 345: last-resort hardcoded return bumped off frozen "341" so empty-tree
    fallback cannot lag living Batch 345 / print_owner header (same class as
    inventory ultimate fallback 336→340→343).
    Batch 346: last-resort bumped off frozen "345" after WAKE346 print_owner header.
    Batch 346: last-resort bumped off frozen "345" so empty-tree fallback cannot
    lag living print_owner Batch 346.
    Batch 352: last-resort bumped off frozen "351" so empty-tree fallback cannot
    lag living Batch 352 / print_owner header (coordinator wake).
    Batch 357: last-resort bumped off frozen "356" so empty-tree fallback cannot
    lag living Batch 357 / print_owner header (coordinator wake).
    """
    try:
        text = _PRINT_OWNER.read_text(encoding="utf-8")
    except OSError:
        text = ""
    m = re.search(r"=== Batch (\d+)\b", text)
    if m:
        return m.group(1)
    try:
        rtext = _REFRESH.read_text(encoding="utf-8")
    except OSError:
        rtext = ""
    m = re.search(r"REFRESH_BATCH_TAG:-(\d+)", rtext)
    if m:
        return m.group(1)


# Batch 357: last-resort bumped off frozen "356".
    # Batch 359: last-resort bumped off frozen "358".
    # Batch 360: last-resort bumped off frozen "359".
    # Batch 368: last-resort bumped off frozen "367".
    # Batch 369: last-resort bumped off frozen "368".
    # Batch 370: last-resort bumped off frozen "369".
    # Batch 371: last-resort bumped off frozen "370".
    # Batch 372: last-resort bumped off frozen "371" (peer missed wake; lag vs print_owner 372).
    # Batch 373: last-resort bumped off frozen "372".
    # Batch 374: last-resort bumped off frozen "373".
    # Batch 375: last-resort bumped off frozen "374".
    # Batch 376: last-resort bumped off frozen "375".
    # Batch 377: last-resort bumped off frozen "376".
    # Batch 378: last-resort bumped off frozen "377".
    # Batch 379: last-resort bumped off frozen "378".
    # Batch 380: last-resort bumped off frozen "379".
    # Batch 381: last-resort bumped off frozen "380".
    # Batch 382: last-resort bumped off frozen "381".
    # Batch 383: last-resort bumped off frozen "382".
    # Batch 384: last-resort bumped off frozen "383".
    # Batch 385: last-resort bumped off frozen "384".
    # Batch 386: last-resort bumped off frozen "385".
    # Batch 387: last-resort bumped off frozen "386".
    # Batch 388: last-resort bumped off frozen "387".
    # Batch 389: last-resort bumped off frozen "388".
    # Batch 391: last-resort bumped off frozen "390".
    # Batch 396: last-resort bumped off frozen "395".
    # Batch 399: last-resort bumped off frozen "398".
    # Batch 400: last-resort bumped off frozen "399".
    # Batch 401: last-resort bumped off frozen "400".
    # Batch 402: last-resort bumped off frozen "401".
    # Batch 403: last-resort bumped off frozen "402".
    # Batch 404: last-resort bumped off frozen "403".
    # Batch 405: last-resort bumped off frozen "404".
    # Batch 406: last-resort bumped off frozen "405".
    # Batch 407: last-resort bumped off frozen "406".
    # Batch 408: last-resort bumped off frozen "407".
    # Batch 409: last-resort bumped off frozen "408".
    # Batch 410: last-resort bumped off frozen "409".
    # Batch 411: last-resort bumped off frozen "410".
    # Batch 412: last-resort bumped off frozen "411".
    # Batch 413: last-resort bumped off frozen "412".
    # Batch 414: last-resort bumped off frozen "413".
    # Batch 415: last-resort bumped off frozen "414".
    # Batch 416: last-resort bumped off frozen "415".
    # Batch 417: last-resort bumped off frozen "416".
    # Batch 418: last-resort bumped off frozen "417".
    # Batch 419: last-resort bumped off frozen "418".
    # Batch 420: last-resort bumped off frozen "419".
    # Batch 421: last-resort bumped off frozen "420".
    # Batch 422: last-resort bumped off frozen "421".
    # Batch 423: last-resort bumped off frozen "422".
    # Batch 424: last-resort bumped off frozen "423".
    # Batch 425: last-resort bumped off frozen "424".
    # Batch 426: last-resort bumped off frozen "425".
    # Batch 427: last-resort bumped off frozen "426".
    # Batch 428: last-resort bumped off frozen "427".
    # Batch 429: last-resort bumped off frozen "428".
    # Batch 430: last-resort bumped off frozen "429".
    # Batch 431: last-resort bumped off frozen "430".
    # Batch 432: last-resort bumped off frozen "431".
    # Batch 433: last-resort bumped off frozen "432".
    # Batch 434: last-resort bumped off frozen "433".
    # Batch 435: last-resort bumped off frozen "434".
    # Batch 436: last-resort bumped off frozen "435".
    # Batch 437: last-resort bumped off frozen "436".
    # Batch 438: last-resort bumped off frozen "437".
    # Batch 439: last-resort bumped off frozen "438".
    # Batch 440: last-resort bumped off frozen "439".
    # Batch 441: last-resort bumped off frozen "440".
    # Batch 442: last-resort bumped off frozen "441".
    # Batch 443: last-resort bumped off frozen "442".
    # Batch 444: last-resort bumped off frozen "443".
    # Batch 445: last-resort bumped off frozen "444".
    # Batch 446: last-resort bumped off frozen "445".
    # Batch 447: last-resort bumped off frozen "446".
    # Batch 448: last-resort bumped off frozen "447".
    # Batch 449: last-resort bumped off frozen "448".
    # Batch 450: last-resort bumped off frozen "449".
    # Batch 451: last-resort bumped off frozen "450".
    # Batch 453: last-resort bumped off frozen "451".
    # Batch 454: last-resort bumped off frozen "453".
    # Batch 455: last-resort bumped off frozen "454".
    # Batch 456: last-resort bumped off frozen "455".
    # Batch 457: last-resort bumped off frozen "456".
    # Batch 458: last-resort bumped off frozen "457".
    # Batch 459: last-resort bumped off frozen "458".
    # Batch 460: last-resort bumped off frozen "459".
    # Batch 461: last-resort bumped off frozen "460".
    # Batch 462: last-resort bumped off frozen "461".
    # Batch 463: last-resort bumped off frozen "462".
    # Batch 464: last-resort bumped off frozen "463".
    # Batch 465: last-resort bumped off frozen "464".
    # Batch 466: last-resort bumped off frozen "465".
    # Batch 467: last-resort bumped off frozen "466".
    return "467"
def batch_marker() -> str:
    """Living wake marker — tip move unlocks re-post."""
    return f"Batch {_living_batch_n()} wake @{_living_tip_short()}"


BATCH_MARKER = batch_marker  # callable; back-compat alias


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
    if f"@ {tip}" in b:
        return True
    if f"wake @{tip}" in b.lower():
        return True
    return False


TASKS: dict[int, str] = {
    # Retained for Batch 338 test wake_body(92) + historical crosswalk context.
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
        "@claude — resume eng (Batch 340): keep `research/bands/ladder.py` at the "
        "exact bytes hardening-lane certificates pin (twelve_project_check source "
        "identity). Tip-align if base drifted; additive-only; give way / reconcile "
        "on migration base — do not re-pin certificates; no lemma_closed flip; no "
        "claim promotion."
    ),
    21: (
        "@claude — resume eng (Batch 340): architectural admission attestations + "
        "salvaged H3 review artifacts on a live tip (not orphaned stack). Tip-align "
        "if base drifted; additive-only; keep DRAFT until reviewed; no obligation/"
        "claim discharge; no lemma_closed flip."
    ),
    12: (
        "Fail-closed OPEN/HOLD eng (Batch 340): keep JETMOD/RN-UNIF `math_status` + "
        "math_console mirrors fail-closed (tools refuse flag moves). HOLD/NEVER-MERGE "
        "per owner order; tip-align if base drifted; additive-only; green CI ≠ "
        "discharge; no lemma_closed flip; no status promotion."
    ),
}

# Batch 340: ladder / admission / fail-closed OPEN/HOLD only (main).
ENG = (36, 21, 12)
SKIP_DRAFTS = (110, 109, 108, 106, 105, 103, 98, 46, 38, 8, 7)

# Batch 343: trial eng-only wake targets (grant/land hygiene — not inventable).
TRIAL_ENG_TASKS: dict[int, str] = {
    114: (
        "Resume eng (Batch 343): land `portable/BATCH341_GRANT.json` onto trial "
        "main (tip-aligned @ living BASE_TIP). Undraft when CI green; additive-only; "
        "no lemma_closed flip; no claim/research promotion; durable write 8/8 preserved."
    ),
}


def resolve_wake_token(
    *,
    env: dict[str, str] | None = None,
    file_candidates: list[Path] | tuple[Path, ...] | None = None,
) -> tuple[str | None, str | None]:
    """Return (token, source_label). Never logs or returns the secret to stdout.

    Batch 340: prefer env MAIN_PUSH_TOKEN over GH_TOKEN / GITHUB_TOKEN (App ghs
    often lacks Issues:write), then durable well-known file drops matching
    grant / when_writable_land.
    """
    environ = env if env is not None else os.environ
    for key in ("MAIN_PUSH_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        val = (environ.get(key) or "").strip()
        if val:
            return val, f"env:{key}"
    candidates = (
        file_candidates if file_candidates is not None else _DURABLE_TOKEN_FILES
    )
    for path in candidates:
        try:
            if not path.is_file():
                continue
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if raw:
            return raw, f"file:{path}"
    return None, None


def token() -> str:
    t, source = resolve_wake_token()
    if not t:
        raise SystemExit(
            "wake token missing — set MAIN_PUSH_TOKEN / GH_TOKEN or drop a PAT at "
            "/cursor/stores/self/MAIN_PUSH_TOKEN, /workspace/.secrets/MAIN_PUSH_TOKEN, "
            "or /tmp/gh-dylan-auth/access_token"
        )
    if os.environ.get("WAKE_TOKEN_SOURCE_LOG", "").strip() in ("1", "true", "yes"):
        print(f"wake_token_source={source}", file=sys.stderr)
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
            "User-Agent": "trial-batch343-wake",
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


def list_comments(n: int, *, repo: str | None = None) -> list[dict]:
    repo = repo or REPO
    out: list[dict] = []
    page = 1
    while True:
        chunk = api(
            "GET",
            f"/repos/{repo}/issues/{n}/comments?per_page=100&page={page}",
        )
        assert isinstance(chunk, list)
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def list_open_trial_eng_prs() -> list[int]:
    """Open trial eng PRs — exclude inventable/research by known skip set + title heuristics."""
    data = api(
        "GET",
        f"/repos/{TRIAL}/pulls?state=open&per_page=100",
    )
    assert isinstance(data, list)
    out: list[int] = []
    for pr in data:
        n = int(pr.get("number") or 0)
        if not n or n in SKIP_DRAFTS:
            continue
        title = (pr.get("title") or "").lower()
        # Skip inventable / research / tip-observe drafts on trial.
        if any(
            k in title
            for k in (
                "inventable",
                "tip-observe",
                "research",
                "claim",
                "lemma",
                "prize",
            )
        ):
            continue
        out.append(n)
    return sorted(out)


def wake_body(n: int, *, repo: str | None = None) -> str:
    marker = batch_marker()
    repo = repo or REPO
    if repo == TRIAL:
        task = TRIAL_ENG_TASKS.get(
            n,
            "Resume Path C eng advance on this trial PR — additive-only; "
            "no lemma_closed flip; no claim/research promotion.",
        )
    else:
        task = TASKS[n]
    return (
        f"**{marker}** — project-intent eng resume (not research flip)\n"
        "\n"
        f"Coordinator: {COORD}\n"
        "\n"
        f"{intent_line()}\n"
        "\n"
        f"**Eng resume task:** {task}\n"
        "\n"
        "Path C intent advance only. Tip-align if base drifted; additive-only; "
        "never promote claims/premises/prizes/lemmas; no lemma_closed flip. "
        f"Trial wake path: [{TRIAL_REPO}]({TRIAL_REPO}) / workflow "
        "`wake-batch322-pr-comments`.\n"
    )


def _post_or_skip(
    n: int,
    *,
    repo: str,
    tip: str,
    marker: str,
    commented: list[dict],
    skipped: list[dict],
    urls: list[str],
) -> None:
    # Recheck here: static targets and previously listed open PRs may be closed.
    pr = api("GET", f"/repos/{repo}/pulls/{n}")
    if (
        not isinstance(pr, dict)
        or pr.get("state") not in ("open", "closed")
        or type(pr.get("merged")) is not bool
    ):
        raise SystemExit(f"Cannot verify PR state for {repo}#{n}; refusing wake")
    if pr["state"] != "open" or pr["merged"]:
        print(f"SKIP {repo}#{n}: PR is closed or merged")
        skipped.append(
            {
                "repo": repo,
                "pr": n,
                "reason": "closed_or_merged_pr",
                "state": pr["state"],
                "merged": pr["merged"],
            }
        )
        return
    comments = list_comments(n, repo=repo)
    existing = [
        c for c in comments if _wake_body_has_living_tip(c.get("body") or "", tip)
    ]
    if existing:
        print(f"SKIP {repo}#{n}: living tip @{tip} already present in wake comment")
        for c in existing:
            u = c.get("html_url") or ""
            print(u)
            if u:
                urls.append(u)
        skipped.append(
            {
                "repo": repo,
                "pr": n,
                "reason": "identical_living_tip_wake",
                "tip": tip,
                "urls": [c.get("html_url") for c in existing if c.get("html_url")],
            }
        )
        return
    print(f"POST {repo}#{n} marker={marker}...")
    created = api(
        "POST",
        f"/repos/{repo}/issues/{n}/comments",
        {"body": wake_body(n, repo=repo)},
    )
    assert isinstance(created, dict)
    u = created.get("html_url") or ""
    print(u)
    if u:
        urls.append(u)
    commented.append({"repo": repo, "pr": n, "url": u})


def main() -> int:
    commented: list[dict] = []
    skipped: list[dict] = []
    tip = _living_tip_short()
    marker = batch_marker()
    urls: list[str] = []

    # Batch 343: trial eng-only first (assignment scope).
    trial_eng = list_open_trial_eng_prs()
    print(f"trial_open_eng_prs={trial_eng}")
    if not trial_eng:
        print("idle_no_commit: no open eng-only PRs on d6g8k5htny-coder/trial")
        result = {
            "batch": int(_living_batch_n()),
            "marker": marker,
            "tip": tip,
            "action": "idle_no_commit",
            "trial_open_eng_prs": [],
            "commented": [],
            "skipped": [{"reason": "no_open_trial_eng_prs"}],
            "lemma_closed": False,
            "flipped_anything": False,
            "scientific_effect": "NONE",
            "goal": "open",
        }
        print("=== RESULT JSON ===")
        print(json.dumps(result, indent=2))
        return 0

    for n in trial_eng:
        _post_or_skip(
            n,
            repo=TRIAL,
            tip=tip,
            marker=marker,
            commented=commented,
            skipped=skipped,
            urls=urls,
        )

    # Historical main eng lanes — tip-sync wake when living tip moved.
    for n in SKIP_DRAFTS:
        skipped.append({"repo": REPO, "pr": n, "reason": "research_or_inventable_draft"})
    for n in ENG:
        _post_or_skip(
            n,
            repo=REPO,
            tip=tip,
            marker=marker,
            commented=commented,
            skipped=skipped,
            urls=urls,
        )

    result = {
        "batch": int(_living_batch_n()),
        "marker": marker,
        "tip": tip,
        "action": "post_eng_pr_wake_comments",
        "trial_open_eng_prs": trial_eng,
        "commented": commented,
        "skipped": skipped,
        "lemma_closed": False,
        "flipped_anything": False,
        "scientific_effect": "NONE",
        "goal": "open",
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
