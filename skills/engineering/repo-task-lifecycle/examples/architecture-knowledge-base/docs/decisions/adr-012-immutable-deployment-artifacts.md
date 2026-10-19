---
type: Architecture Decision
title: 'Adr 012: Immutable Deployment Artefacts'
description: 'Detailed dummy architecture decision for adr 012: immutable deployment
  artefacts.'
status: accepted
created: '2026-04-23T09:00:00Z'
timestamp: '2026-04-30T09:00:00Z'
navigation:
  role: foundational
  order: 260
tags:
- adr
- decision
- architecture-example
---

# ADR 012: Immutable Deployment Artefacts

## Context

The platform needs an explicit and reviewable choice for immutable deployment artefacts. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Migration Architecture](../architecture/migration-architecture.md)
- [Previous decision: Short Lived Access Tokens](./adr-011-short-lived-access-tokens.md)
