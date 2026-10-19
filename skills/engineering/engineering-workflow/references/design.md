# Design

Turn established product or repository truth into bounded behavioural contracts, proportionate implementation plans, work packages, and acceptance artefacts. Use this method before coding when scope or acceptance is not yet clear. A small correction with obvious accepted behaviour needs only a short plan. Planning does not itself authorise implementation or external publication.

## Establish and decompose the outcome

Read the accepted product/contract truth, relevant domain language, decisions, constraints, and active plans. Distinguish facts, assumptions, unresolved owner decisions, and downstream implementation detail. Use [clarification](clarification.md) for consequential unknowns, or [knowledge](knowledge.md) if the canonical foundation itself is unreliable.

Name the outcome and split it by user-visible capability, workflow stage, or domain boundary. Prefer a small number of independently understandable features. Do not break an unclear feature into a long backlog of code tasks.

For each feature, state the problem, user/system outcome, scope and non-goals, invariants, dependencies, assumptions, and observable success. Preserve accepted constraints even when they make the implementation inconvenient. Distinguish a required behaviour from a preferred technical approach.

## Pressure-test the contract

Use scenarios that force precise behaviour: happy paths, boundaries, invalid input, failure/recovery, permissions, state transitions, retries, concurrency, compatibility, and data integrity where relevant. Identify the permission or failure case that could change the public interface. If it is undecided, do not present tentative acceptance as approved.

Map each requirement or invariant to scenarios and verification. Split distinct failure-prone behaviours; merge cases only when their purpose, setup, path, and expected result remain coherent. Do not hide permission or integrity risks inside an umbrella happy-path test. Equally, do not pad the plan with speculative cases unrelated to scope.

Write acceptance through observable public behaviour, with example inputs/outputs and completion signals where useful. Avoid private call order or implementation-specific assertions unless the contract actually requires them.

For acceptance cases needed by this design, retain the requirement link, objective, preconditions, action, expected result, and appropriate automated/manual/either verification mode. Mark unknown environment/data honestly rather than inventing specifics. A review of existing tests should identify actual coverage gaps instead of generating a replacement suite by default. Standalone QA-plan writing remains outside this method.

## Add technical detail and work packages

After behaviour is settled, capture technical choices that materially reduce ambiguity: approved stack, module/API/data boundaries, migrations and compatibility, sequencing, prerequisites, risky integrations, bounded research, and non-goals. Avoid architecture inventory without a delivery consequence.

Each work package needs a coherent outcome, direct prerequisites, acceptance, verification target, implementation entry point where useful, open questions, and a downstream delivery target. Preserve traceability from accepted outcome through feature, invariant/scenario, package, acceptance, and test. Report genuine gaps instead of inventing links.

Stable packages can enter [task lifecycle](task-lifecycle.md); tracker formatting belongs to [publication](publication.md). Consume established output defaults without letting presentation shape unresolved behaviour or select credentials/destinations.

A stacked-review candidate must form one linear dependency chain with at least two useful layers. Each lower layer must be safe, independently reviewable, and valid if upper layers never land. Independent work belongs in ordinary parallel dependencies. Leave physical branches, worktrees, integration, and cleanup to [coordination](coordination.md).

## Control exploratory convergence

Use an experiment contract when design relies on uncertain behaviour or technology: model behaviour, retrieval, orchestration, unfamiliar integration, performance, or migration. Do not require it for a routine correction. Record:

- Problem, current hypothesis, and supporting evidence.
- Governing assumption and expected observable result.
- The observation that would falsify the hypothesis.
- Acceptance condition and the authority/evidence that established it.
- Corrective limit, normally two individually inconclusive assumption-relevant acceptance failures.
- Reset or kill condition.

A predefined falsifier requires immediate design reconsideration on its first decisive observation. The two-attempt limit applies only to inconclusive failures relevant to the same governing assumption and acceptance condition. A typo, broken fixture, or unrelated integration failure is an implementation defect and does not consume that limit.

At the limit, stop delivery before fixing another symptom. Capture what each attempt taught and choose explicitly: reaffirm with new evidence, simplify/delete, replace, or abandon. Reconsideration does not imply adding machinery. Do not weaken acceptance to fit current output. Change it only when new authoritative evidence changes required behaviour, recording that evidence, authority, reason, and affected prior conclusions.

Preserve the active hypothesis, assumption, acceptance/authority, falsifier, failure count, and latest decisive/inconclusive/incidental learning in a justified [handoff](handoff.md) or checkpoint. Compaction never resets contrary evidence.

## Finish when delivery is ready

Return only artefacts justified by scope: contracts, scenario/verification trace, acceptance, technical plan, dependencies/risks, work packages, open decisions, and an experiment contract when needed. Verify every in-scope requirement and direct risk has coverage, cases have no hidden prerequisites, and no unresolved consequential choice is disguised as acceptance. Proceed to [delivery](delivery.md) when the user's authorised outcome is precise enough to implement.
