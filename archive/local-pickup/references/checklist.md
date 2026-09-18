# local-pickup checklist

- find the project root
- check for a deterministic continuity manifest or restart supplement before heuristically scanning handoff files
- locate the local handoff directory
- choose the named or newest relevant handoff
- when a manifest exists, prefer the artefact paths and workflow hints it names
- prefer the handoff whose referenced canonical docs still match the active workstream
- read the operating guide and canonical docs in order
- use a restart supplement for quick recovery, then verify against the referenced handoff and current repo truth
- re-check current branch and working tree state
- re-check runtime facts when the next step depends on them
- verify workflow-stage and next-skill claims when the handoff recorded them
- verify manifest and supplement claims such as branch, commit, as-of point, or artefact paths rather than accepting them blindly
- verify any important assumptions against code or tests
- summarise what is still true and what changed
- classify whether to continue directly, continue after correction, or rediscover
- continue the task from current verified state
