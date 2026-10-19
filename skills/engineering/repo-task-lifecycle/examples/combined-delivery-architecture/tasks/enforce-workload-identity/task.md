---
type: Task
task: enforce-workload-identity
title: Enforce workload identity
description: Deliver enforce workload identity for the Identity Security initiative.
status: in-progress
created: '2026-06-13T08:00:00Z'
timestamp: '2026-06-13T12:00:00Z'
owner: team-identity-security
priority: medium
navigation:
  role: supporting
  order: 230
tags:
- identity-security
- complex-example
- wave-2
depends_on:
- add-privileged-access-reviews/task.md
- model-tenant-isolation/task.md
started: '2026-06-13T09:00:00Z'
effort_minutes: 120
time:
- id: 20260613t090000z-agent-tracked
  status: closed
  actor: agent
  started: '2026-06-13T09:00:00Z'
  finished: '2026-06-13T11:00:00Z'
  elapsed_minutes: 120
  effort_minutes: 120
  method: tracked
  activity: implementation
  summary: Advanced enforce workload identity in the dummy programme.
---

# Enforce workload identity

## Outcome

Deliver the observable result described by **enforce workload identity** and leave reviewable evidence for the next task.

## Scope

- In scope: implementation, validation, and handoff for this delivery slice.
- Out of scope: unrelated product changes and production credentials.

## Acceptance

- [ ] The result is demonstrable in the dummy programme environment.
- [ ] Relevant tests and operational evidence are linked.
- [ ] Follow-on tasks can consume the outcome without rediscovery.

## Dependencies and risks

- [Add Privileged Access Reviews](../add-privileged-access-reviews/task.md)
- [Model Tenant Isolation](../model-tenant-isolation/task.md)

## Related knowledge

- [Programme guidance](../../docs/identity-security.md)

## Evidence

- Dummy evidence will be attached as the task advances through validation.
