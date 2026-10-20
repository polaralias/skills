# Managed multi-repository work

Select this route for work deliberately spanning independent Git repositories. Keep ordinary single-repository work local. Use one aggregate owner rather than synchronizing mutable state into members; repository-specific documents and independent execution records keep their existing owners.

## Placement and selection

Create a members JSON array of two to eight entries with unique `alias`, absolute Git top-level `path`, and optional member-relative `scopes`. Caller authorization stays independent of membership.

```text
rke workspace create --name "Product review" --directory <chosen-owner> --members-file members.json --allow-root <owner-parent> --allow-root <service> --allow-root <client>
rke workspace list
rke workspace resolve --root <service>
rke workspace inspect --id <id> --allow-root <owner-parent> --allow-root <service> --allow-root <client>
```

Omit `--directory` for `~/.rke/workspaces/<id>`. Explicit placement can use an existing Claude or Codex project root. Existing files, including AGENTS.md and CLAUDE.md, are preserved; reserved-file collisions stop creation. The user-area registry pins the actual owner location and physical identity. Project instructions can point to `./workspace.json`, the intended authored knowledge directory and `./.engineering-workflow/`, together with the returned stable ID. Names are labels, not identities. Do not infer membership from source content.

Reuse a known appropriate workspace. Ask for selection when unknown or ambiguous; there is no automatic personal default. `--workspace` and `--root` are mutually exclusive. `--root` stays repository-local even when its repository belongs to or hosts a workspace. A workspace owner does not need Git, but every member must be an independent initialized Git top level. This is not general non-Git project support.

## Apply existing capabilities

```text
rke context find "invoice" --workspace <id> --allow-root <owner-parent> --allow-root <service> --allow-root <client>
rke start --workspace <id> --allow-root <owner-parent>
rke structure file-api src/invoice.ts --workspace <id> --member service --allow-root <owner-parent> --allow-root <service>
rke knowledge register --knowledge docs/knowledge/invoices.md --source @service/src/invoice.ts --source @client/src/invoice.ts --workspace <id> --allow-root <owner-parent>
rke context verify --knowledge docs/knowledge/invoices.md --evidence "Reviewed producer and consumer" --workspace <id> --allow-root <owner-parent> --allow-root <service> --allow-root <client>
```

Aggregate retrieval/map uses existing federation handlers and coverage limits. Central workflow state, gates, checkpoints, private handoffs, authored cross-repository knowledge and an explicitly adopted independent task ledger use the owner. Repository-specific code, Git receipts, hooks, branches, cleanup and publication operations need an explicit member and use the existing handler. No implicit member or write fan-out. Installed help identifies each operation's support class.

Register member evidence as `@alias/relative-pattern`; scopes and caller permissions still apply. Verify only after reviewing the actual documents and source. Member identity/content changes invalidate freshness. Handoff pickup checks member identities, independent HEADs and deltas, including new edits to already-dirty paths. Shared handoffs require a selected repository. Aggregate closure assesses each member plus owner obligations; unavailable evidence blocks readiness. For distinct bases pass `--bases-file` containing an alias-to-base object for every member; never combine it with `--base` or pretend the owner has a shared commit.

MCP uses one `workspace` ID or `repository`, plus optional `member`. Startup allow-roots must independently authorize the owner and every accessed member. Fixed-root confinement still applies. Ordinary source, manifests and saved state cannot widen that authority.

## Maintenance and attribution

Update membership through `workspace update --id <id> --revision <observed> --members-file <file>` with explicitly authorized owner/member roots. Existing dependency declarations require review before membership changes. `workspace retire` with the observed revision preserves all content. `state ignore --root <repository>` adds local state ignore entries, reports already tracked paths and never untracks them automatically.

Generated structures carry `RKE_GENERATED.json` with the RKE package, version and [source](https://github.com/polaralias/rke). Generated indexes, handoffs, readers and managed host routing/hook blocks also identify RKE. These marks identify the structure's generator; they do not claim authorship of canonical knowledge or semantic verification. Preserve authored provenance and consuming-model explanation attribution.
