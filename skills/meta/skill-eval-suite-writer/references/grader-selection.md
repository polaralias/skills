# Choosing Graders

Pick the lightest grader that can prove the behaviour you care about.

## Prefer simple checks first

Use straightforward graders when possible:

- required or forbidden text checks
- artefact existence checks
- schema validation
- limits on tools, turns, runtime, or token budget

## Use richer checks only where needed

Escalate when simple assertions cannot express the requirement:

- diff-based checks when concrete file edits matter
- model-judged or prompt-judged checks for semantic quality
- trigger checks when routing behaviour is the main target
- tool-usage checks when process matters as much as output

## Good suite shape

Most strong suites use:

- a small set of global guardrails
- targeted graders for the parts most likely to fail

Avoid redundant grading. If several graders are proving the same point, keep the clearest one.
