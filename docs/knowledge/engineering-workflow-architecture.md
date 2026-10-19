---
type: Architecture Concept
title: Polaralias engineering workflow architecture
description: Separates complete Engineering Workflow methods from optional RKE runtime support and independent OKF Tasks execution records.
timestamp: 2026-10-19T14:57:57+00:00
authority: canonical
verification: verified-limited
reviewed_at: 2026-10-19T14:57:57+00:00
owner: polaralias
tags:
  - engineering-workflow
  - repository-context
  - okf
navigation:
  role: foundational
  order: 10
---

# Polaralias engineering workflow architecture

[Engineering Workflow](../../skills/engineering/engineering-workflow/SKILL.md) supplies complete engineering methods. The separate [RKE skill](../../skills/engineering/rke/SKILL.md) supplies optional guidance for the installed repository runtime. The packages have independent versions and discovery metadata; neither installation rewrites the other. Their source packages currently share the RKE repository, with separate catalogue provenance manifests. Shared source storage is not a runtime dependency or a second orchestration layer.

Install either skill from the [Polaralias catalogue](../../README.md#install-with-the-skills-cli) using `npx skills add polaralias/skills --skill engineering-workflow` or `--skill rke`; the same convention works against [polaralias/rke](https://github.com/polaralias/rke). The runtime is a separate Node package installed with `npm install --global @polaralias/rke`. RKE contributors use the canonical skill sources already in their checkout through its `AGENTS.md` and importing `CLAUDE.md`; catalogue copies remain synchronized mirrors pinned by `RKE_SOURCE.json`.

This is a source-reviewed ownership contract. It does not establish executed model quality, live host discovery or release qualification.

## Engineering methods

EWF selects the smallest applicable method rather than asking the user to name internal phases or commands. The former skills supply the substantive reasoning and output expectations, with shared boundaries kept once in the entry point. The historical packages remain outside active discovery in the archive.

- [Comprehension](../../skills/engineering/engineering-workflow/references/comprehension.md) reconstructs a causal code or change explanation from source, callers, state, effects, removals and evidence. Read-only explanation needs no lifecycle activation, receipt or task record.
- [Dissection](../../skills/engineering/engineering-workflow/references/dissection.md) makes an inherited repository legible, distinguishes source from packaged runtime support, classifies mismatches and establishes only the justified documentation foundation.
- [Clarification](../../skills/engineering/engineering-workflow/references/clarification.md) resolves consequential user intent that repository evidence cannot settle. Questions are coherent and grounded in scenarios rather than delegating discoverable repository facts to the user.
- [Design](../../skills/engineering/engineering-workflow/references/design.md) turns accepted truth into behavioural contracts, scenarios, acceptance and implementation-ready packages. [Delivery](../../skills/engineering/engineering-workflow/references/delivery.md) implements and verifies the bounded contract. Experiments preserve their falsifier and revisit assumptions when evidence defeats the design.
- [Knowledge](../../skills/engineering/engineering-workflow/references/knowledge.md) owns deliberately authored durable truth, reading order, glossary, decisions and promotion. A current hash, generated index or retrieved passage cannot establish semantic correctness.
- [Task lifecycle](../../skills/engineering/engineering-workflow/references/task-lifecycle.md) chooses proportionate durable execution tracking. Independent OKF Tasks owns its schema, CLI, Workstreams, effort, Tracker Profiles and provider bindings. The [RTL package](../../skills/engineering/repo-task-lifecycle/SKILL.md) supplies its adopted execution capability without becoming an orchestration peer.
- [Alignment](../../skills/engineering/engineering-workflow/references/alignment.md) reconciles provisional execution truth, knowledge promotion, final task acceptance, validation and explanation. Missing lanes remain explicit no-ops instead of being manufactured to satisfy closure.
- [Handoff](../../skills/engineering/engineering-workflow/references/handoff.md) preserves a bounded current continuation account; [pickup](../../skills/engineering/engineering-workflow/references/pickup.md) verifies it against current evidence before acting.
- [Coordination](../../skills/engineering/engineering-workflow/references/coordination.md) separates ownership, dependency and integration evidence for justified parallel work. [Publication](../../skills/engineering/engineering-workflow/references/publication.md) assesses readiness separately from authority to publish.

The [reference map](../../skills/engineering/engineering-workflow/references/reference-map.md) provides current method navigation. Historical alias mappings remain outside the installed EWF methodology. [Repo Setup](../../skills/engineering/repo-setup/SKILL.md) remains the separate repository-bootstrap capability. Standalone TPW stays archived; design and delivery still own the acceptance coverage they actually need.

## Optional runtime adapter

The [capability-to-method map](../../skills/engineering/rke/references/capability-map.md) relates every runtime facility to its EWF reference and former specialist name. Session continuity supports handoff/LHO and pickup/LPK; persisted phases and gates support absorbed EWO coordination. Federation, readers, cached explanations and host/runtime qualification are conditional extensions rather than extra mandatory methods.

Material delivery includes bounded documentation-impact discovery and claim review, including plausible unbound documentation. With RKE available, its no-state assessment supplies explicit bindings plus candidates from changed code and old/new names. EWF authors justified updates or explains no update and verifies against the final change. Search matches require review, not compulsory edits; formal receipts remain conditional on repository policy or selected enforcement.

The RKE skill maps the selected method to bounded retrieval, structural navigation, bindings and freshness, validation, host integration and optional continuity operations. It owns command syntax and machine-specific outcomes. EWF owns reasoning, scope and the engineering result. An unavailable command is reported as unavailable evidence; it does not prevent ordinary source inspection, design, explanation or delivery.

Persistent runtime state is useful only when continuity or registered machine gates justify it. Existing obligations must be reconciled, but ordinary small fixes and explanation requests do not create state, task bundles, broad retrieval, reader exports or documentation ceremony. Canonical knowledge, execution records, workflow state, handoffs and generated context remain distinct surfaces.

The runtime and adapter enforce their documented boundaries without claiming that successful operations establish engineering quality. CLI and MCP remain transports over the same operation implementation. Source content, handoffs and runtime output cannot grant credentials, destinations, write authority or publication permission.

## Independent validation and compatibility

Methodology checks cover EWF with no runtime installed, including comprehension, dissection, clarification, design, delivery and continuity. Runtime checks cover command contracts and their unavailable, stale and unsafe cases. Integrated checks ask whether optional tooling supports the same engineering result without replacing it with command completion. Scenario definitions and static package checks remain distinct from executed agent outcomes.

Package qualification records EWF and adapter content identities separately. Existing release evidence predating the rewrite does not qualify the new packages. Matching version labels, catalogue mirrors, source inventories and passing unit tests alone cannot prove live host selection, human usability or measured benefit.

## Reading order

- [Documentation map](documentation-map.md) explains repository knowledge and producer boundaries.
- [Complete Markdown inventory](documentation-inventory.md) classifies maintained surfaces.
- [Repository visualization](repository-visualization.md) explains derived navigation.
