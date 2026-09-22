---
type: Architecture Concept
title: Polaralias engineering workflow architecture
description: Explains how the Engineering Workflow skill coordinates the independently installed RKE runtime, documentation-driven development, Query-to-Knowledge, Repository Change Comprehension, OKF Tasks, and repository-local evidence.
timestamp: 2026-09-22T15:00:00+01:00
authority: canonical
verification: verified-working
reviewed_at: 2026-09-22T15:00:00+01:00
verified_against:
  - skills/engineering/engineering-workflow/SKILL.md
  - skills/engineering/engineering-workflow/RKE_SOURCE.json
  - skills/engineering/engineering-workflow/references/repo-context-contract.md
  - skills/engineering/engineering-workflow/references/extensions/query-to-knowledge.md
  - skills/engineering/engineering-workflow/references/documentation-lifecycle.md
  - "RKE 0.10.0: 36 deterministic TypeScript tests and 24 packaged grammar fixtures passed"
  - "RKE 0.10.0 npm artefact built, version-validated, no-Python audited, and clean-install smoked"
  - "50,000-file mixed corpus: 770.99 ms Git-verified warm refresh, zero hashes/parses, 546.7 MB peak RSS, zero parser child processes"
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

The `engineering-workflow` skill is the single normal agent entry point for material repository engineering. RKE is the independent installed runtime and repository-knowledge methodology used by that skill. OKF Tasks remains a separate execution-record primitive. The skill keeps one primary phase, activates bounded capabilities only when needed, and retains unresolved obligations as explicit gates rather than requiring an agent to remember a sequence of peer skills.

Documentation-driven development is the governing principle: accepted behaviour and durable repository knowledge guide implementation and are rechecked against source, tests, and runtime evidence. RKE operationalises that principle through retrieval, structural analysis, knowledge bindings, documentation impact, and closure evidence.

## Public lifecycle

The stable lifecycle is `activate`, `start`, `checkpoint`, `resume`, and `close`. `activate` is the single normal agent entrypoint: it creates missing state, validates active state, or opens a new cycle from closed state, then records the current Git HEAD and bounded dirty-path baseline. Understand, design, and close journeys selectively load the detailed judgement needed for their phase. Optional task, coordination, and publication capabilities register their own evidence gates. Scenario and test planning belong to design acceptance; tracker synchronization belongs to OKF Tasks.

Workflow state is compact restart information. It may point to stronger records but does not replace repository knowledge, OKF Tasks, Git evidence, runtime evidence, or a handoff.

Exploratory design uses convergence control. Its experiment contract records the hypothesis, governing assumption, expected observation, predefined falsifier, authoritative acceptance, and reset/kill condition. Observing the falsifier causes immediate design re-entry; otherwise the default reset threshold is two individually inconclusive, assumption-relevant acceptance failures. Incidental implementation faults do not count. Design re-entry cannot weaken acceptance to fit an implementation, and checkpoint/handoff continuity carries the minimum active convergence state across compaction or sessions.

Durable writers use atomic replacement, revision checks, and ownership-recording file locks. Each owner writes and synchronises a complete PID, creation-time, and random-token record under a unique candidate name, then atomically publishes it as the lock path. A paused live creator therefore never exposes a pre-metadata lock that another process can reclaim. A valid live owner is never evicted by age; a demonstrably dead owner is reclaimed immediately, while a malformed legacy or externally damaged record is reclaimed only after a short grace window. Lock identity rechecks and token-safe cleanup prevent a former owner from deleting a replacement lock. Filesystems without atomic hard-link publication return `lock_atomic_publish_unsupported` rather than receiving a weaker fallback. Later acquisition removes only complete candidate files whose recorded owner is demonstrably dead.

## Repository context

`context find` queries a disposable repository-local SQLite FTS5 database over eligible code and documentation. Paths, filenames, symbols, headings, and bodies are weighted without reconstructing a repository-wide JavaScript postings graph. A recursive watcher is only a bounded hot-cache invalidation hint: a short event-delivery barrier and periodic Git verification prevent watcher timing from becoming the correctness boundary. In Git repositories, two batched commands provide tracked index-object identities and dirty/staged/untracked classification. Clean tracked files reuse matching Git identity without per-file stats or reads; dirty, staged, untracked, uncertain, and non-Git files are content-hashed. Concurrent public operations coalesce one refresh, and composed structural operations query the same refreshed SQLite snapshot. The checked 1k/10k/50k mixed-language benchmark separates hot-cache and forced Git-verified warm paths, measures Git launches, and proves zero parser child processes.

Typed OKF concepts contribute their relative Markdown relationships to the index. A direct lexical match remains the ranking baseline; a directly connected concept may be returned as lower-scored `knowledge-relationship` evidence. One-hop parser-backed callers and callees may contribute labelled `structural-neighbour` evidence. Both expansions are navigation, not proof of truth, freshness, or complete runtime reachability. When deterministic evidence is insufficient, the consuming model may reformulate queries and compare bounded returned passages without requiring a second embedding index or whole-repository model ingestion.

