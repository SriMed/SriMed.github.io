from datetime import datetime
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.publication import ROOT, TIMEZONE, publication_plan, render
from scripts.reading import write_include


@unittest.skipUnless(shutil.which("quarto"), "Quarto is required for the rendering integration test")
class RenderTests(unittest.TestCase):
    def test_future_post_is_hidden_then_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("_quarto.yml", "theme.scss", "resume.pdf", "index.qmd", "about.qmd", "writing.qmd", "content.qmd"):
                shutil.copy2(ROOT / name, root / name)
            write_include([], root)
            post = root / "posts" / "scheduled" / "index.qmd"
            post.parent.mkdir(parents=True)
            post.write_text('---\ntitle: "Scheduled test essay"\ndescription: "Test description"\ndate: "2027-07-12"\ndraft: false\n---\n\nSCHEDULED_BODY_SENTINEL\n')
            for hour, visible in ((7, False), (8, True), (7, False)):
                with self.subTest(hour=hour, visible=visible):
                    state, hidden = publication_plan(root, datetime(2027, 7, 12, hour, tzinfo=TIMEZONE))
                    render(root, state, hidden)
                    output = root / "_site"
                    self.assertEqual(json.loads((output / "publication-state.json").read_text()), state)
                    self.assertFalse((root / "_quarto-publication.yml").exists())
                    for name in ("writing.html", "search.json", "writing.xml", "sitemap.xml"):
                        self.assertTrue((output / name).exists(), name)
                        self.assertEqual("posts/scheduled" in (output / name).read_text(), visible, name)
                    content = "\n".join(path.read_text(errors="ignore") for path in output.rglob("*") if path.is_file())
                    self.assertEqual("SCHEDULED_BODY_SENTINEL" in content, visible)


if __name__ == "__main__":
    unittest.main()
