# OKF Tasks Profile

Version 0.4

OKF Tasks is an independent profile of Open Knowledge Format (OKF) v0.1 for representing trackable work as portable Markdown concepts. It adds task lifecycle, workstream, evidence, relationship, and tracker-mapping conventions without changing the OKF base format.

Normative terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as requirement levels.

## 1. Scope

The profile standardizes:

- task and workstream concept types;
- stable repository-local identity;
- baseline lifecycle states and transitions;
- task relationships and external tracker mappings;
- completion and evidence semantics;
- live, manual, and estimated effort records;
- task-bundle indexes and conformance.

It does not standardize product requirements, architecture, sprint membership, comments, attachments, credentials, webhook deployment, or user-interface views. It standardizes portable tracker configuration and adapter behavior while provider authentication and transport remain adapter concerns. Effort estimates and sprint points are portable values; the planning method that produces them remains local.

## 2. Relationship to OKF

An OKF Tasks bundle MUST conform to [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/ee67a5ca27044ebe7c38385f5b6cffc2305a9c1a/okf/SPEC.md). Requirements in this profile are additional constraints. The commit-pinned link identifies the exact upstream text used by this version.

The published identity of this profile version is `https://github.com/polaralias/okf-tasks/blob/v0.4.0/SPEC.md`. Producers SHOULD include that identity in the bundle root index as described in section 10.

Each non-reserved Markdown file in the bundle MUST be an OKF concept with parseable YAML frontmatter and a non-empty `type`. Producers MAY add fields. Consumers MUST preserve unknown fields when round-tripping a record and MUST tolerate unknown task-adjacent concept types.

## 3. Bundle structure

The default repository-local bundle root is `tasks/`:

```text
tasks/
├── index.md
├── log.md                         optional
├── trackers/                      optional
│   └── <tracker-slug>.md
└── <task-slug>/
    ├── task.md
    ├── workstreams/
    │   └── <workstream-slug>.md
    └── time/
        └── <entry-id>.md
```

This default placement keeps operational execution state visibly separate from durable documentation, source code, and configuration.

A repository MAY instead use `docs/tasks/` when its `docs/` tree is already the established home for an actual project's delivery plan and project operations:

```text
docs/
├── PROJECT.md                     durable project context
└── tasks/
    ├── index.md
    └── <task-slug>/
        └── task.md
```

The `docs/tasks/` placement does not make task records canonical product requirements, architecture, or decisions. Producers MUST keep those durable conclusions in the repository's established documentation surfaces and link or promote them from task records. Consumers and adapters MUST accept an explicitly selected bundle root at either placement; document and bundle conformance are otherwise identical.

`index.md` and `log.md` retain their OKF-reserved meanings. Any additional Markdown file, including session or coordination records, MUST be an OKF concept with a descriptive `type`.

The task concept ID is its OKF path, such as `implement-token-rotation/task`. The `task` slug is the stable profile identifier and MUST match its parent directory. A published slug MUST NOT be renamed or reused for a different outcome. Imports MUST receive a unique local slug and MAY retain their source identity in `origin`. Duplicate concept paths are invalid. A published task SHOULD be superseded rather than deleted; deletion is reserved for unpublished mistakes or repository retention policy.

## 4. Task concepts

A task concept MUST use `type: Task` and contain:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `type` | required | Exactly `Task`. |
| `task` | required | Stable lowercase kebab-case task slug. |
| `title` | required | Human-readable title. |
| `description` | required | One-sentence observable outcome summary. |
| `status` | required | A lifecycle status from section 6. |
| `created` | required | RFC 3339 creation timestamp. |
| `timestamp` | required | RFC 3339 time of the last meaningful change. |

`timestamp` is the portable last-updated value. Producers MUST advance it whenever they change lifecycle state, ownership, scope, acceptance, evidence, relationships, effort, estimates, external bindings, or other content that changes the record's meaning. Pure formatting changes that preserve meaning MAY retain it. Filesystem modification time and Git commit time MUST NOT replace this field. Consumers SHOULD label it **Last meaningful change** so it is not confused with creation, work start, completion, synchronization, or observation times.

