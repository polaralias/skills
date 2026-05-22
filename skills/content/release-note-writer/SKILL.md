---
name: release-note-writer
description: Write structured release notes from authoritative planning material,
  shipped implementation detail, and supporting documentation. Use when a user wants
  one or more product changes turned into concise, customer-facing release notes with
  stable structure, clear benefits, useful technical context, and explicit gaps where
  source material is incomplete.
metadata:
  author: James Whelan
  version: 0.1.0
  updated: '2026-05-21'
---

# Release Note Writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `release-note-writer was used in this response.`


Write polished, concise release notes from resolved source material.

This skill is source-resolution gated. Do not draft anything until the authoritative planning or feature source has been resolved and read.

## Output contract

This skill is the source of truth for the output format and writing rules.

Do not let live examples override the core contract:
- one release note entry per valid feature input
- the exact section order and section names from `references/output-template.md`
- the `## Lead app name: feature` heading format
- `[TODO]` placeholders for missing content
- empty or unusable source inputs are skipped and reported as gaps, never written as placeholder-only stubs

## Source model

Typical source inputs include:
- release planning documents
- feature summaries
- implementation tasks or tickets
- knowledge transfer documents
- design notes
- shipped-change summaries
- user-provided planning notes after source resolution

Treat implementation detail as the factual basis of what shipped. Earlier design or planning material can enrich the draft, but it should not override delivered behaviour when the two diverge.

## Source patterns

Classify each feature input before drafting:

### Pattern A — implementation-linked source

The source includes links or references to implementation tasks, tickets, or shipped work items.
- Action: resolve those inputs and use them as the factual basis for behaviour, scope, UI changes, and roles affected.

### Pattern B — documentation-led source

The source points to a structured design, planning, or knowledge transfer document that in turn references implementation detail.
- Action: resolve the document first, then resolve any linked implementation inputs.
- Use the document for framing and the implementation inputs for shipped behaviour.

### Pattern C — framing prose only

The source has substantial feature framing and scope explanation but no linked implementation detail.
- Action: write directly from that source.

### Pattern D — empty or stub

The source is empty, boilerplate, or too thin to support a credible note.
- Action: skip it and include it in the gap report.

## Workflow

Follow this sequence every time:

1. **Identify the resolution input**
   - Resolve the specific release source the user provided.
   - If multiple features are in scope, treat each viable feature input as its own draft unit.

2. **Resolve the authoritative source**
   This is a hard gate.
   - Read the authoritative planning, feature, or release source first.
   - If source resolution fails, stop completely. Do not draft from memory alone unless the user explicitly asks for a light draft.

3. **Classify each candidate input by pattern**
   - Scan the source and classify it into Pattern A, B, C, or D.
   - Record the classification so it can be surfaced in the gap report.

4. **Walk linked detail where required**
   - For Pattern A, resolve the implementation-linked source inputs.
   - For Pattern B, resolve the structured document, then any linked implementation inputs.
   - For Pattern C, use the framing prose directly.
   - For Pattern D, skip and report.

5. **Build a fact pack per valid feature**
   Capture:
   - lead app or product area
   - feature name
   - feature description
   - screenshot reference or `[TODO]`
   - user-facing benefits
   - state
   - affected applications or surfaces
   - UI changes
   - roles affected
   - rollout constraints, access conditions, trade-offs, or risks
   - owner or more-information reference when available
   - customer or audience context when available
   - video overview note when available

6. **Draft the note**
   Use the exact structure from `references/output-template.md`.

   Apply these rules:
   - the H2 must be exactly `Lead app name: feature`
   - the feature description paragraph must appear immediately after the H2
   - include `Screenshot: [TODO]` whenever no screenshot is provided
   - `Feature benefits` bullets must use the form `- **Title:** Explanation`
   - `Technical information` must contain these four lines in this order: `State`, `Affected applications`, `UI changes`, `Roles affected`
   - `Important considerations` is only for rollout constraints, access conditions, technical or UX trade-offs, implementation rationale, or risk
   - `More information` must contain these four lines in this order: `Owner`, `More information`, `Audience or customers`, `Video overview`
   - do not include actual video or prototype links on `Video overview`
   - use `[TODO]` for missing content
   - keep headings and body copy in sentence case
   - keep lists flat with no sub-lists

7. **Return the draft plus the gap report**
   - Show every drafted release note.
   - Then include a short gap report covering every skipped or weak input, including why it was skipped.

8. **Run the output check**
   Before returning, confirm:
   - every drafted note represents one valid feature input
   - no Pattern D input was drafted
   - the gap report is present and complete
   - each note follows the exact section order and H2 format
   - missing items use `[TODO]`
   - no nested lists and no raw implementation dumps

## Missing information policy

- If a field is still missing after source resolution, keep the section and use `[TODO]`.
- Do not omit required sections because data is missing.
- Do not pause for follow-up questions just to remove placeholders unless the user explicitly asks for a no-placeholder draft.

## Non-negotiables

- Do not draft before source resolution succeeds.
- Do not let early design intent outrank shipped implementation detail when they diverge.
- Do not draft placeholder-only entries for empty source inputs.
- Do not collapse multiple unrelated features into one release note.
- Do not dump raw task, ticket, or back-matter sections into the customer-facing body.
- Do not invent benefits, rollout conditions, audience details, or technical facts.
- Do not quote these instructions in the release note itself.

## Resources

- `references/output-template.md` contains the durable release-note template and placeholder conventions.
- `references/source-patterns.md` contains the reusable source-classification and mapping method.
