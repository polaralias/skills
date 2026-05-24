---
name: project-context-builder
description: Create or refresh the canonical PROJECT.md for a real project or programme. Use when scattered notes, files, chats, and board context need to be consolidated into one durable context layer that other people and agents can rely on. Shorthand PCB.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.1.0
  updated: '2026-05-24'
---

# project-context-builder

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `project-context-builder was used in this response.`


The output of this skill is `PROJECT.md`. That file is the durable project context layer and should be treated as the canonical project brief for ongoing work.

Use [references/PROJECT-MD-SPEC.md](./references/PROJECT-MD-SPEC.md) as the governing structure and validation contract.

## Why this skill exists

Projects accumulate truth in messy places: notes, decisions in chat, board items, transcripts, briefs, and uploaded documents. This skill turns that spread-out context into one maintained file that is stable enough for repeated reuse.

It is not a board-sync skill and it is not a PRD generator by default.

## Use it for

- creating a first canonical `PROJECT.md`
- folding new evidence into an existing `PROJECT.md`
- reconciling conflicting sources
- separating confirmed facts from inference and unknowns
- establishing a durable source of truth before packaging, planning, or reporting

## Do not use it for

- direct task creation
- Gantt production
- weekly reporting churn
- live board maintenance
- lightweight coordination work that does not merit a full project context layer

## Typical evidence sources

Useful inputs include:

- uploaded project documents
- user notes and meeting recaps
- board or workspace context
- decision threads from chat or collaboration tools
- existing briefs or overview documents
- an earlier `PROJECT.md`

If `SPACE.md` exists, use it to improve workspace navigation. If not, continue and simply note that workspace-specific lookup detail was limited.

## Working method

### 1. Gather authoritative inputs

Prefer evidence in this order:

- explicit user-provided files and notes
- named systems or connectors with relevant project material
- clearly related nearby artifacts
- current conversation context

Use first-party evidence wherever possible.

### 2. Build a truth map

Sort what you have into:

- confirmed project facts
- inferred structure
- open gaps
- contradictions
- stale or doubtful material

Do not smooth away disagreement. Preserve it explicitly.

### 3. Find the current canonical file if it exists

If `PROJECT.md` already exists:

- start from it
- update rather than replace unless it is badly malformed
- preserve the static-versus-dynamic split from the spec
- keep the decision log append-only in substance
- reduce churn instead of increasing it

### 4. Create or update the file

Follow the exact section order from the spec.

Hard rules:

- `PROJECT.md` is the main deliverable
- use the prescribed section order
- keep the static and dynamic layers distinct
- do not mirror board-level churn into the file
- refresh current-state content rather than stacking history
- keep decisions, assumptions, dependencies, risks, and open questions separate
- include retrieval metadata for important supporting artifacts
- record `SPACE.md` as `not created` if it does not exist
- preserve uncertainty rather than manufacturing confidence
- include the maintenance note described in the spec

### 5. Register the canonical path

Once the file exists:

- confirm that the canonical path is recorded under `project_context_path`
- if no registry entry exists, tell the user exactly where it should be recorded
- if tools allow direct updates, write both the file and the registration

This registration step is part of the job, not a nice-to-have.

### 6. Validate before handing back

Use the spec checklist. Pay particular attention to:

- a valid canonical path in metadata
- current `Last reviewed` information
- no duplicate artifact entries
- no contradictions across current state, milestones, RAID, and next actions
- retrieval clues for major supporting artifacts
- a file that remains durable rather than overstuffed with volatile detail

### 7. Recommend the next route

When useful, point to the next likely skill:

- `project-packager` for audience-specific derivative outputs
- `clickup-project-plan-builder` when the next job is turning truth into a planning surface
- focused follow-up to resolve open questions or contradictions

## Output stance

- `PROJECT.md` is the primary deliverable
- keep facts and inference distinct
- preserve open questions and contradictions
- write in durable language rather than meeting-note shorthand
- produce the thinnest honest file when evidence is limited
- keep live execution churn out of the canonical context
- preserve or add the maintenance note instructing future users or agents to refresh the file when the project truth materially changes
