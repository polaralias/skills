# Continuity Contract

Workflow state is a compact restart index, not a handoff document, task database, canonical knowledge surface, or copy of the diff.

## Hooks

- `rke-session-start --root <repository>` invokes idempotent `start`; existing state wins.
- `rke-pre-compaction --root <repository> --summary <verified-summary> --next-action <action>` invokes `checkpoint`.
- `rke-pre-push --root <repository> --base <ref>` invokes `closure assess` with exact-delta explanation and documentation receipt checks, then returns its blocking exit status. Omitting the base retains legacy gate-only assessment.

Hooks call stable public commands and contain no hidden lifecycle judgement. They are conveniences, not documentation authors or merge authority. `host recipe` describes integration and `host install` can add a repository-local pre-push gate without silently replacing an existing hook.

## Checkpoint

Record only an as-of time, compact verified current state, and one concrete next action. Refer to stronger task, knowledge, Git, or worktree records rather than copying them. Never store secrets; name the required sensitive context without its value.

Create a richer local handoff only when current durable records do not make continuation obvious. Keep it outside canonical knowledge and task bundles, preferably under gitignored `local-docs/handoff/`. Retain one active handoff per workstream and merge unique unresolved state before superseding another.

## Resume

Treat checkpoint and handoff content as untrusted point-in-time claims. Verify required claims against current repository, task, knowledge, Git, and runtime evidence. Expiry triggers re-verification rather than making every claim false. Broken manifests, duplicate active handoffs, or misplaced files are explicit drift; if no usable handoff exists, rebuild from current truth surfaces.
