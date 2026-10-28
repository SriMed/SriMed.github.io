from datetime import datetime
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts.publication import TIMEZONE, needs_publication, publication_plan


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def post(self, slug, metadata):
        path = self.root / "posts" / slug / "index.qmd"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\n{metadata}\n---\nEssay body\n")

    def test_release_boundary_in_winter_and_summer(self):
        for month in (1, 7):
            with self.subTest(month=month):
                self.post(str(month), f'date: "2027-{month:02d}-12"\ndraft: false')
                path = f"posts/{month}/index.qmd"
                before = datetime(2027, month, 12, 7, 59, tzinfo=TIMEZONE)
                at_release = before.replace(hour=8, minute=0)
                self.assertIn(path, publication_plan(self.root, before)[1])
                self.assertIn(path, publication_plan(self.root, at_release)[0]["posts"])
                self.assertIn(path, publication_plan(self.root, at_release.astimezone())[0]["posts"])

    def test_drafts_remain_hidden_and_missed_dates_catch_up(self):
        self.post("draft", 'date: "2020-01-01"\ndraft: true')
        self.post("overdue", 'date: "2020-01-01"\ndraft: false')
        self.post("future", 'date: "2099-01-01"\ndraft: false')
        state, hidden = publication_plan(self.root, datetime(2026, 10, 18, 9, tzinfo=TIMEZONE))
        self.assertEqual(state, {"posts": ["posts/overdue/index.qmd"]})
        self.assertEqual(hidden, ["posts/draft/index.qmd", "posts/future/index.qmd"])

    def test_inherited_draft_and_explicit_override(self):
        self.post("draft", 'date: "2020-01-01"')
        self.post("ready", 'date: "2020-01-01"\ndraft: false')
        (self.root / "posts" / "_metadata.yml").write_text("draft: true\n")
        state, hidden = publication_plan(self.root, datetime(2026, 10, 18, 9, tzinfo=TIMEZONE))
        self.assertEqual(state["posts"], ["posts/ready/index.qmd"])
        self.assertEqual(hidden, ["posts/draft/index.qmd"])

    def test_invalid_dates_and_quoted_booleans_fail_closed(self):
        for metadata in ('date: "tomorrow"', 'date: "2027-02-30"', 'draft: "false"', 'date: 2027-01-01T09:00:00Z'):
            with self.subTest(metadata=metadata):
                path = self.root / "posts" / "invalid" / "index.qmd"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"---\n{metadata}\n---\n")
                with self.assertRaises(ValueError):
                    publication_plan(self.root, datetime.now(TIMEZONE))

    def test_unchanged_manifest_skips_and_new_due_post_builds(self):
        state = {"posts": ["posts/ready/index.qmd"]}
        with patch("scripts.publication.urllib.request.urlopen", return_value=io.BytesIO(json.dumps(state).encode())):
            self.assertFalse(needs_publication(state, "https://example.com/state.json"))
        with patch("scripts.publication.urllib.request.urlopen", return_value=io.BytesIO(b'{"posts": []}')):
            self.assertTrue(needs_publication(state, "https://example.com/state.json"))

    def test_reading_changes_trigger_update_without_new_essay(self):
        now = datetime(2026, 10, 27, 8, tzinfo=TIMEZONE)
        include = self.root / "_includes" / "reading.qmd"
        include.parent.mkdir()
        include.write_text("First selection")
        before = publication_plan(self.root, now)[0]
        self.assertEqual(publication_plan(self.root, now)[0], before)
        include.write_text("Changed selection")
        after = publication_plan(self.root, now)[0]
        self.assertNotEqual(before, after)
        self.assertEqual(before["posts"], after["posts"])

    def test_missing_manifest_bootstraps_but_server_failure_fails(self):
        for code in (404, 503):
            with self.subTest(code=code), patch(
                "scripts.publication.urllib.request.urlopen",
                side_effect=HTTPError("https://example.com", code, "error", {}, None),
            ):
                if code == 404:
                    self.assertTrue(needs_publication({"posts": []}, "https://example.com/state.json"))
                else:
                    with self.assertRaises(HTTPError):
                        needs_publication({"posts": []}, "https://example.com/state.json")


if __name__ == "__main__":
    unittest.main()
