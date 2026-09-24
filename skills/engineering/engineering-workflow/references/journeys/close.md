# Close Journey

Load this journey for material-work reconciliation before completion or merge consideration. Entering it changes the control phase but does not invent, waive, or resolve gates. Use `closure assess` to explain current lanes and `close` only after their evidence-backed gates are resolved.

## Bound change explanation

Establish the actual final delta before explaining it. Reconstruct causal behaviour through the relevant entry point, calls, state, effects, removal or cleanup, and tests rather than listing changed files.

Label claims as:

- `verified`: directly supported by inspected source, runtime, test, provider, or authoritative record evidence;
- `inferred`: a reasoned connection not directly exercised;
- `unresolved`: material evidence is missing or ambiguous;
- `contradicted`: current strong evidence disagrees with another surface.

Produce two proportionate layers for a material code change. Commit context is a subject candidate and one to three causal facts, including significant removal or replacement. The user explanation names the changed entry point, consequential callers and callees, before/after branch or data flow, state and boundary effect, failure/recovery behaviour, and what was removed. Do not let the short `change explain` summary stand in for this explanation. Label each material claim `runtime-verified`, `test-verified`, `code-supported`, `contract-only`, or `unknown`; an authored but unexecuted test is not test-verified. A compact `A → B → C` path is useful when it clarifies the mechanism. Offer questions without making an answer a closure gate. Explanation is not a quiz, approval gate, code-review substitute, or completion proof. A follow-up question that reveals implementation, documentation, decision, or task drift reopens only the affected gate and refreshes the explanation from current evidence.

## Reconciliation order

1. Establish the final change boundary and current validation evidence with `documentation assess --base <ref>`.
2. Record the bounded causal explanation with `change explain --base <ref>` after inspecting the final material delta.
3. Discover task and knowledge lanes independently; an absent or unchanged lane is an explicit no-op, not a silently skipped responsibility.
4. Reconcile task state provisionally when durable tracking is active: stop or correct supported effort, record implementation evidence, blockers and remaining work, but do not mark acceptance complete while promotion or validation is pending. Use the OKF Tasks CLI, not a workflow-state summary, for mutations.
5. Promote verified durable conclusions where required, then run `documentation apply` with the affected concepts and likely reader questions. If no canonical update is warranted after reviewing every changed path, record `documentation disposition` instead; do not bootstrap an empty bundle for closure.
6. Reconcile task acceptance, workstreams, evidence, knowledge links, tracker state, and running effort finally through the authoritative CLI. If knowledge changed, final task links and acceptance must be checked after that change rather than relying on the provisional pass.
7. Validate the task bundle strictly when present and the affected canonical knowledge bundle independently. Check invalid relationships and running effort as well as schema. Validate the integrated tree and any capability-specific surfaces. An absent lane is a reported no-op, not a reason to manufacture it.
8. Run `closure assess --base <ref>`; resolve only gates backed by owning evidence; then run `close --base <ref>`.

`closure assess` returns the RSA-compatible compact alignment view for explanation, tasks, knowledge, validation, handoff, and overall closure. Preserve the two-pass task ordering: execution truth is corrected before promotion, then task acceptance and knowledge links are reconciled after promotion. An absent task bundle or unestablished knowledge surface is an explicit status, not permission to bootstrap one during closure.

For an eligible small correction only, use the `closure complete-small` route in the documentation lifecycle. Its fail-closed checks replace the individual receipt and close commands, not the agent's source review or focused validation. Do not apply it to an exploratory design, durable task, canonical knowledge, or unresolved gate.

When unfinished work must survive the session boundary, run `handoff write` after alignment. A handoff is continuation evidence, not a substitute for task truth, canonical knowledge, validation, or the final explanation.

`closure assess` interprets registered workflow obligations. A `state-clear`, `not-enabled`, or `not-applicable` lane is not independent proof that undocumented work was unnecessary; the caller must register material obligations when they arise.

## Authority boundaries

Merge, publication, deployment, cleanup, tracker writes, and external communication remain separate actions. Readiness does not authorise them.
