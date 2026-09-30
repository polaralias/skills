---
type: Architecture Concept
title: Polaralias engineering workflow architecture
description: Explains how the Engineering Workflow skill coordinates the independently installed RKE runtime, documentation-driven development, Query-to-Knowledge, Repository Change Comprehension, OKF Tasks, and repository-local evidence.
timestamp: 2026-09-27T18:12:08+01:00
authority: canonical
verification: verified-working
reviewed_at: 2026-09-30T08:27:00+01:00
verified_against:
  - skills/engineering/engineering-workflow/SKILL.md
  - skills/engineering/engineering-workflow/RKE_SOURCE.json
  - skills/engineering/engineering-workflow/references/repo-context-contract.md
  - skills/engineering/engineering-workflow/references/extensions/query-to-knowledge.md
  - skills/engineering/engineering-workflow/references/documentation-lifecycle.md
  - skills/engineering/engineering-workflow/references/instruction-preservation-audit.md
  - skills/engineering/engineering-workflow/references/continuity.md
  - skills/engineering/engineering-workflow/references/knowledge-methodology.md
  - skills/engineering/engineering-workflow/references/publication-review.md
  - skills/engineering/engineering-workflow/references/okf-tasks-adapter.md
  - "RKE 0.10.0: default and legacy parity suites, 24 packaged grammar fixtures, and a read-only RCC routing agent case passed locally on 2026-09-30"
  - "Skills catalogue: 33 skill descriptions, 98 routing scenarios, package, version, and EWF mirror parity checks passed locally on 2026-09-30"
  - "RKE 0.10.0 npm artefact built, version-validated, no-Python audited, and clean-install smoked"
  - "Real RKE snapshot: 130 tracked files, about 3.7 s cold index, 0.24 s warm query, 0.84 s one-file refresh, 66 MB parent peak and 397 MB largest parser child observed"
  - "focused convergence evaluation: 2/2 packaged Codex cases passed with persisted phase and gate assertions"
owner: polaralias
tags:
  - engineering-workflow
  - repository-context
  - okf
  - mcp
navigation:
  role: foundational
  order: 10
---

# Polaralias engineering workflow architecture

The `engineering-workflow` skill is the single normal agent entry point for material repository engineering and read-only explanations of repository code, implementation behaviour, or diffs. Code explanations use RCC prose without RKE state; simple document wording questions remain outside EWF. It contains the engineering methodology and remains usable without RKE. RKE is the independently installed repository memory, retrieval, freshness, and deterministic safety toolbelt used when available. OKF Tasks remains a separate execution-record primitive. EWF owns phase and capability judgement; optional RKE state can persist long-running work and unresolved gates.

Documentation-driven development is the governing principle: accepted behaviour and durable repository knowledge guide implementation and are rechecked against source, tests, and runtime evidence. RKE operationalises that principle through retrieval, structural analysis, knowledge bindings, documentation impact, and closure evidence.

## Public lifecycle

The prose lifecycle is understand, design, deliver, and close. EWF directly routes to the relevant journey and extension references. When durable continuity is useful, RKE provides `activate`, `start`, `checkpoint`, `resume`, and `close`: activation records Git HEAD and a bounded dirty-path baseline, while journey and capability operations persist selected phase and gates. RKE is not required to access the references or do ordinary material engineering. Scenario planning belongs to design acceptance; standalone human QA-plan writing remains outside EWF. Tracker publication uses OKF Tasks for durable execution by default and can map stable non-OKF work packages without creating task records.

Workflow state is compact restart information. It may point to stronger records but does not replace repository knowledge, OKF Tasks, Git evidence, runtime evidence, or a handoff. Activation, checkpoint, task checks, and closure validate status, continuity, task fields, timestamps, and receipts before using saved state.

