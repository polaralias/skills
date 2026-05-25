---
name: project-packager
description: Turn an existing PROJECT.md into audience-specific or system-ready project outputs without rediscovering the project from scratch. Use when the project truth already exists and the user needs a reusable package, briefing, handoff, or derivative context artifact. Shorthand PKG.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.2.1
  updated: '2026-05-25'
---

# project-packager

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `project-packager was used in this response.`


This skill starts from `PROJECT.md` and repackages established project truth for a particular audience or downstream workflow. It should change framing and presentation, not quietly redefine the project.

Use [references/PROJECT-MD-SPEC.md](./references/PROJECT-MD-SPEC.md) as the contract for what can be treated as canonical and when write-back is justified.

## Entry conditions

Use this skill only when a canonical `PROJECT.md` already exists or can be found confidently.

If the user only has notes, briefs, PRDs, or scattered documents, route to `project-context-builder` first.

If a relevant `SPACE.md` exists, use it to improve workspace-aware packaging. If not, continue and note the limitation only when it matters.

## What packaging means

Packaging is about producing a fit-for-purpose derivative output:

- leadership summary
- kickoff brief
- project charter
- tool or board handoff
- agent context bundle
- document-ready brief

It is not a re-discovery pass and it is not a board-sync operation.

## Safe-repeat rule

This skill should be safe to run repeatedly.

- do not duplicate artifact listings
- do not pile on repeated boilerplate
- do not rewrite stable sections casually
- write back to `PROJECT.md` only when the packaging run reveals a real durable change

## Working flow

### 1. Confirm the canonical source

Find `PROJECT.md`, read the maintenance note, and check whether the file is current enough to package from.

If the file is missing, clearly incomplete, or materially contradictory, send the work back to `project-context-builder`.

### 2. Define the packaging target

Clarify:

- the audience
- the output type
- whether the result is human-facing, agent-facing, or tool-facing
- whether any supporting artifacts need to travel with it

### 3. Read with layer discipline

Use the spec to distinguish:

- stable context vs changing delivery state
- agreed scope vs future possibility
- made decisions vs pending decisions
- dependencies vs owned work
- risks vs active issues
- committed dates vs aspirational dates

### 4. Produce the derivative output

Create the requested package from `PROJECT.md` plus any clearly relevant supporting material.

Do not fabricate certainty. Do not flatten distinctions just because a cleaner story would read better.

### 5. Write back only when justified

Update `PROJECT.md` only when the packaging run uncovers a durable change such as:

- corrected milestone shape
- a meaningful shift in current state
- a resolved or newly material open question
- a project-level decision
- improved navigation or retrieval metadata
- corrected canonical storage or registry detail

If nothing durable changed, say that the package was derived without modifying the canonical context.

### 6. Validate consistency

Before finishing, ensure:

- `PROJECT.md` still makes sense if you updated it
- current state, milestones, RAID, and next actions remain aligned
- artifact entries are still deduplicated and searchable
- the derived package does not misrepresent the canonical file

## Common packaging targets

### Leadership summary

A compressed view of objective, status, decisions, risks, and next moves.

### Project charter

A stakeholder-ready narrative version of the project shape.

### Kickoff brief

A practical team handoff covering roles, milestones, dependencies, and immediate actions.

### ClickUp planning handoff

A structured planning handoff that preserves hierarchy, scope boundaries, milestones, dependencies, tags, and view logic without creating tasks directly.

### Agent context bundle

A compact downstream package that keeps `PROJECT.md` central while pointing clearly to the key supporting artifacts and, where relevant, `SPACE.md`.

### Document-ready handoff

A structured brief for another writing or planning skill so it does not need to rediscover the project.

## Composition rules

Use adjacent skills rather than reproducing them:

- `project-context-builder` when the canonical file is missing or weak
- `clickup-project-plan-builder` when the next task is board or hierarchy design
- downstream task builders only for actual task creation

## Planning handoff specifics

When packaging for ClickUp planning:

- preserve whether the structure should be workstream-first or feature-first
- keep governance, workshops, milestones, and execution lanes distinct
- recommend the shared project tag plus branch tags pattern where appropriate
- make view logic explicit rather than leaving it implied
- preserve milestone visibility in the handoff
