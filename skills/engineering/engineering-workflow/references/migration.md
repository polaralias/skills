# Engineering Workflow Migration

## Routing policy

`engineering-workflow` is the sole normal skill entry point for material repository engineering. RKE is the independent runtime and methodology. Legacy peer names and aliases are compatibility inputs resolved by `rke legacy route <name>`; they are not phases or instructions to load the old package body. Unknown names are rejected rather than guessed.

`repo-setup` remains an intentionally separate pre-workflow bootstrap capability. It is not absorbed into active engineering lifecycle state.

## Compatibility matrix

| Legacy alias | Legacy package | Replacement destination | Status |
| --- | --- | --- | --- |
| EWO | engineering-workflow-orchestrator | lifecycle start/resume/close | absorbed |
| RDS | repo-dissection | understand journey | absorbed |
| QTK | query-to-knowledge | explicit clarification capability plus `shared-understanding` gate | preserved in EWF |
| RKE | repo-knowledge-engineering | independently installed RKE runtime and methodology used by EWF | preserved as a first-class primitive |
| DDD | doc-driven-development | design journey | absorbed |
| RTL | repo-task-lifecycle | proportional OKF Tasks adapter | absorbed; OKF engine remains independent |
| WTC | worktree-task-coordinator | parallel-delivery extension | absorbed |
| RCC | repo-change-comprehension | `change explain` receipt plus close-journey causal explanation | absorbed |
| RSA | repo-session-alignment | close journey reconciliation and closure assessment | absorbed |
| LHO | local-handoff | checkpoint plus continuity contract | absorbed |
| LPK | local-pickup | resume plus continuity contract | absorbed |
| RPF | repo-publish-finaliser | publication extension | absorbed |
| TPU | tracker-publisher | tracker-sync extension | absorbed |
| TPW | test-plan-writer | QA-planning extension | absorbed |
| RST | repo-setup | separate bootstrap capability | retained separately |

## Physical packages

Absorbed packages live unchanged in the repository-root `archive/` directory. The archive is deliberately outside `skills/`, so active catalogue generation, host discovery, installation, and implicit invocation cannot treat those packages as peers. It preserves historical implementation evidence without maintaining a second live source.

New behaviour and fixes belong in the EWF journey, extension, adapter, or core that owns the mapped destination. Do not modify archived packages to create feature drift. Machine-local installations may retain old package copies until the user refreshes them; project routing must still select EWF.

## Parity evidence

The executable route test covers every documented alias, checks full-name case-insensitive lookup, verifies one destination per input, and rejects unknown names. Public-interface tests separately cover lifecycle, journeys, task modes, closure gates, event-driven documentation, host installation, hooks, context retrieval, knowledge impact, and MCP. Behaviour outside those contracts remains a compatibility-package claim until separately demonstrated.
