# repo-admin.json

Use this file when the repo should be re-bootstrapable by later agents.

## Goal

Keep the config small and deterministic.

It should answer:

- what repo type is this
- which license should be applied
- what short product summary should appear in GitHub metadata
- whether PR-based protection is required
- who owns review requests
- which named ruleset policy should be maintained
- whether release automation is expected later

## Suggested shape

```json
{
  "repoType": "service",
  "license": "Apache-2.0",
  "summary": "Service for ...",
  "descriptionWip": true,
  "enforcePrs": true,
  "releaseProfile": "generic",
  "codeOwners": ["@example-maintainer"],
  "rulesetName": "Protect default branch",
  "requiredApprovals": 1,
  "requireCodeOwnerReview": true,
  "requireReviewThreadResolution": true,
  "organizationAdminBypass": false
}
```

## Notes

- `summary` should be product-facing and reusable for both setup and final description generation.
- `descriptionWip` should usually be `true` during setup and become `false` only after finalisation.
- `releaseProfile` can stay unset when release/version automation is intentionally deferred.
- `codeOwners` must contain accounts or teams that can review the repository. Keep repository-specific values in the consuming repository, not in shared templates.
- `rulesetName` is the stable lookup key. The helper discovers GitHub's generated ruleset ID at runtime.
- Set `organizationAdminBypass` only after confirming the repository is owned by an organisation and the exception matches the user's governance intent.
