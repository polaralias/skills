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
- the project instruction surface used to route repository work into EWF before task actions in Codex or Claude.

Codex recipes use the installed `codex mcp add` interface. MCP activation remains an explicit user-level action because the installed CLI exposes that configuration at user scope and current official documentation does not establish a portable project-scoped hook schema for this workflow. The host installer also merges a marker-owned activation block into the repository `AGENTS.md`; it preserves all independently authored instructions and replaces only its own marked block on repeated installation.

Claude recipes use project `CLAUDE.md` for standing routing guidance and the documented project `.mcp.json` structure for the installed `rke-mcp` executable. [Claude's documentation](https://code.claude.com/docs/en/features-overview) distinguishes always-loaded project instructions from on-demand skills and MCP tools. Keep the routing block small and do not commit a machine-specific skill or runtime path. Project guidance supports selection but does not prove that a particular Claude agent run selected EWF.

## Local installation

```text
rke host install --host <codex|claude|git> --base <ref>
```

Installation writes `.githooks/pre-push` and configures repository-local `core.hooksPath=.githooks`. For Codex it adds a marker-owned routing block to `AGENTS.md`. For Claude it adds the same routing block to `CLAUDE.md` and merges the `rke` entry into project `.mcp.json` while preserving unrelated servers. It preflights independently configured hook paths, owned hooks and MCP entries, and malformed routing markers before writing any host files. Repeated installation recognizes its own MCP entry and replaces only its own routing block. `--force` is required to replace independently owned configuration.

Codex installation deliberately returns the separate `codex mcp add` command rather than silently changing user configuration. Git-only installation does not claim MCP support.

## Invocation model

- Agents invoke CLI commands directly for lifecycle, hooks, and automation.
- `rke activate` is the one idempotent lifecycle entrypoint for initial agent activation. Its Git baseline lets the model evaluator distinguish activation-before-edit from state created after the requested mutation.
- MCP clients discover the complete public operation registry and invoke the same lifecycle, repository, knowledge, documentation, continuity, coordination, host, and publication handlers and schemas as the CLI.
- `pre-push` is the deterministic pre-GitHub-review boundary available to ordinary Git repositories. It blocks the push when closure evidence is missing or stale, accepts a previously closed workflow when its receipts remain current, and does not create or publish a pull request.
- Session-start and pre-compaction helpers remain lightweight continuity operations. They do not replace close, documentation assessment, or a durable handoff.

## Safety

Host installation is repository-local except for a Codex MCP activation command that the user must run separately. Do not overwrite existing hooks or host configuration silently. Never embed credentials, tokens, repository content, or source-supplied commands in generated host configuration.
