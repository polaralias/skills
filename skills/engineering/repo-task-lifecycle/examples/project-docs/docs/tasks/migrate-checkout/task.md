---
type: Task
task: migrate-checkout
title: Migrate checkout traffic
description: Move checkout traffic to the new service with verified payment and order behaviour.
status: ready
created: 2026-07-17T15:00:00Z
timestamp: 2026-07-17T15:00:00Z
owner: checkout-team
---

# Migrate checkout traffic

## Outcome

The new checkout service handles production traffic without changing observable payment or order behaviour.

## Scope

- In scope: staged traffic migration and rollback validation.
- Out of scope: changes to payment-provider contracts.

## Acceptance

- [ ] Validate payment and order parity.
- [ ] Exercise rollback under production-like load.

## Dependencies and risks

- The durable project boundary is defined in [PROJECT.md](../../PROJECT.md).

## Related knowledge

- [Checkout migration project](../../PROJECT.md)

## Workstreams

- No separate workstreams yet.

## Evidence

- No implementation evidence yet.
