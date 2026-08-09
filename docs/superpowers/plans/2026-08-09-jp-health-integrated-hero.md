# Japanese Health Integrated Hero Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate Japanese health-page hero and AirPods explainer with one first-screen section that communicates the user insight, measurement method, and product proof.

**Architecture:** Keep the page as a single static HTML document and reuse the existing sensor animation, video, assets, analytics hooks, and responsive styles. Change only the health page markup/styles and its static contract tests.

**Tech Stack:** HTML, CSS, vanilla JavaScript, Python `unittest`

## Global Constraints

- Preserve the existing sticky LINE CTA and measurement interaction behavior.
- Keep `data-analytics-section="hero"` for historical comparison.
- Do not reproduce sentences from the Apero Makuake page.
- Avoid medical claims and prescriptive chewing targets in the hero.
- Support 320 px and 390 px mobile widths without horizontal overflow.

---

### Task 1: Lock the integrated-hero contract

**Files:**
- Modify: `tests/test_jp_concept_pages.py`

**Interfaces:**
- Consumes: static HTML from `jp/health/index.html`
- Produces: assertions for one integrated hero, approved Japanese copy, preserved sensor UI, and removed legacy hero copy

- [ ] **Step 1: Update the health fixture and hero-specific test**

Assert the new headline `いつもの食事から、自分の「食べ方」が見えてくる。`, the support copy beginning `AirPodsをつけて、いつもどおり食べるだけ。`, one `data-analytics-section="hero"`, no `motion_explainer`, and absence of `いま、何回噛んだっけ？`.

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python3 -m unittest tests.test_jp_concept_pages.JapaneseConceptPagesTest.test_health_uses_the_zip_8c_confirmed_design -v`

Expected: FAIL because the page still contains the legacy hero.

### Task 2: Build the integrated hero

**Files:**
- Modify: `jp/health/index.html`
- Test: `tests/test_jp_concept_pages.py`

**Interfaces:**
- Consumes: existing `.sensor-story`, `.sensor-photo`, `.measurement-panel`, `data-sensor-scene`, and measurement video behavior
- Produces: a single first content section marked as analytics section `hero`

- [ ] **Step 1: Replace the two-section markup with one section**

Use this copy hierarchy:

```text
「何を食べるか」は気にしても、「どう食べるか」は気づきにくい。
いつもの食事から、自分の「食べ方」が見えてくる。
AirPodsをつけて、いつもどおり食べるだけ。食べる速さや噛むリズムを自動で記録します。
```

Retain the meal photograph, trace animation, status pill, measurement count, and phone video inside the same section.

- [ ] **Step 2: Add hero-specific responsive styles**

Place the text in a warm-background intro above the photograph, left-align the explanatory copy, and keep the measurement panel visually connected to the photograph. At 320 px, allow natural wrapping while preventing overflow.

- [ ] **Step 3: Preserve analytics and renumber subsequent sections**

Keep the integrated section at `data-section-order="1"`, change the pain section to order 2, how-to to 3, product proof to 4, FAQ to 5, and final message to 6.

- [ ] **Step 4: Run the full static suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

### Task 3: Visual and behavior verification

**Files:**
- Verify: `jp/health/index.html`

**Interfaces:**
- Consumes: local static server output
- Produces: verified 390 x 844 and 320 x 720 screenshots with working sensor animation and CTA

- [ ] **Step 1: Serve the repository locally**

Run: `python3 -m http.server 4173`

- [ ] **Step 2: Inspect both mobile widths**

Confirm no horizontal overflow, readable Japanese line breaks, visible AirPods mechanism, measurement panel discoverability, sticky LINE CTA, and no console errors.

- [ ] **Step 3: Commit the implementation**

```bash
git add jp/health/index.html tests/test_jp_concept_pages.py docs/superpowers/plans/2026-08-09-jp-health-integrated-hero.md
git commit -m "feat: integrate JP health landing hero"
```
