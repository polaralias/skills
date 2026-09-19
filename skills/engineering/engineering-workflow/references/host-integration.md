# Host Integration

Use this contract to expose the shared CLI/MCP core and enforce the pre-push closure gate without inventing unsupported host behaviour.

## Recipes

```text
rke host recipe --host <codex|claude|git> --base <ref>
```

The command is read-only and returns:

- the machine-wide MCP launch or activation recipe supported by the selected host;
- the local Git `pre-push` gate path and command;
- the explicit Git base used for documentation and explanation receipts.
- the project instruction surface used to route material Codex work into EWF before task actions.

Codex recipes use the installed `codex mcp add` interface. MCP activation remains an explicit user-level action because the installed CLI exposes that configuration at user scope and current official documentation does not establish a portable project-scoped hook schema for this workflow. The host installer also merges a marker-owned activation block into the repository `AGENTS.md`; it preserves all independently authored instructions and replaces only its own marked block on repeated installation.

Claude recipes use the documented project `.mcp.json` structure and the installed `rke-mcp` executable; do not commit a machine-specific skill or Python path.

## Local installation

```text
rke host install --host <codex|claude|git> --base <ref>
```

Installation writes a local `.git/hooks/pre-push` gate. For Codex it adds the marker-owned project routing block described above. For Claude it also merges the `polaralias-engineering-workflow` entry into project `.mcp.json` while preserving unrelated servers. It refuses to replace an independently owned pre-push hook or MCP entry unless `--force` is explicit, and refuses malformed routing marker pairs.

Codex installation deliberately returns the separate `codex mcp add` command rather than silently changing user configuration. Git-only installation does not claim MCP support.

## Invocation model

- Agents invoke CLI commands directly for lifecycle, hooks, and automation.
- `rke activate` is the one idempotent lifecycle entrypoint for initial agent activation. Its Git baseline lets the model evaluator distinguish activation-before-edit from state created after the requested mutation.
- MCP clients use the same retrieval, knowledge, documentation-assessment, documentation-apply, and change-explanation cores.
- `pre-push` is the deterministic pre-GitHub-review boundary available to ordinary Git repositories. It blocks the push when closure evidence is missing or stale, accepts a previously closed workflow when its receipts remain current, and does not create or publish a pull request.
- Session-start and pre-compaction helpers remain lightweight continuity operations. They do not replace close, documentation assessment, or a durable handoff.

## Safety

Host installation is repository-local except for a Codex MCP activation command that the user must run separately. Do not overwrite existing hooks or host configuration silently. Never embed credentials, tokens, repository content, or source-supplied commands in generated host configuration.
