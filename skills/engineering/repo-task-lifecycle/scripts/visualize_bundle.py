from __future__ import annotations

import argparse
from copy import deepcopy
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


INDEX_NAME = "index.md"
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


def read_records(root: Path) -> list[Record]:
    root = root.resolve()
    records: list[Record] = []
    for path in sorted(root.rglob("*.md")):
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


def read_documents(root: Path, records: list[Record]) -> list[dict[str, Any]]:
    root = root.resolve()
    records_by_path = {record.path.resolve(): record for record in records}
    documents: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
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


def build_graph(records: list[Record], documents: list[dict[str, Any]] | None = None) -> dict[str, Any]:
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
    }


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "\\\"").replace("\n", " ")


def generate_markdown(graph: dict[str, Any], name: str, source: str) -> str:
    nodes = graph["nodes"]
    id_map = {node["data"]["id"]: f"n{index}" for index, node in enumerate(nodes)}
    tick = chr(96)
    lines = [
        f"# {name}",
        "",
        "> Generated from repository-local OKF records. The Markdown/YAML bundle remains canonical.",
        "",
        f"Source: {tick}{source}{tick}",
        "",
        f"{tick * 3}mermaid",
        "flowchart LR",
    ]
    for node in nodes:
        data = node["data"]
        detail = f" · {data['status']}" if data.get("status") else ""
        class_name = data["type"].lower().replace(" ", "_")
        if class_name not in {"task", "workstream"}:
            class_name = "unknown"
        lines.append(f'    {id_map[data["id"]]}["{mermaid_label(data["label"] + detail)}"]:::{class_name}')
    for edge in graph["edges"]:
        data = edge["data"]
        relationship_label = str(data.get("fragment") or data["relationship"])
        lines.append(
            f'    {id_map[data["source"]]} -->|{mermaid_label(relationship_label)}| {id_map[data["target"]]}'
        )
    lines.extend(
        [
            "    classDef task fill:#dbeafe,stroke:#2563eb,color:#172554",
            "    classDef workstream fill:#ede9fe,stroke:#7c3aed,color:#2e1065",
            "    classDef unknown fill:#e2e8f0,stroke:#64748b,color:#0f172a",
            tick * 3,
            "",
            "## Legend",
            "",
            "- Blue: task",
            "- Purple: workstream",
            "- Time references: edges to addressable `Task.time[]` fragments",
            "- Arrows: structured relationships or repository-local Markdown links",
            "",
        ]
    )
    return "\n".join(lines)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Interactive graph of an OKF Tasks bundle">
