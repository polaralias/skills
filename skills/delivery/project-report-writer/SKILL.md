---
name: project-report-writer
description: Build project reports from the freshest credible delivery signals available, then validate them against structured execution data and durable project context. Use when the user wants a status report, health view, launch-readiness picture, risk summary, milestone review, or similar project reporting output. Shorthand PRW.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: 1.2.1
  updated: '2026-05-24'
---

# project-report-writer

Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.

This skill produces chat output. Include this proof line in the response: `project-report-writer was used in this response.`


This skill writes concise internal project reporting from fresh signals first, structured execution evidence second, and durable project context third.

## Output families

Infer the report shape from the request. Common modes are:

- balanced project report
- health or RAG report
- status update
- blockers and risks report
- launch-readiness report
- executive snapshot

Always return a text report in chat first.

If the user wants a visual output, still produce the text report first and treat the visual layer as a follow-on built from the same evidence.

## Shared branding config

Before the first branded visual run, check for shared Polaralias config in this order:

- `docs/agents/polaralias-skills.md`
- `docs/agents/polaralias-variables.yaml`
- `~/.agents/config/polaralias-skills/profile.md`
- `~/.agents/config/polaralias-skills/variables.yaml`
- `~/.config/polaralias-skills/profile.md`
- `~/.config/polaralias-skills/variables.yaml`

If any of those files exist, read the relevant ones before asking the user to restate branding choices.

Use shared variables for reusable typography, logo, palette, footer text, and report-cover asset paths when they are present.

Use explicit user instructions for the current job over any saved defaults.

If no shared or repo-local config exists, continue with the packaged defaults and say that no shared Polaralias variables were found, so defaults were used.

After doing that, ask the user whether they want to run `setup-polaralias-skills` so future runs can reuse shared defaults.

## First-use branding prompt

For the first branded visual run in a new environment, ask:

`Do you want me to keep the default report styling, or update this skill with your own branding rules, fonts, colours, logos, and visual defaults first?`

If the user wants shared defaults across repositories, use `setup-polaralias-skills` rather than writing persistent branding into the installed skill package.

If the user wants a repo-specific override instead, collect or update those rules in the repo-local override files before generating the visual output.

## Evidence order

Respect the requested reporting window. Then use evidence in this order:

1. fresh communications to establish the latest credible position
2. board or tracker data to validate and quantify progress
3. project context documents and notes for supporting detail

If fresh communication and the board disagree, name the mismatch instead of smoothing it over.

## When to block instead of guessing

If the necessary execution signal is missing, do not write a pseudo-report. Return a short blocked shell identifying:

- the project
- what signal is unavailable
- what the report is blocked by
- the next concrete action needed

## Working flow

### 1. Resolve the project confidently

Use the project name, customer name, alias, index entry, or `PROJECT.md` anchor. If the match is uncertain, clarify before proceeding.

### 2. Read fresh communication first

Look for the newest credible signals inside the requested time range:

- blockers
- decisions
- risk changes
- scope changes
- sequencing changes
- stakeholder sentiment
- sign-off or launch confidence
- replan signals

Form a preliminary internal view from comms before reading the board.

### 3. Read board or tracker data

If there is no structured execution source, stop and return the blocked shell.

Use the board to quantify and validate:

- current progress
- milestone position
- active blockers
- stale work
- recent completions
- overdue items

Capture only the fields needed to support the report.

### 4. Read supporting context

Use `PROJECT.md`, meeting notes, transcripts, plans, or decision logs to explain and support the current picture, not to override fresher evidence without good reason.

### 5. Set the health view

Health is one component of the report, not the whole report.

Base it on:

- completion position
- milestones slipped or at risk
- blockers
- fresh comms that materially reframe the current position

### 6. Write the report

Write for an internal audience unless the user asks otherwise.

The report should normally cover:

- overall status
- current position
- progress
- milestones
- blockers and risks
- dependencies
- decisions or changes
- next actions
- data gaps

Keep it direct, evidence-based, and concise.

### 7. Offer the visual version when asked

If the user wants slides, HTML, a deck, or a visual summary, treat that as a second step after the text report.

Use:

- [visual-generation-process.md](./references/visual-generation-process.md)
- [visual-reporting-principles.md](./references/visual-reporting-principles.md)

Those references own the visual build logic and presentation rules.

## Important working rules

- freshness is a core rule
- structured board data is the main execution signal once the latest position is understood
- `PROJECT.md` and notes are supporting context
- if data feels thin or suspiciously incomplete, say so
- if a recent thread materially changes the picture, reflect that clearly
- if the canonical project context looks stale, route to `project-context-builder` or tell the user exactly what needs refreshing
