---
type: Architecture Decision
title: 'Adr 009: Regional Active Passive'
description: 'Detailed dummy architecture decision for adr 009: regional active passive.'
status: accepted
created: '2026-04-17T09:00:00Z'
timestamp: '2026-04-24T09:00:00Z'
navigation:
  role: foundational
  order: 230
tags:
- adr
- decision
- architecture-example
---

# ADR 009: Regional Active Passive

## Context

The platform needs an explicit and reviewable choice for regional active passive. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

## Decision

Adopt the named approach as the default architecture policy. Exceptions require a linked decision record that describes the narrower context and migration implications.

## Consequences

- Teams gain a consistent default and a visible dependency surface.
- Implementation work must preserve the documented compatibility boundary.
- Operational evidence becomes part of acceptance rather than a later activity.

<details>
<summary>Alternatives considered</summary>

Central coordination, implicit conventions, and provider-specific coupling were rejected because they weaken portability or make drift harder to review.

</details>

## Related architecture

- [Resilience Model](../architecture/resilience-model.md)
- [Previous decision: Zero Downtime Database Change](./adr-008-zero-downtime-database-change.md)
