# Claude Code Instructions

@AGENTS.md

Before taking task actions, apply the core block under `Portable Skill Invocation Contract` in `README.md` and the family block for each type of work in scope. Inspect the linked catalogue or indexed `SKILL.md` frontmatter to choose skills; do not treat this file as a replacement skill catalogue.

An explicit skill name, documented acronym, or clear match to an installed skill's description requires invocation. Read the selected `SKILL.md` completely and follow its workflow, validation, announcement, and final-response requirements without waiting for the user to invoke it manually.

For material repository engineering and read-only explanations of repository code, implementation behaviour, or diffs, invoke `engineering-workflow` (EWF) as the normal skill entry point and select the relevant method reference. Comprehension does not require workflow state or closure. Simple document wording questions and trivial inspection stay outside EWF. EWF works without RKE. Use the separate `rke` skill for relevant installed runtime retrieval, validation, freshness or optional continuity support; it supports EWF methods rather than defining another lifecycle. OKF Tasks remains the independent execution-record primitive, with `repo-task-lifecycle` (RTL) supplying its execution capability when needed. Select EWF methods by current outcome; historical package crosswalks remain source-side audit material outside the installed methodology. `repo-setup` remains the separate bootstrap capability.

The EWF and RKE adapter packages here are synchronized catalogue mirrors of [polaralias/rke](https://github.com/polaralias/rke), pinned by their `RKE_SOURCE.json` manifests. Update their canonical sources first and use the source repository's mirror tooling; see [README.md](README.md#install-with-the-skills-cli) for Skills CLI installation.
