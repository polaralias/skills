# repo-admin.json

Use this file when the repo should be re-bootstrapable by later agents.

## Goal

Keep the config small and deterministic.

It should answer:

- what repo type is this
- which license should be applied
- what short product summary should appear in GitHub metadata
- whether PR-based protection is required
- whether release automation is expected later

## Suggested shape

```json
{
  "repoType": "mcp",
  "license": "Apache-2.0",
  "summary": "FastMCP server for ...",
  "descriptionWip": true,
  "enforcePrs": true,
  "releaseProfile": "mcp"
}
```

## Notes

- `summary` should be product-facing and reusable for both setup and final description generation.
- `descriptionWip` should usually be `true` during setup and become `false` only after finalisation.
- `releaseProfile` can stay unset when release/version automation is intentionally deferred.
