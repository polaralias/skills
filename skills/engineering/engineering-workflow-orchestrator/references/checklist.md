# engineering-workflow-orchestrator checklist

- classify the current stage before routing the session
- choose the narrowest downstream skill that matches the current slice
- keep current stage, current skill, next skill, canonical references, and verification state explicit
- treat workflow-state as subordinate to canonical docs and verified repo state
- use hook setup only when it reinforces continuity rather than adding noise
- keep Codex and Claude hook config project-local when possible
- verify the documented host lifecycle before claiming compaction-aware continuity support
- use hook events to surface state and handoff expectations, not to pretend a skill body executed automatically
- when using richer continuity hooks, define deterministic outputs for transcript backup, verbose handoff, restart supplement, and manifest
- make `PostCompact` consume the short restart supplement rather than the full verbose handoff
- route pause and resume through `local-handoff` and `local-pickup`
- run repo-change-comprehension for the final material implementation delta before session alignment
- keep commit-safe facts separate from the richer user explanation and optional question invitation
- route verified gaps exposed by follow-up questions through RKE, QTK, TDD, or RTL, then re-close the affected slice
