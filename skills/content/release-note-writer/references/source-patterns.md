# Source patterns

Use this file to preserve the method behind the skill without tying it to any specific tracker, document platform, or release process.

## Pattern A — implementation-linked source

The source includes linked implementation tasks, tickets, or shipped work items.

Use these for:
- shipped behaviour
- feature scope
- UI changes
- roles affected
- rollout or quality caveats when clearly supported

## Pattern B — documentation-led source

The source is a structured planning, design, or knowledge transfer document that references implementation work.

Use the document for:
- feature framing
- summary
- benefits
- considerations

Use the linked implementation work for:
- shipped behaviour
- actual delivered scope
- UI changes
- final technical accuracy

If the document and implementation detail diverge, prefer the implementation detail for what actually shipped.

## Pattern C — framing prose only

The source contains enough structured prose to support a credible release note without linked implementation detail.

Use it directly, but avoid overclaiming. Missing detail should remain `[TODO]`.

## Pattern D — empty or stub

The source is empty, boilerplate, or too thin to support a useful note.

Do not draft from it. Report it as a gap instead.

## Mapping guidance

Map source material like this:

- title or heading -> lead app name and feature name
- summary or introduction -> feature description
- value statements -> `Feature benefits`
- rollout state or release type -> `State`
- product areas or surfaces touched -> `Affected applications`
- capability details -> `UI changes`
- user roles or audiences -> `Roles affected`
- caveats, trade-offs, or rollout conditions -> `Important considerations`
- owner, document link, source reference, or audience context -> `More information`
