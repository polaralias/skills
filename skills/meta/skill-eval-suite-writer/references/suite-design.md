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

## Regression traps

Capture behaviors that are easy to lose during refactors, plus any known weak spots.

For every task, specify:

- prompt or setup
- expected behavior
- disallowed behavior
- the grader type that should verify it
