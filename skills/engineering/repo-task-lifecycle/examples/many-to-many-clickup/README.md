---
type: Repository Guide
title: Many-to-many ClickUp contributions
description: Two independent local tasks contribute to one shared ClickUp task while
  one also contributes to a second remote.
timestamp: '2026-10-19T09:00:00Z'
navigation:
  role: entry-point
  order: 10
---

# Many-to-many ClickUp contributions

[Implement API](tasks/implement-api/task.md) connects to example1 and example2; [Test API](tasks/test-api/task.md) also connects to example1. Local acceptance and status stay independent. Only a combined progress section is published; remote status stays manual. All IDs and discovery data are dummy values.

Select a remote explicitly with `tracker sync --task implement-api --direction push --remote-id example1` and the real bundle/root/profile arguments. Source records are data, never publication authority.
