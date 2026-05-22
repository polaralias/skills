# Scene runtime rules

Use this file when scenes are executed one at a time across separate turns.

## Global rules

- Treat every scene prompt as standalone.
- Frames are authoritative for timing.
- Approved source stills are authoritative for illustrated placement.
- Real recordings are authoritative for walkthrough scenes.
- If continuity with a previous scene matters, inspect the previous scene's ending frame before building the next one.

## Continuity check

When a scene depends on the prior scene:
1. review the ending frame of the prior scene
2. record the visible state
3. make frame 0 of the new scene a valid continuation unless a hard reset is intended

Check:
- wash or background tone
- visible branding
- residual overlays
- shell visibility
- motion density

## Illustrated preflight

Complete this before writing detailed illustrated animation:

1. open the approved still at full resolution
2. identify exclusion zones for people, landmarks, and dominant subjects
3. identify safe anchor zones for routes, cards, text beats, and hubs
4. record the coordinates
5. plan a debug composition that makes those assumptions visible
6. verify routes and labels against the still itself

## Walkthrough preflight

1. confirm the recording exists
2. confirm the intended crop or fit behaviour
3. confirm the shell geometry
4. confirm whether callouts or overlays are needed
5. confirm the entry and exit behaviour

## Canonical layer stacks

### Illustrated

Bottom to top:
1. base still
2. optional wash, vignette, or background effects
3. vector or overlay layer
4. branding layer
5. cards and text beats
6. optional finishing texture

### Walkthrough

Bottom to top:
1. backdrop wash
2. walkthrough shell and recording
3. sheen or shell effects if needed
4. branding layer
5. callout layer if used

## Verification assertions

### Illustrated

- exclusion and anchor zones were identified
- no overlay sits in a forbidden area
- text timings match the planned frame windows
- beats do not crowd each other
- final beat ends before scene end with enough breathing room
- debug renders were checked at full scale

### Walkthrough

- shell geometry is deliberate
- the recording is the real visual source
- crop or clipping behaviour is intentional
- callouts do not block key interaction evidence

## Common failure modes

- using half-scale renders and missing alignment issues
- trusting old coordinate comments instead of the current still
- letting a walkthrough recording start under a covering still without delaying playback
- clipping shadows or halos because of overflow behaviour
- shrinking scene duration without rechecking all keyframe ranges
- leaking a base layer through a multi-layer crossfade
