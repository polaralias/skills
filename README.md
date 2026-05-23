# Skills Workbench

[![skills.sh](https://skills.sh/b/polaralias/skills)](https://skills.sh/polaralias/skills)

A curated library of reusable agent skills for engineering, delivery, content, design, documentation, and automation work.

## Layout

There are two main areas:

- active skill families under [skills](./skills)
- future notes and not-yet-packaged ideas under [future-consideration](./future-consideration)

## Active Skill Families

### Engineering

Location: [skills/engineering](./skills/engineering)

- [repo-dissection](./skills/engineering/repo-dissection): dissect inherited or unclear repositories and turn assumptions into verified documented understanding.
- [query-to-knowledge](./skills/engineering/query-to-knowledge): resolve open repo questions into durable knowledge and canonical documentation.
- [repo-knowledge-engineering](./skills/engineering/repo-knowledge-engineering): keep the repository knowledge base aligned across canonical docs, plans, decisions, glossary, reading order, and validation evidence.
- [local-handoff](./skills/engineering/local-handoff): write a dated local handoff so the next session can resume safely.
- [local-pickup](./skills/engineering/local-pickup): resume from a local handoff and rebuild trustworthy context before editing.
- [test-plan-writer](./skills/engineering/test-plan-writer): turn requirements and change notes into proportionate QA plans and test cases.

### Automation

Location: [skills/automation](./skills/automation)

- [pandoc-converter](./skills/automation/pandoc-converter): run Pandoc conversions with predictable defaults while still allowing custom flags.
- [tasklist-gantt-creator](./skills/automation/tasklist-gantt-creator): generate stakeholder-ready Excel Gantt charts from task lists or planning exports.

### Content

Location: [skills/content](./skills/content)

- [agenda-generator](./skills/content/agenda-generator): draft lean or formal meeting agendas from simple prompts or richer context.
- [linkedin-short-post-drafter](./skills/content/linkedin-short-post-drafter): write short LinkedIn-style posts for updates, launches, events, and capability highlights.
- [long-form-post-drafter](./skills/content/long-form-post-drafter): build evidence-grounded long-form posts, launch articles, and blog-style content.
- [meeting-pack-processor](./skills/content/meeting-pack-processor): turn notes or transcripts into internal packs, follow-up emails, and justified routing outputs.
- [release-note-writer](./skills/content/release-note-writer): turn shipped change detail into concise, customer-facing release notes.
- [scheduling-assistant](./skills/content/scheduling-assistant): turn meeting requests into calendar-aware slot proposals and ready-to-send emails.

### Delivery

Location: [skills/delivery](./skills/delivery)

- [ai-initiative-builder](./skills/delivery/ai-initiative-builder): guide early AI initiative discovery, shaping, and prioritisation.
- [ai-initiative-deep-dive-and-scoping](./skills/delivery/ai-initiative-deep-dive-and-scoping): pressure-test and scope AI initiatives that are ready for deeper validation.
- [clickup-project-plan-builder](./skills/delivery/clickup-project-plan-builder): turn project briefs into practical ClickUp structures, hierarchy, tags, and views.
- [feedback-rice-prioritiser](./skills/delivery/feedback-rice-prioritiser): convert messy feedback into clean product problem statements and RICE drafts.
- [implementation-plan-writer](./skills/delivery/implementation-plan-writer): produce customer-facing implementation plans from kickoff material and confirmed assumptions.
- [kickoff-summary-writer](./skills/delivery/kickoff-summary-writer): turn kickoff and discovery material into evidence-backed summaries for the right audience.
- [project-context-builder](./skills/delivery/project-context-builder): create or refresh a canonical `PROJECT.md` from scattered project context.
- [project-packager](./skills/delivery/project-packager): turn an existing `PROJECT.md` into audience-specific or system-ready project outputs.
- [project-report-writer](./skills/delivery/project-report-writer): build project reports from fresh delivery signals, structured execution data, and durable context.
- [project-support](./skills/delivery/project-support): orient and validate real project work before a more specialized project skill takes over.
- [training-plan-writer](./skills/delivery/training-plan-writer): create paired customer-facing and facilitator-grade training plans from agreed scope.

### Design

Location: [skills/design](./skills/design)

- [mermaid-flowchart-designer](./skills/design/mermaid-flowchart-designer): turn rough notes or existing Mermaid code into clearer flowcharts and architecture diagrams.
- [source-derived-design-system-builder](./skills/design/source-derived-design-system-builder): turn real visual references into a reusable design skill and persistent `DESIGN.md`.

### Documentation

Location: [skills/documentation](./skills/documentation)

- [docx-assistant](./skills/documentation/docx-assistant): create, revise, review, validate, and return `.docx` documents in this environment.
- [knowledge-transfer-documentation-writer](./skills/documentation/knowledge-transfer-documentation-writer): write concise internal knowledge transfer docs from authoritative source material.
- [process-document-writer](./skills/documentation/process-document-writer): create or revise formal process docs, SOPs, runbooks, and operating procedures.

### Media

Location: [skills/media](./skills/media)

- [elevenlabs-ai-voice-gen](./skills/media/elevenlabs-ai-voice-gen): write and clean narration scripts for ElevenLabs voice generation.
- [remotion-explainer-video-production](./skills/media/remotion-explainer-video-production): create Remotion explainer-video plans, timing layouts, overlays, and branded composition guidance.

### Meta

Location: [skills/meta](./skills/meta)

- [skill-eval-suite-writer](./skills/meta/skill-eval-suite-writer): build evaluation suites, scenario matrices, and grader strategies for skills.
- [llm-instruction-fixer](./skills/meta/llm-instruction-fixer): repair prompts, skills, and other LLM instruction artifacts from a review or fix brief.
- [llm-instruction-reviewer](./skills/meta/llm-instruction-reviewer): inspect prompts and instruction artifacts for execution risks before publication or repair.
- [skill-finaliser](./skills/meta/skill-finaliser): turn draft or imported skills into clean, publishable skill packages.
- [setup-polaralias-skills](./skills/meta/setup-polaralias-skills): create update-safe shared Polaralias defaults under `~/.agents/config/polaralias-skills` with `~/.config` as fallback.

## Shared Skill Config

Skills that need durable cross-repo defaults should prefer user-level config outside the installed skill package.

Current convention for Polaralias shared defaults:

- preferred: `~/.agents/config/polaralias-skills/`
- fallback: `~/.config/polaralias-skills/`

This keeps `npx skills update` safe because persistent user customization does not live inside files that the installer may replace.

## Future Consideration

[future-consideration](./future-consideration) holds future-skill notes, rubrics, and idea fragments that are worth keeping but are not yet ready to package as active skills.

Use it for:

- future public skill ideas
- reusable methods that need a cleaner standalone package later
- notes that should not yet be promoted into the active `skills/` tree

## How `tdd` Fits In

I am not forking `tdd` here at the moment.

Use the upstream [`tdd` skill from mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) alongside the engineering family:

- use `repo-dissection` first when the codebase truth is unclear
- use `query-to-knowledge` when terms, decisions, or local behavior are still unresolved
- use `tdd` when doing behavior-changing implementation work
- use `repo-knowledge-engineering` to keep the repository knowledge base aligned in the same slice after implementation or validation work lands
- use `local-handoff` when pausing
- use `local-pickup` when resuming

## Recommended Flows

### Inherited unclear repo

`repo-dissection -> query-to-knowledge -> tdd -> repo-knowledge-engineering -> local-handoff`

### Resumed implementation tranche

`local-pickup -> tdd -> repo-knowledge-engineering -> local-handoff`

### Docs or support alignment pass

`local-pickup -> repo-knowledge-engineering -> local-handoff`

### Support-aware rule

Power-user local capability does not automatically equal repository-supported surface.