The following fields are optional profile extensions:

| Field | Shape | Meaning |
| --- | --- | --- |
| `owner` | string | Primary accountable owner. |
| `assignees` | list of strings | Assigned people or agents. |
| `priority` | string | Producer-defined priority. |
| `tags` | list of strings | OKF cross-cutting categories. |
| `fields` | mapping | Portable typed custom values. Each entry contains `type` and `value`. |
| `parent` | string | Bundle-relative link to a parent task concept. |
| `depends_on` | list of strings | Bundle-relative links to prerequisite task concepts. |
| `external` | list of mappings | External tracker identities defined in section 9. |
| `started` | datetime | Start of the first recorded work session. |
| `finished` | datetime | Final task completion time, set when the task becomes `done`. |
| `effort_minutes` | integer | Generated sum of closed time-entry effort. |
| `estimate` | mapping | Expected active effort and its evidential basis. |
| `sprint_points` | mapping | Team-contextual relative complexity; never a time duration. |
| `completion_history` | list of mappings | Prior completion and reopening events. |
| `origin` | mapping | Source system, repository, and identifier for an imported record. |

The body MUST contain these second-level headings:

- `## Outcome`
- `## Scope`
- `## Acceptance`
- `## Evidence`

Producers SHOULD also include `## Dependencies and risks`, `## Related knowledge`, and `## Workstreams` where applicable.

## 5. Workstream concepts

A separately owned or independently validated delivery unit MAY be represented as a workstream. Every declared workstream is required for its parent task; this profile has no `required: false` workstream flag. Optional follow-up work SHOULD be a separately linked task. A workstream MUST use `type: Workstream` and contain:

- `task`: parent task slug;
- `workstream`: stable lowercase kebab-case workstream slug matching the filename;
- `title` and `description`;
- `status` from section 6;
- `created` as an RFC 3339 datetime;
- `timestamp` as an RFC 3339 datetime.

Workstream `timestamp` follows the same last-meaningful-change rule as Task `timestamp`.

`owner`, `assignees`, and `branch` are optional. Workstream bodies MUST contain `## Assigned outcome`, `## Acceptance and validation`, `## Evidence`, and `## Handoff`.

The lifecycle coordinator owns the parent task record and generated index during concurrent work. A workstream owner SHOULD change only its workstream record and owned implementation paths until integration. Workstreams use the same lifecycle transition graph as tasks. Producers SHOULD normally create an actionable workstream in `ready` rather than `proposed`.

## 6. Lifecycle

The baseline statuses are:

- `proposed`: the outcome exists but readiness is unresolved;
- `ready`: the contract and dependencies are sufficient to start;
- `in-progress`: owned delivery work is active;
- `blocked`: progress requires a named dependency, decision, or external change;
- `validation`: implementation exists and completion checks are active;
- `done`: acceptance, required workstreams, evidence, and knowledge promotion are reconciled;
- `superseded`: another task or decision replaced the record;
- `deferred`: intentionally inactive without a current blocker-resolution expectation.

Normal transitions are:

```text
proposed   -> ready | deferred | superseded
ready      -> in-progress | deferred | superseded
in-progress -> blocked | validation | deferred | superseded
blocked    -> in-progress | deferred | superseded
validation -> in-progress | blocked | done
done       -> in-progress | superseded
deferred   -> ready | superseded
superseded ->
```

A producer MAY force a transition only to correct a record and SHOULD document the reason in the body or commit history.

`done -> in-progress` is a reopening, not a rewrite of history. The producer MUST append the prior `finished` time and the reopening time to `completion_history`, remove the current `finished` value, and retain the task identity and earlier evidence. A replacement outcome uses `superseded` and a link to the successor instead.

Before a task becomes `done`:

