---
type: Architecture Concept
title: Polaralias engineering workflow architecture
description: Explains how the Engineering Workflow skill coordinates the independently installed RKE runtime, documentation-driven development, Query-to-Knowledge, Repository Change Comprehension, OKF Tasks, and repository-local evidence.
timestamp: 2026-09-19T09:20:00+01:00
authority: canonical
verification: verified-working
verified_at: 2026-09-19T09:20:00+01:00
verified_against:
  - skills/engineering/engineering-workflow/SKILL.md
  - skills/engineering/engineering-workflow/RKE_SOURCE.json
  - skills/engineering/engineering-workflow/references/repo-context-contract.md
  - skills/engineering/engineering-workflow/references/extensions/query-to-knowledge.md
  - skills/engineering/engineering-workflow/references/documentation-lifecycle.md
  - "RKE runtime 0.4.0: 145 deterministic tests passed; Ruff and Pyright passed"
  - "RKE 0.4.0 wheel and sdist built, version-validated, and clean-install smoked independently"
  - "retrieval benchmark: recall@1 0.8, recall@5 1.0, MRR 1.0"
  - "structural benchmark: mean recall 1.0 and mean precision 1.0 across 14 contract cases, 10083 output characters"
  - "model invocation evaluation: installed project routing produced activation evidence before requested edits; nested runner still timed out before final response"
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

Durable writers use atomic replacement, revision checks, and ownership-recording file locks. Locks record a PID, creation time, and random owner token; a demonstrably dead or sufficiently stale owner can be reclaimed after the lock identity is rechecked, while token-safe cleanup prevents a former owner from deleting a replacement lock.

## Repository context

`context find` builds a disposable repository-local BM25F index over eligible code and documentation. Paths, filenames, symbols, heading ancestry, and bodies are scored as separate fields, with corpus statistics and postings persisted for reuse. Tree-sitter symbol spans define code chunks across supported languages; oversized Markdown sections become bounded overlapping passages. Clean tracked files reuse Git object identity only after a batched, filter-aware Git content check confirms that the eligible worktree blob still matches the index, so same-size restored-timestamp edits cannot hide behind platform stat caching. Dirty, staged, untracked, uncertain, and mismatched files are content-hashed by the indexer. Results favour distinct files before repeated passages and contain exact paths, line spans, headings or symbols, match-centred snippets, scores, and reasons. Inaccessible Git-visible paths are skipped and reported rather than failing the complete refresh.

Typed OKF concepts contribute their relative Markdown relationships to the index. A direct lexical match remains the ranking baseline; a directly connected concept may be returned as lower-scored `knowledge-relationship` evidence. One-hop parser-backed callers and callees may contribute labelled `structural-neighbour` evidence. Both expansions are navigation, not proof of truth, freshness, or complete runtime reachability. When deterministic evidence is insufficient, the consuming model may reformulate queries and compare bounded returned passages without requiring a second embedding index or whole-repository model ingestion.

## Structural context

The structural core complements BM25F with syntax-aware source inspection: compact file API surfaces, bounded incoming and outgoing call traces, source-cluster and dependency-hub orientation, changed-file caller impact, and regex matches grouped by enclosing symbol and coupling. It selects package and source scopes automatically, persists graph shards, and widens progressively instead of imposing an arbitrary repository file cap. Explicit scopes remain available when the user or repository evidence provides a better boundary. A registry-driven Tree-sitter language pack provides broad grammar coverage, while language adapters supplement definitions, imports, and conservative resolution for representative Python, JavaScript, Rust, Go, .NET, JVM, native, scripting, PHP, and Swift surfaces. Retrieval consumes the same parser-backed symbol spans rather than maintaining another language-specific parser. Batched parsing falls back per file after a worker failure, and regex search is isolated behind a timeout. Content hashes reuse unchanged parse results.

Structural results are navigation evidence, not completeness proof. Duplicate names, dynamic dispatch, reflection, generated code, and framework wiring may remain unresolved. When reliable parser evidence is unavailable, the CLI and MCP return a bounded agent-review packet with an explicit inference schema and uncertainty field rather than presenting pattern matches as parser facts. Validated findings are stored separately with their source digest, confidence, and uncertainties; they participate in navigation until the source changes and never override parser evidence. The checked-in benchmark measures recall, precision, and output size for maintained cases.

