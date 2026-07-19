from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml


TASK_GROUPS = {
    "platform-foundations": (
        "Establish repository boundaries",
        "Define service ownership",
        "Provision development environments",
        "Standardise configuration loading",
        "Build shared authentication middleware",
        "Introduce feature flagging",
        "Automate dependency updates",
        "Publish platform readiness evidence",
    ),
    "identity-security": (
        "Model tenant isolation",
        "Implement token rotation",
        "Add privileged access reviews",
        "Enforce workload identity",
        "Harden session management",
        "Instrument authentication failures",
        "Complete threat model review",
        "Validate security launch controls",
    ),
    "data-migration": (
        "Inventory legacy data sources",
        "Define canonical customer schema",
        "Build change data capture pipeline",
        "Create reconciliation reports",
        "Migrate reference data",
        "Run customer migration rehearsal",
        "Resolve migration exceptions",
        "Approve production cutover data",
    ),
    "customer-experience": (
        "Map onboarding journey",
        "Build account creation flow",
        "Implement organisation switching",
        "Add migration progress centre",
        "Design recoverable form states",
        "Meet accessibility acceptance",
        "Complete guided onboarding trials",
        "Publish customer experience readiness",
    ),
    "observability-release": (
        "Define service level objectives",
        "Create cross-service trace model",
        "Build operational dashboards",
        "Add release health checks",
        "Exercise rollback automation",
        "Run failure injection scenarios",
        "Complete release rehearsal",
        "Approve general availability",
    ),
}

ARCHITECTURE_DOCS = (
    "system-context",
    "container-topology",
    "request-lifecycle",
    "identity-boundary",
    "tenant-isolation",
    "data-platform",
    "event-backbone",
    "deployment-topology",
    "resilience-model",
    "observability-model",
    "security-architecture",
    "migration-architecture",
)

ADRS = (
    "modular-service-boundaries",
    "versioned-event-envelope",
    "oidc-workload-identity",
    "tenant-key-partitioning",
    "transactional-outbox",
    "idempotent-command-handling",
    "schema-registry-compatibility",
    "zero-downtime-database-change",
    "regional-active-passive",
    "central-policy-evaluation",
    "short-lived-access-tokens",
    "immutable-deployment-artifacts",
    "progressive-delivery",
    "open-telemetry-signals",
    "error-budget-release-gates",
    "encrypted-event-payloads",
    "customer-managed-retention",
    "migration-dual-read-window",
    "bounded-retry-policies",
    "architecture-evidence-records",
)

SERVICES = (
    "identity-service",
    "tenant-service",
    "customer-service",
    "migration-service",
    "workflow-service",
    "notification-service",
    "audit-service",
    "reporting-service",
)

INTERFACES = (
    "public-api",
    "identity-events",
    "customer-events",
    "migration-control-api",
    "audit-event-contract",
    "reporting-query-api",
)

QUALITY_ATTRIBUTES = (
    "availability",
    "security",
    "performance",
    "recoverability",
    "operability",
)


def slugify(value: str) -> str:
    return "-".join(value.lower().replace("/", " ").split())


def title(value: str) -> str:
    display = value.replace("-", " ").title()
    return display.replace("Artifacts", "Artefacts")


def stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def markdown_document(metadata: dict[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).rstrip()
    return f"---\n{frontmatter}\n---\n\n{body.strip()}\n"


def task_body(task_title: str, dependencies: list[str], knowledge_path: str) -> str:
    dependency_lines = (
        "\n".join(f"- [{title(item)}](../{item}/task.md)" for item in dependencies)
        if dependencies
        else "- This task begins its delivery chain."
    )
    return f"""# {task_title}

## Outcome

Deliver the observable result described by **{task_title.lower()}** and leave reviewable evidence for the next task.

## Scope

- In scope: implementation, validation, and handoff for this delivery slice.
- Out of scope: unrelated product changes and production credentials.

## Acceptance

- [ ] The result is demonstrable in the dummy programme environment.
- [ ] Relevant tests and operational evidence are linked.
- [ ] Follow-on tasks can consume the outcome without rediscovery.

## Dependencies and risks

{dependency_lines}

## Related knowledge

- [Programme guidance]({knowledge_path})

## Evidence

- Dummy evidence will be attached as the task advances through validation.
"""


def task_metadata(slug: str, task_title: str, status: str, created: datetime, dependencies: list[str], group: str, index: int) -> dict[str, Any]:
    changed = created + timedelta(hours=4)
    metadata: dict[str, Any] = {
        "type": "Task",
        "task": slug,
        "title": task_title,
        "description": f"Deliver {task_title.lower()} for the {title(group)} initiative.",
        "status": status,
        "created": stamp(created),
        "timestamp": stamp(changed),
        "owner": f"team-{group}",
        "priority": ("high", "high", "medium", "medium", "normal", "normal", "high", "normal")[index % 8],
        "navigation": {"role": "supporting", "order": 200 + index * 10},
        "tags": [group, "complex-example", f"wave-{index // 2 + 1}"],
    }
    if dependencies:
        metadata["depends_on"] = [f"{item}/task.md" for item in dependencies]
    if status in {"in-progress", "validation", "done"}:
        started = created + timedelta(hours=1)
        finished = created + timedelta(hours=3)
        metadata.update(
            {
                "started": stamp(started),
                "effort_minutes": 120,
                "time": [
                    {
                        "id": f"{created:%Y%m%d}t{started:%H%M%S}z-agent-tracked",
                        "status": "closed",
                        "actor": "agent",
                        "started": stamp(started),
                        "finished": stamp(finished),
                        "elapsed_minutes": 120,
                        "effort_minutes": 120,
                        "method": "tracked",
                        "activity": "implementation",
                        "summary": f"Advanced {task_title.lower()} in the dummy programme.",
                    }
                ],
            }
        )
        if status == "done":
            metadata["finished"] = stamp(finished)
    return metadata


def task_portfolio_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    all_tasks: list[tuple[str, str, str]] = []
    statuses = ("done", "done", "validation", "in-progress", "ready", "proposed", "blocked", "ready")
    previous_group_tail: str | None = None
    base = datetime(2026, 6, 1, 8, tzinfo=timezone.utc)

    for group_index, (group, titles) in enumerate(TASK_GROUPS.items()):
        group_slugs = [slugify(item) for item in titles]
        for index, task_title_value in enumerate(titles):
            slug = group_slugs[index]
            dependencies: list[str] = []
            if index:
                dependencies.append(group_slugs[index - 1])
            elif previous_group_tail:
                dependencies.append(previous_group_tail)
            if index >= 3:
                dependencies.append(group_slugs[index - 3])
            created = base + timedelta(days=group_index * 9 + index)
            knowledge_path = f"../../docs/{group}.md"
            files[Path("tasks") / slug / "task.md"] = markdown_document(
                task_metadata(slug, task_title_value, statuses[index], created, dependencies, group, index),
                task_body(task_title_value, dependencies, knowledge_path),
            )
            all_tasks.append((slug, task_title_value, group))
        anchor = group_slugs[3]
        related = group_slugs[1:7]
        workstream = {
            "type": "Workstream",
            "task": anchor,
            "workstream": group,
            "title": f"{title(group)} coordination",
            "description": f"Coordinate the connected {title(group).lower()} delivery tasks.",
            "status": "in-progress",
            "created": stamp(base + timedelta(days=group_index * 9)),
            "timestamp": stamp(base + timedelta(days=group_index * 9 + 8)),
            "owner": f"lead-{group}",
            "branch": f"feat/{group}-programme",
            "navigation": {"role": "supporting", "order": 300 + group_index * 10},
        }
        related_links = "\n".join(f"- [{title(item)}](../../{item}/task.md)" for item in related)
        files[Path("tasks") / anchor / "workstreams" / f"{group}.md"] = markdown_document(
            workstream,
            f"""# {title(group)} coordination

## Assigned outcome

Keep the initiative's dependent tasks moving as one inspectable delivery chain.

## Owned and shared paths

- Owned: the dummy `{group}` implementation area.
- Shared: programme evidence and release coordination.

## Acceptance and validation

{related_links}

## Evidence

- The graph exposes task state, dependencies, and effort evidence together.

## Handoff

- Hand off validated outcomes to the next initiative boundary.
""",
        )
        previous_group_tail = group_slugs[-1]

    for group_index, group in enumerate(TASK_GROUPS):
        group_tasks = [(slug, task_title_value) for slug, task_title_value, task_group in all_tasks if task_group == group]
        links = "\n".join(f"- [{task_title_value}](../tasks/{slug}/task.md)" for slug, task_title_value in group_tasks)
        metadata = {
            "type": "Delivery Plan",
            "title": f"{title(group)} delivery plan",
            "description": f"Durable delivery guidance for the {title(group)} initiative.",
            "status": "current",
            "created": stamp(base + timedelta(days=group_index * 9)),
            "timestamp": stamp(base + timedelta(days=group_index * 9 + 8)),
            "tags": [group, "delivery-plan", "complex-example"],
            "navigation": {"role": "entry-point" if group_index == 0 else "foundational", "order": 10 + group_index * 10},
        }
        files[Path("docs") / f"{group}.md"] = markdown_document(
            metadata,
            f"""# {title(group)} delivery plan

## Intent

This document groups a deliberately busy set of tasks so graph, board, temporal, and focus views can be reviewed against realistic density.

## Delivery chain

{links}

## Review signals

| Signal | Expected interpretation |
| --- | --- |
| Blocked tasks | Inspect their incoming dependency chain. |
| Validation tasks | Review evidence and linked workstreams. |
| Completed tasks | Retain them as live implementation evidence. |
""",
        )

    files[Path("README.md")] = """# Complex task portfolio example

This generated dummy workspace stress-tests a task-heavy OKF graph with forty Tasks, five coordinating Workstreams, embedded time evidence, mixed lifecycle states, cross-initiative dependencies, and linked delivery plans.

Task `priority` expresses execution urgency. The independent `navigation` extension marks delivery plans as entry points or foundational reading surfaces; links remain the actual delivery and knowledge relationships.

- [Start with the platform plan](./docs/platform-foundations.md)
- [Inspect the first delivery task](./tasks/establish-repository-boundaries/task.md)
- [Follow the final release task](./tasks/approve-general-availability/task.md)
"""
    return files


def knowledge_metadata(kind: str, name: str, status: str, created: datetime, tags: list[str], role: str = "supporting", order: int = 100) -> dict[str, Any]:
    return {
        "type": kind,
        "title": title(name),
        "description": f"Detailed dummy {kind.lower()} for {title(name).lower()}.",
        "status": status,
        "created": stamp(created),
        "timestamp": stamp(created + timedelta(days=7)),
        "navigation": {"role": role, "order": order},
        "tags": [*tags, "architecture-example"],
    }


def architecture_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    base = datetime(2026, 4, 1, 9, tzinfo=timezone.utc)

    for index, name in enumerate(ARCHITECTURE_DOCS):
        adr_a = index % len(ADRS)
        adr_b = (index + 7) % len(ADRS)
        service_a = SERVICES[index % len(SERVICES)]
        service_b = SERVICES[(index + 3) % len(SERVICES)]
        files[Path("docs/architecture") / f"{name}.md"] = markdown_document(
            knowledge_metadata("Architecture Document", name, "current", base + timedelta(days=index), ["architecture", "system-design"], "entry-point" if index == 0 else "foundational", 10 + index * 10),
            f"""# {title(name)}

## Purpose and boundaries

This document defines the responsibilities, trust boundaries, and collaboration model for {title(name).lower()}. It is intentionally detailed enough to exercise the Reader while remaining connected to the wider decision graph.

## Component model

```mermaid
flowchart LR
  Client[Client] --> Gateway[Policy gateway]
  Gateway --> Service[Domain service]
  Service --> Events[(Event backbone)]
  Service --> Store[(Owned data)]
```

## Runtime flow

1. The caller presents a scoped identity and an idempotency key.
2. Policy is evaluated before domain state is loaded.
3. The domain service commits state and an event atomically.
4. Consumers process the versioned envelope and publish trace evidence.

## Failure handling

- Reject ambiguous tenant context before work begins.
- Bound retries and route exhausted work to reviewable recovery queues.
- Preserve correlation identifiers across synchronous and asynchronous boundaries.

## Security and operability

| Concern | Design response |
| --- | --- |
| Least privilege | Workload identities are scoped per service. |
| Auditability | Security-sensitive transitions emit immutable audit events. |
| Recovery | Replays remain idempotent and observable. |
| Drift | Linked decisions carry explicit last-meaningful-change timestamps. |

## Related decisions and components

- [ADR {adr_a + 1:03d}: {title(ADRS[adr_a])}](../decisions/adr-{adr_a + 1:03d}-{ADRS[adr_a]}.md)
- [ADR {adr_b + 1:03d}: {title(ADRS[adr_b])}](../decisions/adr-{adr_b + 1:03d}-{ADRS[adr_b]}.md)
- [{title(service_a)}](../services/{service_a}.md)
- [{title(service_b)}](../services/{service_b}.md)
""",
        )

    for index, name in enumerate(ADRS):
        architecture = ARCHITECTURE_DOCS[index % len(ARCHITECTURE_DOCS)]
        previous = ADRS[index - 1] if index else None
        status = "proposed" if index >= 17 else "accepted"
        previous_link = (
            f"- [Previous decision: {title(previous)}](./adr-{index:03d}-{previous}.md)"
            if previous
            else "- This is the root decision in the example chain."
        )
        files[Path("docs/decisions") / f"adr-{index + 1:03d}-{name}.md"] = markdown_document(
            knowledge_metadata("Architecture Decision", f"ADR {index + 1:03d}: {name}", status, base + timedelta(days=index * 2), ["adr", "decision"], "foundational", 150 + index * 10),
            f"""# ADR {index + 1:03d}: {title(name)}

## Context

The platform needs an explicit and reviewable choice for {title(name).lower()}. The decision affects service ownership, failure recovery, and the shape of evidence retained by delivery tasks.

## Decision

Adopt the named approach as the default architecture policy. Exceptions require a linked decision record that describes the narrower context and migration implications.

## Consequences

- Teams gain a consistent default and a visible dependency surface.
- Implementation work must preserve the documented compatibility boundary.
- Operational evidence becomes part of acceptance rather than a later activity.

<details>
<summary>Alternatives considered</summary>

Central coordination, implicit conventions, and provider-specific coupling were rejected because they weaken portability or make drift harder to review.

</details>

## Related architecture

- [{title(architecture)}](../architecture/{architecture}.md)
{previous_link}
""",
        )

    for index, name in enumerate(SERVICES):
        architecture = ARCHITECTURE_DOCS[(index * 2) % len(ARCHITECTURE_DOCS)]
        interface = INTERFACES[index % len(INTERFACES)]
        files[Path("docs/services") / f"{name}.md"] = markdown_document(
            knowledge_metadata("Service Design", name, "current", base + timedelta(days=40 + index), ["service", name], "supporting", 400 + index * 10),
            f"""# {title(name)}

## Responsibilities

- Own the service's domain invariants and persistence boundary.
- Publish versioned events after durable state changes.
- Expose health, readiness, trace, and domain metrics.

## API and data ownership

| Surface | Contract |
| --- | --- |
| Commands | Authenticated, idempotent, and tenant-scoped. |
| Queries | Pagination and stable consistency semantics. |
| Events | Versioned envelope with correlation and causation IDs. |

## Dependencies

- [{title(architecture)}](../architecture/{architecture}.md)
- [{title(interface)}](../interfaces/{interface}.md)
""",
        )

    for index, name in enumerate(INTERFACES):
        service_a = SERVICES[index % len(SERVICES)]
        service_b = SERVICES[(index + 2) % len(SERVICES)]
        adr_index = (index * 3 + 1) % len(ADRS)
        files[Path("docs/interfaces") / f"{name}.md"] = markdown_document(
            knowledge_metadata("Interface Contract", name, "current", base + timedelta(days=55 + index), ["interface", "contract"], "supporting", 500 + index * 10),
            f"""# {title(name)}

## Contract

The interface uses explicit versions, stable identifiers, bounded payloads, and machine-readable error semantics.

## Compatibility

- Additive fields remain optional through the supported migration window.
- Breaking changes require a new version and a linked migration decision.
- Consumers must tolerate duplicate delivery and preserve idempotency.

## Producers, consumers, and decisions

- [{title(service_a)}](../services/{service_a}.md)
- [{title(service_b)}](../services/{service_b}.md)
- [ADR {adr_index + 1:03d}: {title(ADRS[adr_index])}](../decisions/adr-{adr_index + 1:03d}-{ADRS[adr_index]}.md)
""",
        )

    for index, name in enumerate(QUALITY_ATTRIBUTES):
        architecture = ARCHITECTURE_DOCS[(index + 4) % len(ARCHITECTURE_DOCS)]
        adr_index = (index * 4 + 2) % len(ADRS)
        files[Path("docs/quality") / f"{name}.md"] = markdown_document(
            knowledge_metadata("Quality Attribute", name, "current", base + timedelta(days=65 + index), ["quality-attribute", name], "reference", 600 + index * 10),
            f"""# {title(name)} quality attribute

## Scenario

When the platform is under realistic load or partial failure, {name} remains measurable through an explicit stimulus, environment, response, and response measure.

## Measures

| Measure | Target |
| --- | --- |
| Detection | Within five minutes |
| Recovery evidence | Linked to the affected service and decision |
| Review cadence | At every material architecture change |

## Design basis

- [{title(architecture)}](../architecture/{architecture}.md)
- [ADR {adr_index + 1:03d}: {title(ADRS[adr_index])}](../decisions/adr-{adr_index + 1:03d}-{ADRS[adr_index]}.md)
""",
        )

    task_titles = (
        "Validate architecture decision coverage",
        "Prototype the event backbone",
        "Exercise tenant isolation",
        "Benchmark critical request paths",
        "Rehearse regional recovery",
        "Approve architecture readiness",
    )
    previous: str | None = None
    for index, task_title_value in enumerate(task_titles):
        slug = slugify(task_title_value)
        dependencies = [previous] if previous else []
        metadata = task_metadata(slug, task_title_value, ("done", "validation", "in-progress", "ready", "proposed", "blocked")[index], base + timedelta(days=75 + index), dependencies, "architecture", index)
        architecture = ARCHITECTURE_DOCS[(index * 2) % len(ARCHITECTURE_DOCS)]
        adr_index = (index * 3) % len(ADRS)
        body = task_body(task_title_value, dependencies, f"../../docs/architecture/{architecture}.md")
        body += f"\n## Decision evidence\n\n- [ADR {adr_index + 1:03d}: {title(ADRS[adr_index])}](../../docs/decisions/adr-{adr_index + 1:03d}-{ADRS[adr_index]}.md)\n"
        files[Path("tasks") / slug / "task.md"] = markdown_document(metadata, body)
        previous = slug

    files[Path("README.md")] = """# Architecture knowledge graph example

This generated dummy workspace stress-tests an architecture-heavy graph with detailed architecture documents, twenty ADRs, service designs, interface contracts, quality attributes, and a small linked implementation backlog.

The system context is the entry point, core architecture and ADRs are foundational, service/interface records are supporting, and quality attributes are references. These are reading-prominence hints rather than authority or dependency claims.

- [Start with the system context](./docs/architecture/system-context.md)
- [Browse the first architecture decision](./docs/decisions/adr-001-modular-service-boundaries.md)
- [Inspect architecture readiness work](./tasks/validate-architecture-decision-coverage/task.md)
"""
    return files


def combined_workspace_files() -> dict[Path, str]:
    """Combine the delivery-heavy and architecture-heavy fixtures into one linked workspace."""
    files = task_portfolio_files()
    for path, content in architecture_files().items():
        if path != Path("README.md"):
            files[path] = content

    files[Path("docs/programme-map.md")] = markdown_document(
        knowledge_metadata(
            "Knowledge Map",
            "Programme delivery and architecture map",
            "current",
            datetime(2026, 7, 18, 9, tzinfo=timezone.utc),
            ["entry-point", "delivery", "architecture"],
            "entry-point",
            1,
        ),
        """# Programme delivery and architecture map

## First reading path

1. [System context](./architecture/system-context.md)
2. [ADR 001: Modular service boundaries](./decisions/adr-001-modular-service-boundaries.md)
3. [Platform foundations delivery plan](./platform-foundations.md)
4. [Establish repository boundaries](../tasks/establish-repository-boundaries/task.md)
5. [Architecture readiness work](../tasks/validate-architecture-decision-coverage/task.md)

## Why this map exists

This record joins the architecture and delivery surfaces into one intentional graph. Its `navigation` metadata marks it as the primary entry point; the links remain the authoritative reading path and relationship evidence.
""",
    )
    files[Path("README.md")] = """# Combined delivery and architecture workspace

This generated dummy workspace combines the task-heavy portfolio and architecture-heavy knowledge base into one connected review surface. It demonstrates execution priority separately from cross-concept reading prominence.

- [Start with the programme map](./docs/programme-map.md)
- [Browse the system context](./docs/architecture/system-context.md)
- [Inspect the delivery chain](./docs/platform-foundations.md)
"""
    return files


def load_cli(script: Path) -> ModuleType:
    candidates = (
        script.with_name("okf_tasks.py"),
        script.parents[1] / "skills" / "okf-task-lifecycle" / "scripts" / "okf_tasks.py",
    )
    cli_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if cli_path is None:
        raise SystemExit("Cannot locate the feature-identical okf_tasks.py index generator.")
    spec = importlib.util.spec_from_file_location("okf_tasks_complex_examples", cli_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load {cli_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_or_check(path: Path, content: str, check: bool, errors: list[str]) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            errors.append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def generate(root: Path, check: bool) -> list[str]:
    cli = load_cli(Path(__file__).resolve())
    examples = root / "examples"
    datasets = {
        "complex-task-portfolio": task_portfolio_files(),
        "architecture-knowledge-base": architecture_files(),
        "combined-delivery-architecture": combined_workspace_files(),
    }
    errors: list[str] = []
    for name, generated in datasets.items():
        dataset_root = examples / name
        expected = {dataset_root / relative: content for relative, content in generated.items()}
        for path, content in expected.items():
            write_or_check(path, content, check, errors)
        bundle = dataset_root / "tasks"
        index_path = bundle / "index.md"
        if not check:
            index_path.parent.mkdir(parents=True, exist_ok=True)
        index_content = cli.generated_index(bundle)
        write_or_check(index_path, index_content, check, errors)
        expected[index_path] = index_content
        if dataset_root.exists():
            extras = sorted(path for path in dataset_root.rglob("*.md") if path not in expected)
            if check:
                errors.extend(str(path) for path in extras)
            else:
                for path in extras:
                    path.unlink()
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic complex OKF example workspaces.")
    parser.add_argument("--root", default=".", help="Repository root that owns the examples directory")
    parser.add_argument("--check", action="store_true", help="Fail when tracked complex examples are stale")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = generate(root, args.check)
    if errors:
        print("Complex example files are stale:")
        for path in errors:
            print(f"- {path}")
        return 1
    verb = "Checked" if args.check else "Generated"
    print(f"{verb} the complex task portfolio and architecture knowledge-base examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
