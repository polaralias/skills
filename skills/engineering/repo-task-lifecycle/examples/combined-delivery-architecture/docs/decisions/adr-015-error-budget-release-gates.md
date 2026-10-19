---
type: Architecture Decision
title: 'Adr 015: Error Budget Release Gates'
description: 'Detailed dummy architecture decision for adr 015: error budget release
  gates.'
status: accepted
created: '2026-04-29T09:00:00Z'
timestamp: '2026-05-06T09:00:00Z'
navigation:
  role: foundational
  order: 290
tags:
- adr
- decision
- architecture-example
---

# ADR 015: Error Budget Release Gates

## Context

The platform needs an explicit and reviewable choice for error budget release gates. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

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

- [Request Lifecycle](../architecture/request-lifecycle.md)
- [Previous decision: Open Telemetry Signals](./adr-014-open-telemetry-signals.md)
