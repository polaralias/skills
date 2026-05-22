# Polaralias Shared Config Contract

Use this file as the canonical key contract for `variables.yaml`.

Consumers should prefer these stable keys before inventing skill-local names.

## Core identity

- `brand_name`
- `footer_text`

## Typography

- `display_font`
- `fallback_font`
- `primary_font_ttf`

Use `primary_font_ttf` when the consuming skill needs an actual font file path, not just a family name.

## Logo and icon assets

- `logo_path`
- `logo_inverse_path`
- `logo_protected_path`
- `accent_icon_path`

Use the most specific available key for the target output. If a skill only needs a general logo path, use `logo_path`.

## Palette

- `palette.primary`
- `palette.secondary`
- `palette.accent`
- `palette.text`
- `palette.muted`
- `palette.surface`
- `palette.neutral_dark`
- `palette.neutral_light`

Not every skill needs every palette key. Missing values should fall back to packaged defaults.

## Tone

- `tone.adjectives`
- `tone.avoid`

## Skill-specific asset paths

- `assets.docx_theme_logo_path`
- `assets.docx_theme_logo_protected_path`
- `assets.docx_theme_accent_icon_path`
- `assets.docx_theme_primary_font_ttf`
- `assets.remotion_brand_reference_path`
- `assets.report_cover_image_path`

## Mapping guidance

For `docx-assistant`, these keys map cleanly to the documented theme inputs:

- `brand_name` -> `DOCX_THEME_BRAND_NAME`
- `display_font` -> `DOCX_THEME_DISPLAY_FONT_NAME`
- `fallback_font` -> `DOCX_THEME_FALLBACK_FONT_NAME`
- `primary_font_ttf` or `assets.docx_theme_primary_font_ttf` -> `DOCX_THEME_PRIMARY_FONT_TTF`
- `logo_path` or `assets.docx_theme_logo_path` -> `DOCX_THEME_LOGO_PATH`
- `logo_protected_path` or `assets.docx_theme_logo_protected_path` -> `DOCX_THEME_LOGO_PROTECTED_PATH`
- `accent_icon_path` or `assets.docx_theme_accent_icon_path` -> `DOCX_THEME_ACCENT_ICON_PATH`

If both a general key and a skill-specific asset key are present, prefer the skill-specific key for that skill.
