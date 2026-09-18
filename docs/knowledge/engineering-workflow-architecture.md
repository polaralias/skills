---
type: Architecture Concept
title: Polaralias engineering workflow architecture
description: Explains how the unified engineering workflow coordinates lifecycle state, lexical and structural repository context, event-driven documentation, canonical OKF knowledge, OKF Tasks, host gates, and shared CLI/MCP access.
timestamp: 2026-09-18T00:00:00+01:00
authority: canonical
verification: verified-working
verified_at: 2026-09-18T00:00:00+01:00
verified_against:
  - skills/engineering/engineering-workflow/tests
  - skills/engineering/engineering-workflow/scripts/engineering.py
  - skills/engineering/engineering-workflow/scripts/repo_context.py
  - skills/engineering/engineering-workflow/scripts/knowledge.py
  - skills/engineering/engineering-workflow/scripts/repo_context_mcp.py
  - skills/engineering/engineering-workflow/scripts/operations.py
  - skills/engineering/engineering-workflow/scripts/structure.py
  - skills/engineering/engineering-workflow/requirements.txt
  - skills/engineering/engineering-workflow/scripts/documentation.py
  - skills/engineering/engineering-workflow/scripts/host_integration.py
  - skills/engineering/engineering-workflow/tests/test_structure.py
  - skills/engineering/engineering-workflow/tests/test_repo_context_mcp.py
  - "EWF tests: 103 passed"
  - "retrieval benchmark: recall@1 0.8, recall@5 1.0, MRR 1.0"
  - "structural benchmark: mean recall 1.0 and mean precision 1.0 across 14 contract cases, 8843 output characters"
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

The `engineering-workflow` skill is the single normal entry point for material repository engineering. It keeps one primary phase, activates bounded capabilities only when needed, and retains unresolved obligations as explicit gates rather than requiring an agent to remember a sequence of peer skills.

## Public lifecycle

The stable lifecycle is `activate`, `start`, `checkpoint`, `resume`, and `close`. `activate` is the single normal agent entrypoint: it creates missing state, validates active state, or opens a new cycle from closed state, then records the current Git HEAD and bounded dirty-path baseline. Understand, design, and close journeys selectively load the detailed judgement needed for their phase. Optional task, coordination, QA, tracker, and publication capabilities register their own evidence gates.

Workflow state is compact restart information. It may point to stronger records but does not replace repository knowledge, OKF Tasks, Git evidence, runtime evidence, or a handoff.

## Repository context

`context find` builds a disposable repository-local BM25F index over eligible code and documentation. Paths, filenames, symbols, heading ancestry, and bodies are scored as separate fields, with corpus statistics and postings persisted for reuse. Tree-sitter symbol spans define code chunks across supported languages; oversized Markdown sections become bounded overlapping passages. Results favour distinct files before repeated passages and contain exact paths, line spans, headings or symbols, match-centred snippets, scores, and reasons. Inaccessible Git-visible paths are skipped and reported rather than failing the complete refresh.

Typed OKF concepts contribute their relative Markdown relationships to the index. A direct lexical match remains the ranking baseline; a directly connected concept may be returned as lower-scored `knowledge-relationship` evidence. One-hop parser-backed callers and callees may contribute labelled `structural-neighbour` evidence. Both expansions are navigation, not proof of truth, freshness, or complete runtime reachability. When deterministic evidence is insufficient, the consuming model may reformulate queries and compare bounded returned passages without requiring a second embedding index or whole-repository model ingestion.

## Structural context

The structural core complements BM25F with syntax-aware source inspection: compact file API surfaces, bounded incoming and outgoing call traces, source-cluster and dependency-hub orientation, changed-file caller impact, and regex matches grouped by enclosing symbol and coupling. A registry-driven Tree-sitter language pack provides broad grammar coverage, while language adapters supplement definitions, imports, and conservative resolution for representative Python, JavaScript, Rust, Go, .NET, JVM, native, scripting, PHP, and Swift surfaces. Retrieval consumes the same parser-backed symbol spans rather than maintaining another language-specific parser. Retrieval parsing and code-led fusion run in bounded worker processes, so a native grammar failure falls back for that file or produces explicit partial-fusion evidence instead of terminating the search. Content hashes reuse unchanged parse results.

Structural results are navigation evidence, not completeness proof. Duplicate names, dynamic dispatch, reflection, generated code, and framework wiring may remain unresolved. When reliable parser evidence is unavailable, the CLI and MCP return a bounded agent-review packet with an explicit inference schema and uncertainty field rather than presenting pattern matches as parser facts. Validated findings are stored separately with their source digest, confidence, and uncertainties; they participate in navigation until the source changes and never override parser evidence. The checked-in benchmark measures recall, precision, and output size for maintained cases.