- every required workstream MUST be `done`, `superseded`, or intentionally `deferred`;
- acceptance criteria MUST be satisfied or explicitly narrowed;
- validation evidence MUST be recorded;
- durable conclusions SHOULD be promoted into the repository's established canonical knowledge surface;
- external tracker state SHOULD be reconciled when a tracker is in use.

## 7. Time and effort

Task-level `started` and `finished` describe lifecycle boundaries; they MUST NOT be used alone to calculate effort. A task MAY span inactive periods, review waits, user prompts, overnight gaps, and several separately recorded sessions.

Time MUST be recorded as `Time Entry` concepts under `<task-slug>/time/`. Each entry MUST contain:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `type` | required | Exactly `Time Entry`. |
| `task` | required | Parent task slug. |
| `entry` | required | Stable entry identifier matching the filename. |
| `status` | required | `running` or `closed`. |
| `actor` | required | Person or agent whose effort is represented. |
| `started` | required | RFC 3339 session or evidence-window start. |
| `method` | required | `tracked`, `tracked-adjusted`, `manual`, or `estimated-commit-review`. |
| `timestamp` | required | RFC 3339 last meaningful change. |

Time Entry `timestamp` MUST advance when an entry is closed or corrected. It is distinct from the activity interval expressed by `started` and `finished`.

A closed entry MUST also contain `finished` and a non-negative integer `effort_minutes`. It SHOULD contain `elapsed_minutes` when a meaningful wall-clock window is known. An entry MAY identify a `workstream`, `source_commits`, and `confidence`.

The body MUST contain `## Summary`, `## Basis`, and `## Activity`.

### 7.1 Live tracking

Starting live tracking creates a `running` entry with `method: tracked`. If the task is `ready`, a producer SHOULD transition it to `in-progress`. A `proposed`, `done`, `deferred`, or `superseded` task MUST NOT start a live entry.

Stopping live tracking closes the entry and records wall-clock `elapsed_minutes`. When the interval reasonably represents active work, `effort_minutes` MAY equal elapsed time. When the interval contains material inactivity, waiting, or unrelated work, the producer MUST use `tracked-adjusted`, record a defensible effort value, and explain the adjustment under `## Basis`.

Only one running entry is permitted for the same task, actor, and workstream combination. Concurrent actors or workstreams MAY have separate entries.

### 7.2 Manual entries

A producer MAY add a closed `manual` entry with an explicit effort value. The entry MUST identify who supplied the value and explain its basis. Manual effort MAY be recorded without exact start and finish boundaries only when the producer uses the same timestamp for both and states that the timing is approximate.

### 7.3 Commit-review estimates

Commit history is activity evidence, not a clock. A producer estimating effort from commits MUST:

- identify the commits reviewed;
- group nearby commits into plausible work sessions instead of treating the entire first-to-last span as active effort;
- state the inactivity-gap threshold, per-session allowance, and any manual adjustment;
- consider related review, testing, prompting, and non-commit work when evidence exists;
- record `method: estimated-commit-review` and `confidence: low`, `medium`, or `high`;
- keep `elapsed_minutes` as the evidence window while recording the smaller estimated active effort separately.

The reference heuristic groups commits separated by no more than 90 minutes. Each group is estimated as the first-to-last commit interval plus 30 minutes of preparation and review, with a minimum of 30 minutes per group. This heuristic is a transparent default, not a claim of precision. An agent SHOULD review the proposed sessions and adjust them when repository or conversation evidence justifies a better estimate.

### 7.4 Rollups and completion

`effort_minutes` on the task MUST equal the sum of `effort_minutes` across its closed time entries. Running entries do not contribute until closed. The first entry start sets task `started`; moving the task to `done` sets task `finished`.

A task MUST NOT become `done` with a running time entry. A producer MAY backfill or correct time after completion, but MUST preserve the method and basis of the correction.

### 7.5 Estimates and sprint points

