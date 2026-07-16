# Test prompts

## 1. Create a durable task
Prompt: "Use $repo-task-lifecycle to register this implementation-ready work package in the repository."
Expected:
- creates a meaningful `tasks/<slug>/task.md`
- records status as proposed until readiness is confirmed
- rebuilds the generated index

## 2. Parallel workstreams
Prompt: "This task has API, UI, and integration workstreams that will run concurrently."
Expected:
- creates separate workstream records without duplicating the parent task
- preserves single-writer ownership of task.md and the index
- routes physical worktree setup to `worktree-task-coordinator`

## 3. Premature completion
Prompt: "The code is merged, so mark the task done even though live verification is pending."
Expected:
- keeps Git, integration, deployment, and live evidence distinct
- refuses to equate merge with full completion

## 4. Canonical truth boundary
Prompt: "Put the new permanent product rule only in the task record."
Expected:
- records the task impact if useful
- routes durable product truth to `repo-knowledge-engineering`

## 5. External tracker mapping
Prompt: "Publish these local tasks to our tracker and rename every folder to its new issue number."
Expected:
- retains meaningful repository slugs
- stores external IDs as references
- delegates publication to `tracker-publisher`
