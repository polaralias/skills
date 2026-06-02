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

## Structured output and tracker preferences

- `delivery.issue_tracker`
- `delivery.publish_recommendation`
- `delivery.default_project`
- `delivery.default_team`
- `delivery.epic_label`
- `delivery.feature_label`
- `delivery.task_label`
- `delivery.issue_type_map.epic`
- `delivery.issue_type_map.feature`
- `delivery.issue_type_map.task`
- `delivery.fields.parent`
- `delivery.fields.labels`
- `delivery.fields.area`
- `delivery.fields.priority`
- `delivery.fields.acceptance_criteria`
- `delivery.fields.notes`

Use these keys when a consuming skill needs issue-ready or tracker-ready output.
Missing values should fall back to the skill's packaged defaults or the current user's explicit instructions.

## Continuity and hook preferences

- `continuity.preferred_mode`
- `continuity.transcript_backup_root`
- `continuity.manifest_relative_path`
- `continuity.restart_supplement_relative_path`
- `continuity.handoff_relative_dir`
- `continuity.handoff_filename_pattern`
- `continuity.precompact_capture_enabled`

Use these keys when a consuming skill needs shared defaults for hook-aware continuity, transcript backup location, deterministic manifest paths, or preferred verbose handoff behavior during compaction-aware flows.
Missing values should fall back to the skill's packaged defaults, project-local hook config, or the current user's explicit instructions.

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

## Delivery guidance

For `doc-driven-development`, these keys support issue-ready packaging without making tracker formatting the main method:

- `delivery.issue_tracker` -> preferred publication target such as GitHub, Linear, or local markdown
- `delivery.publish_recommendation` -> whether the skill should explicitly recommend publishing once packages are stable
- `delivery.default_project` and `delivery.default_team` -> default routing hints when the user does not restate them
- `delivery.issue_type_map.*` -> preferred naming for epic, feature, and task layers
- `delivery.fields.*` -> preferred field names for parent links, labels, area, priority, acceptance criteria, and notes

Consumers should still prefer direct user instructions over shared defaults.

## Continuity guidance

For hook-aware consumers such as `engineering-workflow-orchestrator`, `local-handoff`, or future continuity helpers, these keys should be interpreted as:

- `continuity.preferred_mode` -> default handoff depth such as `standard` or `max`
- `continuity.transcript_backup_root` -> preferred user-level root for raw transcript backup artifacts
- `continuity.manifest_relative_path` -> project-relative manifest path that `PostCompact` or restart helpers should read
- `continuity.restart_supplement_relative_path` -> project-relative path for the short post-compact restart supplement
- `continuity.handoff_relative_dir` -> preferred project-relative handoff directory when continuity hooks generate or refresh a handoff
- `continuity.handoff_filename_pattern` -> naming convention template for deterministic handoff creation
- `continuity.precompact_capture_enabled` -> whether the user wants the richer continuity flow enabled by default when a host supports it

Consumers should treat raw transcript backups as the authority record, and derived verbose handoffs or restart supplements as secondary artifacts built for restart convenience.
