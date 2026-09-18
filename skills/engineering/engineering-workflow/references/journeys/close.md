# Close Journey

Load this journey for material-work reconciliation before completion or merge consideration. Entering it changes the control phase but does not invent, waive, or resolve gates. Use `closure assess` to explain current lanes and `close` only after their evidence-backed gates are resolved.

## Bound change explanation

Establish the actual final delta before explaining it. Reconstruct causal behaviour through the relevant entry point, calls, state, effects, removal or cleanup, and tests rather than listing changed files.

Label claims as:

- `verified`: directly supported by inspected source, runtime, test, provider, or authoritative record evidence;
- `inferred`: a reasoned connection not directly exercised;
- `unresolved`: material evidence is missing or ambiguous;
- `contradicted`: current strong evidence disagrees with another surface.

Produce two proportionate layers when useful: compact commit context and a user-facing behavioural explanation. Explanation is not a quiz, approval gate, code-review substitute, or completion proof. A follow-up question that reveals implementation, documentation, decision, or task drift reopens only the affected gate.

## Reconciliation order

1. Establish the final change boundary and current validation evidence with `documentation assess --base <ref>`.
2. Record the bounded causal explanation with `change explain --base <ref>` after inspecting the final material delta.
3. Discover task and knowledge lanes independently; an absent or unchanged lane is an explicit no-op, not a silently skipped responsibility.
4. Reconcile task state provisionally when durable tracking is active.
5. Promote verified durable conclusions where required, then run `documentation apply` with the affected concepts and likely reader questions.
6. Reconcile task acceptance, workstreams, evidence, knowledge links, tracker state, and running effort finally.
7. Validate the integrated tree and any capability-specific surfaces.
8. Run `closure assess --base <ref>`; resolve only gates backed by owning evidence; then run `close --base <ref>`.

`closure assess` interprets registered workflow obligations. A `state-clear`, `not-enabled`, or `not-applicable` lane is not independent proof that undocumented work was unnecessary; the caller must register material obligations when they arise.

## Authority boundaries

Merge, publication, deployment, cleanup, tracker writes, and external communication remain separate actions. Readiness does not authorise them.
