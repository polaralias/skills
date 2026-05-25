# License Selection

Use this file before writing `LICENSE`.

This skill is intentionally opinionated around a short list of licenses that fit common bootstrap cases. The user can still choose something else, but do not improvise unfamiliar license text.

## Source basis

These summaries are based on the current Choose a License pages:

- MIT: [choosealicense.com/licenses/mit](https://choosealicense.com/licenses/mit/)
- Apache-2.0: [choosealicense.com/licenses/apache-2.0](https://choosealicense.com/licenses/apache-2.0/)
- GPL-3.0: [choosealicense.com/licenses/gpl-3.0](https://choosealicense.com/licenses/gpl-3.0/)
- AGPL-3.0: [choosealicense.com/licenses/agpl-3.0](https://choosealicense.com/licenses/agpl-3.0/)

## Practical defaults

### Apache-2.0

Use when the user wants:

- commercial-friendly reuse
- preservation of copyright and license notices
- a `NOTICE` mechanism for attribution
- a patent grant

This is the best default when the user wants "people can use it, including commercially, but notices and attribution should remain intact."

### MIT

Use when the user wants:

- maximum simplicity
- maximum reuse flexibility
- only a thin notice-preservation requirement

Do not default to MIT when the user explicitly cares about stronger attribution handling than bare notice retention.

### GPL-3.0

Use when the user wants strong copyleft for distributed derivatives.

Do not use when the user wants broad commercial adoption without reciprocal licensing obligations.

### AGPL-3.0

Use when the user explicitly wants network-use copyleft as well as distributed copyleft.

Do not use when the user is concerned that companies may avoid the project because of licensing friction.

## Decision rule

Ask or infer the narrowest stable requirement:

- "commercial-friendly with preserved notices" -> `Apache-2.0`
- "ultra-simple permissive" -> `MIT`
- "derivatives must stay open when distributed" -> `GPL-3.0`
- "hosted modified versions must also publish source" -> `AGPL-3.0`

If the requirement is still ambiguous, do not guess between permissive and copyleft.
