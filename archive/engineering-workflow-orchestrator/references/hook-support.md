# Hook Support

This skill should only describe hook setup that matches real host support.

## Codex

Codex supports project-level hooks.

Relevant surfaces:

- `.codex/hooks.json`
- equivalent inline Codex config when the project uses that instead of a dedicated hooks file

For this skill package, treat Codex compaction continuity as unverified unless you have a current official Codex reference for stable `PreCompact` and `PostCompact` hooks.

What is safe to assume here:

- project-local hook config can exist under `.codex/hooks.json`
- thin session-start workflow surfacing is a reasonable example

What is not packaged here as a runnable example:

- a Codex `PreCompact` to transcript-backup to manifest to `PostCompact` flow

Do not present a richer Codex compaction lifecycle as implemented unless you have verified current official support.

## Claude Code

Claude Code supports project-level hooks in:

- `.claude/settings.json`

Relevant events for this workflow:

- `SessionStart`
- `PreCompact`
- `PostCompact`

Claude Code's official docs also support:

- project-local hook scripts referenced from `.claude/settings.json`
- `${CLAUDE_PROJECT_DIR}` for project-relative script paths
- `transcript_path` in `PreCompact` and `PostCompact` input payloads

Use the same artefact contract across hosts where possible, but only Claude Code gets the full runnable compaction example in this package because that is the host whose lifecycle is documented for this flow.

## Recommended behaviour

- keep hooks small and deterministic
- point them at project-local helper scripts or compact shell commands
- prefer deterministic artefact generation and state surfacing over large inline generated narratives
- avoid writing sensitive values into workflow-state or handoff artefacts
- keep `local-handoff` and `local-pickup` as the durable skills for pause and resume logic

When the host supports it, a stronger continuity pattern is:

- `PreCompact`: copy or persist the raw transcript artefact first
- `PreCompact`: invoke a helper or subagent to derive:
  - a max-verbosity handoff
  - a short restart supplement
  - a machine-readable manifest
- `PostCompact`: read the manifest and consume the short restart supplement

Prefer a deterministic filename or manifest path so `PostCompact` does not have to guess which artefact to load.
Keep the raw transcript backup outside the repo by default unless the user explicitly wants it stored locally with the project.

See also:

- Claude Code settings: [https://code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
- Claude Code hooks: [https://code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- install notes for the packaged helper: [claude-continuity-hook-install.md](./claude-continuity-hook-install.md)
- continuity manifest example: [continuity-manifest.example.json](./continuity-manifest.example.json)
- continuity helper script template: [claude-continuity-hook.py](../scripts/claude-continuity-hook.py)

## Example hook responsibilities

- `SessionStart`: show active workflow stage, current goal, and canonical refs
- `PreCompact`: verify whether workflow-state is current, persist the raw transcript if available, and refresh the derived handoff artefacts
- `PostCompact`: restate workflow stage from the saved supplement and recommend `local-pickup` or the next downstream skill
