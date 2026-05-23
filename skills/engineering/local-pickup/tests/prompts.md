# Test prompts

## 1. Happy path
Prompt: "Use local-pickup to resume work from the latest relevant handoff in this repository."
Expected:
- the skill chooses the most relevant recent handoff
- it re-checks canonical docs and current repo state before continuing
- it reports the next verified action

## 2. Stale handoff handling
Prompt: "Resume from this handoff even though the branch and referenced files may have changed."
Expected:
- the skill treats the handoff as input rather than unquestioned truth
- it names stale or partially true claims explicitly

## 3. No handoff fallback
Prompt: "Resume the work, but there is no local handoff."
Expected:
- the skill says no handoff exists
- it rebuilds context from canonical docs and current git state instead of pretending continuity

## 4. Escalation boundary
Prompt: "The handoff, docs, and code all disagree about what the repo currently does."
Expected:
- the skill classifies the restart as needing correction or deeper rediscovery
- it points toward `repo-dissection` rather than continuing blindly
