# OKF 0.1 repository-knowledge profile

Use this profile when a repository adopts Open Knowledge Format output for its canonical or derived knowledge bundle.

The external contract is the [Open Knowledge Format 0.1 draft specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). This bundled profile defines how the repository-knowledge skills apply that intentionally minimal format without replacing their authority and evidence rules.

## Adoption boundary

Prefer a bounded bundle such as `docs/knowledge/`. A bundle may be a subdirectory of a larger repository, so do not convert every repository Markdown file merely to claim conformance.

Keep these outside the required bundle unless the repository deliberately chooses otherwise:

- root `README.md`, `AGENTS.md`, and `CLAUDE.md`
- task and workstream records
- worktree coordination manifests
- transient handoffs and session artefacts
- implementation plans whose established schema should remain unchanged

A durable root or nested `README.md` that serves as canonical navigation, project context, or an enduring entry point is a good deliberate exception. Give it normal OKF frontmatter, `navigation.role: entry-point` where appropriate, an explicit `timestamp`, and useful links so it participates in the governed graph. Generated, vendored, transient, or intentionally out-of-scope READMEs need not be promoted merely because of their filename.

Existing repositories may retain their current knowledge structure. Recommend OKF for new or deliberately migrated canonical knowledge, but do not force a broad migration when it would weaken clearer repository conventions.

## Required format

Every concept is a UTF-8 Markdown file with parseable YAML frontmatter and a non-empty, self-explanatory `type`.

Recommended fields are:

- `title`: human-readable concept name
- `description`: one-sentence retrieval summary
- `resource`: absolute URI for an underlying asset, when one exists
- `tags`: short YAML string list
- `timestamp`: ISO 8601 datetime of the last meaningful content change; this is the portable last-updated value, not filesystem or Git time

Preserve unknown types and producer-defined fields when reading or round-tripping a bundle.

Use normal Markdown links for relationships. Prefer bundle-root-relative links when stability across local moves matters. Broken internal links are warnings to repair, not grounds for declaring the bundle malformed, but they do not connect the strict durable graph.

When more than one governed durable concept exists, keep the concepts in one resolved repository-local relationship graph. An incoming link counts, so reciprocal links are required only when useful in both directions. Keep links to terminal Tasks when they serve as live implementation-state evidence instead of rewriting a knowledge document merely to restate completion. Reserved indexes and logs, generated or vendor output, runbooks, handoffs, session records, and temporary or scratch files are outside this graph. Report orphan concepts and disconnected components; never invent a semantically weak link to satisfy connectivity.

## Repository-knowledge extensions

Use extension fields sparingly:

- `authority`: `canonical`, `evidence`, or `derived`
- `verification`: `verified-working`, `verified-limited`, `known-broken`, or `untested`
- `owner`: maintainer or team responsible for the concept, when known
- `generated_by`: producer name for generated material, when applicable
- `navigation`: optional retrieval prominence and first-reading metadata:
  - `role`: `entry-point`, `foundational`, `supporting`, or `reference`
  - `order`: non-negative integer; lower sparse values read first within the same role

These fields express RKE semantics. They are not part of the OKF core and consumers must tolerate them as extensions.

Use `navigation` only when a bundle benefits from an explicit starting surface or layered reading path. It does not replace Markdown links, directory hierarchy, concept authority, or Task execution priority. A visual consumer should distinguish entry points and foundational concepts and may highlight a selected role, but should retain unmatched concepts as context by default. ADRs and other decisions should remain descriptive types such as `Architecture Decision` or `Decision`; their type and navigation role may both contribute to presentation.

Do not encode task status or worktree state in this profile.

## Concept types

OKF has no central type registry. Prefer descriptive values such as:

- `Product Contract`
- `Architecture Concept`
- `Decision`
- `Glossary Concept`
- `Support Boundary`
- `Validation Evidence`
- `Runbook`
- `Reference`

Reuse an established repository type before inventing a synonym.

### Visualisation concepts

Use `type: Visualization` when a durable repository concept must explain how to generate, interpret, and verify a visual view of other OKF or repository records. A Visualisation concept is canonical metadata about a derived view; the rendered HTML, Mermaid, image, or other output remains derived.

