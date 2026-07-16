---
name: repo-task-lifecycle
description: Create and maintain durable repository-local task records, workstream records, status transitions, evidence links, and a generated task index. Use when work needs a tracked backlog or task history beside the code, when one task spans multiple workstreams, or when implementation state must survive beyond chat and external trackers. Do not use it to define canonical product truth, design feature contracts, publish to external trackers, or manage physical Git worktrees. Shorthand RTL.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-07-16'
---

# repo-task-lifecycle

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `repo-task-lifecycle was used in this response.`

Use this skill to keep execution truth in the repository without turning task records into product documentation.

Read [references/task-record-contract.md](./references/task-record-contract.md) before creating or changing task records. Use [scripts/task_lifecycle.py](./scripts/task_lifecycle.py) to create records, transition status, rebuild the index, and validate the surface.

## Boundaries

- `repo-knowledge-engineering` owns canonical repository and product truth. Promote durable conclusions there.
- `doc-driven-development` owns feature contracts, acceptance surfaces, and work-package design. Register those packages here only after their shape is stable.
- This skill owns `tasks/<task-slug>/task.md`, its workstream records, evidence links, lifecycle status, and generated `tasks/index.md`.
- `worktree-task-coordinator` owns physical worktrees and concurrent integration when a task needs them.
- `tracker-publisher` adapts stable task records to GitHub, Linear, or another external surface; the repository record remains the local execution ledger unless repository policy says otherwise.

## Task model

Use meaningful kebab-case slugs as durable repository identifiers. Keep external issue IDs as metadata or links, not as the directory name.

Default statuses:

- `proposed`
- `ready`
- `in-progress`
- `blocked`
- `validation`
- `done`
- `superseded`
- `deferred`

One task can contain several workstreams. The lifecycle coordinator owns `task.md` and `tasks/index.md`; each workstream owns only `workstreams/<slug>.md` plus its implementation branch.

## Workflow

### 1. Establish the local task surface

- Read repository guidance and existing task/tracker conventions first.
- If `tasks/` exists, preserve its stronger established contract unless the user asks to migrate it.
- Create a task from a stable outcome or work package, not from a vague idea disguised as ready work.
- Use the script initializer so required fields and index behavior stay deterministic.

```text
python scripts/task_lifecycle.py init --root <repo> --slug <task-slug> --title "<title>"
```

### 2. Record readiness honestly

Capture in `task.md`:

- outcome and scope
- acceptance surface
- dependencies and risks
- source contracts and canonical references
- external references
- workstream summary
- evidence and decision-promotion notes

Keep a task `proposed` while its contract is unresolved. Move it to `ready` only when implementation can begin without inventing product behavior.

### 3. Add workstreams when one task has multiple delivery units

Create workstreams only when they have distinct ownership, branchable outcomes, or separate validation obligations.

```text
python scripts/task_lifecycle.py add-workstream --root <repo> --task <task-slug> --slug <workstream-slug> --title "<title>" --owner <owner> --branch <branch>
```

If two or more workstreams will run concurrently, route physical setup and integration to `worktree-task-coordinator`.

### 4. Update state in the same change as material work

- Update the relevant workstream record when implementation, risk, evidence, or status changes materially.
- Update the parent task when its overall state changes.
- Rebuild `tasks/index.md` in the same commit.
- Keep status statements evidence-backed; a merged change can still be awaiting validation or external verification.
- Use a timestamped session or audit note only when the repository needs a detailed regulated or forensic history. Do not create one for routine progress.

### 5. Reconcile completion

Before `done`, confirm:

- acceptance criteria are satisfied or explicitly narrowed
- every required workstream is `done`, `superseded`, or intentionally `deferred`
- validation evidence is linked
- task and index agree
- durable product or architectural conclusions have been promoted through `repo-knowledge-engineering`
- external tracker state is reconciled when one is in use

Run:

```text
python scripts/task_lifecycle.py validate --root <repo>
```

Adopt validation gradually. Run it manually while a repository establishes the contract; add a read-only non-blocking CI check once the layout is stable, then make it required only after existing records are clean and contributors have a repair path.

### 6. Preserve history without keeping noise active

- Keep completed task records when they are useful delivery history.
- Mark replaced work `superseded` and link the successor.
- Mark deliberately paused work `deferred`; do not leave it ambiguously `blocked` forever.
- Treat `tasks/index.md` as generated navigation, not a hand-edited source of truth.

## Output shape

Report:

- task slug, title, and status
- workstream statuses and owners
- changed task artifacts
- validation and index result
- canonical truth still requiring RKE promotion
- external tracker reconciliation still required

## Guardrails

- Do not use chat history as the only task record after the user requests durable tracking.
- Do not put canonical product requirements only in task files.
- Do not let external issue numbers replace meaningful repository slugs.
- Do not hand-edit the generated index.
- Do not mark a task done solely because code was committed or merged.
- Do not mutate another workstream's record from an implementation branch.
- Do not create physical worktrees from this skill; route that work to `worktree-task-coordinator`.
