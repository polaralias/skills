# Prompt checks

## 1. New themed file

Prompt:
`Create a branded DOCX implementation summary from these notes.`

Expected behaviour:

- the result is a `.docx` artifact rather than only chat output
- the richer route is chosen automatically
- the document uses the full themed system rather than a token accent pass
- major heading hierarchy follows the configured display-font logic when available
- the document uses shared structural pieces instead of collapsing into plain text pages

## 2. Explicit plain file

Prompt:
`Create a simple plain DOCX version of this document.`

Expected behaviour:

- the simple route is used because the prompt explicitly asked for it
- the result stays minimal and utilitarian
- richer theming is not added unnecessarily

## 3. Safe document editing

Prompt:
`Update this uploaded Word document with the reviewer comments and preserve the existing formatting.`

Expected behaviour:

- existing structure and styling remain intact unless the user requests otherwise
- comment, tracked-change, and repair utilities are preferred over flattening the file into plain text

## 4. Package hygiene

Prompt:
`Check that this DOCX skill is still production ready after script changes.`

Expected behaviour:

- smoke and validation paths are still obvious
- generated transient folders such as `node_modules` and `__pycache__` are not left behind inside the packaged skill
