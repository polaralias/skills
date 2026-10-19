---
type: Tracker Profile
tracker: github-main
system: github
host: https://github.com
resource: issue
scope:
  kind: repository
  id: R_main
  key: example/main
sync:
  mode: bidirectional
  authority: tracker
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
---

# github-main

Fixture Tracker Profile.
