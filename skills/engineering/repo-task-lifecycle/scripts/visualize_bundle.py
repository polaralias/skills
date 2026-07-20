from __future__ import annotations

import argparse
from copy import deepcopy
from fnmatch import fnmatchcase
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


INDEX_NAME = "index.md"
DEFAULT_EXCLUSION_FILE = ".okf-visualization-ignore"
LINK_PATTERN = re.compile(r"\]\(([^)\s]+\.md)(?:#([A-Za-z0-9_:-]+))?\)")
COLORS = {
    "Task": "#2563eb",
    "Workstream": "#7c3aed",
}
DEFAULT_COLOR = "#64748b"


class FrontmatterLoader(yaml.SafeLoader):
    pass


FrontmatterLoader.yaml_implicit_resolvers = {
    key: list(value) for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for resolver_key, resolvers in list(FrontmatterLoader.yaml_implicit_resolvers.items()):
    FrontmatterLoader.yaml_implicit_resolvers[resolver_key] = [
        resolver for resolver in resolvers if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]


@dataclass
class Record:
    id: str
    path: Path
    type: str
    title: str
    description: str
    status: str
    tags: list[str]
    body: str
    source: str
    frontmatter_source: str
    frontmatter: dict[str, Any]
    links: list[tuple[str, str, str | None]] = field(default_factory=list)

    def node(self) -> dict[str, Any]:
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "description": self.description,
                "status": self.status,
                "tags": self.tags,
                "color": COLORS.get(self.type, DEFAULT_COLOR),
                "size": 34 + min(44, len(self.body) // 250),
                "frontmatter": self.frontmatter,
            }
        }


