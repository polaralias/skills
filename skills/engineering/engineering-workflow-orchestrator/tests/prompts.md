# Test prompts

## 1. Stage routing
Prompt: "Use one workflow skill to decide whether this repo needs repo-dissection, repo-knowledge-engineering, or doc-driven-development first."
Expected:
- the skill classifies the current stage explicitly
- it chooses the narrowest downstream skill instead of trying to do every stage itself

## 2. Hook-aware continuity
Prompt: "Set up this engineering workflow so compaction and resume keep the current stage visible in both Codex and Claude Code."
Expected:
- the skill describes hook setup only through supported Codex and Claude surfaces
- it keeps hooks thin and routes pause or resume through `local-handoff` and `local-pickup`

## 3. Resume routing
Prompt: "We have a local handoff and want to continue the current tranche. Use the workflow orchestrator to decide the next skill."
Expected:
- the skill routes through `local-pickup` first
- it names the next downstream stage after pickup

## 4. Drift handling
Prompt: "The workflow-state says we are in doc-driven-development, but the canonical docs show implementation already started."
Expected:
- the skill treats canonical docs and verified state as stronger than stale workflow-state
- it updates or de-emphasizes the stale stage instead of preserving a false route
