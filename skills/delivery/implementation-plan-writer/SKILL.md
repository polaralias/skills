---
name: implementation-plan-writer
description: Produce a customer-facing implementation plan from kickoff material, local guidance, and confirmed delivery assumptions. Use when a user needs a structured onboarding or implementation plan that carries a customer from setup through go-live without expanding into generic project-management overhead. Shorthand IPW.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.1.1
  updated: '2026-05-24'
---

# implementation-plan-writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `implementation-plan-writer was used in this response.`


This skill generates one customer-facing implementation plan covering the path to go-live. It is intentionally narrow: the document should explain the implementation journey clearly without becoming a catch-all project pack.

Training remains a placeholder here and is expected to be handled by a downstream training workflow. Post-launch content is deliberately brief.

## Suggested workflow position

Recommended flow only:

```text
kickoff-summary-writer
  -> implementation-plan-writer
  -> training-plan-writer
```

That sequence is guidance, not a hard dependency.

## Compression rules

Use a tight document shape.

- no introductory filler section
- no standalone milestone-summary section
- no support and escalation section
- no appendices unless they add real value
- keep phases consolidated
- keep post-launch to a brief sentence, not a full section
- tighten prose before adding more sections

## Input routes

### Route A: kickoff synthesis already exists

Use the synthesis artifact as the primary source. Anything still marked `[NOT DISCUSSED]`, `[inferred]`, or similar should be surfaced for confirmation before drafting.

### Route B: direct customer briefing

Collect, in one pass where possible:

Required:

- customer name
- implementation lead
- start date
- organisation size

Important:

- customer contacts
- priority challenges
- required integrations
- migration or current-platform context
- domain type
- go-live target
- launch content needs
- reporting or compliance needs
- complexity band if known

Optional:

- organisation structure
- branding constraints
- provisioning approach
- number of admins
- hard deadlines
- known risks

### Route C: transcript or notes

If the user gives raw notes or transcript material, extract the same fields, summarise them cleanly, show any gaps, then confirm those gaps before drafting.

## Source guidance requirement

Do not draft the plan until the relevant local guidance has been read or provided by the user.

### Expected source types

Look for:

- implementation-process guidance
- customer-onboarding guidance
- relevant launch-planning exemplars

### Recovery mode

If the required bundled sources are unavailable:

1. switch explicitly into recovery mode
2. ask the user for the missing source documents and any known deviations
3. proceed only when those are provided
4. do not invent missing delivery steps

## Document build rules

If `{dummy-docx-skill}` is available, use it for final document generation. It owns the final build and styling conventions.

Use the implementation sources to populate delivery stages, responsibilities, and standard milestones. Use `[TBC]` for unresolved details rather than inventing them.

## Default document shape

```text
COVER PAGE
- [Customer Name]
- Implementation Plan
- prepared by / date / version / classification / go-live
- short italicised working-reference note

1. Customer overview
2. Scope and objectives
3. Implementation phases
4. Customer responsibilities
5. Training placeholder
```

## Training placeholder

Include this wording exactly:

---
Training will be delivered in line with the agreed Training Plan document,
provided separately. The training schedule, session topics, curriculum
checklist and UAT workflows are set out in the Training Plan, produced
following agreement of implementation scope. Sessions will largely be
delivered virtually but can be delivered on-site where agreed.
---

## Explicit exclusions

Do not reintroduce:

- an introduction section
- a standalone milestones summary
- a support and escalation section
- appendices by default

## Phase model

Default to three phases unless the implementation genuinely needs more:

- initiation and configuration
- onboarding, training, and piloting
- go-live preparation and launch

## Style rules

- UK English
- plain professional tone
- active voice
- consistent `[TBC]` usage
- no internal-only names in customer-facing sections
- no help-desk references inside implementation phases
- target roughly 8 to 10 body pages

## Output expectations

After document generation:

1. save the file via the active document workflow
2. present the file to the user
3. provide a short inline summary with:
   - key milestones or dates
   - all `[TBC]` items
   - delivery risks inferred from the inputs
   - the likely next step, including training-plan generation if needed

## Downstream coordination

### For training-plan-writer

- do not duplicate scope or project-plan material
- use the implementation scope to shape the training sequence
- keep help-desk references out of training content

### For general task or board builders

- align to the same phase model where appropriate
- avoid inventing a post-launch phase unless the plan really includes one
- keep training as a separate artifact

## Final checks

Before presenting the plan, verify:

1. the body stays within the intended page range
2. the banned sections have not crept back in
3. post-launch remains brief
4. the training placeholder is present verbatim
5. all `[TBC]` items are surfaced in the summary
6. responsibilities are derived from the guidance, not invented casually
7. ownership across activities is coherent
