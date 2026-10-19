---
type: Architecture Decision
title: 'Adr 005: Transactional Outbox'
description: 'Detailed dummy architecture decision for adr 005: transactional outbox.'
status: accepted
created: '2026-04-09T09:00:00Z'
timestamp: '2026-04-16T09:00:00Z'
navigation:
  role: foundational
  order: 190
tags:
- adr
- decision
- architecture-example
---

# ADR 005: Transactional Outbox

## Context

The platform needs an explicit and reviewable choice for transactional outbox. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Tenant Isolation](../architecture/tenant-isolation.md)
- [Previous decision: Tenant Key Partitioning](./adr-004-tenant-key-partitioning.md)
