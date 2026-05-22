---
name: project-support
description: Orient, validate, and route real project work before a more specialised
  project skill takes over. Use when the user needs help deciding whether something
  is a true project, locating or checking PROJECT.md, validating project lookup metadata,
  or choosing the next appropriate project-management skill.
metadata:
  author: James Whelan
  version: 0.1.0
  updated: '2026-05-21'
---

# Project Support

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `project-support was used in this response.`


Use this as the orientation and routing layer for project-management work that needs judgement before execution.

## Reference files

- [PROJECT-MD-SPEC.md](./references/PROJECT-MD-SPEC.md) is the canonical `PROJECT.md` contract
- [PM-GUARDRAILS.md](./references/PM-GUARDRAILS.md) holds the operating guardrails and routing posture

## What this skill is for

- deciding whether the work is really a project or programme
- finding the canonical `PROJECT.md`
- checking whether the lookup chain and context layer are healthy
- surfacing missing foundations, contradictions, or stale context
- routing to the correct specialised project skill

## Lookup sequence

1. decide whether the work is substantial enough to merit a canonical project context layer
2. look for the control-plane anchor or index mapping
3. use `project_context_path` if it exists
4. otherwise search the relevant project or customer folder for `PROJECT.md`
5. if workspace navigation matters, look for `SPACE.md`
6. use the discovered canonical files to orient the rest of the work

## If the canonical layer is weak

When `PROJECT.md` is missing, stale, contradictory, or structurally weak:

- say so directly
- do not pretend scattered fragments are already canonical truth
- route to `project-context-builder` when the project deserves one canonical file

## Routing rules

### Route to `project-context-builder`

When the job is to create, reconcile, or refresh canonical project truth.

### Route to `project-packager`

When the user needs a derivative package, handoff, or context bundle.

### Route to `project-report-writer`

When the user needs reporting, narrative status synthesis, or a health-style view.

### Route to `clickup-project-plan-builder`

When the project truth is stable and the next job is to shape a ClickUp planning surface.

## Support stance

- prefer authoritative artifacts over chat memory
- treat `PROJECT.md` as canonical for real projects
- treat boards as execution evidence rather than full project truth
- call out weak scope, missing owners, unrealistic dates, hidden dependencies, and contradictory status signals
- keep durable context separate from changing status
- be explicit when the setup is not sound enough yet

## Likely outputs

This skill usually returns:

- a concise orientation summary
- a health or setup check on the control-plane metadata
- a list of project-context gaps or risks
- a recommendation for the next project skill
- lightweight project-management advice grounded in the canonical context

## Do not

- replace the specialist skills when the user clearly needs one of them
- duplicate full project truth into an index entry
- assume `SPACE.md` exists
- force project ceremony onto BAU work
- overwrite stable project context during routine support

## Refresh rule

If the canonical context or its index entry looks stale, use edit tools where available. Otherwise tell the user exactly what should be updated and where.
