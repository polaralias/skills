---
type: Task
task: release-okf-tasks
title: Release OKF Tasks
description: Publish a validated OKF Tasks profile with reference tooling and examples.
status: in-progress
created: 2026-07-17T18:00:00Z
timestamp: 2026-07-17T21:00:00Z
started: 2026-07-17T19:30:00Z
effort_minutes: 90
time:
  - id: visualization-session
    status: closed
    actor: agent
    workstream: visualization
    started: 2026-07-17T19:30:00Z
    finished: 2026-07-17T21:00:00Z
    elapsed_minutes: 90
    effort_minutes: 90
    method: tracked
    summary: Implemented and validated the visualisation consumer.
    basis: Explicit start and finish around focussed implementation work.
    activity: implementation
owner: maintainers
tags:
  - release
  - standard
external:
  - tracker: github-main
    system: github
    host: https://github.com
    kind: pull-request
    scope:
      id: R_kgDOTbr1Iw
      key: polaralias/okf-tasks
    id: PR_kwDOTbr1I87zKuvU
    key: "4"
    url: https://github.com/polaralias/okf-tasks/pull/4
    sync:
      base: {}
---

# Release OKF Tasks

## Outcome

The profile, reference implementation, examples, and conformance suite are ready for public use.

## Scope

- In scope: specification, viewer, validation, and release evidence.
- Out of scope: provider-specific tracker adapters.

## Acceptance

- [ ] Validate the profile and both independent implementations.
- [ ] Publish human- and agent-readable examples.
- [ ] Provide derived visualisation without changing task truth.

## Dependencies and risks

- Interactive rendering loads pinned browser libraries from a CDN.

## Related knowledge

- [OKF Tasks specification](../../../SPEC.md)

## Workstreams

- [Specification and conformance](./workstreams/specification.md)
- [Visualisation consumer](./workstreams/visualization.md)

## Evidence

- [Focussed implementation session](./task.md#time:visualization-session)
