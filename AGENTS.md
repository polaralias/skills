# AGENTS

This repository is a local skills library.

Read [README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/README.md) first for the current family layout.

Read [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md) for the canonical `SKILL.md` path index and frontmatter line counts.

## Working Rules

- Treat each `SKILL.md` as the source of truth for that skill.
- If you only need trigger metadata, read just the frontmatter first using the line counts in [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md).
- Read beyond the frontmatter only when you are actually using or updating that skill.
- Use [`.agents/skills/skill-finaliser`](</C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/.agents/skills/skill-finaliser>) as the preferred local path when finalising or normalising skill packages.
- Keep package structure consistent with the finalized engineering skills and the `skill-finaliser` expectations.

## Repo Maintenance Rule

When you make structural or packaging changes in this repository, update every relevant guidance surface in the same slice.

Usually that means checking and updating:

- [README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/README.md)
- [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md)
- [AGENTS.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/AGENTS.md)
- [future-consideration/README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/future-consideration/README.md) when future-note handling changes

Do not leave the tree changed while the repo guidance still points at old paths, old family membership, or old packaging rules.
