# Reader workspace

Use this optional surface when a person wants to read authored concepts, inspect their bound implementation or compare two records. It does not create canonical knowledge or execution records.

```text
rke view project --selection docs/knowledge/system.md --comparison src/service.ts --root <repository>
rke view export --selection docs/knowledge/system.md --comparison src/service.ts --output .engineering-workflow/cache/reader.html --root <repository>
```

`bundle` defaults to `docs/knowledge`. Selection and comparison are explicit repository-relative paths; comparison requires distinct records. The static projection includes at most 40 records, 80 relationships, 32 KiB per body and 256 KiB of body text overall. Selected implementation bindings have priority over unrelated navigation. Omitted, excluded and truncated evidence stays visible. A partial projection returns exit 3 and can still produce a useful export; producer validation remains separate.

Canonical means authored knowledge, source means source evidence and inferred means disposable generated evidence. Those classes do not establish truth or runtime reachability. Source freshness uses the existing reviewed bindings rather than a new viewer receipt. The current projection joins authored relationships, explicit source bindings, file API definitions and selected caller/callee relationships. Selected concepts retain canonical classification beyond the ranked navigation cap. Structural navigation inspects at most four selected/bound source records and eight definitions per record, one hop and 500 edges per trace. Scope/cap and unresolved/internal occurrences remain visible; capped inspection cannot establish complete coverage. Only parser-backed high-confidence links receive `confirmed-static`; reviewed/semantic links remain inferred candidates in this view. Bare unresolved names never select a guessed file. Source-index, definition and trace changes during projection withhold the result. Selected-workspace reading uses the existing caller-authorized workspace session; see below.

The reader offers search, an outline, source line numbers, an evidence inspector, comparison panes, local selection links, browser history and keyboard navigation. Relationships start collapsed and retain their declared verbs. The inspector separates Incoming → Selected → Outgoing, initially includes four links per direction and reveals additional links in bounded steps with explicit hidden counts. Expansion and reading position survive navigation within the exported snapshot. Candidate links retain unresolved labels and a dashed marker. Export-wide omissions have unknown direction and cannot establish complete dependency coverage. Internal Markdown links navigate only included unambiguous records. Remote links and active markup remain text; images, fonts and connections are disabled by the export's content policy. No Markdown or source content can choose a command or a root.

Explicitly labelled Mermaid fences offer on-demand diagram rendering in an opaque script-only sandbox. Original source remains available; errors, timeouts, unavailable assets, unclosed fences and rendering bounds retain plain source. At most eight fences with 8 KiB each receive controls per export, with 128 library edges and 15 seconds per attempt. Only the exact owned frame and current job can report a bounded state and height. Selection changes dispose frames and pending work. The pinned licensed asset is read only when an eligible fence exists; ordinary reading does not execute or initialize the browser engine. Diagram styles and source text stay separate from the parent document and from canonical or structural evidence. Browser fidelity and installed diagram qualification are in progress; deterministic controller tests alone do not establish them.

Exports write a separate HTML file. Existing output requires `--expected-digest` with its exact current `outputDigest`; mismatched, linked, oversized or missing expected output is refused. Preflight and a local lock protect reconciliation, with the usual filesystem concurrency limits. Prefer ignored local exports. The viewer does not validate OKF Tasks, and hiding a record cannot clear its independent validation obligations.

Static browser and deterministic fixture checks are qualification evidence for the reader mechanics. They do not replace the planned formative user study. Fixed-root loopback operation and installed CLI/MCP lifecycle checks have separate evidence in the current qualification ledger; a static export alone does not establish that qualification. Coordinated OKF producer/upstream viewer improvements and the formative user study remain open.

Selection and comparison retain first hydration priority. An explicitly selected explanation and up to eight relevant inferred records also retain bounded priority when requested, followed by selected call endpoints, other explicit bound sources and remaining knowledge navigation. A dense concept's binding list cannot crowd selected comparison dependencies out of the record cap. Counts still disclose every known excluded or capped relationship.