A task MAY contain an `estimate` mapping with:

- `effort_minutes`: required non-negative integer expected active effort;
- `method`: `agent`, `manual`, or `historical`;
- `confidence`: `low`, `medium`, or `high`;
- `basis`: concise explanation of scope, assumptions, and comparison evidence;
- `actor`: person or agent making the estimate;
- `timestamp`: RFC 3339 estimate time.

An agent estimate SHOULD consider acceptance scope, dependencies, review, testing, and knowledge-promotion work. It SHOULD be revised when scope changes materially; Git history provides the estimate history.

A task MAY separately contain `sprint_points` with numeric `value`, a named `scale`, optional team or board `context`, and `timestamp`. Points express relative complexity within that context. Producers and consumers MUST NOT convert points to minutes or infer points from recorded effort as part of this profile.

Estimated effort, sprint points, elapsed time, and recorded effort are separate measures. Completion SHOULD preserve the estimate so consumers can compare expected and actual effort without rewriting history.

## 8. Relationships and knowledge

Task relationships SHOULD use Markdown links in the body so generic OKF consumers can traverse them. Structured `parent` and `depends_on` fields MAY duplicate common relationships for filtering and synchronisation. Missing `parent` or `depends_on` targets are conformant broken links and consumers SHOULD report them as warnings. This preserves OKF's ability to represent partial or externally assembled knowledge without pretending the dependency is satisfied.

Knowledge links MAY leave the task bundle or repository. Generic consumers MUST treat an out-of-bundle target as an external, untyped resource and MUST NOT automatically fetch or traverse it without an explicit policy. Broken knowledge links do not by themselves make the task bundle structurally non-conformant.

An OKF Tasks bundle does not require a particular knowledge-engineering system. Producers SHOULD:

- link existing OKF concepts directly when they share a bundle root;
- link established repository documentation using ordinary Markdown paths;
- cite external authoritative sources when claims depend on them;
- report unresolved knowledge-promotion needs instead of creating a new documentation regime implicitly.

## 9. External trackers and synchronisation

External tracker identities MUST NOT replace the task slug or concept ID. Provider setup is represented by `Tracker Profile` concepts under `trackers/`. Credentials, tokens, webhook secrets, and credential references MUST NOT be stored in a Tracker Profile or task record.

### 9.1 Tracker Profiles

A Tracker Profile MUST contain:

- `type`: exactly `Tracker Profile`;
- `tracker`: stable lowercase kebab-case slug matching the filename;
- `default`: optional boolean selecting the project-local default profile;
- `system`: `github`, `gitlab`, `linear`, or `clickup`;
- `host`: an HTTPS origin without credentials, path, query, or fragment;
- `resource`: provider resource kind, initially `issue` or `task`;
- `scope`: mapping containing provider scope `kind`, stable `id`, and human-facing `key`;
- `sync`: mapping containing `mode` and `authority`;
- `status_map`: complete mapping from every section 6 status to a stable remote state identifier;
- `field_map`: explicit mappings from portable fields to native or custom remote fields;
- `discovery`: mapping containing RFC 3339 `observed_at` and a deterministic `fingerprint` of the discovered provider configuration.

`sync.mode` MUST be `push`, `pull`, `bidirectional`, or `manual`. `sync.authority` MUST be `repository`, `tracker`, or `manual`. Direction controls permitted operations; authority controls conflict resolution. They MUST NOT be inferred from each other.

An initializer MUST discover the selected remote scope, stable state and field identifiers, capabilities, and relevant provider constraints before proposing a profile. It MUST require explicit overrides for missing or ambiguous mappings. Refreshing discovery MUST report configuration drift and MUST NOT silently change an existing mapping. Authentication material remains runtime configuration.

