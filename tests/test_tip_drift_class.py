"""Offline checks for scripts/tip_drift_class.py and the DESCENDANT_OK gates.

Sidecar b3c6 (2026-09-27): hardening merges land several times per hour, so a
strict ``live == BASE_TIP`` gate reds every trial-ci run between an upstream
merge and the next tip-sync pulse. With Path C landed, a live tip that
*descends* from BASE_TIP still carries the stack; BEHIND / DIVERGED stay red.

Repository-intent only. Not evidence about any claim; scientific effect NONE.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tip_drift_class as tdc  # noqa: E402

BASE = "e7652a130398e88b2119884498af0987eef135c0"
LIVE = "d4ad3bbe9dc3eb9e7c6c61a3fe57dbdf3027e10b"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Never hit the compare API in unit tests; each test sets the answer."""
    monkeypatch.setattr(tdc, "_compare_status", lambda *a, **k: pytest.fail("network"))
    tdc._CACHE.clear()


def _status(monkeypatch, value: str):
    monkeypatch.setattr(tdc, "_compare_status", lambda base, live, repo=None, timeout=30: value)


def test_match_is_local_and_prefix_tolerant():
    assert tdc.classify(BASE, BASE) == "MATCH"
    assert tdc.classify(BASE[:7], BASE) == "MATCH"
    assert tdc.classify(BASE, BASE[:12]) == "MATCH"
    assert tdc.classify(BASE.upper(), BASE) == "MATCH"


def test_bad_input_is_unknown_without_network():
    assert tdc.classify("", LIVE) == "UNKNOWN"
    assert tdc.classify(None, LIVE) == "UNKNOWN"
    assert tdc.classify("not-a-sha", LIVE) == "UNKNOWN"
    assert tdc.classify(BASE, "abc") == "UNKNOWN"  # < 7 hex


@pytest.mark.parametrize(
    "status,expected",
    [
        ("ahead", "DESCENDANT"),
        ("behind", "BEHIND"),
        ("diverged", "DIVERGED"),
        ("identical", "MATCH"),
        ("", "UNKNOWN"),
        ("garbage", "UNKNOWN"),
    ],
)
def test_compare_status_maps_to_class(monkeypatch, status, expected):
    _status(monkeypatch, status)
    assert tdc.classify(BASE, LIVE) == expected


def test_acceptable_policy():
    assert tdc.acceptable("MATCH", landed=False) is True
    assert tdc.acceptable("MATCH", landed=True) is True
    assert tdc.acceptable("DESCENDANT", landed=True) is True
    # Not landed → a moved tip still needs a real refresh before landing.
    assert tdc.acceptable("DESCENDANT", landed=False) is False
    for cls in ("BEHIND", "DIVERGED", "UNKNOWN"):
        assert tdc.acceptable(cls, landed=True) is False
        assert tdc.acceptable(cls, landed=False) is False


