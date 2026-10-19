---
type: Quality Attribute
title: Availability
description: Detailed dummy quality attribute for availability.
status: current
created: '2026-06-05T09:00:00Z'
timestamp: '2026-06-12T09:00:00Z'
navigation:
  role: reference
  order: 600
tags:
- quality-attribute
- availability
- architecture-example
---

# Availability quality attribute

## Scenario

When the platform is under realistic load or partial failure, availability remains measurable through an explicit stimulus, environment, response, and response measure.

## Measures

| Measure | Target |
| --- | --- |
| Detection | Within five minutes |
| Recovery evidence | Linked to the affected service and decision |
| Review cadence | At every material architecture change |

## Design basis

- [Tenant Isolation](../architecture/tenant-isolation.md)
- [ADR 003: Oidc Workload Identity](../decisions/adr-003-oidc-workload-identity.md)
