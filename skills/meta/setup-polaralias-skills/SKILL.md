---
name: setup-polaralias-skills
description: Configure shared Polaralias skill defaults outside installed skill folders. Use when a user wants to set or refresh cross-repo defaults such as branding, typography, logos, palette values, footer text, output tone, reusable asset paths, or structured output and tracker preferences for other Polaralias skills. Shorthand SPS.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.3.0
  updated: '2026-05-25'
---

# setup-polaralias-skills

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `setup-polaralias-skills was used in this response.`


Use this skill to create or refresh durable user-level defaults for Polaralias skills without editing installed skill packages.

Persistent customization must live outside the skill folder so `npx skills update` can replace skill files safely without wiping user preferences.

## Config locations

Prefer this user-level location first:

- `~/.agents/config/polaralias-skills/profile.md`
- `~/.agents/config/polaralias-skills/variables.yaml`

Use this fallback only if the preferred location cannot be created or is clearly unsuitable in the current environment:

- `~/.config/polaralias-skills/profile.md`
- `~/.config/polaralias-skills/variables.yaml`

Do not write persistent user customization into an installed skill directory unless the user explicitly asks for a local package override and understands it may be replaced by updates.

## What these files are for

- `profile.md`: human-readable style contract, tone, and usage notes
- `variables.yaml`: stable keys for brand assets, typography, palette, reusable defaults, and structured output or tracker preferences for skills that need them

Use the templates in [references/profile-template.md](./references/profile-template.md), [references/variables-template.yaml](./references/variables-template.yaml), and [references/config-contract.md](./references/config-contract.md) as the starting point.

## Process

### 1. Inspect current state

Check whether any of the preferred or fallback config files already exist.

If they do, read them before asking the user to repeat information they already provided.

If both preferred and fallback locations exist, treat the preferred `~/.agents/config/...` copy as canonical and tell the user the fallback copy also exists.

### 2. Explain the setup briefly

Tell the user these files let multiple Polaralias skills reuse the same defaults across repositories.

Say that the preferred install target is `~/.agents/config/polaralias-skills/` because it sits inside the user's home directory and is likely to be visible to many agents.

### 3. Gather the config

Walk the user through the setup in short sections. Do not dump everything at once if the existing files are absent or incomplete.

Collect or confirm:

- brand or studio name
- preferred output style or tone
- display font and fallback font
- primary display-font TTF path when a renderer needs embedded custom fonts
- logo path or paths
- palette defaults
- footer or attribution text
- reusable asset paths
- preferred issue tracker or local task surface when relevant
- issue or work-package output preferences when relevant
- any branded do/don't rules

If the user only wants partial setup, record only what they actually confirmed and leave the rest explicitly blank or commented in the YAML template.

### 4. Draft before writing

Prepare the draft `profile.md` and `variables.yaml` content first.

Show the user which target path you plan to use and present the draft content for confirmation before writing.

If the user explicitly wants a fast path and the intended values are already clear, you may collapse confirmation into one short approval question instead of a full review pass.

### 5. Confirm and write

Try the preferred directory first:

- `~/.agents/config/polaralias-skills/`

Create or update:

- `profile.md`
- `variables.yaml`

If the preferred path cannot be created or updated, explain why, tell the user you are falling back, and then use:

- `~/.config/polaralias-skills/`

If neither location can be written in the current environment:

- do not fail silently
- return the final drafted file contents in chat
- say that the install step could not be completed automatically
- tell the user which location should be created manually when write access is available

### 6. Local-only approval mode

If the user wants the configuration to stay local to the current installing model or environment, treat that as approval to write only to the accessible user-level config path in that environment.

If the preferred `~/.agents/config/...` path is inaccessible in that environment, fall back gracefully to `~/.config/...` and say that the setup was kept local there instead.

### 7. Report the outcome

Tell the user:

- which path was written
- which files were created or updated
- which downstream skills can now read the shared config
- that repo-specific overrides can still exist separately if a particular repository needs different branding

## Consumer contract

Downstream Polaralias skills should resolve defaults in this order:

1. explicit instructions from the current user request
2. repo-local override files when the skill defines them
3. `~/.agents/config/polaralias-skills/`
4. `~/.config/polaralias-skills/`
5. packaged defaults

If no shared config is found, the consuming skill should continue with packaged defaults and say that no shared Polaralias variables were found, so defaults were used.

When a consuming skill needs concrete asset paths, use the canonical keys described in [references/config-contract.md](./references/config-contract.md) instead of inventing new ad hoc variable names.
When a consuming skill shapes issue-ready or tracker-ready output, use the structured output keys from the shared contract before inventing new tracker labels, publication targets, or hierarchy defaults.
This contract is intended for downstream skills such as `doc-driven-development` and `tracker-publisher`.
