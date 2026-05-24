# doc-driven-development checklist

- identify the canonical epic, product, or contract source before decomposing
- confirm repository truth is strong enough; hand off to `repo-knowledge-engineering` first if it is not
- separate established truth from assumptions and unresolved questions
- decompose by user-visible capability, workflow stage, or domain boundary
- write bounded feature contracts before task breakdown
- define scenarios that cover happy path, edge cases, failures, and state transitions
- turn each feature into observable acceptance artifacts
- invoke `query-to-knowledge` when scenarios expose unresolved terminology or decisions
- create work packages only after the feature contract is implementation-ready
- read shared Polaralias tracker or output defaults when they exist before shaping issue-ready output
- recommend publishing stable work packages to the user's tracker or local task surface
- preserve traceability from epic to feature to package to acceptance surface
- keep tracker formatting subordinate to the contract
- stop before implementation code unless the user explicitly asks for coding too