For an explicit request to see existing inferred subsystem prose, pass `--include-explanations`. Viewing reads validated current receipts; it never launches synthesis or promotes a claim. Up to eight relevant inferred records share the existing record/body caps. Withheld receipts, omitted subsystems/relationships and incomplete prepared/authored coverage keep the view partial. The inspector retains generator, source scope, confidence and producer coverage; source quotes, rationale and open questions remain visible. `freshness: not-applicable` avoids suggesting canonical verification.

To open a particular current subsystem, pass `--explanation <packet-digest>::<subsystem-id>` alongside its source/concept `--selection`. The explanation becomes primary and the selected source/concept is the default comparison. A missing, stale or out-of-scope identity is unavailable; do not clear its receipt or infer a replacement identity. Source, canonical and inferred records retain separate IDs even when they share a source path. Receipt changes during projection withhold the result. Ordinary reader requests omit derived prose.

For before/after source, pass `--base <commit-ref>` to project or export. Selection names the historical path; comparison defaults to that same path in the working tree. `--merge-base` explicitly selects the commit's merge base with current HEAD. Different paths require an explicit comparison. Git-reported rename similarity remains a candidate, and untracked moves are not guessed. Added/deleted sides retain explicit absence; protected historical content is refused. Git commit and working-byte identities remain distinct, and inputs are rechecked. No index build, review receipt or canonical freshness is created. Historical regular blobs must satisfy the same secret, binary, size and path exclusions. Body caps and partial exit 3 still apply. Keep inferred explanation selection in a separate view; source snapshots do not validate runtime execution or historical knowledge.

```text
rke view export --selection src/service.ts --base HEAD --output .engineering-workflow/cache/change-reader.html --root <repository>
rke view project --selection src/old.ts --comparison src/new.ts --base main --merge-base --root <repository>
```

Source line numbers, section permalink buttons and outline entries generate location bookmarks with an exact record identity, optional comparison, `anchor=L42` or `anchor=section:<heading-key>` and the projection's `snapshot` revision. A comparison-pane location becomes primary and retains its counterpart. Internal Markdown heading/source fragments navigate only included unambiguous records. Duplicate/Unicode headings retain distinct keys. Reload/history restore focus and highlighting. A stale, unpinned, invalid, absent or capped location produces a visible notice; do not infer another target. Document-only bookmarks remain compatible and both panes retain reading position.

Documents and Evidence buttons collapse their side panes independently while retaining selection and reading positions. Pane sizes offers labelled keyboard/pointer range controls with bounded widths and comparison balance; Reset restores visible panes/defaults. Controls disable when narrow layouts stack that dimension. `/` reveals document navigation and focuses search. Coverage stays outside the collapsed navigation. Preferences are page-session state, not canonical data or saved reload settings.

This comparison is side-by-side source, without automatic path pairing or aligned line diffs. Live refresh uses a separate fixed-root local session.

For current records in explicitly selected repositories, use `workspace view project` or `workspace view export` with `--manifest`, `--selected-repository`, `--selection`, and optional `--comparison-repository` plus `--comparison`. Read the workspace federation contract first. Caller allow-roots remain independent of declarations. Every selected root retains its status/snapshot/omissions; a failed primary produces no export, and a failed comparison root remains visible beside the available primary. Roots without a reader seed are checked but contribute no documents. Do not infer a seed or another repository from matching names.

Workspace records/bookmarks use alias-qualified identities, and local links remain within the owning root. Search includes repository aliases; the repository filter narrows navigation. Primary and comparison records have first priority, followed by alternating local ranks within the existing shared caps. Canonical/source/inferred provenance and reviewed freshness remain separately owned. Source-bound workspace dependencies retain declaration kind/resolution as inferred candidates, never runtime confirmation. Missing endpoints, unresolved declarations and omitted links keep coverage partial.

