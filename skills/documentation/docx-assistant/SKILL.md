---
name: docx-assistant
description: Use this skill whenever the task is fundamentally about a Microsoft Word document or a `.docx` file. It is the primary route for creating, revising, reviewing, repairing, validating, formatting, or returning Word documents in this environment. Trigger it for explicit Word or `.docx` requests, for formal deliverables such as reports, proposals, policies, plans, SOPs, guides, letters, handouts, questionnaires, templates, runbooks, and similar business documents, and for edit workflows that must preserve existing document structure. Also use it for tracked changes, reviewer comments, page numbering, headers and footers, formatting preservation, search-and-replace, and converting rough notes into a finished document artifact. Do not use it for chat-only drafting, PDF-only work, spreadsheets, slide decks, Google Docs workflows, or unrelated software changes.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.1.0
  updated: '2026-05-22'
---

# DOCX Assistant

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `docx-assistant was used in this response.`


This package is the default Word-document workflow. Use it to generate new `.docx` files, modify existing ones, inspect package structure, apply comments or tracked changes, and run document QA.

For fresh documents, start from the schema-driven entrypoint instead of inventing one-off rendering code:

```bash
python scripts/generate_docx.py --mode branded --input spec.json --output output.docx
```

The authoring contract lives in [references/spec-schema.md](./references/spec-schema.md) and [references/spec-schema.json](./references/spec-schema.json).

## Rendering routes

There are two supported output routes.

### `branded`

Use `branded` unless the user explicitly asks for a stripped-back document.

This route is for polished deliverables where the document should have visual identity and repeatable structure: proposals, reports, customer packs, implementation docs, formal guides, and similar outputs.

The branded route includes:

- cover-page treatment
- running page chrome
- themed section openers
- metadata bars and callout families
- real Word tables and bullets
- optional custom-font embedding when a TTF is supplied

Important constraint: branded does not mean noisy. Keep the page system coherent and restrained.

### `simple`

Use `simple` only when the user explicitly asks for something like `simple`, `plain`, `minimal`, `basic`, `quick`, `unbranded`, `bare`, or `no branding`.

This route keeps:

- standard fonts
- optional lightweight logo/header usage if configured
- plain heading structure
- ordinary tables and bullets

This route does not use the richer cover, section-banner, or themed callout system.

## Theme setup

The richer route is designed around a configurable theme layer rather than a single baked-in visual identity.

Before asking the user to restate branding defaults, check for shared Polaralias config in this order:

- `docs/agents/polaralias-skills.md`
- `docs/agents/polaralias-variables.yaml`
- `~/.agents/config/polaralias-skills/profile.md`
- `~/.agents/config/polaralias-skills/variables.yaml`
- `~/.config/polaralias-skills/profile.md`
- `~/.config/polaralias-skills/variables.yaml`

Use explicit user instructions for the current document over any saved defaults.

If a shared or repo-local variables file exists, use it to populate the theme choices before asking the user for missing assets.

Prefer the shared config keys defined by `setup-polaralias-skills`, especially:

- `brand_name`
- `display_font`
- `fallback_font`
- `primary_font_ttf`
- `logo_path`
- `logo_protected_path`
- `accent_icon_path`
- `footer_text`
- `palette.*`
- skill-specific overrides under `assets.*` for DOCX rendering

If both generic keys and DOCX-specific `assets.*` keys are present, prefer the DOCX-specific values for this skill.

If no shared config exists, continue with the generic themed defaults and say that no shared Polaralias variables were found, so fallback branding was used.

After doing that, ask the user whether they want to run `setup-polaralias-skills` so future branded documents can reuse shared defaults.

Recognised environment variables:

- `DOCX_THEME_DISPLAY_FONT_NAME`
- `DOCX_THEME_PRIMARY_FONT_TTF`
- `DOCX_THEME_FALLBACK_FONT_NAME`
- `DOCX_THEME_LOGO_PATH`
- `DOCX_THEME_LOGO_PROTECTED_PATH`
- `DOCX_THEME_ACCENT_ICON_PATH`
- `DOCX_THEME_BRAND_NAME`

Theme guidance lives in:

- [references/theme-system.md](./references/theme-system.md)
- [references/theme-config.example.json](./references/theme-config.example.json)

If no custom font file is provided, the package should still render successfully using fallbacks.

If a branded run would benefit from custom assets that are not available locally, do not fail or invent them. Ask the user whether they want to add any of the following before finalising the themed document:

- logo files
- a primary display-font TTF
- palette choices
- brand or footer text

If the user does not provide them, continue with the generic themed defaults and say that the package is using fallback branding.

If the user wants shared defaults across repositories, use `setup-polaralias-skills` rather than storing persistent custom values inside the installed skill package.

## Spec constraints

The JSON schema is intentionally strict.

Supported top-level block types:

- `paragraph`
- `heading`
- `bullets`
- `section_banner`
- `callout`
- `table`
- `page_break`
- `raw_docx_xml` only when `--allow_raw_ooxml` is explicitly supplied

Lists must stay as lists. Do not compress bullet content into comma-separated scalar text.

`raw_docx_xml` exists for exceptional OOXML cases only and should not be the normal path.

## Setup

From the skill root:

```bash
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap.ps1
```

Fallback setup:

```bash
./scripts/bootstrap.sh
```

Quick checks:

```bash
node -e "require('docx'); console.log('docx ok')"
python -c "import fitz, lxml, docx, jsonschema; print('python deps ok')"
python scripts/preflight.py --mode branded --qa thorough
```

## Standard creation flow

1. Decide whether the request is `branded` or `simple`.
2. Build a JSON spec that matches `references/spec-schema.json`.
3. Generate the document.
4. Run the appropriate validation depth for the risk level.

Examples:

```bash
python scripts/generate_docx.py --mode branded --input spec.json --output output.docx
python scripts/generate_docx.py --mode simple --input spec.json --output output.docx
```

Supported QA levels:

- `--qa fast`
- `--qa thorough`
- `--qa auto`
- `--qa none`

Interpretation:

- `fast`: semantic checks plus layout lint
- `thorough`: semantic checks, layout lint, and visual contact-sheet review
- `auto`: adds the contact-sheet pass only when lint says the layout risk is high
- `none`: generation only

Use `fast` for short, low-risk, mostly textual documents. Use `thorough` for final, externally shared, structurally dense, or layout-sensitive outputs.

## Font embed rules

Use [scripts/embed_font.py](./scripts/embed_font.py) when:

- the chosen themed result depends on a non-default font
- a real TTF file is available
- preserving that font in Word or Word Online matters

Expected behaviour:

- package the obfuscated font at `word/fonts/font1.odttf`
- register the chosen display font in `word/fontTable.xml`
- write explicit fallback metadata
- exit cleanly without failure if no TTF is configured

## Repair and inspection tools

Use the package utilities directly when the task is not just fresh generation:

- `scripts/validate_docx.py`
- `scripts/layout_lint.py`
- `scripts/render_docx.py`
- `scripts/render_contact_sheet.py`
- comment helpers
- tracked-change helpers
- pack/unpack helpers

Reference material:

- [references/design-standards.md](./references/design-standards.md)
- [references/qa-checklists.md](./references/qa-checklists.md)
