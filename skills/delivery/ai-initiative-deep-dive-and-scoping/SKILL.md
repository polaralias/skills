---
name: ai-initiative-deep-dive-and-scoping
description: Lead the late-stage validation and scoping pass for an AI initiative, including feasibility analysis, POC and MVP boundaries, production-readiness framing, proposal content, and decision-pack outputs. Use when a prioritised initiative is ready for structured challenge rather than early discovery or idea generation.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-05-21'
---

# AI Initiative Deep Dive and Scoping

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `ai-initiative-deep-dive-and-scoping was used in this response.`


Use this skill once an initiative has already survived discovery and prioritisation. Its purpose is to reduce uncertainty enough for a credible proceed, reshape, defer, or stop decision.

## What this stage owns

This stage is responsible for:

- translating a prioritised idea into a testable scope
- assessing feasibility across data, architecture, security, compliance, and delivery
- drawing hard boundaries between POC, MVP, and production
- packaging the work into recommendation-ready artifacts

This is not the right skill for raw brainstorming or loose first-pass triage.

## Minimum context before scoping

Confirm or reconstruct enough context to avoid fictional scope. At minimum, look for:

- the use case in plain language
- the business problem or operational opportunity
- an accountable sponsor or owner
- the value being sought
- the current-state process
- a first view of risk and constraints
- the likely data sources and access position

If these are weak, call out the missing pieces and either label assumptions clearly or recommend a return to earlier-stage work.

## Stage method

Use [references/framework.md](./references/framework.md) as the backbone. The output from this stage should cover:

- required outcomes and constraints
- solution shape and architectural direction
- the practical data position
- legal, privacy, security, and compliance concerns
- assumptions, dependencies, and blockers
- a POC definition
- an MVP definition
- a production path
- measurable success criteria
- explicit go or no-go gates

The standard is disciplined scoping, not optimistic selling.

## Feasibility model

Score each of these areas out of 10 and explain the reasoning:

1. Data availability
2. Data ingestion and processing
3. Data quality and consistency
4. Integration complexity
5. Security and compliance
6. AI task complexity
7. Model complexity
8. Inference complexity
9. Overall architecture complexity
10. Scalability

Show the total out of 100 and classify it:

- `Quick` for 0-25
- `Medium` for 26-50
- `High` for 51-75
- `Complex` for 76-100

Where evidence is weak, say so rather than pretending the score is settled.

## Standard deliverables

Use the references that fit the output the user needs:

- [framework.md](./references/framework.md)
- [proposal-template.md](./references/proposal-template.md)
- [slide-deck-template.md](./references/slide-deck-template.md)

Unless the user narrows the request, the scoping pack should cover:

- problem and opportunity
- proposed AI-enabled approach
- stakeholder map
- business-case basics
- POC purpose and boundary
- MVP scope and operating model
- production-readiness view
- data position and risk posture
- major dependencies and assumptions
- recommendation and next gate

## Decision framing

Make the decision criteria overt. A proceed decision should normally require:

1. Technical feasibility is sufficiently evidenced.
2. POC success measures are concrete.
3. The business case is supportable by sponsor or leadership.
4. Data access and anonymisation expectations are understood.
5. The required stakeholders are aligned enough to proceed.

If one of these is missing, name the blocker and the smallest next action that would clear it.

## Reuse lens

Every substantial scoping output should include a short view on reusable assets, for example:

- repeatable patterns
- reusable components
- shared integration work
- operational practices worth standardising

That reuse view is part of the initiative case, not optional decoration.

## Operating rules

- challenge unsupported optimism
- separate evidence from assumption
- keep POC, MVP, and production boundaries distinct
- treat sensitive data and access constraints as first-class design inputs
- stay decision-oriented instead of drifting into unnecessary implementation detail
