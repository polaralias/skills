---
type: Service Design
title: Workflow Service
description: Detailed dummy service design for workflow service.
status: current
created: '2026-05-15T09:00:00Z'
timestamp: '2026-05-22T09:00:00Z'
navigation:
  role: supporting
  order: 440
tags:
- service
- workflow-service
- architecture-example
---

# Workflow Service

## Responsibilities

- Own the service's domain invariants and persistence boundary.
- Publish versioned events after durable state changes.
- Expose health, readiness, trace, and domain metrics.

## API and data ownership

| Surface | Contract |
| --- | --- |
| Commands | Authenticated, idempotent, and tenant-scoped. |
| Queries | Pagination and stable consistency semantics. |
| Events | Versioned envelope with correlation and causation IDs. |

## Dependencies

- [Resilience Model](../architecture/resilience-model.md)
- [Audit Event Contract](../interfaces/audit-event-contract.md)
