#!/usr/bin/env python3
"""Static contracts for the two Japanese landing-page experiments."""

from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.lang = None
        self.viewport = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag == "img" and values.get("src"):
            self.images.append(values["src"])
        elif tag == "meta" and values.get("name") == "viewport":
            self.viewport = "width=device-width" in values.get("content", "")


class JapaneseConceptPagesTest(unittest.TestCase):
    CASES = {
        "point": {"cta": "https://go.ododok.app/ekfx7o", "headline": "食べているあいだに"},
        "health": {"cta": "https://go.ododok.app/7ueukr", "headline": "よく噛む"},
    }

    def test_each_concept_has_a_mobile_japanese_page_and_only_its_cta(self):
        """Catches a missing route, crossed CTA, or non-mobile/non-Japanese page."""
        for concept, expected in self.CASES.items():
            with self.subTest(concept=concept):
                page = ROOT / "jp" / concept / "index.html"
                html = page.read_text(encoding="utf-8")
                parser = PageParser()
                parser.feed(html)
                self.assertEqual(parser.lang, "ja")
                self.assertTrue(parser.viewport)
                self.assertIn(expected["headline"], html)
                self.assertGreaterEqual(parser.links.count(expected["cta"]), 2)
                other = "point" if concept == "health" else "health"
                self.assertNotIn(self.CASES[other]["cta"], parser.links)

    def test_each_concept_resolves_all_local_images(self):
        """Catches asset paths that break after nesting pages under concept routes."""
        for concept in self.CASES:
            with self.subTest(concept=concept):
                page = ROOT / "jp" / concept / "index.html"
                parser = PageParser()
                parser.feed(page.read_text(encoding="utf-8"))
                for src in parser.images:
                    if not src.startswith(("http://", "https://", "data:")):
                        self.assertTrue((page.parent / src).resolve().is_file(), src)


if __name__ == "__main__":
    unittest.main()
