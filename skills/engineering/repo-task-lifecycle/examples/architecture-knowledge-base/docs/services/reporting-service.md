---
type: Service Design
title: Reporting Service
description: Detailed dummy service design for reporting service.
status: current
created: '2026-05-18T09:00:00Z'
timestamp: '2026-05-25T09:00:00Z'
navigation:
  role: supporting
  order: 470
tags:
- service
- reporting-service
- architecture-example
---

# Reporting Service

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

- [Request Lifecycle](../architecture/request-lifecycle.md)
- [Identity Events](../interfaces/identity-events.md)
