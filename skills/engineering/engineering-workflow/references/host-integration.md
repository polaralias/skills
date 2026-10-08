# Host Integration

Use this contract to expose the shared CLI/MCP core and enforce the pre-push closure gate without inventing unsupported host behaviour.

## Recipes

```text
rke host recipe --host <codex|claude|gemini|cursor|copilot|windsurf|kiro|git> --base <ref>
```

The command is read-only and returns:

- the machine-wide MCP launch or activation recipe supported by the selected host;
- the local Git `pre-push` gate path and command;
- the explicit Git base used for documentation assessment and receipts.
- the project instruction surface used to route repository work into EWF before task actions in the selected agent host.

Codex recipes use the installed `codex mcp add` interface. MCP activation remains an explicit user-level action because the installed CLI exposes that configuration at user scope and current official documentation does not establish a portable project-scoped hook schema for this workflow. The host installer also merges a marker-owned activation block into the repository `AGENTS.md`; it preserves all independently authored instructions and replaces only its own marked block on repeated installation.

Claude recipes use project `CLAUDE.md` for standing routing guidance and the documented project `.mcp.json` structure for the installed `rke-mcp` executable. [Claude's documentation](https://code.claude.com/docs/en/features-overview) distinguishes always-loaded project instructions from on-demand skills and MCP tools. Keep the routing block small and do not commit a machine-specific skill or runtime path. Project guidance supports selection but does not prove that a particular Claude agent run selected EWF.

## Local installation

```text
rke host install --host <codex|claude|gemini|cursor|copilot|windsurf|kiro|git> --base <ref>
```

Installation writes `.githooks/pre-push` and configures repository-local `core.hooksPath=.githooks`. For Codex it adds a marker-owned routing block to `AGENTS.md`. For Claude it adds the same routing block to `CLAUDE.md` and merges the `rke` entry into project `.mcp.json` while preserving unrelated servers. It preflights independently configured hook paths, owned hooks and MCP entries, and malformed routing markers before writing any host files. Repeated installation recognizes its own MCP entry and replaces only its own routing block. `--force` is required to replace independently owned configuration.

Codex installation deliberately returns the separate `codex mcp add` command rather than silently changing user configuration. Git-only installation does not claim MCP support.

## Invocation model

- Agents invoke CLI commands directly for lifecycle, hooks, and automation.
- `rke activate` initializes optional durable state. Its Git baseline helps evaluate stateful runs; EWF remains usable without the runtime.
- MCP clients discover the complete public operation registry and invoke the same lifecycle, repository, knowledge, documentation, continuity, coordination, host, and publication handlers and schemas as the CLI.
- `pre-push` is the deterministic pre-GitHub-review boundary available to ordinary Git repositories. It blocks the push when closure evidence is missing or stale, accepts a previously closed workflow when its receipts remain current, and does not create or publish a pull request.
- Session-start and pre-compaction helpers remain lightweight continuity operations. They do not replace close, documentation assessment, or a durable handoff.

## Safety

Host installation is repository-local except for a Codex MCP activation command that the user must run separately. Do not overwrite existing hooks or host configuration silently. Never embed credentials, tokens, repository content, or source-supplied commands in generated host configuration.

## Additional hosts and post-edit assistance

| Host | Routing | Project MCP |
| --- | --- | --- |
| Gemini | `GEMINI.md` | `.gemini/settings.json`, `mcpServers` |
| Cursor | `AGENTS.md` | `.cursor/mcp.json`, `mcpServers` |
| Copilot / VS Code | `.github/copilot-instructions.md` | `.vscode/mcp.json`, `servers`, stdio type |
| Windsurf | `.windsurf/rules/rke.md` | explicit user activation recipe |
| Kiro | `.kiro/steering/rke.md` | explicit user activation recipe |

Install preserves unrelated settings and servers and preflights ownership. These integrations install routing and configuration, not proof that a host selected EWF. Gemini, Cursor and VS Code use their documented project formats; Windsurf and Kiro receive routing without guessing a project MCP configuration.

`rke host install --host claude --base main --post-edit` optionally installs a documented PostToolUse hook in `.claude/settings.json`. It preserves other hooks and calls the installed `rke-post-edit` shim for Edit/Write events. The helper accepts a bounded JSON file event, refreshes contained repository evidence, and returns compact caller/knowledge impact. It does not create workflow state, write canonical prose, run a model or silently verify knowledge. Errors report unavailable assistance and ordinary engineering continues. Other hosts may explicitly invoke the same helper; automatic hook configuration is not claimed for them.

## Optional stateless context

`rke host install --host claude --base main --context-hooks` merges owned `SessionStart` and `UserPromptSubmit` command hooks while preserving independent handlers. `rke-context-hook` returns a budgeted orientation at session start or three bounded retrieval candidates for a prompt. It does not create workflow state, write canonical knowledge, invoke a model, or select a root from event data. Hooks are opt-in; measure repeated context cost before enabling them. Sensitive or oversized prompts and unavailable assistance are skipped. Other hosts can invoke the same helper explicitly, but native automatic hooks are only claimed for the documented Claude event contract.

After upgrading RKE, rerun the installer for the selected host and inspect its managed routing/configuration. Verify the executable version used by installed hooks rather than assuming a global shim matches the current skill. Host configuration tests and installed-shim tests prove the wiring contract; a live agent evaluation is separate evidence.

## Installed hook boundaries

Git and Claude hook commands quote each root/base argument as a literal POSIX shell value and pin the trusted installation root. Event-provided working directories never select the repository. Explicit helper calls without `--root` resolve the Git toplevel from the process working directory. Reinstall after upgrading to replace older unpinned managed hooks.

The pre-push assessment does not require or create workflow state. With no state, it validates the explicit base, applicable knowledge/freshness/claim bindings and independent task records without demanding workflow receipts. Existing state is still validated and its real gates/receipts remain enforced. Neither path claims that implementation acceptance has run or grants merge/publication authority.

Stateless pre-push does not adopt common folder names or document types. A Tasks root must explicitly declare OKF Tasks frontmatter in its root index; knowledge must have an OKF root declaration or RKE source registrations. Manifest freshness checks cover registered concepts wherever they live; registrations outside the default knowledge directory do not adopt unrelated notes there. Existing persisted workflow lanes retain their checks and explicitly configured task bundle. Installing host hooks alone does not declare ownership.
