---
name: process-document-writer
description: Create or revise formal process documents and structured operating procedures from notes, examples, or existing documents. Use when a user wants a practical SOP, workflow, governance process, runbook, or similar operational document with the final `.docx` generation handled by a dedicated document tool.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.0.0
  updated: '2026-05-21'
---

# Process Document Writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `process-document-writer was used in this response.`


This skill handles process structure and process prose. It should produce documents that read like real operational material: clear, formal, and usable without becoming bloated.

It does not own document rendering. Final `.docx` creation or editing should be handed to a document-generation tool.

## Dependency rule

- use a dedicated document tool for actual Word-document build or edit work
- do not recreate rendering, packaging, or validation logic here
- if the user only needs a draft structure in chat, that is fine
- if they need a finished `.docx`, pass the final build stage onward

## What belongs in this skill

Keep here:

- fresh-document versus update workflow
- default process-document structure
- example-document matching logic
- practical formal writing style
- gap and assumption handling
- dependency on a document tool for final output

Use local references when the user needs alignment to current standards, templates, governance wording, or review expectations.

## Suitable inputs

This skill should handle:

- rough notes
- bullet steps
- workshop outputs
- process descriptions
- existing process documents
- example documents to match in structure or tone

Perfect inputs are not required. Make the best supported interpretation you can.

## Output contract

For each task, produce:

1. a concise in-chat summary of the proposed or updated structure
2. a `.docx` process document when the user wants a final document

The chat summary should not duplicate the whole document.

## Working flow

1. identify whether this is a new document or a revision
2. decide whether existing example documents should shape the output
3. read current bundled standards when current standards matter
4. draft or revise the process structure in plain language
5. pass the final document build or update to the document tool
6. return the finished document plus the short summary

## Default structure

Unless the source material clearly calls for something else, a process document will usually contain:

1. title
2. version or document-control detail where known
3. overview
4. audience and scope
5. purpose or introduction
6. definitions or classifications when useful
7. the main process sections in working order
8. roles and responsibilities
9. controls, records, or governance requirements where relevant
10. review or maintenance section where relevant

Treat that as a default pattern, not a rigid form.

## What to take from example documents

When the user wants alignment to examples, favor:

- short opening overview
- early audience and scope definition
- section names that match the real process rather than generic consultant language
- separate sections for distinct phases or lifecycle stages
- clear role ownership and sign-off points
- explicit outputs, records, or systems where they matter
- concise prose followed by direct steps, timings, triggers, or decisions

Match structure and tone, not outdated content.

## Writing rules

- use clear UK English
- keep the tone formal but practical
- favor direct statements over padded prose
- expose hidden assumptions or dependencies when the source suggests them
- do not fake dates, owners, systems, or controls
- use lifecycle stages where the process naturally has them

## Do not

- invent owners, dates, SLAs, or approvals
- over-formalize a working procedure into policy when that is not what the user asked for
- return a wall of prose when staged sections or steps would read better
- overwrite an uploaded structure unless revision is actually requested
- treat copied ad hoc guidance as authoritative when current standards should come from bundled references