Exploratory design uses convergence control. Its experiment contract records the hypothesis, governing assumption, expected observation, predefined falsifier, authoritative acceptance, and reset/kill condition. Observing the falsifier causes immediate design re-entry; otherwise the default reset threshold is two individually inconclusive, assumption-relevant acceptance failures. Incidental implementation faults do not count. Design re-entry cannot weaken acceptance to fit an implementation, and checkpoint/handoff continuity carries the minimum active convergence state across compaction or sessions.

Durable writers use atomic replacement, revision checks, and ownership-recording file locks. Each owner writes and synchronises a complete PID, creation-time, and random-token record under a unique candidate name, then atomically publishes it as the lock path. A paused live creator therefore never exposes a pre-metadata lock that another process can reclaim. A valid live owner is never evicted by age; a demonstrably dead owner is reclaimed immediately, while a malformed legacy or externally damaged record is reclaimed only after a short grace window. Lock identity rechecks and token-safe cleanup prevent a former owner from deleting a replacement lock. Filesystems without atomic hard-link publication return `lock_atomic_publish_unsupported` rather than receiving a weaker fallback. Later acquisition removes only complete candidate files whose recorded owner is demonstrably dead.

## Repository context

`context find` queries a disposable repository-local SQLite FTS5 database over eligible code and documentation. Parser symbol chunks are supplemented by full-file text windows so module-level wiring remains searchable. Paths, filenames, symbols, headings, and bodies are weighted without reconstructing a repository-wide JavaScript postings graph. A recursive watcher is only a bounded hot-cache invalidation hint: a short event-delivery barrier and periodic Git verification prevent watcher timing from becoming the correctness boundary. In Git repositories, batched commands provide tracked index-object identities and dirty/staged/untracked classification. Clean tracked files reuse matching Git identity without per-file stats or reads; dirty, staged, untracked, uncertain, and non-Git files are content-hashed. Concurrent public operations coalesce one refresh, and composed structural operations query the same refreshed SQLite snapshot. Synthetic benchmarks retain the incremental baseline; disposable snapshots of real RKE, Python and skills repositories show retrieval rank, refresh cost and parser memory limits.

Typed OKF concepts contribute their relative Markdown relationships to the index. Direct lexical matches remain the ranking baseline; bounded relationship slots keep directly connected concepts visible even when lexical matches fill the requested limit. Expanded concepts carry `knowledge-relationship` evidence and source provenance. One-hop parser-backed callers and callees may contribute labelled `structural-neighbour` evidence. Both expansions are navigation, not proof of truth, freshness, or complete runtime reachability. When deterministic evidence is insufficient, the consuming model may reformulate queries and compare bounded returned passages without requiring a second embedding index or whole-repository model ingestion.

## Structural context

The structural core shares the same SQLite files, symbols, imports, edges, and chunks with retrieval. Repositories with at most three detected grammars parse in-process; broader mixes use short-lived language-specific child processes because loading many Tree-sitter WASM grammars together caused multi-gigabyte memory use. Changed files are parsed once and replaced transactionally; unchanged files reuse their rows. The generic extractor provides definitions, lexical imports and name-only calls. Unique same-file and Go same-package targets and relative static imports in TypeScript, JavaScript and Python can resolve to indexed symbols; namespace imports also resolve in reverse caller lookup. Default imports remain unresolved because name-only calls do not establish their exported target. Compact file APIs, bounded caller/callee traces, repository maps, changed-file impact, and exhaustive regex search all consume that current snapshot. Trace and impact query indexed edge candidates at each frontier and cap parser trace evidence at 500 edges. `change impact` refreshes once before tracing up to its bounded symbol set, so composition cannot multiply whole-repository freshness work.

Structural results are navigation evidence, not completeness proof. Duplicate names, dynamic dispatch, reflection, generated code, and framework wiring may remain unresolved. When reliable parser evidence is unavailable, the CLI and MCP return a bounded agent-review packet with an explicit inference schema and uncertainty field rather than presenting pattern matches as parser facts. Validated findings are stored separately with their source digest, confidence, and uncertainties; they may augment partial parser relationships until the source changes, while extracted parser symbols take precedence. The checked-in benchmark measures recall, precision, and output size for maintained cases.

