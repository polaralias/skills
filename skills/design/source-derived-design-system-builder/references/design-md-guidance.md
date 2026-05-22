# DESIGN.md guidance

Use this file when creating the companion `DESIGN.md`.

The goal is to produce a persistent, structured design-system file that coding agents can reuse across sessions.

## File structure

A `DESIGN.md` file has two layers:

1. YAML front matter for machine-readable tokens
2. Markdown body for human-readable rationale

The tokens are the normative values. The prose explains how to apply them.

## Recommended token fields

At minimum:

```yaml
---
name: <system name>
description: <short description>
colors:
  primary: "#000000"
  secondary: "#666666"
typography:
  h1:
    fontFamily: <font>
    fontSize: <size>
  body-md:
    fontFamily: <font>
    fontSize: <size>
rounded:
  sm: 4px
  md: 8px
spacing:
  sm: 8px
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
---
```

Add only what is stable enough to be useful. Do not invent token precision where the source does not support it.

## Recommended markdown sections

When present, keep this order:

1. `## Overview`
2. `## Colors`
3. `## Typography`
4. `## Layout`
5. `## Elevation & Depth`
6. `## Shapes`
7. `## Components`
8. `## Do's and Don'ts`

## What DESIGN.md should capture

- stable token values
- stable visual rationale
- how to use the system
- what the primary hierarchy is
- how interaction or emphasis works
- what should not happen

## What DESIGN.md should not try to do

- it is not a full product specification
- it is not a bag of screenshots
- it is not a workflow guide
- it is not a component implementation library
- it is not a substitute for `SKILL.md`

## Relationship to SKILL.md

Use `SKILL.md` for:
- when to use the system
- what source material to inspect first
- what areas are extrapolated
- live-authority warnings
- system boundaries

Use `DESIGN.md` for:
- tokens
- rationale
- durable application guidance