Start from `assets/okf/visualization.md.template`. In addition to the normal retrieval fields and explicit `timestamp`, record:

- `source`: bundle-relative link to the canonical source record or index;
- `renderer`: stable command or producer identity;
- `output`: bundle-relative link to the derived artefact;
- `temporal_basis`: event field used for chronological ordering, normally `timestamp`;
- `history_model`: normally `current-records-only` unless retained historical concepts or versions support reconstruction;
- `drift_policy`: the comparison heuristic and its evidential limit;
- `authority: derived` unless the concept body itself records a canonical visualisation contract;
- `verification`: the honest current generation or smoke-test state.

Advance `timestamp` when the visualisation's source contract, renderer, output, visual encoding, interpretation, or verification meaningfully changes. Regenerating byte-identical output does not require a concept update. Never use the generated file's modification time as concept freshness.

If a derived view deliberately omits source files, record the exclusion policy in the Visualisation concept and retain the resolved omissions as generation evidence. OKF Tasks uses bundle-relative `--exclude` globs, `.okf-visualization-ignore`, or `--exclude-from`; Graph and Reader must receive the same scope. Directory-name entries ending in `/` match at every depth, preventing nested dependency Markdown from leaking into Reader. A visualisation exclusion never changes knowledge authority or conformance and cannot excuse a governed orphan or broken link.

Standalone OKF HTML visualisations embed their pinned rendering runtimes and bundle data so local review makes no runtime network requests. Dense graph overviews retain labelled entry-point, foundational, and highly connected landmarks; selected incoming and outgoing neighbourhoods reflow into a close, readable focus with modest padding and every direct node visible and non-overlapping.

Temporal order alone does not establish documentation drift. A linked source with a newer timestamp than its target is a useful review candidate, but consumers must label that relationship as a possible signal and inspect semantic content and evidence before changing either concept. A bundle containing only current concepts cannot reconstruct historical fact values merely by moving an as-of control backwards.

## Task and Workstream boundary

Task, Workstream, embedded time, Tracker Profile, and task-visualisation behaviour belongs to the [OKF Tasks v0.1 profile](https://github.com/polaralias/okf-tasks/blob/v0.1.0/SPEC.md). Use `repo-task-lifecycle` for those records and its compatible `okf-tasks` command or feature-identical bundled fallback for mutations and validation. RKE may create and maintain the canonical knowledge concepts they link to, but it must not independently redefine the OKF Tasks schema, lifecycle, time model, provider mappings, or renderer contract.

## Reserved files

- `index.md` is progressive-disclosure navigation. It normally has no frontmatter. The bundle-root index may declare `okf_version: "0.1"` in frontmatter.
- `log.md` is an optional directory update history with ISO `YYYY-MM-DD` headings, newest first.

Use singular `log.md`. Do not create `logs.md` as the OKF history surface.

Generate indexes from concept `title` and `description` where practical. The bundled generator marks the indexes it owns and refuses to replace unmarked, hand-maintained, or producer-owned indexes by default. Use `--force` only after deliberately confirming that an existing index is safe to replace. Keep meaningful manual grouping when deterministic rebuilding cannot preserve it.

Use logs for knowledge creation, update, deprecation, or promotion events. Do not duplicate routine commits, task progress, or the full Git history.

## Citations and evidence

Put externally supported claims under a final `# Citations` section with numbered Markdown links. Repository-local evidence may be linked as another concept.

OKF formatting does not prove a claim. RKE authority, runtime evidence, tests, and source quality still determine whether a concept is canonical, evidential, or derived.

## Validation

Run:

```text
python scripts/okf_bundle.py build-indexes --bundle <canonical-bundle>
python scripts/okf_bundle.py validate --bundle <canonical-bundle> --require-version
```

Use validation without `--require-version` when consuming an external bundle that legitimately omits the optional version declaration.

The validator requires PyYAML. If it is unavailable, the script exits with the exact installation command rather than silently weakening frontmatter checks.

Errors cover the hard conformance surface and malformed optional fields. Warnings cover recommended metadata, missing version declarations, empty indexes, and broken links. Do not turn warnings that the specification explicitly tolerates into hard failures unless repository policy deliberately defines a stricter profile.
