# Repository Context Contract

## Purpose

The repository-context core reduces repeated exploration by returning compact, exact repository evidence through a deterministic local interface. Its contracts, implementation, schemas, prompts, tests, and dependencies are independently maintained within the RKE family.

SQLite FTS5 with field-weighted BM25 is the measurable lexical baseline. It independently weights paths, filenames, complete symbols, heading ancestry, and bodies. Structural operations query normalized symbol, import, and edge rows in the same database. Further expansion must demonstrate improvement against the checked-in corpus rather than replacing the baseline by assumption.

## Public operations

### Find

```text
rke context find "<question>" [--scope <relative-path>] [--limit <count>]
```

Find automatically refreshes the disposable index and returns ranked chunks. Tree-sitter symbol spans are the preferred code-chunk boundary across supported languages; a bounded regex/text fallback remains available when structural evidence cannot be produced. Markdown chunks retain heading ancestry and split oversized sections into overlapping bounded passages. Index terms include separately weighted repository paths, filenames, complete identifiers and their camel-case or snake-case components, Markdown heading ancestry, and chunk bodies.

Results include:

- repository-relative path and exact line span;
- symbol or Markdown heading when available;
- code or documentation kind;
- the native FTS rank used for deterministic ordering;
- bounded source snippet;
- index revision and refresh counts.
- inaccessible Git-visible paths skipped during bounded scanning.

The persisted FTS table owns corpus statistics and postings, so ordinary queries do not reconstruct an in-memory JavaScript search index. Snippets are produced by SQLite around matching terms. Tree-sitter runs in the Node process with grammars loaded once; a parse failure is recorded against the affected file and does not discard valid records for unrelated files. Structural traces are navigation evidence, not proof of runtime reachability.

Refresh is content-incremental and does not treat ordinary filesystem metadata as content identity. Every hot Git query checks porcelain status and HEAD, then hashes only dirty paths against the last indexed state. A stable modified working tree reuses the index; another edit to the same path triggers refresh. Explicit full verification also checks tracked Git object identities through one batched index listing. Clean tracked files reuse a matching recorded Git object identity without per-file stats or reads. Dirty, staged, untracked, uncertain and non-Git files are content-hashed; matching content and extractor identities reuse existing rows, changed files are parsed once and replaced transactionally, and deleted files are removed. Concurrent callers coalesce one refresh, and composed structural operations refresh once before querying the current SQLite snapshot. Results expose `hashedFiles`, `parsed`, `rowsChanged`, and `reusedFiles` so callers can distinguish content work from a no-op parse.

### Check

```text
rke context check
```

Check refreshes the index and reports generated-index freshness separately from canonical-knowledge freshness. Registered knowledge is `fresh` only when every resolved source matches its receipt, `stale` when a receipt differs, and `unknown` when no receipt exists. An empty manifest cannot prove freshness.

### Impact

```text
rke context impact --changed <repository-relative-path> [--changed <path> ...]
```

Impact matches changed paths against explicit manifest source patterns and returns `affectedKnowledge`. It does not infer semantic bindings from generic lexical overlap; an unmatched change remains a documentation-review decision for the caller.

### Verify

```text
rke context verify --knowledge <repository-relative-path> --evidence <summary>
```

Verify resolves all current source patterns for the named document and stores their content hashes plus the canonical document's own hash with a timestamp and compact evidence summary. Invoke it only after reviewing the canonical document against those sources. A document or source change, deletion, or newly matched glob member makes the receipt stale.

### Benchmark

```text
rke context benchmark --corpus <repository-relative-json-path>
```

Corpus schema version 1 contains query records with `id`, `query`, and one or more `relevantPaths`. The result reports per-case ranked paths, recall at 1/5/10, reciprocal rank, and aggregate mean reciprocal rank. The corpus file itself is excluded from ranking to prevent answer leakage.

The repository also provides `npm run benchmark` for performance evidence. It creates a realistic clean tracked mixed Python, TypeScript and C# corpus and measures cold incremental indexing, hot-cache freshness, forced verified-warm freshness, one-file change, repeated retrieval, memory, measured Git process launches, and parser child-process launches. `RKE_BENCHMARK_FILES` controls scale; large runs are deliberately opt-in while deterministic tests execute a small freshness contract.

## Repository and data boundary

