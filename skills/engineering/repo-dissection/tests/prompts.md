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

## 5. OKF-compatible bootstrap
Prompt: "This new repository has no documentation foundation. Bootstrap one that other knowledge tools can consume."
Expected:
- recommends a bounded OKF-compatible knowledge bundle
- creates typed concepts with useful retrieval metadata rather than converting every Markdown file
- hands index generation and conformance validation to `repo-knowledge-engineering`

## 6. Existing OpenWiki claims
Prompt: "OpenWiki already describes this repository, so treat every page as verified truth."
Expected:
- consumes the OpenWiki bundle for orientation
- treats its concepts as producer-owned derived claims
- compares them with code and runtime evidence before canonical promotion

## 7. Unknown OKF extension
Prompt: "This existing concept has a type and extension fields our skills do not recognize. Normalize them away."
Expected:
- preserves unknown types and producer-defined fields
- changes metadata only when evidence or conformance requires it
