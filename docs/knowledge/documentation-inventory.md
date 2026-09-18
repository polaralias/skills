---
type: Repository Documentation Inventory
title: "skills complete Markdown inventory"
description: "Classifies every in-scope tracked or pending Markdown file in the skills repository by OKF or approved specialised schema."
timestamp: 2026-09-18T00:00:00+01:00
authority: derived
verification: verified-working
verified_at: 2026-09-18T00:00:00+01:00
verified_against:
  - "rg --files -g *.md census: 20 in-scope, 133 active skill-package, and 52 archived skill-package Markdown files"
  - "python skills/engineering/engineering-workflow/scripts/engineering.py knowledge check --bundle docs/knowledge --root ."
owner: polaralias
generated_by: repo-knowledge-engineering-census
tags:
  - skills
  - documentation-inventory
navigation:
  role: supporting
  order: 30
---

# skills complete Markdown inventory

This is an exhaustive census of every in-scope tracked or pending Markdown file in this repository. Active skill package trees (`skills/**`) and preserved package interiors (`archive/*/**`), including `SKILL.md`, references, and tests, are deliberately excluded because they retain the skill-package schema. The governed `archive/README.md` boundary document remains in scope. This inventory proves that each in-scope file is either a typed OKF concept, an OKF reserved surface, or an explicitly classified specialised/producer-owned document. It does not duplicate the source content.

## Census result

- In-scope Markdown files: 20
- Excluded active skill-package files: 133
- Excluded archived skill-package files: 52
- Unclassified files: 0
- Exact duplicate governed knowledge bodies: 0

| Classification | Files |
|---|---:|
| Generated visualization | 1 |
| OKF execution concept | 1 |
| Archive boundary guide | 1 |
| OKF knowledge concept | 11 |
| Repository instruction | 3 |
| Reserved OKF navigation/history | 3 |

## Completeness

- No Markdown files are unclassified.

## Duplicate check

- No exact duplicate bodies were found among governed OKF knowledge concepts.

## Complete file inventory

| Path | Classification | Format status | Boundary rationale |
|---|---|---|---|
| [`AGENTS.md`](../../AGENTS.md) | Repository instruction | Specialised schema | Instruction authority remains outside factual knowledge |
| [`archive/README.md`](../../archive/README.md) | Archive boundary guide | Specialised schema | Defines the non-active historical package boundary without becoming a governed concept |
| [`CLAUDE.md`](../../CLAUDE.md) | Repository instruction | Specialised schema | Claude Code routing bridge imports repository instructions and points to the canonical skill catalogue |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Repository instruction | Specialised schema | Instruction authority remains outside factual knowledge |
| [`docs/knowledge/documentation-inventory.md`](documentation-inventory.md) | OKF knowledge concept | OKF | Repository Documentation Inventory |
| [`docs/knowledge/documentation-map.md`](documentation-map.md) | OKF knowledge concept | OKF | Repository Knowledge Map |
| [`docs/knowledge/engineering-workflow-architecture.md`](engineering-workflow-architecture.md) | OKF knowledge concept | OKF | Architecture Concept |
| [`docs/knowledge/index.md`](index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`docs/knowledge/repository-visualization.md`](repository-visualization.md) | OKF knowledge concept | OKF | Visualization |
| [`docs/visualizations/repository-okf.mermaid.md`](../visualizations/repository-okf.mermaid.md) | Generated visualization | Specialised schema | Derived Mermaid report; source records remain authoritative |
| [`future-consideration/autofix-candidate-assessor.md`](../../future-consideration/autofix-candidate-assessor.md) | OKF knowledge concept | OKF | Future Consideration |
| [`future-consideration/codebase-context-pack-builder.md`](../../future-consideration/codebase-context-pack-builder.md) | OKF knowledge concept | OKF | Future Consideration |
| [`future-consideration/company-context-pack-builder.md`](../../future-consideration/company-context-pack-builder.md) | OKF knowledge concept | OKF | Future Consideration |
| [`future-consideration/hook-setup-skill.md`](../../future-consideration/hook-setup-skill.md) | OKF knowledge concept | OKF | Future Consideration |
| [`future-consideration/qa-guidance-pack-builder.md`](../../future-consideration/qa-guidance-pack-builder.md) | OKF knowledge concept | OKF | Future Consideration |
| [`future-consideration/README.md`](../../future-consideration/README.md) | OKF knowledge concept | OKF | Navigation Guide |
| [`INDEX.md`](../../INDEX.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |
| [`README.md`](../../README.md) | OKF knowledge concept | OKF | Repository Guide |
| [`tasks/adopt-rke-okf-knowledge/task.md`](../../tasks/adopt-rke-okf-knowledge/task.md) | OKF execution concept | OKF | Task |
| [`tasks/index.md`](../../tasks/index.md) | Reserved OKF navigation/history | OKF exception | Reserved index.md/log.md schema |

## Repository knowledge

- [Documentation map](documentation-map.md) — RKE-managed reading order and relationship hub.
