---
name: local-handoff
description: Create a local continuation handoff for the next session. Use when you are ending a tranche of work and want the next session to resume safely from a dated handoff stored alongside the work instead of a temp file, especially when the handoff should preserve the current engineering workflow stage for the next resume. Shorthand LHO.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.4.0
  updated: '2026-06-02'
---

# local-handoff

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `local-handoff was used in this response.`

Write a local handoff near the work so the next session can resume without relying on chat history.

Prefer local discoverability over thread-local convenience.

## Modes

Two modes are supported. Default to **standard** unless the trigger for **max-verbosity** is clear.

- **standard**: compact continuation handoff. Prefer references over repetition.
- **max-verbosity**: self-contained continuation handoff. Expand the same core structure with enough inline detail that the next session can act safely even if thread context or linked artifacts are less available.

Choose **max-verbosity** when:

- the user explicitly asks for a detailed, verbose, exhaustive, or standalone handoff
- the shorthand `LHO max` is used
- the handoff crosses a meaningful phase boundary such as test to production
- the handoff is being written for a reader who was not part of the current session
- a hook-driven continuity flow explicitly requests max mode

When the trigger is ambiguous, use **standard** and offer max-verbosity only if the next step clearly benefits from it.

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

### 4. Choose the depth and write the continuation context

The handoff should help the next agent answer:

- What was the goal of this tranche?
- What changed?
- What is still open?
- Which workflow stage were we in?
- Which artifacts are canonical?
- What should happen first in the next session?

In **standard** mode:

- Link to plans, decision docs, specs, PRs, validation reports, or changed files instead of re-copying their contents.
- Summarize only the delta and the next-step logic.
- Read the destination file before overwriting it.

In **max-verbosity** mode:

- Keep the same section backbone, but expand it with source-backed operational detail.
- Prefer inline summaries plus links, not links alone, when the linked material is necessary to act safely.
- Prioritize the details that most reduce restart risk:
  - exact current state
  - verification evidence
  - workflow state
  - open risks
  - next-step sequence
- If time or context budget is constrained, preserve the highest-value continuation detail first instead of attempting a perfect exhaustive dump.
- Distinguish clearly between:
  - observed from files, tools, or command output
  - inherited from the current session or handoff inputs
  - inferred by the model

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

### 5b. Max-verbosity expansion

In **max-verbosity** mode, keep the standard section structure as the backbone and expand each section only as far as the work justifies.

- **Session Goal**: include the immediate goal and the surrounding context a new reader needs.
- **Current State**: use exact identifiers, paths, hosts, branches, counts, and concrete status where available.
- **Verification State**: say what was checked, how it was checked, what evidence exists, and what remains unverified.
- **Workflow State**: capture current stage, current skill, next likely skill, and any active continuity assumptions.
- **Canonical References**: give the references and a short inline summary of why each one matters.
- **Changes Made**: record meaningful deltas, not long diffs.
- **Open Issues Or Risks**: separate hard blockers, risky assumptions, and follow-up checks.
- **Suggested Next Step**: make the first next action concrete and ordered.
- **Suggested Skills**: call out only the skills that are genuinely likely to help next.

Append these sections only when they materially help the next session:

```md
## A. Glossary And Domain Model
## B. Environment And Access
## C. Mechanics That Bite
## D. Interface, API, Or Command Reference
## E. Tooling
## F. Inputs And Data Pipeline
## G. Decision Rulebook
## H. Chronology
## I. Environment Differences
## J. Next-Phase Checklist
## K. Quick Command Reference
```

The quality bar for max mode is not "include everything touched." The quality bar is "preserve enough source-backed detail that a competent next operator can restart safely without guessing."

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

## Max-Verbosity Guardrails

These apply in addition to the main guardrails:

- Self-contained does not mean secret-complete. Never paste secrets, copied credentials, cookies, `.env` values, or similar sensitive material into the handoff.
- Prefer durable operational detail over raw dumps. Do not paste large logs or command output when a precise summary is safer and more useful.
- State the handoff's as-of point when using max mode, ideally with date, time, branch, and commit when known.
- Mark environment-specific facts explicitly so the next session does not over-generalize from one environment to another.
- Prefer exact values from artifacts, commands, and files over recalled values. Flag recalled or uncertain details plainly.
- Omit appendices that do not materially improve restart safety.
- If invoked through a non-interactive continuity flow, do not block on questions. Use the strongest available evidence and note any missing inputs.

## Closing Step

Once the handoff is complete:

- tell the user the handoff is complete
- tell them the exact handoff path
- for max-verbosity handoffs, tell them it is a point-in-time reference that should be re-verified before acting on environment-sensitive steps
- remind them that if they do not want to share handoff documents, they may want to add that handoff path to the target repository's `.gitignore`

## Relationship To Other Skills

- Use `local-pickup` to consume this artifact in the next session.
- Use `engineering-workflow-orchestrator` when the next session should restart through a coordinated stage model or hook-aware workflow.
- Use `repo-dissection` when the current truth is still unclear.
- Use `repo-knowledge-engineering` when the next session is mainly about keeping repository truth surfaces aligned after implementation or validation work.
