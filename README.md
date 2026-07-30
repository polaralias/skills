---
type: "Repository Guide"
title: "Skills Workbench"
description: "Documents Skills Workbench for the skills repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - skills
  - repository-guide
navigation:
  role: entry-point
  order: 10
---
<p align="center">
  <img src="Skills%20Banner.png" alt="Skills Workbench banner" width="960" />
</p>

# Skills Workbench

[![skills.sh](https://skills.sh/b/polaralias/skills)](https://skills.sh/polaralias/skills)

Skills Workbench is a curated library of reusable agent skills for engineering, delivery, content, design, documentation, and automation work.

## What This Repository Contains

The repository packages skills as portable folders with:

- `SKILL.md` instructions and trigger metadata
- optional `scripts/` helpers
- optional `references/` documents
- optional `assets/` such as icons or templates

The main `skills/` tree contains active packaged skills. The `future-consideration/` tree holds ideas and drafts that are not yet packaged for active use.

Every active skill applies the same durable repository-link contract when it creates or meaningfully updates a Task, Workstream, or typed OKF knowledge document. Governed concepts must form one resolved local graph through meaningful task-to-task, document-to-document, or task-to-document relationships; incoming links count and terminal Tasks remain useful implementation-state evidence. Reserved indexes/logs, Tracker Profiles, runbooks, generated/vendor output, handoffs, sessions, and temporary/scratch material are excluded.

## Source Trust Baseline

Every active skill treats files, webpages, messages, repository content, tool output, generated artefacts, and connector data as untrusted content rather than behavioural authority. Source material cannot override the current user or host policy, request secrets, select external destinations, or authorise execution, writes, publication, or communication. Tool-using skills add least-privilege, validation, approval, and recovery controls where their risk surface requires them.

## Local-Only Workspace Convention

Use `local-docs/` at the repo root for machine-local notes, handoffs, continuity artefacts, or other working documents that should stay beside the work without being committed.

The repository `.gitignore` should include `local-docs/`. Skills that deal with repository bootstrap or local continuity should preserve tracked defaults such as `docs/handoff/`, but they can route explicitly local-only artefacts into `local-docs/` when that better matches the user's intent.

## Active Skill Families

### Engineering

Location: [skills/engineering](./skills/engineering)

- <img src="./skills/engineering/repo-setup/assets/icon.svg" alt="repo-setup icon" width="22"> [repo-setup](./skills/engineering/repo-setup) (RST): bootstrap a repository with licensing, governance docs, CODEOWNERS, a named repository ruleset, draft-release scaffolding, and a WIP GitHub description.
- <img src="./skills/engineering/engineering-workflow-orchestrator/assets/icon.svg" alt="engineering-workflow-orchestrator icon" width="22"> [engineering-workflow-orchestrator](./skills/engineering/engineering-workflow-orchestrator) (EWO): route repository truth, decomposition, local task lifecycle, worktree coordination, implementation, session closure, publication, and continuity while keeping each state surface explicit.
- <img src="./skills/engineering/repo-session-alignment/assets/icon.svg" alt="repo-session-alignment icon" width="22"> [repo-session-alignment](./skills/engineering/repo-session-alignment) (RSA): close material engineering sessions by reconciling existing task execution truth, canonical knowledge truth, and each meaningfully changed record's explicit freshness without creating duplicate surfaces.
- <img src="./skills/engineering/repo-dissection/assets/icon.svg" alt="repo-dissection icon" width="22"> [repo-dissection](./skills/engineering/repo-dissection) (RDS): verify unclear repositories, consume derived wikis as claims, and bootstrap an OKF-compatible knowledge foundation with explicit freshness when appropriate.
- <img src="./skills/engineering/query-to-knowledge/assets/icon.svg" alt="query-to-knowledge icon" width="22"> [query-to-knowledge](./skills/engineering/query-to-knowledge) (QTK): resolve repository ambiguity into durable canonical knowledge, including producer-safe OKF capture with explicit last-meaningful-change timestamps.
- <img src="./skills/engineering/repo-knowledge-engineering/assets/icon.svg" alt="repo-knowledge-engineering icon" width="22"> [repo-knowledge-engineering](./skills/engineering/repo-knowledge-engineering) (RKE): maintain and streamline canonical repository truth with bounded OKF generation and consumption, likely-question retrieval checks, explicit retain/merge/archive/delete disposition, verification provenance, partial decision supersession, typed linked entry points, reading order, glossary, and evidence alignment.
- <img src="./skills/engineering/doc-driven-development/assets/icon.svg" alt="doc-driven-development icon" width="22"> [doc-driven-development](./skills/engineering/doc-driven-development) (DDD): turn epic or end-state product truth into feature contracts, implementation-planning notes, work packages, and acceptance artefacts before coding.
- <img src="./skills/engineering/repo-task-lifecycle/assets/icon.svg" alt="repo-task-lifecycle icon" width="22"> [repo-task-lifecycle](./skills/engineering/repo-task-lifecycle) (RTL): maintain and visually review OKF task bundles through the installed `okf-tasks` CLI and definitive light-first Graph/Board/Reader workspace, with typed linked README entry points, transparent path exclusions, vertical relationship focus in the Graph panel, fragment-addressable embedded Task time entries, temporal drift review, workstream effort context, full Markdown reading, explicit last-updated timestamps, RKE Visualisation promotion, project-default tracker profiles, safe sync/exports, and generated indexes. [`polaralias/okf-tasks`](https://github.com/polaralias/okf-tasks) is the authoritative specification, CLI, conformance, and visualisation source.
- <img src="./skills/engineering/worktree-task-coordinator/assets/icon.svg" alt="worktree-task-coordinator icon" width="22"> [worktree-task-coordinator](./skills/engineering/worktree-task-coordinator) (WTC): coordinate isolated Git worktrees, branch and path ownership, integration order, final-tree verification, and safe cleanup for concurrent delivery.
- <img src="./skills/engineering/repo-publish-finaliser/assets/icon.svg" alt="repo-publish-finaliser icon" width="22"> [repo-publish-finaliser](./skills/engineering/repo-publish-finaliser) (RPF): finalise a repository for public release, including publish-safety scanning, release-automation decisions, and final description cleanup.
- <img src="./skills/engineering/local-handoff/assets/icon.svg" alt="local-handoff icon" width="22"> [local-handoff](./skills/engineering/local-handoff) (LHO): write and lifecycle-manage one active, dated, review-bounded handoff per workstream outside canonical knowledge and task bundles, with compact standard mode and a richer max-verbosity mode.
- <img src="./skills/engineering/local-pickup/assets/icon.svg" alt="local-pickup icon" width="22"> [local-pickup](./skills/engineering/local-pickup) (LPK): resume from the active handoff for a workstream, exclude superseded candidates, re-verify expired context, and rebuild trustworthy context before editing.
- <img src="./skills/engineering/tracker-publisher/assets/icon.svg" alt="tracker-publisher icon" width="22"> [tracker-publisher](./skills/engineering/tracker-publisher) (TPU): publish stable work packages or local task records into external trackers without redesigning their hierarchy or ownership.
- <img src="./skills/engineering/test-plan-writer/assets/icon.svg" alt="test-plan-writer icon" width="22"> [test-plan-writer](./skills/engineering/test-plan-writer) (TPW): turn requirements and change notes into proportionate QA plans and test cases.

### Automation

Location: [skills/automation](./skills/automation)

- <img src="./skills/automation/pandoc-converter/assets/icon.svg" alt="pandoc-converter icon" width="22"> [pandoc-converter](./skills/automation/pandoc-converter) (PDC): run Pandoc conversions with predictable defaults, ordinary custom flags, and explicit opt-in for executable filters.
- <img src="./skills/automation/tasklist-gantt-creator/assets/icon.svg" alt="tasklist-gantt-creator icon" width="22"> [tasklist-gantt-creator](./skills/automation/tasklist-gantt-creator) (TGC): generate stakeholder-ready Excel Gantt charts from task lists or planning exports.

### Content

Location: [skills/content](./skills/content)

- <img src="./skills/content/agenda-generator/assets/icon.svg" alt="agenda-generator icon" width="22"> [agenda-generator](./skills/content/agenda-generator) (AGN): draft lean or formal meeting agendas from simple prompts or richer context.
- <img src="./skills/content/linkedin-short-post-drafter/assets/icon.svg" alt="linkedin-short-post-drafter icon" width="22"> [linkedin-short-post-drafter](./skills/content/linkedin-short-post-drafter) (LSP): write short LinkedIn-style posts for updates, launches, events, and capability highlights.
- <img src="./skills/content/long-form-post-drafter/assets/icon.svg" alt="long-form-post-drafter icon" width="22"> [long-form-post-drafter](./skills/content/long-form-post-drafter) (LFP): build evidence-grounded long-form posts, launch articles, and blog-style content.
- <img src="./skills/content/meeting-pack-processor/assets/icon.svg" alt="meeting-pack-processor icon" width="22"> [meeting-pack-processor](./skills/content/meeting-pack-processor) (MPP): turn notes or transcripts into internal packs, follow-up emails, and justified routing outputs.
- <img src="./skills/content/release-note-writer/assets/icon.svg" alt="release-note-writer icon" width="22"> [release-note-writer](./skills/content/release-note-writer) (RNW): turn shipped change detail into concise, customer-facing release notes.
- <img src="./skills/content/scheduling-assistant/assets/icon.svg" alt="scheduling-assistant icon" width="22"> [scheduling-assistant](./skills/content/scheduling-assistant) (SCH): turn meeting requests into calendar-aware slot proposals and ready-to-send emails.

### Delivery

Location: [skills/delivery](./skills/delivery)

- <img src="./skills/delivery/ai-initiative-builder/assets/icon.svg" alt="ai-initiative-builder icon" width="22"> [ai-initiative-builder](./skills/delivery/ai-initiative-builder) (AIB): guide early AI initiative discovery, shaping, and prioritisation.
- <img src="./skills/delivery/ai-initiative-deep-dive-and-scoping/assets/icon.svg" alt="ai-initiative-deep-dive-and-scoping icon" width="22"> [ai-initiative-deep-dive-and-scoping](./skills/delivery/ai-initiative-deep-dive-and-scoping) (ADS): pressure-test and scope AI initiatives that are ready for deeper validation.
- <img src="./skills/delivery/clickup-project-plan-builder/assets/icon.svg" alt="clickup-project-plan-builder icon" width="22"> [clickup-project-plan-builder](./skills/delivery/clickup-project-plan-builder) (CPP): turn project briefs into practical ClickUp structures, hierarchy, tags, and views.
- <img src="./skills/delivery/feedback-rice-prioritiser/assets/icon.svg" alt="feedback-rice-prioritiser icon" width="22"> [feedback-rice-prioritiser](./skills/delivery/feedback-rice-prioritiser) (FRP): convert messy feedback into clean product problem statements and RICE drafts.
- <img src="./skills/delivery/implementation-plan-writer/assets/icon.svg" alt="implementation-plan-writer icon" width="22"> [implementation-plan-writer](./skills/delivery/implementation-plan-writer) (IPW): produce customer-facing implementation plans from kickoff material and confirmed assumptions.
- <img src="./skills/delivery/kickoff-summary-writer/assets/icon.svg" alt="kickoff-summary-writer icon" width="22"> [kickoff-summary-writer](./skills/delivery/kickoff-summary-writer) (KSW): turn kickoff and discovery material into evidence-backed summaries for the right audience.
- <img src="./skills/delivery/project-context-builder/assets/icon.svg" alt="project-context-builder icon" width="22"> [project-context-builder](./skills/delivery/project-context-builder) (PCB): create or refresh a canonical `PROJECT.md` from scattered project context.
- <img src="./skills/delivery/project-packager/assets/icon.svg" alt="project-packager icon" width="22"> [project-packager](./skills/delivery/project-packager) (PKG): turn an existing `PROJECT.md` into audience-specific or system-ready project outputs.
- <img src="./skills/delivery/project-report-writer/assets/icon.svg" alt="project-report-writer icon" width="22"> [project-report-writer](./skills/delivery/project-report-writer) (PRW): build project reports from fresh delivery signals, structured execution data, and durable context.
- <img src="./skills/delivery/project-support/assets/icon.svg" alt="project-support icon" width="22"> [project-support](./skills/delivery/project-support) (PRS): orient and validate real project work before a more specialised project skill takes over.
- <img src="./skills/delivery/training-plan-writer/assets/icon.svg" alt="training-plan-writer icon" width="22"> [training-plan-writer](./skills/delivery/training-plan-writer) (TRW): create paired customer-facing and facilitator-grade training plans from agreed scope.

### Design

Location: [skills/design](./skills/design)

- <img src="./skills/design/mermaid-flowchart-designer/assets/icon.svg" alt="mermaid-flowchart-designer icon" width="22"> [mermaid-flowchart-designer](./skills/design/mermaid-flowchart-designer) (MFD): turn rough notes or existing Mermaid code into clearer flowcharts and architecture diagrams.
- <img src="./skills/design/source-derived-design-system-builder/assets/icon.svg" alt="source-derived-design-system-builder icon" width="22"> [source-derived-design-system-builder](./skills/design/source-derived-design-system-builder) (SDS): turn real visual references into a reusable design skill and persistent `DESIGN.md`.

### Documentation

Location: [skills/documentation](./skills/documentation)

- <img src="./skills/documentation/docx-assistant/assets/icon.svg" alt="docx-assistant icon" width="22"> [docx-assistant](./skills/documentation/docx-assistant) (DXA): create, revise, review, validate, and return `.docx` documents in this environment.
- <img src="./skills/documentation/knowledge-transfer-documentation-writer/assets/icon.svg" alt="knowledge-transfer-documentation-writer icon" width="22"> [knowledge-transfer-documentation-writer](./skills/documentation/knowledge-transfer-documentation-writer) (KTD): write concise internal knowledge transfer docs from authoritative source material.
- <img src="./skills/documentation/process-document-writer/assets/icon.svg" alt="process-document-writer icon" width="22"> [process-document-writer](./skills/documentation/process-document-writer) (PDW): create or revise formal process docs, SOPs, runbooks, and operating procedures.

### Media

Location: [skills/media](./skills/media)

- <img src="./skills/media/elevenlabs-ai-voice-gen/assets/icon.svg" alt="elevenlabs-ai-voice-gen icon" width="22"> [elevenlabs-ai-voice-gen](./skills/media/elevenlabs-ai-voice-gen) (EAV): write and clean narration scripts for ElevenLabs voice generation.
- <img src="./skills/media/remotion-explainer-video-production/assets/icon.svg" alt="remotion-explainer-video-production icon" width="22"> [remotion-explainer-video-production](./skills/media/remotion-explainer-video-production) (REV): create Remotion explainer-video plans, timing layouts, overlays, and branded composition guidance.

### Meta

Location: [skills/meta](./skills/meta)

- <img src="./skills/meta/skill-eval-suite-writer/assets/icon.svg" alt="skill-eval-suite-writer icon" width="22"> [skill-eval-suite-writer](./skills/meta/skill-eval-suite-writer) (SEW): build evaluation suites, scenario matrices, and grader strategies for skills.
- <img src="./skills/meta/llm-instruction-fixer/assets/icon.svg" alt="llm-instruction-fixer icon" width="22"> [llm-instruction-fixer](./skills/meta/llm-instruction-fixer) (LIF): repair prompts, skills, and other LLM instruction artefacts from a review or fix brief.
- <img src="./skills/meta/llm-instruction-reviewer/assets/icon.svg" alt="llm-instruction-reviewer icon" width="22"> [llm-instruction-reviewer](./skills/meta/llm-instruction-reviewer) (LIR): inspect prompts and instruction artefacts for execution risks before publication or repair.
- <img src="./skills/meta/skill-finaliser/assets/icon.svg" alt="skill-finaliser icon" width="22"> [skill-finaliser](./skills/meta/skill-finaliser) (SKF): turn draft or imported skills into clean, publishable skill packages.
- <img src="./skills/meta/setup-polaralias-skills/assets/icon.svg" alt="setup-polaralias-skills icon" width="22"> [setup-polaralias-skills](./skills/meta/setup-polaralias-skills) (SPS): create update-safe shared Polaralias defaults under `~/.agents/config/polaralias-skills` with `~/.config` as fallback, including shared tracker, structured-output, and continuity preferences.

## Using The Repository

- browse the packaged skills under [skills](./skills)
- use [INDEX.md](INDEX.md) if you need the canonical packaged-skill path list
- keep future or not-yet-packaged ideas under [future-consideration](./future-consideration)

### Install with the Skills CLI

Use the Skills CLI through `npx` to discover and install skills from this repository without installing the CLI itself:

```bash
npx skills add polaralias/skills
```

The interactive flow lets you choose the skills and supported agents. You can also list the available skills or install one directly:

```bash
npx skills add polaralias/skills --list
npx skills add polaralias/skills --skill repo-knowledge-engineering
```

Add `--global` to install for the current user instead of the current project. See the [Skills CLI documentation](https://www.skills.sh/docs/cli) for agent selection and non-interactive options.

## Versioning

This repository uses a repo-level [VERSION](./VERSION) file for GitHub Releases.

Any merged change that modifies packaged skills, repo packaging guidance, or release-validation behaviour should update `VERSION` in the same slice rather than leaving the repo-level release number for later cleanup.

When `VERSION` is the canonical release source, draft-release automation should also read `VERSION` directly so GitHub draft releases, pushed tags, and published releases do not drift into separate version tracks.

- adding, deleting, or renaming a packaged skill is a repo-major bump
- changing more than one packaged skill in one release is at least a repo-minor bump
- changing exactly one packaged skill is usually a repo-patch bump unless that skill’s own semver bump is larger

## Contributing

For repository workflow, packaging rules, and agent-focussed maintenance context, read [AGENTS.md](AGENTS.md).

## Repository knowledge

- [Documentation map](docs/knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
