# Generic QA Output Template

## Parent plan pattern

**Name:** `<PREFIX>-TP-001 - <Feature or story title> - Test Plan`

### Source

- primary source: `<story, ticket, spec, or requirement reference>`
- feature area: `<feature or component name>`

### Overview

`<1 to 3 sentences on the behaviour under test from a user or system perspective>`

### Scope

In scope:

- `<item>`

Out of scope:

- `<item>`

### Key risks

- `<risk>`

### Test approach

- UI or interaction coverage: `<high-level note>`
- data validation and persistence: `<high-level note>`
- access control: `<if relevant>`
- integrations or release behaviour: `<if relevant>`
- accessibility families: `<only where relevant>`

### Test data

- `<accounts, roles, seeded records, content states, or setup notes>`

### Environment

- `<environment and notable configuration detail>`

### Baseline comparison

- baseline reference: `<name or N/A>`
- parity notes: `<intentional differences or N/A>`

## Child case pattern

**Name:** `<PREFIX>-TC-### - <Short action-oriented title>`  
Parent: `<PREFIX>-TP-001`

### Context

- area, screen, or workflow: `<where it runs>`
- requirement reference: `<AC, requirement, or direct-risk note>`

### Objective

`<what this case proves>`

### Preconditions

- `<setup required>`

### Steps

1. `<action>`
2. `<action>`
3. `<action>`

### Expected results

- `<clear result linked to the steps>`

### Execution type

- Manual / Automated / Either

### Notes

`<only when needed>`

## ID rules

- the parent plan is always `TP-001`
- test cases are zero-padded and sequential
- the prefix should remain stable across the whole set
