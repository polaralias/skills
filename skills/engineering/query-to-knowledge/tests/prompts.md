# Test prompts

## 1. Happy path
Prompt: "The repository uses three similar terms inconsistently. Resolve the terminology and capture the result in the right docs."
Expected:
- the skill reads the code and canonical docs first
- it asks a small high-signal question batch only for the irreducible judgment calls
- it captures resolved terminology into the right knowledge artifact

## 2. Repository-answerable boundary
Prompt: "Ask me every question you can think of about this unclear module."
Expected:
- the skill does not ask questions the repository can answer directly
- it answers the repository-resolvable portion from evidence first

## 3. Contradiction-driven batch
Prompt: "The docs say one thing, the code suggests another, and support language says a third. Work through that."
Expected:
- the skill groups tightly related contradiction-driven questions
- it keeps the batch on one theme and synthesizes the result after the answers

## 4. Handoff boundary
Prompt: "The main job is now broad doc-system maintenance across glossary, README, and decision records."
Expected:
- the skill recognizes that the broader job belongs to `repository-knowledge-engineering`
- it avoids owning the whole knowledge-base maintenance pass itself