## Canonical knowledge

Canonical knowledge remains deliberately authored. The native knowledge core provides three deterministic operations:

- `knowledge check` validates typed concepts and their durable relationship graph;
- `knowledge build-indexes` generates marked progressive-disclosure navigation from titles and query-shaped descriptions;
- `knowledge register` records explicit source patterns for a concept in `.rke/repo-context.json`; the former `.polaralias/` path is bounded migration input only.

Registration does not establish freshness. After a human or agent reviews the concept against every resolved bound source, `context verify` records an ordered `{path, sha256}` identity list and compact evidence. Paths are values rather than JSON property names so generic secret scanners do not mistake names such as `auth.py` for credential assignments. Later source changes make that receipt stale; the legacy path-keyed hash map remains migration input only. RKE can also assess a few selected claim-sized bindings in a tracked `.rke/claim-bindings.json`; their `current` status means reviewed bytes still match, while tests and behavioral truth remain separate evidence.

The manifest reader rejects unsupported schema versions, malformed or duplicate bindings, and invalid verification receipts before a writer can change the file. Manifest and workflow writers validate their mutated objects before atomic write; the shared operation boundary rejects blank evidence and checkpoint text. All manifest targets pass repository containment checks, including symlink parents. A legacy manifest migrates on the next write only when no canonical manifest exists; bootstrap and closure use the same effective presence check. Registration requires an existing typed concept. Durable graph checks reject disconnected components while excluding transient concepts, and missing title or description remains a warning. Index generation writes relative navigation in the bundle root and nested concept directories. Linked typed concepts are recorded in the disposable SQLite index and can expand a direct lexical result with source provenance.

Generated indexes, retrieval caches, and model answers remain derived surfaces. They do not become canonical automatically.

## Event-driven documentation lifecycle

For an inherited or explicitly requested repository-documentation journey, `documentation bootstrap` classifies the repository as `no-rke`, `partial-rke`, or `mature-rke`. It returns existing truth surfaces, gaps, preserve/review sets, and `fresh`/`stale`/`unverified` binding sets without authoring prose or recommending a fixed foundation filename. Bootstrap hashes current eligible bound files and compares them with verification receipts without writing a context index. Receipt presence alone cannot produce a mature no-op: stale or unverified knowledge is `partial-rke` and requires targeted repair. EWF chooses the appropriate foundation from repository evidence, authors the minimum human-readable truth, registers bindings, and then uses apply and context verification to prove the result.

Documentation work is triggered by material Git events rather than every conversational turn. `documentation assess --base <ref>` classifies the current delta as no-op, explicitly bound update work, or a decision requiring agent judgement. It also discovers applicable root-to-nearest `AGENTS.md` rules and canonical entry points so repository instructions travel with the retrieval-to-generation journey. RCC comprehension remains EWF prose: the agent inspects the bounded change, callers, and tests, then explains the causal before and after to the user.

After an agent authors the minimum durable change, `documentation apply` validates the OKF graph, regenerates marked navigation, requires likely reader questions to retrieve affected canonical knowledge, records binding verification, and writes a local exact-delta completion receipt. Its transaction snapshots the manifest, legacy manifest, receipt and every generated index path, then restores prior content or removes newly created indexes after a later failure. It never generates canonical prose from a diff by itself.

When RKE workflow state is active, `closure assess --base <ref>` and `close --base <ref>` recheck the documentation receipt, knowledge, task and validation lanes. RCC prose has no machine explanation receipt. A no-op assessment avoids documentation ceremony. The optional local pre-push integration enforces applicable deterministic checks; EWF can still close an ordinary engineering task without workflow state.

## OKF Tasks boundary

