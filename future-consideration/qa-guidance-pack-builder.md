# QA Guidance Pack Builder

This is a future-skill candidate.

## Why it is here

This is a useful pattern for turning a team's QA method into a reusable guidance pack that can steer a generic test-plan-writing skill without hard-coding organisation-specific process into the base skill.

## What seems reusable

- acceptance-criteria coverage as a hard gate
- split-versus-merge rules for test-case decomposition
- conditional coverage families for permissions, data integrity, accessibility, validation, and regression
- output-format tailoring for specific trackers, test-management tools, or MCP connectors
- a light extension model where a base skill can consult local reference files when they exist

## Likely public version

A future public skill could be one of:

- `qa-guidance-pack-builder`
- `test-plan-guidance-pack-builder`
- `qa-method-to-skill-builder`

The useful public version would create:

- `testing-guidelines.md`
- `output-format.md`
- optional domain-specific reference files for coverage patterns
- a base-skill update plan showing where those references should be wired in

## Recommended extension pattern

The clean pattern is:

- keep the base `test-plan-writer` generic
- let the skill briefly reference optional local files such as `references/output-format.md`
- if those files exist, use them
- if they do not exist, stay generic and avoid invented system fields

That keeps the public skill portable while still making local tailoring easy.

## What it should do

- extract a team's real QA standards into reference files
- separate durable method from local tooling specifics
- define output contracts for trackers, test systems, or connector payloads
- keep private examples or local naming out of the public base skill
- make it easy to tailor a generic skill without forking its whole workflow
