# Discover and Document template

Use this template for the first structured output of a new or still-rough AI initiative. It is deliberately a discovery artifact, not a prioritisation paper and not a scoping proposal.

## Required Phase 1 output

# Phase 1: Discover and Document - [initiative name]

## 1. Discovery summary

Summarise the initiative in 2 to 4 sentences. Separate the underlying problem from the proposed answer. If the proposed solution is already being treated as fixed, say so.

## 2. Explicit discovery answers

| Discovery question | Current answer | Confidence | Follow-up needed |
|---|---|---:|---|
| What does the user's day/process look like today? |  | High/Medium/Low |  |
| What problem are we solving? |  | High/Medium/Low |  |
| What is the business impact? |  | High/Medium/Low |  |
| How is it done today? |  | High/Medium/Low |  |
| How much time, cost, risk, rework, or delay is involved? |  | High/Medium/Low |  |
| What would the AI need? |  | High/Medium/Low |  |
| Is the required data accessible? |  | High/Medium/Low |  |
| What does success look like? |  | High/Medium/Low |  |
| How will success be measured? |  | High/Medium/Low |  |

Rules:

- answer from the information available
- mark unknowns plainly instead of inventing them
- use confidence to distinguish evidence from inference or absence
- keep follow-up questions tied to gaps that would change the decision

## 3. Challenges and business problems

Separate symptoms from root problems.

| Type | Description | Evidence or source | Business consequence |
|---|---|---|---|
| Challenge |  |  |  |
| Business problem |  |  |  |

## 4. Success metrics

| Metric | Baseline | Target | Measurement method | Owner/source |
|---|---:|---:|---|---|
|  | Unknown if not provided |  |  |  |

Do not accept vague goals such as `improve productivity` unless they are translated into something measurable such as time saved, lower rework, reduced support demand, shorter cycle time, or better accuracy.

## 5. Data and access assessment

| Data/input needed | Why it is needed | Current access position | Sensitivity/risk | Owner or system |
|---|---|---|---|---|
|  |  | Confirmed/Likely/Blocked/Unknown | Low/Medium/High |  |

Also note whether the initiative depends on documents, repos, tickets, transcripts, customer data, analytics, APIs, metadata, logs, or other systems.

## 6. High-risk or prohibited use cases

| Risk/prohibited area | Applies? | Why | Mitigation or exclusion |
|---|---|---|---|
| Sensitive personal data | Yes/No/Unknown |  |  |
| Customer/confidential data | Yes/No/Unknown |  |  |
| Source code/IP exposure | Yes/No/Unknown |  |  |
| Automated decision-making | Yes/No/Unknown |  |  |
| Legal/compliance review needed | Yes/No/Unknown |  |  |
| Security-critical action | Yes/No/Unknown |  |  |
| Uncontrolled external model/data sharing | Yes/No/Unknown |  |  |

If a high-risk pattern appears, reshape the initiative around safer scope, human review, redaction, read-only access, audit logging, or explicit exclusion.

## 7. Applicable AI capability

Identify the actual capability family involved. Be explicit if the right answer may be something other than generative AI.

| Capability | Applies? | Notes |
|---|---|---|
| Retrieval/search over knowledge |  |  |
| Summarisation |  |  |
| Classification/routing |  |  |
| Draft generation |  |  |
| Analysis/reasoning over structured data |  |  |
| Coding/codebase intelligence |  |  |
| Agentic workflow/tool use |  |  |
| Deterministic automation better than AI |  |  |

## 8. Discovery judgement

Choose one:

- Ready for prioritisation
- Needs more discovery
- Reshape before prioritisation
- Do not continue

Explain why in plain language.

## 9. Follow-up questions

Ask no more than 3 to 5 questions, and only where the answers would materially affect value, feasibility, risk, scope, or measurement.

## 10. Artefact offer

If the discovery picture is coherent enough, offer a Phase 1 discovery document. If not, say what needs answering first.

## Phase discipline rules

For initial scaffold, first pass, or rough assessment requests:

- start with this Phase 1 document
- do not open with recommendation or proceed-to-POC language
- do not include POC scope, MVP scope, architecture detail, technical feasibility scoring, production path, or a decision ask unless the user explicitly wants them
- if you include an early directional view, put it at the end as an `Initial readiness signal` and mark it as provisional

Suggested ending:

## Discovery completeness

Summarise what is evidenced, inferred, and still missing.

## Follow-up questions before prioritisation

Ask only the few questions that would change the judgement.

## Discovery judgement

Choose Ready for prioritisation, Needs more discovery, Reshape before prioritisation, or Do not continue.

## Initial readiness signal

Optional. Keep it clearly provisional.

## Artefact offer

Offer a Phase 1 document if the initiative is coherent enough to benefit from one.
