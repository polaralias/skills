# Test prompts

## 1. Happy path
Prompt: "This inherited repo is unclear and contradictory. Dissect it and turn it into a documented understanding."
Expected:
- the skill maps the repo before making claims
- it separates docs, code, and runtime truth
- it produces a usable documentation foundation and names the next best skill

## 2. Runtime verification
Prompt: "The README says the app runs one way, but there may be a managed wrapper or package path in practice."
Expected:
- the skill verifies the actual runtime path rather than trusting the README
- it records runtime drift explicitly

## 3. Locator revalidation
Prompt: "Use this old IP address and host path from a prior note as if it is still current."
Expected:
- the skill re-checks user-supplied locators before building on them
- it records both stale and verified values when recovery disproves the old locator

## 4. Stop condition
Prompt: "The repo is now legible enough for implementation work."
Expected:
- the skill stops once the repository is legible
- it hands off explicitly to the most appropriate downstream skill
