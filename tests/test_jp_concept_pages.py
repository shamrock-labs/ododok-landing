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
        self.media_sources = []
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
        elif tag == "video":
            if values.get("poster"):
                self.images.append(values["poster"])
        elif tag == "source" and values.get("src"):
            self.media_sources.append(values["src"])
        elif tag == "meta" and values.get("name") == "viewport":
            self.viewport = "width=device-width" in values.get("content", "")


class JapaneseConceptPagesTest(unittest.TestCase):
    CASES = {
        "point": {
            "lang": "ja",
            "cta": "https://go.ododok.app/ekfx7o",
            "cta_count": 2,
            "headline": "一日3回の食事が",
            "copy": "食事から交換まで、",
            "images": {
                "../assets/app-point.png",
                "../assets/acorn-drop.png",
                "../assets/daram-spoon.png",
                "../assets/point-airpods-eating-v1.webp",
                "../assets/point-measurement-poster-v1.webp",
                "../assets/point-howto-prepare-v1.webp",
                "../assets/point-howto-eating-v1.webp",
                "../assets/point-howto-report-v1.webp",
                "../assets/point-howto-exchange-v1.webp",
            },
            "source_marker": 'data-source-section="9a"',
        },
        "health": {
            "lang": "ja",
            "cta": "https://go.ododok.app/7ueukr",
            "cta_count": 2,
            "headline": "いま、何回噛んだっけ？",
            "copy": "早食いが気になる理由。",
            "images": {
                "../assets/app-report.png",
                "../assets/daram-spoon.png",
                "../assets/daram-trim.png",
                "../assets/point-airpods-eating-v1.webp",
                "../assets/point-measurement-poster-v1.webp",
                "../assets/point-howto-prepare-v1.webp",
                "../assets/point-howto-eating-v1.webp",
                "../assets/point-howto-report-v1.webp",
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
                self.assertEqual(parser.links.count(expected["cta"]), expected["cta_count"])
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
                for src in parser.images + parser.media_sources:
                    if not src.startswith(("http://", "https://", "data:")):
                        self.assertTrue((page.parent / src).resolve().is_file(), src)

    def test_health_uses_the_zip_8c_confirmed_design(self):
        html = (ROOT / "jp" / "health" / "index.html").read_text(encoding="utf-8")
        self.assertIn("コンセプトA · 確定案（9aデザインシステム適用）", html)
        self.assertIn("これからはオディが", html)
        self.assertIn("数えます。", html)
        self.assertIn("食べるだけで、", html)
        self.assertIn("噛む動きを記録。", html)
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
                self.assertIn("@keyframes cta-breathe", html)
                self.assertIn("5s ease-in-out infinite", html)
                self.assertIn("prefers-reduced-motion:reduce", html)
                self.assertIn("threshold:.08", html)
                self.assertIn("rootMargin:'0px 0px -4% 0px'", html)
                self.assertIn('class="semantic-line"', html)
                self.assertIn("word-break:auto-phrase", html)
                self.assertIn('class="token"', html)
                self.assertNotIn("transition:all", html)

    def test_point_keeps_the_original_hero_then_explains_airpods_motion(self):
        html = (ROOT / "jp" / "point" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-floating-cta', html)
        self.assertIn('data-cta-position="sticky"', html)
        self.assertIn("setTimeout(()=>floatingCta.classList.add('is-idle'),3000)", html)
        self.assertIn("prefers-reduced-motion:reduce", html)
        self.assertIn("一食ごとに、どんぐりが貯まります", html)
        self.assertIn("ポイントになって", html)
        self.assertIn("どんぐり1個 = 1円相当", html)
        self.assertIn("一日3回の食事が", html)
        self.assertIn("../assets/app-point.png", html)
        self.assertIn('data-sensor-scene', html)
        self.assertIn("../assets/point-airpods-eating-v1.webp", html)
        self.assertIn("AirPodsで、ここまでできる。", html)
        self.assertNotIn("AirPodsで検知すると", html)
        self.assertNotIn('class="hero-support"', html)
        self.assertIn("<span class=\"semantic-line\">オディに聞いてみよう。</span>", html)
        self.assertIn("噛む回数の目安を自動で記録", html)
        self.assertIn(".sensor-photo::before", html)
        self.assertIn("height:76px", html)
        self.assertIn("grid-template-columns:minmax(0,1fr) 172px", html)
        self.assertIn("margin-top:-138px", html)
        self.assertIn("@keyframes sensor-capture", html)
        self.assertIn('class="trace-backdrop"', html)
        self.assertIn('class="trace-core"', html)
        self.assertIn("width:16px;height:24px", html)
        self.assertIn("stroke-dasharray:none", html)
        self.assertIn("stroke-dasharray:150", html)
        self.assertIn("stroke:#E85F24", html)
        self.assertIn("data-sensor-count>27", html)
        self.assertIn("sensorCount.textContent='30'", html)
        self.assertIn("if(count>=30)", html)
        self.assertIn("advanceCount", html)
        self.assertIn("},1450)", html)
        self.assertIn("setInterval(advanceCount,760)", html)
        self.assertIn("噛む動きを検知するたび、オディもどんぐりを食べます", html)
        self.assertNotIn("data-odi-bite", html)
        self.assertIn("sensorStarted=false", html)
        self.assertIn("sensorObserver.disconnect()", html)
        self.assertIn('<header class="site-header">', html)
        self.assertIn('>Ododok</a>', html)
        self.assertIn("font-family:'Apple SD Gothic Neo',sans-serif", html)
        self.assertIn("font-weight:800", html)
        self.assertIn("letter-spacing:.01em", html)
        self.assertIn('data-measurement-video muted playsinline preload="metadata"', html)
        self.assertIn("../assets/point-measurement-demo-v1.mp4", html)
        self.assertIn("../assets/point-measurement-poster-v1.webp", html)
        self.assertIn("animation:measurement-device-in 1400ms cubic-bezier(.25,1,.5,1) 1.35s both", html)
        self.assertIn("setTimeout(()=>playMeasurementVideo('autoplay'),2350)", html)
        self.assertIn("measurementPlay?.addEventListener('click',()=>playMeasurementVideo('manual'))", html)
        self.assertIn("Ododokって、どんなアプリ？", html)
        self.assertIn("何回噛んだかを自動で記録してくれるアプリだよ！", html)
        self.assertIn("でも、一食がどうやってポイントになるの？", html)
        self.assertIn("噛む回数や食事時間で変わるよ。まずは一食、一緒に始めてみよう！", html)
        self.assertIn("モーションセンサーに対応したAirPods", html)
        self.assertNotIn("食事時間と噛むリズムによって、貯まるどんぐりが変わるよ！", html)
        self.assertNotIn("今月の獲得見込み", html)
        self.assertNotIn("約2,400円", html)
        self.assertNotIn("直近7日のペースなら", html)
        self.assertEqual(html.count('src="../assets/acorn-drop.png"'), 3)
        self.assertNotIn("45どんぐり", html)
        self.assertNotIn("80どんぐり", html)
        self.assertNotIn("120どんぐり", html)
        self.assertIn("1週間の獲得イメージ", html)
        self.assertNotIn('class="reward-chart-total"', html)
        self.assertEqual(html.count('class="reward-chart-column"'), 7)
        self.assertIn('<b class="reward-chart-day">土</b>', html)
        self.assertIn('<b class="reward-chart-day">日</b>', html)
        self.assertNotIn("1日の上限は300どんぐり＝300円。", html)
        self.assertIn("どうやって噛む動きを記録するの？", html)
        self.assertIn("姿勢・回転・加速度の変化を解析", html)
        self.assertIn("音声や周囲の音は録音しません", html)
        self.assertIn("暗号化した通信でサーバーへ送信", html)
        self.assertIn("最長1年間保管", html)
        self.assertIn("バックグラウンドでも測定できますか？", html)
        self.assertIn("YouTubeなどほかのアプリを開いても", html)
        self.assertIn("<small>Q&amp;A</small>", html)
        self.assertEqual(html.count('class="faq-mark"'), 8)
        self.assertIn("フォローしてOdodokの", html)
        self.assertIn("https://x.com/ododok_jp", html)
        self.assertIn("https://www.instagram.com/hey.ododok_jp/", html)
        self.assertIn('data-social-channel="line"', html)
        self.assertEqual(html.count('class="social-app-icon"'), 3)
        self.assertIn('fill="#050505"', html)
        self.assertIn("Instagram_icon.png/250px-Instagram_icon.png", html)
        self.assertNotIn('id="instagram-app-gradient"', html)
        self.assertIn('fill="#06C755"', html)
        self.assertIn("jp_social_link_clicked", html)
        self.assertIn("© 2026 Ododok", html)
        self.assertNotIn("5,000どんぐり", html)
        self.assertNotIn("現金の受け取り方は？", html)
        self.assertNotIn("現金が貯まります", html)
        self.assertNotIn("口座へ", html)
        self.assertNotIn("© 2026 Odi", html)
        self.assertNotIn("data-motion-prototype", html)
        self.assertNotIn('data-cta-position="cta_2"', html)
        self.assertLess(html.index('data-analytics-section="hero"'), html.index('data-analytics-section="motion_explainer"'))
        self.assertLess(html.index('data-analytics-section="motion_explainer"'), html.index('data-analytics-section="reward_dialogue"'))

    def test_health_keeps_its_existing_hero_motion(self):
        html = (ROOT / "jp" / "health" / "index.html").read_text(encoding="utf-8")
        self.assertIn("@keyframes hero-float", html)
        self.assertIn("7s ease-in-out infinite", html)

    def test_health_shares_product_foundations_without_point_rewards(self):
        html = (ROOT / "jp" / "health" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<header class="site-header">', html)
        self.assertIn('data-floating-cta', html)
        self.assertIn('data-cta-position="sticky"', html)
        self.assertIn("setTimeout(()=>floatingCta.classList.add('is-idle'),3000)", html)
        self.assertEqual(html.count('<article class="howto-slide'), 3)
        self.assertEqual(html.count('<button type="button" data-howto-dot'), 3)
        self.assertIn("測定から振り返りまで、", html)
        self.assertIn("噛む回数と咀嚼テンポの目安を記録", html)
        self.assertIn("jp_howto_step_viewed", html)
        self.assertIn("どのAirPodsでも使えるの？", html)
        self.assertIn("姿勢・回転・加速度の変化を解析", html)
        self.assertIn("音声や周囲の音は録音しません", html)
        self.assertIn("バックグラウンドでも測定できますか？", html)
        self.assertEqual(html.count('class="faq-mark"'), 8)
        self.assertIn("https://x.com/ododok_jp", html)
        self.assertIn("https://www.instagram.com/hey.ododok_jp/", html)
        self.assertIn("jp_social_link_clicked", html)
        self.assertIn("© 2026 Ododok", html)
        self.assertIn('data-analytics-section="motion_explainer"', html)
        self.assertIn('data-sensor-scene', html)
        self.assertIn("AirPodsで、ここまでできる。", html)
        self.assertIn("噛む回数の目安を自動で記録", html)
        self.assertIn("data-sensor-count>27", html)
        self.assertIn("sensorCount.textContent='30'", html)
        self.assertIn("setInterval(advanceCount,760)", html)
        self.assertIn("../assets/point-measurement-demo-v1.mp4", html)
        self.assertIn("噛む動きを検知するたび、オディもどんぐりを食べます", html)
        self.assertNotIn("いつものAirPodsだけ", html)
        self.assertNotIn("追加デバイス0円", html)
        self.assertNotIn('class="hero-support"', html)
        self.assertNotIn("どんぐりを特典へ", html)
        self.assertNotIn("ポイント交換", html)
        self.assertNotIn('data-cta-position="cta_1"', html)
        self.assertNotIn('data-cta-position="cta_2"', html)

    def test_point_howto_is_a_four_step_accessible_swipe_carousel(self):
        html = (ROOT / "jp" / "point" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-howto-track', html)
        self.assertEqual(html.count('<article class="howto-slide'), 4)
        self.assertEqual(html.count('<button type="button" data-howto-dot'), 4)
        self.assertIn('scroll-snap-type:x mandatory', html)
        self.assertIn('scroll-snap-align:center', html)
        self.assertIn('aria-current="step"', html)
        self.assertIn("['ArrowLeft','ArrowRight']", html)
        self.assertIn("requestAnimationFrame", html)
        self.assertIn("jp_howto_step_viewed", html)
        self.assertNotIn("左右にスワイプ", html)
        self.assertIn("howtoAutoplayTimer", html)
        self.assertIn("},4200)", html)
        self.assertIn("stopHowtoAutoplay", html)
        self.assertIn("'pointerdown','touchstart','wheel','focusin'", html)
        self.assertIn("howtoDragging", html)
        self.assertIn("setPointerCapture", html)
        self.assertIn("'pointerup','pointercancel','lostpointercapture'", html)
        self.assertIn("cursor:grab", html)
        self.assertIn("howtoAutoplayStopped=reducedMotion", html)
        self.assertIn("document.addEventListener('visibilitychange'", html)
        self.assertIn("AirPodsをつけて準備", html)
        self.assertIn("いつもどおり食べる", html)
        self.assertIn("食べ方を振り返る", html)
        self.assertIn("どんぐりを特典へ", html)
        self.assertIn("噛む回数と咀嚼テンポの目安を記録", html)
        self.assertIn("※交換先・交換条件は変更となる場合があります。", html)
        self.assertNotIn("現金まで3ステップ。", html)
        self.assertNotIn('class="reward-yen"', html)
        self.assertNotIn(">45円<", html)
        self.assertNotIn(">80円<", html)
        self.assertNotIn(">120円<", html)

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

    def test_amplitude_tracks_the_concept_funnel_without_duplicate_pageviews(self):
        sdk = (ROOT / "jp" / "assets" / "amplitude.js").read_text(encoding="utf-8")
        self.assertIn("cdn.amplitude.com/script/", sdk)
        self.assertIn('serverZone: "US"', sdk)
        self.assertIn("sessionReplay.plugin({ sampleRate: 1 })", sdk)
        self.assertIn("pageViews: false", sdk)
        self.assertIn("elementInteractions: true", sdk)
        self.assertIn("frustrationInteractions: true", sdk)
        self.assertIn('window.addEventListener("pagehide"', sdk)
        self.assertIn('window.amplitude.setTransport("beacon")', sdk)

        required_events = {
            "jp_landing_viewed",
            "jp_line_cta_viewed",
            "jp_line_cta_clicked",
            "jp_section_viewed",
            "jp_scroll_depth_reached",
            "jp_measurement_demo_started",
            "jp_measurement_demo_completed",
            "jp_measurement_video_started",
            "jp_howto_step_viewed",
            "jp_social_link_clicked",
        }
        concept_events = {}

        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn('<script src="../assets/amplitude.js"></script>', html)
                self.assertIn('trackAmplitude("jp_landing_viewed"', html)
                self.assertIn('trackAmplitude("jp_line_cta_clicked"', html)
                self.assertIn('trackAmplitude("jp_section_viewed"', html)
                self.assertIn('experiment_id:"jp_concept_v1"', html)
                self.assertIn('landing_version:"jp_concept_v2"', html)
                self.assertIn("experiment_variant", html)
                self.assertIn("assignment_source", html)
                self.assertIn('environment=["ododok.app","www.ododok.app"]', html)
                self.assertIn('params.get("analytics_debug")==="1"', html)
                self.assertIn('console.debug("[Ododok Analytics]",eventName,JSON.stringify(eventProperties))', html)
                expected_sections = 6
                self.assertGreaterEqual(html.count("data-analytics-section="), expected_sections)
                self.assertIn("Promise.allSettled([amplitudeFlush,airbridgeFlush])", html)
                self.assertIn("const reachedScrollDepths=new Set()", html)
                self.assertIn("[25,50,75,90]", html)
                self.assertIn("const seenHowtoSteps=new Set()", html)
                self.assertIn("const seenVideoPlaybackTriggers=new Set()", html)
                self.assertIn("last_section:lastViewedSection", html)
                self.assertIn("max_scroll_depth_pct:maxScrollDepthPct", html)
                self.assertIn("playback_trigger:playbackTrigger", html)
                self.assertIn("scene_visible_at_playback:isElementMeaningfullyVisible(sensorScene)", html)
                self.assertIn("scene_visible_at_completion:isElementMeaningfullyVisible(sensorScene)", html)
                self.assertIn("navigation_method:navigationMethod", html)
                self.assertIn("reduced_motion:reducedMotion", html)
                concept_events[concept] = set(
                    re.findall(r'trackAmplitude\(["\'](jp_[^"\']+)', html)
                )
                self.assertTrue(required_events.issubset(concept_events[concept]))

        self.assertEqual(concept_events["health"], concept_events["point"])

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
        self.assertRegex(
            found[0],
            r"^\d{15,20}$",
            "Replace __META_PIXEL_ID__ with the real numeric Meta pixel ID in both concept pages.",
        )

    def test_line_cta_reports_meta_airbridge_and_amplitude_without_blocking_navigation(self):
        """Catches a tracker call that can throw into the LINE handoff or split correlation IDs."""
        for concept in self.CASES:
            with self.subTest(concept=concept):
                html = (ROOT / "jp" / concept / "index.html").read_text(encoding="utf-8")
                self.assertIn('try{fbq("track","Lead"', html)
                self.assertEqual(html.count('fbq("track","Lead"'), 1)
                self.assertIn("eventID:eventId", html)
                self.assertIn("event_id:eventId", html)
                self.assertIn('trackAmplitude("jp_line_cta_clicked",clickAttributes)', html)
                self.assertLess(
                    html.index("setTimeout(navigate,1200)"), html.index('fbq("track","Lead"')
                )
                self.assertLess(
                    html.index('fbq("track","Lead"'), html.index("airbridge.events.wait")
                )

    def test_jp_root_router_stays_free_of_tracking(self):
        """Catches tracking on the router, which would double-count and slow the redirect."""
        html = (ROOT / "jp" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("fbq", html)
        self.assertNotIn("facebook", html)
        self.assertNotIn("amplitude", html.lower())
        self.assertNotIn('params.delete("fbclid")', html)

    def test_korean_point_page_reuses_the_point_experience_with_korean_copy(self):
        page = ROOT / "kr" / "point" / "index.html"
        html = page.read_text(encoding="utf-8")

        self.assertIn('<html lang="ko">', html)
        self.assertIn("하루 세 번의 식사가", html)
        self.assertIn("식사부터 교환까지,", html)
        self.assertIn("자주 묻는 질문", html)
        self.assertIn("한 주 적립 예시", html)
        self.assertIn("도토리 1개 = 1원 상당", html)
        self.assertNotIn("도토리 1개 = 1엔 상당", html)
        self.assertNotIn('class="reward-chart-total"', html)
        self.assertEqual(html.count('class="reward-chart-column"'), 7)
        self.assertIn('<b class="reward-chart-day">토</b>', html)
        self.assertIn('<b class="reward-chart-day">일</b>', html)
        self.assertIn("Ododok이 뭐야?", html)
        self.assertIn("몇 번 씹었는지 자동으로 기록해주는 앱이야!", html)
        self.assertIn("그런데 한 끼가 어떻게 포인트가 돼?", html)
        self.assertIn("모션 센서를 지원하는 AirPods", html)
        self.assertNotIn("지금부터 지원", html)
        self.assertNotIn("오디도 냠!", html)
        self.assertIn('<span>120</span><img src="../../jp/assets/acorn-drop.png"', html)
        self.assertIn("setInterval(advanceCount,760)", html)
        self.assertIn("백그라운드에서도 측정되나요?", html)
        self.assertIn("YouTube 등 다른 앱을 열어도", html)
        self.assertNotIn("하루 최대 300도토리", html)
        self.assertIn("howtoDragging", html)
        self.assertIn("kr_landing_viewed", html)
        self.assertIn("kr_line_cta_clicked", html)
        self.assertIn('<script src="../../jp/assets/amplitude.js"></script>', html)
        self.assertIn('src="../../jp/assets/point-howto-report-v1.webp"', html)
        self.assertNotRegex(html, r"[ぁ-んァ-ヶ]")
        self.assertNotIn('class="reward-yen"', html)

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
