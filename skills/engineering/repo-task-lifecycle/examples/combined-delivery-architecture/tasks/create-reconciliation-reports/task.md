---
type: Task
task: create-reconciliation-reports
title: Create reconciliation reports
description: Deliver create reconciliation reports for the Data Migration initiative.
status: in-progress
created: '2026-06-22T08:00:00Z'
timestamp: '2026-06-22T12:00:00Z'
owner: team-data-migration
priority: medium
navigation:
  role: supporting
  order: 230
tags:
- data-migration
- complex-example
- wave-2
depends_on:
- build-change-data-capture-pipeline/task.md
- inventory-legacy-data-sources/task.md
started: '2026-06-22T09:00:00Z'
effort_minutes: 120
time:
- id: 20260622t090000z-agent-tracked
  status: closed
  actor: agent
  started: '2026-06-22T09:00:00Z'
  finished: '2026-06-22T11:00:00Z'
  elapsed_minutes: 120
  effort_minutes: 120
  method: tracked
  activity: implementation
  summary: Advanced create reconciliation reports in the dummy programme.
---

# Create reconciliation reports

## Outcome

Deliver the observable result described by **create reconciliation reports** and leave reviewable evidence for the next task.

## Scope

- In scope: implementation, validation, and handoff for this delivery slice.
- Out of scope: unrelated product changes and production credentials.

## Acceptance

- [ ] The result is demonstrable in the dummy programme environment.
- [ ] Relevant tests and operational evidence are linked.
- [ ] Follow-on tasks can consume the outcome without rediscovery.

## Dependencies and risks

- [Build Change Data Capture Pipeline](../build-change-data-capture-pipeline/task.md)
- [Inventory Legacy Data Sources](../inventory-legacy-data-sources/task.md)

## Related knowledge

- [Programme guidance](../../docs/data-migration.md)

## Evidence

- Dummy evidence will be attached as the task advances through validation.