OKF Tasks owns durable execution truth: outcomes, acceptance, status, workstreams, effort when enabled, evidence, and tracker reconciliation. The workflow adapter chooses `none`, `lightweight`, or `full` activation and delegates strict validation to the authoritative CLI. Task records may link to knowledge concepts, but neither surface is copied into workflow state or redefined by the other.

## Query-to-Knowledge and Repository Change Comprehension

Repository understanding and user-intent convergence are separate. The `understand` journey gathers and verifies repository evidence. Query-to-Knowledge is an explicit capability with a `shared-understanding` gate: it groups consequential questions, explains why each matters, recommends an answer with rationale, and repeats until no material implementation decision is being guessed. Durable decisions are promoted deliberately rather than turning every answer into documentation.

Repository Change Comprehension remains the named causal close-path workflow in EWF prose. The agent gives the user a code-level before and after account, traces state and failure changes, classifies evidence, and labels unverified runtime claims. An optional ignored Markdown note can preserve the account across a long session.

Deep repository dissection is an understand-journey mode backed by `dissection assess`, which inventories likely entry points, runtime and verification candidates, task/knowledge surfaces, producer boundaries, and trust gaps without claiming those candidates have executed. The design journey absorbs feature decomposition and test-plan behaviour through feature contracts, invariants, scenario/verification matrices, acceptance, dependencies, risks, and traceable work packages. Session alignment returns an ordered two-lane close assessment: provisional execution reconciliation, durable knowledge promotion, final execution reconciliation, validation, and optional continuation.

Rich continuity is distinct from compact workflow checkpoint state. `handoff write` creates one deterministic, secret-safe standard or max-depth artefact outside task and knowledge bundles, superseding older active records for the same stream. Local visibility requires ignored, untracked `local-docs/handoff/`; shared visibility requires a commit-capable destination and tracking before pickup. `handoff inspect` checks visibility, expiry, branch, and HEAD drift before returning claims for re-verification. Parallel delivery validates an explicit base, sibling container, unique branches, path ownership, and acyclic dependencies, returning non-executing worktree argv plans. Shared integration ownership, inherited authority, and exact-tip cleanup still need agent review. Publication uses a redacted built-in scanner and an already-installed `gitleaks` binary for working-tree and history scans.

The instruction-preservation audit classifies every absorbed legacy package by editorial judgement retained in EWF Markdown, deterministic behaviour owned by commands, and superseded material or independent owners. Continuity now documents a host-conditional compaction pattern and selective max-handoff depth. Knowledge methodology retains glossary, decision lifecycle, provenance, reading-order and streamline judgement without making optional conventions validator rules. Publication review retains the public-readiness sweep and release-profile questions, while repo-setup owns starter automation. The OKF Tasks adapter retains task-lifecycle judgement but defers record schemas, tracker profiles and provider bindings to the current OKF Tasks specification and CLI.

## Shared CLI and MCP access

The separately installed `@polaralias/rke` npm package owns the CLI, MCP adapter, dependencies, caches, benchmarks, and runtime tests. The skills repository contains only the synchronized EWF catalogue package and a source/version manifest; it does not carry an independently maintained runtime copy. The manifest's source commit records the pre-recreation snapshot of [polaralias/rke](https://github.com/polaralias/rke). RKE is being restarted with current functionality at `0.1.0` from a fresh Git root, so that source commit will not be an ancestor of the new repository history.

The `rke` CLI and `rke-mcp` stdio adapter dispatch the same 43-operation registry for optional continuity, retrieval, structural context, knowledge, documentation evidence, dissection, handoff, coordination, host integration, and publication scanning. Schemas, argument validation, annotations, outcomes, exit semantics, and business handlers therefore have one implementation; each transport only translates its protocol envelope. One machine-wide MCP process accepts an explicit repository on every tool call, validates dynamic targets as Git repositories, and can restrict them with allowed-root boundaries. Repository-local state and evidence never become machine-global merely because the executable is shared. Fixed-root mode remains a compatibility option.

