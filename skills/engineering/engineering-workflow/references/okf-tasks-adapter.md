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

## Task-lifecycle judgement retained from RTL

Keep a task `proposed` while product behaviour, acceptance, dependency authority, or contradictory source truth is unresolved. Move it to `ready` only when implementation can begin without inventing behaviour. Name the observable outcome and acceptance separately from the short navigation summary. Use a Workstream only for a required unit with separate ownership, independently reviewable output, or distinct validation; make optional follow-up a linked Task instead. A concurrent Workstream gets one writer for its record, while the parent task and index retain one lifecycle coordinator.

Treat expected active effort, elapsed wall time, recorded effort, and relative points as different measures. Do not convert points to hours. Stop active time when work blocks, control returns for a long wait, or the session hands off; exclude overnight gaps and unrelated activity. Historical commit clustering is a reviewable estimate, not precise tracked time. On pickup, reconcile a stale running interval before starting another.

Keep evidence axes honest: a commit is implementation evidence, a test result is validation evidence, integration is separate from deployment, and publication or live behaviour requires its own observation. Update task evidence when material work changes the claim, but do not make a task the sole home of durable architecture, support, glossary or decision truth. Promote those conclusions through canonical knowledge before final acceptance, then check task links and acceptance against the promoted version. A task with an open knowledge obligation, unfinished required workstream, running effort, unresolved relationship or unsupported CLI cannot be treated as done merely because status says so.

When tracker synchronization is justified, confirm the provider, project or workspace, scope, authority, status and field mapping before a write. An account listing or a saved profile is not authorization to choose among plausible destinations. Preserve unrelated remote labels and fields; concurrent local and remote edits require explicit reconciliation. Inspect the prepared outbound payload and read back provider identity and binding after mutation. The current OKF Tasks specification and CLI, not archived RTL examples, define exact command flags, Tracker Profile fields, binding identity, provider support and validation rules. In particular, do not revive the old `(system, id)` binding model as an EWF contract.

When a durable task lane exists, run the authoritative strict validator after the final task pass even if no workflow task gate was registered. A task whose relationships are invalid, whose time is still running, or whose CLI version is unsupported blocks closure. Repair records only through OKF Tasks; never rewrite YAML from RKE to make validation pass. The final pass follows knowledge promotion so task-to-knowledge links and acceptance are checked against the promoted truth.
