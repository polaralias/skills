# OKF knowledge profile

RKE reads UTF-8 Markdown concepts with YAML mappings and non-empty `type`, compatible with OKF 0.1 and 0.2. Unknown types and producer fields are preserved. Missing optional metadata produces advice rather than invented hard requirements. The [upstream OKF specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) owns the format; RKE graph connectivity is an additional repository check and is reported separately as `graphConformant` from `okfConformant`.

## Metadata and links

- `generated: {by, at}` identifies the authoring process and optional content datetime. Existing `timestamp` is a legacy fallback. Use explicit UTC offsets.
- `verified` may be one `{by, at}` mapping or a list. Preserve other producers' events; never invent human review. Valid events yield advisory unverified, machine-confirmed or human-reviewed signals, with `human:` actors identifying declared human review.
- `status` is draft, stable or deprecated for knowledge; absent means stable. `stale_after` declares expiry independently of source hashes. Task, Workstream and Tracker Profile status belongs to OKF Tasks and is not reclassified here.
- `sources` entries identify a non-empty `resource` and may carry stable IDs for footnote joins. Resources can be links, relative files or scope descriptors. Only local Markdown resources become graph relationships; URLs are not fetched and scope text is not an execution instruction.
- Relative links resolve from the concept; `/concept.md` resolves from the containing bundle root. A root index declares `okf_version`; indexes are optional. Index changes refresh relationship resolution even when concepts are unchanged.

A high retrieval rank, declared human review or a current hash does not establish semantic truth. Inspect the evidence. Frontmatter signals are producer claims; `.rke/repo-context.json` source bindings and exact review identities separately establish RKE freshness.

## Computation and execution ownership

Attested Computation can retain runtime, parameters, computation, executor/receipt and attester declarations as knowledge. RKE does not execute them, follow remote resources, install tools or grant credentials. Any launch requires current user authorization and explicit command selection.

OKF Tasks remains an independent specification and authoritative CLI for Tasks, Workstreams, acceptance, effort, providers, tracker profiles and visualization. Use the [adapter](okf-tasks-adapter.md) for strict task validation and mutate records through that producer. Supporting OKF knowledge 0.2 does not migrate the separate Tasks schema.

## Bounded navigation

Use `knowledge graph --bundle <dir> --focus <concept> --depth 1 --limit 40` to inspect a selected neighbourhood. Without focus, landmarks and connected hubs guide orientation. Edges and nodes are bounded and omitted counts remain visible. External references are reported without importing another producer's graph. Generated navigation remains disposable and never overrides canonical source.
