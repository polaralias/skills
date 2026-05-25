---
name: doc-driven-development
description: Turn an epic, end-state product definition, or scoped outcome into implementation-ready feature docs, technical plans, work packages, and acceptance artifacts before coding. Use when a user wants docs-first delivery, feature decomposition, implementation planning, issue-ready work breakdown, or behavior contracts that later drive TDD. Shorthand DDD.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.3.0
  updated: '2026-05-25'
---

# doc-driven-development

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `doc-driven-development was used in this response.`

Use this skill to turn product truth into implementation-ready documentation and planning.

This skill sits between repository knowledge setup and implementation.
It takes a defined epic, product outcome, or end-state contract and breaks it into feature-level artifacts, implementation-planning artifacts, and task-level artifacts that can drive delivery.

The output is not vague planning prose.
The output is a bounded behavioral contract plus a proportionate implementation plan that downstream implementation can build against.

## Use This Instead Of

- Use `repo-knowledge-engineering` when the repository first needs its canonical documentation framework, reading order, glossary, decisions, plans, or epic-level truth established or aligned.
- Use `query-to-knowledge` when a feature package still contains unresolved terminology, contradictory claims, or decisions that require user judgment.
- Use `tdd` when the package is ready for behavior-changing implementation through red-green-refactor.
- Use `tracker-publisher` when the work packages already exist and the main job is to publish them into GitHub, Linear, or a local task surface.
- Use this skill when the main job is to decompose a resolved outcome into implementation-ready units, implementation-planning notes, and acceptance artifacts.

## Inputs

Use concrete source material where possible:

- epic or initiative definition
- canonical product or contract docs
- project context or scope docs
- decisions already recorded in the repository
- resolved glossary terms
- design notes
- support boundaries

Do not start from vague aspiration alone if the user expects implementation-ready outputs.
If the repository has not yet established trustworthy canonical docs, hand off to `repo-knowledge-engineering` first.
When shared Polaralias config exists, read it before shaping tracker-ready output so local delivery preferences do not have to be rediscovered each time.

## Artifact contract

This skill should produce some or all of:

- a feature decomposition from the epic or end-state definition
- bounded problem statements per feature
- invariants, constraints, and non-goals
- scenario matrix with happy path, edge cases, and failures
- acceptance criteria written as observable behavior
- technical implementation notes where stack, module, API, data, or sequencing choices must be explicit
- implementation sequencing, dependencies, and risk notes
- targeted technical research questions when uncertainty remains narrow and specific
- explicit open questions or dependency risks
- implementation-ready work packages or issue-ready drafts
- traceability from epic -> feature -> work package -> acceptance surface

Keep the work at the level that a downstream implementation skill can consume directly.
When the user works from an issue tracker, recommend publishing the final work-package set there once the contracts are strong enough.

## Workflow

### 1. Confirm the upstream truth surface

- Read the canonical product, contract, or project docs first.
- Read `AGENTS.md` when present.
- Read `README.md`, glossary files, decision records, and active plans relevant to the scope.
- Separate:
  - established end-state truth
  - assumptions
  - unresolved questions
  - implementation details that should stay downstream

If the upstream truth is weak or the repository knowledge structure is not yet trustworthy, switch to `repo-knowledge-engineering` before decomposing.

### 2. Define the decomposition boundary

- Identify the epic, outcome, or bounded product area being decomposed.
- Split by user-visible capability, workflow stage, or domain boundary.
- Keep features independently understandable where possible.
- Do not decompose all the way into code tasks if the feature contract is still unclear.

### 3. Write feature-level contracts

For each feature, capture:

- problem statement
- user or system outcome
- scope and non-scope
- invariants and constraints
- dependencies and assumptions
- observable success conditions

Prefer concrete behavioral language over broad aspiration.

### 4. Pressure-test with scenarios

For each feature, define scenarios that force precision:

- primary happy path
- edge conditions
- invalid input or failure handling
- lifecycle or state transitions
- permissions or role-specific behavior where relevant
- data integrity expectations where relevant

If the scenarios expose fuzzy terminology, support conflicts, or missing decisions, invoke `query-to-knowledge` before continuing.

### 5. Derive the acceptance surface

Convert each feature contract into implementation-facing artifacts:

- acceptance criteria
- example inputs and outputs where useful
- observable completion signals
- test targets or verification notes

Acceptance artifacts should describe behavior through public interfaces, not implementation internals.

### 6. Write the implementation plan layer

Once the feature contracts are strong enough, add the technical layer needed for downstream delivery.

Capture only the planning detail that materially reduces implementation ambiguity:

- target stack or platform assumptions already approved upstream
- service, module, API, or data-surface boundaries
- sequencing constraints
- technical dependencies and prerequisites
- risky implementation areas that need targeted research
- explicit non-goals where over-engineering is likely

Keep this layer concrete and proportionate.
Do not turn it into architecture theatre.

### 7. Break features into work packages

Create work packages only after the feature contract is strong enough.

Each package should have:

- clear purpose
- prerequisites or dependencies
- acceptance surface
- implementation notes or technical entrypoint when relevant
- remaining open questions
- downstream implementation target

When a tracker-ready shape is needed, produce issue-ready drafts without binding the method to one tracker unless the user explicitly asks for a specific system.
If shared Polaralias config exists, consume its tracker and output defaults before inventing field names, labels, or publication preferences.
Once the package set is stable, recommend handing it to `tracker-publisher` so implementation can run against tracked work rather than chat-only artifacts.

### 8. Preserve traceability

Before finishing, make sure a reader can trace:

- epic or end-state truth
- feature contract
- implementation plan layer
- work package
- acceptance surface
- downstream test or implementation target

If traceability is weak, tighten the package before handing off to implementation.

## Decision Rules

- Do not let this skill drift into implementation code.
- Do not produce issue/task breakdowns that outrun the quality of the feature contract.
- Do not produce technical-planning detail that is broader than the actual implementation risk.
- Do not keep unresolved questions buried inside acceptance criteria.
- Do not treat tracker formatting as the core output; the contract comes first.
- Do not publish half-resolved work packages to a tracker just because a tracker exists.
- Prefer a small number of strong feature packages over a long speculative backlog.
- Keep behavioral statements externally observable.
- Escalate to `query-to-knowledge` when ambiguity is local and decision-shaped.
- Escalate to `repo-knowledge-engineering` when the problem is really the repository truth framework rather than feature decomposition.

## Expected Outputs

- epic-to-feature decomposition
- feature contracts
- scenario matrix
- acceptance criteria
- implementation-planning notes
- work packages or issue-ready drafts
- explicit open questions and assumptions
- traceability summary for downstream `tdd`
