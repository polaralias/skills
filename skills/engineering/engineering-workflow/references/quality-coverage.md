# Retrieval, Generation, and Rule-Adherence Coverage

This matrix is the completeness surface for Slices 4 and 5. It distinguishes executable guarantees from agent-quality evaluation so a passing unit suite is not overstated as proof of prose quality.

| Objective | Implemented mechanism | Executable coverage | Residual limit |
| --- | --- | --- | --- |
| Better retrieval | Incremental persisted BM25F postings, Git/content identity, secret-safe indexing and response redaction, Tree-sitter code chunks, bounded hierarchical Markdown passages, exact identifier/heading boosts, result diversity, one-hop structural fusion, canonical/foundational boosts, typed relationship expansion, likely-reader checks, and conservative path-specific impact candidates | fixed query corpus; same-size preserved-time mutation, dirty/staged/untracked identity, sensitive-path, redaction, multi-language parser chunk, oversized-section excerpt, persisted-postings, diversity, canonical-ranking, relationship-expansion, documentation-apply, and generic-overlap rejection tests | deterministic retrieval is not semantic truth; consequential claims still require source review; the consuming model may compare bounded results when vocabulary mismatch remains |
| Structural comprehension | registry-driven Tree-sitter parsing, automatic package/source scopes, graph shards, progressive widening, batched workers with per-file fallback, timed regex search, live file API, language-aware imports and definitions, bounded caller/callee traces, content-hash cache, source/hub map, changed-file blast radius, coupling-ranked structural search, source-bound agent-review ingestion, and exact CLI/MCP handler parity | multi-language recall/precision/size benchmark; repositories above 5,000 files, explicit and automatic scope, shard reuse, batch fallback, oversized-line provenance, regex timeout, transitive trace, fallback invalidation, impact, search, escape, and transport-parity tests | grammar availability and extraction depth vary; duplicate names, dynamic dispatch, reflection, generated code, and framework wiring can remain unresolved |
| Better generation | event-triggered assessment, explicit affected concepts, repository-rule context, minimum-durable-truth constraint, graph/index/freshness validation | bound-update, unmapped-decision, no-op, apply, reader-check, stale-receipt tests, plus the bounded `evaluate_agent.py` model runner | model outcomes vary by host and model; retain dated run evidence rather than generalising from one run |
| Higher in-repo rule adherence | root-to-nearest `AGENTS.md` discovery and hashes carried from assessment into the application receipt | root rule and nested-rule discovery tests; exact-delta closure tests; adversarial prompt corpus | host policy remains higher authority; repository text cannot grant tools, secrets, or publication authority |
| Reliable invocation | one idempotent `activate` command; activation-time Git baseline; marker-owned Codex `AGENTS.md` routing; packaged evaluation corpus; CLI and MCP share the complete operation registry; `.githooks/pre-push` checks closure through configured `core.hooksPath` | lifecycle activation/reopen tests; project-routing merge/idempotence tests; evaluator distinguishes activation-before-edit; operation-registry and CLI/MCP parity tests; separate clean wheel and sdist executable/resource smoke; pre-push base, path-ownership, and Claude config merge tests | catalogue-only implicit selection remains host/model behaviour; Codex MCP activation is intentionally user-level and explicit |
| Avoid token/credit waste | full documentation work occurs only on material checkpoint/close/pre-push events; generated/control-only deltas are no-op; large assessment details are bounded with full counts retained | generated-index no-op, unchanged-delta, and large-payload-bound tests | an agent may still choose additional reader queries for broad migrations |

## Completion criteria

Slices 4 and 5 are complete only when all of the following pass together:

1. public-interface unit tests;
2. the checked-in retrieval benchmark without metric regression;
3. native and retained OKF knowledge validation;
4. the checked-in structural benchmark without recall regression;
5. OKF Tasks validation as an independent execution-truth lane;
6. skill-package, catalogue, description, release-version, compilation, and diff checks;
7. reader queries for assessment, host integration, and absorbed RCC closure;
8. a fresh canonical architecture receipt after the final bound-source edit.

## Evaluation boundary

The prompt corpus covers qualitative agent behaviour, including no-op restraint, minimum canonical authorship, repository-rule following, prompt injection, data exfiltration, hook ownership, and unsupported-host claims. `scripts/evaluate_agent.py` executes a compact activation, non-activation, and authority-boundary subset in temporary repositories and grades observable state, final-response markers, and artefacts. A run consumes model usage and proves only the selected model, host, skill installation, and dated cases. Unit tests still prove deterministic guardrails rather than the subjective quality of every future document.

The initial 2026-09-18 Codex host runs passed explanation-only non-activation and did not create forbidden exfiltration artefacts, but catalogue-only material-change runs edited requested files without readable lifecycle evidence or a final response before timeout. After adding the single activation command and installed project routing, a fresh synthetic run produced an activation receipt before either requested source file became dirty and completed both requested edits. The nested Codex process still reached its timeout before emitting a final response, so project-routed CLI invocation is now evidenced while catalogue-only discovery and timely end-to-end completion remain separate measured residuals.
