# Retrieval, Generation, and Rule-Adherence Coverage

This matrix is the completeness surface for Slices 4 and 5. It distinguishes executable guarantees from agent-quality evaluation so a passing unit suite is not overstated as proof of prose quality.

| Objective | Implemented mechanism | Executable coverage | Residual limit |
| --- | --- | --- | --- |
| Better retrieval | Incremental SQLite FTS5 storage, content-hash freshness, pruned traversal, secret omission, in-process Tree-sitter code chunks, Markdown passages, and weighted path/filename/symbol/heading/body fields | checked-in query corpus, changed/unchanged identity tests, sensitive-path and traversal tests, multi-language parser fixtures, transport parity, and an executable mixed-language resource benchmark | deterministic lexical retrieval is not semantic truth; consequential claims still require source review; the opt-in 1k/10k/50k matrix measures scaling |
| Structural comprehension | registry-driven in-process Tree-sitter parsing, normalized symbols/imports/edges, live file API, scoped caller/callee traces and impact, repository map, bounded worker-isolated regex search, digest-bound agent-review fallback, and exact CLI/MCP handler parity | checked-in multi-language structural corpus, extraction tests, scoped trace/impact/map/search, secret and oversized-source exclusion, regex timeout, reviewed-evidence invalidation, and transport-parity cases | grammar extraction depth varies; duplicate names, dynamic dispatch, reflection, generated code, and framework wiring can remain unresolved; review evidence is inference and the review-store scan is capped at 100 receipt files per repository |
| Better generation | read-only bootstrap and assessment, exact glob-bound knowledge receipts, stale-source detection, documentation application receipts, and Git-delta-bound causal explanations | zero/partial state assessment, exact source-set receipt, stale-source, impact, application, and explanation tests; plus the bounded TypeScript `rke-eval` runner | model outcomes vary by host and model; retain dated run evidence rather than generalising from one run |
| Higher in-repo rule adherence | root-to-nearest `AGENTS.md` discovery and hashes carried from assessment into the application receipt | root rule and nested-rule discovery tests; exact-delta closure tests; adversarial prompt corpus | host policy remains higher authority; repository text cannot grant tools, secrets, or publication authority |
| Reliable invocation | one idempotent `activate` command; activation-time Git baseline; marker-owned Codex `AGENTS.md` routing; packaged evaluation corpus; CLI and MCP share the complete operation registry; `.githooks/pre-push` checks closure through configured `core.hooksPath` | lifecycle activation/reopen tests; project-routing merge/idempotence tests; evaluator distinguishes activation-before-edit; operation-registry and CLI/MCP parity tests; clean npm pack/install executable and resource smoke; pre-push base, path-ownership, and Claude config merge tests | catalogue-only implicit selection remains host/model behaviour; Codex MCP activation is intentionally user-level and explicit |
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

The prompt corpus covers qualitative agent behaviour, including no-op restraint, minimum canonical authorship, repository-rule following, prompt injection, data exfiltration, hook ownership, unsupported-host claims, inherited-repository documentation, immediate reset after an observed falsifier, and restraint when failures are incidental. `rke-eval` grades the bounded result corpus, including the resulting workflow phase and acceptance gate for convergence cases. A run consumes model usage and proves only the selected model, host, skill installation, and dated cases. Unit tests still prove deterministic guardrails rather than the subjective quality of every future document.

The focused 2026-09-22 Codex host run passed both packaged convergence cases. The observed-falsifier case persisted the `design` phase and reopened `acceptance-defined` after the first decisive observation. The incidental-failure case persisted the `deliver` phase, left `acceptance-defined` closed, kept acceptance unchanged, and requested a valid hypothesis-relevant observation. Both isolated runs used the EWF 4.6.0 package copied from the evaluated npm source tree and completed without modifying product files.

The initial 2026-09-18 Codex host runs passed explanation-only non-activation and did not create forbidden exfiltration artefacts, but catalogue-only material-change runs edited requested files without readable lifecycle evidence or a final response before timeout. After adding the single activation command and installed project routing, a fresh synthetic run produced an activation receipt before either requested source file became dirty and completed both requested edits. The nested Codex process still reached its timeout before emitting a final response, so project-routed CLI invocation is now evidenced while catalogue-only discovery and timely end-to-end completion remain separate measured residuals.
