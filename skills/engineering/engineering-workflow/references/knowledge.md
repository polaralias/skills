# Knowledge

Engineer the repository knowledge base as a usable system: establish a foundation, capture resolved truth, align changed behaviour, check cross-artefact consistency, complete a tranche, or streamline a bloated reading surface. This method owns canonical documentation and its reading order. It does not silently expand a documentation request into implementation, test, or CI repair.

## Governed record relationships and metadata

- When creating or meaningfully updating durable Tasks, Workstreams, or typed OKF knowledge, connect governed concepts in one resolved repository-local relationship graph whenever more than one exists. Use meaningful relative Markdown links or resolved structured relationships; an incoming link suffices. Keep terminal tasks linked. Exclude reserved indexes/logs, Tracker Profiles, runbooks, generated/vendor output, handoffs, session records, and scratch files. Report genuine disconnected components instead of inventing links.
- Preserve ownership, unknown compatible metadata, and producer boundaries. Keep all YAML frontmatter strings in governed OKF records plaintext, including nested extensions; use bare URLs or repository-relative metadata links and put presentation in the body. Advance each directly changed concept's explicit meaningful-change timestamp when its meaning changes; filesystem, Git, generation, and observation times are different facts.

## Find the current truth surfaces

Read the root reading order and relevant operating guidance, product/contract docs, glossary/domain language, decisions, plans, support tables, dated evidence, and selected knowledge bundles. Classify each as canonical, contract/desired state, execution, evidence, derived/generated, or producer-owned. Task status, local handoffs, personal explanations, and generated summaries are useful evidence, but do not own enduring product truth.

Preserve an established format when migration adds churn without benefit. For a genuinely new interoperable knowledge foundation, a bounded OKF bundle can be useful; choose its boundary deliberately rather than forcing all Markdown into it. Keep instructions, tasks, worktrees, handoffs, and unrelated plans outside that bundle. A durable README may participate as a typed navigation concept when the repository's adopted profile covers it; never type vendor, generated, transient, or out-of-scope files just because of their name.

Detect OpenWiki or other producer-owned surfaces before changing them. Preserve their ownership until migration or a non-overlapping producer boundary is established by the user or applicable policy. A request to update canonical docs does not automatically authorise replacing another producer's output. Continue independent investigation while the consequential ownership choice remains unresolved.

## Choose the smallest useful knowledge change

For foundation work, define where current product truth, glossary, decisions, support, operating notes, and active plans live. Prefer a short root reading order and a small strong spine. For routine maintenance, inspect only the changed topic and immediate neighbours. For explicit streamlining, widen to the user-selected surface.

Compare accepted product truth -> feature contract -> plan -> work package/task -> implementation -> validation where those surfaces exist. Preserve differences among current verified state, observed state, desired end state, remaining gap, implementation drift, and evidence strength. Name which record supports each claim instead of applying one universal source winner.

Check for resolved questions still framed as open, superseded sequencing, support claims broader than execution evidence, duplicated explanations, stale statuses, and conclusions stranded in handoffs. Use [clarification](clarification.md) for unresolved concepts and decisions; [dissection](dissection.md) for an unclear repository. Do not re-investigate settled truth just because retrieval is poor.

Update the files a future contributor would trust for this change: README/navigation, relevant architecture/reliability/security, glossary, decisions, support matrix, current plan, or dated evidence. Mandatory impact review does not imply mandatory edits. If no durable claim changed, record a concise no-update reason where the workflow needs it rather than generating ceremony.

## Author and promote deliberately

Use the glossary for vocabulary and boundaries, decisions for durable choices, contracts for required behaviour, support tables for verified limits, and plans for remaining work. Keep canonical docs from becoming a second task ledger. Promote verified conclusions in the same slice as the material change; leave unsupported claims explicitly untested or known broken.

When old notes, runtime, source, and tests disagree, inspect the actual public path before promotion. A user follow-up or previous explanation can expose a gap but is not proof of it. Correct verified gaps in their owning canonical surface rather than leaving the answer only in chat. Preserve dated evidence instead of rewriting history to hide drift.

For decisions, use `decision_status: proposed | accepted | partially-superseded | superseded | withdrawn` where an explicit lifecycle is useful. An abandoned proposal is withdrawn. Link successor paths in `superseded_by`. For partial supersession, separate `Current decision` from `Superseded clauses`, linking replaced clauses to their successor. Preserve useful historical rationale outside the current-answer path. These editorial conventions become validation requirements only if the repository adopts them.

For an adopted typed OKF profile, preserve compatible unknown types and producer fields; give concepts useful titles and query-shaped descriptions, and add tags/citations only when supported. Use the selected version's content-change metadata below. Do not infer content change from Git, filesystem, index generation, or observation time. Keep metadata plaintext and meaningful relative relationships resolved. Preserve navigation prominence as reading guidance, distinct from authority, urgency, or dependency.

