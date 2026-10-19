---
type: Task
task: document-session-policy
title: Document the session rotation policy
description: Establish a canonical session rotation policy from verified implementation behaviour.
status: validation
created: 2026-07-17T09:00:00Z
timestamp: 2026-07-17T11:00:00Z
started: 2026-07-17T10:00:00Z
effort_minutes: 45
time:
  - id: 20260717t100000z-james-manual
    status: closed
    actor: james
    started: 2026-07-17T10:00:00Z
    finished: 2026-07-17T10:00:00Z
    elapsed_minutes: 0
    effort_minutes: 45
    method: manual
    summary: Manual entry for policy review and documentation work.
    basis: The contributor supplied 45 minutes of effort. Exact session boundaries were unavailable, so the timestamps are an approximate attribution point.
    activity: knowledge-maintenance
estimate:
  effort_minutes: 60
  method: manual
  confidence: high
  basis: One focussed review and documentation pass against verified behaviour.
  actor: james
  timestamp: 2026-07-17T09:55:00Z
sprint_points:
  value: 1
  scale: fibonacci
  context: platform-team
  timestamp: 2026-07-17T09:55:00Z
owner: platform-team
---

# Document the session rotation policy

## Outcome

The repository has an evidence-backed policy describing when and how sessions rotate.

## Scope

- In scope: authentication-time rotation and failure handling.
- Out of scope: refresh-token expiry policy.

## Acceptance

- [x] Verify current behaviour in tests.
- [x] Update the canonical architecture document.

## Dependencies and risks

- None.

## Related knowledge

- [Session architecture](../../docs/architecture/sessions.md)

## Workstreams

- No separate workstreams.

## Evidence

- Validation: session integration suite passed.
- Promotion: [Session architecture](../../docs/architecture/sessions.md) now records the verified policy.
- Effort: 45 manually recorded minutes covering policy review and documentation.
- Entry: [policy review session](./task.md#time:20260717t100000z-james-manual).
