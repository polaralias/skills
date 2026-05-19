---
name: pickup
description: Resume work from a local handoff and rebuild trustworthy context before editing. Use when starting a new Codex session on an existing project, especially after prior archaeology, repair, refactor, or documentation work that left a handoff in `.codex/handoffs/`.
---

# Pickup

Resume from the project's own continuation artifacts, not from memory.

Treat the handoff as an input, not as unquestioned truth.

## Workflow

### 1. Find the right handoff

- If the user named a handoff file, use it.
- Otherwise check `.codex/handoffs/` in the current project.
- Prefer the latest dated handoff that matches the current task.
- If multiple handoffs are plausible, pick the narrowest topic match rather than simply the newest file.

### 2. Read the canonical context

- Read the handoff first.
- Then read the docs it identifies as canonical.
- Also read `AGENTS.md`, `README.md`, and the active plan or contract docs when they exist and are relevant.
- Use the current reading order if one exists.

### 3. Verify the handoff against current state

- Check git status when available.
- Confirm that the referenced files still exist.
- Confirm that the cited plan or support status still matches the current state.
- If the project moved on since the handoff was written, name the drift clearly.

Classify each important handoff claim as:

- still true
- stale
- partially true
- needs revalidation

### 4. Rebuild the immediate work context

Before editing, summarize:

- the intended goal of the current session
- the verified current state
- any stale or risky assumptions from the handoff
- the first next step you will take

This summary should be short and should separate verified current truth from inherited notes.

### 5. Continue with the right downstream skill

- Use `repository-dissection` if the handoff points into an area whose truth is still unclear.
- Use `query-to-knowledge` if the next step depends on unresolved terminology, design trade-offs, or contradictory local knowledge.
- Use `tdd` if you are about to change behavior.
- Use `repository-knowledge-engineering` if the next step is primarily alignment across docs, code, plans, and tests.

## Fallbacks

- If no handoff exists, say so plainly and rebuild context from the canonical docs.
- If the handoff exists but is obviously stale, preserve it as evidence and proceed from verified current state.
- If the handoff conflicts with code or docs, trust the strongest current evidence and record the mismatch.

## Guardrails

- Do not continue on handoff claims alone.
- Do not skip the canonical docs just because the handoff looks comprehensive.
- Do not silently flatten `planned` into `done`.
- Prefer a short verified restart over a long inherited narrative.

## Output Shape

At pickup time, produce:

- the chosen handoff path
- the canonical docs you relied on
- the verified current objective
- the immediate next action

Then begin the work.
