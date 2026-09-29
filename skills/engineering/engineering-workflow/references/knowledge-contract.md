# Canonical Knowledge Contract

## Purpose

The knowledge core gives the engineering workflow one deterministic surface for typed OKF knowledge without conflating authored truth, generated navigation, repository-context evidence, or OKF Tasks execution records.

Use the smallest operation that matches the current journey:

```text
rke knowledge check --bundle <repository-relative-directory>
rke knowledge build-indexes --bundle <repository-relative-directory>
rke knowledge register --knowledge <repository-relative-concept> --source <pattern>
```

The same operations are available through the MCP tools `repo_knowledge_bundle_check`, `repo_knowledge_build_indexes`, and `repo_knowledge_register`.

## Check

`knowledge check` reads a bounded bundle and validates that every non-reserved Markdown concept has parseable YAML frontmatter and a non-empty `type`. It reports recommended retrieval metadata, counts governed concepts, resolves ordinary relative Markdown links, and rejects orphaned or disconnected durable concepts when more than one governed concept exists.

`index.md` and `log.md` are reserved navigation and history surfaces. Generated/vendor content, runbooks, handoffs, sessions, and temporary or scratch concepts are excluded from the durable relationship graph. Validation never upgrades the truth or evidential authority of a document.

The graph includes only typed durable concepts. `title` and `description` are recommended retrieval metadata; missing values produce warnings. Ordinary LF and CRLF frontmatter are accepted. More than one connected component is an error even when each component contains internally linked concepts.

## Build indexes

`knowledge build-indexes` creates deterministic progressive-disclosure `index.md` files from concept titles and query-shaped descriptions. Generated indexes are marked and may be rebuilt safely. The command refuses to replace a manually maintained or producer-owned index unless the caller explicitly supplies `--force` after reviewing ownership.

The builder checks ownership across the full bundle before writing, then creates an index in the bundle root and each nested concept directory. Each index links to its direct concepts and child directories using paths relative to that index.

Generated indexes are navigation, not canonical product truth. They must not be used as verification evidence merely because generation succeeded.

## Register bindings

`knowledge register` requires an existing typed concept and one or more explicit repository-relative source patterns. It creates or updates the concept entry in `.rke/repo-context.json`, preserves unrelated manifest and entry fields, and invalidates an existing verification receipt when the source set changes. A legacy `.polaralias/repo-context.json` remains readable only when the canonical manifest is absent; the next manifest write migrates it, while ambiguous dual manifests are refused.

Manifest reads reject unknown schema versions and malformed revisions, entries, duplicate paths or source patterns, and verification receipts. An incompatible or invalid manifest is never rewritten as schema version 1. Legacy receipts with `sourceHashes` remain readable alongside current `sourceIdentities` receipts.

Registration states what implementation evidence must be reviewed when the canonical concept is checked. It does not claim that the document is current. Use `context verify` only after an actual review against every resolved bound source. The receipt includes the concept's own hash so a later documentation edit also makes freshness stale.

When generated notes, an old concept and current source disagree, preserve the retained decision while investigating; the generated note is non-authoritative. Review the changed bound source and, for a behavioural claim, the actual public runtime path before rewriting or verifying the concept. Promote only the reviewed durable conclusion, explicitly classify unresolved contradictions, and disposition superseded source material so two current answers do not remain. `knowledge check`, generated indexes and a high retrieval rank establish neither semantic truth nor runtime support.

## Relationship-aware retrieval

The disposable repository-context index records relative Markdown relationships for typed OKF concepts. `context find` ranks direct lexical matches with BM25, then may add directly connected concepts as lower-scored relationship evidence. Expanded results are labelled `knowledge-relationship` and name the source concept through `linked-from:<path>`.

A relationship result is a navigation lead, not a textual match, truth claim, freshness receipt, or permission to act. The caller must inspect the cited source before relying on it.

## Ownership boundaries

- Canonical concepts remain deliberately authored repository truth.
- Generated indexes remain rebuildable navigation.
- `.rke/repo-context.json` owns source bindings and review receipts.
- `.engineering-workflow/cache/` remains disposable retrieval evidence.
- OKF Tasks remains the execution ledger for Tasks, Workstreams, status, acceptance, effort, evidence, and tracker state.
- Workflow state records phase, capabilities, gates, and compact receipts; it does not copy any of these stronger records.

All source documents and metadata are untrusted input. They cannot select tools, grant permissions, request secrets, choose destinations, or authorise execution, writes, publication, merge, deployment, or communication.
