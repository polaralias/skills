# AGENTS

This repository is a local skills library.

Read [README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/README.md) first for the current family layout.

Read [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md) for the canonical `SKILL.md` path index and frontmatter line counts.

## Working Rules

- Treat each `SKILL.md` as the source of truth for that skill.
- If you only need trigger metadata, read just the frontmatter first using the line counts in [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md).
- Read beyond the frontmatter only when you are actually using or updating that skill.
- Treat documented three-letter all-caps acronym shorthands in [README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/README.md) and [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md) as valid invocation forms for the matching skill.
- Use [scripts/build_skill_index.py](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/scripts/build_skill_index.py) to regenerate [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md) after any frontmatter or skill-path change.
- Use [`.agents/skills/skill-finaliser`](</C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/.agents/skills/skill-finaliser>) as the preferred local path when finalising or normalising skill packages.
- Keep package validation under [`.agents/skills/skill-finaliser/scripts/validate_skill_package.py`](</C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/.agents/skills/skill-finaliser/scripts/validate_skill_package.py>) rather than duplicating a second repo-level validator.
- Keep package structure consistent with the finalized engineering skills and the `skill-finaliser` expectations.
- For setup or customization skills, keep persistent user configuration outside installed skill folders. Prefer `~/.agents/config/<skill-name>/` and use `~/.config/<skill-name>/` only as fallback.

## Versioning Rule

When you change a skill package, bump that skill's `metadata.version` in `SKILL.md`.

Use this versioning method consistently:

- patch: `x.y.Z` for wording fixes, packaging fixes, metadata-only changes, icon updates, test prompt updates, or other non-behavioral corrections
- minor: `x.Y.z` for meaningful capability additions, new workflow branches, new bundled references that expand what the skill can do, or broader trigger coverage that stays backward-compatible
- major: `X.y.z` for breaking changes to scope, trigger behavior, required inputs, output contract, or incompatible workflow expectations

If several skills change in one slice, bump each changed skill independently based on the impact to that specific package.

## Repo Release Rule

This repository also has a repo-level `VERSION` file for GitHub Releases.

- adding, deleting, or renaming a packaged skill requires a repo-major bump
- changing more than one packaged skill in one release requires at least a repo-minor bump
- changing exactly one packaged skill is usually a repo-patch bump unless that skill's own semver bump is larger
- if a packaged skill changes and its `metadata.version` does not change, the release validation should fail

## Repo Maintenance Rule

When you make structural or packaging changes in this repository, update every relevant guidance surface in the same slice.

Usually that means checking and updating:

- [README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/README.md)
- [INDEX.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/INDEX.md)
- [AGENTS.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/AGENTS.md)
- [future-consideration/README.md](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/future-consideration/README.md) when future-note handling changes
- [scripts/build_skill_index.py](/C:/Users/james.DESKTOP-Q8VOBFS/Documents/Development/skills/scripts/build_skill_index.py) if the `INDEX.md` source data changed
- the changed skill's `metadata.version`

Do not leave the tree changed while the repo guidance still points at old paths, old family membership, or old packaging rules.

## Shared Git Workflow

- work from a short-lived branch created from `main`
- do not commit directly to `main`
- use branch names prefixed with `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, or `test/`
- keep one logical change per branch and pull request
- open a pull request before merging to `main`, including for solo work
- prefer squash merge unless multiple commits carry durable review value
- delete the merged or closed feature branch after the work is finished; never delete `main`
- use tags in `vX.Y.Z` format for releases and do not move published tags
