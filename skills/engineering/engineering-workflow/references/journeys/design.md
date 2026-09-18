# Design Journey

Load this journey only when established end-state truth must become a bounded behavioural contract, acceptance surface, or implementation-ready work package.

## Entry and exit

Enter with enough verified truth to distinguish fact, assumption, unresolved decision, and downstream implementation detail. Exit only when observable acceptance is clear enough to guide delivery; entering the journey therefore registers `acceptance-defined` unless it is already outstanding.

## Sequence

1. Name the outcome and authoritative inputs. Label facts, assumptions, unresolved decisions, constraints, and non-goals separately.
2. Define the smallest coherent feature contract: outcome, scope, invariants, dependencies, boundaries, and observable success.
3. Pressure-test happy paths, edge conditions, failures, permissions, state transitions, retries, concurrency where relevant, and data-integrity expectations.
4. Express acceptance through public behaviour rather than internal call order or private implementation structure.
5. Add technical planning only where it materially reduces implementation ambiguity. Do not turn design into speculative architecture inventory.
6. Create work packages only after the contract is strong enough. Preserve traceability from accepted end-state truth through feature, package, acceptance, and test or implementation target.
7. Treat a stacked-review candidate as linear only when each lower layer is independently safe and useful. Otherwise prefer ordinary dependency relationships.

## Decision boundary

Repository evidence can resolve implementation facts, but it cannot invent missing product authority. If an unresolved choice changes public behaviour, permissions, data integrity, or acceptance, keep `acceptance-defined` open and request the smallest coherent user decision.

## Handoff to delivery

Resolve `acceptance-defined` with a compact evidence receipt only after the behavioural contract is actually established. Add delivery gates such as `implementation-validation`, `integrated-tree-validation`, or `knowledge-impact-review` according to the accepted scope; do not resolve them merely because design is complete.
