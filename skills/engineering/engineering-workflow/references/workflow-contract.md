# Engineering Workflow Contract

## State model

Workflow state is local control state, not a source of product, architecture, execution, or Git truth.

```yaml
schema_version: 1
status: active
primary_phase: understand
active_capabilities: []
outstanding_gates: []
task_tracking:
  mode: none
  task_ref: null
continuity:
  checkpoint: null
gate_receipts: []
```

Use exactly one primary phase and any number of independently justified capabilities and gates.

## Phase selection

- `understand`: repository orientation, ambiguity resolution, evidence gathering, or knowledge maintenance is the immediate purpose.
- `design`: resolved truth is being converted into behavioural contracts, scenarios, acceptance, or implementation-ready packages.
- `deliver`: implementation, validation, workstream coordination, or integration is active.
- `close`: the final bounded change, task truth, knowledge impact, validation, and cleanup obligations are being reconciled.
- `pause`: verified continuation state is being prepared.
- `resume`: saved continuation state is being verified before another phase is selected.

A phase is current control context, not the only concern that exists. Capabilities and outstanding gates survive phase changes until deliberately resolved.

Use `journey enter understand`, `journey enter design`, or `journey enter close` to make those transitions deterministically. The operation preserves existing capabilities and gates, records phase history, adds only the journey defaults, and returns the one internal reference to load. Understand activates repository-context retrieval without inventing a knowledge gate. Design registers `acceptance-defined` because observable acceptance is its exit condition. Close adds no gates by assumption; material obligations must already be registered from actual scope.

## Task modes

- `none`: no durable execution record is justified.
- `lightweight`: preserve outcome, acceptance, status, related knowledge, and evidence.
- `full`: add only the required workstreams, effort, estimates, tracker mappings, or detailed reconciliation.

The workflow may escalate task mode when durable execution needs emerge. It must not silently reduce a mode or discard an established task reference.

Use `task configure` to change modes and `task check` to validate the configured bundle. Durable modes activate `task-lifecycle` and register `task-reconciliation`. `none` mode avoids CLI discovery and execution entirely. Full mode makes advanced features available but does not activate them. Read [okf-tasks-adapter.md](./okf-tasks-adapter.md) for the delegation and closure contract.

## Gates

Use concrete obligation names, for example:

- `acceptance-defined`
- `implementation-validation`
- `integrated-tree-validation`
- `task-reconciliation`
- `knowledge-impact-review`
- `knowledge-promotion`
- `worktree-cleanup`
- `publication-safety`

A gate is resolved only by evidence from its owning surface. Workflow state records the obligation and result; it does not manufacture the evidence.

Use `gate add --gate <name>` to register new obligations on an active workflow without resetting existing state or duplicating a gate.

Use `gate resolve --gate <name> --evidence <summary>` to discharge exactly one outstanding gate. The command refuses gates that are not outstanding and stores a compact timestamped receipt without copying full logs, diffs, task records, or canonical documents.

## Command contract

Every command returns structured JSON and a meaningful exit status.

### `activate`

Provides the single normal lifecycle entrypoint for agents. It creates missing state, validates and returns active state, or starts a new cycle from valid closed state. It records a bounded Git baseline—HEAD, dirty-path count, and at most 500 dirty paths—so evaluation can establish whether activation happened before the intended mutation. Invalid existing state is reported rather than overwritten.

### `start`

Creates minimal state when none exists. Repeated invocation preserves existing state rather than resetting it.

### `checkpoint`

Stores a compact verified summary and next action. It never copies complete task, knowledge, worktree, or handoff records.

### `resume`

Validates the stored schema and returns the saved state for repository re-verification. Invalid state is reported rather than silently repaired.

### `close`

Returns a blocked result while outstanding gates remain. With `--base`, it also requires current causal-explanation and documentation receipts for a material Git delta. A gate-free valid state can become closed only when those event-driven checks are clear. Adapters may resolve gates only from structured evidence produced by their owning systems.

### `journey enter`

Transitions an active workflow into the named internal journey. A closed workflow refuses the transition. Specialist legacy names are not stored as phases or capabilities.

### `task configure` and `task check`

Configure proportionate execution persistence and delegate strict bundle conformance to the authoritative OKF Tasks CLI. The adapter preserves established references, constrains configured paths to the repository, never uses a shell, and refuses silent mode reduction.

### `capability enable`

Activates one bounded extension and registers its required gates. The returned reference is the only extension detail to load. Availability does not imply authority to perform external or destructive actions.

### `closure assess`

Reports change, validation, task, knowledge, coordination, publication, and residual lanes independently, plus the compact session-alignment contract and its required reconciliation ordering. With `--base`, it recomputes the material-delta fingerprint and checks the explanation and documentation receipts. It is read-only and blocks through its exit status while any gate or event-driven receipt remains unresolved. A ready assessment still leaves workflow state active; only `close` performs the terminal state transition.

