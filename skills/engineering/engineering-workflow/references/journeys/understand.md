# Understand Journey

Load this journey only when repository orientation, ambiguity resolution, runtime verification, or canonical-knowledge maintenance is the immediate purpose.

## Modes and exit condition

Use bounded orientation for an already-legible repository. Use deep dissection when the repository is inherited, contradictory, underdocumented, or the user asks how the whole system works. Start deep dissection with `rke dissection assess`; its inventory is a navigation aid, not runtime proof. When the requested outcome is a documented repository, also run `rke documentation bootstrap` to establish the minimum foundation or an explicit no-op before authoring.

Stop broad discovery once the repository is legible enough to name the next bounded decision or change. Deep dissection additionally requires a codebase map, selected runtime path, trust and mismatch classification, documentation foundation or explicit no-op, and a concrete next-work recommendation. Neither mode requires unrelated archaeology.

## Sequence

1. Establish the active repository, user goal, applicable instructions, likely entry points, and current workflow gates.
2. Use `context find` for bounded retrieval before broad file traversal. Treat results as candidates and inspect the cited source.
3. Map the relevant runtime path: entry point, calls, state, effects, tests, packaging or deployment boundary, and ownership. In deep dissection, also inventory competing entry points, duplicated truth surfaces, task/knowledge bundles, and producer-owned documentation.
4. Separate local source intent, observed runtime behaviour, packaged or deployed behaviour, canonical knowledge, and desired future truth.
5. Classify mismatches as documentation drift, runtime or packaging drift, behavioural defect, missing test, architecture debt, or unresolved product judgement.
6. Answer repository-resolvable questions from evidence. When user judgement is irreducible, ask one dense, decision-coherent batch using concrete scenarios and contradictions. After repeated non-progress, switch back to bounded inspection.
7. Run `context impact` when changed paths may affect canonical knowledge. Distinguish explicit bindings from unmatched changes; use retrieval only as review evidence, never as an inferred binding.
8. Classify mismatches as documentation drift, packaging/runtime drift, behavioural defect, missing test, architecture debt, support-boundary mismatch, or unresolved product judgement.
9. In deep dissection, exercise the selected public runtime path where safe and record success path, error path, state location, public boundary, and whether source, package, wrapper, container, or deployed artefact actually ran. Where source and packaged launchers disagree, exercise both independently with the same representative request; identify the exact executable, arguments, working directory, version, artefact, and observed result. An entrypoint named in a manifest is only declared support. An importable module or passing source test does not prove that the installed or packaged command works.
10. Promote only verified durable conclusions into the lightest correct canonical surface. When the repository has no trustworthy foundation, establish the minimum useful reading order, glossary/decisions/operating surface, machine-readable support or trust artefact, and repair plan. Generated answers, derived summaries, and producer-owned records do not become canonical automatically.

## Evidence rules

- Documentation and generated summaries are claims. Code is intended behaviour until exercised or otherwise verified.
- Prefer bounded black-box checks for consequential runtime claims; restore user-controlled state when safe verification mutates it.
- Classify knowledge surfaces before editing them: canonical, evidence, derived, execution, generated, or producer-owned.
- For a bounded slice, compare only the strongest relevant artefacts. Preserve reading order, terminology, accepted decisions, current contracts, and evidence links when they matter.
- After deliberate promotion, disposition affected source material as retain, merge, archive, or delete. Do not leave two competing current answers.
- Test likely reader questions against retrieval: each should reach one clear current answer or remain an explicit gap.
- If an OpenWiki-owned surface exists, stop before knowledge mutation until its ownership and migration boundary is explicitly resolved.

## Deep-dissection output contract

Return a codebase map, runtime validation record, declared-versus-verified trust table, mismatch classification, documentation spine disposition, task/knowledge inventory, one machine-readable trust artefact when it prevents rediscovery, repair or refactor plan, and the next bounded journey. For each material support claim, cite the selected entrypoint and the observed public invocation or label it `declared`, `code-supported`, `unverified`, or `broken`. Preserve conflicting source and packaged observations rather than collapsing them into one verdict. Label unexecuted tests and conventional entry points as candidates rather than proof.

## Gates

Entering the journey does not manufacture a knowledge obligation. Add `knowledge-impact-review` when material changes need classification, and add `knowledge-promotion` only when a verified durable conclusion must enter canonical knowledge.
