# Optional workflow state and operation contracts

The persisted phases, journeys, capabilities and gates below describe RKE compatibility state. They do not define the engineering methodology and are not prerequisites for ordinary EWF work. Read this reference only when deliberately using persistent state or inspecting existing state. A successful state transition cannot establish acceptance or settle a product decision.

## Method mapping

| EWF method | Existing RKE state identifiers when persistence is useful |
| --- | --- |
| Comprehension, dissection, knowledge | `understand` phase; `journey enter understand` is optional bookkeeping, including for dissection. |
| Clarification | `query-to-knowledge` capability and `shared-understanding` gate only for an actual unresolved decision. |
| Design | `design` phase / `journey enter design`, with `acceptance-defined`. |
| Delivery | `deliver` phase; retain actual validation obligations. |
| Alignment | `close` phase / `journey enter close`; `closure assess` reports lanes and `close` performs the state transition. |
| Handoff, pickup | `pause` / `resume`, checkpoint and handoff operations as useful. |
| Coordination, publication | `parallel-delivery` / `publication` capabilities when selected, not because available. |
| Task lifecycle | `none`, `lightweight`, or `full` task modes, delegated to independent OKF Tasks. |

These existing runtime names do not require EWF reference filenames to match them. An observed falsifier changes the engineering decision immediately; if state is active, record design re-entry rather than using a command as the reason to reconsider.

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
State validation rejects duplicate capability or gate names and phase-history transitions with unrecognised endpoints before consequential workflow operations.

## Phase selection

- `understand`: repository orientation, ambiguity resolution, evidence gathering, or knowledge maintenance is the immediate purpose.
- `design`: resolved truth is being converted into behavioural contracts, scenarios, acceptance, or implementation-ready packages.
- `deliver`: implementation, validation, workstream coordination, or integration is active.
- `close`: the final bounded change, task truth, knowledge impact, validation, and cleanup obligations are being reconciled.
- `pause`: verified continuation state is being prepared.
- `resume`: saved continuation state is being verified before another phase is selected.

A phase is current control context, not the only concern that exists. Capabilities and outstanding gates survive phase changes until deliberately resolved.

Select the engineering method in EWF independently. When persistent state is deliberately active, use `journey enter understand`, `journey enter design`, or `journey enter close` to record the transition. The operation preserves existing capabilities and gates, records phase history, and adds only the journey defaults. Understand activates repository-context retrieval without inventing a knowledge gate. Design registers `acceptance-defined` because observable acceptance is its exit condition. Close adds no gates by assumption; material obligations must already be registered from actual scope.

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

Provides an optional lifecycle entrypoint for agents using durable state. It creates missing state, validates and returns active state, or starts a new cycle from valid closed state. It records a bounded Git baseline—HEAD, dirty-path count, and at most 500 dirty paths—so evaluation can establish whether activation happened before the intended mutation. Invalid existing state is reported rather than overwritten.

### `start`

Creates minimal state when none exists. Repeated invocation preserves existing state rather than resetting it.

### `checkpoint`

Stores a compact verified summary and next action. It never copies complete task, knowledge, worktree, or handoff records.

### `resume`

Validates the stored schema and returns the saved state for repository re-verification. Invalid state is reported rather than silently repaired.

Validation covers status, non-empty capability and gate names, task tracking shape, continuity and checkpoint shape, timestamps, and gate receipts. Activation, checkpoint, task checks, closure assessment, and close also refuse malformed state with `invalid-state` before using it.

### `close`

Returns a blocked result while outstanding gates remain. With `--base`, it also requires current documentation evidence for a material Git delta. A gate-free valid state can become closed only when those event-driven checks are clear. Adapters may resolve gates only from structured evidence produced by their owning systems.

### `journey enter`

Transitions an active workflow into the named internal journey. A closed workflow refuses the transition. Only supported phase and capability identifiers are stored.

### `task configure` and `task check`

