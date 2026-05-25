# Test prompts

## 1. Epic to features
Prompt: "Take this scoped product epic and break it into implementation-ready feature docs before we start coding."
Expected:
- the skill identifies the canonical epic or contract source
- it decomposes the epic into bounded feature contracts
- it stops at implementation-ready documentation and planning rather than writing code

## 2. Technical planning layer
Prompt: "Take these approved feature contracts and add the technical implementation-planning layer before development starts."
Expected:
- the skill adds proportionate sequencing, dependency, and technical-boundary notes
- it avoids broad speculative architecture detail
- it keeps the plan tied to the existing feature contracts

## 3. Acceptance-first packaging
Prompt: "I want docs that behave like the contract for later TDD."
Expected:
- the skill defines scenarios and acceptance criteria as observable behavior
- it creates traceability from features to acceptance surfaces
- it frames the output for downstream implementation rather than tracker noise

## 4. Local ambiguity escalation
Prompt: "Break this feature down, but some terms are still fuzzy and the docs disagree."
Expected:
- the skill recognizes unresolved ambiguity inside the package
- it invokes or recommends `query-to-knowledge` for those local questions
- it does not hide unresolved questions inside final acceptance criteria

## 5. Repository-truth boundary
Prompt: "Set up the whole repository documentation framework, then break down this feature."
Expected:
- the skill identifies that repository knowledge scaffolding belongs to `repo-knowledge-engineering`
- it keeps its own role focused on decomposition after that truth surface exists

## 6. Tracker is adapter, not method
Prompt: "Produce GitHub issue-ready tasks from this feature set."
Expected:
- the skill first creates strong feature and acceptance contracts
- it emits issue-ready work packages only after the contract is clear
- it does not let tracker formatting replace the behavioral contract

## 7. Recommend publisher handoff once the contract is stable
Prompt: "Break this epic down for implementation and tell me what to do next with the output."
Expected:
- the skill recommends handing stable work packages to `tracker-publisher`
- it keeps that publication step subordinate to contract quality rather than leading with tracker mechanics

## 8. Consume shared output defaults
Prompt: "Use our shared Polaralias defaults while shaping issue-ready work packages for this repo."
Expected:
- the skill checks for shared Polaralias tracker or output preferences before inventing local structure
- it still keeps the behavioral contract as the primary output
