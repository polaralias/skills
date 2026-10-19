---
type: Architecture Decision
title: 'Adr 019: Bounded Retry Policies'
description: 'Detailed dummy architecture decision for adr 019: bounded retry policies.'
status: proposed
created: '2026-05-07T09:00:00Z'
timestamp: '2026-05-14T09:00:00Z'
navigation:
  role: foundational
  order: 330
tags:
- adr
- decision
- architecture-example
---

# ADR 019: Bounded Retry Policies

## Context

The platform needs an explicit and reviewable choice for bounded retry policies. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Event Backbone](../architecture/event-backbone.md)
- [Previous decision: Migration Dual Read Window](./adr-018-migration-dual-read-window.md)