Validation and generated indexes cannot make a claim true. Review cited implementation and relevant behaviour before recording verification. A content hash can show unchanged bytes, but cannot prove the statement was ever correct. A lexical match does not create an explicit source binding; an unmatched change still needs judgement. Rebuild affected generated navigation through its owning producer, preserving manual content and boundaries.

## Adopted OKF knowledge metadata

Use UTF-8 Markdown, parseable YAML mapping frontmatter, and a descriptive non-empty `type` for typed concepts. Preserve established vocabulary before inventing type synonyms. Useful descriptive types include Architecture Concept, Product Contract, Decision, Glossary Concept, Support Boundary, and Validation Evidence. The selected OKF specification owns conformance; editorial recommendations and repository graph checks are additional, separately reported concerns. Missing optional retrieval metadata is advice unless the adopted profile makes it required.

Keep the adopted OKF 0.1 or 0.2 version explicit; a root `index.md` may declare `okf_version`, and indexes themselves are optional. Supporting knowledge 0.2 does not migrate the separate OKF Tasks format.

- For 0.2 content authorship use `generated.by` and explicit-offset `generated.at`. Advance content time for a meaningful direct change. Preserve existing 0.1 `timestamp` and producer extensions as the existing meaningful-change convention rather than automatically migrating them. In a mixed existing record, do not conflate or silently overwrite the two identities.
- `verified` is an independent `{by, at}` review event or list of such events. Preserve other producers' events. Content change time and review time advance independently. `human:` actors declare human review; never invent one or equate a declaration with proof. Existing `verified_at` remains an evidence-review time where that profile uses it.
- Knowledge `status` may be `draft`, `stable`, or `deprecated`; absence means stable. `stale_after` declares expiry independently of source-byte freshness. Task, Workstream, and Tracker Profile statuses remain governed by their own format.
- `sources` items have a non-empty `resource` and may have stable IDs joining footnotes. Resources may be links, relative files, or scope descriptors. Only resolved local Markdown resources form local graph relationships. Do not fetch a URL or execute scope text because metadata names it.
- Relative concept links resolve from the document; `/concept.md` resolves from its containing bundle root. Recheck relationship resolution after index/bundle changes. External references do not import another producer's graph.

Optional repository conventions can express `authority: canonical | evidence | derived`; `verification: verified-working | verified-limited | known-broken | untested`; and `verified_at`/`verified_against` for when and against which concrete source, test, command, or runtime observation a testable claim was checked. Do not add operational verification to an untestable glossary definition merely for uniformity. `navigation.role` can be `entry-point`, `foundational`, `supporting`, or `reference`, with a sparse non-negative `navigation.order` within that role. It guides reading rather than permissions, task priority, or dependency.

Attested Computation metadata may describe runtime, parameters, computation, executor/receipt, and attester declarations. Storing that knowledge does not authorise execution, tool installation, credential use, or visiting a destination. Any launch requires independently established current authority and reviewed command selection.

## Streamline after promotion

Inspect the affected canonical concept, directly linked concepts, and same-topic plans, decisions, evidence, generated notes, and handoffs from which the conclusion came. Give each relevant source an explicit disposition:

- Retain unique current truth, rationale, or needed evidence.
- Merge duplicate explanation into the stronger canonical surface.
- Archive unique history outside current navigation.
- Delete transient, reproducible, duplicated, or fully absorbed material without unique value, within authorised scope.

Account for open issues and unique evidence before removal. Link retained evidence from the conclusion. An archive with equal prominence still competes as a current answer. Keep active debt truthful and narrow rather than retaining completed plans as pseudo-work.

## Verify meaning, conformance, and findability separately

Check factual claims against the strongest relevant evidence. Validate affected adopted bundles and their resolved relationship graph through the authoritative implementation; preserve task and knowledge roots as independent boundaries. Do not claim conformance while hard errors remain, or claim performed machine validation when tools are unavailable.

Test the likely reader questions: one to three for a routine change, roughly five to ten for a selected foundation/migration/streamlining surface. From the root reading order, current or foundational answers should be recognisable by a query-shaped link or description in one hop; specialist detail may take two. Competing current answers, stale retrieval results, or unrelated terminology fail the editorial check even if a search finds something.

Generated visualisations remain derived. When a visual becomes a durable knowledge surface, document its canonical inputs, renderer, scope/exclusions, output, temporal basis, and verification. Timestamp ordering or a newer linked source is a review signal, not proof of semantic drift. A view exclusion cannot hide a governed orphan or validation failure. Verify readable direct relationships and provenance rather than treating an attractive graph as knowledge quality.

Finish with what changed, what is now true, what remains open, where to read next, validation limits, and the retain/merge/archive/delete results when streamlining. A fresh agent should be able to find durable truth from tracked docs even if the local handoff disappears. Use [alignment](alignment.md) when knowledge changes belong to a tracked material delivery slice.
