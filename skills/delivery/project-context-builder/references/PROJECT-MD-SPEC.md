# PROJECT.md Format Specification

Version: 1.3
Status: Canonical reference for `project-context-builder` and `project-packager` skills.

---

## What PROJECT.md is

`PROJECT.md` is the canonical project context file for a true project or internal programme. It is the single source of truth for agents and humans working on that project across sessions.

It is **not** intended for routine account management, BAU delivery coordination, or lightweight PM oversight where no real project structure exists. It is for work that has genuine project shape: defined outcomes, bounded scope, milestones, dependencies, and evolving delivery context.

It is **not** a PRD, a status report, or a task list. It is the durable context layer that makes all of those things possible without re-explaining the project from scratch.

Every true project has exactly one `PROJECT.md`. It is created by `project-context-builder` and maintained by both `project-context-builder` and `project-packager`.

---

## Durability rule

`PROJECT.md` must stay durable. It should capture project truth, guardrails, milestone shape, major decisions, retrieval paths, and stable delivery context.

It must **not** try to mirror the live delivery board.

Keep the following out of `PROJECT.md` unless they materially change project truth:
- day-to-day task churn
- routine board updates
- weekly status noise
- granular owner/date movement that belongs in the operational planning tool
- meeting-by-meeting summaries

When in doubt, prefer the thinner durable version.

---

## Maintenance note requirement

Immediately below the H1 heading, include a short maintenance note for humans and LLMs.

Use this model exactly or very close to it:

```markdown
> **Maintenance note for humans and LLMs**
>
> This file is the durable project context layer, not the live delivery board. Use it for project truth, guardrails, major decisions, milestone shape, and retrieval paths. Do **not** treat it as the minute-by-minute status source.
>
> If any of the following shifts materially, pause and ask the user whether `PROJECT.md` should be refreshed before relying on it: delivery shape, milestone dates, scope / non-scope, prototype approach, core user journey, canonical storage path, or key ownership.
>
> Highly fluid operational detail should live in boards, meeting notes, and working docs referenced from this file, not be duplicated here.
```

This note is mandatory.

---

## Filename and location

**Filename:** `PROJECT.md` (always uppercase, always `.md`)

**Human-readable title inside the file:** `# Project Context` as the H1 heading, followed by the project name on the next line if helpful.

**Default storage location:** a durable shared document repository, under the customer or project folder.

Recommended path pattern:
```text
/Projects/[customer-slug]/PROJECT.md
```

Example:

```text
/Projects/nhse-dcat/PROJECT.md
```

**Preferred registration rule:** record the canonical file path in the project data mapping or equivalent project index under a `project_context_path` field, so any agent can locate it without broad searching.

**Fallback registration rule:** if no config doc exists, record the path in the parent project task or equivalent project metadata location.

---

## One-file rule and migration guidance

A true project should have exactly one canonical `PROJECT.md`.

In practice, older projects may already contain overlapping artefacts such as:
- project briefs
- overview documents
- copied context packs
- duplicated project folders
- archived versions of earlier context docs

When creating or updating `PROJECT.md` in an environment with multiple candidate context documents:

1. Identify the authoritative copy using:
   - location
   - ownership
   - freshness
   - references from the project data mapping or parent project metadata
   - whether the document is actively maintained
2. Preserve the one-file rule by selecting or creating a single canonical `PROJECT.md`.
3. Do not silently discard legacy context sources. If they still matter, reference them in Supporting artefacts and retrieval paths or a short migration note in Metadata or Current state.
4. If canonical ownership is unclear, mark that explicitly and avoid pretending certainty.

---

## Layer model

`PROJECT.md` has two layers. Skills must respect these boundaries.

### Static layer

Set at project kickoff or during deliberate reshaping. Only updated with intent, not on routine packaging runs.

Sections in the static layer:
- Metadata
- Purpose
- Outcomes and success measures
- Scope
- Non-scope
- Stakeholders and roles
- Workspace navigation

Static sections may be updated by `project-context-builder` when the project is being reshaped, or when a PM explicitly triggers an update. They must not be silently overwritten by packaging runs.

### Dynamic layer

Updated when material facts change. These sections reflect current project shape, not board churn.

Sections in the dynamic layer:
- Current delivery shape
- Current state
- Milestones
- Risks, assumptions, dependencies
- Open questions
- Supporting artefacts and retrieval paths
- Next recommended actions

