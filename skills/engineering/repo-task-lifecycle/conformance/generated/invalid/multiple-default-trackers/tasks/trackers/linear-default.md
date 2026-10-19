---
type: Tracker Profile
tracker: linear-default
system: linear
host: https://api.linear.app
resource: issue
scope:
  kind: team
  id: team-id
  key: ENG
sync:
  mode: bidirectional
  authority: repository
status_map:
  proposed: open
  ready: open
  in-progress: open
  blocked: open
  validation: open
  done: closed
  superseded: closed
  deferred: closed
field_map:
  title:
    remote: title
  tags:
    remote: labels
    strategy: managed-subset
    managed_prefix: 'okf:'
discovery:
  observed_at: '2026-07-17T09:00:00Z'
  fingerprint: sha256:fixture
  capabilities:
    webhooks: true
default: true
---

# linear-default

Fixture Tracker Profile.
