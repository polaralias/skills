---
type: Interface Contract
title: Public Api
description: Detailed dummy interface contract for public api.
status: current
created: '2026-05-26T09:00:00Z'
timestamp: '2026-06-02T09:00:00Z'
navigation:
  role: supporting
  order: 500
tags:
- interface
- contract
- architecture-example
---

# Public Api

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Identity Service](../services/identity-service.md)
- [Customer Service](../services/customer-service.md)
- [ADR 002: Versioned Event Envelope](../decisions/adr-002-versioned-event-envelope.md)