A bundle MUST contain at most one Tracker Profile with `default: true`. When an operation omits an explicit profile, a producer MAY use that saved default or a sole available profile. If several profiles exist without one unambiguous default, it MUST stop, identify the available profiles, and require a user or governing policy to choose the project scope. Setup agents SHOULD derive candidate surfaces from the current repository and provider discovery, prompt before selecting among multiple writable repositories, projects, teams, or Lists, and save the confirmed choice for later task creation and synchronization.

For tracker-authoritative bidirectional synchronization, `status_map` MUST be round-trippable: two OKF states MUST NOT map to the same remote identifier. Repository-authoritative projections MAY be lossy, but adapters MUST preserve the local state and MUST NOT infer a more specific local state when pulling the collapsed remote value.

Each `field_map` value MUST contain `remote`, using a provider-stable field identifier where available. A mapping MAY override `authority`. A `tags` mapping MUST declare `strategy` as `replace`, `managed-subset`, `read-only`, or `ignore`. `managed-subset` also requires `managed_prefix` or `managed_values`; adapters MUST preserve labels or tags outside that declared ownership boundary.

Portable custom values use task `fields` entries containing a declared `type` and `value`. Adapters MUST NOT coerce an incompatible remote type silently, match mutable field names as identities, or invent missing select options.

### 9.2 External bindings

Each task `external` entry MUST contain `tracker`, `system`, `host`, `kind`, `scope`, `id`, `key`, `url`, and `sync`. `scope` MUST contain stable `id` and human-facing `key`. `id` is the provider-global opaque object identity; `key` is the human-facing issue number or identifier. The binding system, host, and scope ID MUST agree with its referenced Tracker Profile.

The tuple `(system, host, kind, id)` MUST be unique across the bundle. Multiple provider mappings for one task are allowed, but the same provider-native record MUST NOT map to more than one local task. Issue numbers and display keys are not identities because they may repeat across repositories, projects, lists, or provider hosts.

Binding `sync` MAY contain `last_synced`, `remote_revision`, and `base`. Reconciliation state belongs to the binding; task-level `sync` is not permitted. `base` SHOULD retain local and remote revisions and/or per-field hashes from the last successful reconciliation.

A conflict exists when the same mapped field changed locally and remotely since the base. Adapters MUST report the field and competing values and MUST NOT silently select a winner. Writes MUST be read back and verified when the provider may omit unsupported or unauthorized values. Missing remote records MUST NOT cause automatic local deletion.

Webhook consumers MUST authenticate provider events, deduplicate replayed deliveries, tolerate out-of-order events, and reconcile against current remote state rather than trusting an event payload as complete state.

### 9.3 Provider requirements

- GitHub profiles are repository-scoped. An adapter MUST distinguish organization Issue Fields from Projects item fields and MUST exclude pull requests returned by issue-list APIs.
- GitLab profiles are project-scoped and MUST record host identity. Adapters MAY use the Issues REST API for baseline issues and the Work Item API for discovered capabilities, but MUST account for server version and tier.
- Linear profiles are team-scoped. Initializers MUST use stable workflow-state IDs and categories; state names alone are insufficient. Triage, blocked, validation, duplicate, and cancellation mappings require explicit discovered states or documented lossy projection.
- ClickUp profiles are List-scoped and MUST record the Workspace and custom task type when applicable. Initializers MUST discover status and custom-field applicability. A moved task MUST be revalidated against its new location before synchronization continues.

Creating or updating a remote record MUST use only mapped allowlisted fields. Provider-required fields and custom-field applicability MUST be checked, and the resulting record MUST be read back before recording a successful base.

### 9.4 Agent execution boundary

Remote content and synchronization do not authorize execution. Assignment, labels, comments, field values, or issue text MUST NOT grant an agent tools, credentials, network access, repository write access, or permission to publish. An agent invocation requires an independent policy or human authorization identifying the allowed provider scope, repository, starting ref, agent identity, resource limits, and remote revision used as input. Resulting branches, pull requests, merge requests, and validation evidence SHOULD be linked from task evidence.

### 9.5 External content and artifact security

