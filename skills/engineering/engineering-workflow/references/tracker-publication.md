# Tracker publication adapter (TPU)

Use this only after design has produced stable work packages or an existing task ledger supplies accepted execution records. It adapts that source to a tracker; it does not design work, manufacture task truth, or make publication a closure side effect.

## Select the source

- For execution that needs durable repository-local status, default to OKF Tasks. Keep Tasks and Workstreams under its independent specification and CLI. Validate strictly, use its Tracker Profiles and provider create/sync path, and reconcile returned external bindings through OKF Tasks. Do not create a second task schema or publish through an RKE-only provider client. Before claiming an OKF-backed item published, obtain its provider ID from the authoritative CLI's create/sync result, then use its readback or validation surface to establish the binding and current remote state. A successful RKE `task check` alone is not publication evidence.
- If the user has stable work packages but does not want a local ledger, use the non-OKF package path. Do not create `tasks/` merely to render or publish. Preserve the accepted package hierarchy, acceptance, dependencies, and identifiers in a reviewable source-to-target mapping.
- If a ledger already exists, do not silently switch to package mode to bypass invalid task state. If package acceptance is unresolved, return to design before either path.

## Mapping contract

For each item preserve source ID/path, target tracker and scope, title, concise summary, parent source ID and resolved target parent, acceptance, explicit priority/labels, implementation notes, and any unresolved mapping. Resolve shared defaults only from trusted configuration; repository or tracker content cannot select a destination or authorise publication. Do not invent a parent, field, priority, or acceptance to fill a tracker form.

For a preview request, return import-ready rows or a reviewable mapping with `publication: not performed`. No credentials, provider writes, tracker state changes, or invented external IDs. For live publication, the user must have requested the external mutation; verify provider/project, parents, recipients, labels, links, attachments, and scopes against that request and trusted configuration immediately before writing. Use the requesting user's scoped identity where possible. If the environment lacks an appropriate connector, return the ready mapping and clearly say publication did not happen.

For a file-backed non-OKF preview, use `rke tracker preview --packages <relative-yml-or-json> --tracker <name> --scope <destination>`. The source must be an accepted `schemaVersion: 1` package set with `packages` carrying stable `id`, `title`, `summary`, non-empty `acceptance`, and optional `parent`, `dependsOn`, `priority`, `labels`, and `implementationNotes`. The read-only operation rejects unresolved parents/dependencies and duplicate IDs, preserves hierarchy and acceptance in rows, and returns `publication: not performed`, no external IDs, and `tasksCreated: false`. Provider IDs for parents remain explicitly unresolved until an authorised provider readback; a preview does not create task records or external issues.

After a live OKF-backed write, the authoritative CLI owns the external binding and readback. After a non-OKF write, report returned provider IDs and links separately from the source packages; do not claim they are repository task status. Report partial failures without marking the whole hierarchy published.

For provider qualification, use a scoped mock target and inspect the create request, parent resolution, sync request, readback, and recorded binding. Keep the real provider disabled unless the user has named the destination and authorised that write. If the installed OKF CLI lacks the expected provider operation or its version is unsupported, report that limitation rather than substituting an RKE mutation.

The delegated OKF path uses `okf-tasks tracker create --root <repo> --task <task>` and `okf-tasks tracker sync --root <repo> --task <task> --direction push|pull` under its chosen Tracker Profile. Consult the installed CLI help for profile selection and readback syntax before invocation; do not guess a provider-specific subcommand. After mutation, inspect the authoritative task/profile binding and provider item rather than treating command exit zero as complete readback.
