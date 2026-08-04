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
        "point": {
            "cta": "https://go.ododok.app/ekfx7o",
            "headline": "食べているあいだに",
            "copy": "現金まで3ステップ",
            "images": {"../assets/app-home-jp-crop.png", "../assets/daram-spoon.png"},
        },
        "health": {
            "cta": "https://go.ododok.app/7ueukr",
            "headline": "あなたの噛み方は",
            "copy": "3つのタイプ、どれ？",
            "images": {"../assets/jp-report.png", "../assets/jp-home.png"},
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
                self.assertEqual(parser.lang, "ja")
                self.assertTrue(parser.viewport)
                self.assertIn(expected["headline"], html)
                self.assertIn(expected["copy"], html)
                self.assertGreaterEqual(parser.links.count(expected["cta"]), 2)
                self.assertTrue(expected["images"].issubset(set(parser.images)))
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

    def test_each_concept_has_motion_and_reduced_motion_fallback(self):
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn("@keyframes hero-float", html)
                self.assertIn("@keyframes cta-pulse", html)
                self.assertIn(".reveal", html)
                self.assertIn("prefers-reduced-motion: reduce", html)

    def test_health_rewards_match_the_live_policy_and_large_images_are_lazy(self):
        html = (ROOT / "jp" / "health" / "index.html").read_text(encoding="utf-8")
        for misleading_amount in ("月36,000円分", "月54,000円分", "月72,000円分"):
            self.assertNotIn(misleading_amount, html)
        self.assertIn("1日の上限は300どんぐり＝300円", html)
        self.assertGreaterEqual(html.count('loading="lazy"'), 2)


if __name__ == "__main__":
    unittest.main()
