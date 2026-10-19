---
type: Service Design
title: Notification Service
description: Detailed dummy service design for notification service.
status: current
created: '2026-05-16T09:00:00Z'
timestamp: '2026-05-23T09:00:00Z'
navigation:
  role: supporting
  order: 450
tags:
- service
- notification-service
- architecture-example
---

# Notification Service

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

- [Security Architecture](../architecture/security-architecture.md)
- [Reporting Query Api](../interfaces/reporting-query-api.md)
