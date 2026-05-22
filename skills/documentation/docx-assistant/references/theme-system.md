# Theme guide

This file defines the reusable visual contract for the richer document route.

## Design intent

The document system should feel:

- composed
- legible
- modern without being flashy
- structured enough to guide scanning

The goal is a repeatable page language, not decorative improvisation.

## Layout grammar to preserve

These ideas should survive even when colours, fonts, or logos change:

- a distinct opening page
- restrained running identity on body pages
- clear section-entry rhythm
- compact information bars
- a consistent family of semantic callouts
- tables designed for reading, not ornament

## Route split

The package has two visual tiers.

### Simple route

Use this for low-friction outputs where clarity matters more than identity.

Expected characteristics:

- default or system fonts
- minimal page chrome
- straightforward headings
- no rich cover or visual callout system

### Branded route

Use this when the document should feel intentionally designed.

Expected characteristics:

- configurable visual identity
- display-font hierarchy
- cover plus running chrome
- shared banner/callout/metadata patterns

Do not water this route down into a token logo pass.

## Typography

The richer route supports an optional custom display font.

Inputs:

- `DOCX_THEME_DISPLAY_FONT_NAME`
- `DOCX_THEME_PRIMARY_FONT_TTF`
- `DOCX_THEME_FALLBACK_FONT_NAME`

Recommended baseline without a custom kit:

- display: `Aptos Serif` or `Georgia`
- body: `Arial` or `Aptos`

If a custom TTF is provided and permitted for embedding, package it. If not, continue with fallbacks rather than failing the whole build.

## Colour behaviour

The theme should support:

- one dominant accent for labels and signals
- one secondary accent for separators or underlines
- dark primary text
- pale support surfaces for panels

Avoid combinations that reduce readability.

## Brand assets

Optional inputs:

- `DOCX_THEME_LOGO_PATH`
- `DOCX_THEME_LOGO_PROTECTED_PATH`
- `DOCX_THEME_ACCENT_ICON_PATH`
- `DOCX_THEME_BRAND_NAME`

If assets are missing, omit them gracefully. Do not invent fake branding.

## Cover and running identity

Recommended opening-page pattern:

- logo if available
- large title in the display face
- supporting subtitle or metadata
- no competing running header/footer chrome on the same page

Recommended body-page pattern:

- lighter repeated identity
- clear visual spacing
- support structure that helps navigation but does not dominate

## Shared UI pieces

The following elements should feel like one system:

- section banners
- metadata bars
- `visual`
- `key_info`
- `takeaway`
- `warning`
- `tip`

Change their styling through the theme, not by inventing a new component family for each document.
