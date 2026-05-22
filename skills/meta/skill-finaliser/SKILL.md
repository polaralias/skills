---
name: skill-finaliser
description: Finalise imported, draft, or half-finished skills into a clean, publishable skill package. Use when extracting a zipped skill, normalising SKILL.md frontmatter, aligning agents/openai.yaml to the expected interface shape, tightening trigger descriptions, adding a license file, creating or refreshing tests/prompts.md, generating or fixing an icon, checking package hygiene, and validating that bundled references, scripts, and tests are proportionate to the skill's purpose.
metadata:
  author: James Whelan
  version: "0.1.0"
  updated: "2026-05-20"
---

# Skill Finaliser

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `skill-finaliser was used in this response.`

Bring a loose, imported, or half-finished skill up to a clean package standard.

This skill is about packaging, UI metadata, visual consistency, source-of-truth hygiene, instruction quality, and proportionate validation.

Read `references/finalisation-standards.md` before editing.
Read `references/icon-template.svg` before creating a new icon.
Use `references/test-prompts-template.md` when creating `tests/prompts.md`.

For `SKILL.md` frontmatter and `agents/openai.yaml`, use the local `skill-creator` guidance as the spec companion when field shape or generation rules are unclear.

Run `scripts/validate_skill_package.py` against the target skill before treating the pass as complete.

## Finalisation goals

By the end of the pass, the target skill should have:

- a canonical folder under the target skills directory
- a polished `SKILL.md` with clear trigger wording
- the required precedence line near the top of `SKILL.md`
- a skill name that reads like a capability or deliverable
- `agents/openai.yaml` aligned to the skill's actual behaviour
- `assets/icon.svg` in the package icon style when the skill ships with an icon
- a generic repo license file with the current default copyright notice
- `tests/prompts.md` with plain-English regression prompts and expected behaviour
- runnable smoke or validation tests for executable skills where reasonable
- bundled references limited to stable operational resources
- explicit dynamic lookup exceptions only when the skill truly depends on per-run inputs
- no meaningful contradictions, ambiguity traps, tone drift, or obvious coverage gaps in the instruction surface
- no generated dependency, cache, or output folders

## Workflow

### 1. Inspect the source skill

Read the full target skill first:

- `SKILL.md`
- `agents/openai.yaml` if present
- `references/`, `scripts/`, `assets/`, and `tests/`

Identify:

- the final skill name and destination folder
- what the skill actually does
- whether the description is strong enough to trigger correctly
- whether local files are stable resources or stale guidance
- whether executable resources exist
- whether generated clutter is present

### 2. Normalise the folder

Place the skill in the target skills directory using this baseline shape:

```text
<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── assets/icon.svg
├── tests/prompts.md
└── references/ ...optional
```

Keep only files that materially support the skill. Do not add README-style extras.

Remove generated clutter if present, especially:

- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/` or `venv/`
- `dist/`, `build/`, or ad hoc output folders
- OS/editor junk such as `.DS_Store` or `Thumbs.db`
- stray import archives once the canonical skill folder exists

### 3. Rewrite the frontmatter

Use frontmatter for trigger-relevant signal only:

- `name`
- `description`
- `metadata.author`
- `metadata.version`
- `metadata.updated`

The `description` is the primary trigger. Make it explicit about:

- what the skill does
- which prompts or contexts should trigger it
- important exclusions when they prevent misuse

Keep the description under 1024 characters.

Move these out of the frontmatter:

- live URLs
- exact lookup roots
- document-reading instructions
- workflow sequencing
- long section lists

Use action-oriented names such as:

- `*-writer`
- `*-builder`
- `*-converter`
- `*-finaliser`
- `*-assistant`
- `*-support`

Keep the folder name, `SKILL.md` `name`, and packaged zip name identical.

### 4. Create or refresh `agents/openai.yaml`

Always create or update `agents/openai.yaml` so it matches the final skill.

Include:

- `interface.display_name`
- `interface.short_description`
- `interface.default_prompt`
- `interface.icon_small`
- `interface.icon_large`
- `policy.allow_implicit_invocation: true`
- `policy.products: [chatgpt, codex, api, atlas]`

Rules:

- `display_name` should be short, human-facing, and title case
- `short_description` should stay close to the trigger description
- `default_prompt` should tell another model how to use the skill without duplicating the full `SKILL.md`
- if the icon exists, point both icon fields to `assets/icon.svg`

### 5. Create `assets/icon.svg`

Create an icon that matches the package icon style. Use `references/icon-template.svg` as the structural baseline.

Keep these invariants:

- `128x128` canvas with rounded square background
- subtle inner stroke
- small translucent accent circle in the top-right quadrant
- one strong background colour
- one central white MDI glyph
- one slightly offset dark shadow version of the same MDI glyph underneath
- glyph visually centred in the rendered canvas, not just mathematically centred

Use a Material Design Icons glyph that represents the skill's actual job. Do not use text monograms, initials, or ad hoc drawn symbols as the primary mark unless the user explicitly overrides that rule.

### 6. Add the license file

Ensure a license file exists in the packaged skill.

Default to the local generic license text unless the user has explicitly provided a different license:

```text
Copyright (c) James Whelan / polaralias.

