---
name: query-to-knowledge
description: Resolve open repository questions into durable knowledge. Use when terminology is fuzzy, decisions are still soft, docs and code disagree, or a plan needs pressure-testing before implementation. This skill asks the largest useful set of repository questions in one turn, minimizes token waste, and captures resolved results into the repository knowledge base such as `GLOSSARY.md`, `docs/decisions/`, and canonical docs.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.1.0
  updated: '2026-05-23'
---

# Query To Knowledge

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `query-to-knowledge was used in this response.`

Use this skill when the repository does not yet know something clearly enough.

The job is to turn ambiguity into durable repository knowledge without burning tokens on long one-question-at-a-time interrogation.

## Use This Instead Of

- Use `repo-dissection` when the whole repository is still unclear and you first need to establish what is actually there.
- Use `repo-knowledge-engineering` when the knowledge base already exists and the main job is to establish structure, evolve it, or keep it aligned after changes.
- Use this skill when the missing piece is local uncertainty: unclear terms, unresolved trade-offs, contradictory claims, or under-specified behavior.

## Workflow

### 1. Rebuild the question surface before asking anything

- Read the relevant code and canonical docs first.
- Read `AGENTS.md` when present.
- Read the repository's domain-language file when present, such as `GLOSSARY.md` or `CONTEXT.md`.
- Read `docs/decisions/` if it exists.
- Read active plans or contract docs when the repository is already in a repair or design tranche.
- Separate:
  - questions that can be answered from the repository
  - questions that need the user's judgment
  - questions that depend on other questions
  - stale inherited assumptions that must be revalidated first

Do not ask questions that the repository can answer directly.
When the repository can answer 80 percent of the question, answer that part from evidence and ask the user only for the irreducible judgment call.

### 2. Build a question batch instead of a question queue

Ask one comprehensive set of questions for the current ambiguity before waiting for a reply.

Include all missing user judgments that are useful to resolve now, as long as the questions stay relevant to the same decision or ambiguity.
Use conditional phrasing when needed instead of splitting dependent questions into separate turns.
Only ask fewer questions when adding more would create noise, topic drift, or an unreasonably hard reply.

Within a batch:

- keep each question short
- ask the largest useful set rather than a token small batch
- keep all questions relevant to the current decision or ambiguity
- avoid repeating context already established
- include a recommended answer only when it materially sharpens the decision

Prefer contradiction-driven batches when possible:

- code vs docs
- two docs disagreeing
- code vs user expectation
- declared support vs observed behavior

### 3. Stress-test with concrete scenarios

When language or behavior is fuzzy, use concrete scenarios to force precision.

Examples:

- boundary cases
- conflicting user expectations
- lifecycle transitions
- naming collisions between related concepts

Prefer scenario pressure over abstract debate.

If the ambiguity is still unresolved after two batches and the repository can be probed safely, switch from asking to bounded repository or runtime inspection.

### 4. Synthesize after each batch

After the user responds, produce a short synthesis:

- resolved
- still open
- changed understanding
- next question batch or capture step

Do not keep rediscovering the same branch of the conversation.
If two batches in a row produce no meaningful clarification, stop querying and pivot to repository exploration, implementation probing, or a different downstream skill.

### 5. Capture resolved knowledge immediately

When something is resolved, write it to the right repository artifact in the same slice.

Default targets:

- the repository's glossary file such as `GLOSSARY.md` or `CONTEXT.md` for terms, boundaries, and canonical language
- `docs/decisions/` for durable decisions and trade-offs
- canonical product or contract docs for behavior-level truths
- support docs or capability tables for support-boundary conclusions
- execution plans or debt trackers for unresolved but important open questions

Do not force every resolved point into a decision record. Use the lightest artifact that preserves the truth.
Do not continue the questioning pattern once the answer is already established by code plus tests. Capture it directly.

### 6. Preserve the boundary with repository knowledge engineering

This skill resolves uncertainty and captures new knowledge.

It does not own the whole knowledge base. Once the open questions are resolved, hand off to `repo-knowledge-engineering` when the larger task becomes:

- reshaping the documentation foundation
- aligning many artifacts after implementation
- maintaining the reading order and knowledge system as a whole

When the remaining uncertainty is no longer conceptual but behavioral, switch to `tdd`.

## Decision Rules

- Ask fewer, denser questions rather than many thin turns.
- Do not batch unrelated topics together.
- Do not ask the user to answer what the repository can answer.
- Do not keep recommending answers when the recommendation adds no value.
- Use the glossary file such as `GLOSSARY.md` or `CONTEXT.md` for vocabulary and concept boundaries, not implementation notes.
- Use `docs/decisions/` only for durable decisions that future readers would otherwise question.
- Distinguish between terminology questions, product-decision questions, support-claim questions, and protocol-meaning questions because they capture to different artifacts.
- If a topic is still too broad after one batch, narrow the next batch instead of broadening the debate.

## Expected Outputs

- resolved terminology
- clarified behavior or scope assumptions
- updated glossary file such as `GLOSSARY.md` or `CONTEXT.md`
- new or updated decision notes under `docs/decisions/`
- a short summary of what is now known and what remains open
