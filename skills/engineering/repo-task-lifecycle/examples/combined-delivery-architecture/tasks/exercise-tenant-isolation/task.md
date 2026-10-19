---
type: Task
task: exercise-tenant-isolation
title: Exercise tenant isolation
description: Deliver exercise tenant isolation for the Architecture initiative.
status: in-progress
created: '2026-06-17T09:00:00Z'
timestamp: '2026-06-17T13:00:00Z'
owner: team-architecture
priority: medium
navigation:
  role: supporting
  order: 220
tags:
- architecture
- complex-example
- wave-2
depends_on:
- prototype-the-event-backbone/task.md
started: '2026-06-17T10:00:00Z'
effort_minutes: 120
time:
- id: 20260617t100000z-agent-tracked
  status: closed
  actor: agent
  started: '2026-06-17T10:00:00Z'
  finished: '2026-06-17T12:00:00Z'
  elapsed_minutes: 120
  effort_minutes: 120
  method: tracked
  activity: implementation
  summary: Advanced exercise tenant isolation in the dummy programme.
---

# Exercise tenant isolation

## Outcome

Deliver the observable result described by **exercise tenant isolation** and leave reviewable evidence for the next task.

## Scope

- In scope: implementation, validation, and handoff for this delivery slice.
- Out of scope: unrelated product changes and production credentials.

## Acceptance

- [ ] The result is demonstrable in the dummy programme environment.
- [ ] Relevant tests and operational evidence are linked.
- [ ] Follow-on tasks can consume the outcome without rediscovery.

## Dependencies and risks

- [Prototype The Event Backbone](../prototype-the-event-backbone/task.md)

## Related knowledge

- [Programme guidance](../../docs/architecture/tenant-isolation.md)

## Evidence

- Dummy evidence will be attached as the task advances through validation.

## Decision evidence

- [ADR 007: Schema Registry Compatibility](../../docs/decisions/adr-007-schema-registry-compatibility.md)