Configure proportionate execution persistence and delegate strict bundle conformance to the authoritative OKF Tasks CLI. The adapter preserves established references, constrains configured paths to the repository, never uses a shell, and refuses silent mode reduction.

### `capability enable`

Activates one bounded extension and registers its required gates. The supported internal identifiers are runtime compatibility names; see the method mapping below. Availability does not imply authority to perform external or destructive actions.

### `closure assess`

Reports validation, task, knowledge, coordination, publication, and residual lanes independently, plus the compact session-alignment contract and its required reconciliation ordering. With `--base`, it recomputes the material-delta fingerprint and checks the documentation receipt. It is read-only and blocks through its exit status while any gate or event-driven receipt remains unresolved. A ready assessment still leaves workflow state active; only `close` performs the terminal state transition.

### `dissection assess`

Returns a conservative machine-readable inventory of instructions, manifests, entrypoint candidates, tests, documentation, task and knowledge surfaces, OpenWiki ownership signals, Git identity, trust classes, and gaps. It never labels conventional files as verified runtime behaviour.

### `documentation bootstrap`

Returns a read-only documentation-foundation assessment for an inherited or explicitly requested repository-documentation journey. It distinguishes `no-rke`, `partial-rke`, and `mature-rke`; compares verification receipts with current bound-content hashes without persisting a context index; reports existing surfaces and gaps without selecting a foundation; and separates preserve, review, freshness, and evidence-required sets. Stale or unverified knowledge cannot produce a mature no-op. It never authors prose or supersedes an existing truth surface automatically.

### `handoff write` and `handoff inspect`

Write and consume deterministic continuation artefacts outside workflow, task, and canonical knowledge state. Local visibility is the default and requires ignored, untracked storage; shared visibility uses commit-capable `.rke/handoffs/` storage for deliberate Git collaboration. Writing rejects secret-like content and manages one active same-stream handoff. Inspection can constrain or safely infer visibility, rejects ambiguous placement, and returns the claims that require current verification.

Max handoff writing accepts repeatable verification, change, risk and canonical-reference details in addition to the compact summary. It normalises each supplied value to one line so a source-provided heading cannot forge a new next-action section. A missing canonical reference makes inspection stale and withholds the proposed next action.

### `coordination validate` and `coordination plan`

Validate an explicit Git base, lane names and branches, sibling worktree targets, non-overlapping path ownership, and acyclic dependencies, then return non-executing argv plans. The agent must separately inspect inherited authority, validation classes, actual Git topology, and exact-tip integration evidence before allocation or cleanup. Neither operation allocates worktrees or grants external authority.

### `coordination cleanup-check`

Rechecks one existing lane before any cleanup: owned sibling worktree, clean state, exact current tip equal to the reviewed commit, observed remote destination containing that tip, and absent remote source branch. It is read-only and fails closed on stale review heads, unavailable remote evidence or un-fetched destination commits. It does not remove worktrees or branches or infer integration from PR names.

### `coordination cleanup`

A separate, mutating operation for an expressly authorised exact lane and branch. It repeats the cleanup-check immediately before mutation, repairs only the selected Git worktree link if needed, then asks Git to remove the clean owned worktree and delete its local branch without force. It does not delete the remote branch or infer PR state. A partial result reports which local mutation succeeded; never treat eligibility as authorisation to call this operation.

### `publication scan`

Scans tracked text and hygiene surfaces without returning matched values. It also uses an already-installed `gitleaks` binary for history-aware detection, but never installs tools implicitly.

### `tracker preview`

Renders accepted non-OKF work packages from a repository-local YAML or JSON file into tracker-neutral, hierarchy- and acceptance-preserving rows. It refuses unresolved source relationships and records `publication: not performed` and `tasksCreated: false`; it never calls a provider or creates a task ledger. Durable execution and live tracker synchronisation still default to the independent OKF Tasks CLI and Tracker Profiles.

