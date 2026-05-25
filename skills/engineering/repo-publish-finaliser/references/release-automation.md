# Release Automation

Use this file when `repo-publish-finaliser` needs to decide whether to add or repair release/version automation.

## Decision rule

Ask or infer:

- does this repo need tagged GitHub Releases
- is there a canonical version source in-repo
- which repo family does it belong to

If the answer is still unclear, do not force release automation into a repo just because it could exist.

## Supported profiles

Use the starter assets and script surface from sibling skill [repo-setup](../repo-setup):

- `scripts/repo_setup.py apply-release-profile --profile android`
- `scripts/repo_setup.py apply-release-profile --profile mcp`
- `scripts/repo_setup.py apply-release-profile --profile homeassistant`
- `scripts/repo_setup.py apply-release-profile --profile generic`

These starter profiles intentionally avoid deprecated Node 20-only action pins.

## Android profile

Use for Android apps where the release artifact should be a debug APK.

Expected shape:

- debug CI on pushes and PRs to `main`
- tag-triggered GitHub Release publish flow
- `versionName` and `versionCode` extracted from Gradle
- `version-metadata.json` emitted
- artifact named explicitly, for example `audiofocus-debug.apk`

Canonical version source:

- `app/build.gradle.kts`

## MCP / Python profile

Use for Python packages and servers where `pyproject.toml` is the release source of truth.

Expected shape:

- tag-triggered release publish flow
- tag must equal `v{project.version}`
- `version-metadata.json` emitted

Canonical version source:

- `pyproject.toml`

## Home Assistant profile

Use for integrations where `manifest.json` defines the shipped integration version.

Expected shape:

- tag-triggered release publish flow
- tag must equal `v{manifest.version}`
- `version-metadata.json` emitted

Canonical version source:

- `custom_components/<domain>/manifest.json`

## Generic profile

Use when the repo has a simple repo-level version and does not need a specialized parser.

Expected shape:

- tag-triggered release publish flow
- tag must equal `v{VERSION}`
- `version-metadata.json` emitted

Canonical version source:

- `VERSION`

## Description cleanup

If setup previously set a `WIP:` GitHub description, finalisation should remove the prefix and tighten the wording so it describes the finished or publish-ready repo accurately.

README cleanup should follow the same principle:

- the README should describe the finished project for humans first
- agentic or repo-operations detail should live in `AGENTS.md`
- include a checked-in banner, logo, or icon when the repo already has a suitable asset