**Decision log** is a special case: it is append-only in substance. New decisions are added at the top. Existing entries should not be materially rewritten or removed. Minor factual corrections are allowed where they do not change the meaning of the original decision.

---

## Write rules

These rules apply to any agent or skill writing to `PROJECT.md`.

| Section | Write rule |
|---|---|
| Metadata | Update `last_reviewed` and `last_reviewed_by` on every write |
| Purpose | Static, do not overwrite without explicit reshaping |
| Outcomes | Static, do not overwrite without explicit reshaping |
| Scope / Non-scope | Static, do not overwrite without explicit reshaping |
| Stakeholders | Static, update only when contacts or roles change |
| Workspace navigation | Static, update only when workspace or repository structure changes |
| Current delivery shape | Overwrite only when delivery model or milestone logic materially changes |
| Current state | Always overwrite with latest durable snapshot, do not append history |
| Milestones | Keep only project-shaping milestones and gates, not routine board dates |
| RAID | Keep current project-level picture only; resolved items belong in the decision log |
| Decision log | Append-only in substance, prepend new entries, do not materially rewrite old entries |
| Open questions | Keep only unresolved questions that materially affect project truth or safe planning |
| Supporting artefacts | Add new entries freely, update existing entries when retrieval paths or authority change, do not duplicate entries |
| Next recommended actions | Keep short and durable; do not mirror the active task board |

---

## Staleness thresholds

These thresholds apply when any agent or skill is deciding whether `PROJECT.md` is current enough to use without prompting a refresh.

| Signal | Threshold | Action |
|---|---|---|
| `Last reviewed` in Metadata | More than 30 days ago | Surface to user, ask whether to proceed or refresh first |
| `Current state — As of` date | More than 14 days ago | Surface to user, ask whether to proceed or refresh first |
| Any milestone date is in the past with status not `Complete` | Any | Flag as stale milestone, do not silently treat it as current |
| Material shift observed in conversation vs file | Any | Ask the user whether to refresh `PROJECT.md` before relying on it |
| Both date thresholds exceeded | Both exceeded | Recommend running `project-context-builder` before packaging or agent work |

Staleness does not block use of the file. It is a signal to surface to the user, not a hard stop. The user decides whether to proceed or refresh.

---

## File delivery guidance

When an agent produces or updates `PROJECT.md`, it must deliver the result in a way the user can act on without additional steps.

### If the relevant document connector is available

1. Write or update the file at the registered canonical path.
2. Confirm the write succeeded and display the path.
3. Confirm the `project_context_path` field is set in the project data mapping or equivalent index. If it is not, update it or prompt the user to do so.

### If a document connector is not available

1. Produce `PROJECT.md` as a downloadable file.
2. Also render the full content as a markdown block in chat so the user can copy it immediately.
3. Tell the user exactly where to put it:

> Save this file as `PROJECT.md` in your project folder at the registered canonical path.
>
> Once uploaded, add that path to your project data mapping or equivalent project index under the `project_context_path` field so agents can find it in future sessions.

### Both cases

- Never silently finish without confirming where the file lives or will live.
- Never assume a previous path is still correct without verifying.

---

## Canonical section definitions

Use exactly these section headings in this order.

---

### 1. Metadata

```markdown
## Metadata

| Field | Value |
|---|---|
| Customer | [Customer name] |
| Project | [Project or programme name] |
| Canonical path | /Projects/[customer-slug]/PROJECT.md |
| Workspace | [Primary workspace or board space] |
| SPACE.md path | [Path to SPACE.md if it exists, or "not created"] |
| Last reviewed | [YYYY-MM-DD] |
| Last reviewed by | [Name or agent/skill name] |
| Created | [YYYY-MM-DD] |
| Status | [Active / On hold / Closed] |
```

---

### 2. Purpose

One sentence only. What this project is, who it is for, and why it exists.

```markdown
## Purpose

[One sentence: what the project is, who it is for, and why it exists.]
```

---

### 3. Outcomes and success measures

What success looks like. Be specific where possible.

```markdown
## Outcomes and success measures

- [Outcome 1 — specific and measurable where possible]
- [Outcome 2]
- [...]

### What would make this project fail

- [Failure condition 1]
- [...]
```

---

### 4. Scope

What is explicitly in scope. If an item is contested, note it.

```markdown
## Scope

- [Item 1]
- [Item 2 — contested, see decision log entry [date]]
- [...]
```

---

### 5. Non-scope

