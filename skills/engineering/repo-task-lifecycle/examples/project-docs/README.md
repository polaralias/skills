---
type: Knowledge Document
title: Project documentation placement
description: Example placing operational task records beneath established project documentation.
timestamp: 2026-07-19T12:00:00Z
navigation:
  role: entry-point
  order: 10
---
# Project documentation placement

This example uses `docs/tasks/` because the repository's `docs/` tree is already the home for an actual project's context and delivery material. `docs/PROJECT.md` remains durable project knowledge; `docs/tasks/` contains operational execution state.

- [Inspect the checkout migration task](./docs/tasks/migrate-checkout/task.md)

Initialise this placement with:

```text
okf-tasks init-bundle --root . --placement docs
```

Use `--bundle docs/tasks` for subsequent lifecycle commands.
