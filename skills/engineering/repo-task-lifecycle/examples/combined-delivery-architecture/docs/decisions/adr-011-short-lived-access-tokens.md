---
type: Architecture Decision
title: 'Adr 011: Short Lived Access Tokens'
description: 'Detailed dummy architecture decision for adr 011: short lived access
  tokens.'
status: accepted
created: '2026-04-21T09:00:00Z'
timestamp: '2026-04-28T09:00:00Z'
navigation:
  role: foundational
  order: 250
tags:
- adr
- decision
- architecture-example
---

# ADR 011: Short Lived Access Tokens

## Context

The platform needs an explicit and reviewable choice for short lived access tokens. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Security Architecture](../architecture/security-architecture.md)
- [Previous decision: Central Policy Evaluation](./adr-010-central-policy-evaluation.md)
