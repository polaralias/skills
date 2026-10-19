---
type: Architecture Decision
title: 'Adr 008: Zero Downtime Database Change'
description: 'Detailed dummy architecture decision for adr 008: zero downtime database
  change.'
status: accepted
created: '2026-04-15T09:00:00Z'
timestamp: '2026-04-22T09:00:00Z'
navigation:
  role: foundational
  order: 220
tags:
- adr
- decision
- architecture-example
---

# ADR 008: Zero Downtime Database Change

## Context

The platform needs an explicit and reviewable choice for zero downtime database change. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Deployment Topology](../architecture/deployment-topology.md)
- [Previous decision: Schema Registry Compatibility](./adr-007-schema-registry-compatibility.md)