def parse_document(path: Path) -> tuple[dict[str, Any], str, str, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None
    normalized = text.replace("\r\n", "\n")
    try:
        _, frontmatter, body = normalized.split("---", 2)
        metadata = yaml.load(frontmatter, Loader=FrontmatterLoader)
    except (ValueError, yaml.YAMLError):
        return None
    if not isinstance(metadata, dict) or not metadata.get("type"):
        return None
    return metadata, body.lstrip("\n"), normalized, frontmatter.strip("\n")


def as_strings(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def task_prefix(record_id: str) -> str:
    marker = "/tasks/"
    normalized = f"/{record_id}"
    if marker in normalized:
        return normalized.split(marker, 1)[0].lstrip("/")
    return ""


def task_id(record_id: str, slug: str) -> str:
    prefix = task_prefix(record_id)
    base = f"{prefix}/tasks" if prefix else "tasks"
    if record_id.startswith("tasks/") or "/tasks/" in record_id:
        return f"{base}/{slug}/task"
    return f"{slug}/task"


def relationship_id(record_id: str, value: str) -> str:
    clean = value.split("#", 1)[0].strip().lstrip("./")
    if clean.endswith(".md"):
        return clean[:-3]
    if "/" in clean:
        return clean
    return task_id(record_id, clean)


def extract_markdown_links(body: str, source: Path, root: Path) -> list[tuple[str, str, str | None]]:
    relationships: list[tuple[str, str, str | None]] = []
    root = root.resolve()
    for match in LINK_PATTERN.finditer(body):
        target = match.group(1)
        fragment = match.group(2)
        if "://" in target or target.startswith("/"):
            continue
        try:
            resolved = (source.parent / target).resolve().relative_to(root)
        except ValueError:
            continue
        relationship = "time" if fragment and fragment.startswith("time:") else "links"
        relationships.append((resolved.with_suffix("").as_posix(), relationship, fragment))
    return relationships


def structured_links(record: Record) -> list[tuple[str, str, str | None]]:
    metadata = record.frontmatter
    relationships: list[tuple[str, str, str | None]] = []
    if record.type == "Workstream":
        task = metadata.get("task")
        if task:
            relationships.append((task_id(record.id, str(task)), "workstream", None))
    elif record.type == "Task":
        parent = metadata.get("parent")
        if parent:
            relationships.append((relationship_id(record.id, str(parent)), "parent", None))
        for dependency in as_strings(metadata.get("depends_on")):
            relationships.append((relationship_id(record.id, dependency), "depends on", None))
    return relationships


def normalise_exclusion(pattern: str) -> str:
    value = pattern.strip().replace("\\", "/")
    if not value or value.startswith("#"):
        return ""
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"Visualisation exclusion must be relative to the bundle root: {pattern}")
    while value.startswith("./"):
        value = value[2:]
    if ".." in Path(value).parts:
        raise ValueError(f"Visualisation exclusion cannot traverse outside the bundle root: {pattern}")
    directory_pattern = value.endswith("/")
    value = value.rstrip("/")
    return f"{value}/" if directory_pattern else value


def load_exclusions(
    root: Path,
    patterns: list[str] | None = None,
    exclusion_file: Path | None = None,
) -> list[str]:
    values = list(patterns or [])
    policy = exclusion_file or (root / DEFAULT_EXCLUSION_FILE)
    if exclusion_file is not None and not policy.is_file():
        raise ValueError(f"Visualisation exclusion file not found: {policy}")
    if policy.is_file():
        values.extend(policy.read_text(encoding="utf-8").splitlines())
    normalised = [normalise_exclusion(value) for value in values]
    return list(dict.fromkeys(value for value in normalised if value))


def is_excluded(path: Path, root: Path, exclusions: list[str] | None = None) -> bool:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    for pattern in exclusions or []:
        if pattern.endswith("/"):
            directory = pattern.rstrip("/")
            if "/" not in directory and any(
                fnmatchcase(part, directory) for part in relative.split("/")[:-1]
            ):
                return True
            if relative == directory or relative.startswith(f"{directory}/"):
                return True
        candidates = [pattern]
        while candidates[-1].startswith("**/"):
            candidates.append(candidates[-1][3:])
        if any(fnmatchcase(relative, candidate) for candidate in candidates):
            return True
        plain = pattern.rstrip("/")
        if relative == plain or relative.startswith(f"{plain}/"):
            return True
    return False


def excluded_markdown_paths(root: Path, exclusions: list[str] | None = None) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for path in sorted(root.rglob("*.md"))
        if is_excluded(path, root, exclusions)
    ]


def read_records(root: Path, exclusions: list[str] | None = None) -> list[Record]:
    root = root.resolve()
    records: list[Record] = []
    for path in sorted(root.rglob("*.md")):
        if is_excluded(path, root, exclusions):
            continue
        if path.name == INDEX_NAME:
            continue
        parsed = parse_document(path)
        if parsed is None:
            continue
        metadata, body, source, frontmatter_source = parsed
        record_id = path.relative_to(root).with_suffix("").as_posix()
        record = Record(
            id=record_id,
            path=path,
            type=str(metadata.get("type") or "Unknown"),
            title=str(metadata.get("title") or metadata.get("entry") or record_id),
            description=str(metadata.get("description") or ""),
            status=str(metadata.get("status") or ""),
            tags=as_strings(metadata.get("tags")),
            body=body,
            source=source,
            frontmatter_source=frontmatter_source,
            frontmatter=metadata,
        )
        record.links.extend(extract_markdown_links(body, path, root))
        record.links.extend(structured_links(record))
        records.append(record)
    return records


def read_documents(
    root: Path,
    records: list[Record],
    exclusions: list[str] | None = None,
) -> list[dict[str, Any]]:
    root = root.resolve()
    records_by_path = {record.path.resolve(): record for record in records}
    documents: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        if is_excluded(path, root, exclusions):
            continue
        source = path.read_text(encoding="utf-8")
        record = records_by_path.get(path.resolve())
        body = record.body if record else source
        heading = next(
            (line.lstrip("# ").strip() for line in body.splitlines() if line.startswith("# ")),
            path.stem,
        )
        documents.append(
            {
                "path": path.relative_to(root).as_posix(),
                "title": record.title if record else heading,
                "body": body,
                "source": source,
                "frontmatter": record.frontmatter_source if record else "",
                "record_id": record.id if record else None,
            }
        )
    return documents