<title>OKF Tasks Viewer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.31.2/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@16.1.2/lib/marked.umd.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.10.1/dist/mermaid.min.js"></script>
<style>
:root{color-scheme:dark;--ink:#eef6ff;--muted:#8fa6c7;--faint:#526887;--base:#050b18;--surface:#081426;--surface-2:#0b1b32;--line:rgba(139,181,235,.14);--line-strong:rgba(114,197,255,.3);--cyan:#22c7f4;--blue:#2d75ff;--red:#f04452;--radius-xl:24px;--radius-lg:18px;--ease:cubic-bezier(.32,.72,0,1)}
*{box-sizing:border-box}html,body{height:100%}html{background:var(--base);scroll-behavior:smooth}body{margin:0;overflow:hidden;background:radial-gradient(circle at 12% 0%,rgba(26,77,161,.18),transparent 34%),var(--base);color:var(--ink);font:14px/1.55 Manrope,Segoe UI,sans-serif}
body:after{content:"";position:fixed;inset:0;pointer-events:none;z-index:4;opacity:.18;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.12'/%3E%3C/svg%3E")}
button,input,select{font:inherit}.skip-link{position:fixed;top:10px;left:10px;z-index:20;transform:translateY(-160%);padding:8px 12px;border-radius:8px;background:white;color:#071126}.skip-link:focus{transform:none}
.app-header{position:relative;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:24px;height:82px;padding:0 24px;border-bottom:1px solid var(--line);background:rgba(5,11,24,.94)}
.identity{display:flex;align-items:center;gap:13px;min-width:0}.mark{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:linear-gradient(145deg,#0f294e,#071226);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 10px 30px rgba(0,95,190,.17);color:var(--cyan);font:500 16px JetBrains Mono,monospace}.mark:after{content:"";position:absolute;width:5px;height:5px;margin:25px 0 0 27px;border-radius:50%;background:var(--red);box-shadow:0 0 12px var(--red)}
.identity-copy{min-width:0}.identity h1{margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:16px;font-weight:700;letter-spacing:-.02em}.identity p{margin:1px 0 0;color:var(--muted);font-size:11px}.stats{display:flex;align-items:center;gap:8px}.stat{min-width:82px;padding:8px 11px;border-radius:12px;background:rgba(16,35,63,.62);box-shadow:inset 0 0 0 1px var(--line)}.stat strong{display:block;font:500 15px JetBrains Mono,monospace;font-variant-numeric:tabular-nums}.stat span{display:block;color:var(--muted);font-size:9px;letter-spacing:.12em;text-transform:uppercase}
.workspace{position:relative;z-index:2;display:grid;grid-template-columns:minmax(0,1fr) minmax(340px,410px);gap:10px;height:calc(100% - 82px);padding:10px}.graph-shell,.detail-shell{min-height:0;padding:5px;border-radius:var(--radius-xl);background:rgba(109,161,224,.06);box-shadow:inset 0 0 0 1px rgba(153,197,255,.08)}
.graph-core,.detail-core{position:relative;height:100%;overflow:hidden;border-radius:calc(var(--radius-xl) - 5px);background:var(--surface);box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 22px 60px rgba(0,5,15,.28)}
.graph-core:before{content:"";position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(rgba(79,130,190,.24) .7px,transparent .7px),radial-gradient(circle at 50% 34%,rgba(28,86,170,.2),transparent 42%);background-size:22px 22px,100% 100%}.graph-toolbar{position:absolute;z-index:3;top:16px;left:16px;right:16px;display:flex;align-items:center;justify-content:space-between;gap:10px;pointer-events:none}.tool-group{display:flex;align-items:center;gap:7px;padding:5px;border-radius:14px;background:rgba(7,18,35,.9);box-shadow:inset 0 0 0 1px var(--line),0 14px 34px rgba(0,6,18,.3);pointer-events:auto}
.search-wrap{position:relative}.search-wrap svg{position:absolute;top:50%;left:12px;width:15px;transform:translateY(-50%);color:var(--muted)}#search{width:min(29vw,320px);height:38px;padding:0 36px;border:0;border-radius:10px;outline:0;background:#0c1c33;color:var(--ink);transition:box-shadow .45s var(--ease),background .45s var(--ease)}#search::placeholder{color:#6f85a5}#search:focus{background:#102441;box-shadow:0 0 0 2px rgba(34,199,244,.42)}.clear-search{position:absolute;top:50%;right:8px;width:25px;height:25px;transform:translateY(-50%);border:0;border-radius:7px;background:transparent;color:var(--muted);cursor:pointer}.clear-search:hover{background:rgba(255,255,255,.06);color:var(--ink)}
select,.icon-button{height:38px;border:0;border-radius:10px;background:#0c1c33;color:var(--ink);cursor:pointer;outline:0;transition:transform .45s var(--ease),background .45s var(--ease),box-shadow .45s var(--ease)}select{padding:0 31px 0 11px}.icon-button{display:grid;place-items:center;width:38px}.icon-button svg{width:16px}.icon-button:hover,select:hover{background:#132845}.icon-button:active{transform:scale(.95)}select:focus-visible,.icon-button:focus-visible{box-shadow:0 0 0 2px rgba(34,199,244,.45)}
.filter-rail{position:absolute;z-index:3;top:79px;left:21px;display:flex;gap:6px}.filter-chip{padding:6px 10px;border:0;border-radius:9px;background:rgba(7,18,35,.82);box-shadow:inset 0 0 0 1px var(--line);color:var(--muted);font-size:11px;cursor:pointer;transition:color .45s var(--ease),background .45s var(--ease),transform .45s var(--ease)}.filter-chip:hover{color:var(--ink);transform:translateY(-1px)}.filter-chip[aria-pressed="true"]{background:#123153;box-shadow:inset 0 0 0 1px rgba(34,199,244,.45);color:#dff8ff}
#graph{position:absolute;inset:0}.graph-shell:fullscreen{padding:0;background:var(--surface)}.graph-shell:fullscreen .graph-core{border-radius:0}.document-browser{position:absolute;z-index:5;inset:58px auto 14px 14px;width:min(390px,calc(100% - 28px));overflow:auto;border:1px solid var(--line-strong);border-radius:7px;background:color-mix(in srgb,var(--surface) 96%,transparent);box-shadow:0 18px 50px rgba(0,0,0,.28)}.document-browser-head{position:sticky;top:0;z-index:1;display:flex;align-items:center;justify-content:space-between;padding:12px 13px;border-bottom:1px solid var(--line);background:var(--surface)}.document-browser-head strong{font-size:11px}.document-tree{padding:9px}.document-tree details{margin-left:10px}.document-tree summary{padding:5px;color:var(--muted);font:500 10px JetBrains Mono,monospace;cursor:pointer}.document-tree button{display:block;width:100%;padding:6px 8px;border:0;border-radius:4px;background:transparent;color:var(--ink);font:400 10px JetBrains Mono,monospace;text-align:left;cursor:pointer}.document-tree button:hover{background:var(--surface-2);color:var(--cyan)}.graph-foot{position:absolute;z-index:3;right:17px;bottom:16px;display:flex;align-items:center;gap:11px;padding:8px 11px;border-radius:10px;background:rgba(7,18,35,.8);box-shadow:inset 0 0 0 1px var(--line);color:var(--muted);font-size:10px;pointer-events:none}.legend-item{display:flex;align-items:center;gap:5px}.legend-dot{width:7px;height:7px;border-radius:2px}.results{position:absolute;z-index:3;left:20px;bottom:16px;color:var(--muted);font:500 10px JetBrains Mono,monospace;letter-spacing:.02em}
.detail-core{overflow:auto;scrollbar-color:#294568 transparent;scrollbar-width:thin}.detail-inner{padding:27px 25px 48px}.eyebrow{display:flex;align-items:center;gap:8px;margin-bottom:14px;color:var(--muted);font-size:9px;font-weight:700;letter-spacing:.17em;text-transform:uppercase}.eyebrow:before{content:"";width:17px;height:1px;background:var(--cyan)}.empty-state{display:grid;place-items:center;height:100%;padding:36px;text-align:center}.empty-orbit{display:grid;place-items:center;width:70px;height:70px;margin:0 auto 17px;border-radius:22px;background:#0e213c;box-shadow:inset 0 0 0 1px var(--line),0 16px 40px rgba(0,0,0,.22);color:var(--cyan)}.empty-orbit svg{width:27px}.empty-state h2{margin:0 0 5px;font-size:17px}.empty-state p{max-width:29ch;margin:0;color:var(--muted);font-size:12px}
.record-head{padding-bottom:22px;border-bottom:1px solid var(--line)}.record-kicker{display:flex;align-items:center;justify-content:space-between;gap:12px}.type-chip{display:inline-flex;align-items:center;gap:7px;padding:5px 9px;border-radius:8px;background:#122540;color:#dbeeff;font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.type-chip:before{content:"";width:6px;height:6px;border-radius:2px;background:var(--chip-color);box-shadow:0 0 10px var(--chip-color)}.status-chip{padding:5px 8px;border-radius:7px;background:rgba(255,255,255,.045);color:var(--muted);font:500 9px JetBrains Mono,monospace}.record-head h2{margin:14px 0 4px;font-size:25px;line-height:1.15;letter-spacing:-.045em;text-wrap:balance}.record-id{overflow-wrap:anywhere;color:var(--faint);font:400 10px JetBrains Mono,monospace}.description{max-width:60ch;margin:15px 0 0;color:#b6c8e1;font-size:12px;line-height:1.65;text-wrap:pretty}
.meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:16px 0 0}.meta-block{min-height:57px;padding:10px 11px;border-radius:11px;background:#0a192e;box-shadow:inset 0 0 0 1px rgba(139,181,235,.09)}.meta-block span{display:block;margin-bottom:4px;color:var(--faint);font-size:8px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.meta-block strong{font-size:11px;font-weight:600}.tag-list{display:flex;flex-wrap:wrap;gap:5px}.tag{display:inline-block;padding:3px 6px;border-radius:5px;background:#142b49;color:#a9c8e9;font:500 9px JetBrains Mono,monospace}
.record-section{padding-top:23px}.section-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:11px}.section-heading h3{margin:0;font-size:11px;font-weight:700;letter-spacing:.01em}.section-heading span{color:var(--faint);font:400 9px JetBrains Mono,monospace}.code-block{margin:0;overflow:auto;padding:14px;border-radius:12px;background:#050e1c;box-shadow:inset 0 0 0 1px rgba(122,171,230,.11);color:#a8c6e9;font:400 10px/1.65 JetBrains Mono,monospace}.raw-disclosure{margin-top:12px;border:1px solid var(--line);border-radius:5px}.raw-disclosure summary{padding:10px 12px;color:var(--muted);font:500 10px JetBrains Mono,monospace;cursor:pointer}.raw-disclosure[open] summary{border-bottom:1px solid var(--line);color:var(--ink)}.raw-disclosure .code-block{max-height:420px;border:0;border-radius:0}.markdown{color:#b8cae2;font-size:12px;line-height:1.72}.markdown h1,.markdown h2,.markdown h3{margin:1.45em 0 .55em;color:var(--ink);font-weight:650;letter-spacing:-.02em}.markdown h1{font-size:18px}.markdown h2{font-size:15px}.markdown h3{font-size:13px}.markdown p:first-child{margin-top:0}.markdown a,.backlink{color:#5ed7f8;text-decoration-color:rgba(94,215,248,.36);text-underline-offset:3px}.markdown code{padding:2px 4px;border-radius:4px;background:#102440;color:#d4edff;font:400 .92em JetBrains Mono,monospace}.markdown pre{overflow:auto;padding:12px;border:1px solid var(--line);border-radius:5px;background:#080d13}.markdown pre code{padding:0;background:transparent}.markdown table{display:block;width:max-content;max-width:100%;overflow:auto;border-spacing:0;border-collapse:collapse}.markdown th,.markdown td{padding:7px 9px;border:1px solid var(--line);text-align:left}.markdown tr:nth-child(2n){background:color-mix(in srgb,var(--surface-2) 75%,transparent)}.markdown blockquote{margin:15px 0;padding-left:14px;border-left:2px solid var(--cyan);color:var(--muted)}.markdown details{margin:12px 0;border:1px solid var(--line);border-radius:5px;padding:9px 11px}.markdown details summary{font-weight:600;cursor:pointer}.markdown .task-list-item{list-style:none}.markdown .task-list-item input{margin:0 7px 0 -20px}.markdown .mermaid{margin:14px 0;overflow:auto;padding:12px;border:1px solid var(--line);border-radius:5px;background:var(--surface-2);text-align:center}.backlink-list{display:grid;gap:6px;margin:0;padding:0;list-style:none}.backlink{display:flex;align-items:center;justify-content:space-between;padding:9px 10px;border-radius:9px;background:#0b1d34;text-decoration:none;transition:transform .45s var(--ease),background .45s var(--ease)}.backlink:hover{transform:translateX(2px);background:#102946;color:#9ddbed}.backlink span{color:var(--faint)}
[hidden]{display:none!important}@media(max-width:980px){body{overflow:auto}.app-header{height:auto;min-height:76px;padding:13px 16px}.stats .stat:nth-child(3){display:none}.workspace{grid-template-columns:1fr;height:auto;min-height:calc(100dvh - 76px);padding:8px}.graph-shell{height:62dvh;min-height:470px}.detail-shell{height:auto;min-height:500px}.detail-core{overflow:visible}.graph-toolbar{align-items:flex-start}.tool-group:last-child{flex-direction:column}.filter-rail{top:76px}.graph-foot{display:none}#search{width:min(52vw,320px)}}@media(max-width:620px){.identity p,.stats{display:none}.app-header{height:68px}.workspace{min-height:calc(100dvh - 68px)}.graph-shell{height:67dvh;min-height:430px}.graph-toolbar{top:11px;left:11px;right:11px}.tool-group{gap:4px;padding:4px}.tool-group:last-child{position:absolute;right:0;top:49px;flex-direction:row}#search{width:calc(100vw - 58px)}.filter-rail{top:111px;left:15px;right:15px;overflow:auto;padding-bottom:4px}.results{left:15px}.detail-inner{padding:22px 18px 40px}.meta-grid{grid-template-columns:1fr}.record-head h2{font-size:22px}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;transition-duration:.01ms!important}}
/* Restrained technical-review theme. This intentionally overrides the decorative first-pass shell. */
:root{--ink:#e8edf5;--muted:#8d99aa;--faint:#586273;--base:#080b10;--surface:#0c1119;--surface-2:#101720;--line:#202936;--line-strong:#334154;--cyan:#39b8dd;--red:#e0525e}
:root[data-theme="light"]{color-scheme:light;--ink:#172033;--muted:#59677a;--faint:#7b8798;--base:#eef2f6;--surface:#f8fafc;--surface-2:#ffffff;--line:#d7dee8;--line-strong:#aeb9c8;--cyan:#087c9b;--red:#c33d49}
body{overflow:hidden;background:var(--base);font-size:13px}body:after,.graph-core:before{display:none}
.app-header{height:64px;min-height:0;padding:0 20px;border-bottom:1px solid var(--line);background:#0a0e14}
.identity{gap:11px}.mark{position:relative;width:32px;height:32px;border:1px solid #314155;border-radius:6px;background:#101925;box-shadow:none;font-size:12px}.mark:after{right:5px;bottom:5px;width:3px;height:3px;margin:0;box-shadow:none}
.identity h1{font-size:14px;font-weight:650}.identity p{margin:0;font-size:10px}.stats{gap:0}.stat{display:flex;align-items:baseline;gap:5px;min-width:0;padding:0 12px;border-left:1px solid var(--line);border-radius:0;background:transparent;box-shadow:none}.stat strong{display:inline;font-size:12px}.stat span{display:inline;font-size:9px;letter-spacing:.08em}
.view-tabs{align-self:stretch;display:flex;align-items:stretch;gap:2px}.view-tab{position:relative;padding:0 15px;border:0;background:transparent;color:var(--muted);font-size:11px;font-weight:600;cursor:pointer}.view-tab:hover{color:var(--ink)}.view-tab[aria-selected="true"]{color:var(--ink)}.view-tab[aria-selected="true"]:after{position:absolute;right:12px;bottom:0;left:12px;height:2px;background:var(--cyan);content:""}.view-tab:focus-visible{outline:2px solid var(--cyan);outline-offset:-3px}
.workspace{grid-template-columns:minmax(0,1fr) 380px;gap:0;height:calc(100% - 64px);min-height:0;padding:0}.graph-shell,.detail-shell{height:auto;min-height:0;padding:0;border-radius:0;background:transparent;box-shadow:none}.detail-shell{border-left:1px solid var(--line)}.graph-core,.detail-core{border-radius:0;background:var(--surface);box-shadow:none}.detail-core{overflow:auto}
.documents-view{position:relative;z-index:2;display:grid;grid-template-columns:minmax(0,1fr) 280px;height:calc(100% - 64px);min-height:0;background:var(--surface)}.reader-main{min-width:0;overflow:auto}.reader-header{position:sticky;top:0;z-index:2;padding:18px clamp(22px,4vw,64px) 14px;border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--surface) 96%,transparent);backdrop-filter:blur(12px)}.reader-header h2{margin:0 0 3px;font-size:18px;letter-spacing:-.025em}.reader-path{color:var(--faint);font:400 9px JetBrains Mono,monospace}.reader-body{max-width:920px;margin:0 auto;padding:38px clamp(22px,5vw,76px) 80px;font-size:13px}.reader-tree-panel{min-width:0;overflow:auto;border-left:1px solid var(--line);background:var(--surface-2)}.reader-tree-head{position:sticky;top:0;z-index:1;padding:16px 14px 12px;border-bottom:1px solid var(--line);background:var(--surface-2)}.reader-tree-head strong{display:block;font-size:11px}.reader-tree-head span{display:block;margin-top:2px;color:var(--faint);font-size:9px}.reader-tree-panel .document-tree{padding:10px 8px 30px}.document-tree button[aria-current="page"]{background:color-mix(in srgb,var(--cyan) 12%,transparent);color:var(--cyan)}
.graph-toolbar{top:14px;left:14px;right:14px}.tool-group{gap:6px;padding:0;border-radius:0;background:transparent;box-shadow:none}.tool-group:last-child{flex-direction:row}
#search{width:min(28vw,300px);height:36px;border:1px solid var(--line);border-radius:6px;background:#0b121c;box-shadow:none}#search:focus{border-color:#4c8296;background:#0e1722;box-shadow:none}.search-wrap svg{left:11px;width:14px}.clear-search{border-radius:4px}
select,.icon-button{height:36px;border:1px solid var(--line);border-radius:6px;background:#0b121c;box-shadow:none}.icon-button{width:36px}.icon-button:hover,select:hover{border-color:var(--line-strong);background:#111a25}.icon-button:focus-visible,select:focus-visible{border-color:var(--cyan);box-shadow:none}
.icon-button[data-tooltip]{position:relative}.icon-button[data-tooltip]:after{position:absolute;z-index:20;right:0;top:calc(100% + 8px);width:max-content;max-width:220px;padding:6px 8px;border:1px solid var(--line-strong);border-radius:5px;background:var(--ink);color:var(--surface);content:attr(data-tooltip);font:500 10px/1.3 Manrope,Segoe UI,sans-serif;opacity:0;pointer-events:none;transform:translateY(-3px);transition:opacity .14s ease,transform .14s ease}.icon-button[data-tooltip]:hover:after,.icon-button[data-tooltip]:focus-visible:after{opacity:1;transform:none}
.filter-rail{top:61px;left:14px;gap:3px;padding:3px;border:1px solid var(--line);border-radius:6px;background:#0b121c}.filter-chip{padding:5px 8px;border-radius:3px;background:transparent;box-shadow:none;font-size:10px}.filter-chip:hover{transform:none}.filter-chip[aria-pressed="true"]{background:#1a2734;box-shadow:none;color:#e6f7fb}
.graph-foot{right:15px;bottom:13px;gap:12px;padding:0;border-radius:0;background:transparent;box-shadow:none;font-size:9px}.legend-dot{width:6px;height:6px;border-radius:1px}.results{left:15px;bottom:13px;font-size:9px}
.detail-inner{padding:24px 22px 44px}.eyebrow{margin-bottom:16px;font-size:9px}.eyebrow:before{display:none}.empty-orbit{width:54px;height:54px;border:1px solid var(--line);border-radius:8px;background:#101720;box-shadow:none}.empty-orbit svg{width:23px}.empty-state h2{font-size:15px}.empty-state p{font-size:11px}
.record-head{padding-bottom:20px}.type-chip{padding:0;border-radius:0;background:transparent;font-size:9px}.type-chip:before{width:5px;height:5px;border-radius:1px;box-shadow:none}.status-chip{padding:0;border-radius:0;background:transparent}.record-head h2{margin-top:13px;font-size:22px}.record-id{font-size:9px}.description{margin-top:13px;font-size:11px}
.meta-grid{gap:14px;margin-top:17px}.meta-block{min-height:46px;padding:0 0 0 10px;border-left:1px solid var(--line-strong);border-radius:0;background:transparent;box-shadow:none}.meta-block span{font-size:8px}.meta-block strong{font-size:10px}.tag-list{gap:4px}.tag{padding:0;border-radius:0;background:transparent;color:#9cb5c9;font-size:8px}.tag:not(:last-child):after{content:","}
.record-section{padding-top:22px}.section-heading{margin-bottom:9px}.section-heading h3{font-size:10px}.section-heading span{font-size:8px}.code-block{padding:12px;border:1px solid var(--line);border-radius:5px;background:#080d13;box-shadow:none;font-size:9px}.markdown{font-size:11px}.markdown h1{font-size:16px}.markdown h2{font-size:14px}.markdown h3{font-size:12px}.backlink-list{gap:1px}.backlink{padding:8px 0;border-bottom:1px solid var(--line);border-radius:0;background:transparent}.backlink:hover{transform:none;background:transparent;color:#9ddbed}
@media(max-width:760px){body{overflow:auto}.app-header{height:60px;padding:0 13px}.identity p,.stats{display:none}.view-tab{padding:0 10px}.workspace{grid-template-columns:1fr;height:auto;min-height:calc(100dvh - 60px);padding:0}.graph-shell{height:62dvh;min-height:440px}.detail-shell{min-height:500px;border-top:1px solid var(--line);border-left:0}.detail-core{overflow:visible}.graph-toolbar{top:10px;left:10px;right:10px}.tool-group:last-child{position:absolute;top:44px;right:0;flex-direction:row}.filter-rail{top:98px;left:10px;right:10px}.graph-foot{display:none}#search{width:calc(100vw - 20px)}.results{left:11px}.detail-inner{padding:22px 17px 40px}.meta-grid{grid-template-columns:1fr}.documents-view{grid-template-columns:1fr;height:auto;min-height:calc(100dvh - 60px)}.reader-tree-panel{grid-row:1;border-bottom:1px solid var(--line);border-left:0;max-height:260px}.reader-main{grid-row:2;overflow:visible}.reader-header{padding:14px 17px}.reader-body{padding:26px 17px 60px}}
:root[data-theme="light"] .app-header{background:#fff}:root[data-theme="light"] .mark{background:#e8eef5;color:#086f8b}:root[data-theme="light"] #search,:root[data-theme="light"] select,:root[data-theme="light"] .icon-button,:root[data-theme="light"] .filter-rail{background:#fff}:root[data-theme="light"] #search:focus,:root[data-theme="light"] .icon-button:hover,:root[data-theme="light"] select:hover{background:#f3f6f9}:root[data-theme="light"] .filter-chip[aria-pressed="true"]{background:#dce8f0;color:#183244}:root[data-theme="light"] .code-block{background:#f1f4f8;color:#334155}:root[data-theme="light"] .markdown{color:#334155}:root[data-theme="light"] .markdown code{background:#e8eef5;color:#183244}:root[data-theme="light"] .description{color:#455468}:root[data-theme="light"] .tag{color:#376079}:root[data-theme="light"] .type-chip{color:#314155}
.temporal-rail{position:absolute;z-index:3;top:100px;left:14px;right:14px;display:flex;align-items:center;gap:8px;max-width:720px;padding:7px 9px;border:1px solid var(--line);border-radius:6px;background:color-mix(in srgb,var(--surface) 96%,transparent);box-shadow:0 8px 24px rgba(0,0,0,.12)}.temporal-rail select{height:30px;min-width:150px}.temporal-rail input[type="range"]{min-width:120px;flex:1;accent-color:var(--cyan)}.temporal-label,.temporal-output,.drift-count{white-space:nowrap;color:var(--muted);font:500 9px JetBrains Mono,monospace}.temporal-output{min-width:112px;color:var(--ink)}.drift-button{height:30px;padding:0 10px;border:1px solid var(--line);border-radius:4px;background:var(--surface-2);color:var(--muted);font-size:10px;cursor:pointer}.drift-button[aria-pressed="true"]{border-color:#d97706;background:color-mix(in srgb,#d97706 13%,var(--surface));color:#f59e0b}.drift-count{min-width:96px}.temporal-note{position:absolute;z-index:3;top:145px;left:18px;color:var(--faint);font-size:9px}.graph-core:has(.temporal-rail) .filter-rail{top:61px} @media(max-width:760px){.temporal-rail{top:136px;overflow:auto}.temporal-note{top:181px}.filter-rail{top:98px!important}}
</style>
</head>
<body>
<a class="skip-link" href="#detail">Skip to record details</a>
<header class="app-header"><div class="identity"><div class="mark" aria-hidden="true">{ }</div><div class="identity-copy"><h1 id="name"></h1><p>OKF Tasks · derived bundle view</p></div></div><nav class="view-tabs" role="tablist" aria-label="Viewer mode"><button class="view-tab" id="graph-tab" type="button" role="tab" aria-selected="true" aria-controls="graph-view">Graph</button><button class="view-tab" id="documents-tab" type="button" role="tab" aria-selected="false" aria-controls="documents-view" tabindex="-1">Documents</button></nav><div class="stats" aria-label="Bundle summary"><div class="stat"><strong id="record-count">0</strong><span>Records</span></div><div class="stat"><strong id="relation-count">0</strong><span>Relations</span></div><div class="stat"><strong id="type-count">0</strong><span>Types</span></div></div></header>
<main class="workspace" id="graph-view" role="tabpanel" aria-labelledby="graph-tab"><section class="graph-shell" aria-label="Task relationship graph"><div class="graph-core"><div class="graph-toolbar"><div class="tool-group"><label class="search-wrap" aria-label="Search records"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg><input id="search" type="search" placeholder="Search records…" autocomplete="off"><button class="clear-search" id="clear-search" type="button" aria-label="Clear search" hidden>×</button></label></div><div class="tool-group"><label><span class="skip-link">Graph layout</span><select id="layout" aria-label="Graph layout"><option value="cose">Force layout</option><option value="breadthfirst">Hierarchy</option><option value="concentric">Concentric</option><option value="circle">Circle</option><option value="grid">Grid</option></select></label><button class="icon-button" id="browse-documents" type="button" aria-label="Browse documents in graph view"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 6.5h7l2 2h9v10.5H3z"/><path d="M3 9h18"/></svg></button><button class="icon-button" id="theme" type="button" aria-label="Use dark theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2m-3-7-1.5 1.5M6.5 17.5 5 19m14 0-1.5-1.5M6.5 6.5 5 5"/></svg></button><button class="icon-button" id="fit" type="button" aria-label="Fit all visible records into the graph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg></button><button class="icon-button" id="fullscreen" type="button" aria-label="Enter graph fullscreen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3H3v5M16 3h5v5M8 21H3v-5m13 5h5v-5"/></svg></button><button class="icon-button" id="reset" type="button" aria-label="Clear graph search and filters"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 4v6h6M20 20v-6h-6"/><path d="M5.5 15a7.5 7.5 0 0 0 12.2 2.4L20 14M4 10l2.3-3.4A7.5 7.5 0 0 1 18.5 9"/></svg></button></div></div><div class="filter-rail" id="type-filters" aria-label="Filter by record type"></div><aside class="document-browser" id="document-browser" aria-label="Document tree" hidden><div class="document-browser-head"><strong>Markdown documents</strong><button class="icon-button" id="close-documents" type="button" aria-label="Close document browser">×</button></div><nav class="document-tree" id="document-tree"></nav></aside><div id="graph"></div><div class="results" id="results" aria-live="polite"></div><div class="graph-foot" aria-label="Graph legend"><span class="legend-item"><i class="legend-dot" style="background:#2563eb"></i>Task</span><span class="legend-item"><i class="legend-dot" style="background:#7c3aed"></i>Workstream</span><span class="legend-item"><i class="legend-dot" style="background:#059669"></i>Time</span></div></div></section>
<aside class="detail-shell" id="detail"><div class="detail-core"><div class="empty-state" id="empty"><div><div class="empty-orbit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="8" r="2.5"/><circle cx="12" cy="17" r="2.5"/><path d="m9.2 8.2 5.3-.1m-6 1 2.5 5.6m4.3-4.5-2.1 4.5"/></svg></div><h2>Explore the bundle</h2><p>Select a node or browse the document tree to inspect its rendered Markdown and source.</p></div></div><article class="detail-inner" id="content" hidden><div class="eyebrow" id="inspector-label">Record inspector</div><header class="record-head"><div class="record-kicker"><span id="record-type" class="type-chip"></span><span id="record-status" class="status-chip"></span></div><h2 id="record-title"></h2><div id="record-id" class="record-id"></div><p id="record-description" class="description"></p><div class="meta-grid"><div class="meta-block"><span>Tags</span><div id="record-tags" class="tag-list"></div></div><div class="meta-block"><span>Connections</span><strong id="record-connections">0 relationships</strong></div><div class="meta-block"><span>Last meaningful change</span><time id="record-last-updated">Not recorded</time></div><div class="meta-block"><span>Created</span><time id="record-created">Not recorded</time></div><div class="meta-block"><span>Started</span><time id="record-started">Not recorded</time></div><div class="meta-block"><span>Finished</span><time id="record-finished">Not recorded</time></div></div></header><section class="record-section"><div class="section-heading"><h3>Markdown body</h3><span>GitHub-style sanitized preview</span></div><div id="record-body" class="markdown"></div></section><section class="record-section" id="backlinks" hidden><div class="section-heading"><h3>Linked from</h3><span id="backlink-count"></span></div><ul id="backlinks-list" class="backlink-list"></ul></section><section class="record-section"><div class="section-heading"><h3>Raw source</h3><span>optional inspection</span></div><details class="raw-disclosure" id="raw-frontmatter-section"><summary>Raw frontmatter</summary><pre id="raw-frontmatter" class="code-block"></pre></details><details class="raw-disclosure"><summary>Complete source document</summary><pre id="raw-document" class="code-block"></pre></details></section></article></div></aside></main>
<section class="documents-view" id="documents-view" role="tabpanel" aria-labelledby="documents-tab" hidden><article class="reader-main" id="reader-main"><header class="reader-header"><h2 id="reader-title">Choose a document</h2><div class="reader-path" id="reader-path">Select a Markdown file from the tree</div></header><div class="markdown reader-body" id="document-reader"></div></article><aside class="reader-tree-panel" aria-label="Markdown file tree"><div class="reader-tree-head"><strong>Repository documents</strong><span>Markdown files in this bundle</span></div><nav class="document-tree" id="reader-tree"></nav></aside></section>
<script>window.OKF_NAME=__NAME__;window.OKF_GRAPH=__GRAPH__;</script>
<script>
(()=>{const graph=window.OKF_GRAPH,index={},incoming={},outgoing={},documentsByPath=Object.fromEntries((graph.documents||[]).map(document=>[document.path,document]));let activeType="",readerPath="",savedTheme;const $=id=>document.getElementById(id);try{savedTheme=localStorage.getItem("okf-theme")}catch{}document.documentElement.dataset.theme=savedTheme||"light";$("name").textContent=window.OKF_NAME;$("record-count").textContent=graph.nodes.length;$("relation-count").textContent=graph.edges.length;$("type-count").textContent=graph.types.length;for(const n of graph.nodes)index[n.data.id]=n.data;for(const e of graph.edges){(incoming[e.data.target]??=[]).push(e.data.source);(outgoing[e.data.source]??=[]).push(e.data.target)}
let temporalField="timestamp",temporalCutoff=Infinity,temporalAtLatest=true,driftReview=false;
function labelButton(button){const label=button.getAttribute("aria-label")||button.textContent.trim();if(label){button.dataset.tooltip=label;button.title=label}}function labelButtons(){for(const button of document.querySelectorAll("button"))labelButton(button)}
const filters=$("type-filters");for(const value of ["",...graph.types]){const button=document.createElement("button");button.type="button";button.className="filter-chip";button.dataset.type=value;button.textContent=value||"All records";button.setAttribute("aria-pressed",String(value===""));button.onclick=()=>{activeType=value;for(const item of filters.children)item.setAttribute("aria-pressed",String(item===button));filter()};filters.appendChild(button)}
const tree={folders:{},files:[]};for(const doc of graph.documents||[]){const parts=doc.path.split("/"),file=parts.pop();let cursor=tree;for(const part of parts){cursor.folders[part]??={folders:{},files:[]};cursor=cursor.folders[part]}cursor.files.push({...doc,file})}function renderTree(node,host,onSelect){for(const name of Object.keys(node.folders).sort()){const details=document.createElement("details"),summary=document.createElement("summary"),children=document.createElement("div");details.open=true;summary.textContent=name;details.append(summary,children);host.appendChild(details);renderTree(node.folders[name],children,onSelect)}for(const doc of node.files.sort((a,b)=>a.file.localeCompare(b.file))){const button=document.createElement("button");button.type="button";button.textContent=doc.file;button.dataset.path=doc.path;button.setAttribute("aria-label",`Open ${doc.path}`);button.onclick=()=>onSelect(doc.path);host.appendChild(button)}}renderTree(tree,$("document-tree"),path=>{showDocument(path);$("document-browser").hidden=true});renderTree(tree,$("reader-tree"),showReaderDocument);
function xml(value){return String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&apos;"})[char])}
function titleLines(value){const words=String(value||"").trim().split(/\s+/),lines=[""];for(const word of words){const current=lines.at(-1),next=(current+" "+word).trim();if(next.length<=26||!current)lines[lines.length-1]=next;else if(lines.length<2)lines.push(word);else{lines[1]+=" "+word}}if(lines[1]?.length>29)lines[1]=lines[1].slice(0,28).trimEnd()+"…";return lines.slice(0,2)}
function cardSvg(data){const light=document.documentElement.dataset.theme==="light",lines=titleLines(data.label),type=String(data.type||"RECORD").toUpperCase(),status=String(data.status||"UNSPECIFIED").replaceAll("-"," ").toUpperCase(),accent=data.color||"#64748b",titleY=lines.length===1?51:44,bg=light?"#ffffff":"#0f1620",border=light?"#c7d0dc":"#2a3543",title=light?"#172033":"#edf2f8",meta=light?"#657387":"#8794a5";const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="220" height="76" viewBox="0 0 220 76"><rect x=".75" y=".75" width="218.5" height="74.5" rx="7" fill="${bg}" stroke="${border}" stroke-width="1.5"/><path d="M1 8a7 7 0 0 1 7-7h2v74H8a7 7 0 0 1-7-7z" fill="${accent}" opacity=".9"/><circle cx="20" cy="17" r="3" fill="${accent}"/><text x="29" y="20" fill="${meta}" font-family="JetBrains Mono,monospace" font-size="8" font-weight="500" letter-spacing=".8">${xml(type)}</text><text x="205" y="20" text-anchor="end" fill="${meta}" font-family="JetBrains Mono,monospace" font-size="7.5">${xml(status)}</text><text x="17" y="${titleY}" fill="${title}" font-family="Manrope,Segoe UI,sans-serif" font-size="13" font-weight="600">${xml(lines[0])}</text>${lines[1]?`<text x="17" y="61" fill="${title}" font-family="Manrope,Segoe UI,sans-serif" font-size="13" font-weight="600">${xml(lines[1])}</text>`:""}</svg>`;return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`}
for(const node of graph.nodes){const d=node.data,links=new Set([...(incoming[d.id]||[]),...(outgoing[d.id]||[])]).size,minutes=Number(d.frontmatter?.effort_minutes);d.metric=Number.isFinite(minutes)?`${minutes} MIN · ${links} LINK${links===1?"":"S"}`:`${links} LINK${links===1?"":"S"}`;if(d.type==="Workstream"){d.nodeWidth=208;d.nodeHeight=74}else if(d.type==="Tracker Profile"){d.nodeWidth=224;d.nodeHeight=76}else if(d.type==="Visualization"){d.nodeWidth=232;d.nodeHeight=78}else{d.nodeWidth=220;d.nodeHeight=76}const semanticStatus=d.status;d.status=[semanticStatus,d.metric].filter(Boolean).join(" · ");d.card=cardSvg(d);d.status=semanticStatus}
const cy=cytoscape({container:$("graph"),elements:[...graph.nodes,...graph.edges],style:[{selector:"node",style:{width:220,height:76,shape:"round-rectangle","background-color":"#0f1620","background-image":"data(card)","background-fit":"cover","background-image-opacity":1,"border-width":0,"overlay-opacity":0,"transition-property":"opacity, border-width, border-color","transition-duration":"260ms"}},{selector:"node:selected",style:{"border-width":2,"border-color":"#65c8e3"}},{selector:"node.hover",style:{"border-width":1,"border-color":"#758397"}},{selector:"edge",style:{width:1.5,"line-color":"#53657a","target-arrow-color":"#53657a","target-arrow-shape":"triangle","arrow-scale":.8,"curve-style":"bezier",label:"data(relationship)",color:"#d6e2ee","font-family":"JetBrains Mono","font-size":9,"font-weight":500,"text-background-color":"#0c1119","text-background-opacity":.96,"text-background-padding":4,"text-background-shape":"roundrectangle","text-border-color":"#334154","text-border-width":1,"text-border-opacity":1,"text-rotation":"autorotate","transition-property":"opacity, line-color, target-arrow-color, width","transition-duration":"260ms"}},{selector:"edge.neighbour",style:{width:2.25,"line-color":"#55c0df","target-arrow-color":"#55c0df",color:"#e8f8fc"}},{selector:"node.neighbour",style:{"border-width":1,"border-color":"#3b6170"}},{selector:".dim",style:{opacity:.08}}],layout:{name:"cose",animate:true,animationDuration:520,animationEasing:"ease-out",padding:88,nodeRepulsion:24000,idealEdgeLength:170,edgeElasticity:.15,nestingFactor:1.1},wheelSensitivity:.18,minZoom:.22,maxZoom:1.8});
cy.style().selector("node").style({width:"data(nodeWidth)",height:"data(nodeHeight)"}).selector('node[type = "Task"]').style({shape:"round-rectangle"}).selector('node[type = "Workstream"]').style({shape:"cut-rectangle"}).selector('node[type = "Tracker Profile"]').style({shape:"barrel"}).selector('node[type = "Visualization"]').style({shape:"round-hexagon"}).selector("edge.possible-drift").style({width:3,"line-style":"dashed","line-color":"#d97706","target-arrow-color":"#d97706",color:"#f59e0b"}).selector("node.drift-newer").style({"border-width":3,"border-color":"#d97706"}).selector("node.drift-older").style({"border-width":2,"border-style":"dashed","border-color":"#f59e0b"}).update();
function temporalValue(data,field=temporalField){const value=data.frontmatter?.[field],parsed=Date.parse(value);return Number.isFinite(parsed)?parsed:null}
function temporalDates(){return [...new Set(graph.nodes.map(node=>temporalValue(node.data)).filter(value=>value!==null))].sort((a,b)=>a-b)}
function updateTemporalRange(reset=false){const dates=temporalDates(),range=$("time-range");range.max=String(Math.max(0,dates.length-1));if(reset||Number(range.value)>Number(range.max))range.value=range.max;const index=Number(range.value||0);temporalAtLatest=!dates.length||index===dates.length-1;temporalCutoff=dates[index]??Infinity;const exact=dates[index]?new Date(dates[index]).toISOString():"No dated records";$("time-output").textContent=dates[index]?`Through ${new Intl.DateTimeFormat(undefined,{dateStyle:"medium"}).format(dates[index])}`:"No dates";$("time-output").title=exact;filter();if($("layout").value==="timeline")runLayout("timeline")}
function updateDrift(){let count=0;cy.elements().removeClass("possible-drift drift-newer drift-older");if(driftReview){for(const edge of cy.edges()){const sourceTime=temporalValue(edge.source().data()),targetTime=temporalValue(edge.target().data());if(sourceTime!==null&&targetTime!==null&&sourceTime>targetTime){edge.addClass("possible-drift");edge.source().addClass("drift-newer");edge.target().addClass("drift-older");count++}}}$("drift-count").textContent=driftReview?`${count} possible signal${count===1?"":"s"}`:"Drift review off";$("drift-count").title="Timestamp ordering is a review signal, not proof of drift."}
function runLayout(name){if(name!=="timeline"){cy.layout({name,animate:true,animationDuration:650,animationEasing:"ease-out",padding:74}).run();return}const nodes=cy.nodes(),dated=nodes.map(node=>temporalValue(node.data())).filter(value=>value!==null),min=Math.min(...dated),max=Math.max(...dated),span=Math.max(1,max-min),lanes=new Map(graph.types.map((type,index)=>[type,index]));cy.layout({name:"preset",fit:true,padding:74,animate:true,positions:node=>{const value=temporalValue(node.data()),x=value===null?960:80+((value-min)/span)*800,y=90+(lanes.get(node.data("type"))??graph.types.length)*125;return{x,y}}}).run()}
function filter(){const q=$("search").value.trim().toLowerCase();let visible=0;cy.nodes().forEach(n=>{const d=n.data(),hay=[d.label,d.id,d.status,d.description,...(d.tags||[])].join(" ").toLowerCase(),time=temporalValue(d),afterCutoff=!temporalAtLatest&&(time===null||time>temporalCutoff),dim=Boolean((q&&!hay.includes(q))||(activeType&&d.type!==activeType)||afterCutoff);n.toggleClass("dim",dim);if(!dim)visible++});cy.edges().forEach(e=>e.toggleClass("dim",e.source().hasClass("dim")||e.target().hasClass("dim")));$("results").textContent=`${visible} of ${graph.nodes.length} records`;$("clear-search").hidden=!q;updateDrift()}
function resolveInternal(sourceId,href){if(!href||href.startsWith("#")||/^[a-z][a-z0-9+.-]*:/i.test(href))return null;const clean=href.split("#",1)[0].split("?",1)[0];if(!clean.endsWith(".md"))return null;const parts=clean.startsWith("/")?[]:sourceId.split("/").slice(0,-1);for(const part of clean.replace(/^\//,"").split("/")){if(!part||part===".")continue;if(part==="..")parts.pop();else parts.push(part)}return parts.join("/").replace(/\.md$/,"")}
function renderMarkdown(value,body=$("record-body")){if(!globalThis.marked||!globalThis.DOMPurify){body.textContent=value;return body}body.innerHTML=DOMPurify.sanitize(marked.parse(value,{gfm:true,breaks:false}),{USE_PROFILES:{html:true}});if(globalThis.mermaid){const diagrams=[];for(const code of body.querySelectorAll("code.language-mermaid")){const host=document.createElement("div");host.className="mermaid";host.textContent=code.textContent;code.parentElement.replaceWith(host);diagrams.push(host)}if(diagrams.length){mermaid.initialize({startOnLoad:false,securityLevel:"strict",theme:document.documentElement.dataset.theme==="light"?"default":"dark"});mermaid.run({nodes:diagrams}).catch(()=>{})}}return body}
function resolveDocument(sourcePath,href){if(!href||href.startsWith("#")||/^[a-z][a-z0-9+.-]*:/i.test(href))return null;const clean=href.split("#",1)[0].split("?",1)[0];if(!clean.endsWith(".md"))return null;const parts=clean.startsWith("/")?[]:sourcePath.split("/").slice(0,-1);for(const part of clean.replace(/^\//,"").split("/")){if(!part||part===".")continue;if(part==="..")parts.pop();else parts.push(part)}return parts.join("/")}
function showReaderDocument(path){const doc=documentsByPath[path];if(!doc)return;readerPath=path;$("reader-title").textContent=doc.title;$("reader-path").textContent=doc.path;const body=renderMarkdown(doc.body,$("document-reader"));for(const button of $("reader-tree").querySelectorAll("button[data-path]"))button.setAttribute("aria-current",button.dataset.path===path?"page":"false");for(const link of body.querySelectorAll("a[href]")){const target=resolveDocument(path,link.getAttribute("href"));if(target&&documentsByPath[target]){link.title=`Open ${target}`;link.onclick=event=>{event.preventDefault();showReaderDocument(target)}}else if(link.protocol==="http:"||link.protocol==="https:"){link.target="_blank";link.rel="noopener noreferrer"}}$("reader-main")?.scrollTo?.({top:0,behavior:"auto"})}
function switchView(view){const documents=view==="documents";$("graph-view").hidden=documents;$("documents-view").hidden=!documents;$("graph-tab").setAttribute("aria-selected",String(!documents));$("documents-tab").setAttribute("aria-selected",String(documents));$("graph-tab").tabIndex=documents?-1:0;$("documents-tab").tabIndex=documents?0:-1;if(documents&&!readerPath){const first=(graph.documents||[])[0];if(first)showReaderDocument(first.path)}if(!documents)setTimeout(()=>{cy.resize();cy.fit(cy.elements(":visible"),72)},0)}
function setRecordTime(id,value){const element=$(id);if(!value){element.textContent="Not recorded";element.removeAttribute("datetime");element.title="";return}const parsed=new Date(value),valid=!Number.isNaN(parsed.valueOf());element.textContent=valid?new Intl.DateTimeFormat(undefined,{dateStyle:"medium",timeStyle:"short"}).format(parsed):String(value);element.dateTime=String(value);element.title=String(value)}
function showDocument(path){const document=documentsByPath[path];if(!document)return;if(document.record_id&&index[document.record_id]){show(document.record_id);return}cy.elements().removeClass("neighbour");cy.elements().unselect();$("empty").hidden=true;$("content").hidden=false;$("inspector-label").textContent="Document inspector";const chip=$("record-type");chip.textContent="Document";chip.style.setProperty("--chip-color","#64748b");$("record-title").textContent=document.title;$("record-id").textContent=document.path;$("record-status").textContent="Markdown";$("record-description").textContent="Repository Markdown document.";$("record-tags").textContent="No tags";$("record-connections").textContent="Not an OKF record";for(const field of ["record-last-updated","record-created","record-started","record-finished"])setRecordTime(field,null);$("backlinks").hidden=true;$("raw-frontmatter-section").hidden=true;$("raw-frontmatter").textContent="";$("raw-document").textContent=document.source;renderMarkdown(document.body);if(innerWidth<761)$("detail").scrollIntoView({behavior:"smooth",block:"start"})}
function show(id){const d=index[id];if(!d)return;cy.elements().removeClass("neighbour");cy.elements().unselect();const selected=cy.getElementById(id);selected.select();selected.neighborhood().addClass("neighbour");$("empty").hidden=true;$("content").hidden=false;$("inspector-label").textContent="Record inspector";$("raw-frontmatter-section").hidden=false;const chip=$("record-type");chip.textContent=d.type;chip.style.setProperty("--chip-color",d.color);$("record-title").textContent=d.label;$("record-id").textContent=id;$("record-status").textContent=d.status||"no status";$("record-description").textContent=d.description||"No description supplied.";const tags=$("record-tags");tags.replaceChildren(...((d.tags||[]).map(value=>{const span=document.createElement("span");span.className="tag";span.textContent=value;return span})));if(!tags.childNodes.length)tags.textContent="No tags";const connectionCount=new Set([...(incoming[id]||[]),...(outgoing[id]||[])]).size;$("record-connections").textContent=`${connectionCount} ${connectionCount===1?"relationship":"relationships"}`;setRecordTime("record-last-updated",d.frontmatter?.timestamp);setRecordTime("record-created",d.frontmatter?.created);setRecordTime("record-started",d.frontmatter?.started);setRecordTime("record-finished",d.frontmatter?.finished);$("raw-frontmatter").textContent=graph.frontmatters[id]||"";$("raw-document").textContent=graph.sources[id]||graph.bodies[id]||"";const body=renderMarkdown(graph.bodies[id]||"");for(const link of body.querySelectorAll("a[href]")){const target=resolveInternal(id,link.getAttribute("href"));if(target&&index[target]){link.title=`Open ${index[target].label}`;link.onclick=event=>{event.preventDefault();show(target)}}else if(link.protocol==="http:"||link.protocol==="https:"){link.target="_blank";link.rel="noopener noreferrer"}}const sources=incoming[id]||[],section=$("backlinks"),list=$("backlinks-list");list.replaceChildren();section.hidden=!sources.length;$("backlink-count").textContent=`${sources.length} source${sources.length===1?"":"s"}`;for(const source of sources){const li=document.createElement("li"),a=document.createElement("a");a.href="#";a.className="backlink";a.innerHTML=`<strong></strong><span>↗</span>`;a.querySelector("strong").textContent=index[source]?.label||source;a.onclick=e=>{e.preventDefault();show(source)};li.appendChild(a);list.appendChild(li)}if(innerWidth<761)$("detail").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"})}
function setTheme(theme){document.documentElement.dataset.theme=theme;try{localStorage.setItem("okf-theme",theme)}catch{}$("theme").setAttribute("aria-label",theme==="light"?"Use dark theme":"Use light theme");labelButton($("theme"));for(const node of cy.nodes()){const d=node.data(),semanticStatus=d.status;d.status=[semanticStatus,d.metric].filter(Boolean).join(" · ");node.data("card",cardSvg(d));d.status=semanticStatus}const light=theme==="light";cy.style().selector("edge").style({color:light?"#334155":"#d6e2ee","line-color":light?"#8492a5":"#53657a","target-arrow-color":light?"#8492a5":"#53657a","text-background-color":light?"#f8fafc":"#0c1119","text-border-color":light?"#b8c2cf":"#334154"}).update();updateDrift()}
$("graph-tab").onclick=()=>switchView("graph");$("documents-tab").onclick=()=>switchView("documents");for(const tab of document.querySelectorAll('[role="tab"]'))tab.onkeydown=event=>{if(event.key!=="ArrowLeft"&&event.key!=="ArrowRight")return;event.preventDefault();const target=tab===$("graph-tab")?$("documents-tab"):$("graph-tab");target.click();target.focus()};
$("temporal-field").onchange=event=>{temporalField=event.target.value;updateTemporalRange(true)};$("time-range").oninput=()=>updateTemporalRange();$("drift-review").onclick=()=>{driftReview=!driftReview;$("drift-review").setAttribute("aria-pressed",String(driftReview));updateDrift()};
cy.on("tap","node",e=>show(e.target.id()));cy.on("mouseover","node",e=>e.target.addClass("hover"));cy.on("mouseout","node",e=>e.target.removeClass("hover"));$("search").oninput=filter;$("clear-search").onclick=()=>{$("search").value="";$("search").focus();filter()};$("layout").onchange=e=>cy.layout({name:e.target.value,animate:true,animationDuration:650,animationEasing:"ease-out",padding:74}).run();$("browse-documents").onclick=()=>{$("document-browser").hidden=!$("document-browser").hidden};$("close-documents").onclick=()=>{$("document-browser").hidden=true};$("theme").onclick=()=>setTheme(document.documentElement.dataset.theme==="light"?"dark":"light");$("fit").onclick=()=>cy.animate({fit:{eles:cy.elements(":visible"),padding:72},duration:560,easing:"ease-out"});$("fullscreen").onclick=async()=>{if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector(".graph-shell").requestFullscreen()};document.addEventListener("fullscreenchange",()=>{const active=Boolean(document.fullscreenElement);$("fullscreen").setAttribute("aria-label",active?"Exit fullscreen":"Enter fullscreen");labelButton($("fullscreen"));setTimeout(()=>{cy.resize();cy.fit(cy.elements(":visible"),72)},0)});$("reset").onclick=()=>{$("search").value="";activeType="";for(const item of filters.children)item.setAttribute("aria-pressed",String(!item.dataset.type));filter();cy.animate({fit:{eles:cy.elements(),padding:72},duration:560,easing:"ease-out"})};labelButtons();setTheme(document.documentElement.dataset.theme);filter();if(graph.nodes[0])show(graph.nodes[0].data.id)})();
</script>
</body>
</html>
"""


def generate_html(graph: dict[str, Any], name: str) -> str:
    rendered = HTML_TEMPLATE.replace("__NAME__", safe_json(name)).replace("__GRAPH__", safe_json(graph))
    temporal_controls = (
        '<div class="temporal-rail" aria-label="Temporal graph controls">'
        '<span class="temporal-label">Time field</span><select id="temporal-field" aria-label="Temporal field">'
        '<option value="timestamp">Last meaningful change</option><option value="created">Created</option>'
        '<option value="started">Started</option><option value="finished">Finished</option></select>'
        '<input id="time-range" type="range" min="0" value="0" aria-label="Show records through date">'
        '<output id="time-output" class="temporal-output">All dated records</output>'
        '<button id="drift-review" class="drift-button" type="button" aria-pressed="false" '
        'aria-label="Review possible timestamp drift">Review drift</button>'
        '<span id="drift-count" class="drift-count">Drift review off</span></div>'
        '<div class="temporal-note">Timestamp ordering is a review signal, not proof of drift.</div>'
    )
    rendered = rendered.replace(
        '<div class="filter-rail" id="type-filters" aria-label="Filter by record type"></div>',
        '<div class="filter-rail" id="type-filters" aria-label="Filter by record type"></div>' + temporal_controls,
    )
    return (
        rendered.replace('<option value="grid">Grid</option>', '<option value="grid" selected>Grid</option><option value="timeline">Timeline</option>')
        .replace('layout:{name:"cose"', 'layout:{name:"grid"')
        .replace('$("layout").onchange=e=>cy.layout({name:e.target.value,animate:true,animationDuration:650,animationEasing:"ease-out",padding:74}).run()', '$("layout").onchange=e=>runLayout(e.target.value)')
        .replace('$("reset").onclick=()=>{$("search").value="";activeType="";for(const item of filters.children)item.setAttribute("aria-pressed",String(!item.dataset.type));filter();cy.animate({fit:{eles:cy.elements(),padding:72},duration:560,easing:"ease-out"})}', '$("reset").onclick=()=>{$("search").value="";activeType="";temporalField="timestamp";driftReview=false;$("temporal-field").value="timestamp";$("drift-review").setAttribute("aria-pressed","false");$("layout").value="grid";for(const item of filters.children)item.setAttribute("aria-pressed",String(!item.dataset.type));updateTemporalRange(true);runLayout("grid")}')
        .replace('setTheme(document.documentElement.dataset.theme);filter();if(graph.nodes[0])', 'setTheme(document.documentElement.dataset.theme);updateTemporalRange(true);if(graph.nodes[0])')
    )


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
    rendered = generate_html(build_relationship_view(graph), name)
    rendered = rendered.replace("OKF Tasks · derived bundle view", "OKF Tasks · relationship map")
    rendered = rendered.replace("#graph{position:absolute;inset:0}", "#graph{position:absolute;inset:165px 0 0}")
    rendered = rendered.replace(
        '<option value="cose">Force layout</option>',
        '<option value="relationship" selected>Relationship layout</option><option value="cose">Force layout</option>',
    ).replace('<option value="grid" selected>Grid</option>', '<option value="grid">Grid</option>')
    rendered = rendered.replace(
        'layout:{name:"grid",animate:true,animationDuration:520,animationEasing:"ease-out",padding:88,nodeRepulsion:24000,idealEdgeLength:170,edgeElasticity:.15,nestingFactor:1.1}',
        'layout:{name:"preset",positions:node=>node.data("relationshipPosition"),fit:false}',
    )
    rendered = rendered.replace(
        'function runLayout(name){if(name!=="timeline")',
        'function runLayout(name){if(name==="relationship"){cy.layout({name:"preset",positions:node=>node.data("relationshipPosition")||node.position(),fit:false,animate:true,animationDuration:650,animationEasing:"ease-out"}).run();cy.zoom(1);cy.pan({x:0,y:0});return}if(name!=="timeline")',
    )
    rendered = rendered.replace(
        '$("layout").value="grid";for(const item',
        '$("layout").value="relationship";for(const item',
    ).replace('runLayout("grid")', 'runLayout("relationship")')
    rendered = rendered.replace(
        '$("record-count").textContent=graph.nodes.length;',
        '$("record-count").textContent=graph.nodes.filter(node=>!node.data.virtual).length;',
    )
    rendered = rendered.replace(
        'for(const n of graph.nodes)index[n.data.id]=n.data;',
        'for(const n of graph.nodes)if(!n.data.virtual)index[n.data.id]=n.data;',
    )
    rendered = rendered.replace(
        'if(graph.nodes[0])show(graph.nodes[0].data.id)',
        'const firstRecord=graph.nodes.find(node=>!node.data.virtual);if(firstRecord)show(firstRecord.data.id)',
    )
    rendered = rendered.replace(
        'if(!dim)visible++',
        'if(!dim&&!d.virtual)visible++',
    ).replace(
        '${visible} of ${graph.nodes.length} records',
        '${visible} of ${graph.nodes.filter(node=>!node.data.virtual).length} records',
    )
    rendered = rendered.replace(
        '.selector("edge.possible-drift")',
        '.selector(\'node[virtual]\').style({width:1,height:1,"background-image":"none","background-opacity":0,"border-width":0,label:"data(label)",color:"#64748b","font-family":"JetBrains Mono","font-size":12,"font-weight":500,"text-valign":"center","text-halign":"left","text-margin-x":8,"text-transform":"uppercase","overlay-opacity":0}).selector("edge.possible-drift")',
    )
    rendered = rendered.replace(
        '<span class="legend-item"><i class="legend-dot" style="background:#059669"></i>Time</span>',
        '<span class="legend-item"><i class="legend-dot" style="background:#059669"></i>Time</span><span class="legend-item"><i class="legend-boundary"></i>Bundle lane</span>',
    )
    rendered = rendered.replace(
        "</style>",
        ".legend-boundary{width:12px;height:8px;border:1px dashed var(--line-strong)}\n"
        ".graph-core.relationship-map #graph{inset:0}\n"
        "</style>",
        1,
    )
    return rendered


def write_or_check(path: Path, content: str, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != normalized:
            raise SystemExit(f"Generated visualization is stale or missing: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render OKF Tasks records as interactive HTML and GitHub Mermaid.")
    parser.add_argument("--bundle", required=True, help="Directory containing OKF Markdown records")
    parser.add_argument("--name", help="Display name (default: bundle directory name)")
    parser.add_argument("--html", help="Interactive HTML output path")
    parser.add_argument("--markdown", help="GitHub-rendered Mermaid Markdown output path")
    parser.add_argument("--check", action="store_true", help="Fail when requested outputs are stale")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.bundle).resolve()
    if not root.is_dir():
        raise SystemExit(f"Bundle directory not found: {root}")
    if not args.html and not args.markdown:
        raise SystemExit("Select at least one output with --html or --markdown.")
    records = read_records(root)
    if not records:
        raise SystemExit(f"No OKF records found under: {root}")
    graph = build_graph(records, read_documents(root, records))
    name = args.name or root.name
    if args.html:
        write_or_check(Path(args.html), generate_html(graph, name), args.check)
    if args.markdown:
        write_or_check(Path(args.markdown), generate_markdown(graph, name, args.bundle), args.check)
    print(f"Visualized {len(graph['nodes'])} records and {len(graph['edges'])} relationships.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
