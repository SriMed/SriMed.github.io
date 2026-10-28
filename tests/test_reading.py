import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.reading import INCLUDE, date_label, public_readings, query_notion, write_include


def page(title="A reading", day="2026-10-27", show=True, link="https://example.com/article"):
    return {"properties": {
        "Title": {"title": [{"plain_text": title}]},
        "Authors": {"rich_text": [{"plain_text": "An author"}]},
        "Link": {"url": link},
        "Show on website": {"checkbox": show},
        "Date Read": {"date": {"start": day, "end": "2026-10-28"}},
        "Progress": {"select": {"name": "In Progress"}},
        "Notes": {"rich_text": [{"plain_text": "PRIVATE_SENTINEL"}]},
    }}


class ReadingTests(unittest.TestCase):
    def test_only_selected_public_fields_are_exported(self):
        archived = page("Archived")
        archived["archived"] = True
        rows = public_readings([page(), page("Private", show=False), archived])
        self.assertEqual(len(rows), 1)
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(rows))
        self.assertNotIn("properties", rows[0])

    def test_five_newest_with_stable_ties(self):
        pages = [page(f"Reading {i}", f"2026-10-{i:02}") for i in range(20, 28)]
        pages.append(page("A first alphabetically", "2026-10-27"))
        rows = public_readings(pages)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["title"], "A first alphabetically")
        self.assertEqual(rows[-1]["start"], "2026-10-24")

    def test_unsafe_links_fail_before_publishing(self):
        for url in ("javascript:alert(1)", "file:///private/file", "https://user:password@example.com"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                public_readings([page(link=url)])

    def test_html_is_escaped_and_dates_show_range(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_include(public_readings([page('<script>alert("x")</script>')]), root)
            html = (root / INCLUDE).read_text()
            self.assertNotIn("<script>", html)
            self.assertIn("&lt;script&gt;", html)
            self.assertIn("Oct 27–28, 2026", html)
            self.assertIn('rel="noopener noreferrer"', html)
            self.assertNotIn("reading-status", html)

    def test_api_filters_and_caps_before_fetching(self):
        with patch("scripts.reading.urllib.request.urlopen", return_value=io.BytesIO(b'{"results": []}')) as fetch:
            query_notion("secret", "00000000-0000-0000-0000-000000000001")
        payload = json.loads(fetch.call_args.args[0].data)
        self.assertEqual(payload["page_size"], 5)
        self.assertEqual(payload["filter"], {"property": "Show on website", "checkbox": {"equals": True}})

    def test_missing_activity_dates_show_neither_date_nor_status(self):
        for kind, progress in (("Podcast", "Done"), ("Podcast", "In Progress"), ("Video", "Done"), ("Video", "In Progress")):
            with self.subTest(kind=kind, progress=progress), tempfile.TemporaryDirectory() as directory:
                source = page()
                source["properties"]["Type"] = {"select": {"name": kind}}
                source["properties"]["Progress"] = {"select": {"name": progress}}
                source["properties"]["Date Read"] = {"date": None}
                root = Path(directory)
                write_include(public_readings([source]), root)
                html = (root / INCLUDE).read_text()
                self.assertNotIn("reading-status", html)
                self.assertIn(f"An author · {kind}</p>", html)
                self.assertNotIn("Publication date not recorded", html)
                self.assertNotIn("Oct", html)
                self.assertNotIn("My listening date not recorded", html)
                self.assertNotIn("My watching date not recorded", html)
                self.assertNotIn("reading-activity-date", html)

    def test_publication_and_personal_activity_dates_remain_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            source = page()
            source["properties"]["Published"] = {"rich_text": [{"plain_text": "2017-12-01"}]}
            root = Path(directory)
            write_include(public_readings([source]), root)
            html = (root / INCLUDE).read_text()
            self.assertIn("An author · Dec 1, 2017", html)
            self.assertIn('class="reading-activity-date">Read: Oct 27–28, 2026', html)

    def test_date_ranges_across_months_and_years(self):
        self.assertEqual(date_label("2026-10-27", "2026-11-02"), "Oct 27 – Nov 2, 2026")
        self.assertEqual(date_label("2026-12-31", "2027-01-02"), "Dec 31, 2026 – Jan 2, 2027")


if __name__ == "__main__":
    unittest.main()
