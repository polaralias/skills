# Remotion explainer workflow

## Multi-pass pattern

### Pass 1: source-image or visual-direction pass

Use this for illustrated scenes.

Goal:
- define the scene concept clearly
- specify the required visual read
- reserve negative space where text or overlays will sit
- forbid baked-in text or logos inside the still unless the user explicitly wants them

Keep the visual brief self-contained:
- scene concept
- environment or context
- composition rule
- style direction
- negative constraints
- hard text constraint where relevant

### Pass 2: composition pass

Use this for illustrated, walkthrough, and hybrid scenes.

For every composition specify:
- composition ID
- duration in frames and seconds
- fps
- width and height
- base plate
- layer stack
- component choices
- exact text wording and timing windows
- transition behaviour

### Walkthrough-only scenes

Skip Pass 1.

Instead provide:
- recording source
- crop or fit instructions
- shell treatment
- callout placement
- timing windows

### Hybrid scenes

Split into two adjacent compositions:
- illustrated exit composition
- walkthrough entry composition

Use a shared wash or transition tone to join them.

## Scene-type decision rules

Use **illustrated** when the scene should explain a concept, system, or transformation through a crafted editorial image.

Use **walkthrough** when the scene should show an actual interface, workflow, or product interaction.

Use **hybrid** when the concept needs both:
- a designed conceptual setup
- a real product demonstration

## Render workflow

Prefer local Remotion rendering.

Typical commands:

```bash
npx remotion render src/index.ts MyScene out/my-scene.mp4 --codec h264 --crf 10
```

Debug stills:

```bash
npx remotion still src/index.ts MyScene out/frame-120.png --frame=120 --overwrite
```

Preview during development:

```bash
npx remotion studio
```

## Production checklist

- base plate is the correct source still or recording
- composition registration matches intended duration and dimensions
- timing windows are specified in frames
- text matches the approved script or on-screen wording
- debug renders were produced for illustrated scenes
- walkthrough scenes use the real recording, not a mocked imitation
- hybrid scenes are split cleanly when needed