All rights reserved.

Source repository: https://github.com/polaralias/skills
```

Do not leave an empty placeholder file by default.

### 7. Audit bundled resources vs dynamic runtime files

Treat these as allowed local resources:

- output templates
- example payloads
- JSON schemas
- deterministic scripts
- static assets
- reference files describing stable formats or output structure
- intentionally bundled guidance that should travel with the skill

Only use dynamic runtime lookups for explicit per-run context when the skill truly depends on them.

Do not allow fallback wording like:

- `use the local copy if the bundled file is unavailable`
- `use the offline backup`
- `search broadly for alternatives`

If a required canonical bundled document is missing:

- stop and report it
- widen the search only if the user explicitly authorises that

### 8. Check test availability and depth

If the skill contains executable resources, inspect whether there is a credible validation path.

Also check whether `tests/prompts.md` exists. Treat it as the human-readable regression checklist, not a substitute for runnable tests.

Minimum expectation:

- non-trivial skills should have a `tests/prompts.md`
- simple one-script skills should usually have at least one runnable smoke or validation path
- multi-script or higher-risk skills should have representative tests or smoke checks for the main workflows

If a useful test can be added without unreasonable cost, add it instead of only documenting the gap.

### 9. Run an instruction-quality pass

Before declaring the skill finished, review the skill text itself as an instruction artifact.

Check for:

- contradictions between trigger wording, body rules, and response-proof requirements
- ambiguity in quantities, scope, precedence, or exclusions
- tone or persona drift inside the skill package
- excessive cognitive load from deeply nested rules or scattered exceptions
- missing coverage for likely usage variants, failure paths, or linked reference behavior
- cross-file inconsistencies between `SKILL.md`, `openai.yaml`, tests, and bundled references

Use the same mindset as a strong instruction reviewer, but keep the finaliser focused on shipping quality rather than producing a separate review artifact.

### 10. Tighten the skill language

Rewrite the target skill so the boundary is obvious:

- stable templates stay local
- bundled guidance lives in `references/`
- dynamic runtime inputs stay narrow and explicit

Remove local-fallback or backup-copy language.

### 11. Apply conservative fixes

When repairing issues found in the instruction-quality pass:

- preserve the skill's actual purpose
- fix the highest-risk contradictions and ambiguities first
- keep edits minimal unless the structure itself is causing failures
- avoid adding new capability surface unless it is needed to close a real gap
- do a short self-check after edits to confirm the repair did not introduce a new conflict

### 12. Cross-skill reference pass

After the main packaging pass, do a second look across the skill stack:

- scan for sibling or upstream/downstream skills that would materially improve the target skill's usage or packaging
- add a narrow `Related skill` or similar note only when it helps
- avoid reference chains

Also confirm:

- the response-proof instruction exists where the skill produces chat output
- the precedence line is present near the top of `SKILL.md`
- the skill is in a good state to hand off to `skill-eval-suite-writer` if the user wants formal evaluation coverage later

### 13. Sanity-check the result

Before finishing, confirm:

- folder name matches the skill name
- frontmatter is complete and internally consistent
- `description` is under 1024 characters and trigger-focused
- `agents/openai.yaml` matches the final `SKILL.md`
- `assets/icon.svg` exists and uses the package style if the skill ships with an icon
- the license file exists
- `tests/prompts.md` exists and is meaningful
- executable skills include runnable smoke or validation tests where practical
- references are only bundled where that makes sense
- dynamic lookup exceptions are narrow and documented
- instruction text is internally consistent and clear enough to execute reliably
- no generated dependency or cache folders remain

## Red flags

Stop and fix the skill if you find any of these:

- `description` exceeds 1024 characters or is padded with low-signal workflow detail
- `description` contains live URLs, document-reading instructions, or long section lists that belong in the body
- `openai.yaml` describes a different skill than `SKILL.md`
- the target skill produces chat responses but is missing the `<skill-name> was used in this response.` instruction
- the target skill is missing the required precedence line
- the icon is missing or visually off-centre
- `tests/prompts.md` is missing for a non-trivial skill
- executable scripts exist but there is no credible smoke test, validation path, or acknowledged testing gap
- the instruction surface still contains obvious contradictions, ambiguity, or cross-file drift after finalisation
- generated folders such as `node_modules` or `__pycache__` are present in the packaged skill

## Resources

- `references/finalisation-standards.md`
- `references/icon-template.svg`
- `references/test-prompts-template.md`

## Response proof

This is a hard requirement for any chat response produced with this skill. Include a brief proof line at the start or end of the message in the form: `<skill-name> was used in this response.` If multiple skills were used, list them all in the same proof line. Do not place this line inside generated documents unless the user explicitly asks for it.
