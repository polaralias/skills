---
type: Tracker Profile
tracker: linear-security
default: true
system: linear
host: https://api.linear.app
resource: issue
scope:
  kind: team
  id: 6c02a067-25da-4f67-b2e3-c0aa3217f01a
  key: SEC
  name: Security
sync:
  mode: bidirectional
  authority: repository
status_map:
  proposed: 0cb1dfe4-8fb5-4ea4-885a-72e0f460f71b
  ready: 2dd49ec8-52f5-41ce-ba45-7b2477827410
  in-progress: 44532c8f-0ff6-4d90-b988-a78b801b15a5
  blocked: 61a44f94-2892-4c98-ae01-7bcf5938d749
  validation: 7457f6ed-e1d1-4f16-86d4-dddf0f9df71a
  done: 8d8ab38f-e9ab-45bd-8eef-b80d82976567
  superseded: cc694d19-9e83-454d-97d7-b2b41897c2ea
  deferred: 0d55bdb1-9e5b-4dd6-9a43-2c999ea9c3c3
field_map:
  title:
    remote: title
  description:
    remote: description
  assignees:
    remote: assignee
  priority:
    remote: priority
  tags:
    remote: labels
    strategy: managed-subset
    managed_prefix: "okf:"
discovery:
  observed_at: 2026-07-17T11:45:00Z
  fingerprint: sha256:linear-security-fixture
  capabilities:
    webhooks: true
    arbitrary_fields: false
---

# Linear Security

## Setup evidence

- Provider system: `linear`.
- Resource: `issue`.
- Selected team: `SEC` (stable ID `6c02a067-25da-4f67-b2e3-c0aa3217f01a`).
- Discovery observed: `2026-07-17T11:45:00Z` with fingerprint `sha256:linear-security-fixture`.
- Authentication is read from the runtime environment; no credential or credential reference is stored here.
- Project default selected: `yes`.

## Mapping review

Team-scoped workflow and field mappings for the Security team. The distinct state IDs preserve round-trip behaviour.
