---
type: "Future Consideration"
title: "Hook Setup Skill"
description: "Documents Hook Setup Skill for the skills repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - skills
  - future-consideration
navigation:
  role: reference
  order: 200
---
# Hook Setup Skill

This is a future-skill candidate.

## Why it is here

There is a reusable pattern around session-continuity hooks that is broader than engineering alone, but it is not yet clean enough to package as a standalone public skill.

For now, the shared user-level setup surface likely belongs in `setup-polaralias-skills`, while domain-specific skills such as `engineering-workflow-orchestrator` can adopt the pattern as a consumer.

## What seems reusable

- hook-aware continuity across compaction and resume
- deterministic artefact contracts between `PreCompact` and `PostCompact`
- transcript backup before compaction when the host exposes a durable thread artefact
- a derived handoff artefact that is explicitly marked as source-backed rather than authoritative raw record
- a machine-readable continuity manifest that multiple skills can consume
- a short post-compact restart supplement separate from the full verbose handoff
- clear evidence labelling such as `from transcript`, `from local files`, and `inferred`
- non-interactive behaviour for hook-driven execution

## Likely public version

A future public skill could be one of:

- `hook-setup-skill`
- `workflow-hook-setup`
- `agent-continuity-hook-setup`

The public version would probably:

- configure shared hook defaults outside installed skill folders
- install or draft project-local hook scaffolding for supported hosts
- define a continuity manifest schema
- define deterministic file naming for handoff and restart artefacts
- explain how downstream skills such as `local-handoff`, `local-pickup`, and orchestrators should consume those artefacts

## What it should do

- detect which host is being targeted such as Codex, Claude Code, or another agent runtime
- configure `SessionStart`, `PreCompact`, and `PostCompact` patterns where supported
- keep raw transcript backup, verbose handoff, and short restart supplement as separate artefact classes
- make `PostCompact` consume a computable manifest rather than searching heuristically
- enforce safe-to-commit handoff rules even when the raw source artefact is more sensitive
- stay thin and declarative rather than pretending hooks can replace the actual specialist skills

## Good pairing

This would pair well with:

- `setup-polaralias-skills` for shared user-level defaults and hook preferences
- `engineering-workflow-orchestrator` for engineering-stage continuity
- `local-handoff` for full handoff generation
- `local-pickup` for safe restart from the saved artefacts

## Why this belongs here

- the pattern is clearly reusable
- the boundaries between shared setup, artefact contract, and domain-specific orchestration still need refining
- it is worth preserving now without prematurely locking the package shape

## Repository knowledge

- [Documentation map](../docs/knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
