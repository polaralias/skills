---
name: repo-setup
description: Bootstrap a repository with baseline governance, licensing, branch protection, draft-release scaffolding, and a GitHub description. Use when a user wants to set up a new repo, scaffold publish-readiness, choose a license, apply standard contributor or agent docs, or turn on PR-based protection for `main` before active engineering work begins. Set the initial GitHub description in a clear WIP form and recommend `engineering-workflow-orchestrator` as the next step when setup is complete. Shorthand RST.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.2.0
  updated: '2026-06-06'
---

# repo-setup

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `repo-setup was used in this response.`

Use this skill to make a repository safe and legible to start working in.

This is a bootstrap skill, not a final release skill. Set up the repo early, keep the result repeatable, and prefer deterministic script or template application over one-off prose edits.

Read [references/license-selection.md](./references/license-selection.md) before choosing a license.
Read [references/polaralias-defaults.md](./references/polaralias-defaults.md) before applying defaults.
Read [references/repo-admin-config.md](./references/repo-admin-config.md) before creating or updating `repo-admin.json`.

Use [scripts/repo_setup.py](./scripts/repo_setup.py) for deterministic file rendering and GitHub settings whenever possible.

## Workflow

### 1. Inspect the current repo state

- Read the root `README.md`, `AGENTS.md`, and existing `.github/workflows/` first.
- Determine the repo type and whether baseline governance files already exist.
- Check whether a GitHub description is missing or clearly placeholder-quality.
- If the repo already has release automation, do not overwrite it blindly during setup.
- Review the root `.gitignore`.
- Flag clearly when `local-docs/` already exists so the user knows a local-only docs area is already available.

### 2. Choose the license deliberately

- Use the Choose a License summaries in `references/license-selection.md`.
- Prefer `Apache-2.0` when the user wants commercial-friendly reuse with preserved notices and attribution.
- Prefer `MIT` only when the user explicitly wants the most permissive path and is comfortable with thinner attribution obligations.
- Do not silently apply strong copyleft licenses just because they are available.
- If the user wants a license not covered by the local templates, stop and choose the exact license text first instead of improvising.

### 3. Apply the baseline governance layer

Use the script layer first:

- `sync-doc-templates` to apply or refresh:
  - `LICENSE`
  - `NOTICE`
  - `CONTRIBUTING.md`
  - `AGENTS.md` baseline block
  - `.github/release-drafter.yml`
  - `.github/workflows/release-drafter.yml`
- `set-description` to set a concise GitHub repo description in WIP form
- `set-branch-protection` to enforce PR-based protection on `main`

Use the Polaralias defaults profile unless the repo has explicit override requirements.

Also make the local-only docs convention explicit:

- ensure the root `.gitignore` contains `local-docs/`
- ensure a root `local-docs/` folder exists for machine-local notes and continuity artifacts
- keep tracked project documentation in normal repo paths; use `local-docs/` only for intentionally local-only material

When scaffolding release automation around a repo-level `VERSION` file:

- make the draft-release flow read `VERSION` directly for the draft name and tag
- do not leave Release Drafter on an independent label-derived version path when `VERSION` is the canonical source of release truth

### 4. Create or refresh repo-admin configuration

- Prefer a checked-in `repo-admin.json` when the repo should be re-bootstrapable by other agents.
- Keep it small and explicit.
- At minimum capture:
  - repo type
  - chosen license
  - summary text
  - whether PR enforcement is on
  - whether release automation is expected later

### 5. Keep the description honest

- During setup, the description should usually carry a visible WIP marker, for example `WIP: Home Assistant integration for ...`
- The description should still state the product clearly, not hide behind process language.
- Do not leave the repo with no description unless the user explicitly declines one.

### 6. Stop at bootstrap boundaries

- Do not turn this skill into the full release automation pass.
- If the repo clearly needs release/version automation, note that `repo-publish-finaliser` should be run later.
- If engineering work is about to start, recommend `engineering-workflow-orchestrator` as the next skill.

## Output shape

When using this skill, report:

- the chosen license and why
- the governance files added or updated
- whether `local-docs/` already existed or was created
- whether `.gitignore` already covered `local-docs/` or was updated
- whether branch protection with PR requirement was enabled
- the GitHub description that was set
- whether `repo-admin.json` was added or updated
- the recommended next skill

## Guardrails

- Prefer script-backed edits over ad hoc rewrite work.
- Do not overwrite an existing richer repo-specific `AGENTS.md`; merge the shared baseline block instead.
- Do not remove existing release automation during setup unless the user explicitly asks for replacement.
- Keep the WIP description concise and product-facing.
- Do not turn `local-docs/` into tracked canonical documentation.
- Recommend `engineering-workflow-orchestrator` rather than assuming the next implementation stage.
