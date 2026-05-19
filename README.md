# My Skills Repo

This is my repository for development skills tailored to my own workflows.

## Layout

Current skills are grouped under [engineering](./engineering).

## Engineering Skills

### `repository-dissection`

Location: [engineering/repository-dissection](./engineering/repository-dissection)

Use this first for inherited, unclear, or vibe-coded repositories where the job is to dissect what is really there and turn that into documented understanding.

### `query-to-knowledge`

Location: [engineering/query-to-knowledge](./engineering/query-to-knowledge)

Use this when open questions, fuzzy terminology, or unresolved trade-offs need to be turned into durable repository knowledge without wasting turns on long serial interrogation.

### `repository-knowledge-engineering`

Location: [engineering/repository-knowledge-engineering](./engineering/repository-knowledge-engineering)

Use this to establish, evolve, and maintain the repository knowledge base, including canonical docs, `GLOSSARY.md`, decisions, plans, and handoff surfaces.

### `local-handoff`

Location: [engineering/local-handoff](./engineering/local-handoff)

Use this at the end of a tranche to write a dated local handoff under `.codex/handoffs/` so the next session can resume cleanly.

### `pickup`

Location: [engineering/pickup](./engineering/pickup)

Use this at the start of a resumed session to read the latest local handoff, re-check current state, and continue from verified context.

## How `tdd` Fits In

I am not forking `tdd` here at the moment.

Use the upstream [`tdd`](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) skill alongside the engineering family:

- use `repository-dissection` first when the codebase truth is unclear
- use `query-to-knowledge` when terms, decisions, or local behavior are still unresolved
- use `tdd` when doing behavior-changing implementation work
- use `repository-knowledge-engineering` to keep code, tests, and docs aligned in the same slice
- use `local-handoff` when pausing
- use `pickup` when resuming
