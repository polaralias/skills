# Publication and Release Review

Load this reference only when public-readiness, release automation, or a publication safety pass is in scope. The [publication extension](extensions/publication.md) owns the EWF gate and `rke publication scan` route. This reference preserves the editorial and release-choice guidance from the archived finaliser; it does not authorise a release, repository-setting change, or provider write.

## Establish the release truth

Read the human-facing README, operating guidance, canonical architecture and support boundaries, active plans, and actual package or application entrypoint. Inspect repository-defined build, test and release commands before executing them. Check a representative public invocation, including its error path when material. Classify each public statement as observed, code-supported, accepted limitation, known gap, or stale. A passing build cannot establish that installation instructions or first-contact documentation are truthful.

Review `TODO`, `FIXME`, stale “next step” and open-blocker wording in public surfaces. Give each outdated plan, migration note, archive, example or setup story an explicit disposition: update, retain as clearly historical evidence, or remove after preserving unique truth. Prefer a human-facing README that explains the project, installation and use; place agent maintenance routines in `AGENTS.md` or deeper docs. Keep reading-order links and any glossary or decision lifecycle aligned. Do not call the repository publish-ready while product behaviour or public documentation still materially disagree.

## Bounded safety sweep

Run `rke publication scan` and inspect its coverage, findings, and omitted files. Then apply judgement to the areas automation cannot settle:

- Secrets and credentials: keys, tokens, passwords, private keys, OAuth/cloud credential files, `.env` files, and secret-like values in docs, examples, fixtures, history and packaged artefacts. Do not echo values in a report.
- Local traces: absolute home paths, usernames, workstation names, `AppData`, OneDrive, `.codex`, `.agents`, localhost-only routes, and development-specific assumptions. Distinguish an intentional public example from accidental disclosure.
- PII: personal email, phone, exported IDs and names in logs or assets. An intended public maintainer identity is different from an accidental private identity.
- Generated clutter: caches, build output, swap files, scratch notes and missing ignore rules. After deliberate deletion or moves, inspect empty directories; keep documented placeholders and packaging structure.
- Binary and image metadata: author fields, export paths and embedded software traces when assets are in scope. Harmless timestamps need no stripping unless the publication standard requires it.
- Archives and completed docs: retain genuine historical evidence with clear status; remove duplicate or misleading current-answer surfaces after preserving unique rationale.

The scan is an automated hygiene signal, not semantic approval. Treat matches as candidates for review and coverage gaps as unknowns. Use an independently verified scanner when required by the release policy; if unavailable, report the gap rather than claiming a clean history. Re-run focused validation and the scan after cleanup. Report what is clean, what was corrected, what remains public by design, and what remains unverified.

## Choose release automation deliberately

First determine whether tagged releases are needed, what single repository source owns the version, and which artefacts are meant to ship. If the repository already has automation, inspect it before changing it. For a new or repaired setup, route to the separate `repo-setup` capability and its maintained release-profile assets; do not copy archived workflow YAML into EWF.

| Profile | When useful | Version and release check |
| --- | --- | --- |
| Android | An app ships an APK or other declared Android artefact. | Read Gradle `versionName` and `versionCode`; verify the tagged workflow builds and names the intended artefact. |
| MCP or Python | A Python package or server uses project metadata as release truth. | Match the release tag to `pyproject.toml` project version and validate the built package. |
| Home Assistant | An integration's manifest owns the shipped version. | Match the tag to `custom_components/<domain>/manifest.json` and validate the integration package. |
| Generic | A repository-level `VERSION` is the canonical source. | Make the draft and tag workflow read that value; avoid a separate label-derived release version. |

These are profile-selection questions, not universal requirements. Verify current actions, permissions, provenance and artefact paths against the selected repository before editing or running release automation. The repo-setup assets own starter workflow mechanics; RKE release validation and the project's CI own deterministic checks. A completed review or resolved `publication-safety` gate still leaves the actual publish action separate.
