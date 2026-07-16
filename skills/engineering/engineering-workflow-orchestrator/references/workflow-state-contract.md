# Workflow State Contract

Use this contract when `engineering-workflow-orchestrator` keeps a project-local workflow-state artifact or when it shapes hook-aware continuation behavior.

The record can live in any project-local path the repository already treats as durable session metadata.
Prefer a small JSON or YAML file over prose when a hook needs to read it.

## Required fields

- `workflow_stage`
- `current_skill`
- `next_skill`
- `canonical_refs`
- `verification_state`

## Optional fields

- `updated_at`
- `active_goal`
- `open_questions`
- `tracker_target`
- `handoff_path`
- `task_record`
- `workstream_record`
- `coordination_manifest`

## Example JSON

```json
{
  "workflow_stage": "doc-driven-development",
  "current_skill": "doc-driven-development",
  "next_skill": "query-to-knowledge",
  "canonical_refs": [
    "README.md",
    "docs/product-truth.md",
    "docs/plan/epic-a.md"
  ],
  "verification_state": "Epic truth aligned. Feature package drafted. Two terminology questions remain.",
  "updated_at": "2026-05-25T10:30:00Z",
  "active_goal": "Decompose reporting epic into implementation-ready work packages",
  "open_questions": [
    "Confirm whether exports must support CSV and XLSX in the first slice"
  ],
  "tracker_target": "Linear",
  "handoff_path": "local-docs/handoff/2026-05-25-reporting-epic.md"
}
```

## Handoff alignment

When `local-handoff` writes a workflow-aware handoff, keep these fields aligned with:

- `workflow_stage` -> `## Workflow State`
- `current_skill` -> `## Workflow State`
- `next_skill` -> `## Suggested Skills`
- `canonical_refs` -> `## Canonical References`
- `verification_state` -> `## Verification State`

## Guardrails

- keep the record short enough that hooks can read it cheaply
- do not duplicate long plan bodies or large specs
- update the record when the stage changes materially
- remove or de-emphasize stale `next_skill` values after the session takes a different path
- link to task or worktree records rather than copying their full state into the workflow record
- when the handoff is intentionally local-only, point `handoff_path` at the repo's `local-docs/` area rather than inventing a new ignore convention
