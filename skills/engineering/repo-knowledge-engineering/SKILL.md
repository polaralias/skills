---
name: repo-knowledge-engineering
description: Establish, evolve, and keep the repository knowledge base trustworthy while engineering work continues. Use when shaping the documentation foundation, refining canonical artifacts, running cross-artifact truth checks, or aligning canonical docs, plans, decisions, glossary, reading order, tracker state, and validation evidence after changes land. Shorthand RKE.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 2.3.0
  updated: '2026-05-25'
---

# repo-knowledge-engineering

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `repo-knowledge-engineering was used in this response.`

Use this skill to engineer the repository knowledge base as a working system.

That can mean:

- establishing the first durable knowledge structure
- defining the repository's canonical product and epic-level truth surfaces
- evolving that structure as the repository matures
- running cross-artifact truth checks across docs, plans, trackers, and evidence
- aligning the knowledge base after code or documentation changes land

The repository knowledge base includes the docs and working surfaces agents rely on to understand and continue the project:

- `AGENTS.md` or another operating guide when present
- `README.md` or another root reading order
- `GLOSSARY.md` when the repository uses an explicit glossary
- canonical docs
- decision records or notes under `docs/decisions/`
- plans and trackers
- navigation and reading order
- handoff artifacts
- dated evidence when validation happens

This skill owns the repository knowledge system, not implementation work.
It may document what tests, evaluation harnesses, CI checks, or validation runs prove, but it does not author or repair test code, eval harnesses, CI logic, or application code unless the user explicitly asks for that work or another implementation skill is also invoked.
It is later in the flow than repository dissection.

## Use This Instead Of

- Use `repo-dissection` when the repository truth is still unclear and you need to turn implicit understanding into explicit documented understanding.
- Use `doc-driven-development` when the repository truth already exists and the main job is to decompose that truth into feature contracts, work packages, and acceptance artifacts before coding.
- Use `tdd` when the main job is behavior change through red-green-refactor, including adding or repairing tests and implementation code.
- Use this skill when the main job is to shape or maintain the repository knowledge base itself.

## Phases

### 1. Foundation

Use this skill to create or reshape the knowledge base:

- define the reading order
- decide which artifacts are canonical
- define where end-state product truth and epic-level scope live
- choose where glossary, decisions, plans, and support truth live
- create the minimum documentation spine the repository actually needs

### 2. Capture

Use this skill to absorb newly resolved knowledge into the right artifacts:

- glossary updates
- decision capture
- clarified support or contract docs
- updated plans and trackers

### 3. Alignment

Use this skill to keep the knowledge base synchronized with current repository truth, including code outcomes, validated behavior, and current support truth after work lands.

### 4. Analysis

Use this skill to run a cross-artifact check before or after implementation:

- compare epic-level truth to feature contracts
- compare feature contracts to implementation plans
- compare implementation plans to work packages or tracker items
- compare repository claims to validation evidence
- identify drift, missing promotion, stale plans, or contradictory status language

### 5. Tranche Completion

Use this skill to close a tranche honestly:

- move completed plans out of the active surface
- narrow or retire debt that is no longer current
- move implemented behavior out of future-tense or open-question language
- confirm the root reading order still points at the current truth

## Workflow

### 1. Identify the canonical knowledge surface

- Find the repository's reading order and source-of-truth docs.
- Separate:
  - evidence docs
  - desired-state or contract docs
  - epic-level or product-truth docs
  - execution-plan docs
  - generated or derived docs
- Keep local handoffs explicitly subordinate to tracked canonical truth.
- If `GLOSSARY.md` exists, treat it as the glossary or domain-language source.
- If `docs/decisions/` exists, treat it as the durable decision-history source.
- Know which files future agents are expected to trust first.

### 2. Classify the requested change

Classify the work before editing:

- behavior change already resolved elsewhere
- validation-evidence or documentation change
- contract clarification
- documentation correction
- plan-state update
- mixed slice

If the slice changes repository truth, the canonical knowledge base must move with it.

### 3. Decide what must stay aligned

For the current slice, check whether you must update:

- support matrix or support-status docs
- README or root navigation
- architecture, reliability, or security docs
- `GLOSSARY.md` if domain language or glossary truth changed
- `docs/decisions/` if a durable decision changed or was resolved
- active plans or debt trackers
- validation, CI-status, or evidence docs when other work changed what the repository now proves
- evidence notes if new validation happened

