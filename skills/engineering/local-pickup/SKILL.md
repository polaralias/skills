---
name: local-pickup
description: Resume work from a local handoff and rebuild trustworthy context before editing. Use when you are starting a new session on an existing project, especially after prior archaeology, repair, refactor, or documentation work that left a handoff in `docs/handoff/` or the repository's established handoff area, including workflow-aware handoffs that preserve the prior engineering stage. Shorthand LPK.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 2.3.1
  updated: '2026-05-25'
---

# local-pickup

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `local-pickup was used in this response.`

Resume from the project's own continuation artifacts, not from memory.

Treat the handoff as an input, not as unquestioned truth.

## Workflow

### 1. Find the right handoff

- If the user named a handoff file, use it.
- Otherwise check `docs/handoff/` in the current project or the repository's established handoff area.
- Prefer the latest dated handoff that matches the current task.
- If multiple handoffs are plausible, pick the narrowest topic match rather than simply the newest file.
- Prefer the handoff whose referenced canonical docs still exist and still point to the same active workstream.

### 2. Read the canonical context

- Read the handoff first.
- Then read `AGENTS.md` when present.
- Then read the root reading-order docs.
- Then read the domain-language file such as `GLOSSARY.md` or `CONTEXT.md` when present.
- Then read the active plan, support-truth docs, or contract docs the handoff identifies as canonical.
- Use the current reading order if one exists.

### 3. Verify the handoff against current state

- Check git status when available.
- Check the current branch when available.
- Confirm that the referenced files still exist.
- Confirm that the cited plan or support status still matches the current state.
- If the handoff includes workflow-state fields, confirm that the current stage and proposed next skill still match the strongest current evidence.
- When the next step depends on runtime claims such as a device IP, auth mode, managed launcher, or external route, re-check them before relying on the handoff.
- If the project moved on since the handoff was written, name the drift clearly.

Classify each important handoff claim as:

- still true
- stale
- partially true
- needs revalidation

Then classify the restart path:

- continue directly
- continue after correction
- stop and rediscover via `repo-dissection`

### 4. Rebuild the immediate work context

Before editing, summarize:

- the intended goal of the current session
- the verified current state
- the verified workflow stage and next skill when the handoff captured them
- any stale or risky assumptions from the handoff
- the first next step you will take

This summary should be short and should separate verified current truth from inherited notes.

### 5. Continue with the right downstream skill

- Use `repo-dissection` if the handoff points into an area whose truth is still unclear.
- Use `engineering-workflow-orchestrator` if the user wants the resumed session routed through the broader engineering workflow or hook-aware continuity.
- Use `query-to-knowledge` if the next step depends on unresolved terminology, design trade-offs, or contradictory local knowledge.
- Use `tdd` if you are about to change behavior.
- Use `repo-knowledge-engineering` if the next step is primarily alignment across repository truth surfaces after implementation or validation work.

## Fallbacks

- If no handoff exists, say so plainly and rebuild context from the canonical docs.
- If the handoff exists but is obviously stale, preserve it as evidence and proceed from verified current state.
- If the handoff conflicts with code or docs, trust the strongest current evidence and record the mismatch.
- If no handoff exists but unfinished local work makes the active stream obvious, rebuild from canonical docs and git state and recommend creating a retrospective handoff at tranche end.

## Guardrails

- Do not continue on handoff claims alone.
- Do not skip the canonical docs just because the handoff looks comprehensive.
- Do not silently flatten `planned` into `done`.
- If canonical docs and the handoff both disagree with code or tests, stop pretending continuity is intact and escalate to deeper rediscovery.
- Prefer a short verified restart over a long inherited narrative.

If local-pickup discovers a meaningful mismatch, refresh the handoff or leave a short mismatch note before the session ends so the next restart does not rediscover the same problem.

## Output Shape

At local-pickup time, produce:

- the chosen handoff path
- the canonical docs you relied on
- the verified current objective
- the verified workflow stage when the handoff captured it
- the immediate next action

Then begin the work.
