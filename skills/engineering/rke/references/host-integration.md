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
- the project instruction surface used to select EWF methods for material engineering and load the RKE adapter when runtime support is useful.

Codex recipes use `codex mcp add` as an explicit user-level action. Current [Codex documentation](https://developers.openai.com/codex/mcp) also supports trusted-project `.codex/config.toml` MCP configuration; the current installer keeps its activation manual. It merges owned routing into repository `AGENTS.md`. Native Codex hooks are not installed by this profile.

Claude recipes use project `CLAUDE.md` and the documented `.mcp.json` structure. MCP launches the actual loaded RKE script through the current Node executable with a root allow-list. Keep routing small; generated launch configuration contains machine-specific executable/script/root paths and should not be published as portable configuration. Project guidance supports selection but does not prove that a live agent selected EWF or the RKE adapter.

## Local installation

```text
rke host install --host <codex|claude|gemini|cursor|copilot|windsurf|kiro|git> --base <ref>
```

Installation writes `.githooks/pre-push` and configures repository-local `core.hooksPath=.githooks`. For Codex it adds a marker-owned routing block to `AGENTS.md`. For Claude it adds the same routing block to `CLAUDE.md` and merges the `rke` entry into project `.mcp.json` while preserving unrelated servers. It preflights independently configured hook paths, owned hooks and MCP entries, and malformed routing markers before writing any host files. Repeated installation recognizes its own MCP entry and replaces only its own routing block. `--force` is required to replace independently owned configuration.

```text
rke host inspect --host <host> --root <repository>
rke host status --host <host> --root <repository>
rke host preview --host <host> --action <install|repair|remove> --root <repository>
rke host install --host <host> --dry-run --root <repository>
rke host repair --host <host> --root <repository>
rke host remove --host <host> --root <repository>
```

Inspection and preview create no configuration or cache. A schema-1 local ledger at `.engineering-workflow/hosts.json` records component hashes, selected options and shared owners; it is configuration bookkeeping, not canonical knowledge or live-host proof. Repair restores missing verified entries and upgrades unchanged owned entries. Removal retains shared Git/routing resources while another host uses them; final removal restores the prior local hook-path setting. Edited owned entries, malformed/duplicate-key JSON, oversized settings, linked configuration paths and invalid ownership records are refused before host writes. Foreign JSON members and hook handlers retain their bytes. Forced replacement may retain a bounded, non-sensitive displaced component for later restoration; it does not authorize replacing subsequently modified owned entries. Writes recheck captured inputs and attempt rollback on failure, preserving later foreign edits and reporting any recovery needed. This is not a filesystem-wide transaction.

Reinstallation retains selected Claude opt-in hooks. Explicit `--post-edit false` or `--context-hooks false` removes only those owned handlers. Hooks still do not invoke a model. Unsupported automatic hooks remain manual recipes; no user-level configuration is silently changed.

Launcher receipts record the installed Node and script directory solely to compare owned configuration. Inspection can identify an unchanged launcher from another runtime location as upgradeable, and repair replaces it with the currently loaded runtime. Removal can reconcile an unchanged prior launcher without executing it. Old schema-1 receipts may recover launcher identity only from an exact unchanged generated configuration, with the selected root and base preserved. Arbitrary commands or modified entries cannot be adopted through this migration.

Git configuration scope is explicit in inspection and previews. When the owner has enabled `extensions.worktreeConfig`, installation uses `git config --worktree` and preserves common configuration and sibling hook paths. Without that extension, local hook changes require one registered worktree. Multiple worktrees refuse automatic installation even with force and return no activation command; the owner must configure isolated scope first. The installer does not enable the shared extension or migrate common Git settings automatically. See [Git worktree configuration](https://git-scm.com/docs/git-worktree#_configuration_file) for the required `core.worktree`/`core.bare` migration and older-Git compatibility boundary. A scope change while host ownership remains active requires reconciliation rather than silent adoption. Remove owned installation before an intentional scope migration. These checks qualify configured worktree isolation, not every external Git configuration migration.

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

Official contracts reviewed on 2026-10-10: [Gemini MCP](https://geminicli.com/docs/tools/mcp-server/), [Cursor MCP](https://cursor.com/docs/mcp), [VS Code MCP](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [Windsurf rules](https://docs.windsurf.com/windsurf/cascade/memories), and [Kiro steering](https://kiro.dev/docs/steering/). VS Code still supports `.vscode/mcp.json` as a compatibility format but recommends portable `.mcp.json`; the present profile preserves its existing VS Code scope. Windsurf's documented rules path remains a fallback in its current desktop documentation. Static profile coverage and live-session qualification remain separate.

`rke host install --host claude --base main --post-edit` optionally installs a documented PostToolUse hook in `.claude/settings.json`. It preserves other hooks and calls the loaded post-edit script through the selected Node executable for Edit/Write events. The helper accepts a bounded JSON file event, refreshes contained repository evidence, and returns compact caller/knowledge impact. It does not create workflow state, write canonical prose, run a model or silently verify knowledge. Errors report unavailable assistance and ordinary engineering continues. Other hosts may explicitly invoke the same helper; automatic hook configuration is not claimed for them.

## Optional stateless context

`rke host install --host claude --base main --context-hooks` merges owned `SessionStart` and `UserPromptSubmit` command hooks while preserving independent handlers. `rke-context-hook` returns a budgeted orientation at session start or three bounded retrieval candidates for a prompt. It does not create workflow state, write canonical knowledge, invoke a model, or select a root from event data. Hooks are opt-in; measure repeated context cost before enabling them. Sensitive or oversized prompts and unavailable assistance are skipped. Other hosts can invoke the same helper explicitly, but native automatic hooks are only claimed for the documented Claude event contract.

After upgrading RKE, rerun the installer for the selected host and inspect its managed routing/configuration. Verify the executable version used by installed hooks rather than assuming a global shim matches the current skill. Host configuration tests and installed-shim tests prove the wiring contract; a live agent evaluation is separate evidence.

## Installed hook boundaries

New installations pin a schema-1 physical root identity in MCP and native hook arguments and local ownership receipts. The identity binds the canonical directory's filesystem identity and `.git` directory or linked-worktree administration identity; ordinary edits and commits retain it. Replacement of the directory or Git administration at the same path invalidates it. Installed Git hooks also verify their process working directory against the pinned repository before closure assessment, so a copied hook cannot assess another worktree's changes against the original root.

MCP root options may be followed by `--root-identity <opaque-identity>`; generated recipes supply this argument. Manual root options without that argument capture identity at server startup and therefore establish a process-lifetime pin rather than installation history. Tool calls and workspace access preserve those caller boundaries. Shared operation scopes recheck identity around results and before guarded path, Git and atomic-write operations. Cached engines retain their own root identity. These checks do not provide a filesystem-wide transaction or make unverified prose trustworthy.

An older receipt lacking physical identity cannot prove its historical root. Inspection identifies launchers needing the new pin; repair may capture the currently selected root while reconciling unchanged owned components. A changed recorded physical identity refuses reconciliation, including force. Intentional repository or Git-administration relocation needs explicit owner reconciliation and fresh installation rather than automatic rebinding. Post-edit/context assistance reports unavailable evidence on refusal; the pre-push gate fails with a non-zero result.

Git execution resolves an absolute regular executable from the host PATH outside the selected repository and caller-authorized data roots. Repository cwd executables, data-root-owned PATH entries and relative PATH entries cannot choose it. Cached executable paths are resolved again before reuse. Inherited Git repository-location variables are cleared for these selected-root calls. Missing trusted Git remains an explicit unavailable capability; the runtime does not install one or execute a repository fallback.

Git hooks quote Node, script, root and base as literal POSIX shell values. Claude hooks use the documented executable/argument-vector form with the real Node executable and loaded script; this also avoids Windows npm `.cmd` shim limitations. See [Claude command hooks](https://code.claude.com/docs/en/hooks). Event-provided working directories never select the repository. Explicit helper calls without `--root` resolve the Git toplevel from the process working directory. Exact old pinned shim entries may be adopted and upgraded; modified entries remain owner changes. Roots containing host interpolation syntax are refused for automatic installation. Reinstall after upgrading and inspect the actual selected runtime; fixture coverage does not establish a live host session.

The pre-push assessment does not require or create workflow state. With no state, it validates the explicit base, applicable knowledge/freshness/claim bindings and independent task records without demanding workflow receipts. Existing state is still validated and its real gates/receipts remain enforced. Neither path claims that implementation acceptance has run or grants merge/publication authority.

Pre-push, with or without workflow state, does not adopt common folder names or document types. A Tasks root must explicitly declare OKF Tasks frontmatter in its root index; knowledge must have an OKF root declaration or RKE source registrations. Manifest freshness checks cover registered concepts wherever they live; registrations outside the default knowledge directory do not adopt unrelated notes there. Workflow state alone does not claim either bundle. Enabled lightweight/full task tracking always validates its configured bundle, even when the bundle or recognised records are missing or malformed. Mode none leaves undeclared task directories alone; an explicit OKF Tasks root declaration still requests validation. Existing workflow gates and documentation receipts remain enforced. Installing host hooks alone does not declare ownership.
