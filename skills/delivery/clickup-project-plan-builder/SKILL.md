---
name: clickup-project-plan-builder
description: Design and build ClickUp project-planning structures, including hierarchy, tags, and saved views for Gantt-led or board-led delivery. Use when a user wants a project brief turned into a practical ClickUp planning surface rather than a generic task dump.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-05-21'
---

# ClickUp Project Plan Builder

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `clickup-project-plan-builder was used in this response.`


This skill translates a project into a workable ClickUp planning setup. The output is not just a list of tasks. It is the full planning surface: the right list or view strategy, a durable hierarchy, a clean tag model, and the views needed to run the work.

## Expected deliverable

The default output is:

1. a decision on where the plan should live
2. a task hierarchy built around the project shape
3. a tag pattern that supports focused views
4. a view manifest for day-to-day management
5. a short completion or handoff summary

When requested, this can also include a dataset for downstream Gantt export.

## Planning philosophy

The durable pattern is:

- structure around workstreams or meaningful lanes
- keep governance and delivery distinct
- use tags deliberately to support reporting and filtered Gantts
- treat views as part of the planning artifact
- treat ownership fields as meaningful planning data

Do not force every project into a rigid child-task template.

## First decision: where should the plan live?

Choose the planning surface before creating anything.

### Prefer a dedicated list when

- the project needs its own statuses or view defaults
- the structure is large enough to justify separation
- the plan will be reviewed as a standalone workstream
- a shared list would become noisy or confusing

### Prefer filtered views on an existing list when

- the project is one stream inside a stable shared planning list
- the existing list already has suitable fields and statuses
- tags can isolate the project cleanly
- adding another list would create unnecessary fragmentation

There is no rule that every project gets its own list.

## Inputs to confirm

Before building, gather or infer:

- target workspace, Space, Folder, or list context
- project name
- customer or programme name if relevant
- date boundaries or key milestones
- major workstreams, feature areas, or delivery lanes
- governance, workshop, and release needs
- whether a dedicated list is desired or an existing surface should be used
- any status model that must be preserved
- any tag conventions already in use

If the brief is too vague to produce a sound structure, stop and ask for clearer scope.

## Build sequence

### 1. Check capability

Inspect the available ClickUp write surface and decide what can be created directly. If lists or views cannot be created live, do not silently skip them. Build what you can and return an explicit setup manifest for the remainder.

### 2. Shape the hierarchy

Default structure:

- one parent representing the overall project or programme
- first-level branches for meaningful workstreams, features, governance lanes, workshops, or milestone lanes
- child tasks beneath those branches where detailed planning is useful

Avoid phase-first structures unless the project genuinely depends on them.

### 3. Define the tag model

Use tags only when they improve navigation or reporting.

Baseline pattern:

- one shared project tag applied across the whole plan
- one branch-specific tag wherever filtered views need to isolate a workstream or lane

Additional tags should exist only for a clear reporting or planning reason.

### 4. Define the views

Views are part of the planned output, not optional polish.

Typical dedicated-list set:

- `List`
- `Board`
- full-project `Gantt`
- filtered Gantts for major branches where useful

Typical shared-list set:

- one project-filtered Gantt using the shared project tag
- filtered workstream Gantts using branch tags
- optional filtered List or Board views

Define the target view set before creating it.

### 5. Handle statuses and fields

If you control the list, favor statuses that distinguish unscheduled work, planned work, active work, and done or milestone states.

If the plan lives in an existing shared list, adapt to the established status model unless there is a strong reason and explicit permission to change it.

Use ownership fields as real planning signals. Do not treat them as optional decoration.

### 6. Create and verify

Preferred order:

1. create the list if needed
2. create the top-level parent
3. create first-level branches
4. create child tasks
5. apply tags and field values
6. create the views
7. verify that hierarchy, tags, and views align

## Validation pass

Before finishing, confirm:

- the planning surface choice still makes sense
- the shared project tag exists across the plan
- branch tags exist wherever filtered views depend on them
- a full-project Gantt exists or is captured in the manifest
- governance, workshops, and milestones are not mixed into ordinary execution branches
- ownership is visible as a planning field
- no dedicated-list assumption was baked into a shared-list solution
- any blocked live actions are returned as an explicit setup manifest

## Handoffs

- Use a downstream Gantt export workflow when the user wants an Excel workbook or offline planning output.
- Use an implementation-specific planning skill only when the request is clearly for implementation delivery rather than general project planning.
