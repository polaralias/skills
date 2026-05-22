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
