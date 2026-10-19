---
type: Interface Contract
title: Reporting Query Api
description: Detailed dummy interface contract for reporting query api.
status: current
created: '2026-05-31T09:00:00Z'
timestamp: '2026-06-07T09:00:00Z'
navigation:
  role: supporting
  order: 550
tags:
- interface
- contract
- architecture-example
---

# Reporting Query Api

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Notification Service](../services/notification-service.md)
- [Reporting Service](../services/reporting-service.md)
- [ADR 017: Customer Managed Retention](../decisions/adr-017-customer-managed-retention.md)
