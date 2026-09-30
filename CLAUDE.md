# Claude Code Instructions

@AGENTS.md

Before taking task actions, apply the core block under `Portable Skill Invocation Contract` in `README.md` and the family block for each type of work in scope. Inspect the linked catalogue or indexed `SKILL.md` frontmatter to choose skills; do not treat this file as a replacement skill catalogue.

An explicit skill name, documented acronym, or clear match to an installed skill's description requires invocation. Read the selected `SKILL.md` completely and follow its workflow, validation, announcement, and final-response requirements without waiting for the user to invoke it manually.

For material repository engineering and read-only explanations of repository code, implementation behaviour, or diffs, invoke `engineering-workflow` (EWF) as the single normal skill entry point. Code explanations use RCC prose without creating RKE state. Simple document wording questions and trivial read-only inspection stay outside EWF. EWF works without RKE. When RKE is available, use its deterministic repository evidence and safety operations; activate durable workflow state when continuity or machine gates are useful. OKF Tasks remains the independent execution-record primitive. Resolve legacy engineering names and aliases through EWF compatibility routing instead of invoking absorbed packages as orchestration peers. `repo-setup` remains a separate pre-workflow bootstrap capability.
