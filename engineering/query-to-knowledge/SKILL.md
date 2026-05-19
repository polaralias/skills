---
name: query-to-knowledge
description: Resolve open repository questions into durable knowledge. Use when terminology is fuzzy, decisions are still soft, docs and code disagree, or a plan needs pressure-testing before implementation. This skill batches tightly related questions, minimizes token waste, and captures resolved results into the repository knowledge base such as `GLOSSARY.md`, `docs/decisions/`, and canonical docs.
---

# Query To Knowledge

Use this skill when the repository does not yet know something clearly enough.

The job is to turn ambiguity into durable repository knowledge without burning tokens on long one-question-at-a-time interrogation.

## Use This Instead Of

- Use `repository-dissection` when the whole repository is still unclear and you first need to establish what is actually there.
- Use `repository-knowledge-engineering` when the knowledge base already exists and the main job is to establish structure, evolve it, or keep it aligned after changes.
- Use this skill when the missing piece is local uncertainty: unclear terms, unresolved trade-offs, contradictory claims, or under-specified behavior.

## Workflow

### 1. Rebuild the question surface before asking anything

- Read the relevant code and canonical docs first.
- Read `GLOSSARY.md` if it exists.
- Read `docs/decisions/` if it exists.
- Separate:
  - questions that can be answered from the repository
  - questions that need the user's judgment
  - questions that depend on other questions

Do not ask questions that the repository can answer directly.

### 2. Build a question batch instead of a question queue

Ask a small batch of tightly related questions in one turn.

Default batch size:

- 2 to 5 questions

Only ask one question at a time when the next question genuinely depends on the answer.

Within a batch:

- keep each question short
- keep all questions on one theme
- avoid repeating context already established
- include a recommended answer only when it materially sharpens the decision

### 3. Stress-test with concrete scenarios

When language or behavior is fuzzy, use concrete scenarios to force precision.

Examples:

- boundary cases
- conflicting user expectations
- lifecycle transitions
- naming collisions between related concepts

Prefer scenario pressure over abstract debate.

### 4. Synthesize after each batch

After the user responds, produce a short synthesis:

- resolved
- still open
- changed understanding
- next question batch or capture step

Do not keep rediscovering the same branch of the conversation.

### 5. Capture resolved knowledge immediately

When something is resolved, write it to the right repository artifact in the same slice.

Default targets:

- `GLOSSARY.md` for terms, boundaries, and canonical language
- `docs/decisions/` for durable decisions and trade-offs
- canonical product or contract docs for behavior-level truths

Do not force every resolved point into a decision record. Use the lightest artifact that preserves the truth.

### 6. Preserve the boundary with repository knowledge engineering

This skill resolves uncertainty and captures new knowledge.

It does not own the whole knowledge base. Once the open questions are resolved, hand off to `repository-knowledge-engineering` when the larger task becomes:

- reshaping the documentation foundation
- aligning many artifacts after implementation
- maintaining the reading order and knowledge system as a whole

## Decision Rules

- Ask fewer, denser questions rather than many thin turns.
- Do not batch unrelated topics together.
- Do not ask the user to answer what the repository can answer.
- Do not keep recommending answers when the recommendation adds no value.
- Use `GLOSSARY.md` for vocabulary and concept boundaries, not implementation notes.
- Use `docs/decisions/` only for durable decisions that future readers would otherwise question.
- If a topic is still too broad after one batch, narrow the next batch instead of broadening the debate.

## Expected Outputs

- resolved terminology
- clarified behavior or scope assumptions
- updated `GLOSSARY.md`
- new or updated decision notes under `docs/decisions/`
- a short summary of what is now known and what remains open
