# Test prompts

## 1. Baseline bootstrap
Prompt: "Use $repo-setup to make this new repo ready to start working in."
Expected:
- the skill inspects the existing repo surface before applying templates
- it chooses a license deliberately rather than blindly
- it applies contributor and agent governance plus PR-based branch protection

## 2. License guidance
Prompt: "Use $repo-setup and help me choose between Apache-2.0 and MIT."
Expected:
- the skill uses the bundled Choose a License summary
- it explains the attribution and commercial-use tradeoff clearly

## 3. WIP description
Prompt: "Use $repo-setup and make sure the GitHub repo gets a description."
Expected:
- the skill sets a concise repo description
- the setup-stage description includes a visible WIP marker

## 4. Existing AGENTS merge
Prompt: "Use $repo-setup, but this repo already has a substantial AGENTS.md."
Expected:
- the skill merges the shared governance block instead of replacing the whole file
- it preserves repo-specific instructions

## 5. Handoff recommendation
Prompt: "Use $repo-setup, then tell me the best next skill for actual implementation work."
Expected:
- the skill finishes at bootstrap scope
- it recommends `engineering-workflow-orchestrator` as the next step

## 6. Local-only docs convention
Prompt: "Use $repo-setup and make sure this repo has a safe place for local-only handoffs and notes."
Expected:
- the skill reviews `.gitignore`
- it ensures `local-docs/` exists and is gitignored
- it tells the user whether `local-docs/` was already present

## 7. VERSION-aligned release draft
Prompt: "Use $repo-setup for a repo whose canonical release number lives in VERSION, and make sure the draft release does not invent its own version."
Expected:
- the scaffolded release-drafter workflow reads `VERSION`
- the draft release name and tag align with `VERSION`
- the setup does not leave a separate label-derived draft versioning path in place
