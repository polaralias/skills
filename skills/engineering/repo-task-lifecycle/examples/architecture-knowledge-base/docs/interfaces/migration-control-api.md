---
type: Interface Contract
title: Migration Control Api
description: Detailed dummy interface contract for migration control api.
status: current
created: '2026-05-29T09:00:00Z'
timestamp: '2026-06-05T09:00:00Z'
navigation:
  role: supporting
  order: 530
tags:
- interface
- contract
- architecture-example
---

# Migration Control Api

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Migration Service](../services/migration-service.md)
- [Notification Service](../services/notification-service.md)
- [ADR 011: Short Lived Access Tokens](../decisions/adr-011-short-lived-access-tokens.md)
