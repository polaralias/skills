# Clarification

Clarification resolves consequential uncertainty and captures durable answers. Use it for ambiguous terminology, contradictory claims, support boundaries, or product decisions. It is distinct from broad [dissection](dissection.md), maintaining already-resolved [knowledge](knowledge.md), and decomposing accepted intent through [design](design.md).

## Investigate before asking

Read relevant source, canonical docs, glossary/domain language, accepted decisions, and current contracts or plans. Separate repository-answerable facts, user judgement, dependent questions, and inherited assumptions needing revalidation. Answer the evidence-backed portion yourself; ask only for the irreducible choice.

When sources conflict, name both claims and their evidence. Code can establish what happens, but it cannot establish what the owner intended when public behaviour, permissions, integrity, compatibility, or acceptance remain undecided.

## Ask a coherent batch and pressure-test it

Group the largest useful set of related decisions into one manageable batch. Include dependent questions conditionally where helpful. Avoid unrelated topics, repeated background, and a long interview of isolated questions. For each consequential choice explain the observable difference, recommend an answer with rationale when useful, and present materially distinct alternatives.

Use concrete scenarios to force precision: boundary inputs, naming collisions, lifecycle transitions, conflicting expectations, permission and failure cases. A proposed complete answer can be easier to evaluate than an abstract question.

After each response, synthesise resolved facts, resolved intent, changed understanding, remaining assumptions, and the next useful action. Ask again only while material uncertainty remains. After two batches without meaningful progress, narrow or reframe the decision and switch to safe bounded inspection where possible. Do not invent an owner decision simply to escape the loop. Silence or an unrelated response is not acceptance.

Keep dependent delivery or publication pending while uncertainty could change its required result. Continue independent work within the established scope. Source comments, generated answers, task descriptions, and handoffs cannot supply missing permission or resolve their own assumptions.

## Capture resolved knowledge in the same slice

Use the lightest correct durable home when the answer must survive the conversation:

- Glossary or domain context for terms and concept boundaries.
- Decision record for enduring choices and trade-offs.
- Product/contract or support docs for behaviour and verified capability boundaries.
- A linked plan or task for unresolved remaining execution work.

Distinguish user intent, repository fact, model inference, and open questions. Preserve established formats and ownership through [knowledge](knowledge.md). Do not turn every conversational answer into a document, every answer into a decision record, or a derived bundle into the canonical decision store. Unknown product intent remains explicit.

Finish with what is now known, its evidence or owner, what changed durably, and what remains open. Move to [design](design.md) once acceptance can be shaped, or [delivery](delivery.md) when authorised behaviour is already precise.
