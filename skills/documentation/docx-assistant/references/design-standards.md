# Document design rules

## Core rules

- Favour readability over novelty.
- Keep headings in sentence case unless the request says otherwise.
- Maintain stable spacing and sensible line lengths.
- Prefer real Word constructs over visual hacks.

## Rich/themed outputs

When using the richer route:

- keep the cover, section rhythm, information bars, and callout system aligned
- reserve the display face for high-value hierarchy
- keep body copy on dependable office-safe fonts
- avoid header/footer competition with the opening page

## Font handling

- Use `scripts/embed_font.py` when the visual result depends on a real custom font.
- Keep explicit fallback metadata in the package.
- If no custom font file exists, complete the build with a sane fallback rather than treating that as fatal.

## Tables, banners, and panels

- Tables must remain readable at page width.
- Callouts should communicate meaning, not just add colour.
- Section banners should mark transitions, not carry long content payloads.

## When to treat a document as high risk

Escalate QA when the document contains things like:

- several tables
- wide tables
- multiple images
- many repeated panels
- several section changes
- manual OOXML injections
- heavy header/footer manipulation