Scopes narrow hydration, bindings, traces and inferred receipts. Authored validation needs the complete selected knowledge bundle within scope; `--bundle` and `--comparison-bundle` select explicit alternative bundles. Index refresh and producer freshness still operate inside the authorized repository; scopes are query/hydration bounds rather than a filesystem sandbox. Explanation flags apply to the primary root, and cross-scope receipts are withheld. Reader evidence is checked again after aggregation, then all root snapshots and the manifest are rechecked. Changed roots lose their records/dependent links. These checks do not create a global transaction or knowledge-review receipt. Git-base source comparison remains single-root; this workspace adapter reads current evidence.

```text
rke workspace view export --manifest workspace.json --selected-repository service --selection docs/knowledge/system.md --comparison-repository client --comparison src/service.ts --root <owner> --allow-root <permitted-root>
```


## Fixed-root live reading

Use `view serve` or `workspace view serve` with the same selection arguments as projection. The receipt contains a private loopback URL; keep the CLI or MCP process alive while reading. Refresh snapshot reloads the captured selection and preserves location bookmarks. A changed projection revision makes old bookmarks visibly stale.

The server binds only to 127.0.0.1 on an ephemeral port. Its authenticated GET route accepts no replacement root, path, operation or selection. Sessions capture physical owner/caller roots, selected workspace topology/scopes and request arguments. Physical replacement, retargeting or scope changes require a new session; unavailable or denied children cannot gain authorization on refresh. An explicit single-root Git baseline resolves once at startup. Source evidence is recomputed through the existing producers and caps; refresh creates no canonical knowledge or review receipt.

Keep the URL private because its nonce grants access to the selected evidence. Responses disable caching and remote execution/connections. Invalid request authority is rejected before projection; unavailable evidence returns an opaque failure without serving an older snapshot. Each process supports at most eight sessions, closes idle sessions after ten minutes, and owns their cleanup. MCP input closure drains queued calls before closing its sessions; stopping the owning CLI closes its reader. Offline exports remain independent of a running process.

`rke view serve --selection src/service.ts --root <repository>`

`rke workspace view serve --manifest workspace.json --selected-repository service --selection src/service.ts --root <owner> --allow-root <permitted-root>`


## Code presentation

The reader colors recognized source extensions and explicitly labelled code fences using pinned highlight.js 11.12.0 at export/refresh time. Grammars load only when highlighting is requested. No browser highlighter or remote asset is required. The library's result passes a span/text-only conversion with exact reconstructed-text comparison, then the client creates text nodes and styled spans. Multiline comments/strings retain context; source line numbers and snapshot-bound locations retain their original identities.

Decoration is disposable presentation, not structural or semantic evidence. Unknown/unlabelled languages, failed conversions, oversized token runs and the 64 KiB aggregate decoration cap fall back to plain original code. The original projection, body caps, provenance and content digests remain unchanged. Empty fenced lines remain empty, and source-line placeholders retain their existing layout. Syntax support does not establish parser or language-server qualification. Explicit Mermaid fences use the isolated on-demand rendering described above, retaining original source.

The HTML output/replacement bound is 12 MiB, separate from all projection/body/diagram-input budgets. Existing output still requires its exact current digest and a regular unlinked destination. The extra presentation asset must not silently make an export impossible to refresh.

Diagram labels retain authored SVG size with scrolling inside the frame, and reduced-motion preferences disable animation. Dense/mobile fidelity remains separately qualified; a ready message does not prove readability.

Generated diagram SVG is bounded to512KiB, parsed and checked before adoption inside the opaque frame. Nonces are assigned to sandbox-created styles before insertion; the parent keeps its script and stylesheet policies. Dense30-node mobile fixtures retain16px labels and scroll to the final node without page-wide overflow or HTTP requests. Browser checks qualify those concrete fixtures, not arbitrary diagrams or human usability.
