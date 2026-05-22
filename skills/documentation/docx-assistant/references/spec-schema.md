# DOCX content spec

The preferred authoring path for this skill is: write a compact JSON document description, validate it, then render it through `scripts/generate_docx.py`.

Example:

```bash
python scripts/generate_docx.py --mode branded --input spec.json --output output.docx
```

## Output routes

The schema feeds two renderers:

- `branded`: full themed route with cover, page chrome, section treatments, structured callouts, tables, and optional custom-font embedding
- `simple`: reduced route with ordinary typography and lighter presentation

These routes share the same content model. The mode changes rendering, not the semantic structure of the input.

## Closed block model

Only these top-level block types are valid:

- `paragraph`
- `heading`
- `bullets`
- `section_banner`
- `callout`
- `table`
- `page_break`
- `raw_docx_xml`

Anything else should be rejected.

## Bullet rules

Use a dedicated `bullets` block for list content.

Valid list placement:

- directly in the main block flow
- inside `callout.body`

Invalid list placement:

- banner labels
- banner titles
- banner subtitles
- metadata fields
- cover title or subtitle fields
- callout titles

If the content is list-shaped, keep it list-shaped. Do not flatten it into a single sentence full of commas.

## Raw OOXML rule

`raw_docx_xml` is an advanced escape hatch for package-level or OOXML-specific cases.

Requirements:

- it must be explicitly enabled with `--allow_raw_ooxml`
- it should be used sparingly
- it should not become the default way to represent ordinary layout
