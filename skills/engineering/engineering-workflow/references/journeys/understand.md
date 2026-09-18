# Understand Journey

Load this journey only when repository orientation, ambiguity resolution, runtime verification, or canonical-knowledge maintenance is the immediate purpose.

## Exit condition

Stop broad discovery once the repository is legible enough to name the next bounded decision or change. The journey exits with current evidence, explicit uncertainties, and any justified knowledge obligation; it does not require exhaustive archaeology.

## Sequence

1. Establish the active repository, user goal, applicable instructions, likely entry points, and current workflow gates.
2. Use `context find` for bounded retrieval before broad file traversal. Treat results as candidates and inspect the cited source.
3. Map only the relevant runtime path: entry point, calls, state, effects, tests, packaging or deployment boundary, and ownership.
4. Separate local source intent, observed runtime behaviour, packaged or deployed behaviour, canonical knowledge, and desired future truth.
5. Classify mismatches as documentation drift, runtime or packaging drift, behavioural defect, missing test, architecture debt, or unresolved product judgement.
6. Answer repository-resolvable questions from evidence. When user judgement is irreducible, ask one dense, decision-coherent batch using concrete scenarios and contradictions. After repeated non-progress, switch back to bounded inspection.
7. Run `context impact` when changed paths may affect canonical knowledge. Keep explicit bindings, lexical candidates, and unmapped changes distinct.
8. Promote only verified durable conclusions into the lightest correct canonical surface. Generated answers, derived summaries, and producer-owned records do not become canonical automatically.

## Evidence rules

- Documentation and generated summaries are claims. Code is intended behaviour until exercised or otherwise verified.
- Prefer bounded black-box checks for consequential runtime claims; restore user-controlled state when safe verification mutates it.
- Classify knowledge surfaces before editing them: canonical, evidence, derived, execution, generated, or producer-owned.
- For a bounded slice, compare only the strongest relevant artefacts. Preserve reading order, terminology, accepted decisions, current contracts, and evidence links when they matter.
- After deliberate promotion, disposition affected source material as retain, merge, archive, or delete. Do not leave two competing current answers.
- Test likely reader questions against retrieval: each should reach one clear current answer or remain an explicit gap.

## Gates

Entering the journey does not manufacture a knowledge obligation. Add `knowledge-impact-review` when material changes need classification, and add `knowledge-promotion` only when a verified durable conclusion must enter canonical knowledge.