What is explicitly out of scope.

```markdown
## Non-scope

- [Item 1]
- [Item 2]
- [...]
```

---

### 6. Stakeholders and roles

Key people only. Include enough context to understand their relationship to the project.

```markdown
## Stakeholders and roles

| Name | Organisation | Role | Notes |
|---|---|---|---|
| [Name] | [Org] | [Role — e.g. Senior Sponsor, Programme Lead, Technical Contact] | [Any relevant notes] |
```

---

### 7. Workspace navigation

Where the project lives operationally. Agents use this section to orient themselves without blind searching.

This section should contain only project-specific navigation anchors. Space-wide conventions, field schemas, status definitions, and naming rules belong in `SPACE.md` if it exists.

```markdown
## Workspace navigation

### Planning workspace

- Primary board or list: [Name / ID / "not verified"]
- Parent project item: [ID or "not applicable"]
- Internal delivery board: [List/view/task or "not verified"]
- External shared board: [List/view/task or "not verified"]
- Context doc copy: [Doc ID/path or "not present"]
- Config doc: [Doc ID/path or "not present"]
- SPACE.md: [path or "not created"]

### Document repository

- Canonical project context: [path]
- Project documents: [path]

### Collaboration channels

- Primary channel: [name or "not verified"]
- Customer-facing channel: [name or "none"]

### Key contacts

- Escalation contact: [Name, email, or handle]
```

---

### 8. Current delivery shape

How the project is structured right now. Updated only when the delivery model or milestone logic materially changes.

```markdown
## Current delivery shape

### Approach

[2 to 4 sentences: delivery model, methodology, and any meaningful constraints on how delivery works. Keep this durable.]

### Phases

| Phase | Description | Status |
|---|---|---|
| [Phase name] | [What happens in this phase] | [Not started / In progress / Complete] |
```

---

### 9. Current state

A plain-language snapshot of where the project is right now.

Rules:
- always overwrite, never append
- maximum 120 words
- no history, no meeting-by-meeting recap
- must state current focus, main blocker or concern, and immediate next shift
- keep it durable enough to survive normal board churn

```markdown
## Current state

**RAG status:** [Red / Amber / Green]
**Current phase:** [Phase name]
**As of:** [YYYY-MM-DD]

[2 to 4 sentences: what is happening right now, what the immediate focus is, what the main blocker or concern is, and what changes next.]
```

---

### 10. Milestones

Keep only project-shaping dates and gates. Overwrite on each update. Stale milestones are worse than none.

```markdown
## Milestones

| Milestone | Target date | Status | Notes |
|---|---|---|---|
| [Milestone name] | [YYYY-MM-DD] | [Not started / In progress / At risk / Complete] | [Relevant note] |
```

Do not use this table as a proxy for the whole release plan.

---

### 11. Risks, assumptions, dependencies

Current project-level RAID picture. Overwrite on each update. Resolved items belong in the decision log, not here.

```markdown
## Risks, assumptions, dependencies

### Risks

| Risk | Likelihood | Impact | Owner | Mitigation |
|---|---|---|---|---|
| [Risk] | [H/M/L] | [H/M/L] | [Name] | [Action] |

### Assumptions

- [Assumption — state what is being assumed and what breaks if it is wrong]
- [...]

### Dependencies

| Dependency | Owner | Due | Status |
|---|---|---|---|
| [Dependency] | [Name or team] | [Date or "TBC"] | [Status] |
```

If confidence is weak or evidence is incomplete, note that inline rather than presenting guesswork as fact.

---

### 12. Decision log

Append-only in substance. New entries go at the top. Do not materially edit or remove prior decisions. If a decision is superseded, add a new entry stating that.

```markdown
## Decision log

### [YYYY-MM-DD] — [Decision title]

**Decision:** [What was decided, in one or two sentences.]
**Rationale:** [Why this decision was made.]
**Made by:** [Name or group]
**Impact:** [What this changes or rules out]

---
```

Minor factual corrections are allowed where they do not alter the substance of the original decision.

---

### 13. Open questions

Only include unresolved questions that materially affect project truth or safe planning. When resolved, move the resolution to the decision log and remove it from here.

```markdown
## Open questions

| Question | Owner | Priority | Raised |
|---|---|---|---|
| [Question] | [Name or "unassigned"] | [H/M/L] | [YYYY-MM-DD] |
```

---

### 14. Supporting artefacts and retrieval paths

