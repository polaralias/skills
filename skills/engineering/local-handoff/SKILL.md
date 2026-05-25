---
name: local-handoff
description: Create a local continuation handoff for the next session. Use when you are ending a tranche of work and want the next session to resume safely from a dated handoff stored alongside the work instead of a temp file, especially when the handoff should preserve the current engineering workflow stage for the next resume. Shorthand LHO.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.3.1
  updated: '2026-05-25'
---

# local-handoff

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `local-handoff was used in this response.`

Write a compact handoff near the work so the next session can resume without relying on chat history.

Prefer local discoverability over thread-local convenience.

## Workflow

### 1. Resolve the target working area

- Identify the project root from the current task context.
- Prefer the project being actively edited, not a separate notes area.
- Read `AGENTS.md`, `README.md`, or the canonical navigation doc when they exist so the handoff uses the project's own language.

### 2. Ensure local storage exists

- Use `docs/handoff/` under the project root by default.
- Create the directory if it does not exist.

If the repository already has an established continuous handoff folder, use that instead of creating a parallel convention.

### 3. Name the handoff deterministically

- Use `YYYY-MM-DD-topic.md`.
- Derive `topic` from the user's stated next task when possible.
- If the next task is broad or unspecified, use `session-handoff`.
- Avoid random suffixes.

Before creating a new file, check whether a same-day handoff already exists for the same stream of work.

- If the session is continuing the same tranche, prefer updating the existing handoff.
- If the goal or phase changed materially, create a new handoff file.
- If a new handoff supersedes an older one, say so explicitly.

### 4. Write only the high-signal continuation context

The handoff should help the next agent answer:

- What was the goal of this tranche?
- What changed?
- What is still open?
- Which workflow stage were we in?
- Which artifacts are canonical?
- What should happen first in the next session?

Prefer references over repetition:

- Link to plans, decision docs, specs, PRs, validation reports, or changed files instead of re-copying their contents.
- Summarize only the delta and the next-step logic.
- Read the destination file before overwriting it.

### 5. Use this structure

```md
# Handoff: <topic>

## Session Goal

## Current State

## Verification State

## Workflow State

## Canonical References

## Changes Made

## Open Issues Or Risks

## Suggested Next Step

## Suggested Skills
```

## Guardrails

- If the current work follows an explicit multi-skill engineering flow, capture:
  - current workflow stage
  - current skill
  - next likely skill
- Keep workflow-state short and aligned with any separate workflow metadata the repository maintains.
- Keep the handoff short enough that a fresh agent will still read the linked docs.
- Do not duplicate large plan or spec content already captured elsewhere.
- Do not copy large diffs or long plan bodies into the handoff.
- Never record secrets, tokens, credentials, private keys, cookies, copied `.env` values, or any other sensitive values in the handoff.
- The handoff must be safe to share as a document even if the user later decides to commit or publish it accidentally.
- If sensitive runtime context matters, describe where it lives and what kind of access is required instead of copying the value.
- Call out stale assumptions, partial verification, or unrun tests explicitly.
- Record branch or worktree assumptions when the next session could land in the wrong context.
- Record whether the next session depends on local uncommitted state.
- If no files changed, say so directly.
- Do not create a handoff when the tranche is truly complete and canonical docs plus commits already make continuation obvious.

## Closing Step

Once the handoff is complete:

- tell the user the handoff is complete
- tell them the exact handoff path
- remind them that if they do not want to share handoff documents, they may want to add that handoff path to the target repository's `.gitignore`

## Relationship To Other Skills

- Use `local-pickup` to consume this artifact in the next session.
- Use `engineering-workflow-orchestrator` when the next session should restart through a coordinated stage model or hook-aware workflow.
- Use `repo-dissection` when the current truth is still unclear.
- Use `repo-knowledge-engineering` when the next session is mainly about keeping repository truth surfaces aligned after implementation or validation work.
