---
type: Quality Attribute
title: Recoverability
description: Detailed dummy quality attribute for recoverability.
status: current
created: '2026-06-08T09:00:00Z'
timestamp: '2026-06-15T09:00:00Z'
navigation:
  role: reference
  order: 630
tags:
- quality-attribute
- recoverability
- architecture-example
---

# Recoverability quality attribute

## Scenario

When the platform is under realistic load or partial failure, recoverability remains measurable through an explicit stimulus, environment, response, and response measure.

## Measures

| Measure | Target |
| --- | --- |
| Detection | Within five minutes |
| Recovery evidence | Linked to the affected service and decision |
| Review cadence | At every material architecture change |

## Design basis

- [Deployment Topology](../architecture/deployment-topology.md)
- [ADR 015: Error Budget Release Gates](../decisions/adr-015-error-budget-release-gates.md)
