---
type: Service Design
title: Migration Service
description: Detailed dummy service design for migration service.
status: current
created: '2026-05-14T09:00:00Z'
timestamp: '2026-05-21T09:00:00Z'
navigation:
  role: supporting
  order: 430
tags:
- service
- migration-service
- architecture-example
---

# Migration Service

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

- [Event Backbone](../architecture/event-backbone.md)
- [Migration Control Api](../interfaces/migration-control-api.md)
