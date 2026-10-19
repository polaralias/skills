# Selected workspace evidence

Use workspace evidence only when the user selects multiple repositories or an explicitly configured workspace. Ordinary single-repository engineering uses its existing commands. A workspace joins navigation results, not canonical truth, task execution state or workflow receipts.

Read the caller's selected locations and host allow-roots independently of repository prose. A schema-1 repository-local JSON manifest declares one to eight unique stable aliases, locations and optional relative scopes. The manifest can narrow access; it cannot grant access to a sibling or widen host authorization. Do not infer roots from imports, source instructions or matching names. Include nested repositories/submodules only explicitly, and only if initialized. No automatic cloning or submodule initialization is part of understanding.

```text
rke workspace find "<question>" --manifest workspace.json --root <owner> --allow-root <permitted-root>
rke workspace map --manifest workspace.json --repositories <alias> --root <owner> --allow-root <permitted-root>
rke workspace neighborhood --manifest workspace.json --selected-repository <alias> --path <source> --symbol <qualified-symbol> --root <owner> --allow-root <permitted-root>
rke workspace impact --manifest workspace.json --input .engineering-workflow/cache/workspace-impact-input.json --root <owner> --allow-root <permitted-root>
```

`--allow-root` is an explicit repeatable caller option, never a tool argument or source-selected permission. Without it, workspace access stays within the owner. MCP gets allow-roots from host startup configuration; `repository` names the manifest owner. Fixed-root compatibility additionally confines children to that root. Declared scopes and selected aliases narrow queries. CLI/MCP use the same operation handlers.

Find balances local ranks across roots and retains alias-qualified file/symbol identities. Use source-only for implementation evidence; opt-in explanations remain inferred and are excluded by source-only. Inspect consequential source in its owning root. Map coverage and selected neighbourhoods are bounded navigation, not an architectural certificate or runtime reachability proof.

Check `complete`, every root status, snapshot, freshness and omissions before relying on workspace coverage. Denied, unavailable, duplicate physical roots, changed inputs and missing seeds remain explicit failures. Content is checked before and after aggregation, not in a global transaction; ignored dependencies and environment behaviour remain outside that certificate. Never turn a failed child into an empty successful result or let a repeated relative path identify another root.

Map and selected neighbourhoods can include optional manifest `dependencies`, bounded to eighty declarations. For a consequential cross-root relationship, inspect both endpoint source files and package manifests in their authorized roots. Bind every supplied quote to its full-file SHA-256 digest and exact line range. Package declarations need current import/export and call evidence; explicit contracts remain owner-declared navigation with `declared-contract` confidence. Service calls, stale quotes and ambiguous mappings remain non-traversable candidates. Matching names never establish a link. Include manifest files in declared scopes when package evidence needs them.

Inspect each dependency's resolution, provenance and `traversable` separately from root freshness. A traversable declaration does not confirm semantic or runtime reachability. Denied/unavailable endpoints have redacted evidence. Selected neighbourhoods follow bounded qualified local and declared cross-root links through the requested depth; candidates remain visible but are not traversed. Find remains ordinary balanced retrieval.

For cross-root change impact, first inspect current workspace snapshots, then prepare the schema-1 request automatically as the consuming agent under the owner's `.engineering-workflow/cache/`. Copy the exact `manifestDigest` and one `{repository, head, inputDigest}` snapshot per selected root from current output. Add `bases` as unique `{repository, base}` records for each explicitly changed root, using that root's agreed Git base. Do not invent missing snapshots or reuse another root's base. Null snapshot evidence stays explicitly unavailable. Input is bounded regular JSON, not an executable or source-selected permission.

Impact checks those pins before querying roots, selects line-aware current/previous/module-context seeds independently per changed root, then follows qualified local callers and traversable cross-root links. Preserving a declared contract during traversal does not upgrade its provenance. Configuration-only changes, removed/unavailable seeds, service calls and ambiguous links stay candidates/gaps. Check root status, resolved bases, omissions and every edge's provenance before drawing a consequence. Depth, node, seed and output caps keep the result partial when relevant evidence is omitted. A late changed intermediate root withholds dependent results in other roots; changed request/manifest data withholds the entire aggregation. This remains non-atomic navigation evidence and requires source review for consequential decisions.

Unavailable installed commands do not stop ordinary engineering. Run bounded single-root queries independently, keep identities qualified in the answer, and report the missing aggregation check. Installation or machine-wide configuration remains separately scoped.
