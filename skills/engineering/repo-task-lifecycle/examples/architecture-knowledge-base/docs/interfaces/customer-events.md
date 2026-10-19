---
type: Interface Contract
title: Customer Events
description: Detailed dummy interface contract for customer events.
status: current
created: '2026-05-28T09:00:00Z'
timestamp: '2026-06-04T09:00:00Z'
navigation:
  role: supporting
  order: 520
tags:
- interface
- contract
- architecture-example
---

# Customer Events

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Customer Service](../services/customer-service.md)
- [Workflow Service](../services/workflow-service.md)
- [ADR 008: Zero Downtime Database Change](../decisions/adr-008-zero-downtime-database-change.md)