Every artefact that materially matters to this project.

**Do not use bare links or file names.** Every entry must include enough context for an agent to locate it via search without relying on a hardcoded URL.

A direct link may be included for convenience, but it is secondary to retrieval metadata and must not be the only locator.

```markdown
## Supporting artefacts and retrieval paths

### [Artefact name]

| Field | Value |
|---|---|
| Purpose | [What this document is and why it matters to the project] |
| Source system | [Document repository / board / chat / email / external] |
| Search terms | ["[customer name] training plan", filter: .docx] |
| Likely location | [Folder path or list name — not a full URL] |
| File type | [.docx / .xlsx / .md / doc / etc.] |
| Owner | [Name or role] |
| Authority rule | [What makes this the authoritative version] |
| Update cadence | [When this document is typically updated] |
| Direct link (optional) | [Current known URL/path, if useful] |
```

Repeat this block for each artefact.

---

### 15. Next recommended actions

Current next steps only. Always overwrite. Keep this section short and durable.

Rules:
- maximum 3 to 5 actions
- only include actions that materially affect project truth or the next project-shaping step
- do not mirror the active task board

```markdown
## Next recommended actions

1. [Action — owner — by when]
2. [Action — owner — by when]
3. [...]
```

---

## Agent usage notes

When an agent fetches `PROJECT.md`, it should:

1. Read the maintenance note first.
2. Read **Workspace navigation** to orient itself before making planning or document calls.
3. Check **Metadata — Last reviewed** and **Current state — As of** against the staleness thresholds before proceeding.
4. Read **Current state** to understand the immediate context.
5. Use **Supporting artefacts and retrieval paths**, especially search terms and likely location, to locate documents.
6. Check **Metadata — SPACE.md path** and load `SPACE.md` if workspace-aware work is involved and the file exists.
7. Treat **Decision log** as authoritative on anything that was previously debated, changed, or superseded.
8. Ask the user whether to refresh `PROJECT.md` if conversation evidence shows material drift from the current file.

Agents should not assume a stored URL is still correct. Retrieval metadata takes precedence over convenience links.
If the stored path is absent or stale, look first in the project data mapping and the relevant project folder, then broaden to a general repository search before assuming `PROJECT.md` does not exist.

---

## SPACE.md relationship

If a `SPACE.md` exists for the workspace associated with this project, its path is recorded in both the Metadata section and the Workspace navigation section.

`SPACE.md` holds workspace-specific navigation detail such as:
- list IDs
- custom field keys
- status definitions
- naming conventions

Agents doing workspace-aware work should load `SPACE.md` alongside `PROJECT.md`, not instead of it.

`PROJECT.md` does not duplicate `SPACE.md` content. It references it.

If no `SPACE.md` exists yet, mark that explicitly as `not created` and continue without inventing one.

---

## What PROJECT.md is not

- Not a task list — task detail lives in the planning board
- Not a status report — current state is a durable snapshot, not a weekly report
- Not a PRD — scope and outcomes are here, but detailed requirements belong in a separate artefact referenced in Supporting artefacts and retrieval paths
- Not a meeting log — decisions are captured here, meeting notes belong in their source system
- Not a customer-facing document — it is written for agents and PMs
- Not a substitute for lightweight PM context where no real project structure exists

---

## Validation checklist

Before publishing or handing off a `PROJECT.md`, verify:

- [ ] Maintenance note for humans and LLMs is present near the top of the file
- [ ] Metadata includes a valid canonical path and `Last reviewed` date
- [ ] Purpose is a single clear sentence
- [ ] Scope and non-scope are distinct and unambiguous
- [ ] Current state is current, concise, and overwritten rather than appended
- [ ] Current state `As of` date is within the last 14 days, or staleness has been explicitly flagged to the user
- [ ] Milestones are current or explicitly marked at risk
- [ ] Every artefact in Supporting artefacts and retrieval paths has search terms and a likely location, not just a name or URL
- [ ] Artefact entries are not duplicated
- [ ] Decision log entries are in reverse chronological order, newest at top
- [ ] Open questions that have been resolved are removed and reflected in the decision log
- [ ] SPACE.md path is populated or explicitly marked `not created`
- [ ] The canonical path is registered in the project data mapping under `project_context_path`, or a fallback location if no mapping exists
- [ ] File delivery has been confirmed — either written to the document repository directly, or download and upload instructions provided to the user
- [ ] The file is not overloaded with volatile board-level detail
