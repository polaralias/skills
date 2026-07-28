---
type: "Future Consideration"
title: "Autofix candidate assessor"
description: "Documents Autofix candidate assessor for the skills repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - skills
  - future-consideration
navigation:
  role: reference
  order: 200
---
# Autofix candidate assessor

Status:
- not yet shaped as a public skill
- worth revisiting later as a fresh generic skill

Why it was not promoted now:
- too narrow in current form
- stronger as a generic automation-triage skill than as a one-off narrow package

What is worth preserving:

- the exclusion-gate idea before scoring
- the dimension-based rubric:
  - repro clarity
  - expected behaviour clarity
  - scope locality
  - technical directness
  - determinism
  - verification simplicity
  - coordination risk
- the downgrade logic for:
  - permissions or identity nuance
  - cross-system propagation
  - workflow/state-machine complexity
  - historical data repair
  - broad migrations
  - weak acceptance criteria
  - frontend/backend contract ambiguity

Likely future public shape:
- `autofix-candidate-assessor`
- or `bug-fix-automation-triager`

Likely future scope:
- assess whether a bug is suitable for AI-led or automated fixing
- score confidence without overclaiming
- separate ticket evidence from inference
- support single-ticket and batch triage

## Repository knowledge

- [Documentation map](../docs/knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
