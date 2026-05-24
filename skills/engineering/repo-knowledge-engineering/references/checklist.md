# repo-knowledge-engineering checklist

- identify active docs, specs, plans, tests, archive docs, and local handoffs
- identify `AGENTS.md` or other operating guidance when present
- separate current verified behavior from desired end state
- identify where epic-level or product-truth docs should live and whether they are canonical yet
- identify the canonical reading order before polishing secondary docs
- establish the knowledge-base structure if it does not yet exist
- update docs in the same slice as behavior changes
- document validation evidence and test status when relevant without authoring tests, eval harnesses, CI jobs, or application code from this skill alone
- update `GLOSSARY.md` when glossary or domain language changes
- update `docs/decisions/` when a durable decision changes and the repository uses decision records
- update active plans and support truth in the same slice when behavior moved
- move completed plans out of the active surface
- keep local handoffs subordinate to tracked docs
- keep archive docs evidence-backed and de-emphasized
- label evidence, canonical, execution, and generated surfaces clearly when they coexist
- scan for publish-safety leakage before public release
