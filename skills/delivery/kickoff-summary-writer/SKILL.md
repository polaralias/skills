---
name: kickoff-summary-writer
description: Turn kickoff, discovery, or onboarding source material into an evidence-backed synthesis with traceable references, then package it for the right audience. Use when a user wants a kickoff summary, discovery recap, implementation overview, or similar synthesis from transcripts, notes, or mixed source packs. Shorthand KSW.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.1.0
  updated: '2026-05-24'
---

# kickoff-summary-writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `kickoff-summary-writer was used in this response.`


This skill always starts with synthesis. It should first build a traceable summary from the source pack and only then shape the final output for internal or external use.

## What it is for

Use it to:

- extract the practical project and customer picture from mixed source material
- keep claims traceable to source material
- surface gaps, uncertainties, and contradictions
- separate product feature signals from broader workflow or governance discussion
- produce the right audience version after the synthesis is agreed

It is an upstream synthesis skill, not a task-creation or board-building skill.

## Source handling

Accepted inputs include:

- raw transcripts
- notes or meeting summaries
- uploaded customer artifacts
- mixed source packs

Treat all user-provided source material as part of one synthesis pass unless the user asks to separate it.

Before extracting content, create a compact source register with:

- filename
- source type
- date if known
- locator approach used for citation
- working-text artifact if conversion was needed

For internal synthesis, use direct inline references in this form:

- `[ref: <filename> | <locator> | "<short quote>"]`

If sources disagree, preserve the conflict explicitly instead of smoothing it away.

## Audience gate

Before generating final documents, resolve the audience mode:

- internal
- external or shareable
- unclear

If the user has not made the audience explicit, ask a short audience question before generating final files.

Default rules:

- internal mode: internal synthesis only
- external/shareable mode: internal synthesis plus shareable overview, unless the user asks for only the shareable version
- unclear mode: ask before final generation

## Extraction pass

Extract the following groups and cite every populated field in the internal synthesis:

### Basic customer or programme context

- customer or organisation name
- lead contacts
- timing signals
- size, complexity, or tier clues
- go-live or launch targets

### Current-state picture

- current platform or process
- known pain points
- operating model
- compliance or reporting constraints

### Delivery and configuration needs

- integrations
- provisioning approach
- launch content needs
- branding needs
- admin footprint

### Priorities and constraints

- key challenges to solve
- deadlines
- risks and blockers
- explicit exclusions

### Feature and workflow signals

Classify mentions as:

- feature
- workflow or programme
- governance or reporting practice
- outcome or KPI
- ambiguous

Only confirmed feature rows should drive trainable scope.

### Training signals

Capture:

- preferred format
- cadence
- learner group
- trainer-led vs self-service cues

## Assumptions and inference checkpoint

Any assumption or inferred value remains provisional until the user confirms it.

Before generating files, present:

1. assumptions register
2. inference review
3. feature mapping review
4. proposed scope shortlist
5. audience confirmation if still unresolved

Wait for explicit sign-off before final file generation.

## Gap analysis

List every unresolved, unconfirmed, or not-discussed field and group the gaps as:

- blockers
- important
- nice to have

## Local-context pass

Make a best-effort attempt to read any bundled local guidance or feature references before final packaging. If that context is unavailable, note the limitation in the internal synthesis and lower confidence where appropriate rather than pretending validation occurred.

## Final outputs

If `{dummy-docx-skill}` exists, use it for the actual document build rules.

### Internal synthesis

Suggested structure:

1. source register
2. customer snapshot
3. extracted information
4. feature and workflow shortlist
5. training signals
6. gap analysis
7. recommended next steps

Rules:

- factual tone
- citation for every populated field
- no unconfirmed inference presented as fact

### Shareable overview

Suggested structure:

1. implementation summary
2. agreed or indicated scope
3. key decisions and working assumptions
4. risks, dependencies, and open items
5. immediate next steps

Rules:

- clean external tone
- no inline citations in the body
- no raw source quotes in the body
- uncertain items belong in assumptions or open items, not as facts

## Final checks

Before handing back files, confirm:

1. the internal synthesis cites every populated field
2. unresolved fields are marked clearly
3. feature mappings show confidence
4. gap analysis is tiered
5. external output contains no internal evidence formatting
6. unconfirmed assumptions were not promoted into fact
7. the user explicitly approved the confirmation checkpoint before file generation
