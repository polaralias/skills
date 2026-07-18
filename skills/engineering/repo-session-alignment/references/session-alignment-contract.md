# Session alignment contract

Use this contract to keep repository closure deterministic without creating a third source of truth.

## Lane discovery

| Lane | Present when | Absent status | Mutation rule |
| --- | --- | --- | --- |
| Tasks | An established task bundle exists at `tasks/` or `docs/tasks/` | `not present` | Reconcile through `repo-task-lifecycle`; never create a bundle during closure |
| Knowledge | Repository instructions, reading order, RKE metadata, or canonical docs establish a durable knowledge surface | `not established` | Align through `repo-knowledge-engineering`; never create a parallel tree during closure |

An OKF task bundle and an OKF knowledge bundle are independently conformant bundle roots. Their different paths do not weaken OKF support.

## Required ordering

1. Capture the verified Git and validation delta.
2. Discover and check both lanes.
3. Reconcile execution truth provisionally.
4. Promote affected durable truth into canonical knowledge.
5. Reconcile execution truth finally and link promotion evidence.
6. Validate each affected bundle independently.
7. Produce a handoff when unfinished work must survive the session boundary.

The provisional task pass prevents stale progress and time records from shaping promotion. The final task pass prevents a task from closing before its durable-knowledge obligation is satisfied.

## Status vocabulary

Report exactly one status per lane:

- Tasks: `updated`, `no-op`, `not present`, or `blocked`
- Knowledge: `updated`, `no-op`, `not established`, or `blocked`

Report an overall closure status:

- `complete`: both checks ran, required validation passed, and no closure obligation remains
- `incomplete`: checks ran, but truthful unfinished work remains and is recorded or handed off
- `blocked`: a required check, mutation, or validation could not be completed

## Minimum report

```text
Session alignment
- Tasks: <status> — <path or concise reason>
- Knowledge: <status> — <path or concise reason>
- Validation: <commands/results or not applicable>
- Handoff: <path, not required, or blocked>
- Closure: <complete|incomplete|blocked>
```

Mention external tracker drift separately as `pending external reconciliation` when it exists. Do not perform that reconciliation unless the user independently authorised it.

