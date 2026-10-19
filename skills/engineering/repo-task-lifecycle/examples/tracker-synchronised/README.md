---
type: Knowledge Document
title: Tracker-synchronised bundle
description: Example of a repository task projected safely to an external tracker.
timestamp: 2026-07-19T12:00:00Z
navigation:
  role: entry-point
  order: 10
---
# Tracker-synchronised bundle

This example keeps the repository task canonical and records a Linear issue as an external projection. Provider API behaviour is not implied, but any adapter must prepare the exact outbound artefact according to sections 9.1 and 9.2 of the profile.

- [Inspect the audit-events task](./tasks/add-audit-events/task.md)

From the repository root, a safe body can be staged with:

```text
okf-tasks prepare-export --root . --source examples/tracker-synchronised/tasks/add-audit-events/task.md --output .okf-exports/add-audit-events.md
```

The ignored `.okf-exports/` staging directory is deliberately outside this example and should not be committed.
