---
name: repository-knowledge-engineering
description: Establish, evolve, and keep the repository knowledge base trustworthy while engineering work continues. Use when shaping the documentation foundation, refining canonical artifacts, or aligning code, tests, plans, and maintained knowledge after changes land.
---

# Repository Knowledge Engineering

Use this skill to engineer the repository knowledge base as a working system.

That can mean:

- establishing the first durable knowledge structure
- evolving that structure as the repository matures
- aligning the knowledge base after code or documentation changes land

The repository knowledge base includes the docs and working surfaces agents rely on to understand and continue the project:

- `README.md` or another root reading order
- `GLOSSARY.md` when the repository uses an explicit glossary
- canonical docs
- decision records or notes under `docs/decisions/`
- plans and trackers
- navigation and reading order
- handoff artifacts
- dated evidence when validation happens

This skill is broader than test harnessing and later in the flow than repository dissection.

## Use This Instead Of

- Use `repository-dissection` when the repository truth is still unclear and you need to turn implicit understanding into explicit documented understanding.
- Use `tdd` when the main job is behavior change through red-green-refactor.
- Use this skill when the main job is to shape or maintain the repository knowledge base itself.

## Phases

### 1. Foundation

Use this skill to create or reshape the knowledge base:

- define the reading order
- decide which artifacts are canonical
- choose where glossary, decisions, plans, and support truth live
- create the minimum documentation spine the repository actually needs

### 2. Capture

Use this skill to absorb newly resolved knowledge into the right artifacts:

- glossary updates
- decision capture
- clarified support or contract docs
- updated plans and trackers

### 3. Alignment

Use this skill to keep the knowledge base synchronized with code, tests, and current support truth after work lands.

## Workflow

### 1. Identify the canonical knowledge surface

- Find the repository's reading order and source-of-truth docs.
- Separate:
  - evidence docs
  - desired-state or contract docs
  - execution-plan docs
  - generated or derived docs
- If `GLOSSARY.md` exists, treat it as the glossary or domain-language source.
- If `docs/decisions/` exists, treat it as the durable decision-history source.
- Know which files future agents are expected to trust first.

### 2. Classify the requested change

Classify the work before editing:

- behavior change
- harness change
- contract clarification
- documentation correction
- plan-state update
- mixed slice

If the slice changes repository truth, the canonical knowledge base must move with it.

### 3. Decide what must stay aligned

For the current slice, check whether you must update:

- tests or harness code
- support matrix or support-status docs
- README or root navigation
- architecture, reliability, or security docs
- `GLOSSARY.md` if domain language or glossary truth changed
- `docs/decisions/` if a durable decision changed or was resolved
- active plans or debt trackers
- evidence notes if new validation happened

Do not update everything by default. Update the exact files future contributors would trust for this change.

### 4. Preserve knowledge boundaries

- Keep dated validation notes as evidence.
- Keep support matrices and root docs as current contract.
- Keep execution plans focused on how remaining gaps will close.
- Keep `GLOSSARY.md` focused on glossary and domain language, not implementation detail.
- Keep `docs/decisions/` focused on durable decisions, not routine progress notes.
- Do not silently rewrite old evidence to hide drift; either update the current contract or add a new dated evidence record.

### 5. Update knowledge in the same slice as the work

- If behavior changed, update the contract docs in the same tranche.
- If support status changed, update the support matrix before widening public claims elsewhere.
- If glossary language changed, update `GLOSSARY.md` in the same slice.
- If a durable decision was made or invalidated, update `docs/decisions/` if the repository uses decision records.
- If a plan assumption became false, update the plan immediately.
- If navigation changed, update the reading order so future agents do not rediscover the repository from scratch.

### 6. Keep the language sharp

Use explicit status language:

- verified working
- verified limited
- known broken
- untested

Distinguish:

- current verified state
- desired end state
- remaining gap
- implementation drift
- evidence strength

### 7. Finish with a trustworthy next-step surface

At the end of the slice, make sure a fresh agent can answer:

- what changed
- what is now true
- what is still open
- where to read next

If that answer still depends on chat history, the repository knowledge engineering pass is incomplete.

## Decision Rules

- Do not widen support claims based on manifests or generated docs alone.
- Do not let README or entry docs lag behind known contract changes.
- Do not delete evidence just because the current contract improved.
- Prefer a small number of strong canonical docs over a growing pile of loose notes.
- Create `GLOSSARY.md` or `docs/decisions/` when they would materially improve the repository knowledge base; do not create them as empty ceremony.
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
- dated evidence note for new validation
- local handoff that reflects the new truth