## Canonical knowledge

Canonical knowledge remains deliberately authored. The native knowledge core provides three deterministic operations:

- `knowledge check` validates typed concepts and their durable relationship graph;
- `knowledge build-indexes` generates marked progressive-disclosure navigation from titles and query-shaped descriptions;
- `knowledge register` records explicit source patterns for a concept in `.polaralias/repo-context.json`.

Registration does not establish freshness. After a human or agent reviews the concept against every resolved bound source, `context verify` records source hashes and compact evidence. Later source changes make that receipt stale.

Generated indexes, retrieval caches, and model answers remain derived surfaces. They do not become canonical automatically.

## Event-driven documentation lifecycle

Documentation work is triggered by material Git events rather than every conversational turn. `documentation assess --base <ref>` classifies the current delta as no-op, explicitly bound update work, or a decision requiring agent judgement. It also discovers applicable root-to-nearest `AGENTS.md` rules and canonical entry points so repository instructions travel with the retrieval-to-generation journey. `change explain` records the RCC-compatible causal layer against the same fingerprint.

After an agent authors the minimum durable change, `documentation apply` validates the OKF graph, regenerates marked navigation, requires likely reader questions to retrieve affected canonical knowledge, records binding verification, and writes a local exact-delta completion receipt. It never generates canonical prose from a diff by itself.

`closure assess --base <ref>`, `close --base <ref>`, and the pre-push hook recompute the fingerprint. Material work blocks when either the causal explanation or documentation receipt is missing or stale. A closed workflow remains eligible for read-only reassessment, so completing the lifecycle does not make the subsequent pre-push gate fail. A no-op assessment avoids documentation ceremony.

## OKF Tasks boundary

OKF Tasks owns durable execution truth: outcomes, acceptance, status, workstreams, effort when enabled, evidence, and tracker reconciliation. The workflow adapter chooses `none`, `lightweight`, or `full` activation and delegates strict validation to the authoritative CLI. Task records may link to knowledge concepts, but neither surface is copied into workflow state or redefined by the other.

## Shared CLI and MCP access

The CLI and stdio adapter dispatch one operation registry for retrieval, structural context, knowledge, documentation, and explanation. Argument validation, annotations, and business handlers therefore have one implementation; each transport only translates its protocol envelope. MCP supports the stateless `2026-07-28` lifecycle through `server/discover` and per-request metadata while retaining the MCP `2025-11-25` initialize-handshake path for compatible clients. The adapter fixes the repository root at process start and distinguishes read-only retrieval, validation, analysis, and assessment from mutating application, explanation, verification, index generation, and binding registration.

## Legacy archive

The absorbed engineering packages are preserved unchanged under the repository-root `archive/` directory. That directory is outside catalogue generation, installation, BM25 retrieval, and structural analysis. Legacy names remain compatibility inputs to EWF routing, not separately invoked or maintained implementations. `repo-setup` remains active because bootstrap precedes the material engineering lifecycle.

## Host integration

`host recipe` describes supported MCP, project-routing, and Git-gate setup. `host install` writes a local Git `pre-push` hook; for Codex it merges a marker-owned activation block into project `AGENTS.md`, and for Claude it merges a portable project `.mcp.json` entry. Independently authored instructions, hooks, and unrelated configuration are preserved.

Codex integration uses the installed `codex mcp add` interface but keeps user-level MCP activation explicit. The project `AGENTS.md` block directs material changes through the installed EWF and its single `activate` command without inventing an undocumented hook schema. Git-only mode provides pre-push enforcement without claiming an MCP installation.

The packaged model-evaluation runner tests implicit activation, project-routed activation ordering, nearby non-activation, and source-driven authority expansion in temporary repositories. It grades the activation receipt rather than mere state-file existence and checks that named implementation files were clean in the activation Git baseline. Windows fixtures seed an evaluator-owned unactivated state file so sandbox ACLs cannot hide evidence from the parent grader, and timeout diagnostics are bounded.

On the latest 2026-09-18 project-routed run, EWF activated before either requested implementation file became dirty and the agent completed both requested edits. The nested Codex process still timed out before emitting its final response. Project-routed CLI invocation is therefore evidenced; catalogue-only discovery and timely end-to-end completion remain separate measured residuals rather than completed claims.

## Reading order

- [Documentation map](documentation-map.md) — repository knowledge entry point and schema boundaries.
- [Complete Markdown inventory](documentation-inventory.md) — exhaustive classification of repository Markdown surfaces.
- [Repository visualization](repository-visualization.md) — derived visualisation contract.

# Citations

1. [MCP 2026-07-28 server discovery](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/discover.mdx)
2. [MCP 2026-07-28 tools](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx)
