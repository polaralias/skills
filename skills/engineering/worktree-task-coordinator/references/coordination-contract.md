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
- Create every linked checkout with Git worktree commands; a copied repository directory is not a worktree and must not be registered as one.
- Use one unique branch and worktree path per workstream.
- Create all worktrees from the same recorded base revision unless a dependency explicitly requires a later base.
- When a remote is authoritative, resolve the recorded base from refreshed remote-tracking state rather than assuming the local default branch is current.
- Revalidate names and paths immediately before each `git worktree add`; the environment may have changed since planning.
- Use a dedicated integration worktree when unrelated changes make the primary checkout unsafe as the integration surface.

## Delivery topology

`delivery_topology` defaults to `parallel` when it is absent from an existing schema-version-1 manifest.

- `parallel`: workstream branches are siblings from the recorded common base and remain independently landable.
- `integration-branch`: source branches feed one recorded integration branch before the durable destination.
- `stacked`: every layer has one direct predecessor, the bottom layer targets `integration_destination`, and `integration_order` lists the chain from bottom to top.

For stacked delivery, record `base_ref` and `stack_parent` on every workstream. The bottom layer uses a null parent. Every higher layer uses the preceding workstream slug as its parent, names that workstream in `depends_on`, and uses the parent's branch as its direct base. A branching dependency graph is not a valid stack.

Provider-native stack publication is a runtime capability. Verify current provider support, repository eligibility, authentication, CLI or API behaviour, merge rules, and linked-worktree compatibility before mutation. Do not install tooling, push branches, create reviews, rebase, or merge merely because the manifest selects `stacked`.

## Path ownership

`owned_paths` are single-writer surfaces. Parent and child paths overlap, so assigning `src/` to one stream and `src/api/` to another is a collision.

`shared_paths` are known integration surfaces. If several workstreams list the same shared path, `shared_path_owners` must name one of those streams as integration owner. Non-owners provide change intent or a commit for the owner to reconcile; they do not race edits.

A stack does not silently relax path ownership. When consecutive layers intentionally change the same path, declare it shared and serialise the handoff from the lower layer to the higher one. Compare each stacked layer with its direct base so inherited lower-layer changes are not misreported as new ownership.

## Integration order

Every workstream appears once. Dependencies must appear earlier than their dependants. The order is a reconciliation plan, not merge permission.

For stacked delivery the order is the stack itself. Merge or queue only the contiguous ready prefix beginning at the lowest unmerged layer. After a lower layer changes or lands, treat all higher recorded tips and checks as stale until the provider or local stack operation has finished and every layer has been refreshed.

## Validation classes

- Parallel-safe checks do not contend for the same mutable service, port, database, generated output, or external environment.
- Serial checks share mutable state or are meaningful only after all branches are integrated.
- The final integrated tree always receives the required serial and completeness checks.

## Authority

The manifest uses `inherited` for push, merge, deploy, and publish. This means authority must come from the user, repository policy, or the active workflow—not from this coordination record. Any manifest value that claims to grant authority is invalid.

## Integration evidence

Record integration evidence against the exact source tip. Supported proof modes are:

- `ancestry`: current Git history proves the source tip is reachable from the intended durable destination.
- `exact-review-head`: the merged review's recorded head object ID equals the source tip and its base equals the intended destination.
- `recorded-rewrite-chain`: evidence maps the source tip through an integration branch or history-rewriting operation to a terminal merged review and the verified final tree.

Use full object IDs in durable evidence. A branch name may be reused, a local branch may advance after publication, and a remote branch may be deleted without merging. Review lookup must therefore include repository identity, review identifier, base, head branch, head object ID, and state. Choose the exact review; never select the first same-named result.

`durably-integrated` means the selected proof has been checked against current Git and provider state. A manifest value cannot grant that state by itself. Refresh it after bot commits, merge-queue changes, rebases, or any other operation that can move a branch.

## Cleanup evidence

Before removing a worktree, record:

- clean worktree status
- branch commit retained or integrated
- integration destination and result
- required checks complete or explicitly pending
- workstream record reconciled
- current local branch tip and its matching integration source tip
- remote branch state
- cleanup disposition and reason

`ready` requires a clean worktree, an absent remote branch, and `durably-integrated` evidence whose source tip equals the current local branch tip. `removed` records the same proof after the registered path is gone. Use `retained` for deliberately preserved work and `deferred` when any required observation is unknown or still pending.

Remove the registered clean worktree without force before deleting its branch. Use ancestry-aware branch deletion when ancestry is preserved. Forced local branch deletion is allowed only for a rewritten history whose exact current tip has durable integration evidence. If any item is uncertain or changed since verification, defer cleanup.

Inspect worktree pruning with a dry run. Pruning only clears administrative entries for missing paths and is not integration evidence.

Delete the sibling container only after both the registered inventory and physical directory confirm that it is empty.
