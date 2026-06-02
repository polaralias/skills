# Hook Setup Skill

This is a future-skill candidate.

## Why it is here

There is a reusable pattern around session-continuity hooks that is broader than engineering alone, but it is not yet clean enough to package as a standalone public skill.

For now, the shared user-level setup surface likely belongs in `setup-polaralias-skills`, while domain-specific skills such as `engineering-workflow-orchestrator` can adopt the pattern as a consumer.

## What seems reusable

- hook-aware continuity across compaction and resume
- deterministic artifact contracts between `PreCompact` and `PostCompact`
- transcript backup before compaction when the host exposes a durable thread artifact
- a derived handoff artifact that is explicitly marked as source-backed rather than authoritative raw record
- a machine-readable continuity manifest that multiple skills can consume
- a short post-compact restart supplement separate from the full verbose handoff
- clear evidence labeling such as `from transcript`, `from local files`, and `inferred`
- non-interactive behavior for hook-driven execution

## Likely public version

A future public skill could be one of:

- `hook-setup-skill`
- `workflow-hook-setup`
- `agent-continuity-hook-setup`

The public version would probably:

- configure shared hook defaults outside installed skill folders
- install or draft project-local hook scaffolding for supported hosts
- define a continuity manifest schema
- define deterministic file naming for handoff and restart artifacts
- explain how downstream skills such as `local-handoff`, `local-pickup`, and orchestrators should consume those artifacts

## What it should do

- detect which host is being targeted such as Codex, Claude Code, or another agent runtime
- configure `SessionStart`, `PreCompact`, and `PostCompact` patterns where supported
- keep raw transcript backup, verbose handoff, and short restart supplement as separate artifact classes
- make `PostCompact` consume a computable manifest rather than searching heuristically
- enforce safe-to-commit handoff rules even when the raw source artifact is more sensitive
- stay thin and declarative rather than pretending hooks can replace the actual specialist skills

## Good pairing

This would pair well with:

- `setup-polaralias-skills` for shared user-level defaults and hook preferences
- `engineering-workflow-orchestrator` for engineering-stage continuity
- `local-handoff` for full handoff generation
- `local-pickup` for safe restart from the saved artifacts

## Why this belongs here

- the pattern is clearly reusable
- the boundaries between shared setup, artifact contract, and domain-specific orchestration still need refining
- it is worth preserving now without prematurely locking the package shape
