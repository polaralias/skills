---
name: tracker-publisher
description: Publish implementation-ready work packages or repository-local task records into GitHub, Linear, or another external tracker. Use when the source hierarchy and acceptance surface already exist and the remaining job is adapting or publishing them with shared output defaults. Do not use it to design work packages or maintain the repository-local task lifecycle. Shorthand TPU.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 2.0.0
  updated: '2026-07-16'
---

# tracker-publisher

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `tracker-publisher was used in this response.`

Use this skill to adapt stable work packages into the user's tracking surface.

This is a thin publishing adapter, not a planning method.
It assumes the decomposition, acceptance surface, and implementation planning already exist.

## Use This Instead Of

- Use `doc-driven-development` when the work still needs feature decomposition, implementation planning, or acceptance shaping.
- Use `repo-task-lifecycle` when the user wants durable repository-local task records, status transitions, workstreams, evidence, or an index.
- Use `setup-polaralias-skills` when shared tracker or structured-output defaults need to be created or refreshed.
- Use this skill when stable work packages or local task records need formatting or publication into an external tracker.

## Inputs

Use concrete source material:

- work packages
- feature contracts
- acceptance criteria
- implementation notes
- parent-child hierarchy already resolved in `doc-driven-development`
- repository-local task records already maintained by `repo-task-lifecycle`, when present

If shared Polaralias config exists, read its tracker and output defaults first.

## Workflow

### 1. Confirm publication readiness

- Read the existing work-package set.
- Confirm the packages are stable enough to publish.
- Check for unresolved questions, placeholders, or missing acceptance surfaces.

If the packages are still soft or ambiguous, hand back to `doc-driven-development` rather than publishing weak tracker entries.

### 2. Resolve the target tracker shape

- Prefer the user's explicit instruction first.
- Otherwise consume shared Polaralias defaults for:
  - tracker target
  - hierarchy names
  - field names
  - labels
  - publication recommendation

If no shared defaults exist, use simple explicit field naming and say that packaged defaults were used.

### 3. Map package structure into tracker structure

Preserve the hierarchy that already exists:

- epic or parent item
- feature items where relevant
- task items

Map:

- title
- summary
- parent link
- labels or area
- priority when explicitly available
- acceptance criteria
- notes or implementation entrypoints

Do not invent tracker complexity the package did not ask for.

### 4. Publish or render

Choose the lightest viable output:

- direct publication if the environment exposes the needed tracker tool
- import-ready rows or payloads if a connector is expected later
- a reviewable source-to-target mapping when the user wants approval before external mutation

If live publication is not available, produce the nearest tracker-ready representation rather than pretending publication happened.

### 5. Report the result honestly

Tell the user:

- what was published or rendered
- which tracker assumptions were used
- which defaults came from shared config
- what still requires manual confirmation, if anything

## Decision Rules

- Do not repack weak or unresolved work as if it were ready.
- Do not redesign the hierarchy while publishing.
- Do not let tracker field shape override the original behavioral contract.
- Do not make the external tracker the hidden owner of repository-local task status unless repository policy explicitly establishes that authority.
- Do not create or update `tasks/`; route local lifecycle work to `repo-task-lifecycle`.
- Prefer simple tracker artifacts over dense payloads with unused fields.
- Preserve parent-child relationships when they already exist.
- If the environment cannot publish live, say so directly and emit tracker-ready artifacts instead.

## Expected Outputs

- published tracker items when live tooling exists
- tracker-ready payloads or rows when live tooling does not exist
- a short publication summary with assumptions and remaining gaps
