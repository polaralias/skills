# OpenWiki coexistence

Use this reference when a repository contains or is considering an OpenWiki-generated knowledge bundle.

OpenWiki code mode maintains repository documentation under `openwiki/`, uses `openwiki/INSTRUCTIONS.md` as its user-authored brief, and may maintain marked sections in root agent instruction files. OpenWiki 0.2 emits OKF-compatible Markdown concepts and deterministic directory indexes.

## Ownership model

Treat `openwiki/` as producer-owned:

- OpenWiki writes and regenerates its concept files and indexes.
- RKE may read and validate the bundle but must not run its index builder against `openwiki/`.
- Edit `openwiki/INSTRUCTIONS.md` only when the user wants to change OpenWiki's scope or priorities.
- Preserve OpenWiki-managed marker blocks in `AGENTS.md` and `CLAUDE.md`; update surrounding repository guidance without rewriting the producer block.
- Allow OpenWiki's non-Markdown operational metadata, such as update checkpoints, to remain inside its directory. OKF conformance applies to the Markdown bundle documents.

Do not let OpenWiki and RKE silently co-own the same canonical files.

## Authority model

OpenWiki output is generated or derived knowledge by default. It is valuable for code discovery, architecture orientation, and change detection, but formatting and generation do not make its claims canonical or verified.

RKE should:

1. Read relevant OpenWiki concepts during discovery and cross-artifact analysis.
2. Compare claims with code, runtime evidence, decisions, and canonical contracts.
3. Correct OpenWiki through its producer workflow when generated documentation is stale.
4. Promote durable verified conclusions into the canonical bundle when future work must rely on them.
5. Link canonical and derived concepts rather than copying large bodies in both directions.

## Recommended layout

```text
README.md                 repository reading order
AGENTS.md                 agent routing and producer-managed block
docs/knowledge/           canonical RKE-managed OKF bundle
openwiki/                 OpenWiki-managed derived OKF bundle
```

An existing repository may choose different paths. What matters is explicit ownership and reading order.

## Update workflow

- Let OpenWiki create or update its bundle through its normal interactive or CI/PR path.
- Review generated changes as derived documentation, including unexpected deletions, broad rewrites, unsupported claims, and secret or machine-local leakage.
- Run the OKF validator read-only against `openwiki/` when useful. Do not require the optional root version declaration unless OpenWiki emits one.
- Re-run the RKE drift check when OpenWiki reveals a contradiction with canonical knowledge.
- Never widen canonical support claims from an OpenWiki page alone.

OpenWiki is an optional producer and consumer ecosystem participant. RKE must remain usable without installing it.

## Authoritative references

- [OpenWiki repository and code-mode behavior](https://github.com/langchain-ai/openwiki)
- [OpenWiki 0.2 OKF announcement](https://www.langchain.com/blog/openwiki-0-2-adds-okf-support)
