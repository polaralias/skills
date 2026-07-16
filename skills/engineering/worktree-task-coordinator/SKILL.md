---
name: worktree-task-coordinator
description: Coordinate concurrent Git work through explicit worktree, branch, path-ownership, dependency, integration-order, and verification records. Use when one repository task has two or more independently mergeable workstreams, when agents need isolated checkouts, or when parallel changes must be reconciled safely. Do not use it to design the backlog, implement the changes, or grant merge, deployment, or external-system authority. Shorthand WTC.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-07-16'
---

# worktree-task-coordinator

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `worktree-task-coordinator was used in this response.`

Use this skill to make concurrent Git work physically separate, explicitly assigned, and safely reconcilable.

Read [references/coordination-contract.md](./references/coordination-contract.md) before creating worktrees. Use [scripts/worktree_manifest.py](./scripts/worktree_manifest.py) to validate a coordination manifest before creating or integrating worktrees.

## Boundaries

- `repo-task-lifecycle` owns the parent task record, task status, workstream records, and task index.
- `doc-driven-development` owns feature contracts and work-package design.
- Each assigned implementation agent owns changes inside its worktree and declared paths.
- This skill owns worktree layout, branch allocation, collision prevention, dependency order, reconciliation, and cleanup.
- Existing repository policy and the user own merge, push, deployment, and external-system authority. A coordination manifest records those limits; it cannot widen them.

Use a single checkout when the work is sequential, tightly coupled, or too small to justify isolation.

## Workflow

### 1. Confirm a parallel-safe split

- Start from an implementation-ready task or work-package set.
- Split only where each workstream has a coherent outcome and can be committed independently.
- Record shared paths explicitly. Give a shared path one integration owner or serialize edits to it.
- Keep task-level metadata under the lifecycle coordinator; workstreams update only their own record.

### 2. Inspect the repository before mutation

- Confirm the repository root, clean status, current branch, remotes, and base revision.
- Run `git worktree list --porcelain` and inventory existing branches before choosing names or paths.
- Use a sibling container outside the primary checkout, such as `<parent>/<repo>-worktrees/`; do not nest worktrees inside the repository.
- Respect repository branch naming rules and the intended integration destination.

### 3. Write and validate the manifest

Start from [assets/worktree-manifest.template.json](./assets/worktree-manifest.template.json). Store the task-specific copy under the task folder when `repo-task-lifecycle` is active.

Record:

- repository root and sibling worktree container
- base revision and integration destination
- workstream slug, branch, worktree path, owner, dependencies, and status
- owned and shared paths
- integration order
- validation commands classified as parallel-safe or serial
- inherited authority boundaries

Run:

```text
python scripts/worktree_manifest.py validate --manifest <path>
```

Fix every collision, invalid path, dependency cycle, and authority expansion before creating a worktree.

### 4. Create and assign worktrees

- Create one branch and one worktree per workstream from the recorded base revision.
- Use `git worktree add -b <branch> <path> <base>` only after confirming neither the branch nor path already exists.
- Tell each worker its worktree, branch, owned paths, shared-path rule, acceptance surface, validation obligations, and prohibited actions.
- Require each workstream to finish with a committed branch and an updated workstream record. Uncommitted edits are not a handoff.

### 5. Monitor without collapsing isolation

Track these axes separately:

- Git: clean/dirty, committed/uncommitted, ahead/behind
- staged or integrated: absent/partial/complete in the integration destination
- deployed or published: not attempted/pending/succeeded/failed
- live or externally verified: unverified/verified/limited/broken

Do not translate success on one axis into success on another. Wait for asynchronous checks when they are part of completion; unchanged pending state is not a failure.

### 6. Reconcile in dependency order

- Refresh the integration destination before integrating.
- Check each branch contains the expected commits and only the intended path surface.
- Compare source artifacts with their staged or mirrored destination when the workflow copies or packages files.
- Treat renames and moves as shared structural operations: assign one owner, verify the old path is absent, the new path is present, and no other branch recreated a stale copy.
- Integrate in the manifest order, resolving shared paths through the assigned integration owner.
- After each integration, verify that previously integrated behavior remains present.
- Judge completeness from the final integrated tree, not from isolated worktree success.

Run parallel-safe checks as early as useful. Run serial or shared-resource checks against the final integrated tree.

### 7. Close and clean up

- Reconcile lifecycle records and evidence before declaring the task complete.
- Remove worktrees only after confirming they are clean and their commits are safely integrated or intentionally retained.
- Prune stale worktree metadata after removal.
- Delete branches only through the repository's normal post-merge policy.
- Preserve the manifest as coordination evidence when the repository keeps task history.

## Output shape

Report:

- manifest path and base revision
- worktree/branch assignment table
- owned/shared-path decisions
- dependency and integration order
- per-axis verification state
- cleanup performed or deliberately deferred
- any authority the user or repository policy must still supply

## Guardrails

- Do not create overlapping path ownership without an explicit integration owner or serialization rule.
- Do not assign two worktrees the same branch or path.
- Do not create worktrees inside the main checkout.
- Do not merge, push, deploy, publish, or change external state merely because the manifest names that destination.
- Do not remove a dirty worktree or an unintegrated branch.
- Do not let worker branches edit the task index or parent task record unless they are the lifecycle coordinator.
- Do not accept a copy or move as complete without source-to-destination parity and stale-path checks.
- Do not treat passing isolated tests as proof that the integrated tree is complete.
