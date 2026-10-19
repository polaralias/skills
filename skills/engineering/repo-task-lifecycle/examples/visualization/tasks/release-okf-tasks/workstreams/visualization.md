---
type: Workstream
task: release-okf-tasks
workstream: visualization
title: Visualisation consumer
description: Render task relationships without becoming a source of truth.
status: in-progress
created: 2026-07-17T20:00:00Z
timestamp: 2026-07-17T21:00:00Z
owner: tooling-maintainer
branch: feat/visualization
---

# Visualisation consumer

## Assigned outcome

Users can inspect OKF Tasks as interactive HTML or GitHub-rendered Mermaid.

## Owned and shared paths

- Owned: scripts/visualize_bundle.py, docs/VISUALIZATION.md
- Shared: examples/visualization/

## Acceptance and validation

- [ ] Render structured and Markdown relationships.
- [ ] Sanitise rendered task bodies.
- [ ] Keep generated views reproducible.

## Evidence

- Commit: pending review.
- Validation: local unit tests.
- Integration: not published.

## Handoff

- Keep the viewer optional and provider-neutral.
