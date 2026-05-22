---
name: training-plan-writer
description: 'Produce paired customer-facing training plans: a concise operational
  version and a more detailed facilitator-grade version. Use when a user needs training
  design built from agreed scope, customer objectives, and practical UAT or sandbox
  workflows rather than generic project-management content.'
metadata:
  author: James Whelan
  version: 0.1.0
  updated: '2026-05-21'
---

# Training Plan Writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `training-plan-writer was used in this response.`


This skill creates two related training outputs for the same audience and scope:

- a concise training plan for easy reference
- a detailed training plan with richer session and UAT guidance

These are training artifacts, not implementation plans in disguise. Do not let them accumulate unrelated project-management content.

## Suggested place in the workflow

Recommended sequence:

```text
kickoff-summary-writer
  -> implementation-plan-writer
  -> training-plan-writer
```

Run this after the implementation shape is understood, ideally with both synthesis and implementation-plan inputs available.

## Optional pedagogy layer

If a pedagogy-focused skill exists in the environment, apply it. Where it conflicts with generic defaults in this skill, the pedagogy guidance should win. If none exists, proceed with the default training structure and say so in the final summary.

## Input collection

### Best case: upstream documents exist

Extract from the synthesis and implementation-plan artifacts:

- customer name
- training lead or facilitator
- in-scope workflows and features
- training format
- cadence, session count, and session length
- learner group
- UAT or sandbox tenant name
- assignment or rollout model
- go-live date

Anything marked `[NOT DISCUSSED]`, `[inferred]`, or `[TBC]` should be confirmed before drafting.

### Direct-input route

If no upstream documents exist, ask for:

Required:

- customer name
- trainer name
- UAT or sandbox tenant
- go-live target
- in-scope features
- operating model and training objectives

Important:

- training format
- number and cadence of sessions
- session duration
- who will attend

Optional:

- blackout dates or delivery constraints
- explicitly excluded features

## Source-guidance rule

Do not generate the plans until the relevant local guidance or user-provided references have been read.

Expected source types:

- training-overview guidance
- exemplar training plans
- feature-specific reference material where present

If those sources are missing, switch to recovery mode, request the missing documents, and do not invent feature workflows.

## Core training principles

Unless stronger guidance overrides them, use these defaults:

- tailor the plan to the customer's actual operating model
- cover administrative and setup foundations early where they are prerequisites
- keep feature sequencing dependency-aware
- include pre-reading plus live facilitated sessions
- make Session 1 an orientation or walkthrough
- use UAT-first working patterns from Session 2 onward
- treat sandbox or UAT access as a hard prerequisite
- keep activities tied to practical customer workflows
- include a route for follow-up questions and post-session recordings

## Scope pass

### Pass 1: decide feature scope

Separate:

- in-scope features needed for pilot, compliance, integration, or launch readiness
- later-phase features that are confirmed out of scope for now

### Pass 2: expand the chosen features

For each in-scope feature, derive:

- checkbox activities for the concise plan
- concise inline tips
- UAT workflow steps for the detailed plan
- expected outcomes and evidence cues
- session-linked pre-reading

## Concise plan structure

Use `{dummy-docx-skill}` for final build rules if it exists.

Suggested structure:

```text
COVER / HEADER
- training title
- trainer
- UAT tenant
- go-live date
- version

FORMAT
- orientation first
- UAT-first from Session 2 onward
- final readiness review
- sessions recorded and shared
- support route between sessions

SESSION SCHEDULE

CURRICULUM
- one heading per in-scope feature
- why it matters
- activities
- inline tips
- references
```

## Detailed plan structure

Use `{dummy-docx-skill}` for final build rules if it exists.

Suggested sections:

```text
COVER PAGE
1. Training overview
2. Session schedule
3. Session details
4. Support between sessions
Appendix A: feature references
```

Detailed-plan expectations:

- every session includes at least one numbered UAT workflow
- every workflow includes an expected outcome
- every workflow includes at least one evidence or confirmation point
- reference links live in the appendix rather than being scattered everywhere

## Final checks

Across both outputs, verify:

1. the feature sequence follows dependencies or any deviation is explained
2. the named UAT tenant is used consistently
3. the orientation-first and UAT-first model is preserved
4. support routes point to the trainer or delivery team only

For the concise plan, verify:

5. format, schedule, and curriculum sections all exist
6. each feature has practical activities and references
7. inline tips cover real prerequisites or gotchas
8. no project-plan material is included

For the detailed plan, verify:

9. each session includes at least one numbered UAT workflow
10. each workflow includes an expected outcome
11. each workflow includes an evidence cue
12. the overview explains customer objectives and operating model
13. sandbox readiness is confirmed or explicitly flagged as a blocker
14. blended learning elements appear throughout
15. Appendix A covers the in-scope features fully

## Output

1. save both documents through the active build workflow
2. present both outputs to the user
3. provide a short summary covering:
   - sessions planned
   - feature coverage
   - any sequencing deviations
   - missing guidance or scope gaps
   - whether pedagogy guidance was applied
