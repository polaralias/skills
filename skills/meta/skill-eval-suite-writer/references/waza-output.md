# Waza Output Mode

Treat Waza as a concrete packaging target, not as the whole evaluation method.

## Typical files

Waza output usually includes:

- `eval.yaml`
- `tasks/*.yaml`

## What belongs in `eval.yaml`

The suite file normally defines:

- suite identity and description
- target skill
- run configuration
- suite-level graders or guards
- task file patterns

## What belongs in task files

Each task file should usually capture:

- task identifier and label
- prompt or setup
- whether trigger behaviour matters
- required or forbidden outcomes
- task-specific graders

## Good reasons to emit Waza output

Waza is a good fit for:

- routing checks
- required or forbidden content
- schema enforcement
- tool-use limits
- behaviour budgets

If a simple markdown plan is enough, prefer that instead of forcing a runner format.
