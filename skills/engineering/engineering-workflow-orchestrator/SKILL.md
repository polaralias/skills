---
name: engineering-workflow-orchestrator
description: Coordinate a repository engineering session across repo-dissection, repo-knowledge-engineering, doc-driven-development, query-to-knowledge, tracker-publisher, tdd, local-handoff, and local-pickup. Use when a user wants one top-level skill to classify the current workflow stage, route to the right downstream skill, keep the active stage explicit, or set up Codex and Claude Code hook scaffolding around compaction and resume. Shorthand EWO.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.2.0
  updated: '2026-06-02'
---

# engineering-workflow-orchestrator

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `engineering-workflow-orchestrator was used in this response.`

Use this skill to coordinate the engineering skill stack as one explicit workflow.

This skill does not replace the specialist skills.
It decides which one should take over next, keeps the current stage explicit, and can set up workflow-aware hook scaffolding for Codex and Claude Code when the user wants the session state preserved across compaction or resume.

When hook-aware continuity is requested, this skill may define a lightweight artifact flow in which:

- `PreCompact` preserves a durable thread artifact when the host exposes one
- a subagent or helper step derives a max-verbosity handoff plus a short restart supplement from that saved artifact and current repo state
- `PostCompact` consumes the saved supplement and routes the resumed session through `local-pickup` or the next downstream skill

Do not assume both hosts expose the same compaction lifecycle. Ground hook setup in the verified host documentation before describing a runnable flow.

Read [references/workflow-state-contract.md](./references/workflow-state-contract.md) before defining workflow-stage metadata.
Read [references/hook-support.md](./references/hook-support.md) before configuring hooks.

## Use This Instead Of

- Use `repo-dissection` when the repository truth is still unclear and the session mainly needs repository archaeology.
- Use `repo-knowledge-engineering` when the main job is shaping or aligning canonical repository truth.
- Use `doc-driven-development` when the upstream truth already exists and the main job is decomposition, implementation planning, and work-package shaping.
- Use `query-to-knowledge` when narrow contradictions or unresolved terminology need focused resolution.
- Use `tracker-publisher` when work packages are already strong enough and the remaining job is tracker publication.
- Use `local-handoff` or `local-pickup` directly when the user only wants a continuation artifact or resume pass.
- Use this skill when the user wants top-level workflow coordination, stage tracking, or hook-aware session continuity.

## Inputs

Use the strongest available context:

- the user goal for the current tranche
- current repository state
- canonical docs or reading-order docs
- any current handoff artifact
- whether the workflow should be hook-aware in Codex, Claude Code, or both
- whether shared Polaralias defaults exist and matter for downstream tracker publication

## Stage model

Keep the active workflow stage explicit.

Default stages:

- `repo-dissection`
- `repo-knowledge-engineering`
- `doc-driven-development`
- `query-to-knowledge`
- `tracker-publisher`
- `tdd`
- `repo-knowledge-engineering-close`
- `local-handoff`

Do not force every stage into every session.
Skip stages that are unnecessary for the current slice.

## Workflow

### 1. Classify the current stage

- Read the repo reading order first.
- Decide whether the current slice is:
  - unclear repository archaeology
  - documentation-foundation work
  - feature decomposition and implementation planning
  - narrow clarification
  - tracker publication
  - implementation
  - post-implementation truth alignment
  - pause or resume
- State the chosen stage plainly.

### 2. Confirm the next skill

Route to the narrowest viable downstream skill:

- unclear repository truth -> `repo-dissection`
- canonical truth or alignment work -> `repo-knowledge-engineering`
- decomposition or implementation planning -> `doc-driven-development`
- narrow contradiction or missing decision -> `query-to-knowledge`
- publication into GitHub, Linear, or local tasks -> `tracker-publisher`
- behavior-changing implementation -> `tdd`
- pause -> `local-handoff`
- resume -> `local-pickup`

If the user wants a coordinated session rather than an immediate handoff, keep the workflow summary explicit and then continue with the chosen downstream skill.

### 3. Maintain workflow-state metadata

When the session spans several stages, define or update a lightweight workflow-state record using the contract in `references/workflow-state-contract.md`.

At minimum capture:

- current stage
- current skill
- next skill
- canonical references
- verification state

If a local handoff will be written later, keep this metadata consistent with the handoff.

### 4. Set up hook scaffolding when useful

When the user wants compaction-aware or resume-aware continuity:

- prefer project-local hook config
- use Codex project hooks under `.codex/hooks.json` or the equivalent inline Codex config surface
- use Claude Code project hooks under `.claude/settings.json`
- keep hooks lightweight and stage-aware
- use hooks to surface workflow-state and handoff expectations
- do not claim the hooks directly execute a skill body unless the host platform truly supports that

For richer continuity, prefer a deterministic artifact contract over a vague reminder-only hook flow when the host documents the required compaction events.

- `PreCompact` should:
  - save a raw transcript or equivalent durable thread artifact when the host makes that available
  - pass the saved artifact path, project root, and target handoff path into a helper or subagent step
  - produce a max-verbosity handoff and a short restart supplement
  - write a machine-readable manifest that `PostCompact` can consume without searching heuristically
- `PostCompact` should:
  - read the manifest or equivalent deterministic output
  - consume the short restart supplement rather than the full verbose handoff body
  - restore workflow-stage context and route the resumed session through `local-pickup` or the next downstream skill

Treat the raw saved transcript as the authority record, and the verbose handoff as a derived continuation artifact.

If the host does not document stable `PreCompact` and `PostCompact` hooks, do not invent a compaction-aware implementation. Fall back to the thinner `SessionStart` or manual-handoff pattern and say the richer flow is not currently grounded for that host.

Use hooks to reinforce the workflow, for example:

- `SessionStart`: surface active workflow-state and canonical references
- `PreCompact`: preserve the continuity artifacts or remind the session to refresh them before compaction
- `PostCompact`: consume the saved supplement, restate the saved workflow stage, and route the next step through `local-pickup` or the next downstream skill

### 5. Keep orchestration subordinate to truth

- Do not keep a stale stage label after the work changed direction.
- Do not let the orchestrator override stronger repository truth.
- If the workflow-state and canonical docs disagree, trust the strongest current evidence and update the workflow-state.
- If the hooks are installed but drift from the workflow contract, repair the hook config or disable it rather than leaving misleading automation behind.

### 6. Close the loop

At tranche end:

- route to `repo-knowledge-engineering` when canonical truth needs to be reconciled
- route to `local-handoff` when work is pausing
- keep the final workflow-state aligned with the handoff or the canonical docs

## Output shape

When using this skill, produce:

- the current workflow stage
- the next skill
- the reason that skill is the right next step
- any workflow-state fields that need updating
- any hook-install recommendation or hook drift found

## Guardrails

- This skill is an orchestrator, not a replacement for the specialist skill bodies.
- Do not invent extra stages when the existing stage model is enough.
- Do not use hooks as an excuse to skip `local-handoff` or `local-pickup`.
- Do not pretend native compaction and local workflow-state solve the same problem.
- Do not treat a derived verbose handoff as more authoritative than the saved raw transcript or current repo truth.
- Prefer a thin, legible workflow over a meta-layer that hides the real work.