### `dissection assess`

Returns a conservative machine-readable inventory of instructions, manifests, entrypoint candidates, tests, documentation, task and knowledge surfaces, OpenWiki ownership signals, Git identity, trust classes, and gaps. It never labels conventional files as verified runtime behaviour.

### `documentation bootstrap`

Returns a read-only documentation-foundation assessment for an inherited or explicitly requested repository-documentation journey. It distinguishes `no-rke`, `partial-rke`, and `mature-rke`; recommends the minimum foundation or `no-op`; and separates preserve, review, and evidence-required sets. It never authors prose or supersedes an existing truth surface automatically.

### `handoff write` and `handoff inspect`

Write and consume deterministic continuation artefacts outside workflow, task, and canonical knowledge state. Local visibility is the default and requires ignored, untracked storage; shared visibility uses commit-capable `.rke/handoffs/` storage for deliberate Git collaboration. Writing rejects secret-like content and manages one active same-stream handoff. Inspection can constrain or safely infer visibility, rejects ambiguous placement, and returns the claims that require current verification.

### `coordination validate` and `coordination plan`

Validate worktree topology, path ownership, dependencies, inherited authority, and validation classes, then return non-executing argv plans. Neither operation allocates worktrees or grants external authority.

### `publication scan`

Scans tracked text and hygiene surfaces without returning matched values. It also uses an already-installed `gitleaks` binary for history-aware detection, but never installs tools implicitly.

### `documentation assess`

Computes the material Git delta from an explicit base, filters local/generated control surfaces, and returns `no-op`, `update`, or `decision-required`. Explicit bindings identify update candidates; lexical or unmapped changes retain an agent-judgement obligation.

### `change explain`

Records a bounded RCC-compatible causal explanation against the exact material-delta fingerprint. The local receipt is explanatory evidence, not canonical knowledge, validation proof, or publication authority.

### `documentation apply`

Validates already-authored canonical changes, requires affected-concept coverage, rebuilds generated indexes, checks one or more likely reader questions, verifies reviewed bindings, and records an exact-delta completion receipt. It never writes canonical prose from the assessment alone.

### `host recipe` and `host install`

Expose supported MCP activation and local Git pre-push enforcement. Recipe is read-only. Install refuses independently owned hook or MCP entries without explicit force. Codex user-level MCP activation remains a returned command; Claude project MCP configuration uses `.mcp.json`; Git-only mode installs no MCP entry.

### `legacy route`

Maps a retained documented legacy alias or full package name to exactly one replacement journey, capability, adapter, or lifecycle operation. It does not mutate state or execute the destination. Unknown and deliberately retired inputs fail without fuzzy guessing. `repo-setup` maps to a separate bootstrap capability rather than an EWF phase.

### `context find`

Refreshes disposable repository evidence and returns BM25F-ranked chunks with repository-relative paths, line spans, symbols or headings, snippets, score reasons, and an index revision. Parser-backed one-hop fusion is attempted only for code-led or exact-identifier result sets. A scope must remain inside the configured repository root.

### `context check`

Refreshes the generated index and reports index freshness, changed and deleted file counts, and deliberately separate knowledge-freshness fields derived from explicit bindings and receipts. A fresh generated index is not proof that canonical knowledge is fresh.

### `context impact`

Classifies each supplied changed path exactly once as explicitly bound, a lexical review candidate, or unmapped. Bound impacts report `fresh`, `stale`, or `unknown` from verification receipts; candidates never receive deterministic freshness status.

### `context verify`

Records hashes for every currently resolved source of one registered canonical document after an actual review. The tracked receipt can establish freshness until a bound source changes, disappears, or a glob resolves to a different set.

### `context benchmark`

Runs a repository-local versioned query corpus and reports recall at 1, 5, and 10 plus mean reciprocal rank. Retrieval metrics measure candidate quality, not engineering correctness.

### `knowledge check`

Validates typed OKF concepts and the resolved durable relationship graph inside one bounded bundle. It is read-only and does not establish factual correctness.

### `knowledge build-indexes`

Builds marked progressive-disclosure indexes from concept titles and query-shaped descriptions. It refuses to replace manual indexes without explicit force.

### `knowledge register`

Registers explicit source patterns for one existing typed concept in the repository-context manifest. A changed source set invalidates prior freshness evidence; registration itself leaves freshness unknown.

## Truth precedence

When surfaces disagree, investigate rather than applying one universal winner. Prefer the strongest current evidence for the claim being made:

- current user and host policy for authority;
- verified runtime and tests for observed behaviour;
- canonical knowledge for accepted product and architecture truth;
- OKF Tasks for execution status and obligations;
- Git and provider evidence for branch, review, and integration state;
- workflow state and handoffs only for continuation hints.
