from __future__ import annotations

import argparse
from pathlib import Path

from visualize_bundle import (
    build_graph,
    generate_html,
    generate_markdown,
    generate_relationship_html,
    excluded_markdown_paths,
    load_exclusions,
    read_documents,
    read_records,
    write_or_check,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    ("examples/visualization/tasks", "OKF Tasks visualisation example", "okf-tasks-visualization.html", generate_html),
    ("examples/complex-task-portfolio", "OKF Tasks complex task portfolio", "okf-tasks-complex-task-portfolio.html", generate_html),
    ("examples/architecture-knowledge-base", "OKF architecture knowledge base", "okf-tasks-architecture-knowledge-base.html", generate_html),
    ("examples/combined-delivery-architecture", "OKF combined delivery and architecture workspace", "okf-tasks-combined-workspace.html", generate_html),
    ("examples", "OKF Tasks example bundles", "okf-tasks-examples.html", generate_html),
    ("examples", "OKF Tasks relationship map", "okf-tasks-relationships.html", generate_relationship_html),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the reviewable local OKF Tasks HTML pages.")
    parser.add_argument("--root", default=str(PROJECT_ROOT), help="OKF Tasks repository root")
    parser.add_argument("--output-dir", help="Output directory (default: <root>/local-docs)")
    parser.add_argument("--check", action="store_true", help="Fail if any generated page is stale")
    parser.add_argument("--mermaid", action="store_true", help="Also generate scalable Mermaid reports beside the primary HTML workspaces")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output_dir).resolve() if args.output_dir else root / "local-docs"
    for source_name, title, filename, renderer in PAGES:
        source = root / source_name
        exclusions = load_exclusions(source)
        records = read_records(source, exclusions)
        graph = build_graph(
            records,
            read_documents(source, records, exclusions),
            {"patterns": exclusions, "paths": excluded_markdown_paths(source, exclusions)},
        )
        write_or_check(output / filename, renderer(graph, title), args.check)
        if args.mermaid and renderer is generate_html:
            mermaid_name = f"{Path(filename).stem}.mermaid.md"
            write_or_check(output / mermaid_name, generate_markdown(graph, title, source_name), args.check)
    verb = "Checked" if args.check else "Generated"
    mermaid_count = sum(renderer is generate_html for *_, renderer in PAGES) if args.mermaid else 0
    print(f"{verb} {len(PAGES)} HTML pages and {mermaid_count} Mermaid reports in {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
