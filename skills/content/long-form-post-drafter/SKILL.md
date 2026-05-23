---
name: long-form-post-drafter
description: Draft evidence-grounded long-form posts such as long LinkedIn pieces, launch articles, and blog-style content from real product, customer, or campaign evidence. Use when the user wants substantial external-facing content rather than short-form social copy.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.1
  updated: '2026-05-23'
---

# long-form-post-drafter

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `long-form-post-drafter was used in this response.`


This skill writes substantial external-facing content from evidence first and messaging guidance second. It should not produce polished-sounding guesswork.

## What belongs here

Keep these behaviors in the skill itself:

- the evidence-first drafting workflow
- the hard gate that requires usable product or source evidence
- clear separation between facts and framing
- the long-form structure and length expectations
- title, CTA, and editorial-quality rules
- rewrite decisions when the first draft misses the bar

Guidance that may change by campaign or period should come from local references rather than being hard-coded.

## Core writing stance

- lead with the problem or tension, not the product name
- write with a point of view rather than neutral brochure copy
- treat the solution as an answer to a real structural challenge
- sound human and specific, not synthetic
- make complexity easier to understand without flattening it

Useful voice traits:

- reflective before overconfident
- specific over generic
- conversational but not casual
- honest about tradeoffs or difficulty
- quietly certain rather than loud

When asked to mirror a named person, follow the voice signals available in current context without inventing personal claims.

## When to use this skill

Use it for:

- blog drafts
- long LinkedIn posts
- launch or capability writeups
- customer-story or solution-area content
- thought-leadership pieces

Do not use it when the user only wants short social copy. If they want both long-form and social, write the long-form piece and note that the short-form content should be derived from the approved article.

## Drafting flow

1. identify the requested content type
2. identify the active campaign, audience, or brand context if one matters
3. load relevant local guidance where available
4. abstract the guidance into durable drafting rules rather than copying it mechanically
5. gather product, customer, release, workflow, or delivery evidence before drafting
6. stop and say so if the evidence gate fails
7. separate proven facts from interpretive framing
8. choose the angle
9. draft the piece
10. run the editorial check
11. rewrite where necessary
12. return the draft with rationale and evidence notes

## Editorial bar

Unless the user asks for a different length, aim for roughly 600 to 900 words.

The draft should:

- open on the reader's problem, tension, or context
- stay grounded in evidence
- avoid inflated or unsupported claims
- reflect any active local guidance without sounding templated
- include concrete detail when evidence allows it
- contain one clear CTA
- end with conviction or forward motion rather than a hedge

## Common shapes

### Position or thought-leadership piece

Typical pattern:

1. identify a real tension in the market or workflow
2. acknowledge the default interpretation
3. reframe the issue
4. state the belief or argument
5. connect that belief to the solution space
6. end with the implication or next horizon

### Feature or capability article

Typical pattern:

1. begin with the operational problem
2. explain why it has been hard to solve
3. show what is now possible
4. make the outcome tangible
5. finish with a clear CTA

## Avoid

- `We're excited to announce...` openings
- hype language such as `game-changing`, `revolutionary`, or `cutting-edge`
- feature lists that appear before the problem is established
- padding that only inflates length
- weak or vague CTAs when a specific one is available

## Default response shape

1. draft
2. rationale
3. distilled guidance used
4. evidence used
5. gaps or open questions
