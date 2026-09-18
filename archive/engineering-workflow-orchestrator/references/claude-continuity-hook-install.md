# Claude Continuity Hook Install

This package includes a runnable helper script template at [../scripts/claude-continuity-hook.py](../scripts/claude-continuity-hook.py).

To use it in a real Claude Code project:

1. Copy the script into the target repository at:
   - `.claude/hooks/claude-continuity-hook.py`
2. Add or merge the example config from [claude-settings.example.json](./claude-settings.example.json) into:
   - `.claude/settings.json`
3. Keep the continuity manifest and restart supplement project-local under:
   - `.claude/continuity/`
4. Prefer the raw transcript backup outside the repo, for example:
   - `~/.agents/state/transcripts/<project>/<date>/<session>.jsonl`

Why these locations:

- Claude Code officially supports project settings in `.claude/settings.json`.
- Claude Code officially supports project-relative hook scripts and documents `${CLAUDE_PROJECT_DIR}` for referencing them safely from hook config.
- Claude Code officially documents `PreCompact` and `PostCompact` hook events, including `transcript_path` and `compact_summary` inputs.

Official references:

- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)

This helper script handles the deterministic file plumbing:

- `PreCompact`:
  - copies the raw transcript to a durable backup location
  - writes or refreshes `.claude/continuity/current.json`
- `PostCompact`:
  - stores the compact summary
  - writes `.claude/continuity/restart-supplement.md`
  - refreshes the manifest for later `local-pickup`

What it does not do:

- it does not generate a full max-verbosity handoff by itself
- it does not claim Codex parity for compaction hooks

Treat the script as a host-side continuity helper, not as a replacement for `local-handoff` or `local-pickup`.
