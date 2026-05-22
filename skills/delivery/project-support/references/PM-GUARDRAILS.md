# Project Management Guardrails

## Core assumptions

- `PROJECT.md` is the canonical context layer for real projects
- the index or parent metadata is the lookup anchor
- boards represent execution state, not full project truth
- durable project artifacts should live in a stable shared repository

## Good PM discipline

- define outcomes, not just deliverables
- keep scope and non-scope explicit
- challenge unrealistic dates, weak ownership, and hidden dependencies
- separate enduring context from moving status
- record material decisions and rationale
- avoid duplicating the same truth across several systems without a reason
- prefer authoritative artifacts over memory or chat fragments
- call out stale, contradictory, or weakly evidenced context

## Routing expectations

- no `PROJECT.md` for a real project means route to `project-context-builder`
- handoff pack or context bundle work means route to `project-packager`
- reporting work means route to `project-report-writer`
- workspace-oriented navigation can use `SPACE.md`, but only when it exists

## Anti-patterns

- inventing canonical context from weak evidence
- treating a task board as sufficient project definition
- letting changing sections accumulate stale history
- rewriting stable project sections casually during support or packaging
- presenting guesswork as settled fact
