---
name: remotion-explainer-video-production
description: Create illustrated, walkthrough, or hybrid explainer videos in Remotion
  using a multi-pass workflow. Use when a user wants scene prompts, composition plans,
  timing layouts, overlay systems, branded walkthrough shells, debug compositions,
  or full Remotion scene guidance for editorial explainer videos built from still
  images, screen recordings, or both.
metadata:
  author: James Whelan
  version: 0.1.0
  updated: '2026-05-21'
---

# Remotion Explainer Video Production

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `remotion-explainer-video-production was used in this response.`


Use this skill for Remotion-based explainer-video work that combines:
- illustrated scenes built on approved stills
- walkthrough scenes built on real product recordings
- hybrid scenes that split illustrated and walkthrough beats cleanly

Default to a multi-pass workflow:
1. define or refine the scene concept
2. generate or approve the still or recording source
3. build the Remotion composition
4. verify with full-scale debug renders

## First-use style rule

If this is the first time the skill is being used for production-ready output in the current environment, ask one short question before generating final compositions:

`Do you want me to keep the default explainer-video style, or tailor this skill with your own brand kit, typography, logos, colours, and component defaults first?`

If the user wants a custom style, update or create `references/brand-and-style.md` before producing final scene plans or composition guidance.

## Optional local override

If `references/brand-and-style.md` exists, read it before producing:
- scene prompts
- composition specs
- branding instructions
- typography rules
- logo placement rules
- colour assignments

Use it as the local style contract.

If it does not exist, continue with the generic editorial explainer style and do not invent brand-specific assets.

## Hard production rules

- Every composition must use a fixed canvas, not a responsive layout.
- Work in absolute pixel coordinates.
- Use frame numbers as the source of truth for timing.
- Verify illustrated overlays against the actual approved still, not memory or prior notes.
- Render debug compositions and full-scale stills before signing off detailed overlay placement.

## Core workflow

1. **Identify the scene type**
   Decide whether the requested beat is:
   - **illustrated**
   - **walkthrough**
   - **hybrid**

2. **Resolve the source plate**
   - For illustrated scenes: resolve the approved still or the prompt that will generate it.
   - For walkthrough scenes: resolve the actual product recording.
   - For hybrid scenes: resolve both and decide the split point.

3. **Read the shared guidance**
   - Read `references/workflow.md`.
   - Read `references/scene-runtime-rules.md`.
   - Read `references/component-patterns.md`.
   - If `references/brand-and-style.md` exists and is relevant, read that too.

4. **Choose the pass pattern**
   - **Pass 1**: still-image prompt or still-direction brief for illustrated scenes
   - **Pass 2**: Remotion composition plan
   - Walkthrough-only scenes skip Pass 1 and go straight to capture notes plus Pass 2

5. **Run illustrated preflight when needed**
   Before writing detailed composition code or specs for an illustrated scene:
   - inspect the still at full resolution
   - identify anchor zones and exclusion zones
   - create or plan a debug composition with grid and crosshairs
   - verify route starts, ends, labels, and cards visually
   - iterate until the coordinates are correct

6. **Build the composition plan**
   For each scene define:
   - composition ID
   - duration in frames and seconds
   - fps
   - width and height
   - layer stack
   - timing windows for text and motion beats
   - component choices
   - transition behaviour
   - source assets required

7. **Split hybrids cleanly**
   If a scene mixes illustration and walkthrough:
   - create one illustrated composition that exits to a clean wash
   - create one walkthrough composition that enters from the same wash
   - do not force both visual languages into one crowded composition

8. **Verify before sign-off**
   - render debug stills at full scale
   - render key real-scene frames at full scale
   - verify timing, safe text placement, route alignment, and continuity

## Default visual stance

If no local style override exists:
- use a calm editorial explainer feel
- prefer large graphic shapes over detailed clutter
- keep backgrounds readable and supportive of overlays
- use restrained motion rather than constant movement
- use route, card, and beat components to clarify narrative structure
- avoid dashboard-heavy or infographic-first compositions unless the user explicitly wants that

## Output expectations

When asked for production guidance, provide:
- a concise scene-by-scene plan
- pass structure where relevant
- exact timing windows in frames
- component and layer choices
- verification requirements

When asked for prompts, keep them self-contained and scene-specific.

When asked for code-level guidance, specify Remotion structures, composition registration, component usage, and verification steps rather than hand-waving at animation ideas.

## Non-negotiables

- Do not skip the debug-verification loop for illustrated overlay placement.
- Do not rely on previous-turn memory for shared production rules.
- Do not treat seconds as more authoritative than frames.
- Do not place overlays over assumed safe zones without checking the actual still.
- Do not mix illustrated and walkthrough language carelessly inside one scene when a split composition is cleaner.
- Do not invent brand assets, font names, or logo files without a local style reference.

## Resources

- `references/workflow.md` defines the multi-pass production workflow.
- `references/component-patterns.md` defines reusable component roles and overlay patterns.
- `references/scene-runtime-rules.md` defines continuity, preflight, layer-stack, and verification rules.
- `references/brand-and-style.md` is optional and should be used only when present and relevant.
