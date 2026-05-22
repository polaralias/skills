# Coverage and Splitting Guidance

## Coverage baseline

Every in-scope requirement or acceptance criterion needs at least one case.

Walk the source item by item and confirm where each one is covered before you finish.

If a requirement contains several meaningful behaviors that could fail independently, split them into separate coverage units.

## General rules

- include a case only when it maps to an in-scope requirement or a direct change risk
- direct change risks are behavior paths that share the changed workflow, validation path, permission rule, persistence path, rendering path, or integration point
- when a case exists for direct change risk rather than explicit requirement text, say so
- when in doubt, prefer the clearer split

## Merge rule

Merge checks only when they:

- exercise the same user flow
- use the same product mechanism
- have the same kind of expected outcome

If any of those differ, keep the cases separate.

## Coverage families to preserve

Use these only when they are relevant to the source material.

### Permissions

If the change affects role-restricted behavior, include a dedicated case proving that an unauthorized user cannot access or perform the action.

### Data integrity

Every plan should include a separate data-integrity case.

Keep it distinct from simple save-and-reload persistence. Check both that new or edited data works correctly and that pre-existing data is not damaged.

### Accessibility

Where accessibility matters, keep separate coverage families such as:

- automated accessibility checks
- small viewport behavior
- keyboard-only use
- RTL or localization

### Required UI elements

If the source calls out specific UI elements, treat distinct required elements as separate coverage units unless they clearly share the same render pass and failure mode.

### Alternate render paths

Fallback, placeholder, loading, empty, and error states should usually be separate coverage units when they represent different render behavior.

### Save-state validation

When validation is part of save or publish behavior, separate cases are often needed for:

- blocking invalid state
- allowing valid state
- allowing cleared optional configuration where supported
- validation messaging

### Multiple-instance behavior

If the feature supports more than one instance of the same kind of item, test both authoring/configuration and runtime/application behavior where relevant.

### Count and tally logic

Header totals, counters, and filtered tallies should stay separate from list rendering when they can fail independently.

### Search behavior

Search behavior and search-input hardening should be separated when both matter.

## Execution-type guidance

- default to `Automated` for deterministic automation-friendly behavior
- use `Manual` when human judgement or visual interpretation is genuinely required
- use `Either` when both modes are practical

Do not make the entire plan manual by default without a reason.
