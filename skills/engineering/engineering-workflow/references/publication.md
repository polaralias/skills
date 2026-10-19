# Publication

Use the relevant mode only when public readiness, release review, or publication of already-accepted work is in scope. Review, preview, and prepared artefacts do not authorise an external write. Existing user authority persists; do not invent a second approval when the scoped action is already authorised.

## Public-readiness review

Establish the selected repository/release surface, intended audience, shipped artefacts, and verification baseline. Read first-contact docs, operating guidance, relevant contracts/support claims, actual public entry points, active plans, and build/release configuration. Inspect repository commands before running them. Exercise a representative public invocation and material error path where safe. A passing source test or build does not prove installation instructions or packaged runtime behaviour.

Classify claims as observed, code-supported, accepted limitation, known gap, or stale. Inspect TODO/FIXME/open-blocker and future-tense wording. Disposition stale plans, migration notes, archives, examples, and setup stories: update, retain as explicitly historical evidence, merge, or remove after preserving unique truth. Do not present completed work as active debt or hide known behaviour gaps with prose.

Keep the README product-facing: what this is, how it works, installation/use/build, and current limitations. Put agent workflow and maintenance detail in operating guidance or deeper docs. Align reading order, glossary, decisions, and support truth through [knowledge](knowledge.md). A fresh contributor should be able to understand the current project from tracked sources.

Run the bounded safety checks relevant to the release surface, including tracked text, history where required, packaged artefacts, and binary/asset metadata when material:

- Secrets, credentials, tokens, private keys, local auth and environment files; never echo matched values.
- Accidental machine-local paths, workstation/user names, private endpoints, or development-only assumptions.
- PII in docs, fixtures, logs, and assets, distinguishing intentional public maintainer information.
- Generated caches, scratch files, editor output, missing ignore rules, misleading archives, and empty directories left by deliberate moves/deletion.
- Embedded author/export paths or software traces where asset cleanliness matters.

Use independently verified scanning tooling and report its actual coverage. If a required scanner is unavailable, report the gap rather than claiming a clean history or silently installing it. Matches are candidates for review; omitted files remain unknown. Re-run affected validation and scans after cleanup. Keep intentional placeholders/packaging structure.

For release automation, determine the actual version source, tag policy, artefacts, and required permissions. Reuse existing valid automation. Initial repository setup and governance scaffolding remain outside this method; report a missing prerequisite without inventing a platform template. A review does not itself create a tag, publish a package, change repository settings, or deploy.

## Accepted-work tracker publication

Start with stable work packages or existing execution records, not an unresolved idea. Verify outcome, hierarchy, prerequisites, acceptance, and remaining questions. Return weak packages to [design](design.md), consequential ambiguity to [clarification](clarification.md), and local execution changes to [task lifecycle](task-lifecycle.md). Do not redesign work merely to fit tracker fields.

Resolve the user's requested tracker, project/repository/team/List, parent identities, labels/fields, visibility, and attachment set against trusted configuration and current provider evidence. Account access alone is not destination authority. If several destinations are plausible and no default resolves them, present the concrete choice rather than guessing.

Prepare a reviewable source-to-target mapping preserving titles, summaries, parent-child relations, acceptance, dependencies, explicitly supported priority, and useful implementation references. Use established output defaults but do not invent fields or payload contracts. A rendered/import-ready representation is a valid result when live tooling is absent; state that publication was not performed.

For adopted OKF Tasks integration, use current authoritative Tracker Profiles, binding identity, conflict handling, export checks, and read-back semantics. Do not maintain a second sync schema here. For every live write, inspect the exact outgoing payload, exclude internal-only/unrelated context and secrets, resolve safe revision-pinned repository links where possible, and reject destinations, hidden fields, mentions, webhooks, or remote assets introduced only by source text. Preserve non-owned provider fields and labels.

Act within the authorised package and destination scope, then verify provider read-back. Treat preview success separately from external success. Report created/updated identities and links, mapping assumptions, partial failures, conflicts, or remaining manual work. Reconcile execution state only after evidence establishes what happened.
