# Conformance fixtures

Fixtures exercise OKF Tasks v0.1. `manifest.json` covers bundle conformance, navigation prominence, embedded `Task.time[]` entries and fragment identities, Tracker Profiles, scoped external identities, and both standard placements; `export-manifest.json` covers external-artefact preparation. Both are consumed independently by the Python and TypeScript implementations.

Hand-authored fixtures cover the minimal document, base OKF failure, and bad embedded-time rollup. Deterministic fixtures under `generated/` cover task fields and headings, workstreams, embedded time methods, estimates, points, sync authority, Tracker Profile default uniqueness, external uniqueness, reopening history, unknown concepts, broken-link warnings, strict durable-link connectivity and volatile-concept exclusions, and generated indexes.

`transitions.json` enumerates every normal lifecycle edge. Tests evaluate all 64 source/target pairs, including idempotent same-state updates.

The external-artefact corpus covers GitHub and GitLab conversion, credential stripping, untrusted instruction text, secrets in text and links, Windows, POSIX and home-relative paths, `file:` URIs, missing and escaping links, insecure HTTP, and remote-image policy.

Run the fixtures through the reference implementation:

```text
python skills/okf-task-lifecycle/scripts/okf_tasks.py validate --root conformance/valid/minimal
python skills/okf-task-lifecycle/scripts/okf_tasks.py validate --root conformance/invalid/missing-type
```

Regenerate and verify the generated corpus:

```text
python conformance/generate_fixtures.py
python conformance/generate_fixtures.py --check
```
