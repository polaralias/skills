---
type: Interface Contract
title: Audit Event Contract
description: Detailed dummy interface contract for audit event contract.
status: current
created: '2026-05-30T09:00:00Z'
timestamp: '2026-06-06T09:00:00Z'
navigation:
  role: supporting
  order: 540
tags:
- interface
- contract
- architecture-example
---

# Audit Event Contract

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [Workflow Service](../services/workflow-service.md)
- [Audit Service](../services/audit-service.md)
- [ADR 014: Open Telemetry Signals](../decisions/adr-014-open-telemetry-signals.md)
