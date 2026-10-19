---
type: Interface Contract
title: Identity Events
description: Detailed dummy interface contract for identity events.
status: current
created: '2026-05-27T09:00:00Z'
timestamp: '2026-06-03T09:00:00Z'
navigation:
  role: supporting
  order: 510
tags:
- interface
- contract
- architecture-example
---

# Identity Events

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Tenant Service](../services/tenant-service.md)
- [Migration Service](../services/migration-service.md)
- [ADR 005: Transactional Outbox](../decisions/adr-005-transactional-outbox.md)
