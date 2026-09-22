# Design Journey

Load this journey only when established end-state truth must become a bounded behavioural contract, acceptance surface, or implementation-ready work package.

## Entry and exit

Enter with enough verified truth to distinguish fact, assumption, unresolved decision, and downstream implementation detail. Exit only when observable acceptance is clear enough to guide delivery; entering the journey therefore registers `acceptance-defined` unless it is already outstanding.

## Sequence

1. Name the outcome and authoritative inputs. Label facts, assumptions, unresolved decisions, constraints, and non-goals separately.
2. Define the smallest coherent feature contract: outcome, scope, invariants, dependencies, boundaries, and observable success.
3. Pressure-test happy paths, edge conditions, failures, permissions, state transitions, retries, concurrency where relevant, and data-integrity expectations.
4. Build a scenario and verification matrix that connects each invariant and acceptance statement to happy-path, boundary, failure, permission, state-transition, retry, concurrency, and integrity coverage as relevant. This absorbs test planning without creating a separate QA capability.
5. Express acceptance through public behaviour rather than internal call order or private implementation structure. Include example inputs/outputs and observable completion signals where they reduce ambiguity.
6. Add technical planning only where it materially reduces implementation ambiguity: approved stack assumptions, module/API/data boundaries, migration and compatibility constraints, sequencing, research spikes, and risky integration surfaces. Do not turn design into speculative architecture inventory.
7. Create work packages only after the contract is strong enough. Each package needs purpose, prerequisites, acceptance, verification target, technical entrypoint where useful, open questions, and a downstream implementation target.
8. Preserve traceability from accepted end-state truth through feature, invariant, scenario, package, acceptance, and test or implementation target. Report gaps instead of manufacturing links.
9. Treat a stacked-review candidate as linear only when each lower layer is independently safe, useful, and testable. Otherwise prefer ordinary dependency relationships.

## Convergence contract

Add an experiment contract when the design depends on an uncertain technical or behavioural hypothesis, including LLM behaviour, retrieval strategy, orchestration, unfamiliar integrations, performance work, or migrations. Do not require it for a routine bounded correction.

Record:

- the problem being explained and the current hypothesis
- evidence supporting the hypothesis
- the governing assumption being tested
- the expected observable result
- the observation that would falsify the hypothesis
- the acceptance condition
- the maximum corrective attempts before reset, defaulting to two assumption-relevant failures
- the reset or kill condition

Count failures against the same governing assumption and acceptance condition, not every failed build. A typo, broken fixture, or unrelated integration fault is an implementation defect and does not consume the convergence limit.

When the limit is reached, stop delivery before repairing the next symptom. Capture what each attempt taught, return through `rke journey enter design`, and explicitly choose one outcome: reaffirm with new evidence, simplify or delete, replace, or abandon. Do not interpret design reconsideration as permission to add machinery by default. Keep the learning in the task, handoff, or canonical knowledge surface justified by its durability; `change explain` remains bounded to the Git delta.

## Output contract

Produce only the artefacts justified by scope: epic-to-feature decomposition, bounded feature contracts, invariants and non-goals, scenario/verification matrix, observable acceptance, proportionate technical plan, dependency and risk notes, implementation-ready work packages, open questions, a traceability summary, and a convergence contract only for genuinely exploratory work. Stable packages may be handed to OKF Tasks; tracker formatting and synchronization remain owned there.

## Decision boundary

Repository evidence can resolve implementation facts, but it cannot invent missing product authority. If an unresolved choice changes public behaviour, permissions, data integrity, or acceptance, keep `acceptance-defined` open and request the smallest coherent user decision.

## Handoff to delivery

Resolve `acceptance-defined` with a compact evidence receipt only after the behavioural contract is actually established. Add delivery gates such as `implementation-validation`, `integrated-tree-validation`, or `knowledge-impact-review` according to the accepted scope; do not resolve them merely because design is complete.
