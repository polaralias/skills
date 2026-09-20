# Repository Context Contract

## Purpose

The repository-context core reduces repeated exploration by returning compact, exact repository evidence through a deterministic local interface. Its contracts, implementation, schemas, prompts, tests, and dependencies are independently maintained within the RKE family.

Field-aware BM25F is the measurable lexical baseline. It independently weights paths, filenames, complete symbols, heading ancestry, and bodies instead of approximating fields through token repetition. Canonical knowledge and foundational or entry-point navigation roles receive bounded, explicitly labelled boosts after lexical scoring; these labels improve reader routing but do not prove truth or freshness. One-hop parser-backed call relationships and directly linked typed OKF concepts may add lower-scored, explicitly labelled evidence. Further expansion must demonstrate improvement against the checked-in corpus rather than replacing the baseline by assumption.

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
- score and debuggable match reasons;
- bounded source snippet;
- index revision and refresh counts.
- inaccessible Git-visible paths skipped during bounded scanning.

The persisted index contains field lengths, document frequencies, and per-term postings so ordinary queries do not rebuild corpus statistics. Exact identifier and heading matches receive labelled bounded boosts. Result selection first favours distinct files, then fills remaining capacity with additional passages, reducing repeated same-file chunks. Snippets are centred on a matched term when the stored passage exceeds the response bound.

Direct lexical results use `term-match`. A connected typed concept introduced through the OKF relationship graph uses `knowledge-relationship` plus `linked-from:<path>` and must not be interpreted as containing the query terms.
Parser-backed neighbours use `structural-neighbour` plus `structurally-linked-from:<path>::<symbol>`. Structural fusion is one-hop, bounded, and attempted only when code leads the results or an exact identifier is present. Native parsing is isolated in workers; one crashing grammar falls back or produces explicit partial-fusion warnings rather than terminating retrieval. Structural fusion is navigation evidence, not proof of runtime reachability.

Refresh is fingerprint-incremental. Demonstrably clean tracked files may reuse Git object identity and prior chunks only after one batched, filter-aware Git content check proves each eligible worktree blob still matches the index. Dirty, staged, untracked, uncertain and mismatched files are read and content-hashed by the indexer; modification time and size alone are never accepted as identity. The eligible-path set prevents redundant work over excluded trees and avoids repeated file and symlink checks after bounded enumeration. Deleted files are removed. Results expose `hashedFiles` and `reusedFiles` so callers can distinguish a content refresh from a no-op check.

### Check

```text
rke context check
```

Check refreshes the index and reports generated-index freshness separately from canonical-knowledge freshness. Registered knowledge is `fresh` only when every resolved source matches its receipt, `stale` when a receipt differs, and `unknown` when no receipt exists. An empty manifest cannot prove freshness.

### Impact

```text
rke context impact --changed <repository-relative-path> [--changed <path> ...]
```

Impact classifies each changed path into one evidence class:

- `boundImpacts`: an explicit source pattern connects the change to canonical knowledge; its receipt can report `fresh`, `stale`, or `unknown`;
- `candidateImpacts`: at least two non-generic terms from the changed file's name and immediate parent all occur in a registered canonical document, alongside meaningful lexical overlap; this conservative fallback means review-candidate, never stale;
- `unmappedChanges`: no explicit or meaningful lexical relationship was found.

Explicit bindings take precedence. One changed path is not also emitted as a candidate or unmapped change.
Weaker overlap remains unmapped so broad repository vocabulary does not flood assessment output.

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

The repository also provides `python scripts/benchmark_freshness.py` for performance evidence. Its default 1k, 10k and 50k tracked-file matrix measures cold indexing, a warm find, and a same-size one-file change with restored timestamps. The full matrix is deliberately opt-in; deterministic tests execute a small contract case that validates result shape and freshness behaviour.

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

The optional `verified` object is engine-maintained receipt data. It contains `verifiedAt`, the supplied evidence summary, and a `sourceHashes` map. Generated indexes remain ignored and disposable; bindings and receipts are tracked knowledge-maintenance evidence.

## Evidence limits

Retrieval rank means lexical relevance, not truth, authority, completeness, freshness of canonical knowledge, or permission to act. Verify consequential claims against the returned source and the current runtime where appropriate.

When deterministic evidence does not settle the question, the consuming model may issue narrower reformulations and semantically compare only the bounded returned passages and structural evidence. The core does not require a second embedding index, remote model call, or whole-repository model ingestion.

The context engine owns generated retrieval evidence and index freshness. It does not own workflow state, OKF Tasks execution truth, canonical knowledge, Git integration truth, or publication authority.

## Retrieval benchmark

The bundled corpus covers exact-symbol, natural-language feature, configuration, architecture, and terminology queries. The current lexical baseline is recall@1 `0.80`, recall@5 `1.00`, recall@10 `1.00`, and mean reciprocal rank `1.00`. Improvements must preserve or improve aggregate metrics while inspecting individual query classes for hidden regressions.
