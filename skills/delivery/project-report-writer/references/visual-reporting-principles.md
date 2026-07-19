# Visual reporting principles

Use this file for visual-specific rules. It should preserve the strong reporting method and component logic without collapsing back into the earlier branded renderer identity.

## Component palette

Treat the deck as a component sequence rather than a fixed slide template.

Useful slide components include:

- `cover`
- `overview`
- `timeline`
- `risks`
- `two_column_lists`
- `signal_actions`
- `editorial_split`
- `narrative`
- `kpi_strip`
- `checklist_strip`

Component selection guide:

- `cover`: opening slide with status, headline, and key framing signals
- `overview`: narrative summary with a supporting evidence rail or metric strip
- `timeline`: dated milestones, launch windows, decision gates, phase sequences, or any story where timing is central
- `risks`: blockers, dependencies, and likely failure points
- `two_column_lists`: paired dependencies, decisions, actions, or compare-and-contrast views
- `signal_actions`: evidence-source summary with actions and a bottom line
- `editorial_split`: interpretation-led reporting with a fact rail
- `narrative`: simple headline plus body plus optional callout for lighter editorial treatment
- `kpi_strip`: compact metric row for a small number of cards
- `checklist_strip`: readiness checks, gate sequences, or compact operational ladders

Rules:

- Pick the component that best preserves the evidence.
- Reuse components as needed when the report is long.
- Keep the order narrative and evidence-led.
- If the report is time-bound, the slide mix should usually include a timeline.
- Omit the timeline only when dates are incidental or not material to the story.
- Do not force the pack to stop at a small fixed slide count if the story needs more space.
- If content will not fit, split it into more slides.
- Review the full deck as a contact sheet before handoff and fix any clipped, blank, empty, duplicated, or partially stripped slide content first.

## Layout principles

- Think **editorial briefing**, not software dashboard.
- Prefer asymmetry, hierarchy, and whitespace over repeated equal-width panels.
- Avoid the generic `3 equal cards in a row` pattern unless the content truly demands it.
- Use cards only when they clarify hierarchy. Otherwise use open layout, ruled separators, or grouped text.
- Keep slide content scannable. A slide should land one idea, not a full report chapter.
- Keep widths contained. Do not let text stretch edge-to-edge on wide screens.
- Reserve vertical space above any bottom binding so no panel, chip, or paragraph runs underneath it.
- Avoid floating control pills that overlap the lower edge of a slide.

## Style stance

- Treat the output like an editorial leadership briefing, not a dashboard demo.
- Prefer one strong structural move per slide.
- Keep colour hierarchy disciplined.
- Avoid purple-neon accents, fake app chrome, floating glass panels, or decorative widgets.
- Use executive language, not technical diary notes.
- Put the interpretation upfront.
- Prefer evidence over enthusiasm.
- Avoid claiming ROI where there is no baseline.
- Mark assumptions clearly.

## Theme and brand separation

Keep branding mode separate from theme.

Theme may change:

- background treatment
- contrast and text-colour strategy
- panel, rule, and divider styling
- the amount of tint used versus open space

Brand mode may change:

- accent colours
- selected panel fills
- chips, dividers, and progress punctuation

What stays fixed:

- the editorial layout stance
- executive readability
- restrained hierarchy
- portability

## Timeline identity

The timeline should remain one of the strongest available visual moves when the reporting story depends on gates, milestone slippage, launch windows, or phased progress.

Good timeline behaviour:

- make the current position obvious
- distinguish complete, active, at-risk, and future states clearly
- preserve gate logic rather than flattening everything into equal events
- work as a narrative slide, not as a decorative flourish

Keep the timeline important as a method, but make it look different from the old report family.

## Slide architecture

Default to the smallest deck that preserves the story. Four to six slides is common for concise updates, but do not force a fixed length.

Useful content patterns:

1. Overview
2. Progress and milestone path
3. Blockers and risks
4. Dependencies and decisions
5. Next actions and bottom line

Hard rule:

- Every slide must read as a static slide with no page scroll and no internal slide scroll at the target desktop viewport.
- If the evidence needs more room, add slides rather than cramming content into a fixed count.
- If the desktop content does not fit cleanly, reduce copy, tighten the layout, or add another slide.

## What not to do

- no fake charts with invented numbers
- no lorem ipsum or placeholder labels
- no filler subtitles
- no repeated footer branding
- no cluttered legends, chrome, or presentation toys
- no generic styled HTML file when the user asked for a real visual report
- no recreation of the former branded report appearance just because the component pattern is similar
