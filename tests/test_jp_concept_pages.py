#!/usr/bin/env python3
"""Static contracts for the two Japanese landing-page experiments."""

from html.parser import HTMLParser
from pathlib import Path
import re
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
        "point": {
            "lang": "ja",
            "cta": "https://go.ododok.app/ekfx7o",
            "headline": "一日3回の食事が",
            "copy": "現金まで3ステップ。",
            "images": {"../assets/app-point.png", "../assets/daram-spoon.png"},
            "source_marker": 'data-source-section="9a"',
        },
        "health": {
            "lang": "ja",
            "cta": "https://go.ododok.app/7ueukr",
            "headline": "いま、何回噛んだっけ？",
            "copy": "早食いが気になる理由。",
            "images": {
                "../assets/app-report.png",
                "../assets/daram-spoon.png",
                "../assets/daram-trim.png",
            },
            "source_marker": 'data-source-section="8c"',
        },
    }

    def test_each_concept_has_a_mobile_japanese_page_and_only_its_cta(self):
        """Catches a missing route, crossed CTA, or non-mobile/non-Japanese page."""
        for concept, expected in self.CASES.items():
            with self.subTest(concept=concept):
                page = ROOT / "jp" / concept / "index.html"
                html = page.read_text(encoding="utf-8")
                parser = PageParser()
                parser.feed(html)
                self.assertEqual(parser.lang, expected["lang"])
                self.assertTrue(parser.viewport)
                self.assertIn(expected["headline"], html)
                self.assertIn(expected["copy"], html)
                self.assertGreaterEqual(parser.links.count(expected["cta"]), 2)
                self.assertTrue(expected["images"].issubset(set(parser.images)))
                self.assertIn(expected["source_marker"], html)
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

    def test_health_uses_the_zip_8c_confirmed_design(self):
        html = (ROOT / "jp" / "health" / "index.html").read_text(encoding="utf-8")
        self.assertIn("コンセプトA · 確定案（9aデザインシステム適用）", html)
        self.assertIn("これからはオディが数えます。", html)
        self.assertIn("噛んだ回数・食事の速さ・リズムを自動で記録し", html)
        self.assertNotIn("噛み方タイプ診断型", html)

    def test_both_live_pages_are_fully_japanese(self):
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIsNone(re.search(r"[가-힣]", html))

    def test_airbridge_sdk_and_events_are_concept_specific(self):
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn("airbridge.init", html)
                self.assertIn("createAirbridge", html)
                self.assertIn("__AIRBRIDGE__", html)
                self.assertLess(html.index("createAirbridge"), html.index("airbridge.init"))
                self.assertNotIn('<script src="https://static.airbridge.io/sdk/latest/airbridge.min.js"></script>', html)
                self.assertIn("ododokdev", html)
                self.assertIn("webToken", html)
                self.assertIn("utmParsing:true", html)
                self.assertIn("jp_landing_viewed", html)
                self.assertIn("jp_line_cta_clicked", html)
                self.assertIn("airbridge.events.wait", html)
                self.assertIn("airbridge.events.wait(1000,", html)
                self.assertNotIn('target="_blank"', html)
                self.assertIn("customAttributes", html)
                self.assertIn(f'concept: "{concept}"', html)
                self.assertIn("page_path", html)
                self.assertIn("cta_position", html)
                self.assertIn("utm_source", html)


if __name__ == "__main__":
    unittest.main()
