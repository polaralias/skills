# Test prompts

## 1. Happy path
Prompt: "Use local-pickup to resume work from the latest relevant handoff in this repository."
Expected:
- the skill chooses the most relevant recent handoff
- it re-checks canonical docs and current repo state before continuing
- it reports the next verified action

## 1a. Workflow-aware pickup
Prompt: "Resume from the latest handoff, and it includes a workflow stage and next skill."
Expected:
- the skill verifies the workflow-stage claims against current repo truth
- it reports the verified stage and the next grounded action rather than repeating the handoff blindly

## 1b. Post-compact continuity pickup
Prompt: "Resume from the saved post-compact continuity artifacts for this project."
Expected:
- the skill checks for a deterministic manifest or restart supplement before scanning handoff files
- it uses the restart supplement for quick orientation and the referenced handoff for deeper context
- it still verifies the claims against current repo truth before continuing

## 1c. Manifest drift handling
Prompt: "Use local-pickup, but the continuity manifest points to a handoff path that no longer exists."
Expected:
- the skill reports the broken manifest reference plainly
- it falls back to the strongest current local continuation evidence instead of pretending the manifest is authoritative

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
