# Canonical Knowledge Methodology

Load this reference when establishing a knowledge foundation, promoting durable conclusions, maintaining a decision or glossary, or streamlining a repository's reading path. The [knowledge contract](knowledge-contract.md) owns RKE's current deterministic bundle, index and binding operations. This reference carries editorial judgement from the archived repository-knowledge skill; it does not add validator rules that the runtime does not implement.

## Choose the surface

Start with the repository's established reading order and canonical ownership. Prefer a bounded knowledge bundle such as `docs/knowledge/` when adopting OKF. Keep Tasks, Workstreams, worktree manifests, handoffs, sessions, generated output, and unrelated plans in their own surfaces. Do not convert every Markdown file just to claim conformance. A durable root or nested README can be a deliberate entry-point concept when it genuinely serves as canonical navigation.

Choose the actual knowledge job before editing: **foundation** establishes the minimum reading spine and owner boundaries; **capture** places a newly resolved term or decision; **alignment** updates claims after verified implementation; **analysis** compares product truth, feature contracts, plans, packages and evidence for drift; **tranche completion** removes future-tense or stale debt from completed work; **streamline** consolidates known answers in an existing bloated surface. Route unresolved product choices to QTK instead of disguising them as streamline work.

Create or refresh `GLOSSARY.md` when domain terms are causing repeated ambiguity. Create `docs/decisions/` when durable choices and their rationale need a lifecycle. Neither path is mandatory ceremony. Reuse an established repository type before inventing a synonym; useful descriptive types include `Architecture Concept`, `Product Contract`, `Decision`, `Glossary Concept`, `Support Boundary`, and `Validation Evidence`.

For an adopted OKF 0.1 bundle, write UTF-8 Markdown with parseable YAML frontmatter and a self-explanatory non-empty `type`. Keep frontmatter string values plain text; presentation and labelled links belong in the body. `title` and a one-sentence, query-shaped `description` help readers find the concept. Preserve unknown types and producer fields. Set a meaningful `timestamp` when creating or changing the concept's meaning rather than inferring it from file or Git time. The current RKE validator enforces only its documented hard checks and reports selected retrieval metadata as warnings; these editorial conventions are not silently enforced by `knowledge check`.

## Authority, verification and reading order

Use these optional repository-knowledge extensions when the selected bundle benefits from them:

| Field | Editorial meaning |
| --- | --- |
| `authority` | `canonical`, `evidence`, or `derived`; formatting alone does not grant authority. |
| `verification` | `verified-working`, `verified-limited`, `known-broken`, or `untested`; distinguish observed support from intended behaviour. |
| `verified_at` and `verified_against` | When a testable claim is verified, record when it was checked and the concrete source, command, test or runtime evidence. Do not apply operational verification metadata to an untestable glossary definition or decision merely for uniformity. |
| `navigation.role` and `navigation.order` | Optional reading prominence: `entry-point`, `foundational`, `supporting`, or `reference`, with a non-negative sparse order within a role. This does not replace links or establish task priority. |

Treat `timestamp` as content change and `verified_at` as evidence review; advance them independently. A generated index, a high retrieval rank, or a current byte hash does not prove semantic truth. For external claims, use a citations section with numbered links when that improves traceability. Keep current answers visible from the root reading order in one navigation hop where practical; specialised supporting detail may take two. If two plausible current answers compete or a superseded answer has equal prominence, repair the reading path.

For a durable visualisation contract, use a `Visualization` concept to name its canonical source, renderer, derived output, temporal basis, history model, exclusions and drift policy. The rendered HTML, diagram or image stays derived. A newer source timestamp is a review lead, not proof that the target is wrong; inspect semantics and evidence first. The authoritative producer owns generation flags, embedded assets and scope mechanics, including OKF Tasks visualisation. Do not use an exclusion to conceal a governed orphan or conformance error.

## Decisions and contradictions

When durable decisions need explicit status, use `decision_status: proposed | accepted | partially-superseded | superseded | withdrawn`. `accepted` is current; `withdrawn` is an abandoned proposal. For partial or full supersession, name successor paths in `superseded_by`. In a partially superseded decision, separate `## Current decision` from `## Superseded clauses`, and link each replaced clause to its successor. Keep useful historical rationale as reference material, while removing it from the current-answer path. These are editorial conventions until the selected repository's validator explicitly enforces them.

If generated notes, old docs, source, tests, and runtime disagree, preserve the contradiction long enough to inspect the actual public path. Classify current verified state, observed state, desired state, remaining gap, and evidence strength. Promote a durable conclusion only after reviewing the bound source and relevant behaviour; leave unsupported claims `untested` or `known-broken`. A task's status or external tracker item cannot substitute for canonical product truth.

## Promotion and streamlining

After promoting a conclusion, review the source material it came from. Choose an explicit disposition for each affected note: **retain** unique truth or evidence, **merge** duplicate explanation into the strongest concept, **archive** unique history outside current navigation, or **delete** transient, reproducible, or fully absorbed material with no unique evidential value. Preserve open issues and rationale before removing a note. Moving a stale answer into an equally prominent archive is not streamlining. Use optional `log.md` for meaningful knowledge creation, update, deprecation or promotion events, not routine commits or task progress.

Keep a routine check bounded to the changed topic and its immediate neighbours. Widen to a selected surface for an explicit foundation or streamline request. Test one to three likely reader questions for a routine change and roughly five to ten representative questions for a foundation or migration. Check both retrieval rank and the root reading path; a found but stale or misleading answer still fails the editorial review. Finish with enough tracked knowledge that a fresh agent could understand what changed, what is current, what is open, and where to read next even without a local handoff.

The independent OKF Tasks specification and CLI own Task, Workstream, effort, Tracker Profile, provider, and task visualisation rules. This methodology must not revive legacy task fields or provider bindings as a competing schema.