## Canonical knowledge

Canonical knowledge remains deliberately authored. The native knowledge core provides three deterministic operations:

- `knowledge check` validates typed concepts and their durable relationship graph;
- `knowledge build-indexes` generates marked progressive-disclosure navigation from titles and query-shaped descriptions;
- `knowledge register` records explicit source patterns for a concept in `.rke/repo-context.json`; the former `.polaralias/` path is bounded migration input only.

Registration does not establish freshness. After a human or agent reviews the concept against every resolved bound source, `context verify` records source hashes and compact evidence. Later source changes make that receipt stale.

Generated indexes, retrieval caches, and model answers remain derived surfaces. They do not become canonical automatically.

## Event-driven documentation lifecycle

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

The separately installed `polaralias-rke` package owns the CLI, MCP adapter, dependencies, caches, benchmarks, and runtime tests. The skills repository contains only the synchronized EWF catalogue package and a source/version manifest; it does not carry an independently maintained runtime copy.

The `rke` CLI and `rke-mcp` stdio adapter dispatch the complete same operation registry for lifecycle, retrieval, structural context, knowledge, documentation, explanation, dissection, handoff, coordination, host integration, and publication scanning. Schemas, argument validation, annotations, outcomes, exit semantics, and business handlers therefore have one implementation; each transport only translates its protocol envelope. One machine-wide MCP process accepts an explicit repository on every tool call, validates dynamic targets as Git repositories, and can restrict them with allowed-root boundaries. Repository-local state and evidence never become machine-global merely because the executable is shared. Fixed-root mode remains a compatibility option.

## Distribution and release integrity

RKE's package version has one source and is checked against the requested `vX.Y.Z` release tag and both built artifacts. CI builds the wheel and source distribution, then installs and exercises each independently in a clean environment, including the CLI, MCP initialization, hooks, and packaged evaluation resources. The tag workflow attests the artifacts and publishes them to PyPI through trusted publishing before it promotes an existing draft or creates the public GitHub release. A PyPI failure therefore cannot present an incomplete version as the latest public GitHub release.

## Legacy archive

The absorbed engineering packages are preserved unchanged under the repository-root `archive/` directory. That directory is outside catalogue generation, installation, BM25 retrieval, and structural analysis. Retained legacy names remain compatibility inputs to EWF routing, not separately invoked or maintained implementations. TPU and TPW are deliberately retired: OKF Tasks owns tracker synchronization and the design journey owns scenario/test planning. `repo-setup` remains active because bootstrap precedes the material engineering lifecycle.

## Host integration

`host recipe` describes machine-wide MCP activation, project routing, and repository-local Git-gate setup. `host install` writes a local Git `pre-push` hook; for Codex it merges a marker-owned activation block into project `AGENTS.md`, and for Claude it merges an `rke-mcp` entry. Independently authored instructions, hooks, and unrelated configuration are preserved.

Codex integration uses `codex mcp add rke -- rke-mcp` once at user scope. The project `AGENTS.md` block directs material changes through EWF and `rke activate`; repository selection belongs to each operation rather than the server installation. Git-only mode provides pre-push enforcement without claiming an MCP installation.

The packaged model-evaluation runner tests implicit activation, project-routed activation ordering, nearby non-activation, and source-driven authority expansion in temporary repositories. It grades the activation receipt rather than mere state-file existence and checks that named implementation files were clean in the activation Git baseline. Windows fixtures seed an evaluator-owned unactivated state file so sandbox ACLs cannot hide evidence from the parent grader, and timeout diagnostics are bounded.

On the latest 2026-09-18 project-routed run, EWF activated before either requested implementation file became dirty and the agent completed both requested edits. The nested Codex process still timed out before emitting its final response. Project-routed CLI invocation is therefore evidenced; catalogue-only discovery and timely end-to-end completion remain separate measured residuals rather than completed claims.

## Reading order

- [Documentation map](documentation-map.md) — repository knowledge entry point and schema boundaries.
- [Complete Markdown inventory](documentation-inventory.md) — exhaustive classification of repository Markdown surfaces.
- [Repository visualization](repository-visualization.md) — derived visualisation contract.

# Citations

1. [MCP 2026-07-28 server discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx)
2. [MCP 2026-07-28 tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx)
