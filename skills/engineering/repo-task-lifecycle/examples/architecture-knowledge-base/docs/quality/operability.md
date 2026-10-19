---
type: Quality Attribute
title: Operability
description: Detailed dummy quality attribute for operability.
status: current
created: '2026-06-09T09:00:00Z'
timestamp: '2026-06-16T09:00:00Z'
navigation:
  role: reference
  order: 640
tags:
- quality-attribute
- operability
- architecture-example
---

# Operability quality attribute

## Scenario

When the platform is under realistic load or partial failure, operability remains measurable through an explicit stimulus, environment, response, and response measure.

## Measures

| Measure | Target |
| --- | --- |
| Detection | Within five minutes |
| Recovery evidence | Linked to the affected service and decision |
| Review cadence | At every material architecture change |

## Design basis

- [Resilience Model](../architecture/resilience-model.md)
- [ADR 019: Bounded Retry Policies](../decisions/adr-019-bounded-retry-policies.md)
