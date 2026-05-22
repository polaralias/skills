# Company Context Pack Builder

This is a future-skill candidate.

## Why it is here

This is a reusable pattern:

- build a narrative context pack for a company
- build a commercial context pack for a company
- use both as supplementary context layers for other skills

## What seems reusable

- narrative context as a durable doctrine layer
- commercial context as a durable buyer and market layer
- explicit boundaries between qualitative guidance and confidential data
- reference-map structure that lets another skill load only the relevant context
- prompt examples that show how to invoke the pack safely

## Likely public version

A future public skill could be one of:

- `company-context-pack-builder`
- `company-narrative-context-builder`
- `company-commercial-context-builder`

The most likely useful public version is a combined builder that creates:

- a narrative-context pack
- a commercial-context pack
- a boundary/usage guide explaining when they should only act as supplementary context

## What it should do

- turn company source material into structured context packs
- separate doctrine, positioning, terminology, buyer roles, and market signals
- enforce confidentiality boundaries
- forbid invented numbers, private targets, or unsupported claims
- make the resulting packs usable by downstream writing, planning, and messaging skills

## Why this belongs here

- the pattern is useful, but the best version should be built as a standalone public skill
- the value is in the structure and boundaries, not any one company profile
- it is better treated as a builder than as a static pack
