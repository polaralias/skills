---
name: repository-dissection
description: Dissect an inherited, unclear, or vibe-coded repository and turn it into an explicit documented understanding. Use when Codex needs to map structure, treat docs as unverified claims, validate real runtime behavior, classify mismatches between docs/code/runtime, and bootstrap the first usable documentation foundation.
---

# Repository Dissection

Use this skill to take a repository from implicit, folklore-driven, or vibe-coded understanding to explicit, documented understanding.

The goal is to make the repository legible enough that later work can proceed against documented reality instead of inherited assumptions.

## Core stance

- Treat documents as claims until verified.
- Treat code as intended behavior until tested.
- Treat generated references and manifest-derived docs as declared surface, not proven behavior.
- Distinguish between:
  - local source truth
  - packaged or deployed runtime truth
  - desired future product truth
- Distinguish between:
  - intended availability
  - current trust level
  - validated replacement behavior

## Use This Instead Of

- Use this skill when the repository is still unclear, inherited, contradictory, or underdocumented.
- Use `repository-knowledge-engineering` once the repository knowledge base exists and the main job is to establish, evolve, or align that system.
- Use `tdd` when the main job is behavior change through red-green-refactor.

## Workflow

### 1. Map the repository before changing it

Start by identifying:

- entrypoints
- runtime layers
- packaging and deployment surfaces
- test locations
- docs/spec locations
- obvious duplicated or conflicting truth sources

### 2. Separate current intent from validated behavior

Read the declared interfaces first:

- README
- setup/config docs
- tool or API references
- runtime launch scripts
- main server entrypoints

Then inspect code that actually defines behavior.

Separate explicitly:

- what the repository currently does
- what the existing docs say it does
- what the project should eventually guarantee

### 3. Verify the real runtime path

Before claiming behavior, determine which path actually runs in the current environment.

Record:

- selected runtime mode
- actual backend command
- whether local source, binary, or package artifact is in use

Do not stop at "it starts". Also verify where state lands, what the public boundary exposes, and whether the docs describe the same runtime story the code actually uses.

### 4. Perform live verification where possible

Prefer black-box checks at the public boundary:

- health endpoint
- auth path
- representative read flows
- representative write flows when safe

Use real credentials only if available and only without writing secrets into repository files.

Classify results precisely:

- success-path verified
- error-path verified
- fixture missing
- validated broken
- validated replacement available

### 5. Classify findings

Group findings into:

- documentation drift
- packaging/runtime drift
- behavior bugs
- missing tests
- architecture debt

Also classify by trust outcome:

- validated runtime behavior
- validated replacement behavior
- confirmed broken runtime behavior
- drift between declared contract and implementation
- intended but still unverified surface

### 6. Bootstrap the first usable knowledge base

When the repository is inconsistent or underdocumented, create or rewrite the minimum knowledge surfaces future work needs.

Good targets include:

- a trustworthy README or root reading order
- a glossary or domain-language file such as `GLOSSARY.md`
- decision notes under `docs/decisions/` when durable trade-offs need to be captured
- a repair or refactor plan
- reliability, security, or operating notes where the runtime story is unclear

Do not create ceremony for its own sake. Create the documentation spine the repository actually needs.

### 7. Stop when the repo is legible

Stop this skill once:

- current runtime truth is documented
- major mismatches are classified
- the first usable knowledge base exists
- the next step is clearly either knowledge engineering, implementation work, or targeted question resolution

## Decision Rules

- If docs and code disagree, do not force one to win early. Preserve the difference until you have enough evidence.
- If tests exist but cannot be executed, count them as potential assets, not proof.
- If no tests exist, say so plainly and treat manual validation artifacts as temporary evidence.
- If the repository is small, favor thoroughness over taxonomy.
- If the repository’s first-contact docs are misleading, rewriting them is part of the dissection, not polish.
- If you create many docs, preserve a short reading order at the root.

## Expected Outputs

- codebase map
- runtime validation record
- mismatch classification
- initial knowledge base or docs spine
- repair or refactor plan
- a clear recommendation for what should happen next
