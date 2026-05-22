# Visual generation process

Use this file when the user wants a visual report, visual summary, slideshow, presentation, leadership-ready update, deck, or HTML-slide version of a project report.

This file is the source of truth for visual-generation workflow. Keep `SKILL.md` focused on reporting logic and use this file for the visual build process.

## Workflow

This is the full visual-report pathway. Do not treat it as a light formatting pass.

1. Finish the text report first.
2. Reduce the findings into one clear story arc.
3. Review any locally available example family or visual baseline before building.
4. Build a **single-file portable HTML deck** from the same evidence using structured slide data and component choices rather than freeform HTML.
5. Reject the file if the shell is incomplete, the slide payload does not match the story, or key visual scaffolding is clearly broken.
6. Render the deck to screenshots or a contact sheet so every slide can be reviewed in one pass.
7. Review the contact sheet for clipping, blank panels, missing hero content, empty component regions, duplicate slides, and footer overlap.
8. Verify the HTML renders cleanly before returning it.

The HTML deck is not a separate research pass. It is a visual retelling of the same findings already grounded in fresh comms, the project board, and supporting notes.

If the contact sheet shows blank content, empty component regions, clipped text, duplicate slides, or footer overlap, fix the payload or component choice and rerender before handing it back.
If the failure is isolated to one slide, regenerate that slide rather than abandoning the whole deck.

## Structured visual payload rules

- Build the deck as structured slide data, not as raw HTML first.
- Use a reusable slide/component system.
- Pick the smallest set of slides that tells the story clearly, but allow the deck to grow when preserving meaning matters more than brevity.
- If the data is best told as overview plus risks plus actions, do that.
- If milestones, gates, or launch dates genuinely drive the story, include a timeline component.
- Keep wording concise enough for slide reading at desktop width.
- If a component that requires core data renders empty, regenerate that slide with a better-fit component or corrected fields, rerender the deck, and rerun the screenshot check.

## Portable HTML rules

- Return one self-contained `.html` file when HTML is requested.
- Inline required fonts and imagery if the deck needs them.
- Do not depend on sibling asset files, CDNs, or web-hosted fonts.
- Keep CSS and JS in the same file unless the user explicitly asks for a multi-file bundle.
- If a footer binding is fixed to the viewport, make the content shell shorter to account for it rather than letting the footer cover the slide body.
- Do not ship scrolling slide containers at the desktop/default breakpoint. If a desktop slide needs more room, split it into more slides or tighten the layout.

## QA checklist

Before returning the HTML deck:

- confirm the text report already exists in chat
- confirm the deck tells the same story as the text report
- confirm branding mode was either left as default or explicitly agreed
- confirm there are no external font or CDN dependencies
- confirm the HTML still works offline
- confirm the slide content is readable at desktop width
- confirm every desktop slide is fully visible without page scroll or internal slide scroll
- confirm time-bound reports include a timeline slide when dates, gates, or launch windows matter
- confirm there is no horizontal overflow
- confirm there is no vertical overlap between the content and any fixed footer binding
- confirm navigation and progress indicators sit in a dedicated bottom binding rather than floating over slide content
- confirm the output reads like a serious internal or leadership briefing, not a generic dashboard

## Visual identity note

Carry across the useful discipline from the earlier report system, especially:

- timeline-led storytelling when timing is central
- strong separation between overview, risks, actions, and milestone path
- deliberate component choice rather than one repeated slide shell
- rigorous contact-sheet QA before handoff

Do **not** recreate the old branded visual language wholesale. The sanitised skill should keep the method and structural quality while producing a distinct visual style.
