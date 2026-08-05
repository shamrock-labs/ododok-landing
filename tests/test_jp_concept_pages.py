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
        self.assertIn("これからはオディが", html)
        self.assertIn("数えます。", html)
        self.assertIn("噛んだ回数・速さ・リズムを", html)
        self.assertNotIn("噛み方タイプ診断型", html)

    def test_both_live_pages_are_fully_japanese(self):
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIsNone(re.search(r"[가-힣]", html))

    def test_both_pages_share_mobile_safe_motion_and_line_groups(self):
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn("opacity:.15", html)
                self.assertIn("translateY(22px)", html)
                self.assertIn("1400ms cubic-bezier(.25,.1,.25,1)", html)
                self.assertIn("@keyframes hero-float", html)
                self.assertIn("7s ease-in-out infinite", html)
                self.assertIn("@keyframes cta-breathe", html)
                self.assertIn("5s ease-in-out infinite", html)
                self.assertIn("prefers-reduced-motion:reduce", html)
                self.assertIn("threshold:.08", html)
                self.assertIn("rootMargin:'0px 0px -4% 0px'", html)
                self.assertIn('class="semantic-line"', html)
                self.assertIn("word-break:auto-phrase", html)
                self.assertIn('class="token"', html)
                self.assertGreaterEqual(html.count('class="support-line"'), 4)
                self.assertNotIn("transition:all", html)

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

    def test_meta_pixel_base_code_is_installed_on_both_pages(self):
        """Catches a concept page that ships without PageView tracking."""
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn("connect.facebook.net/en_US/fbevents.js", html)
                self.assertIn("fbq('init',", html)
                self.assertIn("fbq('track','PageView')", html)
                self.assertIn("https://www.facebook.com/tr?id=", html)
                self.assertLess(html.index("fbq('init',"), html.index("fbq('track','PageView')"))
                self.assertNotIn('<script src="https://connect.facebook.net', html)

    def test_meta_pixel_id_is_real_and_identical_everywhere(self):
        """Catches a placeholder reaching production or an ID that drifts between the four copies."""
        found = []
        for concept in self.CASES:
            html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
            found += re.findall(r"fbq\('init','([^']+)'\)", html)
            found += re.findall(r"facebook\.com/tr\?id=([^&\"]+)&", html)
        self.assertEqual(len(found), 4, f"expected two pixel ID references per page, got {found}")
        self.assertEqual(len(set(found)), 1, f"pixel ID differs between copies: {sorted(set(found))}")
        # Meta object IDs have grown over time; bound the shape loosely, not to a fixed width.
        self.assertRegex(
            found[0],
            r"^\d{15,20}$",
            "Replace __META_PIXEL_ID__ with the real numeric Meta pixel ID in both concept pages.",
        )

    def test_line_cta_reports_a_meta_lead_without_blocking_navigation(self):
        """Catches a pixel call that can throw into the LINE handoff or lose CAPI deduplication."""
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn('try{fbq("track","Lead"', html)
                self.assertEqual(html.count('fbq("track","Lead"'), 1)
                self.assertIn("eventID:eventId", html)
                self.assertIn("event_id:eventId", html)
                # The navigation fallback must be armed before any tracking call can throw.
                self.assertLess(
                    html.index("setTimeout(navigate,1200)"), html.index('fbq("track","Lead"')
                )
                # The pixel reuses the existing wait window instead of adding its own delay.
                self.assertLess(
                    html.index('fbq("track","Lead"'), html.index("airbridge.events.wait")
                )

    def test_jp_root_router_stays_free_of_tracking(self):
        """Catches a pixel on the router, which would double-count PageView and slow the redirect."""
        html = (ROOT / "jp" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("fbq", html)
        self.assertNotIn("facebook", html)
        # fbclid must survive the redirect so _fbc is attributed on the concept page.
        self.assertNotIn('params.delete("fbclid")', html)

    def test_jp_root_is_a_stable_concept_router(self):
        """Catches regressions that expose the old point page or re-bucket on refresh."""
        html = (ROOT / "jp" / "index.html").read_text(encoding="utf-8")

        self.assertIn('const EXPERIMENT_ID = "jp_concept_v1"', html)
        self.assertIn('const VARIANTS = ["health", "point"]', html)
        self.assertIn('localStorage.getItem(STORAGE_KEY)', html)
        self.assertIn('localStorage.setItem(STORAGE_KEY, variant)', html)
        self.assertIn('globalThis.crypto.getRandomValues', html)
        self.assertIn('params.get("variant")', html)
        self.assertIn('params.delete("variant")', html)
        self.assertIn('params.set("experiment_variant", variant)', html)
        self.assertIn('params.set("assignment_source", assignmentSource)', html)
        self.assertIn('location.replace(destination.href)', html)
        self.assertIn('href="./health/"', html)
        self.assertIn('href="./point/"', html)
        self.assertNotIn("どんぐり1個 = 1円", html)


if __name__ == "__main__":
    unittest.main()
