"""Wake eligibility checks with all GitHub requests replaced by local fixtures."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "post_batch322_wake_comments.py"
SPEC = importlib.util.spec_from_file_location("wake_pr_state_subject", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
wake = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wake)


class WakePrStateTests(unittest.TestCase):
    def setUp(self):
        # No test may reach credentials or the network, even if API mocking regresses.
        for owner, attribute in (
            (wake, "token"),
            (wake, "resolve_wake_token"),
            (wake.urllib.request, "urlopen"),
        ):
            blocker = patch.object(
                owner, attribute, side_effect=AssertionError("live access forbidden")
            )
            blocker.start()
            self.addCleanup(blocker.stop)
        self.calls = []
        self.commented = []
        self.skipped = []
        self.urls = []
        self.output = io.StringIO()

    def run_target(
        self, payload, *, repo="d6g8k5htny-coder/main", number=36,
        comments=(), error=None,
    ):
        pull_path = f"/repos/{repo}/pulls/{number}"
        comment_path = f"/repos/{repo}/issues/{number}/comments"

        def fake_api(method, path, body=None):
            self.calls.append((method, path, body))
            if method == "GET" and path == pull_path:
                if error is not None:
                    raise error
                return payload
            if method == "GET" and path == comment_path + "?per_page=100&page=1":
                return list(comments)
            if method == "POST" and path == comment_path:
                return {"html_url": "https://github.com/comment/new"}
            raise AssertionError((method, path))

        with (
            patch.object(wake, "api", side_effect=fake_api),
            patch.object(wake, "_living_tip_short", return_value="abcdef0"),
            patch.object(wake, "_living_batch_n", return_value="999"),
            contextlib.redirect_stdout(self.output),
        ):
            wake._post_or_skip(
                number, repo=repo, tip="abcdef0", marker="Batch 999 wake @abcdef0",
                commented=self.commented, skipped=self.skipped, urls=self.urls,
            )

    def assert_only_state_read(self, repo="d6g8k5htny-coder/main", number=36):
        self.assertEqual(self.calls, [("GET", f"/repos/{repo}/pulls/{number}", None)])
        self.assertEqual(self.commented, [])
        self.assertEqual(self.urls, [])

    def test_closed_main_target_is_skipped_before_comment_read(self):
        self.run_target({"state": "closed", "merged": False})
        self.assert_only_state_read()
        self.assertEqual(len(self.skipped), 1)
        self.assertEqual(self.skipped[0]["pr"], 36)

    def test_merged_target_is_skipped_even_with_inconsistent_open_state(self):
        for state in ("closed", "open"):
            with self.subTest(state=state):
                self.calls.clear()
                self.run_target({"state": state, "merged": True})
                self.assert_only_state_read()
        self.assertEqual(len(self.skipped), 2)

    def test_open_target_with_older_wake_posts_current_task(self):
        self.run_target(
            {"state": "open", "merged": False},
            comments=[{"body": "Batch 1 wake @deadbee", "html_url": "old"}],
        )
        self.assertEqual([(m, p) for m, p, _ in self.calls], [
            ("GET", "/repos/d6g8k5htny-coder/main/pulls/36"),
            ("GET", "/repos/d6g8k5htny-coder/main/issues/36/comments?per_page=100&page=1"),
            ("POST", "/repos/d6g8k5htny-coder/main/issues/36/comments"),
        ])
        body = self.calls[-1][2]["body"]
        self.assertIn("**Batch 999 wake @abcdef0**", body)
        self.assertIn("keep `research/bands/ladder.py`", body)
        self.assertIn("lemma_closed=false", body)
        self.assertEqual(self.commented, [{
            "repo": "d6g8k5htny-coder/main", "pr": 36,
            "url": "https://github.com/comment/new",
        }])
        self.assertEqual(self.skipped, [])
        self.assertEqual(self.urls, ["https://github.com/comment/new"])

    def test_open_trial_target_preserves_same_tip_deduplication(self):
        self.run_target(
            {"state": "open", "merged": False}, repo="d6g8k5htny-coder/trial", number=114,
            comments=[{
                "body": "Batch 1 wake @abcdef0",
                "html_url": "https://github.com/comment/existing",
            }],
        )
        self.assertEqual([(m, p) for m, p, _ in self.calls], [
            ("GET", "/repos/d6g8k5htny-coder/trial/pulls/114"),
            ("GET", "/repos/d6g8k5htny-coder/trial/issues/114/comments?per_page=100&page=1"),
        ])
        self.assertEqual(self.commented, [])
        self.assertEqual(self.skipped[0]["reason"], "identical_living_tip_wake")
        self.assertEqual(self.urls, ["https://github.com/comment/existing"])

    def test_unknown_or_malformed_pull_state_refuses_before_comments(self):
        for payload in (
            None, [], {}, {"state": "open"},
            {"state": "unknown", "merged": False},
            {"state": "open", "merged": None},
            {"state": "open", "merged": "false"},
            {"state": "open", "merged": 0},
            {"state": ["open"], "merged": False},
        ):
            with self.subTest(payload=payload):
                self.calls.clear()
                with self.assertRaises(SystemExit):
                    self.run_target(payload)
                self.assert_only_state_read()

    def test_api_failure_refuses_before_comments(self):
        for error in (
            SystemExit("HTTP 403"), urllib.error.URLError("offline"),
            ValueError("invalid JSON"),
        ):
            with self.subTest(error=type(error).__name__):
                self.calls.clear()
                with self.assertRaises(type(error)):
                    self.run_target(None, error=error)
                self.assert_only_state_read()

    def test_trial_target_closed_after_open_listing_is_rechecked(self):
        def fake_api(method, path, body=None):
            self.calls.append((method, path, body))
            if (method, path) == ("GET", "/repos/d6g8k5htny-coder/trial/pulls?state=open&per_page=100"):
                return [{"number": 114, "title": "Engineering repair", "state": "open"}]
            if (method, path) == ("GET", "/repos/d6g8k5htny-coder/trial/pulls/114"):
                return {"state": "closed", "merged": True}
            raise AssertionError("Unexpected comment access: " + path)

        with (
            patch.object(wake, "api", side_effect=fake_api),
            patch.object(wake, "ENG", ()),
            patch.object(wake, "_living_tip_short", return_value="abcdef0"),
            patch.object(wake, "_living_batch_n", return_value="999"),
            patch.dict(wake.os.environ, {"GITHUB_STEP_SUMMARY": ""}),
            contextlib.redirect_stdout(self.output),
        ):
            self.assertEqual(wake.main(), 0)
        self.assertEqual(self.calls, [
            ("GET", "/repos/d6g8k5htny-coder/trial/pulls?state=open&per_page=100", None),
            ("GET", "/repos/d6g8k5htny-coder/trial/pulls/114", None),
        ])


if __name__ == "__main__":
    unittest.main()
