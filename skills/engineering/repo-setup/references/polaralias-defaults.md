# Polaralias Defaults

Use this file before applying shared setup templates.

## Governance defaults

- Default license: `Apache-2.0`
- Add `NOTICE` with `James Whelan / Polaralias`
- Add `.github/CODEOWNERS` using the configured owner list
- Require PRs for the default branch with a repository ruleset
- Ruleset name: `Protect default branch`
- Required approving review count: `1`
- Require code-owner review: `true`
- Require conversation resolution: `true`
- Disallow force pushes: `true`
- Disallow deleting the protected branch: `true`
- Admin bypass: off unless explicitly requested; organisation-admin bypass is valid only for organisation-owned repositories
- Do not enable auto-delete head branches by default

## Description defaults

At setup time:

- set a product-facing GitHub description
- prefix it with `WIP: `
- keep it short enough for GitHub repo metadata

At finalisation time:

- remove the `WIP: ` prefix
- tighten wording so it describes the finished or publish-ready state

## Docs defaults

`CONTRIBUTING.md` and `AGENTS.md` should consistently say:

- work from a short-lived feature branch
- do not commit directly to `main`
- open a PR before merging to `main`
- prefer squash merge unless history shape matters
- delete merged or closed feature branches
- never delete `main`

## Draft release defaults

- keep `.github/release-drafter.yml`
- keep `.github/workflows/release-drafter.yml`
- use `release-drafter/release-drafter@v7`
- do not use deprecated Node 20 action pins
