---
type: Tracker Profile
tracker: github-main
default: true
system: github
host: https://github.com
resource: pull-request
scope:
  kind: repository
  id: R_kgDOTbr1Iw
  key: polaralias/okf-tasks
  name: OKF Tasks
sync:
  mode: manual
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
  description:
    remote: body
  tags:
    remote: labels
    strategy: managed-subset
    managed_prefix: "okf:"
discovery:
  observed_at: 2026-07-18T10:00:00Z
  fingerprint: sha256:visualisation-github-main
  capabilities:
    pull_requests: true
---

# OKF Tasks GitHub repository

## Setup evidence

- Provider system: `github`.
- Resource: `pull-request`.
- Selected repository: `polaralias/okf-tasks` (stable ID `R_kgDOTbr1Iw`).
- Discovery observed: `2026-07-18T10:00:00Z` with fingerprint `sha256:visualization-github-main`.
- Authentication is read from the runtime environment; no credential or credential reference is stored here.
- Project default selected: `yes`.

## Mapping review

This manually reconciled profile demonstrates scoped pull-request evidence. Its open/closed projection is intentionally repository-authoritative and lossy.