## Distribution and release integrity

RKE's `package.json` is the sole runtime version source and is checked against the requested `vX.Y.Z` release tag and built npm artefact. CI type-checks, runs the default and executable legacy-parity suites, audits the no-Python invariant, validates the 43-operation/24-grammar release contract, packs the package, and exercises every npm bin shim from a clean installation. The tag workflow verifies that the tag commit is on main, then attests the npm package. Publication compares the tested tarball's SHA-512 integrity with any existing exact npm version, so a matching retry can finish GitHub Release promotion; mismatched bytes or registry failure block. New versions publish with provenance.

## Legacy archive

The absorbed engineering packages are preserved unchanged under the repository-root `archive/` directory. That directory is outside catalogue generation, installation, BM25 retrieval, and structural analysis. Retained legacy names remain compatibility inputs to EWF routing, not separately invoked or maintained implementations. TPU routes to the bounded tracker-publication adapter: OKF Tasks owns durable execution and its Tracker Profiles, while stable non-OKF work packages can be previewed or published through a separately authorised connector. TPW remains outside EWF as standalone human QA-plan writing. `repo-setup` remains active because bootstrap precedes the material engineering lifecycle.

## Host integration

`host recipe` describes machine-wide MCP activation, project routing, and repository-local Git-gate setup. `host install` writes a local Git `pre-push` hook; for Codex it merges a marker-owned EWF routing block into project `AGENTS.md`, and for Claude it merges that block into `CLAUDE.md` and an `rke` server entry into `.mcp.json`. The block directs applicable use of RKE's deterministic commands while allowing ordinary engineering when RKE is unavailable. The installer checks routing markers and MCP ownership before writing and accepts its own existing entry on repeat installation. Independently authored instructions, hooks, and unrelated configuration are preserved.

Codex integration uses `codex mcp add rke -- rke-mcp` once at user scope. The project `AGENTS.md` block directs material changes through EWF; `rke activate` is used when persistent state helps. Repository selection belongs to each operation rather than the server installation. Git-only mode provides optional pre-push checks without claiming an MCP installation.

The packaged model-evaluation runner tests EWF routing, source-driven authority expansion, documentation bootstrap, convergence decisions, read-only RCC routing without workflow state, RCC prose without a change-explanation command, ordinary engineering without RKE, evidence-based foundation choice, and optional continuity state in isolated temporary repositories. It copies the exact packaged EWF source under evaluation and grades authored evidence and state when applicable.

On the focused 2026-09-22 Codex run, both packaged convergence cases passed. The first observed falsifier persisted `design` with `acceptance-defined` reopened. Two incidental failures persisted `deliver`, left the gate closed, kept acceptance unchanged, and requested a valid hypothesis-relevant observation. This proves only those dated host/model cases; future model behaviour remains evaluation evidence rather than a deterministic runtime guarantee.

The 2026-09-24 to 2026-09-27 parity qualification used a staged TypeScript RKE installation because the machine's legacy Python shim was broken. Earlier material activation attempts timed out after edits and tests; the small-change route briefly addressed that overhead. The 2026-09-30 boundary pass removed that route and the explanation receipt. Focused agent cases passed for RCC prose without the command, material engineering without RKE, foundation choice from repository evidence, and optional state for a long workflow. A scoped loopback provider previously validated OKF Tasks create/sync/readback and a conflict refusal; no live tracker write was authorised. These dated runs are not blanket future model guarantees.

## Reading order

- [Documentation map](documentation-map.md) — repository knowledge entry point and schema boundaries.
- [Complete Markdown inventory](documentation-inventory.md) — exhaustive classification of repository Markdown surfaces.
- [Repository visualization](repository-visualization.md) — derived visualisation contract.

# Citations

1. [MCP 2026-07-28 server discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx)
2. [MCP 2026-07-28 tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx)
