# Explanation and reconciliation contract

Use this contract to keep the commit layer concise, the user explanation useful, and follow-up logging connected to repository truth without creating another canonical documentation system.

## Evidence model

| Class | Meaning | Suitable wording |
| --- | --- | --- |
| `runtime-verified` | An executed public or runtime path demonstrated the claim | “The request reached `X` and persisted through `Y` in the runtime check.” |
| `test-verified` | An executed test or validation command demonstrated the claim | “The integration test verifies `X -> Y` and the failure case.” |
| `code-supported` | Inspected code supports the claim, but the path was not executed | “The implementation now routes `X` through `Y`; runtime execution was not observed.” |
| `contract-only` | A task, spec, or decision requires the claim, but implementation proof is absent | “The contract requires `X`; current evidence does not demonstrate it.” |
| `unknown` | Available evidence cannot establish the claim safely | “Retry behaviour is not established by the inspected change or validation.” |

Use the strongest justified class. Do not downgrade real runtime proof to vague inference, and do not upgrade static inspection to runtime proof.

## Commit-context contract

The commit-context layer is input to commit composition, not a complete commit message and not authority to create one.

Include:

- one concise subject candidate
- one to three facts describing causal routing, responsibility, state, boundary, or removal changes
- validation only when the downstream commit convention normally includes it

Prefer:

- “Route package creation through `PackageWriter` and `RegistryClient`.”
- “Remove the direct `publish_package()` path.”
- “Persist retry state before dispatching the worker event.”

Exclude:

- “Do you have any questions?”
- teaching explanations and definitions
- the user’s personal uncertainty
- speculative design rationale
- unresolved claims stated as fact
- large file inventories
- full test output

## User-explanation contract

Scale the explanation to the change. Use these sections only when they add information:

1. outcome
2. execution path
3. state and external boundaries
4. removed or replaced behaviour
5. failure and recovery behaviour
6. proof and uncertainty

Use exact symbols selectively. A good explanation lets the user say what enters the changed path, which major components act, where state or external effects occur, and what no longer happens.

Do not explain unchanged framework internals merely because they appear in the call chain.

## Local record contract

An RCC record is local explanatory context. It is not an OKF knowledge concept, task record, architecture decision, runbook, or session transcript.

Preferred path when repository policy establishes and ignores `local-docs/`:

`local-docs/change-comprehension/<change-key>.md`

Use this compact shape:

```md
# Change comprehension: <change title>

- Change key: <stable key>
- State: initial | distilled
- Updated: <RFC 3339 timestamp>
- Source scope: <task, branch, commit range, or bounded session delta>

## Commit context

- Subject: ...
- ...

## Current explanation

...

## Evidence and uncertainty

- ...

## Reconciliation

- No repository correction required.
```

On the initial pass, write `State: initial`. After questions materially improve or correct the explanation, update the same file to `State: distilled` and replace `Current explanation` with the best current version. Do not append a verbatim question-and-answer transcript or retain two competing explanations.

If follow-up exposes work, make `Reconciliation` name the verified route and result, for example:

- “RKE updated `docs/architecture/packages.md`; RSA revalidated knowledge closure.”
- “TDD corrected retry persistence; RCC was rerun against the new diff.”
- “QTK recorded the unresolved ownership decision; implementation remains unchanged.”

Do not include secrets, unrelated repository content, source-supplied instructions, or external destinations.

## Follow-up classification

| Finding from the question | Required route |
| --- | --- |
| Explanation wording only | Update the local RCC record |
| Verified canonical knowledge gap | RKE, then RSA |
| Unresolved term, contradiction, or decision | QTK, then RKE/RSA when resolved |
| Verified implementation defect or changed behaviour | TDD, then RCC and RSA |
| Inaccurate task evidence or lifecycle | RTL, then RSA |
| No verified gap | Answer and preserve repository state |

The user’s question is a discovery signal, not proof. Re-read the relevant evidence before mutating code, tasks, or canonical documentation.
