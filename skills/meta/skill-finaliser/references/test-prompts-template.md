# `tests/prompts.md` template

Use this as a baseline when creating a manual regression checklist for a skill.

Keep it short. Aim for 5 to 10 prompts.

```md
# Test prompts

## 1. Happy path
Prompt: "..."
Expected:
- ...
- ...

## 2. Source-of-truth rule
Prompt: "..."
Expected:
- ...
- ...

## 3. Boundary or exclusion
Prompt: "..."
Expected:
- ...

## 4. Failure or missing input
Prompt: "..."
Expected:
- ...
- ...
```

Guidance:

- use plain English, not machine assertions
- describe what the skill should do, not every internal implementation detail
- make sure at least one prompt checks the bundled-guidance rule when the skill depends on `references/` documents
- make sure at least one prompt checks an exclusion, refusal, or stop condition when the skill has one
