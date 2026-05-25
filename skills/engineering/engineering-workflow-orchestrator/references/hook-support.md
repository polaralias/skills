# Hook Support

This skill should only describe hook setup that matches real host support.

## Codex

Codex supports project-level hooks.

Relevant surfaces:

- `.codex/hooks.json`
- equivalent inline Codex config when the project uses that instead of a dedicated hooks file

Relevant events for this workflow:

- `SessionStart`
- `PreCompact`
- `PostCompact`

Use these events to surface workflow-state, remind the session to refresh a handoff before compaction, and restate the saved workflow stage after compaction.

## Claude Code

Claude Code supports project-level hooks in:

- `.claude/settings.json`

Relevant events for this workflow:

- `SessionStart`
- `PreCompact`
- `PostCompact`

Use the same contract across both hosts where possible so the workflow-state stays portable.

## Recommended behavior

- keep hooks small and deterministic
- point them at project-local helper scripts or compact shell commands
- prefer reminders, validation, and state surfacing over large generated narratives
- avoid writing sensitive values into workflow-state or handoff artifacts
- keep `local-handoff` and `local-pickup` as the durable skills for pause and resume logic

## Example hook responsibilities

- `SessionStart`: show active workflow stage, current goal, and canonical refs
- `PreCompact`: verify whether workflow-state and handoff are present and current
- `PostCompact`: restate workflow stage and recommend `local-pickup` or the next downstream skill
