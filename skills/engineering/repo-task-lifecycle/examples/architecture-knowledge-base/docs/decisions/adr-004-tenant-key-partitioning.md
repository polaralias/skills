---
type: Architecture Decision
title: 'Adr 004: Tenant Key Partitioning'
description: 'Detailed dummy architecture decision for adr 004: tenant key partitioning.'
status: accepted
created: '2026-04-07T09:00:00Z'
timestamp: '2026-04-14T09:00:00Z'
navigation:
  role: foundational
  order: 180
tags:
- adr
- decision
- architecture-example
---

# ADR 004: Tenant Key Partitioning

## Context

The platform needs an explicit and reviewable choice for tenant key partitioning. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Identity Boundary](../architecture/identity-boundary.md)
- [Previous decision: Oidc Workload Identity](./adr-003-oidc-workload-identity.md)
