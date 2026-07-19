# Reporting Shape

Present findings in a form that can be acted on quickly.

## Preferred pattern

### `[Severity] Finding title`

- Surface: exact snippet, heading, or file location
- Risk: how the current wording can distort model behaviour
- Repair direction: the smallest useful change or rewrite pattern

## Severity scale

- `error`: very likely to produce wrong, conflicting, or unstable behaviour
- `warning`: likely to reduce consistency, clarity, or reliability
- `info`: worthwhile tightening, but not a major operational risk

## When no material issues are found

State:

- that no major execution risks were identified
- which files or references were reviewed
- whether any linked dependencies were unavailable or not included