- The configured repository root is fixed for an invocation.
- Scopes and benchmark corpora must be repository-relative and cannot escape through traversal or symlinks.
- In Git repositories, index tracked files plus visible non-ignored untracked files. Outside Git, retrieval and dissection share a bounded filesystem walker that prunes Git metadata, workflow caches, dependencies, vendor output, archives and bytecode caches before descent. Skip and report paths that cannot be inspected because of an inaccessible link, reparse point, race, or filesystem error rather than failing the entire refresh.
- Exclude Git metadata, workflow caches, dependency caches, binary files, files over one megabyte, and credential surfaces such as `.env`, private keys, `.npmrc`, `.pypirc`, `.netrc`, Docker and Kubernetes configuration, and provider credential stores.
- Redact detected secret-like values before persistence or response. Report omitted and redacted paths plus finding kinds without returning the values.
- A local tool is not automatically secret-safe. Never assume arbitrary source text is safe to send to a model merely because its path passed eligibility checks.
- Store the versioned, disposable cache under `.engineering-workflow/cache/`; consumers should Git-ignore `.engineering-workflow/`.

## MCP adapter

`rke-mcp` is a machine-wide stdio adapter for both MCP protocol eras. It supports the stateless `2026-07-28` protocol through `server/discover`, required per-request protocol metadata, result discriminators, response identity, and cache hints. It retains the `2025-11-25` initialize handshake for legacy clients. It uses newline-delimited UTF-8 JSON-RPC, emits only protocol messages on stdout, bounds each input message to four MiB, and requires an explicit repository on each tool call. `--allow-root` constrains dynamic repositories and `--root` retains fixed-root compatibility.

It exposes every operation in the authoritative registry, including lifecycle, gates, journeys, tasks, closure, host integration, retrieval, structure, knowledge, documentation, dissection, continuity, coordination and publication. Both transports dispatch the same registered handlers and validation contract, including read-only and idempotence annotations. Successful calls return the same payload in `structuredContent` and JSON-encoded text content for backwards compatibility. Non-zero domain and validation outcomes preserve their structured payload and become tool errors; unknown tools and unknown protocol methods remain JSON-RPC errors. An unexpected request failure is isolated to that response so the server can process the next request.

## Knowledge binding manifest

Store durable bindings in the tracked `.rke/repo-context.json` manifest. Its normative schema is [repo-context-manifest.schema.json](./repo-context-manifest.schema.json). Read-only compatibility accepts the legacy `.polaralias/repo-context.json` only when no canonical manifest exists; writes migrate to `.rke`, and dual manifests are an explicit error.

```json
{
  "schemaVersion": 1,
  "knowledge": [
    {
      "path": "docs/architecture.md",
      "sources": ["src/**/*.py", "config/providers.toml"]
    }
  ]
}
```

Paths and patterns are repository-relative. `*` stays within one segment; `**` spans zero or more directories. Canonical documents must exist, entries must have unique paths, and source patterns cannot escape the repository. The engine preserves unknown manifest and entry fields that do not violate these invariants.

The optional `verified` object is engine-maintained receipt data. New receipts contain `verifiedAt`, the supplied evidence summary, and an ordered `sourceIdentities` list of `{path, sha256}` records. Keeping paths out of JSON property names prevents filenames such as `auth.py` from looking like credential assignments to generic secret scanners. RKE continues to read the legacy `sourceHashes` map during the pre-1.0 migration. Generated indexes remain ignored and disposable; bindings and receipts are tracked knowledge-maintenance evidence.

## Evidence limits

Retrieval rank means lexical relevance, not truth, authority, completeness, freshness of canonical knowledge, or permission to act. Verify consequential claims against the returned source and the current runtime where appropriate.

When deterministic evidence does not settle the question, the consuming model may issue narrower reformulations and semantically compare only the bounded returned passages and structural evidence. The core does not require a second embedding index, remote model call, or whole-repository model ingestion.

The context engine owns generated retrieval evidence and index freshness. It does not own workflow state, OKF Tasks execution truth, canonical knowledge, Git integration truth, or publication authority.

## Retrieval benchmark

The bundled corpus covers exact-symbol, natural-language feature, configuration, architecture, and terminology queries. The current lexical baseline is recall@1 `0.80`, recall@5 `1.00`, recall@10 `1.00`, and mean reciprocal rank `1.00`. Improvements must preserve or improve aggregate metrics while inspecting individual query classes for hidden regressions.
