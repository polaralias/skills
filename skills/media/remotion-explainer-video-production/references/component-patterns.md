# Component patterns

These are reusable roles, not fixed branded implementations.

## Persistent scene primitives

### Brand corners

Use for persistent corner logos or identity marks.

Rules:
- keep them subtle
- place them consistently
- render them above scene content unless the intro sequence owns branding itself

### Grain overlay

Use only when the scene benefits from a tactile editorial finish.

Rules:
- keep it subtle
- use as a top layer in illustrated scenes
- avoid it in clean product walkthrough scenes unless the user explicitly wants a stylised treatment

### Intro sequence

Use for title or cold-open scenes where branding and framing need a controlled reveal.

Rules:
- let the intro own its own transitions
- do not duplicate persistent branding layers inside the intro unless intended

## Overlay families

### Route overlay

Use to show movement, connection, progression, or convergence across an illustrated scene.

Two useful weights:
- **heavy route** for architectural or road-like narrative paths
- **light route** for sketchy, diagrammatic, or multi-node flows

Choose one route style per scene.

### Arrival emphasis

Use at the endpoint of a route to show:
- destination
- convergence
- activation
- completion

### Radar or pulse effect

Use to give a hub, node, or destination a low-motion sense of activity without turning the scene into a glowing dashboard.

### Paper or editorial card

Use for labels, fragment explanations, role cards, or walkthrough callouts.

Rules:
- keep entry restrained
- prefer fade plus scale over jumpy motion
- use only light float
- keep the copy concise

### Text beat

Use for key thesis lines or emphasis statements.

Rules:
- time beats to meaningful spoken phrases or major visual beats
- avoid too many beats in one scene
- keep beat durations long enough to read comfortably
- use vignette or emphasis carefully so it supports rather than overwhelms

### Wavy banner or backdrop band

Use behind walkthrough callouts or grouped notes when a flat panel would feel too sterile.

## Debug composition

Every detailed illustrated scene should have a companion debug composition.

Include:
- base still
- grid
- crosshairs
- labelled anchor points
- candidate paths
- mask or exclusion outlines where relevant

Use the debug composition to verify placement before signing off the real scene.

## Walkthrough shell

Use for real product recordings.

Typical responsibilities:
- frame the recording
- provide a stable branded container
- support controlled crop, inset, and fade behaviour
- host callouts without fighting the recording

Rules:
- the real recording owns the main visual field
- do not overload the shell with unnecessary decoration