## Structural context

The structural core shares the same SQLite files, symbols, imports, edges, and chunks with retrieval. One Node process loads WebAssembly Tree-sitter grammars in-process for TypeScript, Python, C#, and the rest of the packaged 24-language fixture set. Changed files are parsed once and replaced transactionally; unchanged files reuse their rows. Compact file APIs, bounded caller/callee traces, repository maps, changed-file impact, and exhaustive regex search all consume that current snapshot. `change impact` refreshes once before tracing up to its bounded symbol set, so composition cannot multiply whole-repository freshness work.

Structural results are navigation evidence, not completeness proof. Duplicate names, dynamic dispatch, reflection, generated code, and framework wiring may remain unresolved. When reliable parser evidence is unavailable, the CLI and MCP return a bounded agent-review packet with an explicit inference schema and uncertainty field rather than presenting pattern matches as parser facts. Validated findings are stored separately with their source digest, confidence, and uncertainties; they participate in navigation until the source changes and never override parser evidence. The checked-in benchmark measures recall, precision, and output size for maintained cases.

## Canonical knowledge

Canonical knowledge remains deliberately authored. The native knowledge core provides three deterministic operations:

- `knowledge check` validates typed concepts and their durable relationship graph;
- `knowledge build-indexes` generates marked progressive-disclosure navigation from titles and query-shaped descriptions;
- `knowledge register` records explicit source patterns for a concept in `.rke/repo-context.json`; the former `.polaralias/` path is bounded migration input only.

Registration does not establish freshness. After a human or agent reviews the concept against every resolved bound source, `context verify` records an ordered `{path, sha256}` identity list and compact evidence. Paths are values rather than JSON property names so generic secret scanners do not mistake names such as `auth.py` for credential assignments. Later source changes make that receipt stale; the legacy path-keyed hash map remains migration input only.

Generated indexes, retrieval caches, and model answers remain derived surfaces. They do not become canonical automatically.

## Event-driven documentation lifecycle

For an inherited or explicitly requested repository-documentation journey, `documentation bootstrap` first classifies the foundation as `no-rke`, `partial-rke`, or `mature-rke`. It returns existing truth surfaces, gaps, minimum recommendations, preserve/review sets, evidence requirements, likely reader questions, and `fresh`/`stale`/`unverified` binding sets without authoring prose or automatically superseding anything. Bootstrap hashes current eligible bound files and compares them with verification receipts without writing a context index. Receipt presence alone cannot produce a mature no-op: stale or unverified knowledge is `partial-rke` and requires targeted repair. EWF traces the real runtime, authors the minimum human-readable truth, registers bindings, and then uses apply and context verification to prove the result.

Documentation work is triggered by material Git events rather than every conversational turn. `documentation assess --base <ref>` classifies the current delta as no-op, explicitly bound update work, or a decision requiring agent judgement. It also discovers applicable root-to-nearest `AGENTS.md` rules and canonical entry points so repository instructions travel with the retrieval-to-generation journey. `change explain` records the RCC-compatible causal layer against the same fingerprint.

After an agent authors the minimum durable change, `documentation apply` validates the OKF graph, regenerates marked navigation, requires likely reader questions to retrieve affected canonical knowledge, records binding verification, and writes a local exact-delta completion receipt. Its transaction holds both the documentation lock and the canonical manifest lock, so a failed rollback cannot erase an ordinary manifest writer's concurrent update. It never generates canonical prose from a diff by itself.

`closure assess --base <ref>`, `close --base <ref>`, and the pre-push hook recompute the fingerprint. Material work blocks when either the causal explanation or documentation receipt is missing or stale. A closed workflow remains eligible for read-only reassessment, so completing the lifecycle does not make the subsequent pre-push gate fail. A no-op assessment avoids documentation ceremony.

## OKF Tasks boundary

OKF Tasks owns durable execution truth: outcomes, acceptance, status, workstreams, effort when enabled, evidence, and tracker reconciliation. The workflow adapter chooses `none`, `lightweight`, or `full` activation and delegates strict validation to the authoritative CLI. Task records may link to knowledge concepts, but neither surface is copied into workflow state or redefined by the other.

## Query-to-Knowledge and Repository Change Comprehension

Repository understanding and user-intent convergence are separate. The `understand` journey gathers and verifies repository evidence. Query-to-Knowledge is an explicit capability with a `shared-understanding` gate: it groups consequential questions, explains why each matters, recommends an answer with rationale, and repeats until no material implementation decision is being guessed. Durable decisions are promoted deliberately rather than turning every answer into documentation.

