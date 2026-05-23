---
name: feedback-rice-prioritiser
description: Turn messy customer or user feedback into a clean, product-ready problem statement and prioritisation draft. Use when a user shares feedback and wants a structured RICE item, feature request, backlog candidate, or prioritised product note. The skill explains and applies RICE, asks for missing confirmations when needed, and can prepare a tracker-ready handoff without assuming one specific tool.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.1
  updated: '2026-05-23'
---

# feedback-rice-prioritiser

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `feedback-rice-prioritiser was used in this response.`


Convert messy feedback into a clean, product-ready prioritisation draft.

## Core idea

This skill does two related jobs:

1. Turn raw feedback into a clear product problem statement.
2. Frame that problem for prioritisation, using RICE where appropriate.

RICE is useful here as a decision aid, not as fake precision. Use it to expose trade-offs and missing evidence, not to pretend certainty where none exists.

## What RICE means

RICE stands for:

- **Reach**: how many users, customers, teams, or workflows are affected in a meaningful period
- **Impact**: how much the improvement would change the user experience, efficiency, trust, revenue, risk, or adoption
- **Confidence**: how strong the evidence is for the problem, the root cause, and the expected benefit
- **Effort**: how much work the change is likely to take across product, design, engineering, data, QA, or rollout

If the user wants a strict RICE format, include all four dimensions explicitly. If they only want a structured feature request or backlog draft, still use RICE thinking to shape the output even if you do not score it numerically.

## Workflow

1. Analyse the user-provided feedback.
2. Infer the likely feature area, affected users, and affected surfaces.
3. Draft the write-up in chat.
4. Add a RICE view:
   - either a qualitative RICE read
   - or a scored RICE draft if the user asked for scoring
5. Stop and ask for confirmation or missing evidence where needed before any tracker-ready handoff.

Never skip the confirmation step when key metadata is unresolved.

## Accepted input

Treat any of the following as valid input:
- pasted customer quotes or summaries
- internal notes
- screenshots described in chat
- meeting notes
- transcripts
- call summaries
- support summaries
- mixed, messy feedback from multiple customers or users

Do not complain about rough input. Extract the signal and move on.

## Step 1: Analyse the feedback

Read the material and infer:
- the core problem
- the user impact
- the likely feature area
- any likely affected customers, user types, or audiences
- any likely affected apps, product surfaces, or workflows
- whether the issue sounds urgent, recurring, blocked, or commercially important

Be explicit about uncertainty. Mark anything not directly stated as inferred.

## Step 2: Produce the draft in chat

Write a concise draft suitable for a RICE item, feature request, backlog note, or tracker-ready issue.

Use this structure by default:

### Proposed title
`[Feature] Short problem summary`

### Problem
2 to 4 short paragraphs describing what is going wrong and why it is painful, risky, or expensive.

### User impact
Explain who is affected and what friction, confusion, rework, reporting risk, delay, or operational pain it causes.

### Example
Include a concrete example when the feedback supports one. If a timezone, reporting, import, permission, or workflow edge case is central to the issue, make the example specific.

### Proposed improvement
State the clearest product change that would reduce the pain.

### Why it matters
State the value in product terms such as lower support load, fewer errors, better trust, improved adoption, lower admin effort, reduced churn risk, or stronger compliance confidence.

### Inferred metadata
Include:
- **Feature:** <best-guess feature tag or tags>
- **Affected customers / users:** <confirmed or inferred list>
- **Affected apps / surfaces:** <confirmed or inferred list>
- **Priority signal:** <Unknown until confirmed>

Keep the tone factual and product-facing. Do not write like a support reply.

## Step 3: Add the RICE view

If the user asked for RICE explicitly, include:

### RICE assessment
- **Reach:** [estimate or qualitative statement]
- **Impact:** [high / medium / low or a short explanation]
- **Confidence:** [high / medium / low with reason]
- **Effort:** [high / medium / low or rough estimate]

### RICE reasoning
Explain what evidence supports each part and where the evidence is weak.

### Priority recommendation
State one of:
- pursue now
- investigate further
- keep in backlog
- merge with a broader theme
- do not prioritise yet

If the user did not ask for explicit RICE, keep the same logic but compress it into:

### Prioritisation read
- likely reach
- likely impact
- evidence confidence
- likely effort
- recommendation

## Step 4: Hard stop and ask for confirmation

After the draft, stop and ask for the missing confirmations before any tracker-ready handoff.

Ask for all unresolved items in one short follow-up, such as:

- confirm or correct the proposed title
- confirm or correct the feature area
- name any affected customers, user groups, or audiences
- name any other affected apps or surfaces
- confirm whether this should be treated as a priority item
- confirm whether to prepare a tracker-ready version now

If the user only partially answers, update the draft and ask only for the missing items.

If the user corrects the feature, title, customers, or apps, treat the correction as the new source of truth.

## Step 5: Prepare tracker-ready handoff if requested

Once the user has explicitly confirmed, prepare a tracker-ready handoff.

This skill does not assume one fixed tracker. The handoff should include:

- approved title
- final approved description
- feature tags
- affected customers, users, or surfaces
- priority signal
- optional RICE section if requested

If the user names a specific tool such as ClickUp, Linear, or Notion, shape the output so it can be pasted or created there cleanly. If no tool is named, return a neutral copy-ready block.

## Gating rules

Do not prepare a final tracker-ready payload while any of these are still unresolved:
- no confirmed feature area
- no confirmed affected customer, user group, or app/surface when those matter to the prioritisation
- priority not answered when the user is asking for backlog triage rather than just drafting

If the evidence is weak, still produce a useful draft, but mark assumptions clearly.

## Output quality rules

- Keep the draft concise but specific.
- Separate evidence from inference.
- Prefer product language over support language.
- Do not overstate reach or urgency if the evidence is weak.
- Call out hidden risks when obvious from the feedback.
- When feedback is weak or vague, still produce a draft, but mark assumptions clearly.

## Resources

- `references/rice-and-drafting-guidance.md`: default shape for the product-facing draft and the RICE framing
