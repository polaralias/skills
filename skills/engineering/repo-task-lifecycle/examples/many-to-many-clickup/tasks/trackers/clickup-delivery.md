---
type: Tracker Profile
tracker: clickup-delivery
default: true
system: clickup
host: https://app.clickup.com
resource: task
scope:
  kind: list
  id: example-list
  key: Example delivery
  workspace_id: example-workspace
  space_id: example-space
sync:
  mode: bidirectional
  authority: repository
status_map:
  proposed: proposed
  ready: ready
  in-progress: in-progress
  blocked: blocked
  validation: validation
  done: done
  superseded: superseded
  deferred: deferred
field_map:
  tags:
    remote: tags
    strategy: read-only
discovery:
  observed_at: '2026-10-19T09:00:00Z'
  fingerprint: sha256:example-only
---

# Example ClickUp delivery

Dummy discovery; refresh against an explicitly selected real List before use.
