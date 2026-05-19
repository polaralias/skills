---
name: local-handoff
description: Create a local continuation handoff for the next Codex session. Use when ending a tranche of work and you want the next session to resume safely from a dated handoff stored alongside the work instead of a temp file.
---

# Local Handoff

Write a compact handoff near the work so the next session can resume without relying on chat history.

Prefer local discoverability over thread-local convenience.

## Workflow

### 1. Resolve the target working area

- Identify the project root from the current task context.
- Prefer the project being actively edited, not a separate notes area.
- Read `AGENTS.md`, `README.md`, or the canonical navigation doc when they exist so the handoff uses the project's own language.

### 2. Ensure local storage exists

- Use `.codex/handoffs/` under the project root.
- Create the directory if it does not exist.
- Keep handoffs untracked by default.

### 3. Wire ignore rules on first use

- If `.gitignore` exists and does not already ignore the handoff area, add an entry for `.codex/handoffs/`.
- If `.gitignore` does not exist, create it and add `.codex/handoffs/`.
- Do not ignore the entire `.codex/` tree unless the project already chose that policy.
- If the target is not a git repository, still use `.codex/handoffs/`, but note that ignore wiring could not be verified.

### 4. Name the handoff deterministically

- Use `YYYY-MM-DD-topic.md`.
- Derive `topic` from the user's stated next task when possible.
- If the next task is broad or unspecified, use `session-handoff`.
- Avoid random suffixes.

### 5. Write only the high-signal continuation context

The handoff should help the next agent answer:

- What was the goal of this tranche?
- What changed?
- What is still open?
- Which artifacts are canonical?
- What should happen first in the next session?

Prefer references over repetition:

- Link to plans, ADRs, specs, PRs, validation reports, or changed files instead of re-copying their contents.
- Summarize only the delta and the next-step logic.

### 6. Use this structure

```md
# Handoff: <topic>

## Session Goal

## Current State

## Canonical References

## Changes Made

## Open Issues Or Risks

## Suggested Next Step

## Suggested Skills
```

## Guardrails

- Keep the handoff short enough that a fresh agent will still read the linked docs.
- Do not duplicate large plan or spec content already captured elsewhere.
- Do not record secrets, tokens, credentials, private keys, cookies, or copied `.env` values in the handoff.
- If sensitive runtime context matters, describe where it lives and what kind of access is required instead of copying the value.
- Call out stale assumptions, partial verification, or unrun tests explicitly.
- If no files changed, say so directly.

## Relationship To Other Skills

- Use `pickup` to consume this artifact in the next session.
- Use `repository-dissection` when the current truth is still unclear.
- Use `repository-knowledge-engineering` when the next session is mainly about keeping code, tests, and docs aligned.
