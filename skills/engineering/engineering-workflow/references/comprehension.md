# Comprehension

Use comprehension to explain a bounded implementation, current behaviour, or change. Answer a read-only question directly from inspected evidence; it needs no workflow activation, task, documentation receipt, or closure ceremony. For a material completed implementation, carry the causal explanation into the final report. Cosmetic and mechanical changes need only a concise account unless the user asks for depth.

## Bound the question and reconstruct the path

Identify the user's question and the relevant task, feature contract, commit range, staged diff, or session delta. Separate unrelated dirty-worktree changes. If the boundary is uncertain, state it instead of inventing a complete narrative.

Read consequential source, changed callers and callees, interfaces, tests, deleted code, and renamed symbols. Compare intended behaviour, implementation, documentation, and validation. Inspect enough surrounding code to establish what initiates the behaviour, which components run in order, what state changes, which boundary is crossed, what was removed or bypassed, and what meaningful failure or recovery behaviour applies.

Explain before and after through real symbols where they help. For example: `orders` now routes creation through `OrderWriter`, which reserves inventory before persistence; the direct write path was removed. A compact `A -> B -> C` path can clarify control or data flow. Avoid narrating every changed line or teaching syntax unless asked. Preserve contradictions between sources until resolved.

## Label evidence precisely

| Class | Meaning |
| --- | --- |
| runtime-verified | Observed through an executed public or runtime path |
| test-verified | Demonstrated by a successfully executed relevant test/check |
| code-supported | Supported by inspected implementation, without execution |
| contract-only | Required by an accepted contract, without implementation proof |
| unknown | Material evidence is missing or ambiguous |

A statically reconstructed call chain is code-supported. An authored but unexecuted test is intended coverage. State uncertainty where it changes what the user should believe.

## Produce the useful layers

Lead the user explanation with the outcome. Cover the consequential execution path, before/after behaviour, state and boundary effects, removal, failure/recovery, and evidence supporting material claims. Scale detail to the question. Explanation is neither a quiz nor a substitute for code review, validation, or canonical documentation.

For a completed material change, also supply compact commit context when useful: a subject candidate and one to three causal facts, including significant replacement or removal. Keep tutorial detail, personal questions, speculative rationale, and long evidence discussion out of that layer. Supplying commit context does not authorise staging or committing.

Invite questions naturally when helpful; an unanswered invitation never blocks completion. Do not require the user to demonstrate understanding.

## Preserve and reconcile explanations when needed

For long-running changes, an optional ignored local comprehension note can retain the bounded scope, current explanation, commit facts, evidence, and uncertainty. Verify the location is ignored and safe before writing. If no safe local surface exists, answer in chat without creating a tracked log convention. Keep one distilled current account rather than a transcript or competing explanations. This note is continuation context, not canonical knowledge or task evidence.

On a follow-up, refresh source evidence and answer first. Classify what the question exposed:

- Clearer explanation only: update the local account if present.
- Verified canonical gap: correct the owning surface through [knowledge](knowledge.md).
- Unresolved terminology or decision: use [clarification](clarification.md).
- Incorrect implementation or changed intended behaviour: use [delivery](delivery.md), then refresh the explanation.
- Inaccurate execution state: use [task lifecycle](task-lifecycle.md).

After a material correction, reconcile affected lanes through [alignment](alignment.md). A leading question is not proof of a defect; verify it. A verified gap should not remain only in chat or a personal explanation note.
