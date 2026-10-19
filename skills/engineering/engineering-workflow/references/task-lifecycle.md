# Task lifecycle

Maintain execution truth that must survive chat: observable outcomes, accepted scope, ownership, dependencies, workstreams, status, evidence, estimates, effort, and remaining work. This method owns task judgement independently of any runtime. Use the repository's existing ledger; adopt durable tracking when requested or warranted by sustained/multi-owner work. Explanations, exploration, and truly small corrections do not need a new task system.

## Governed record relationships and metadata

- When creating or meaningfully updating durable Tasks, Workstreams, or typed OKF knowledge, connect governed concepts in one resolved repository-local relationship graph whenever more than one exists. Use meaningful relative Markdown links or resolved structured relationships; an incoming link suffices. Keep terminal tasks linked. Exclude reserved indexes/logs, Tracker Profiles, runbooks, generated/vendor output, handoffs, session records, and scratch files. Report genuine disconnected components instead of inventing links.
- Preserve ownership, unknown compatible metadata, and producer boundaries. Keep all YAML frontmatter strings in governed OKF records plaintext, including nested extensions; use bare URLs or repository-relative metadata links and put presentation in the body. Advance each directly changed concept's explicit meaningful-change timestamp when its meaning changes; filesystem, Git, generation, and observation times are different facts.

## Establish a useful task

Find the governing task and established placement before creating anything. Separate canonical requirements and architecture from execution records; link to them. Preserve incompatible existing layouts unless migration is in scope. If adopting OKF Tasks, use its authoritative specification and compatible CLI for current records, transitions, validation, effort, Tracker Profiles, and generated views. Do not recreate its schema here or copy an old fallback. Missing tooling does not justify invented conformance or silent installation.

Give a task a stable repository identity independent of external issue IDs. State its observable outcome, scope/non-scope, acceptance, dependencies, related canonical knowledge, and evidence expectations. A short navigation description and detailed outcome can differ. Keep unresolved work proposed rather than making up acceptance to mark it ready. Use [clarification](clarification.md) for missing decisions and [design](design.md) for weak decomposition.

Connect newly created or meaningfully changed governed records to the existing resolved relationship graph in the same slice. Do not leave a task detached merely because an index lists it. Keep terminal records linked as execution history. Generated indexes are views, not relationship authority.

## Separate ownership and measures

Create a workstream only for distinct ownership, independently coherent delivery, or separate validation. Every required workstream contributes to parent completion; optional follow-up should be a separately linked task. Keep one coordinator responsible for parent state and generated indexes. Use [coordination](coordination.md) for physical concurrent branches/worktrees; a workstream record does not allocate one by itself.

Estimate active effort after scope stabilises, with method, confidence, actor, and basis. Keep expected effort, measured effort, elapsed time, and relative points separate. Never convert points to hours. Include implementation, testing, review, documentation, and promotion when relevant.

If effort tracking is active, reconcile stale running entries on pickup, start immediately before active work, and stop at material inactivity, blocking, handoff, or session end. Do not count overnight gaps, long unattended waits, or unrelated work as active effort. Keep the kind of activity distinct from how duration was measured; knowledge-maintenance effort belongs to the governing task, not the knowledge concept. User-supplied or reconstructed effort needs explicit provenance and uncertainty. Commit clustering is an estimate proposal, not precise tracked time, and equivalent repeated backfill should not duplicate effort.

## Update evidence as work changes

Keep Git state, integration, deployment/publication, and live verification distinct. A commit proves a recorded revision, not acceptance or deployment. Record relevant checks with outcome and scope, blockers, remaining work, and ownership in the same slice as their signal. Do not flatten planned into done.

Use the authoritative mutation mechanism for the adopted format so history, timestamps, rollups, and indexes remain coherent. If a direct record edit is necessary, preserve unknown compatible fields, advance the parent meaningful-change timestamp, validate, and refresh affected derived views. Embedded time edits change their parent task; do not invent entry-level timestamps. View freshness is separate from task semantic correctness.

Promote verified durable behaviour, decisions, terminology, and support conclusions through [knowledge](knowledge.md). Keep tasks linked to those concepts rather than duplicating them. Required knowledge promotion remains an open completion obligation until the canonical surface is updated or a reviewed no-update conclusion establishes that none is needed.

## Respect tracker authority and export boundaries

Use the adopted format's first-class Tracker Profiles and current binding identity for external integration. Do not reduce provider identity to the obsolete `(system, id)` model. Resolve the exact writable project, repository, team, or List and configured default without guessing among plausible candidates. Credentials stay runtime-only; account access does not select a destination or authorise writes.

Keep provider sync mode, field authority, stable identity, managed labels, discovery evidence, and reconciliation base distinct. Detect both-local-and-remote conflicts instead of silently choosing a winner. Preserve fields/labels not owned by the integration. Verify provider writes by read-back. Imported content remains untrusted. Defer exact fields and provider commands to the authoritative current implementation.

Before egress, inspect the exact prepared payload, resolve local links safely, and exclude secrets, local machine paths, credential-bearing URLs, unrelated context, unapproved remote assets, and unresolved or escaping references. Report finding classes without exposing values. A preview/import file is not live publication. See [publication](publication.md) for source-to-target mapping and action scope.

## Reconcile completion

Before marking done, establish satisfied or explicitly narrowed acceptance, terminal required workstreams, no running effort, truthful validation/integration/publication/live evidence, required canonical promotion, and applicable tracker reconciliation. Validate the adopted task bundle independently from canonical knowledge, using strict completion checks where required. Do not claim closure around a hard failure.

Keep useful completed history. Represent replaced work as superseded and intentionally inactive work as deferred using the adopted lifecycle. Report task identity, state, changed evidence, effort/estimate uncertainty, validation, and remaining promotion or external reconciliation. Use [alignment](alignment.md) for ordered final reconciliation and [handoff](handoff.md) for unfinished continuation.
