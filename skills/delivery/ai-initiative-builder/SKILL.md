---
name: ai-initiative-builder
description: Guide early-stage AI initiative work through discovery and prioritisation. Use when a user wants to shape an idea, capture the right discovery questions, test whether it is worth pursuing, or produce a structured prioritisation view before deeper scoping begins.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-05-21'
---

# AI Initiative Builder

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `ai-initiative-builder was used in this response.`


Use this skill to turn a rough AI concept into a grounded Phase 1 or Phase 2 output. The job here is to sharpen the initiative, expose weak assumptions early, and decide whether it is ready to move forward. It is not the place to jump straight into POC design or proposal packaging.

## Stage ownership

This skill covers:

- discovery and initiative framing
- prioritisation and proceed-or-not-yet judgement

It does not cover:

- deep-dive feasibility workshops
- POC, MVP, or production scoping
- executive proposal packs
- implementation retrospectives

## Route to the right phase

Choose the smallest appropriate phase rather than generating the whole lifecycle by default.

| User intent | Primary output | Exclude unless asked |
|---|---|---|
| shape this idea, first pass, discovery, flesh this out, capture the initiative | discovery output | POC or MVP scope, formal recommendation pack, feasibility scoring |
| prioritise this, should we do it, rank it, proceed or not | prioritisation output | deep scoping detail unless needed to justify the judgement |
| deep dive, scope, POC, MVP, architecture, production path | handoff to Phase 3 scoping skill | full scoping work inside this skill |
| proposal, readout, board deck, slides | handoff to Phase 3 scoping skill | final decision-pack output here |
| retrospective, implementation review | out of scope | review output here |

For immature ideas, discovery comes first. Do not lead with recommendations or scope detail when the upstream understanding is still thin.

## Discovery mode

Use [discover-document-template.md](./references/discover-document-template.md) when the idea still needs shaping.

The discovery pass should make the following explicit:

- current user or process reality
- the problem to solve
- business consequences
- how the work is done now
- current time, cost, delay, risk, or rework
- what the AI system would actually need to access or handle
- whether that data is available, sensitive, reliable, and owned
- what success would look like
- how success would be measured
- known risks, exclusions, and prohibited patterns
- which AI capability is genuinely relevant

Unknowns stay unknown. Inference should be labelled as inference.

Discovery mode should close with:

1. discovery completeness
2. follow-up questions before prioritisation
3. discovery judgement
4. optional readiness signal
5. artifact recommendation

## Prioritisation mode

Use [scoring-rubric.md](./references/scoring-rubric.md) once the discovery answers are good enough to score honestly.

If the user asks to score too early, surface the missing information first or proceed only with clearly labelled assumptions.

When providing a prioritisation output, include a `Prioritisation assessment` section covering:

- business value
- strategic fit
- implementation complexity
- risk
- reuse potential
- data readiness
- adoption risk
- decision readiness

Then add:

- what supports the case
- what weakens the case
- what must be true before progressing
- the recommended next step

## Boundaries

This skill ends at:

- a usable discovery document or structured equivalent
- a prioritisation judgement
- a recommendation about whether the initiative is ready for Phase 3 scoping

If the user asks for POC, MVP, production path, proposal, or executive pack outputs, route to the later-stage scoping skill.

## Working rules

- challenge weak value cases, weak ownership, poor data position, and vague success criteria
- keep discovery, prioritisation, and scoping clearly separated
- mark inferred content and missing evidence openly
- keep the output reusable for later tracking without turning it into administrative overhead
- say plainly when the evidence is not strong enough yet
