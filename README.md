# My Skills Repo

This is my repository for development skills tailored to my own workflows.

## Layout

Current skills are grouped under [skills/engineering](./skills/engineering).

## Engineering Skills

### `repository-dissection`

Location: [skills/engineering/repository-dissection](./skills/engineering/repository-dissection)

Use this first for inherited, unclear, or vibe-coded repositories where the job is to dissect what is really there and turn that into documented understanding.

### `query-to-knowledge`

Location: [skills/engineering/query-to-knowledge](./skills/engineering/query-to-knowledge)

Use this when open questions, fuzzy terminology, or unresolved trade-offs need to be turned into durable repository knowledge without wasting turns on long serial interrogation.

### `repository-knowledge-engineering`

Location: [skills/engineering/repository-knowledge-engineering](./skills/engineering/repository-knowledge-engineering)

Use this to establish, evolve, and maintain the repository knowledge base, including canonical docs, `GLOSSARY.md`, decisions, plans, and handoff surfaces.

### `local-handoff`

Location: [skills/engineering/local-handoff](./skills/engineering/local-handoff)

Use this at the end of a tranche to write a dated local handoff under `docs/handoff/` in the repository being worked on. The skill finishes by reminding the user of the handoff path and, if relevant, that they may want to ignore it if they do not want to share handoff documents.

### `pickup`

Location: [skills/engineering/pickup](./skills/engineering/pickup)

Use this at the start of a resumed session to read the latest local handoff, re-check current state, and continue from verified context.

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
