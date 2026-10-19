---
type: Task
task: second-task
title: Second task
description: Exercise one portable task conformance rule.
status: ready
created: '2026-07-17T09:00:00Z'
timestamp: '2026-07-17T09:00:00Z'
depends_on:
- fixture-task/task
external:
- tracker: github-other
  system: github
  host: https://github.com
  kind: issue
  scope:
    id: R_other
    key: example/other
  id: I_issue_2
  key: '1'
  url: https://github.com/example/other/issues/1
  sync:
    remote_revision: revision-1
    base:
      remote: revision-1
---

# Second task

## Outcome

Produce the stated outcome.

## Scope

- Included: the fixture contract.

## Acceptance

- [ ] The fixture is evaluated.

## Evidence

- Conformance fixture.
