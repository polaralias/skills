# Engineering Workflow Migration

## Routing policy

`engineering-workflow` is the sole normal skill entry point for material repository engineering. RKE is the independent runtime and methodology. Retained legacy peer names and aliases are compatibility inputs resolved by `rke legacy route <name>`; they are not phases or instructions to load the old package body. Unknown and deliberately retired names are rejected rather than guessed.

`repo-setup` remains an intentionally separate pre-workflow bootstrap capability. It is not absorbed into active engineering lifecycle state.

## Compatibility matrix

| Legacy alias | Legacy package | Replacement destination | Status |
| --- | --- | --- | --- |
| EWO | engineering-workflow-orchestrator | lifecycle start/resume/close | absorbed |
| RDS | repo-dissection | deep understand journey plus `dissection assess` | absorbed with executable inventory and expanded output contract |
| QTK | query-to-knowledge | explicit clarification capability plus `shared-understanding` gate | preserved in EWF |
| RKE | repo-knowledge-engineering | independently installed RKE runtime and methodology used by EWF | preserved as a first-class primitive |
| DDD | doc-driven-development | design journey | absorbed with feature, scenario, verification, acceptance, planning, package, and traceability contracts |
| RTL | repo-task-lifecycle | proportional OKF Tasks adapter | absorbed; OKF engine remains independent |
| WTC | worktree-task-coordinator | parallel-delivery extension plus `coordination validate/plan` | absorbed with transport-parity runtime operations |
| RCC | repo-change-comprehension | `change explain` receipt plus close-journey causal explanation | absorbed |
| RSA | repo-session-alignment | close journey plus ordered two-lane `closure assess` | absorbed with compact alignment status contract |
| LHO | local-handoff | `handoff write` plus continuity contract | absorbed with deterministic standard/max artefacts and supersession |
| LPK | local-pickup | `handoff inspect`, lifecycle resume, and continuity contract | absorbed with active selection and re-verification contract |
| RPF | repo-publish-finaliser | publication extension plus `publication scan` | absorbed |
| RST | repo-setup | separate bootstrap capability | retained separately |

TPU and TPW are deliberately retired rather than routed. Tracker synchronization belongs to the independent OKF Tasks primitive. Scenario and test planning are part of the DDD design/delivery acceptance surface, so a second QA capability would create competing ownership.

## Physical packages

Absorbed packages live unchanged in the repository-root `archive/` directory. The archive is deliberately outside `skills/`, so active catalogue generation, host discovery, installation, and implicit invocation cannot treat those packages as peers. It preserves historical implementation evidence without maintaining a second live source.

New behaviour and fixes belong in the EWF journey, extension, adapter, or core that owns the mapped destination. Do not modify archived packages to create feature drift. Machine-local installations may retain old package copies until the user refreshes them; project routing must still select EWF.

## Parity evidence

The executable route test covers every retained alias, checks full-name case-insensitive lookup, verifies one destination per input, and proves TPU/TPW rejection. Public-interface tests separately cover lifecycle, journeys, task modes, ordered session alignment, dissection, handoff writing and pickup, worktree coordination, publication scanning, closure gates, event-driven documentation, host installation, hooks, context retrieval, knowledge impact, and CLI/MCP parity.