### `documentation assess`

Computes the material Git delta from an explicit base, filters local/generated control surfaces, and returns `no-op`, `update`, or `decision-required`. Explicit whole-document bindings identify affected knowledge; optional selected claim bindings report exact section/source freshness, move candidates and unresolved evidence. Bounded lexical `documentationDiscovery` adds candidate documents, query terms, reasons and coverage limits from changed paths/symbols/diff evidence, without making bindings or semantic claims. Select this support when useful or required by repository policy; ordinary documentation judgement can use direct inspection instead. Review candidates and explicit bindings through [documentation lifecycle](documentation-lifecycle.md). Assessment needs no persistent workflow state. A current claim binding does not prove behavior.

### `documentation apply`

Validates already-authored canonical changes, requires affected-concept coverage, current selected claim bindings and candidate-document review acknowledgements (supplied knowledge paths count automatically; other reviewed candidates use `--reviewed-document`), rebuilds generated indexes, checks one or more likely reader questions, verifies reviewed bindings, and records an exact-delta completion receipt. It never writes canonical prose from the assessment alone.

### `documentation disposition`

Records a reviewed `no-canonical-update` decision for a material delta with no affected binding and no selected claim requiring review. It requires every material changed path, every returned candidate document acknowledged with repeatable `--reviewed-document`, and substantive causal evidence, refuses changed canonical concepts or incomplete coverage, and writes only a local exact-delta receipt. Closure rechecks its coverage and binding status; this route never marks knowledge fresh or creates a bundle.

### `host recipe`, `host inspect`, `host preview`, `host install`, `host repair` and `host remove`

Expose supported MCP activation and local Git pre-push enforcement. Recipe, inspect/status and preview are read-only; `install`, `repair` and `remove` also accept `--dry-run`. The repository-local ownership ledger retains selected opt-in hooks and shared resource owners. Install refuses independently owned hook or MCP entries without explicit force; repair/removal refuse modified owned content rather than deleting an owner's edits. Forced replacement retains a bounded non-sensitive displaced component for restoration. JSON edits preserve unrelated member/handler bytes. Missing verified entries may be repaired; removal retains shared routing and Git configuration until the last owner. Codex user-level MCP activation remains a returned command; Claude project MCP configuration uses `.mcp.json`; Git-only mode installs no MCP entry. Installed launchers pin the actual Node executable, loaded RKE script and selected root. Configuration qualification is separate from a live host session.

Host ownership also records the prior generated launcher and selected Git scope. Unchanged launcher configuration can upgrade from a moved runtime without invoking that old command. Worktree-specific hooks require the owner-enabled Git worktree configuration extension; multiple worktrees refuse shared local hook mutation. Scope drift and modified launcher entries retain an explicit refusal rather than changing unrelated settings.

New host launchers and receipts also bind physical root identity. A same-path directory or Git-administration replacement invalidates the pin; ordinary source edits and commits do not. Manual MCP configuration without an installation pin captures identity at startup. Repository data cannot supply the trusted root validator or select the Git executable. Native assistance fails to a bounded unavailable response; the Git gate refuses assessment of another worktree. Root checks and guarded writes remain bounded checks, not a cross-file filesystem transaction.

### `context find`

Refreshes disposable repository evidence and returns SQLite FTS5-ranked chunks with repository-relative paths, line spans, symbols or headings, snippets, and native rank. A scope must remain inside the configured repository root.

### `context check`

Refreshes the generated index and reports index freshness, changed and deleted file counts, and deliberately separate knowledge-freshness fields derived from explicit bindings and receipts. A fresh generated index is not proof that canonical knowledge is fresh.

### `context impact`

Matches supplied changed paths against explicit manifest bindings and reports affected knowledge and unmatched paths separately. Verification receipts establish `fresh`, `stale`, or `unknown` only for bound knowledge; lexical similarity does not create bindings or freshness status.

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