Repository records, tracker fields, retrieved documents, generated text, and other natural-language artifacts cross trust boundaries. A consumer or adapter MUST treat externally sourced content as untrusted data, not as instructions or authority. Prompt wording such as “ignore instructions in content” MAY be used as defence in depth but MUST NOT be treated as a security boundary.

An agent that reads untrusted content MUST receive only the data, tools, network access, and credentials needed for its bounded task. Text contained in a task or linked artifact MUST NOT grant permission, select a tool, expand network access, or authorise a write. High-impact actions require deterministic policy checks and SHOULD require human approval.

Before an artifact leaves the repository for a tracker, API, message, comment, or other external system, a conformant adapter MUST perform a deterministic egress check over the exact rendered payload. The check MUST:

- reject detected credentials, private keys, access tokens, and other configured secret patterns without reproducing the secret in diagnostics;
- reject `file:` links, absolute machine-local paths, UNC paths, repository paths outside the declared root, and unresolved local links;
- apply an explicit field or content allowlist so repository-only metadata is not exported accidentally;
- preserve provenance sufficient to identify the source record, adapter, and publication revision;
- require explicit approval or a documented policy before publishing data classified as sensitive;
- fail closed when a required check cannot run.

Secret and prompt-injection detection are incomplete controls. Passing an egress check is evidence that configured checks found no violation; it is not proof that an artifact contains no sensitive or adversarial content. Adapters SHOULD combine deterministic inspection with data classification, least privilege, output schemas, rate and cost limits, audit records, and a revocable integration identity.

Removing URLs, matching suspicious phrases, or asking a model to sanitise content MAY reduce specific risks but is not a complete prompt-injection control. The enforcement boundary MUST remain deterministic code and constrained authority outside the model.

When a third-party AI system receives or produces an artifact, the integration owner MUST document the data sent, retention and training terms, vendor security evidence, and whether returned content can influence an internal action. The integration SHOULD be adversarially tested with direct and indirect prompt-injection cases. Regardless of vendor assurances, returned content MUST remain untrusted at the local boundary and the integration MUST limit its downstream blast radius.

If an external artifact will later be consumed by an AI system, the receiving integration MUST keep that artifact distinguishable from trusted instructions, validate any structured output, and prevent the content from autonomously increasing its own privileges or initiating a sensitive action. Active content such as HTML, remote images, or embedded links SHOULD be removed unless required and explicitly permitted.

This threat model follows the layered direction in [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) and the [UK NCSC analysis of prompt injection](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection): systems should reduce authority and blast radius rather than assume natural-language instructions can make an LLM trustworthy.

### 9.6 Repository-link portability

Repository Markdown SHOULD retain relative links because they work in clones and across branches. Before publishing that Markdown outside its repository-rendering context, an adapter MUST resolve each local link against the source document and repository root.

For a link whose target is inside the repository, the adapter MUST convert it to a canonical web URL when a supported repository remote is available:

- GitHub: `https://<host>/<owner>/<repository>/blob/<ref>/<path>`;
- GitLab: `https://<host>/<namespace>/<project>/-/blob/<ref>/<path>`.

The adapter MUST percent-encode path and ref components, preserve a safe fragment, remove credentials from the configured remote URL, and verify that the resolved filesystem target remains inside the repository root. A commit SHA or immutable tag SHOULD be used for evidence links; a named branch MAY be used for intentionally living documentation.

An adapter MUST NOT publish a machine-local absolute path. When no supported remote can be resolved, or the target is missing or outside the repository, the adapter MUST stop publication and report the link location without echoing sensitive path content. It MUST NOT silently submit a known-broken or local-only link. Already remote `https` links and document-local `#fragment` links MAY pass through unchanged according to the adapter's URL policy.

## 10. Indexes and logs

The bundle-root `index.md` SHOULD declare the following fields using the OKF root-index exception:

