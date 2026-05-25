# Skill finalisation standards

Use this reference when taking a draft skill to a shippable state.

The aim is to preserve strong methodology, align to the Agent Skills specification, and make the package internally consistent, testable, and easy for an agent to activate correctly.

## 0. External specification anchor

Treat the Agent Skills specification as the primary external contract for skill packaging:

- [Agent Skills specification](https://agentskills.io/specification)

That specification defines the durable baseline for:

- directory structure
- `SKILL.md` frontmatter
- `name`
- `description`
- optional `license`
- optional `compatibility`
- optional `metadata`
- optional `allowed-tools`
- the role of `scripts/`, `references/`, and `assets/`
- progressive disclosure and validation expectations

Use this file as the implementation-focused companion, not as a replacement for the public spec.

## 1. Canonical packaging principles

### 1.1 Trigger clarity

The `description` field is the real activation surface.

Good descriptions:

- say what the skill does
- say when to use it
- include concrete trigger signals
- avoid bloated workflow detail

Keep `description` within the Agent Skills limit and keep it trigger-oriented rather than procedural.

### 1.2 Name discipline

Names should be concrete, action-oriented, and stable.

Preferred patterns include:

- `*-writer`
- `*-builder`
- `*-converter`
- `*-finaliser`
- `*-assistant`
- `*-support`

Rules:

- choose a name that reflects the capability or output clearly
- keep the directory name and the `SKILL.md` `name` field identical
- avoid vague abstract nouns when a stronger action-based name exists

### 1.3 Progressive disclosure

Keep the main `SKILL.md` operational but not overloaded.

- core trigger and workflow logic in `SKILL.md`
- stable deep reference material in `references/`
- executable logic in `scripts/`
- static assets in `assets/`
- repository-root script folders only for repo-wide maintenance utilities, not one skill's executable helpers

Do not bury essential activation logic several files deep.

## 2. Canonical SKILL.md expectations

Use a clean frontmatter ordering unless a strong reason exists not to:

```yaml
---
name: skill-name
description: Clear trigger description that explains what the skill does and when to use it.
metadata:
  author: James Whelan
  version: "0.1.0"
  updated: "2026-05-20"
---
```

Rules:

- keep frontmatter focused on packaging metadata and trigger clarity
- move procedural detail into the body
- keep exclusions only where they genuinely prevent misuse
- use sentence case and concrete wording
- in this repository, append a three-letter all-caps alias to the end of the description using `Shorthand ABC.`

For this repository's alias convention:

- default to a three-letter all-caps alias
- prefer a short distinctive abbreviation of the skill name
- keep the alias stable once published
- if a clean three-letter alias would collide or mislead, surface the conflict explicitly rather than silently picking a noisy fallback

Near the top of the body, include the required precedence line:

`Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.`

## 3. Canonical companion metadata

When the package includes `agents/openai.yaml`, keep it aligned to the real skill behavior rather than treating it as decorative metadata.

Typical shape:

```yaml
interface:
  display_name: "Human Facing Name"
  short_description: "Readable description aligned with the trigger description."
  icon_small: assets/icon.svg
  icon_large: assets/icon.svg
  default_prompt: "Tell another model how to use the skill in one dense operational sentence."
policy:
  allow_implicit_invocation: true
  products:
  - chatgpt
  - codex
  - api
  - atlas
```

Rules:

- `display_name` should be short and readable
- `short_description` should stay close to the trigger description
- `default_prompt` should describe the workflow, not just restate the title
- if `SKILL.md` changes materially, review `openai.yaml` in the same pass
- if the local repository exposes aliases in generated indexes or README listings, keep those surfaces aligned in the same slice

## 4. Reference and script philosophy

### 4.1 What should be bundled

Bundle stable dependencies that the skill truly relies on, such as:

- output templates
- schemas
- deterministic scripts
- example payloads
- stable guidance docs
- reference material that defines file format or output structure

Placement rule:

- keep skill-specific scripts inside the packaged skill under `scripts/`
- keep skill-specific reference docs inside the packaged skill under `references/`
- keep skill-specific templates and static resources inside the packaged skill under `assets/`
- reserve top-level repo script directories for repository-wide tooling such as index builders, validators, or release-maintenance utilities

### 4.2 What should stay dynamic

Use runtime lookup only for explicitly per-run context when that context should not ship inside the skill.

Do not default to dynamic lookup for material that is actually stable enough to bundle.

### 4.3 Missing bundled reference rule

If a canonical bundled reference is missing:

- stop and say it is unavailable
- widen the search only if the user explicitly authorises it

Do not hide a missing reference behind vague fallback wording.

## 5. Instruction-quality review

Treat the skill package itself as an instruction artifact.

Before finalising it, inspect for:

- contradictions between frontmatter, body rules, exclusions, and output requirements
- ambiguity in trigger language, scope, precedence, or soft terms
- tone or persona drift across `SKILL.md`, `openai.yaml`, references, and tests
- excessive cognitive load from nested rules or scattered exceptions
- missing coverage for likely usage variants or failure paths
- cross-file inconsistencies between `SKILL.md`, `references/`, `tests/`, and companion metadata

This is where the methodology from:

- `llm-instruction-reviewer`
- `llm-instruction-fixer`
- `skill-eval-suite-writer`

becomes directly relevant.

### 5.1 Conservative repair rule

When repairing a skill:

- preserve its real purpose and operating model
- fix high-risk contradictions and ambiguities first
- prefer minimal edits unless the structure is the problem
- avoid inventing new capability just because there is room for it
- run a short post-fix self-check before considering the skill final

## 6. Testing and evaluation readiness

If a skill includes executable resources, the verification story should match the risk level.

Minimum expectations:

- non-trivial skills should normally include `tests/prompts.md`
- utility skills should usually expose at least one smoke or validation path
- multi-script skills should cover representative main workflows

`tests/prompts.md` should typically include:

- a primary happy path
- one or more exclusion or boundary cases
- source-of-truth checks where relevant
- a failure or missing-input path when relevant

If the skill is strong enough for formal evaluation work, it may be a good downstream candidate for `skill-eval-suite-writer`, but eval authoring is optional rather than part of basic finalisation.

## 7. Package hygiene

Skill folders should not ship with generated dependency installs, caches, or machine-local artifacts.

Remove these when present:

- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/` or `venv/`
- `dist/`
- `build/`
- ad hoc output folders
- `.DS_Store`
- `Thumbs.db`
- stray import archives once the canonical skill folder exists

## 8. Local repository-specific rules

Only a small part of finalisation should be repo-identity-specific.

### 8.1 Icon family

Package icons in this repo should follow the local icon family:

- `128x128` canvas
- rounded square background
- faint inner outline
- small translucent accent circle near the top-right
- one central MDI glyph
- one subtle shadow or support version of the same MDI glyph beneath it
- simple, high-contrast composition
- visually centred when rasterised

Use `icon-template.svg` as the local baseline frame.

Use a Material Design Icons glyph as the primary icon mark. Do not use monograms, acronyms, or free-drawn symbols as the packaged default unless the user explicitly asks for a non-MDI treatment.

#### Brand palette

Use this palette as the default source of truth for the current icon family:

- navy base: `#0b172b`
- white foreground: `#fdfdfd`
- red accent: `#e40117`
- light grey: `#bfc2ca`
- pale grey: `#d6d7dc`
- dark slate: `#333d4b`
- medium slate: `#3f4956`
- muted slate: `#777e8c`

Guidance:

- use the navy tile as the default base
- use white for the primary glyph
- keep the red as accent punctuation rather than dominant fill
- use the grey range for support geometry, shadow forms, or outline work
- keep the composition angular and precise rather than soft or playful

### 8.2 License file presence

Skills in this repository should ship with a bundled license file unless the user explicitly chooses a different packaging model.

Default license text for this repository:

```text
Copyright (c) James Whelan / polaralias.

All rights reserved.

Source repository: https://github.com/polaralias/skills
```

Rules:

- keep the license file present and non-empty
- keep the frontmatter or package metadata aligned to the actual file arrangement
- if the user later adopts a different public license, update the packaged file and references in the same pass
- do not let license mechanics dominate the skill instructions themselves

## 9. Final pass checklist

Before treating a skill as complete, confirm:

- the folder name and frontmatter `name` agree
- the trigger description is clear, specific, and within spec limits
- the repository's alias convention is satisfied, including the three-letter alias in frontmatter and any linked local surfaces that expose aliases
- any companion metadata reflects the actual skill behavior
- required precedence language is present
- bundled references are present and operational
- dynamic lookup exceptions are narrow and justified
- instruction language is internally consistent
- executable resources have a credible validation path
- generated dependency, cache, and junk folders are absent
- the package aligns with the Agent Skills specification and the local repo conventions
