# Test prompts

## 1. Happy path
Prompt: "Align the repository knowledge base after this tranche so a fresh agent can continue from tracked docs."
Expected:
- the skill identifies the canonical knowledge surface
- it updates the right docs in the same slice as the truth change
- it leaves a trustworthy next-step reading surface

## 2. Canonical boundary
Prompt: "Update every document in the repository just to be safe."
Expected:
- the skill updates only the docs future contributors would actually trust for the current change
- it avoids broad noisy edits by default

## 3. Evidence vs contract
Prompt: "A newer validation note disproves an older contract doc. Smooth it over by rewriting the old evidence."
Expected:
- the skill preserves evidence boundaries
- it updates current contract docs without erasing historical evidence

## 4. Publish-safety check
Prompt: "The repository may be nearing public use. Do a final documentation alignment pass."
Expected:
- the skill checks for machine-local paths, stale setup stories, or secrets leakage in tracked docs
- it sharpens the root reading order before polishing secondary docs

## 5. Harness means repository truth, not tests
Prompt: "Build the repository knowledge harness for this project so agents can work from tracked docs before implementation starts."
Expected:
- the skill interprets `harness` as the documentation and evidence system around repository truth
- it creates or tightens reading order, canonical doc boundaries, plans, decisions, glossary, or evidence surfaces as needed
- it does not write tests, eval harnesses, CI jobs, or application code

## 6. Docs-first tranche before code
Prompt: "Replicate a docs-first workflow here: create the documentation spine and execution-plan surfaces first, then stop before writing code."
Expected:
- the skill establishes a minimal canonical documentation spine
- it records assumptions, decisions, and next-step reading order
- it stops at repository knowledge artifacts rather than drifting into implementation

## 7. Explicit no-tests boundary
Prompt: "Update the repo truth surfaces for this validation approach, but do not add tests yet."
Expected:
- the skill captures what validation evidence exists and where it lives
- it updates canonical docs and evidence notes proportionately
- it does not treat missing tests as permission to author them
