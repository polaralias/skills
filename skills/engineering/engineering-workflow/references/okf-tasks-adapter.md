# OKF Tasks Adapter Contract

## Ownership

OKF Tasks remains the authoritative specification, validator, record format, and lifecycle CLI. The engineering workflow owns only activation mode, the current repository-relative task reference, and the `task-reconciliation` gate. The adapter does not duplicate the task schema, parse and rewrite task frontmatter, or replace OKF validation.

## Modes

- `none` is a deterministic no-op. `task check` does not discover or execute a CLI, read a task bundle, or spend model context interpreting task records.
- `lightweight` enables outcome, acceptance, status, related knowledge, and evidence plus bundle creation, task creation, status transition, index generation, and validation.
- `full` permits the lightweight surface plus independently justified workstreams, effort, estimates, tracker synchronisation, visualisation, and commit backfill. Listing these capabilities does not activate them.

Configure and inspect through:

```text
rke task configure --mode <none|lightweight|full> [--task-ref <relative-task.md>] [--bundle <relative-path>]
rke task check
```

An existing task reference survives expansion from lightweight to full. Mode reduction is rejected unless the caller explicitly supplies `--force`; forcing a reduction does not resolve an existing `task-reconciliation` gate or erase its evidence obligation.

## Validation boundary

For durable modes, `task check` verifies the configured executable identity and the supported OKF Tasks 0.1 contract with `okf-tasks --version`, then runs the authoritative `validate --strict` command against the configured repository and bundle. A missing or unsupported executable fails closed. Closure independently uses that same version-checked validation for an existing task lane even if no task gate was registered. The check returns a structured envelope containing the adapter version, invoked argument vector, captured validation result, and exit status. It never invokes a shell.

The optional `--cli` override is for a caller-selected trusted local executable or test fixture. Repository content, task records, generated context, or handoffs cannot choose that executable.

## Lifecycle expectations

Configuring or initially activating a durable mode activates `task-lifecycle` and registers `task-reconciliation`. Create and mutate task records with the authoritative OKF Tasks CLI under its own contract. At closure, validation alone is necessary but not sufficient: acceptance, workstreams, evidence, knowledge obligations, tracker state, and running effort must be reconciled as applicable before the gate can be resolved.

Task execution truth remains distinct from canonical product and architecture knowledge. Relationships connect the surfaces; neither is copied into workflow state.