Repository Change Comprehension remains the named causal close-path workflow. `change explain` records how the final delta changes entry points, calls, state, effects, removals, and tests; it does not merely list changed files.

Deep repository dissection is an understand-journey mode backed by `dissection assess`, which inventories likely entry points, runtime and verification candidates, task/knowledge surfaces, producer boundaries, and trust gaps without claiming those candidates have executed. The design journey absorbs feature decomposition and test-plan behaviour through feature contracts, invariants, scenario/verification matrices, acceptance, dependencies, risks, and traceable work packages. Session alignment returns an ordered two-lane close assessment: provisional execution reconciliation, durable knowledge promotion, final execution reconciliation, validation, and optional continuation.

Rich continuity is distinct from compact workflow checkpoint state. `handoff write` creates one deterministic, secret-safe standard or max-depth artefact outside task and knowledge bundles. Local visibility strongly steers to ignored, untracked `local-docs/handoff/`; shared visibility deliberately uses commit-capable `.rke/handoffs/`. `handoff inspect` constrains or safely infers that visibility and returns the claims that must be re-verified. Parallel delivery uses `coordination validate/plan` for repository/container boundaries, path ownership, shared integration owners, dependencies, inherited authority, and non-executing worktree argv plans. Publication uses a redacted built-in scanner and an already-installed `gitleaks` binary when available.

## Shared CLI and MCP access

The separately installed `@polaralias/rke` npm package owns the CLI, MCP adapter, dependencies, caches, benchmarks, and runtime tests. The skills repository contains only the synchronized EWF catalogue package and a source/version manifest; it does not carry an independently maintained runtime copy.

The `rke` CLI and `rke-mcp` stdio adapter dispatch the complete same operation registry for lifecycle, retrieval, structural context, knowledge, documentation, explanation, dissection, handoff, coordination, host integration, and publication scanning. Schemas, argument validation, annotations, outcomes, exit semantics, and business handlers therefore have one implementation; each transport only translates its protocol envelope. One machine-wide MCP process accepts an explicit repository on every tool call, validates dynamic targets as Git repositories, and can restrict them with allowed-root boundaries. Repository-local state and evidence never become machine-global merely because the executable is shared. Fixed-root mode remains a compatibility option.

## Distribution and release integrity

RKE's `package.json` is the sole runtime version source and is checked against the requested `vX.Y.Z` release tag and built npm artefact. CI type-checks, tests, audits the no-Python invariant, validates the 41-operation/24-grammar release contract, packs the package, and exercises CLI retrieval, MCP discovery, and evaluator resources from a clean installation. The tag workflow attests and publishes the npm package with provenance before promoting the GitHub release.

## Legacy archive

The absorbed engineering packages are preserved unchanged under the repository-root `archive/` directory. That directory is outside catalogue generation, installation, BM25 retrieval, and structural analysis. Retained legacy names remain compatibility inputs to EWF routing, not separately invoked or maintained implementations. TPU and TPW are deliberately retired: OKF Tasks owns tracker synchronization and the design journey owns scenario/test planning. `repo-setup` remains active because bootstrap precedes the material engineering lifecycle.

## Host integration

`host recipe` describes machine-wide MCP activation, project routing, and repository-local Git-gate setup. `host install` writes a local Git `pre-push` hook; for Codex it merges a marker-owned activation block into project `AGENTS.md`, and for Claude it merges an `rke-mcp` entry. Independently authored instructions, hooks, and unrelated configuration are preserved.

Codex integration uses `codex mcp add rke -- rke-mcp` once at user scope. The project `AGENTS.md` block directs material changes through EWF and `rke activate`; repository selection belongs to each operation rather than the server installation. Git-only mode provides pre-push enforcement without claiming an MCP installation.

The packaged model-evaluation runner tests implicit activation, project-routed activation ordering, nearby non-activation, source-driven authority expansion, documentation bootstrap, and convergence decisions in isolated temporary repositories. It copies the exact packaged EWF source under evaluation, grades persisted phase and gates as well as activation order and authored evidence, and bounds timeout diagnostics.

On the focused 2026-09-22 Codex run, both packaged convergence cases passed. The first observed falsifier persisted `design` with `acceptance-defined` reopened. Two incidental failures persisted `deliver`, left the gate closed, kept acceptance unchanged, and requested a valid hypothesis-relevant observation. This proves only those dated host/model cases; future model behaviour remains evaluation evidence rather than a deterministic runtime guarantee.

## Reading order

- [Documentation map](documentation-map.md) — repository knowledge entry point and schema boundaries.
- [Complete Markdown inventory](documentation-inventory.md) — exhaustive classification of repository Markdown surfaces.
- [Repository visualization](repository-visualization.md) — derived visualisation contract.

# Citations

1. [MCP 2026-07-28 server discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx)
2. [MCP 2026-07-28 tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx)