def test_bad_env_token_falls_back_to_anonymous(monkeypatch):
    """A 401 on the authenticated compare call must not yield UNKNOWN."""
    import urllib.error

    monkeypatch.undo()  # use the real _compare_status, with urllib stubbed
    tdc._CACHE.clear()
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_definitely_bad")
    seen: list[bool] = []

    class _Resp:
        def __init__(self, status):
            self._s = status

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"status": self._s}).encode()

    def fake_urlopen(req, timeout=30):
        authed = "Authorization" in req.headers or "authorization" in {k.lower() for k in req.headers}
        seen.append(authed)
        if authed:
            raise urllib.error.HTTPError(req.full_url, 401, "Bad credentials", {}, None)
        return _Resp("ahead")

    monkeypatch.setattr(tdc.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(tdc.subprocess, "run", lambda *a, **k: pytest.fail("gh should not be needed"))
    assert tdc.classify(BASE, LIVE) == "DESCENDANT"
    assert seen == [True, False]


def test_api_exhausted_falls_back_to_git_ancestry_before_gh(monkeypatch):
    """NA-0009: both API paths dead (rate limit) → git ancestry answers; gh never needed."""
    monkeypatch.undo()
    tdc._CACHE.clear()
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("MAIN_PUSH_TOKEN", raising=False)

    def dead_urlopen(req, timeout=30):
        raise OSError("API rate limit exceeded")

    monkeypatch.setattr(tdc.urllib.request, "urlopen", dead_urlopen)
    monkeypatch.setattr(tdc, "_git_compare_status", lambda base, live, repo=None, timeout=120: "ahead")
    monkeypatch.setattr(tdc.subprocess, "run", lambda *a, **k: pytest.fail("gh should not be needed"))
    assert tdc.classify(BASE, LIVE) == "DESCENDANT"


def _seed_remote(tmp_path: Path, branch: str) -> tuple[Path, dict[str, str]]:
    """Local 'research repo': A -> B -> C on `branch`; D diverges from A on 'other'."""
    src = tmp_path / "src"
    src.mkdir()
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def g(*a: str) -> str:
        import os

        return subprocess.run(["git", "-C", str(src), *a], check=True, capture_output=True, text=True,
                              env={**os.environ, **env}).stdout.strip()

    g("init", "-q", "-b", branch)
    shas: dict[str, str] = {}
    for name in ("A", "B", "C"):
        (src / name).write_text(name, encoding="utf-8")
        g("add", name)
        g("commit", "-q", "-m", name)
        shas[name] = g("rev-parse", "HEAD")
    g("checkout", "-q", "-b", "other", shas["A"])
    (src / "D").write_text("D", encoding="utf-8")
    g("add", "D")
    g("commit", "-q", "-m", "D")
    shas["D"] = g("rev-parse", "HEAD")
    g("checkout", "-q", branch)
    return src, shas


def test_git_compare_status_classes_offline(monkeypatch, tmp_path):
    """identical / ahead / behind / diverged / unknown from a local mirror; no network, no token."""
    monkeypatch.undo()
    branch = "chatgpt/drive-github-hardening-test"
    src, s = _seed_remote(tmp_path, branch)
    monkeypatch.setenv("TIP_DRIFT_GIT_URL", str(src))
    monkeypatch.setenv("TIP_DRIFT_GIT_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(tdc, "HARDENING_BRANCH", branch)
    monkeypatch.setattr(tdc.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(OSError("no api")))

    assert tdc._git_compare_status(s["A"], s["C"]) == "ahead"
    assert tdc._git_compare_status(s["C"], s["A"]) == "behind"
    assert tdc._git_compare_status(s["B"], s["B"][:7]) == "identical"
    assert tdc._git_compare_status(s["B"], s["D"]) == "diverged"  # D is off-branch: 40-hex, fetched by SHA
    assert tdc._git_compare_status(s["A"], "deadbeef") == ""  # unknown stays unknown
    mirror = tdc._git_mirror_dir(tdc.MAIN_REPO)
    assert (mirror / "HEAD").is_file()  # cached for later calls in the same run

    tdc._CACHE.clear()
    assert tdc.classify(s["A"], s["C"]) == "DESCENDANT"
    assert tdc.classify(s["B"], s["D"]) == "DIVERGED"
    assert tdc.classify(s["A"], "deadbeef") == "UNKNOWN"


def test_intent_descends_helper_uses_git_fallback():
    """tests/test_intent._descends_from_base_tip must not depend on `gh` alone (NA-0009)."""
    text = (ROOT / "tests" / "test_intent.py").read_text(encoding="utf-8")
    i = text.index("def _descends_from_base_tip(")
    body = text[i: text.index("\ndef _living_tip(", i)]
    # main fb1f6a54: the helper routes through the shared classifier transport, which
    # (this PR) now includes the git-ancestry step, so no gh-only path remains.
    assert "_tdc._compare_status(base, sha)" in body
    assert 'in ("ahead", "identical", "behind")' in body
    src = (ROOT / "scripts" / "tip_drift_class.py").read_text(encoding="utf-8")
    assert "status = _git_compare_status(base, live, repo)" in src


def test_path_c_landed_reads_verify(tmp_path):
    good = tmp_path / "VERIFY.json"
    good.write_text(json.dumps({"path_c_landed": True}), encoding="utf-8")
    assert tdc.path_c_landed(good) is True
    bad = tmp_path / "VERIFY2.json"
    bad.write_text(json.dumps({"path_c_landed": "true"}), encoding="utf-8")
    assert tdc.path_c_landed(bad) is False
    assert tdc.path_c_landed(tmp_path / "missing.json") is False


def test_main_exit_codes(monkeypatch, capsys):
    _status(monkeypatch, "ahead")
    assert tdc.main([BASE, LIVE, "--landed"]) == 0
    assert capsys.readouterr().out.strip() == "DESCENDANT"

    monkeypatch.setattr(tdc, "path_c_landed", lambda *a, **k: False)
    assert tdc.main([BASE, LIVE]) == 1

    _status(monkeypatch, "behind")
    assert tdc.main([BASE, LIVE, "--landed"]) == 1

    _status(monkeypatch, "")
    assert tdc.main([BASE, LIVE, "--landed"]) == 2

    assert tdc.main([BASE, BASE]) == 0


def test_main_json_never_flips_research(monkeypatch, capsys):
    _status(monkeypatch, "ahead")
    assert tdc.main([BASE, LIVE, "--landed", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["class"] == "DESCENDANT"
    assert data["acceptable"] is True
    assert data["scientific_effect"] == "NONE"
    assert data["lemma_closed"] is False


def test_cli_rejects_bad_input_with_exit_2():
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tip_drift_class.py"), "nope", "alsonope"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 2
    assert p.stdout.strip() == "UNKNOWN"


def test_gates_carry_descendant_ok_and_keep_hard_fail():
    """Each wired gate mentions DESCENDANT_OK and still exits 1 on other drift."""
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("tip_drift_class.py") == 2
    assert "DESCENDANT_OK" in ci
    assert "::error::tip-drift: live hardening SHA" in ci

    refresh = (ROOT / "scripts" / "refresh_path_c_bundle.sh").read_text(encoding="utf-8")
    assert "TIP_DRIFT_DESCENDANT_OK" in refresh
    assert 'echo "refresh_path_c_bundle: dry-run TIP_DRIFT ${PRIOR_SHORT} -> ${LIVE_SHORT}' in refresh

    for rel in (
        "scripts/assert_path_c_ready.sh",
        "scripts/owner_open_path_c_pr.sh",
        "scripts/owner_land_path_c.sh",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "tip_drift_class.py" in text, rel
        assert "DESCENDANT" in text, rel

    for rel in (
        "scripts/path_c_dry_run.py",
        "scripts/write_path_c_status.py",
        "scripts/when_writable_land.py",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "tip_drift_class" in text, rel
        assert "tip_exact_match" in text, rel


def test_apply_all_0017_semantic_guard_present():
    text = (ROOT / "portable" / "patches" / "apply_all.sh").read_text(encoding="utf-8")
    assert '"$bn" == 0017-*' in text
    assert "already-applied (semantic)" in text


def test_guard_prefers_checkout_head_over_wrong_tip_sha(tmp_path):
    """A --tip-sha that is not the audited checkout's HEAD must not be stamped."""
    import guard_no_status_promotion as g  # noqa: PLC0415

    repo = tmp_path / "co"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", repo], check=True)
    subprocess.run(["git", "-C", repo, "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"], check=True)
    head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    assert g._git_head_sha(repo) == head
    src = (ROOT / "scripts" / "guard_no_status_promotion.py").read_text(encoding="utf-8")
    assert "using HEAD (tip_sha must describe the audited tree)" in src
