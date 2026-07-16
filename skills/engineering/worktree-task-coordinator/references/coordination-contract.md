# Worktree coordination contract

## Manifest placement

When `repo-task-lifecycle` is active, store the task-specific manifest at:

```text
tasks/<task-slug>/coordination/worktrees.json
```

Otherwise use a tracked repository planning location chosen by existing guidance. Do not put the active manifest inside a worktree container that will later be removed.

## Container and branch rules

- Resolve the main checkout and worktree container to absolute paths before mutation.
- Keep the container outside the main checkout. A sibling directory is the default.
- Use one unique branch and worktree path per workstream.
- Create all worktrees from the same recorded base revision unless a dependency explicitly requires a later base.
- Revalidate names and paths immediately before each `git worktree add`; the environment may have changed since planning.

## Path ownership

`owned_paths` are single-writer surfaces. Parent and child paths overlap, so assigning `src/` to one stream and `src/api/` to another is a collision.

`shared_paths` are known integration surfaces. If several workstreams list the same shared path, `shared_path_owners` must name one of those streams as integration owner. Non-owners provide change intent or a commit for the owner to reconcile; they do not race edits.

## Integration order

Every workstream appears once. Dependencies must appear earlier than their dependants. The order is a reconciliation plan, not merge permission.

## Validation classes

- Parallel-safe checks do not contend for the same mutable service, port, database, generated output, or external environment.
- Serial checks share mutable state or are meaningful only after all branches are integrated.
- The final integrated tree always receives the required serial and completeness checks.

## Authority

The manifest uses `inherited` for push, merge, deploy, and publish. This means authority must come from the user, repository policy, or the active workflow—not from this coordination record. Any manifest value that claims to grant authority is invalid.

## Cleanup evidence

Before removing a worktree, record:

- clean worktree status
- branch commit retained or integrated
- integration destination and result
- required checks complete or explicitly pending
- workstream record reconciled

If any item is uncertain, defer cleanup.