Do not update everything by default. Update the exact files future contributors would trust for this change.
Do not treat this step as permission to write or repair tests, evaluation harnesses, CI jobs, or application code.

### 4. Run a bounded cross-artifact truth check

When the repository has several linked planning and execution surfaces, compare the strongest current artifacts:

- epic or product-truth docs
- feature contracts
- implementation-plan docs
- work packages or tracker items
- canonical contract docs
- validation evidence

Check for:

- statements that changed in one surface but not the others
- open questions that were resolved but never promoted
- tasks or tracker items that no longer match the accepted contract
- implementation plans that still describe superseded sequencing
- validation claims that overstate what the repository actually proves

If drift exists, name which surface is strongest, which surfaces are stale, and what must be promoted, corrected, or de-emphasized.

### 5. Preserve knowledge boundaries

- Keep dated validation notes as evidence.
- Keep support matrices and root docs as current contract.
- Keep execution plans focused on how remaining gaps will close.
- Keep `GLOSSARY.md` focused on glossary and domain language, not implementation detail.
- Keep `docs/decisions/` focused on durable decisions, not routine progress notes.
- Keep generated inventories, route tables, and other derived artifacts clearly labeled as derived rather than canonical support truth.
- Do not silently rewrite old evidence to hide drift; either update the current contract or add a new dated evidence record.

### 6. Update knowledge in the same slice as the work

- If behavior changed, update the contract docs in the same tranche.
- If support status changed, update the support matrix before widening public claims elsewhere.
- If glossary language changed, update `GLOSSARY.md` in the same slice.
- If a durable decision was made or invalidated, update `docs/decisions/` if the repository uses decision records.
- If a plan assumption became false, update the plan immediately.
- If behavior is now repaired and validated elsewhere, move it out of `known broken`, `proposed`, or future-tense plan language in the same slice.
- If navigation changed, update the reading order so future agents do not rediscover the repository from scratch.

### 7. Promote new truth

- If behavior changed and is now validated, promote it from plan, risk, or exploratory language into canonical contract docs.
- If a risk narrowed but did not disappear, restate the narrower remaining risk rather than just marking the section done.
- If a handoff contains context important enough for future work, promote that truth into tracked docs before later tranches depend on it.

### 8. Keep the language sharp

Use explicit status language:

- verified working
- verified limited
- known broken
- untested

Distinguish:

- current verified state
- current observed state
- desired end state
- remaining gap
- implementation drift
- evidence strength

### 9. Finish with a trustworthy next-step surface

At the end of the slice, make sure a fresh agent can answer:

- what changed
- what is now true
- what is still open
- where to read next

If that answer still depends on chat history, the repository knowledge engineering pass is incomplete.
Ask explicitly whether a fresh agent could continue from tracked docs even if the local handoff were deleted.

## Decision Rules

- Do not widen support claims based on manifests or generated docs alone.
- Do not let README or entry docs lag behind known contract changes.
- Do not delete evidence just because the current contract improved.
- Do not write or repair tests, eval harnesses, CI jobs, or application code from this skill alone.
- Do not treat tracker state as repository truth when canonical docs or evidence disagree.
- Prefer a small number of strong canonical docs over a growing pile of loose notes.
- Create `GLOSSARY.md` or `docs/decisions/` when they would materially improve the repository knowledge base; do not create them as empty ceremony.
- Correct the root reading order before polishing lower-level docs when the entrypoint is misleading.
- Run a bounded publish-safety check when the repository is nearing public use:
  - secrets or tokens in notes
  - machine-local paths
  - stale setup stories
  - unsafe archive notes
- If a change is bounded and local, resist turning it into another archaeology pass.
- If repeated anti-drift work reveals a specialized recurring workflow, capture that as a future skill candidate only after it repeats.

## Common Outputs

- root reading order or knowledge-base foundation
- updated support matrix
- aligned README and architecture docs
- tightened reliability or security posture docs
- refreshed glossary or `GLOSSARY.md`
- new or updated decision record under `docs/decisions/`
- refreshed active plan or debt tracker
- cross-artifact drift summary
- archive compaction or evidence index cleanup when note sprawl exists
- dated evidence note for new validation
- local handoff that reflects the new truth
