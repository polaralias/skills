---
type: Task
task: adopt-rke-okf-knowledge
title: Adopt RKE OKF knowledge format
description: Represent durable repository knowledge and migration evidence in the
  full RKE OKF format.
status: done
created: '2026-07-28T21:57:15Z'
timestamp: '2026-07-28T23:11:45Z'
owner: polaralias
time:
- id: 20260728t215716z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T21:57:16Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Adjusted allocation from one shared cross-repository migration and validation
    session; prevents duplicate portfolio effort.
  basis: 'Wall-clock session was 19 minutes. Active effort was adjusted to 2 minutes:
    Adjusted allocation from one shared cross-repository migration and validation
    session; prevents duplicate portfolio effort.'
  finished: '2026-07-28T22:16:19Z'
  elapsed_minutes: 19
  effort_minutes: 2
- id: 20260728t223505z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T22:35:05Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Adjusted allocation from one shared branch-rename, duplicate-removal, and
    exhaustive Markdown census session.
  basis: 'Wall-clock session was 4 minutes. Active effort was adjusted to 2 minutes:
    Adjusted allocation from one shared branch-rename, duplicate-removal, and exhaustive
    Markdown census session.'
  finished: '2026-07-28T22:39:03Z'
  elapsed_minutes: 4
  effort_minutes: 2
- id: 20260728t224139z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T22:41:39Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Applied and verified the skill-package Markdown exclusion in the exhaustive
    repository census.
  basis: 'Wall-clock session was 9 minutes. Active effort was adjusted to 1 minutes:
    Applied and verified the skill-package Markdown exclusion in the exhaustive repository
    census.'
  finished: '2026-07-28T22:50:28Z'
  elapsed_minutes: 9
  effort_minutes: 1
- id: 20260728t225603z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T22:56:03Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Generated, integrated, and validated repository-wide HTML and Mermaid OKF
    visualizations.
  basis: 'Wall-clock session was 16 minutes. Active effort was adjusted to 1 minutes:
    Generated, integrated, and validated repository-wide HTML and Mermaid OKF visualizations.'
  finished: '2026-07-28T23:11:42Z'
  elapsed_minutes: 16
  effort_minutes: 1
started: '2026-07-28T21:57:16Z'
effort_minutes: 6
completion_history:
- finished: '2026-07-28T22:17:46Z'
  reopened: '2026-07-28T22:35:05Z'
- finished: '2026-07-28T22:39:37Z'
  reopened: '2026-07-28T22:41:38Z'
- finished: '2026-07-28T22:50:30Z'
  reopened: '2026-07-28T22:56:02Z'
finished: '2026-07-28T23:11:45Z'
---

# Adopt RKE OKF knowledge format

## Outcome

Durable repository knowledge is represented with portable, plaintext OKF metadata, connected through an RKE-managed relationship graph, and kept distinct from operational Task state and specialised producer-owned schemas.

## Scope

- In scope: type and connect 8 durable knowledge documents; create and validate the bounded `docs/knowledge/` bundle; record this migration as an OKF Task; generate repository-wide HTML and Mermaid views.
- In scope: preserve canonical, evidence, derived, generated, instruction, handoff, fixture, and task boundaries.
- Out of scope: change product behaviour, upgrade support claims, rewrite historical evidence, publish externally, or alter generated/vendor content outside its owning workflow.

## Acceptance

- [x] Classify durable documents and deliberate schema exclusions.
- [x] Add required and recommended plaintext RKE OKF metadata.
- [x] Connect governed knowledge and execution concepts through repository-relative links.
- [x] Preserve reserved indexes and specialised document schemas.
- [x] Classify all 17 in-scope repository Markdown files with zero omissions; exclude 160 skill-package documents.
- [x] Remove the redundant repository overview and confirm zero exact duplicate governed knowledge bodies.
- [x] Build and validate the `docs/knowledge/` bundle.
- [x] Validate the OKF Tasks bundle in strict mode.
- [x] Generate repository-wide standalone HTML and scalable Mermaid visualizations with persisted exclusions.
- [x] Confirm skill-package documents retain their own schema and the upstream OKF Tasks implementation remains semantically feature-identical.

## Dependencies and risks

- The installed `okf-tasks 0.1.0` package is missing its task-body asset; the feature-identical bundled reference CLI is used instead.
- Metadata migration does not upgrade the evidential strength of existing repository claims.
- Existing manual indexes, generated documents, handoffs, fixtures, and skill packages retain their owning formats.

## Related knowledge

- [Documentation map](../../docs/knowledge/documentation-map.md)
- [Repository visualization](../../docs/knowledge/repository-visualization.md)

## Workstreams

- No separately owned workstreams are required.

## Evidence

- RKE bundle validation: conformant (3 concepts, 1 generated index).
- OKF Tasks strict validation: valid (1 task, 0 workstreams, 0 warnings).
- Visualization freshness: standalone HTML and Mermaid outputs match the repository records and persisted exclusion policy.
- Upstream lifecycle validation: 51 tests passed; generated skill index is current at repository version 5.19.0.
- Complete Markdown census: 17 in-scope files, 160 skill-package files excluded, 0 unclassified, 0 exact duplicate governed knowledge bodies.
