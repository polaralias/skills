# AI initiative lifecycle framework

## Phase 1: Discover and define

The first phase should make the opportunity explicit before anyone starts scoring or scoping it. The aim is to document the business problem, the current way of working, the value at stake, the likely data requirements, the success conditions, the risks, and the type of AI capability that might actually help.

This phase should end with a discovery artifact that answers the core questions directly. It is not the place to jump ahead into POC or MVP design unless the user explicitly asks for a later-stage view.

Questions Phase 1 should answer in plain terms:

- what the current user or operational process looks like
- what problem is being addressed
- what business impact that problem creates
- how the work happens today
- what time, cost, risk, rework, or delay is currently absorbed
- what the AI-assisted solution would need access to
- whether the required data is accessible, sensitive, reliable, and owned
- what success should look like
- how that success would be measured

It should also surface:

- challenges
- underlying business problems
- measurable success indicators
- major risks
- high-risk or prohibited patterns and how they would be constrained
- which AI capability is actually relevant, if any

Use `references/discover-document-template.md` for the standard Phase 1 output.

Typical Phase 1 canvas fields include:

| Field | Intent |
|---|---|
| Initiative name | Short, clear, and outcome-oriented |
| Discovery summary | Separate the problem from the guessed solution |
| User/process today | Describe the current workflow |
| Problem statement | Name the pain clearly |
| Business impact | Show time, cost, quality, risk, or customer impact |
| Current process | Explain the status quo, including workarounds |
| Time/cost involved | Estimate current effort, delay, rework, or opportunity cost |
| AI needs | List documents, repos, tickets, data, tools, permissions, APIs, or models |
| Data access | Note confirmed, likely, blocked, or unknown data position |
| Success definition | Explain what a good outcome means operationally |
| Success metrics | Add measurable outcomes and baselines where possible |
| Risks | Cover accuracy, adoption, operational, legal, cost, security, and reputational concerns |
| High-risk/prohibited areas | Highlight sensitive data, autonomous decisions, code/IP, compliance, or uncontrolled sharing |
| Applicable AI capability | Retrieval, summarisation, classification, generation, analysis, code intelligence, agentic workflow, or deterministic automation |
| Open questions | Anything that materially affects the decision or scope |

## Phase 2: Prioritise

Only score an initiative once Phase 1 is sufficiently explicit. If the discovery picture is weak, recommend more discovery or a reshaped initiative before assigning scores.

Typical prioritisation dimensions:

- business value
- strategic fit
- implementation complexity
- risk
- reuse potential
- data readiness
- stakeholder readiness

Useful heuristics:

- high value plus low or medium complexity tends to make a strong first-wave candidate
- high value plus high complexity may still be worthwhile, but usually after dependency work
- low value plus low complexity is only worthwhile if it creates reusable learning or fast credibility
- low value plus high complexity is usually a poor candidate

## Phase 3: Deep dive and scope

This phase tests feasibility properly and sets boundaries for POC, MVP, and production.

Review areas include:

- functional requirements
- non-functional requirements
- architecture direction
- POC and MVP scope
- risk, legal, and compliance
- data landscape
- technical feasibility and complexity
- reusable building blocks

Maturity path:

- POC: prove the risky assumption quickly
- MVP: prove controlled, usable value
- Production: add supportability, security, observability, and operational depth

Do not skip stages unless equivalent evidence already exists.

## Decision gates

A strong go/no-go call should usually cover:

1. technical feasibility has been evidenced enough
2. POC success criteria are clear
3. leadership or sponsor backing exists
4. data access and anonymisation expectations are defined
5. stakeholder alignment is good enough to proceed

## Principles to carry through

- keep the workflow simple and structured
- force prioritisation before deep scoping
- design for reuse when it is genuine
- think about data and access early
- filter weak ideas out before they consume major effort
