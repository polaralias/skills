# Delivery checklist

Use this file as the final shipping gate for generated `.docx` files.

## Themed output checks

- The opening page has a readable hierarchy.
- Any configured logo or mark renders at the expected scale and is not distorted.
- The cover is not fighting with running headers or footers.
- The section-entry treatment, info bars, and callout family look internally consistent.
- The chosen display font appears where expected when embedded, or the fallback result still reads cleanly.

## Font package checks

- `word/fonts/font1.odttf` exists when a custom font was requested.
- `word/fontTable.xml` contains the configured display-font entry.
- fallback font metadata is present
- the output is not relying on an obsolete custom-font route

## Layout checks

- headings do not crash into banners, tables, or panels
- bullets are real bullets
- tables stay within the page and remain readable
- there is no accidental duplication of cover and body chrome across sections

## Comment and threading checks

- The authoritative main document part is `word/document.xml` after replies are added or comments are repaired.
- No `[trash]/*` co-authoring residue remains in the final package.
- Every `w15:commentEx` `w15:paraId` resolves to a paragraph in its comment.
- Every `w15:paraIdParent` resolves to a top-level parent comment key.
- Comment metadata retains its namespace declarations and `mc:Ignorable` prefixes.
- The final document passes `scripts/validate_docx.py` without structural errors.
- For review deliverables, replies—especially replies to multi-paragraph comments—have been confirmed as nested in desktop Word without a repair prompt.

## Hold-the-file conditions

Do not ship the document if:

- a required logo or mark is missing or visibly wrong
- a required custom font was not embedded
- page chrome conflicts with the cover
- layout lint still reports unresolved serious issues
- threaded replies are unresolved, display as top-level comments, or cause Word to offer a repair
