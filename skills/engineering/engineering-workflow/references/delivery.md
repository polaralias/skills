# Delivery

Implement the accepted bounded outcome, preserving existing user work and established repository constraints. A named small fix should begin with its source and relevant tests, rather than broad archaeology or persistent workflow setup.

## Establish the working boundary

Confirm the repository, branch/worktree, current changes, applicable instructions, accepted outcome, and likely source/test locations. Inspect the path from public entry point to consequential implementation. Use bounded search when the location is unknown; read known source directly. Generated context and structural traces are navigation evidence, not substitutes for consequential source review.

Identify what validation would distinguish success from the reported failure or requested behaviour. If intended behaviour is consequentially ambiguous, use [clarification](clarification.md). If the scope needs decomposition or risky design, use [design](design.md). Do not turn repository investigation into permission to rewrite unrelated architecture.

## Make and verify the change

For a defect, reproduce or otherwise establish the failure, minimise the relevant path, form a hypothesis, and verify that the fix addresses its cause. Use instrumentation or a focused experiment when evidence is insufficient. Follow an explicitly requested test-first or other implementation method. Choose regression tests that protect meaningful behaviour and failure boundaries rather than echoing implementation structure. Trivial reversible wording or formatting changes need inspection, not invented test code.

Change the smallest coherent surface that satisfies the accepted outcome. Preserve compatibility, validation, authority, error/recovery, and data integrity boundaries. Review consequential callers, removals, migrations, and effects on packaged interfaces. Avoid opportunistic refactoring unless necessary for correctness or expressly in scope.

Inspect repository-defined commands before running them. Run focused checks appropriate to the change, then required repository checks. Broaden only when scope, failures, integration, or unresolved concerns justify it. Distinguish unrun, failed, blocked, and passed checks. A test file or scenario definition is not executed evidence.

When design has an experiment contract, count only assumption-relevant inconclusive failures and return to [design](design.md) immediately on its falsifier or at its corrective limit. Do not keep repairing symptoms or lower acceptance to manufacture success.

## Carry the resulting truth forward

For every material code, contract, or interface change, complete a bounded documentation-impact review before reporting completion. Start with explicit source/document relationships and the existing reading order. Also search plausible documentation using changed paths, names, symbols, removed or renamed identifiers, and the behaviour visible in the diff; an absent binding is not evidence that no documentation is affected. Inspect relevant passages against the final implementation and tests, including consequential callers or consumers. Exclude generated and producer-owned surfaces from direct authorship; use their owning process where a warranted change belongs there.

Resolve the reviewed candidates by updating the owning durable claims or explaining why their existing wording remains correct. A lexical match is a candidate for review, not an obligation to edit or a source binding. If discovery is unavailable, truncated, unsupported, or yields no useful candidates, inspect the relevant existing documentation directly and disclose material residual gaps; do not claim exhaustive coverage. A renamed or deleted source needs review of its old terminology as well as its replacement. Refresh the affected review after later edits change its evidence.

Use [knowledge](knowledge.md) for actual durable changes to architecture, behaviour, support, reliability/security, decisions, terminology, or first-contact docs. Verify meaning against source and relevant checks, then verify adopted format and findability separately. Report the documents updated or a concise reviewed no-update reason and the important coverage limits. A routine code-and-test correction does not need a new knowledge bundle, task, persistent state, or formal closure receipt. Pure wording/formatting changes need only the corresponding bounded editorial review.

For durable tracked work, update affected execution evidence through [task lifecycle](task-lifecycle.md).

Use [comprehension](comprehension.md) for a material causal explanation. Use [alignment](alignment.md) when a material slice needs task/knowledge reconciliation or the user requests closure/readiness. For a local bounded correction, report the outcome, focused validation, and actual remaining obligations promptly; do not invent a release, publication, or whole-repository completion claim.

If multiple workers are authorised and useful, use [coordination](coordination.md) before overlapping edits. Validate the final integrated tree, not just worker reports. Stage, commit, push, merge, deploy, or publish only within established authority. If work must stop unfinished, preserve the verified state through [handoff](handoff.md).
