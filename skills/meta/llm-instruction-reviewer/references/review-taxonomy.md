# Review Lenses

Use these lenses to decide whether an instruction artifact is likely to execute cleanly.

## Rule collisions

Look for places where the model could obey one rule only by violating another.

Common forms:

- direct statement-to-statement conflict
- unclear priority ordering
- impossible combinations of constraints
- output requirements that point in different directions
- refusal or safety instructions that clash with the stated behavior

Representative patterns:

- concise answer vs exhaustive answer
- never ask questions vs always clarify first
- JSON only vs prose explanation required

## Meaning uncertainty

Flag wording that depends too much on interpretation.

Typical signals:

- soft quantities such as `briefly`, `some`, or `a few`
- vague quality bars such as `high quality` or `professional`
- pronouns or references with unclear targets
- missing boundaries, exceptions, or precedence

Good repairs replace guesswork with explicit rules, thresholds, or examples.

## Voice and operating stance

Check whether the file asks the model to sound or behave in ways that do not fit together.

Examples:

- warm and conversational in one place, rigid and terse elsewhere
- deferential phrasing paired with highly assertive behavior
- confident tone without uncertainty handling

Raise this only when it can affect outputs, not when it is just a branding preference.

## Execution burden

Models become unreliable when too many rules must be held in working memory at once. Watch for:

- deep nesting
- long paragraphs encoding branching logic
- many simultaneous constraints without ordering
- scattered exceptions that silently override earlier rules

The right fix is usually better structure, not more words.

## Missing behavior coverage

Ask where a capable model would still have to guess.

Typical gaps:

- likely user variants not addressed
- incomplete or messy input
- refusal, fallback, or recovery behavior
- what to do when constraints cannot all be satisfied

## Multi-file drift

Where several files jointly define behavior, examine the combined surface for:

- duplicate rules with different wording or meaning
- inconsistent formatting requirements
- voice drift between files
- hidden assumptions about which file wins

If not all linked files were available, mark the composition review as incomplete.

## Additional user criteria

If the user names extra checks, treat them as equal in importance to the core lenses. Examples include:

- schema discipline
- citation quality
- trigger precision
- tool-use limits
- policy alignment
