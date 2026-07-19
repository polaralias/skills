# local-handoff checklist

- confirm the session really needs a continuation artefact
- choose mode: `standard` by default, `max-verbosity` only when the trigger is clear
- find the project root
- ensure `docs/handoff/` exists or choose the project's established handoff area
- if the user wants a local-only handoff, prefer `local-docs/handoff/` when the repo uses that convention
- update an existing same-day same-stream handoff when that is the cleanest continuation path
- use a dated deterministic filename
- in `standard` mode, reference canonical docs instead of duplicating them
- in `max-verbosity` mode, preserve the same core structure but expand the highest-value continuation detail first
- exclude secrets and sensitive values from the handoff
- in `max-verbosity` mode, mark observed facts, inherited context, and inference clearly when they differ
- in `max-verbosity` mode, state the as-of point and call out environment-specific facts when relevant
- record branch, verification state, and local-state assumptions when relevant
- record the current workflow stage, current skill, and next skill when the session follows an explicit engineering workflow
- record verification status and the next concrete task
- add optional appendices only when they materially improve restart safety
- finish by telling the user the handoff path and, when relevant, remind them that future local-only handoffs can live under `local-docs/handoff/`
- point the next session at the recommended `local-pickup` skill
