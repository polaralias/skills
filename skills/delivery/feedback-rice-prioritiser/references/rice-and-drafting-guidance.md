# RICE and drafting guidance

## Drafting standard

Use this as the default shape for the draft shown in chat when the user wants a RICE item, backlog task, feature request, or prioritised feedback note.

### Proposed title
`[Feature] Short problem summary`

### Problem
Clear description of the problem and why it happens.

### User impact
Who is affected and what goes wrong in practice.

### Example
Concrete scenario if one helps explain the issue.

### Proposed improvement
The clearest product change that would reduce the pain.

### Why it matters
Operational, commercial, product, or UX value.

### Inferred metadata
- Feature
- Affected customers or users
- Affected apps/surfaces
- Priority signal

## Title pattern

Use the strongest confirmed or most confidently inferred feature in square brackets.

Examples:
- `[Badge] Badge reporting makes active vs expired status hard to interpret`
- `[Events] Event import makes timezone changes easy to misconfigure`
- `[Reports] Permissions make cross-team reporting hard to manage`

## RICE guidance

### Reach

Estimate how broadly the issue matters:
- how many customers
- how many end users
- how many admins
- how many workflows
- how often the pain occurs

If exact numbers are unavailable, use a bounded qualitative estimate and say why.

### Impact

Assess the likely value of fixing it:
- trust
- time saved
- error reduction
- support load reduction
- compliance confidence
- adoption
- retention or churn risk

### Confidence

State how certain the evidence is:
- direct customer evidence
- repeated signal across multiple customers
- one anecdote only
- inferred root cause
- known gap vs speculative improvement

### Effort

Estimate implementation weight broadly:
- low
- medium
- high

Only be more specific if the user already has engineering context.

## Safe behaviour

- Never present weak evidence as a strong RICE score.
- If evidence is thin, say so explicitly.
- Use RICE to clarify trade-offs, not to manufacture precision.
- If multiple feedback items clearly belong to one broader theme, say so instead of forcing duplicate backlog entries.
