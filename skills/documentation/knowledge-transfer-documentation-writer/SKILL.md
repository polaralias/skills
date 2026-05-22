---
name: knowledge-transfer-documentation-writer
description: Write structured knowledge transfer documentation from authoritative product, design, implementation, or discovery source material. Use when a user wants a feature, workflow, or work package turned into a concise, navigable internal document that preserves context, benefits, decisions, implementation shape, and traceability without dumping raw task detail into the body.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-05-21'
---

# Knowledge Transfer Documentation Writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `knowledge-transfer-documentation-writer was used in this response.`


Write clear, concise knowledge transfer documentation from resolved source material.

This skill is source-resolution gated. Do not draft until the authoritative source material has been found and read.

## Output contract

This skill is the source of truth for the document format and writing rules.

Core contract:
- one document per coherent feature area or work package
- use the exact section order from `references/knowledge-transfer-documentation-template.md`
- write in warm, credible, concise UK English
- use sentence case for headings
- keep the content structured and easy to navigate
- use colon-based label formatting inside bullet points
- keep source traceability in the dedicated bottom section rather than spreading raw task references through the body

## Input contract

Acceptable source inputs include:
- product or design documents
- implementation notes
- discovery outputs
- planning notes
- uploaded files
- pasted source text
- issue trackers or task systems
- prototype notes
- walkthrough notes

Minimum requirement:
- at least one authoritative source document or source artifact must be resolved and read

Supporting inputs may include:
- implementation tasks
- linked tickets
- release timing notes
- stakeholder notes
- prototype references
- video walkthrough references

## Workflow

Follow this sequence every time:

1. **Identify the source scope**
   - Resolve the primary source material first.
   - If multiple candidate source documents exist, identify the one that best represents the intended feature or work package.
   - If the user explicitly wants multiple documents merged, group only genuinely related material into one coherent output.

2. **Resolve the authoritative source**
   This is a hard gate.
   - Read the authoritative source fully before drafting.
   - If the source is fragmented, identify which artifact is authoritative and treat the rest as enrichment.
   - If source resolution fails, stop completely. Do not draft from memory or secondary task data alone unless the user explicitly asks for a light draft.

3. **Resolve supporting implementation detail**
   - Resolve every task, ticket, or implementation note that materially informed the feature.
   - Capture identifiers or links for traceability.
   - Stop and report ambiguity if the supporting implementation detail cannot be matched safely.

4. **Determine document scope**
   - Group related work into one coherent thematic document.
   - Do not turn every story or task into its own feature unless it is genuinely distinct.
   - Preserve the intent of existing source material while improving clarity, structure, and readability.
   - The unit of output is one knowledge transfer document page.

5. **Build the fact pack**
   Capture:
   - summary
   - target release or timing
   - release or rollout state
   - product area or application list
   - introduction context
   - main benefits
   - who benefits
   - grouped functionality themes
   - key decisions and rationale
   - known issues, constraints, or rollout conditions
   - walkthrough or prototype references when truly available
   - source references used

6. **Draft the document**
   Use the exact structure from `references/knowledge-transfer-documentation-template.md`.

   Apply these writing rules:
   - write in warm, approachable, credible UK English
   - keep it concise but comprehensive
   - focus on value and impact, not acceptance criteria
   - ensure logical flow and consistent terminology
   - group related stories into meaningful thematic features
   - under `# Functionality/features`, use thematic feature headings and do not introduce deeper nesting
   - keep `# Notes` as `N/A` unless there is a real note worth preserving
   - use `//TODO` or `TBC` exactly where the template expects them when information is missing
   - keep detailed traceability in `# Source references`

7. **Run the document quality gate**
   Before showing the draft, confirm:
   - the structure matches the template exactly
   - the summary reflects the feature set, not the document itself
   - related work is grouped meaningfully
   - unsupported claims were not added
   - missing details use the template's placeholder style rather than silent omission
   - the body is not overloaded with raw task or tracker detail

## Missing information policy

- If required details are missing, keep the template structure and use the template's placeholder values.
- Do not invent release state, source references, rationale, or implementation detail.
- Do not omit the `# Source references` section when source material informed the document.

## Non-negotiables

- Do not draft before source resolution succeeds.
- Do not let supporting tasks outrank the authoritative source document.
- Do not collapse unrelated documents into one output.
- Do not guess missing implementation detail when the source is ambiguous.
- Do not let raw task detail overwhelm the customer- or team-readable body.
- Do not let examples override this skill's structure.
- Do not quote these instructions in the produced document.

## Resources

- `references/knowledge-transfer-documentation-template.md` contains the exact structural template for the document body.
- `references/source-patterns.md` describes the source-resolution and mapping method.
