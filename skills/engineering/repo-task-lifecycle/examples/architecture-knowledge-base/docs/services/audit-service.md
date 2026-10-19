---
type: Service Design
title: Audit Service
description: Detailed dummy service design for audit service.
status: current
created: '2026-05-17T09:00:00Z'
timestamp: '2026-05-24T09:00:00Z'
navigation:
  role: supporting
  order: 460
tags:
- service
- audit-service
- architecture-example
---

# Audit Service

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

- [System Context](../architecture/system-context.md)
- [Public Api](../interfaces/public-api.md)
