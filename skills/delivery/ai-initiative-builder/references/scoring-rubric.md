# Scoring rubric

Use ratings to support judgement, not to simulate precision that the evidence does not justify. Every rating should carry an explanation of the evidence and the uncertainty behind it.

## Business value

High:

- clear connection to revenue, cost reduction, quality, risk reduction, customer value, delivery speed, or strategic capability
- measurable baseline or credible proxy exists
- the pain is frequent or materially costly

Medium:

- benefit is plausible but the baseline is weak, the audience is narrow, or the commercial value is only partly understood

Low:

- novelty-led, convenience-only, weakly owned, or without meaningful consequence

## Strategic fit

High:

- clearly supports active organisational, product, or operational priorities
- advances a known delivery, quality, customer, platform, or go-to-market goal

Medium:

- useful but not strongly tied to a live priority

Low:

- interesting but disconnected from the current direction

## Reuse potential

High:

- likely to create reusable data, prompts, workflows, APIs, tools, evaluation assets, security patterns, or operational playbooks
- could support multiple future initiatives

Medium:

- some transferable patterns exist, but the work is still strongly tied to one workflow

Low:

- largely a one-off

## Implementation complexity

High:

- many systems, unclear ownership, difficult integration, production-grade orchestration, complex architecture, or heavy change-management demand

Medium:

- meaningful integration or process change is needed, but existing patterns make it manageable

Low:

- contained workflow, accessible data, low integration burden, and simple operating model

## Data readiness

High:

- the data exists, is accessible, has an owner, is good enough, and can be used safely

Medium:

- the data probably exists, but access, quality, structure, or sensitivity still needs validation

Low:

- the data is unavailable, unowned, poor quality, highly sensitive, or impractical to use

## Risk

High:

- sensitive information, legal or compliance concerns, reputational downside, code/IP exposure, autonomous decisions, or very low tolerance for inaccuracy

Medium:

- risk is manageable with review, permissions, read-only design, redaction, logging, or human approval

Low:

- low sensitivity, low consequence, human-reviewed output, or internal exploratory use

## Adoption risk

High:

- users must significantly change behaviour, trust opaque outputs, or do extra work before value appears

Medium:

- some workflow change is needed, but there is clear sponsor pull or user benefit

Low:

- the initiative fits existing behaviour or removes an obvious pain

## Decision readiness

Ready:

- sponsor, decision maker, POC boundary, success metrics, data position, and next-step ask are all sufficiently clear

Nearly ready:

- one or two meaningful gaps remain, but the initiative can still be discussed honestly

Not ready:

- the problem, owner, data access, or success model is still too vague

## Technical feasibility deep-dive scale

The later deep-dive phase should usually score each of these from 0 to 10, where 0 is trivial and 10 is highly complex or risky:

1. Data availability
2. Ingestion and processing
3. Data quality and consistency
4. Integration complexity
5. Security and compliance
6. AI task complexity
7. Model complexity
8. Inference complexity
9. Overall architecture complexity
10. Scalability

Interpretation:

- 0-25: Quick
- 26-50: Medium
- 51-75: High
- 76-100: Complex

For a narrow POC, score only the POC-relevant scope rather than dragging in full production complexity prematurely.
