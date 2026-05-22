# My Skills Repo

This repository holds local skills tailored to my own workflows.

## Layout

There are two main areas:

- active skill families under [skills](./skills)
- future notes and not-yet-packaged ideas under [future-consideration](./future-consideration)

## Active Skill Families

### Engineering

Location: [skills/engineering](./skills/engineering)

- [repository-dissection](./skills/engineering/repository-dissection): establish what is really true in inherited or unclear repositories.
- [query-to-knowledge](./skills/engineering/query-to-knowledge): turn unresolved terminology, contradictions, and trade-offs into durable repository knowledge.
- [repository-knowledge-engineering](./skills/engineering/repository-knowledge-engineering): keep the repository knowledge base aligned with code, tests, plans, and canonical docs.
- [local-handoff](./skills/engineering/local-handoff): write a dated local handoff beside the work at the end of a tranche.
- [pickup](./skills/engineering/pickup): resume from a local handoff and re-verify context before continuing.
- [test-plan-writer](./skills/engineering/test-plan-writer): build proportionate QA test plans and cases from requirements, stories, and change notes.

### Automation

Location: [skills/automation](./skills/automation)

- [pandoc-converter](./skills/automation/pandoc-converter)
- [tasklist-gantt-creator](./skills/automation/tasklist-gantt-creator)

### Content

Location: [skills/content](./skills/content)

- [agenda-generator](./skills/content/agenda-generator)
- [linkedin-short-post-drafter](./skills/content/linkedin-short-post-drafter)
- [long-form-post-drafter](./skills/content/long-form-post-drafter)
- [meeting-pack-processor](./skills/content/meeting-pack-processor)
- [release-note-writer](./skills/content/release-note-writer)
- [scheduling-assistant](./skills/content/scheduling-assistant)

### Delivery

Location: [skills/delivery](./skills/delivery)

- [ai-initiative-builder](./skills/delivery/ai-initiative-builder)
- [ai-initiative-deep-dive-and-scoping](./skills/delivery/ai-initiative-deep-dive-and-scoping)
- [clickup-project-plan-builder](./skills/delivery/clickup-project-plan-builder)
- [feedback-rice-prioritiser](./skills/delivery/feedback-rice-prioritiser)
- [implementation-plan-writer](./skills/delivery/implementation-plan-writer)
- [kickoff-summary-writer](./skills/delivery/kickoff-summary-writer)
- [project-context-builder](./skills/delivery/project-context-builder)
- [project-packager](./skills/delivery/project-packager)
- [project-report-writer](./skills/delivery/project-report-writer)
- [project-support](./skills/delivery/project-support)
- [training-plan-writer](./skills/delivery/training-plan-writer)

### Design

Location: [skills/design](./skills/design)

- [mermaid-flowchart-designer](./skills/design/mermaid-flowchart-designer)
- [source-derived-design-system-builder](./skills/design/source-derived-design-system-builder)

### Documentation

Location: [skills/documentation](./skills/documentation)

- [docx-assistant](./skills/documentation/docx-assistant)
- [knowledge-transfer-documentation-writer](./skills/documentation/knowledge-transfer-documentation-writer)
- [process-document-writer](./skills/documentation/process-document-writer)

### Media

Location: [skills/media](./skills/media)

- [elevenlabs-ai-voice-gen](./skills/media/elevenlabs-ai-voice-gen)
- [remotion-explainer-video-production](./skills/media/remotion-explainer-video-production)

### Meta

Location: [skills/meta](./skills/meta)

- [skill-eval-suite-writer](./skills/meta/skill-eval-suite-writer)
- [llm-instruction-fixer](./skills/meta/llm-instruction-fixer)
- [llm-instruction-reviewer](./skills/meta/llm-instruction-reviewer)
- [skill-finaliser](./skills/meta/skill-finaliser)

## Future Consideration

[future-consideration](./future-consideration) holds future-skill notes, rubrics, and idea fragments that are worth keeping but are not yet ready to package as active skills.

Use it for:

- future public skill ideas
- reusable methods that need a cleaner standalone package later
- notes that should not yet be promoted into the active `skills/` tree

## How `tdd` Fits In

I am not forking `tdd` here at the moment.

Use the upstream [`tdd` skill from mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) alongside the engineering family:

- use `repository-dissection` first when the codebase truth is unclear
- use `query-to-knowledge` when terms, decisions, or local behavior are still unresolved
- use `tdd` when doing behavior-changing implementation work
- use `repository-knowledge-engineering` to keep code, tests, and docs aligned in the same slice
- use `local-handoff` when pausing
- use `pickup` when resuming

## Recommended Flows

### Inherited unclear repo

`repository-dissection -> query-to-knowledge -> tdd -> repository-knowledge-engineering -> local-handoff`

### Resumed implementation tranche

`pickup -> tdd -> repository-knowledge-engineering -> local-handoff`

### Docs or support alignment pass

`pickup -> repository-knowledge-engineering -> local-handoff`

### Support-aware rule

Power-user local capability does not automatically equal repository-supported surface.
