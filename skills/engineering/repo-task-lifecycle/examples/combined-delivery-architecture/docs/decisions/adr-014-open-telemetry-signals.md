---
type: Architecture Decision
title: 'Adr 014: Open Telemetry Signals'
description: 'Detailed dummy architecture decision for adr 014: open telemetry signals.'
status: accepted
created: '2026-04-27T09:00:00Z'
timestamp: '2026-05-04T09:00:00Z'
navigation:
  role: foundational
  order: 280
tags:
- adr
- decision
- architecture-example
---

# ADR 014: Open Telemetry Signals

## Context

The platform needs an explicit and reviewable choice for open telemetry signals. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Container Topology](../architecture/container-topology.md)
- [Previous decision: Progressive Delivery](./adr-013-progressive-delivery.md)