def build_graph(
    records: list[Record],
    documents: list[dict[str, Any]] | None = None,
    exclusions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ids = {record.id for record in records}
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str | None]] = set()
    for record in records:
        for target, relationship, fragment in record.links:
            if (target == record.id and not fragment) or target not in ids:
                continue
            key = (record.id, target, relationship, fragment)
            if key in seen:
                continue
            seen.add(key)
            data = {
                "id": f"e{len(edges)}",
                "source": record.id,
                "target": target,
                "relationship": relationship,
            }
            if fragment:
                data["fragment"] = fragment
            edges.append({"data": data})
    structured_pairs = {
        frozenset((edge["data"]["source"], edge["data"]["target"]))
        for edge in edges
        if edge["data"]["relationship"] != "links"
    }
    edges = [
        edge
        for edge in edges
        if edge["data"]["relationship"] != "links"
        or frozenset((edge["data"]["source"], edge["data"]["target"])) not in structured_pairs
    ]
    for index, edge in enumerate(edges):
        edge["data"]["id"] = f"e{index}"
    return {
        "nodes": [record.node() for record in records],
        "edges": edges,
        "bodies": {record.id: record.body for record in records},
        "sources": {record.id: record.source for record in records},
        "frontmatters": {record.id: record.frontmatter_source for record in records},
        "documents": documents
        if documents is not None
        else [
            {
                "path": record.path.name,
                "title": record.title,
                "body": record.body,
                "source": record.source,
                "frontmatter": record.frontmatter_source,
                "record_id": record.id,
            }
            for record in records
        ],
        "types": sorted({record.type for record in records}),
        "palette": COLORS,
        "exclusions": exclusions or {"patterns": [], "paths": []},
    }


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "\\\"").replace("\n", " ")


def mermaid_class(data: dict[str, Any]) -> str:
    return {"Task": "task", "Workstream": "workstream", "Tracker Profile": "tracker"}.get(
        str(data.get("type")), "knowledge"
    )


def concept_area(record_id: str) -> str:
    parts = [part for part in record_id.split("/") if part]
    if "tasks" in parts:
        index = parts.index("tasks")
        return "/".join(parts[:index]) or "tasks"
    return parts[0] if len(parts) > 1 else "repository root"


