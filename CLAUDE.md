# Claude Code Instructions

@AGENTS.md

Before taking task actions, apply the core block under `Portable Skill Invocation Contract` in `README.md` and the family block for each type of work in scope. Inspect the linked catalogue or indexed `SKILL.md` frontmatter to choose skills; do not treat this file as a replacement skill catalogue.

An explicit skill name, documented acronym, or clear match to an installed skill's description requires invocation. Read the selected `SKILL.md` completely and follow its workflow, validation, announcement, and final-response requirements without waiting for the user to invoke it manually.

For material repository engineering, invoke `engineering-workflow` (EWF) as the single normal skill entry point and run the installed RKE runtime's idempotent `rke activate` command before broad inspection or mutation. RKE remains the independent repository-knowledge methodology and executable runtime; OKF Tasks remains the independent execution-record primitive. Resolve legacy engineering names and aliases through EWF compatibility routing instead of invoking absorbed packages as orchestration peers. `repo-setup` remains a separate pre-workflow bootstrap capability.
