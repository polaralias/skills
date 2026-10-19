---
type: Task
task: fixture-task
title: Fixture task
description: Exercise one portable task conformance rule.
status: ready
created: '2026-07-17T09:00:00Z'
timestamp: '2026-07-17T09:00:00Z'
owner: agent
assignees:
- agent
- reviewer
priority: high
navigation:
  role: entry-point
  order: 10
tags:
- spec
estimate:
  effort_minutes: 180
  method: agent
  confidence: medium
  basis: Compared with similar work.
  actor: agent
  timestamp: '2026-07-17T09:00:00Z'
sprint_points:
  value: 3
  scale: fibonacci
  context: platform
  timestamp: '2026-07-17T09:00:00Z'
fields:
  risk:
    type: single-select
    value: high
  target-date:
    type: date
    value: '2026-08-01'
external:
- tracker: github-main
  system: github
  host: https://github.com
  kind: issue
  scope:
    id: R_main
    key: example/main
  id: I_issue_1
  key: '1'
  url: https://github.com/example/main/issues/1
  sync:
    remote_revision: revision-1
    base:
      remote: revision-1
producer_extension:
  preserve: true
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