def connected_components(graph: dict[str, Any]) -> list[list[str]]:
    node_ids = [str(node["data"]["id"]) for node in graph["nodes"] if not node["data"].get("virtual")]
    neighbours = {node_id: set() for node_id in node_ids}
    for edge in graph["edges"]:
        source, target = str(edge["data"]["source"]), str(edge["data"]["target"])
        if source in neighbours and target in neighbours:
            neighbours[source].add(target)
            neighbours[target].add(source)
    remaining, components = set(node_ids), []
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        stack, component = [start], []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in sorted(neighbours[current], reverse=True):
                if neighbour in remaining:
                    remaining.remove(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return sorted(components, key=lambda component: (-len(component), component[0]))


def mermaid_diagram(
    graph: dict[str, Any], node_ids: set[str], *, boundary_ids: set[str] | None = None
) -> list[str]:
    boundary_ids = boundary_ids or set()
    nodes = [node for node in graph["nodes"] if str(node["data"]["id"]) in node_ids]
    id_map = {str(node["data"]["id"]): f"n{index}" for index, node in enumerate(nodes)}
    lines = ["flowchart LR"]
    for node in nodes:
        data = node["data"]
        detail = f" · {data['status']}" if data.get("status") else ""
        class_name = "boundary" if str(data["id"]) in boundary_ids else mermaid_class(data)
        lines.append(f'    {id_map[str(data["id"])]}["{mermaid_label(str(data["label"]) + detail)}"]:::{class_name}')
    for edge in graph["edges"]:
        data = edge["data"]
        source, target = str(data["source"]), str(data["target"])
        if source in id_map and target in id_map:
            relationship = str(data.get("fragment") or data["relationship"])
            lines.append(f'    {id_map[source]} -->|{mermaid_label(relationship)}| {id_map[target]}')
    lines.extend([
        "    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554",
        "    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065",
        "    classDef tracker fill:#ffedd5,stroke:#ea580c,color:#431407",
        "    classDef knowledge fill:#dcfce7,stroke:#16a34a,color:#052e16",
        "    classDef boundary fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray:4 3",
    ])
    return lines


def area_overview_diagram(graph: dict[str, Any], connected_ids: set[str]) -> list[str]:
    areas: dict[str, set[str]] = {}
    for node_id in connected_ids:
        areas.setdefault(concept_area(node_id), set()).add(node_id)
    area_ids = {area: f"a{index}" for index, area in enumerate(sorted(areas))}
    relations: dict[tuple[str, str], set[str]] = {}
    for edge in graph["edges"]:
        data = edge["data"]
        source, target = str(data["source"]), str(data["target"])
        if source not in connected_ids or target not in connected_ids:
            continue
        source_area, target_area = concept_area(source), concept_area(target)
        if source_area != target_area:
            relations.setdefault((source_area, target_area), set()).add(str(data["relationship"]))
    lines = ["flowchart LR"]
    for area in sorted(areas):
        lines.append(f'    {area_ids[area]}["{mermaid_label(area)} · {len(areas[area])} concepts"]')
    for (source, target), labels in sorted(relations.items()):
        lines.append(f'    {area_ids[source]} -->|{mermaid_label(", ".join(sorted(labels)))}| {area_ids[target]}')
    lines.append("    classDef default fill:#eef2ff,stroke:#4f46e5,color:#1e1b4b")
    return lines


def generate_markdown(graph: dict[str, Any], name: str, source: str) -> str:
    nodes_by_id = {str(node["data"]["id"]): node for node in graph["nodes"] if not node["data"].get("virtual")}
    components = connected_components(graph)
    connected = [component for component in components if len(component) > 1]
    isolated = [component[0] for component in components if len(component) == 1]
    connected_ids = {node_id for component in connected for node_id in component}
    degrees = {node_id: 0 for node_id in nodes_by_id}
    neighbours = {node_id: set() for node_id in nodes_by_id}
    for edge in graph["edges"]:
        source_id, target_id = str(edge["data"]["source"]), str(edge["data"]["target"])
        if source_id in degrees and target_id in degrees:
            degrees[source_id] += 1
            degrees[target_id] += 1
            neighbours[source_id].add(target_id)
            neighbours[target_id].add(source_id)
    tick = chr(96)
    lines = [
        f"# {name}",
        "",
        "> Generated from repository-local OKF records. The Markdown/YAML bundle remains canonical.",
        "",
        f"Source: {tick}{source}{tick}",
        "",
        "The report separates the connected repository map from detailed component and key-concept views so large bundles remain reviewable.",
        "",
    ]
    if connected_ids:
        lines.extend(["## Connected-area overview", "", f"{tick * 3}mermaid", *area_overview_diagram(graph, connected_ids), tick * 3, ""])
    for component_index, component in enumerate(connected, 1):
        lines.extend([f"## Connected component {component_index}", ""])
        if len(component) <= 18:
            lines.extend([f"{tick * 3}mermaid", *mermaid_diagram(graph, set(component)), tick * 3, ""])
            continue
        component_set = set(component)
        for area in sorted({concept_area(node_id) for node_id in component}):
            area_ids = {node_id for node_id in component if concept_area(node_id) == area}
            boundary = {neighbour for node_id in area_ids for neighbour in neighbours[node_id] if neighbour in component_set - area_ids}
            lines.extend([f"### {area}", "", f"{tick * 3}mermaid", *mermaid_diagram(graph, area_ids | boundary, boundary_ids=boundary), tick * 3, ""])
    key_ids = [node_id for node_id in sorted(connected_ids, key=lambda value: (-degrees[value], value)) if degrees[node_id] >= 2][:6]
    if key_ids:
        lines.extend(["## Key concept neighbourhoods", ""])
        for node_id in key_ids:
            data = nodes_by_id[node_id]["data"]
            neighbourhood = {node_id, *neighbours[node_id]}
            lines.extend([f"### {data['label']}", "", f"{tick * 3}mermaid", *mermaid_diagram(graph, neighbourhood, boundary_ids=neighbourhood - {node_id}), tick * 3, ""])
    if isolated:
        lines.extend(["## Unconnected concepts", "", "These records are listed instead of receiving equal visual weight in the connected graph.", ""])
        for node_id in isolated:
            data = nodes_by_id[node_id]["data"]
            lines.append(f"- **{data['label']}** — `{node_id}` ({data['type']})")
        lines.append("")
    lines.extend(["## Legend", "", "- Blue: task", "- Purple: workstream", "- Orange: tracker profile", "- Green: durable knowledge", "- Dashed neutral nodes: neighbouring context repeated from another area or key-concept view", "- Time references: edges to addressable `Task.time[]` fragments", "- Arrows: structured relationships or repository-local Markdown links", ""])
    return "\n".join(lines)


VISUALIZER_TEMPLATE = Path(__file__).with_name("visualizer_template.html")
MERMAID_RUNTIME = Path(__file__).with_name("vendor") / "mermaid-11.10.1.min.js"


def render_html_workspace(
    graph: dict[str, Any],
    name: str,
    subtitle: str = "Derived visual workspace",
    default_layout: str = "grid",
) -> str:
    template = VISUALIZER_TEMPLATE.read_text(encoding="utf-8")
    if not MERMAID_RUNTIME.is_file():
        raise SystemExit(f"Bundled Mermaid runtime not found: {MERMAID_RUNTIME}")
    mermaid_runtime = MERMAID_RUNTIME.read_text(encoding="utf-8").replace("</script", "<\\/script")
    payload = deepcopy(graph)
    payload["name"] = name
    payload["subtitle"] = subtitle
    payload["default_layout"] = default_layout
    return template.replace("__MERMAID_RUNTIME__", mermaid_runtime).replace("__GRAPH__", safe_json(payload))


def generate_html(graph: dict[str, Any], name: str) -> str:
    return render_html_workspace(graph, name)


def build_relationship_view(graph: dict[str, Any]) -> dict[str, Any]:
    """Add visual-only bundle labels and stable lanes without changing canonical edges."""
    grouped = deepcopy(graph)
    groups: dict[str, list[dict[str, Any]]] = {}
    for node in grouped["nodes"]:
        record_id = str(node["data"]["id"])
        parts = record_id.split("/")
        group_key = parts[0] if len(parts) > 1 and parts[0] != "tasks" else "bundle"
        groups.setdefault(group_key, []).append(node)
    bundle_nodes: list[dict[str, Any]] = []
    type_rows = {"Task": 0, "Workstream": 1, "Tracker Profile": 2}
    for group_index, (group_key, members) in enumerate(groups.items()):
        group_id = f"__bundle__/{group_key}"
        column = group_index % 2
        row = group_index // 2
        base_x = 230 + column * 620
        base_y = 80 + row * 245
        by_type: dict[int, list[dict[str, Any]]] = {}
        for member in members:
            type_row = type_rows.get(str(member["data"].get("type")), 4)
            by_type.setdefault(type_row, []).append(member)
        for type_row, row_members in by_type.items():
            for member_index, member in enumerate(row_members):
                offset = (member_index - (len(row_members) - 1) / 2) * 250
                member["data"]["relationshipPosition"] = {
                    "x": base_x + offset,
                    "y": base_y + type_row * 75,
                }
        bundle_nodes.append(
            {
                "data": {
                    "id": group_id,
                    "label": group_key.replace("-", " ").title(),
                    "type": "Bundle",
                    "status": f"{len(members)} records",
                    "description": "Visual grouping only; relationships remain the explicit graph edges.",
                    "tags": [],
                    "frontmatter": {},
                    "color": "#64748b",
                    "virtual": True,
                    "relationshipPosition": {"x": base_x - 100, "y": base_y - 50},
                }
            }
        )
    grouped["nodes"] = bundle_nodes + grouped["nodes"]
    return grouped


def generate_relationship_html(graph: dict[str, Any], name: str) -> str:
    """Render an edge-first review page with records grouped by source bundle."""
    return render_html_workspace(
        build_relationship_view(graph),
        name,
        subtitle="Relationship map with stable source-bundle lanes",
        default_layout="relationship",
    )


def clear_windows_download_zone(path: Path) -> None:
    """Remove Mark of the Web only from a standalone HTML file we just generated."""
    if os.name != "nt" or path.suffix.lower() != ".html":
        return
    try:
        Path(f"{path}:Zone.Identifier").unlink(missing_ok=True)
    except OSError:
        pass


def write_or_check(path: Path, content: str, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != normalized:
            raise SystemExit(f"Generated visualization is stale or missing: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8")
    clear_windows_download_zone(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render OKF Tasks records as interactive HTML and GitHub Mermaid.")
    parser.add_argument("--bundle", required=True, help="Directory containing OKF Markdown records")
    parser.add_argument("--name", help="Display name (default: bundle directory name)")
    parser.add_argument("--html", help="Interactive HTML output path")
    parser.add_argument("--markdown", help="GitHub-rendered Mermaid Markdown output path")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Exclude a bundle-relative path or glob; repeat for multiple selections",
    )
    parser.add_argument(
        "--exclude-from",
        type=Path,
        help=f"Read newline-delimited exclusions (default: <bundle>/{DEFAULT_EXCLUSION_FILE} when present)",
    )
    parser.add_argument(
        "--mermaid",
        nargs="?",
        const="__AUTO__",
        help="Scalable Mermaid report; omit the path to write <html-name>.mermaid.md beside --html",
    )
    parser.add_argument("--check", action="store_true", help="Fail when requested outputs are stale")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.bundle).resolve()
    if not root.is_dir():
        raise SystemExit(f"Bundle directory not found: {root}")
    if not args.html and not args.markdown and not args.mermaid:
        raise SystemExit("Select at least one output with --html, --mermaid, or --markdown.")
    try:
        exclusions = load_exclusions(root, args.exclude, args.exclude_from)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    excluded_paths = excluded_markdown_paths(root, exclusions)
    records = read_records(root, exclusions)
    if not records:
        raise SystemExit(f"No OKF records found under: {root}")
    graph = build_graph(
        records,
        read_documents(root, records, exclusions),
        {"patterns": exclusions, "paths": excluded_paths},
    )
    name = args.name or root.name
    if args.html:
        write_or_check(Path(args.html), generate_html(graph, name), args.check)
    if args.markdown:
        write_or_check(Path(args.markdown), generate_markdown(graph, name, args.bundle), args.check)
    if args.mermaid:
        if args.mermaid == "__AUTO__":
            mermaid_path = Path(args.html).with_suffix(".mermaid.md") if args.html else Path(f"{root.name}.mermaid.md")
        else:
            mermaid_path = Path(args.mermaid)
        write_or_check(mermaid_path, generate_markdown(graph, name, args.bundle), args.check)
    print(
        f"Visualized {len(graph['nodes'])} records and {len(graph['edges'])} relationships; "
        f"excluded {len(excluded_paths)} Markdown files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
