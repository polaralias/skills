# Alignment

Reconcile a material slice before claiming completion, readiness, or handing it over. Check existing execution truth and canonical knowledge independently; a required check does not require an edit. This method does not bootstrap missing systems, authorise external tracker changes, or turn routine local work into a release exercise.

## Establish the final delta and explanation

Inspect current status and the bounded diff, including pre-existing user changes, deleted paths, and relevant final validation. Identify behaviour, decisions, terminology, support boundaries, unfinished work, and touched execution records. Do not infer completion from a clean tree or a worker summary.

For material implementation, consume or refresh [comprehension](comprehension.md) against the actual final delta: causal before/after behaviour, concrete symbols, removals, state/boundary effects, failure paths, and evidence class. Keep compact commit facts separate from the user explanation. A local explanatory note is optional; waiting for user questions is never a completion gate. Mechanical-only changes need no architectural story.

## Reconcile in this order

1. Discover the existing task bundle/ledger and canonical knowledge surfaces separately. Respect their established roots and ownership. If absent, report tasks not present or knowledge not established; do not create them merely because alignment ran.
2. Reconcile execution provisionally through [task lifecycle](task-lifecycle.md): correct supported effort, workstreams, implementation and validation evidence, blockers, and remaining work. Identify durable promotion obligations. Do not mark acceptance complete while required validation or promotion remains pending.
3. Recheck the final-delta documentation-impact review from [delivery](delivery.md), including plausible unbound documentation and old terminology for renamed/deleted code. Align affected canonical truth through [knowledge](knowledge.md): promote verified decisions, language, architecture, behaviour, support, and operational conclusions. Update only the owning affected documents and navigation. A reviewed no-update conclusion is valid. Do not copy task/session logs into canonical knowledge.
4. Return to task reconciliation after promotion: link updated knowledge, satisfy or retain promotion obligations, and apply only evidence-backed acceptance/status transitions. Recheck these links and obligations after canonical edits rather than relying on the provisional pass.
5. Validate the task bundle and affected adopted knowledge bundles independently, including resolved relationships and running effort. Rebuild only relevant generated navigation/views through their owner. Validate the final integrated tree where work was combined. Run capability-specific required checks without making an absent capability a reason to invent infrastructure.
6. Reconcile actual existing workflow obligations against the final evidence. A stored clear/not-applicable status cannot establish that an undocumented obligation was assessed. A later source, contract, or canonical edit can invalidate earlier evidence; refresh the affected checks.

Keep explicit timestamps on directly changed governed concepts aligned with their meaning, preserving unknown compatible fields. Do not substitute Git, filesystem, or observation time. Treat schema and retrieval success as distinct from factual correctness.

## Report a truthful result

Use a compact disposition for each relevant lane:

| Lane | Useful states |
| --- | --- |
| Tasks | updated, no-op, not present, blocked |
| Knowledge | updated, no-op, not established, blocked |
| Validation | passed with scope, failed, not run, unavailable |
| Explanation | current for the bounded material delta, not applicable |
| Continuation | unnecessary, saved, required but missing |

Call the requested work complete only when its actual obligations are met. Report unfinished work and the next owner/action instead of overstating readiness. A failed required validator blocks the corresponding closure claim; it does not justify hiding unrelated progress. Mention pending external tracker or release action separately.

When ending with unfinished work, write the [handoff](handoff.md) after aligning known truth. The handoff preserves continuation; it cannot replace the task, canonical docs, validation, or final causal explanation. A follow-up that exposes a real implementation, decision, documentation, or task gap reopens only affected work and this reconciliation after correction.
