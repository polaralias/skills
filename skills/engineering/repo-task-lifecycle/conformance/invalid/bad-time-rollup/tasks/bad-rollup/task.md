---
type: Task
task: bad-rollup
title: Bad time rollup
description: Demonstrate rejection of a task whose effort does not match its time entries.
status: in-progress
created: 2026-07-17T09:00:00Z
timestamp: 2026-07-17T10:00:00Z
started: 2026-07-17T09:00:00Z
effort_minutes: 120
time:
- id: 20260717t090000z-agent-tracked
  status: closed
  actor: agent
  started: 2026-07-17T09:00:00Z
  finished: 2026-07-17T10:00:00Z
  elapsed_minutes: 60
  effort_minutes: 60
  method: tracked
  activity: implementation
  summary: Valid time entry paired with an invalid parent rollup.
  basis: The explicit start and stop interval represents active work.
---

# Bad time rollup

## Outcome

This fixture must fail validation.

## Scope

- In scope: time rollup validation.

## Acceptance

- [ ] Validation fails.

## Evidence

- The task claims 120 minutes while its embedded entry records 60.
