# Task record contract

## Layout

```text
tasks/
├── index.md
└── <task-slug>/
    ├── task.md
    ├── workstreams/
    │   └── <workstream-slug>.md
    ├── coordination/        optional
    └── sessions/            optional audit profile
```

`task.md` is the parent execution record. A workstream file is the single-writer record for one separately assigned delivery unit. `index.md` is generated navigation.

## Identity

- Use stable kebab-case slugs derived from meaning.
- Keep tracker numbers, pull request numbers, and vendor IDs in External references.
- Do not rename a task directory merely because its external tracker mapping changes.

## Status semantics

- `proposed`: outcome exists, but readiness is unresolved.
- `ready`: contract and dependencies are sufficient to start.
- `in-progress`: owned delivery work is active.
- `blocked`: progress requires a named dependency, decision, or external change.
- `validation`: implementation is present and completion checks are active.
- `done`: acceptance, required workstreams, evidence, and promotion have been reconciled.
- `superseded`: another task or decision replaced this record.
- `deferred`: intentionally inactive without a current blocker-resolution expectation.

## Ownership

The lifecycle coordinator is the only writer for `task.md` and `tasks/index.md` during concurrent work. Each workstream owner writes only its workstream file and implementation branch. Integration reconciles the parent record after workstream commits are available.

## Evidence axes

Record Git, integration, deployment/publication, and live verification independently. A commit or merge does not prove deployment or external behavior.

## Canonical promotion

Task records may cite product requirements and record delivery findings, but they are not the sole home for durable product, architecture, support, or decision truth. Promote those conclusions through `repo-knowledge-engineering` before closing the task.
