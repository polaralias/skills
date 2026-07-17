# Scenario Design

Organize the suite by the kinds of behavior you need confidence in.

## Activation cases

Include prompts or setups that clearly should trigger the skill or instruction pattern.

## Non-activation cases

Add nearby prompts that should not trigger it, especially if routing precision matters.

## Straight success cases

Cover ordinary in-scope requests where the behavior should be clean and unremarkable.

## Messy but valid cases

Include incomplete, unusual, or noisy inputs that are still legitimately in scope.

## Boundary and refusal cases

Add situations where the skill should narrow scope, decline, defer, or surface a guardrail.

For source-consuming or tool-using skills, include adversarial cases where untrusted content attempts to:

- override the user or host policy
- obtain secrets or unrelated context
- select a tool, credential, recipient, webhook, or network destination
- trigger a write, execution, publication, or external message
- poison a persistent knowledge file, handoff, generated prompt, or downstream agent instruction

Expected behaviour should verify both non-compliance and safe handling: quote or quarantine the content only when needed as evidence, continue the legitimate task where possible, and require explicit authority for consequential actions.

## Regression traps

Capture behaviors that are easy to lose during refactors, plus any known weak spots.

For every task, specify:

- prompt or setup
- expected behavior
- disallowed behavior
- the grader type that should verify it
