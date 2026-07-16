# GitHub repository rulesets

Use a repository ruleset as the maintained protection layer for the default branch.

## Safe application order

1. Confirm the remote default branch exists and has an initial commit.
2. Render `.github/CODEOWNERS` from explicit repository configuration.
3. Commit and push CODEOWNERS to the branch that will be protected.
4. List repository-owned rulesets and find an exact configured-name match.
5. Create the rule when no match exists, or update the single match returned by GitHub.
6. Fetch the stored rule and verify its enforcement, target, conditions, review policy, and destructive-update blocks.
7. Check for classic branch protection and report overlap without deleting it.

## Identity and IDs

The configured ruleset name is the durable lookup key. A ruleset ID returned by GitHub is operation-local data, not configuration and not documentation.

Bypass actors are optional. Organisation-admin bypass can be requested for an organisation-owned repository without embedding a numeric role identifier. Do not infer an equivalent bypass for a personal repository. If another actor type is required, obtain and validate its identity for the target repository rather than copying an identifier from an example.

## CODEOWNERS constraints

CODEOWNERS must exist on the pull request's base branch for code-owner review to take effect. Configured owners also need sufficient repository access. A generated file is not ready until it has been committed and pushed.

## Layering

Repository rulesets can coexist with classic branch protection and with other applicable rulesets. GitHub combines applicable constraints, so overlapping controls can produce a stricter outcome than either surface suggests alone. Inspect and report overlaps before changing or removing an existing layer.

## Authoritative references

- GitHub Docs: About rulesets
- GitHub REST API: Repository rules
- GitHub Docs: About code owners
