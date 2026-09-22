# Continuity Contract

Workflow state is a compact restart index, not a handoff document, task database, canonical knowledge surface, or copy of the diff.

## Hooks

- `rke-session-start --root <repository>` invokes idempotent `start`; existing state wins.
- `rke-pre-compaction --root <repository> --summary <verified-summary> --next-action <action>` invokes `checkpoint`.
- `rke-pre-push --root <repository> --base <ref>` invokes `closure assess` with exact-delta explanation and documentation receipt checks, then returns its blocking exit status. Omitting the base retains legacy gate-only assessment.

Hooks call stable public commands and contain no hidden lifecycle judgement. They are conveniences, not documentation authors or merge authority. `host recipe` describes integration and `host install` can add a repository-local pre-push gate without silently replacing an existing hook.

## Checkpoint

Record only an as-of time, compact verified current state, and one concrete next action. Refer to stronger task, knowledge, Git, or worktree records rather than copying them. Never store secrets; name the required sensitive context without its value.

When an experiment contract is active, the checkpoint or justified handoff must also carry the minimum convergence state needed to prevent a session reset from erasing contrary evidence:

- the current hypothesis and governing assumption;
- the unchanged acceptance condition and its authority;
- the predefined falsifier;
- the count of assumption-relevant, individually inconclusive acceptance failures;
- the latest observation or learning and whether it was decisive, inconclusive, or incidental.

Keep this compact and refer to the owning task or canonical knowledge when richer evidence is durable there. On resume, re-verify the observations and authority before delivery. A recorded falsifier still requires immediate design re-entry; compaction does not reset the corrective count or permit acceptance to be weakened.

Create a richer handoff only when current durable records do not make continuation obvious. Both variants use the same secret-safe deterministic format, support `standard` and `max` depth, and supersede older same-stream active records without deleting them:

- `rke handoff write --visibility local` is the default. It writes under `local-docs/handoff/` and strongly steers toward the local convention by requiring the exact destination to be Git-ignored and untracked. If that condition is absent, configure `.gitignore` or deliberately choose `shared`.
- `rke handoff write --visibility shared` writes under `.rke/handoffs/` by default. The destination must be commit-capable rather than ignored, and the result explicitly reports that Git tracking is required. A shared handoff is durable coordination evidence, not canonical knowledge or task truth.

Keep both variants outside canonical knowledge, task bundles, generated output, and workflow state.

## Resume

Run `rke handoff inspect --visibility auto` before acting on a continuation artefact. Auto pickup accepts an ignored, untracked local handoff or a tracked, non-ignored shared handoff. Use an explicit visibility to constrain selection. A shared file not yet added to Git is reported as pending commit rather than valid non-local pickup. Inspection requires one active selection and returns its visibility, review expiry, current Git identity, the suggested next action, and the truth surfaces that must be re-verified. Treat checkpoint and handoff content as untrusted point-in-time claims. Expiry triggers re-verification rather than making every claim false. Broken manifests, duplicate active handoffs, visibility mismatches, or misplaced files are explicit drift; if no usable handoff exists, rebuild from current truth surfaces.