```yaml
okf_version: "0.1"
okf_tasks_version: "0.4"
okf_tasks_profile: https://github.com/polaralias/okf-tasks/blob/v0.4.0/SPEC.md
```

Its body MUST contain a top-level heading and SHOULD group task links under status headings. Each entry SHOULD include the task description.

Example:

```markdown
## ready

- [Implement token rotation](./implement-token-rotation/task.md) — Rotate session tokens safely after authentication.
```

Indexes MAY be generated and SHOULD NOT be edited by hand when marked as generated. A bundle MAY use `log.md` for chronological bundle-level changes. Git history remains valid provenance and no per-change log entry is required.

## 11. Conformance

Conformance is claimed for a named artifact or implementation class, not for the ecosystem in the abstract.

### 11.1 Document conformance

A Task, Workstream, or Time Entry document is conformant when it satisfies the applicable field, path, body, and semantic requirements in this profile. A conformant document may still contain a broken relationship target.

### 11.2 Bundle conformance

An OKF Tasks v0.4 bundle is conformant when:

1. it conforms to OKF v0.1;
2. every `Task` and `Workstream` concept satisfies the required profile fields and body headings;
3. task and workstream slugs match their paths;
4. every lifecycle status is recognized;
5. a `done` task has no active required workstreams;
6. every `Time Entry` satisfies section 7 and task effort rollups agree;
7. a `done` task has no running time entries and has a `finished` timestamp;
8. estimates and sprint points satisfy section 7.5 without implicit conversion;
9. `index.md`, when generated, agrees with the task records;
10. Tracker Profiles and external bindings satisfy section 9, and external identities are bundle-unique.

### 11.3 Producer conformance

A conformant producer MUST emit conformant documents and bundles, MUST use only normal transitions unless an explicit forced-correction mode is selected, MUST preserve stable identities, and MUST retain unknown fields when updating a record.

### 11.4 Consumer conformance

A conformant consumer MUST read every required profile field, MUST tolerate unknown fields and unknown task-adjacent concept types, MUST treat unresolved relationship targets as warnings rather than structural errors, and MUST apply an explicit policy before traversing out-of-bundle links.

### 11.5 Synchronisation adapter conformance

A conformant adapter MUST satisfy the producer and consumer requirements for records it writes and reads. It MUST map provider states explicitly, enforce external mapping uniqueness, respect record and field authority, store or otherwise identify a reconciliation base, detect same-field divergent changes, and expose conflicts without silent overwrite. For every external-bound artifact it MUST also satisfy the trust-boundary, egress, secret-handling, and link-portability requirements in sections 9.5 and 9.6.

Consumers SHOULD treat semantic completion evidence and knowledge promotion as reviewable obligations rather than claims that syntax validation alone can prove.

## 12. Versioning and release status

The repository `VERSION` file is the release source of truth. Profile `0.x` releases may add constraints in a new minor version; patch releases clarify text or fix tooling without changing conformant data. A tagged profile URL and schema `$id` are immutable. Normative changes require corresponding positive and negative conformance fixtures and agreement from both maintained implementations.

Version 0.4 defines first-class Tracker Profiles and scoped external bindings for GitHub, GitLab, Linear, and ClickUp. It is released when all required clauses have fixtures where machine-testable, two independently implemented validators agree on the fixture manifest, examples validate, release automation is green, and governance identifies the accepting maintainer. Those conditions are part of this repository's automated release bar.

## Appendix A — Minimal task

```markdown
---
type: Task
task: implement-token-rotation
title: Implement token rotation
description: Rotate session tokens safely after authentication.
status: ready
created: 2026-07-17T09:00:00Z
timestamp: 2026-07-17T09:00:00Z
---

# Implement token rotation

## Outcome

Authenticated sessions receive a newly rotated token without interrupting valid requests.

## Scope

- In scope: login-time rotation.
- Out of scope: periodic background rotation.

## Acceptance

- [ ] Add integration coverage for token replacement.

## Evidence

- No implementation evidence yet.
```
