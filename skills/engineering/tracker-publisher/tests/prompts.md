# Test prompts

## 1. Publish stable package set
Prompt: "Publish these already-approved work packages into Linear."
Expected:
- the skill treats the package set as the source of truth
- it maps the existing hierarchy into tracker-ready items
- it does not rewrite the behavioral contract while publishing

## 2. Fall back to tracker-ready output
Prompt: "Turn this package set into GitHub issue-ready artifacts, but there is no live GitHub connector here."
Expected:
- the skill says live publication is unavailable
- it emits tracker-ready artifacts instead of pretending publication succeeded

## 3. Shared defaults
Prompt: "Use our shared Polaralias tracker defaults when publishing this package set."
Expected:
- the skill reads shared tracker and field defaults first
- it uses those defaults without inventing new structure unnecessarily

## 4. Not ready to publish
Prompt: "Publish these work packages even though some acceptance criteria are still TBD."
Expected:
- the skill refuses to treat unresolved packages as publication-ready
- it sends the work back toward `doc-driven-development`
