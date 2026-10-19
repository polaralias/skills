---
type: Architecture Decision
title: 'Adr 013: Progressive Delivery'
description: 'Detailed dummy architecture decision for adr 013: progressive delivery.'
status: accepted
created: '2026-04-25T09:00:00Z'
timestamp: '2026-05-02T09:00:00Z'
navigation:
  role: foundational
  order: 270
tags:
- adr
- decision
- architecture-example
---

# ADR 013: Progressive Delivery

## Context

The platform needs an explicit and reviewable choice for progressive delivery. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [System Context](../architecture/system-context.md)
- [Previous decision: Immutable Deployment Artefacts](./adr-012-immutable-deployment-artifacts.md)
