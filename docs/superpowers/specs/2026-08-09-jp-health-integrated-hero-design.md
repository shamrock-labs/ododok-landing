# Japanese Health Landing Integrated Hero

## Goal

Reduce first-screen confusion on `/jp/health/` by showing the user problem, the AirPods-based measurement method, and a visible product result in one continuous hero experience.

## Direction

Remove the current standalone hero that leads with chewing-count questions. Promote the existing AirPods measurement story to the first content section and redesign it as an integrated hero.

The copy borrows the tone and narrative structure of the referenced Apero Makuake page without reproducing its sentences: acknowledge an everyday behavior, avoid scolding or medical promises, preserve the enjoyment of eating, and frame measurement as a gentle opportunity to notice one's own eating style.

## Hero content

- Eyebrow: `食事には気をつけていても、「食べ方」までは気づきにくい。`
- Headline: `いつもの食事から、自分の「食べ方」が見えてくる。`
- Supporting copy: `AirPodsをつけて、いつもどおり食べるだけ。食べる速さや噛むリズムを自動で記録します。`
- Visual proof: retain the existing meal photograph, AirPods motion trace, measurement animation, and phone UI.
- Result copy: describe checking the meal afterward as a lightweight reflection, not a health diagnosis.

## Layout

- Keep the sticky Ododok header.
- Place the headline and supporting copy above the meal photograph.
- Keep the photo and motion trace immediately visible beneath the copy.
- Let part of the measurement-result panel appear near the first viewport boundary to signal that the page continues.
- Preserve the sticky LINE CTA and avoid adding a second competing hero CTA.

## Page flow

1. Integrated hero: problem, mechanism, and immediate proof.
2. Existing pain/context section.
3. Existing how-to, product proof, FAQ, and final CTA sections.

## Analytics

- Keep `data-analytics-section="hero"` on the integrated hero so historical section events remain comparable.
- Remove the separate `motion_explainer` section event because that content becomes part of the hero.
- Preserve LINE CTA and measurement interaction events.

## Verification

- Run the existing Japanese concept-page tests.
- Verify the mobile layout at 390 x 844 and a narrower 320 px viewport.
- Confirm the hero is readable without horizontal overflow and that the next content is visibly discoverable.
- Confirm the measurement animation and sticky LINE CTA still work.
