# AI initiative lifecycle framework

## Phase 1: Discover and define

Start by making the opportunity explicit. The first phase should document the business problem, the current operating pattern, the value at stake, the likely data requirements, the success measures, the key risks, and the AI capability that might actually help.

This phase should end with a discovery artifact that answers the core questions directly. It is not the place to lead with POC or MVP design unless the user explicitly asks for later-stage material.

The core questions are:

- what does the user or process do today
- what problem is being solved
- what business impact does that problem create
- how is the work done now
- what time, cost, risk, rework, or delay is involved
- what would the AI need access to
- is the required data accessible, sensitive, reliable, and owned
- what does success look like
- how will success be measured

Also make visible:

- challenges
- underlying business problems
- success metrics
- risks
- high-risk or prohibited use cases and how they would be controlled
- which AI capability really applies

## Phase 2: Prioritise

Only prioritise after the discovery picture is explicit enough to score honestly. If the Phase 1 answers are weak, the correct move is more discovery or a reshaped initiative.

Typical prioritisation dimensions:

- business value
- strategic fit
- implementation complexity
- risk
- reuse potential
- data readiness
- stakeholder readiness

Useful heuristics:

- high value plus low or medium complexity often makes a strong early target
- high value plus high complexity may still be worth doing, but usually after dependency work
- low value plus low complexity is only worthwhile if it creates reusable learning or fast credibility
- low value plus high complexity is usually not worth progressing

## Phase 3: Deep dive and scope

This phase validates feasibility properly and defines the boundary between POC, MVP, and production.

Review:

- functional requirements
- non-functional requirements
- architecture direction
- POC and MVP boundaries
- legal, risk, and compliance position
- data assessment
- technical feasibility and complexity
- reusable patterns or building blocks

Maturity path:

- POC proves the riskiest assumption quickly
- MVP proves usable value in controlled scope
- Production adds supportability, security, observability, and maintainability

Do not skip stages unless there is already strong evidence from equivalent work.

## Decision gates

A strong go/no-go decision should normally cover:

1. technical feasibility is evidenced enough
2. POC success criteria are concrete
3. sponsor or leadership backing exists
4. data access and anonymisation expectations are defined
5. stakeholder alignment is strong enough to proceed

## Principles to preserve

- keep the path simple and structured
- prioritise before deep scoping
- design for reuse where it is real
- bring data and access concerns forward early
- filter weak ideas before they consume major effort
