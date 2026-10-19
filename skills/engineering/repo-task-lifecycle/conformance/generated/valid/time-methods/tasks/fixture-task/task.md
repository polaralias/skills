---
type: Task
task: fixture-task
title: Fixture task
description: Exercise one portable task conformance rule.
status: ready
created: '2026-07-17T09:00:00Z'
timestamp: '2026-07-17T09:00:00Z'
started: '2026-07-17T09:00:00Z'
effort_minutes: 180
time:
- id: manual-entry
  status: closed
  actor: agent
  started: '2026-07-17T09:00:00Z'
  finished: '2026-07-17T10:00:00Z'
  elapsed_minutes: 60
  effort_minutes: 30
  method: manual
  activity: implementation
  basis: Explicit fixture values.
- id: adjusted-entry
  status: closed
  actor: agent
  started: '2026-07-17T09:00:00Z'
  finished: '2026-07-17T10:00:00Z'
  elapsed_minutes: 60
  effort_minutes: 60
  method: tracked-adjusted
  activity: implementation
  basis: Explicit fixture values.
- id: commit-review
  status: closed
  actor: agent
  started: '2026-07-17T09:00:00Z'
  finished: '2026-07-17T10:00:00Z'
  elapsed_minutes: 60
  effort_minutes: 90
  method: estimated-commit-review
  activity: implementation
  basis: Explicit fixture values.
  confidence: medium
  source_commits:
  - aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  estimation:
    session_gap_minutes: 90
    allowance_minutes: 30
    session_count: 1
    sessions:
    - started: '2026-07-17T09:00:00Z'
      finished: '2026-07-17T10:00:00Z'
      effort_minutes: 90
---

# Fixture task

## Outcome

Produce the stated outcome.

## Scope

- Included: the fixture contract.

## Acceptance

- [ ] The fixture is evaluated.

## Evidence

- Conformance fixture.
