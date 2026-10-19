from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts" / "visualize_bundle.py"
GENERATE_LOCAL_DOCS = REPOSITORY / "scripts" / "generate_local_docs.py"
GENERATE_COMPLEX_EXAMPLES = REPOSITORY / "scripts" / "generate_complex_examples.py"
SPEC = importlib.util.spec_from_file_location("visualize_bundle", SCRIPT)
assert SPEC and SPEC.loader
visualize_bundle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = visualize_bundle
SPEC.loader.exec_module(visualize_bundle)


class VisualizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        task = self.root / "tasks" / "ship-viewer" / "task.md"
        workstream = self.root / "tasks" / "ship-viewer" / "workstreams" / "ui.md"
        task.parent.mkdir(parents=True)
        workstream.parent.mkdir(parents=True)
        task.write_text(
            """---
type: Task
task: ship-viewer
title: Ship viewer
description: Render the task graph.
status: in-progress
created: 2026-07-17T20:00:00Z
timestamp: 2026-07-17T21:00:00Z
tags: [visualization]
started: 2026-07-17T20:00:00Z
effort_minutes: 30
time:
  - id: session
    status: closed
    actor: agent
    started: 2026-07-17T20:00:00Z
    finished: 2026-07-17T20:30:00Z
    elapsed_minutes: 30
    effort_minutes: 30
    method: tracked
    activity: implementation
---
# Ship viewer

See the [UI workstream](./workstreams/ui.md).
Review the [recorded session](./task.md#time:session).
""",
            encoding="utf-8",
        )
        workstream.write_text(
            """---
type: Workstream
task: ship-viewer
workstream: ui
title: Build UI
description: Build the interactive graph.
status: ready
created: 2026-07-17T20:00:00Z
timestamp: 2026-07-17T20:00:00Z
---
# Build UI
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @unittest.skipUnless(os.name == "nt", "Windows alternate data streams only")
    def test_generated_html_clears_windows_download_zone(self) -> None:
        output = self.root / "visualization.html"
        output.write_text("downloaded", encoding="utf-8")
        zone = Path(f"{output}:Zone.Identifier")
        zone.write_text("[ZoneTransfer]\nZoneId=3\n", encoding="utf-8")

        visualize_bundle.write_or_check(output, "generated", False)

        self.assertFalse(zone.exists())
        self.assertEqual("generated\n", output.read_text(encoding="utf-8"))

    def graph(self, include_documents: bool = False) -> dict[str, object]:
        records = visualize_bundle.read_records(self.root)
        documents = visualize_bundle.read_documents(self.root, records) if include_documents else None
        return visualize_bundle.build_graph(records, documents)

    def generated(self, include_documents: bool = True) -> str:
        return visualize_bundle.generate_html(self.graph(include_documents), "Example")

    def embedded_payload(self, generated: str) -> dict[str, object]:
        match = re.search(
            r'<script type="application/json" id="okf-bundle">(.*?)</script>',
            generated,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_builds_task_workstream_and_fragment_addressed_time_relationships(self) -> None:
        graph = self.graph()
        ids = {node["data"]["id"] for node in graph["nodes"]}
        self.assertEqual({"tasks/ship-viewer/task", "tasks/ship-viewer/workstreams/ui"}, ids)
        relationships = {
            (
                edge["data"]["source"],
                edge["data"]["target"],
                edge["data"]["relationship"],
                edge["data"].get("fragment"),
            )
            for edge in graph["edges"]
        }
        self.assertIn(
            ("tasks/ship-viewer/task", "tasks/ship-viewer/task", "time", "time:session"),
            relationships,
        )
        self.assertIn(
            ("tasks/ship-viewer/workstreams/ui", "tasks/ship-viewer/task", "workstream", None),
            relationships,
        )

    def test_embeds_a_safe_dynamic_payload_in_the_definitive_workspace(self) -> None:
        task = self.root / "tasks" / "ship-viewer" / "task.md"
        task.write_text(
            task.read_text(encoding="utf-8").replace(
                "Render the task graph.", "Render </script><script>alert(1)</script> safely."
            ),
            encoding="utf-8",
        )
        generated = self.generated()
        self.assertNotIn("</script><script>alert(1)</script>", generated)
        payload = self.embedded_payload(generated)
        self.assertEqual("Example", payload["name"])
        self.assertEqual(2, len(payload["nodes"]))
        task_node = next(node["data"] for node in payload["nodes"] if node["data"]["type"] == "Task")
        self.assertEqual("session", task_node["frontmatter"]["time"][0]["id"])

    def test_preserves_the_definitive_graph_board_reader_identity(self) -> None:
        generated = self.generated()
        self.assertIn('<button class="view-tab" data-view="graph"', generated)
        self.assertIn('<button class="view-tab" data-view="board"', generated)
        self.assertIn('<button class="view-tab" data-view="reader"', generated)
        self.assertIn('class="wordmark"', generated)
        self.assertIn('class="detail" id="detail"', generated)
        self.assertIn('--serif:Charter,"Bitstream Charter"', generated)
        self.assertIn('--accent:#2b4bc4', generated)

    def test_uses_embedded_task_time_as_task_data(self) -> None:
        generated = self.generated()
        payload = self.embedded_payload(generated)
        task = next(node["data"] for node in payload["nodes"] if node["data"]["type"] == "Task")
        self.assertEqual("session", task["frontmatter"]["time"][0]["id"])
        self.assertIn("times:Array.isArray(t.frontmatter?.time)", generated)
        self.assertIn("Time is canonical Task frontmatter data", generated)

    def test_graph_keeps_relationships_visible_and_focusable(self) -> None:
        generated = self.generated()
        self.assertIn('id="cy"', generated)
        self.assertIn("function buildGraph()", generated)
        self.assertIn("function applyGraphFocus()", generated)
        self.assertIn('"label":"data(elabel)"', generated)
        self.assertIn('cy.on("tap","node.main"', generated)
        self.assertIn('id="fit-btn"', generated)

    def test_standalone_workspace_embeds_all_runtimes_without_remote_requests(self) -> None:
        generated = self.generated()
        self.assertNotIn('src="http://', generated)
        self.assertNotIn('src="https://', generated)
        self.assertNotIn("cdn.jsdelivr.net/npm/mermaid", generated)
        self.assertIn('securityLevel:"strict"', generated)
        self.assertNotIn("__MERMAID_RUNTIME__", generated)

    def test_dense_overview_preserves_landmarks_and_reflows_selected_neighbourhood(self) -> None:
        generated = self.generated()
        self.assertIn("function updateGraphOverviewDetail()", generated)
        self.assertIn('node.toggleClass("overview-compact",overview&&(node.data("deg")===0||(compact&&!prominent)))', generated)
        self.assertIn('node.data("deg")>=4', generated)
        self.assertIn("function focusGraphNeighborhood(path)", generated)
        self.assertIn('name:"concentric"', generated)
        self.assertIn("minNodeSpacing:10,spacingFactor:.44", generated)
        self.assertIn("graphViewportFor(focus.union(crumbs),44,1.6)", generated)
        self.assertIn("function arrangeOverviewIsolates(connected,isolates,metrics)", generated)
        self.assertIn("function widenOverviewConnected(connected)", generated)
        self.assertIn("function widenOverviewComposition(nodes)", generated)
        self.assertIn("Math.min(720000,200000+count*26000)", generated)
        self.assertIn("idealEdgeLength:compact?64+count*4:125", generated)
        self.assertIn("Math.min(1.45,Math.max(1,1.05/", generated)
        self.assertIn("Math.min(1.8,canvasAspect*.68)", generated)
        self.assertIn('cy.fit(cy.elements("node.main,edge")', generated)
        self.assertIn("separateOverlappingNodes(focusNodes", generated)
        template = SCRIPT.with_name("visualizer_template.html").read_text(encoding="utf-8")
        graph_config = template.split("cy=cytoscape({", 1)[1].split("// layout runs", 1)[0]
        self.assertNotIn("wheelSensitivity", graph_config)

    def test_graph_filters_types_and_reading_prominence_without_hiding_context(self) -> None:
        generated = self.generated()
        self.assertIn('id="reading-filter"', generated)
        self.assertIn('data-kind="${k}"', generated)
        self.assertIn('state.graphKind===button.dataset.kind', generated)
        self.assertIn('function applyGraphFilters()', generated)
        self.assertIn('selector:".filterdim"', generated)
        self.assertIn('decision:"ADR / decision"', generated)
        self.assertIn('readingRole:navigation.role||""', generated)
        self.assertIn('displayLabel', generated)
        self.assertIn('Reading prominence', generated)

    def test_graph_uses_a_compact_vertical_relationship_focus_panel(self) -> None:
        generated = self.generated()
        self.assertIn("function renderGraphFocus(host)", generated)
        self.assertIn('className="graph-focus-flow"', generated)
        self.assertTrue('graphFocusLane("Incoming",incoming,"incoming",path)' in generated)
        self.assertTrue('graphFocusLane("Outgoing",outgoing,"outgoing",path)' in generated)
        self.assertIn('if(state.view==="graph"){renderGraphFocus(host)', generated)
        focus = generated.split("function renderGraphFocus(host)", 1)[1].split(
            "function renderRecordDetail", 1
        )[0]
        self.assertNotIn("renderMd(", focus)
        self.assertIn("Open in Reader", focus)
        self.assertIn('function centerGraphFocus(host,anchor)', generated)
        self.assertIn('graphScrollCue("up",incoming.length,incomingLane)', generated)
        self.assertIn('graphScrollCue("down",outgoing.length,outgoingLane)', generated)
        self.assertIn('host.scrollTop=Math.max(0', generated)

    def test_board_supports_columns_rows_effort_and_embedded_time_evidence(self) -> None:
        generated = self.generated()
        self.assertIn('data-layout="columns"', generated)
        self.assertIn('data-layout="rows"', generated)
        self.assertIn("function buildKanban()", generated)
        self.assertIn("function buildRows()", generated)
        self.assertIn("function effortHtml(logged,estimate)", generated)
        self.assertIn("m.times.length", generated)
        self.assertIn("e.finished||e.started", generated)

    def test_reader_renders_github_markdown_mermaid_and_repository_navigation(self) -> None:
        (self.root / "README.md").write_text("# Repository guide\n", encoding="utf-8")
        generated = self.generated()
        payload = self.embedded_payload(generated)
        self.assertIn("README.md", {document["path"] for document in payload["documents"]})
        self.assertIn('class="reader"', generated)
        self.assertIn('id="rtree"', generated)
        self.assertIn("function buildTree()", generated)
        self.assertIn("function openReader(path)", generated)
        self.assertIn("marked.parse(text||\"\")", generated)
        self.assertIn("code.language-mermaid", generated)
        self.assertIn('securityLevel:"strict"', generated)
        self.assertIn("DOMPurify.sanitize", generated)

    def test_typed_readme_is_a_linked_knowledge_record(self) -> None:
        readme = self.root / "README.md"
        readme.write_text(
            """---
type: Knowledge Document
title: Repository guide
description: Start here for delivery context.
timestamp: 2026-07-19T12:00:00Z
navigation:
  role: entry-point
  order: 10
---
# Repository guide

Continue with the [viewer task](./tasks/ship-viewer/task.md).
""",
            encoding="utf-8",
        )
        graph = self.graph(include_documents=True)
        ids = {node["data"]["id"] for node in graph["nodes"]}
        self.assertIn("README", ids)
        self.assertIn(
            ("README", "tasks/ship-viewer/task", "links"),
            {
                (edge["data"]["source"], edge["data"]["target"], edge["data"]["relationship"])
                for edge in graph["edges"]
            },
        )

    def test_explicit_exclusions_remove_records_and_reader_documents_with_provenance(self) -> None:
        omitted = self.root / "notes" / "scratch.md"
        omitted.parent.mkdir()
        omitted.write_text(
            "---\ntype: Knowledge Document\ntitle: Scratch\ntimestamp: 2026-07-19T12:00:00Z\n---\n# Scratch\n",
            encoding="utf-8",
        )
        policy = self.root / visualize_bundle.DEFAULT_EXCLUSION_FILE
        policy.write_text("# Deliberately outside this view\nnotes/**\n", encoding="utf-8")
        exclusions = visualize_bundle.load_exclusions(self.root)
        records = visualize_bundle.read_records(self.root, exclusions)
        documents = visualize_bundle.read_documents(self.root, records, exclusions)
        paths = visualize_bundle.excluded_markdown_paths(self.root, exclusions)
        graph = visualize_bundle.build_graph(
            records,
            documents,
            {"patterns": exclusions, "paths": paths},
        )
        self.assertNotIn("notes/scratch", {node["data"]["id"] for node in graph["nodes"]})
        self.assertNotIn("notes/scratch.md", {document["path"] for document in graph["documents"]})
        self.assertEqual(["notes/scratch.md"], graph["exclusions"]["paths"])
        generated = visualize_bundle.generate_html(graph, "Example")
        self.assertIn("RAW.exclusions?.paths?.length", generated)
        self.assertIn("RAW.exclusions.paths.length} excluded", generated)

    def test_rejects_exclusions_outside_the_bundle(self) -> None:
        with self.assertRaisesRegex(ValueError, "relative to the bundle root"):
            visualize_bundle.normalise_exclusion("C:/outside/*.md")
        with self.assertRaisesRegex(ValueError, "cannot traverse"):
            visualize_bundle.normalise_exclusion("../outside/*.md")

    def test_directory_exclusions_match_dependencies_at_every_depth(self) -> None:
        omitted = (
            self.root / "node_modules" / "top" / "README.md",
            self.root / "lambdas" / "worker" / "node_modules" / "nested" / "README.md",
            self.root / "triggers" / "hook" / ".venv" / "site-packages" / "README.md",
            self.root / ".pytest_cache" / "README.md",
        )
        for path in omitted:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Dependency documentation\n", encoding="utf-8")
        policy = self.root / visualize_bundle.DEFAULT_EXCLUSION_FILE
        policy.write_text(
            "node_modules/\n.venv/\n**/.pytest_cache/**\n",
            encoding="utf-8",
        )
        exclusions = visualize_bundle.load_exclusions(self.root)
        self.assertEqual(
            ["node_modules/", ".venv/", "**/.pytest_cache/**"],
            exclusions,
        )
        self.assertEqual(
            {path.relative_to(self.root).as_posix() for path in omitted},
            set(visualize_bundle.excluded_markdown_paths(self.root, exclusions)),
        )

    def test_adds_temporal_comparison_and_evidence_cautious_drift_indicators(self) -> None:
        generated = self.generated()
        self.assertIn('id="temporal-field"', generated)
        self.assertIn('id="drift-btn"', generated)
        self.assertIn("const driftEdgeKeys=()", generated)
        self.assertIn('selector:"edge.drift"', generated)
        self.assertIn("possible timestamp-order signal", generated)
        self.assertIn("review semantics before calling content stale", generated)
        self.assertIn('className="bcard"', generated)
        self.assertIn('possibleDrift?" drift":""', generated)

    def test_defaults_to_light_and_persists_theme_choice(self) -> None:
        generated = self.generated()
        self.assertIn('<html lang="en" data-theme="light">', generated)
        self.assertIn('localStorage.getItem("okf-proto-theme")', generated)
        self.assertIn('localStorage.setItem("okf-proto-theme",next)', generated)
        self.assertIn('@media(prefers-reduced-motion:reduce)', generated)

    def test_generates_github_mermaid(self) -> None:
        markdown = visualize_bundle.generate_markdown(self.graph(), "Example", "tasks")
        self.assertIn(chr(96) * 3 + "mermaid", markdown)
        self.assertIn("## Connected-area overview", markdown)
        self.assertIn("## Connected component 1", markdown)
        self.assertIn("## Key concept neighbourhoods", markdown)
        self.assertIn("Build UI · ready", markdown)
        self.assertIn("time:session", markdown)

    def test_visualization_manifest_covers_normative_generation_modes(self) -> None:
        manifest = json.loads((REPOSITORY / "conformance" / "visualization-manifest.json").read_text(encoding="utf-8"))
        case_ids = {case["id"] for case in manifest["cases"]}
        self.assertEqual(
            {
                "scalable-mermaid-report",
                "dynamic-small-graph-framing",
                "paired-derived-output",
                "prominence-and-type-filtering",
                "explicit-view-exclusions",
                "offline-semantic-graph",
                "typed-readme-knowledge",
                "reader-workspace-navigation",
            },
            case_ids,
        )

    def test_mermaid_flag_places_report_beside_html(self) -> None:
        html = self.root / "review.html"
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--bundle", str(self.root), "--html", str(html), "--mermaid"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = html.with_suffix(".mermaid.md")
        self.assertTrue(report.is_file())
        self.assertIn("## Connected component 1", report.read_text(encoding="utf-8"))

    def test_large_mermaid_component_splits_by_area_with_boundary_context(self) -> None:
        nodes = []
        edges = []
        for index in range(20):
            area = "alpha" if index < 10 else "beta"
            node_id = f"{area}/tasks/task-{index}/task"
            nodes.append({"data": {"id": node_id, "label": f"Task {index}", "type": "Task", "status": "ready"}})
            if index:
                previous_area = "alpha" if index - 1 < 10 else "beta"
                edges.append({"data": {"id": f"e{index}", "source": f"{previous_area}/tasks/task-{index - 1}/task", "target": node_id, "relationship": "depends on"}})
        markdown = visualize_bundle.generate_markdown({"nodes": nodes, "edges": edges}, "Large", "tasks")
        self.assertIn("### alpha", markdown)
        self.assertIn("### beta", markdown)
        self.assertIn("classDef boundary", markdown)
        for index in range(20):
            self.assertIn(f"Task {index} · ready", markdown)

    def test_small_graph_uses_compact_layout_and_always_fits(self) -> None:
        generated = self.generated()
        self.assertIn("function graphLayoutMetrics(count)", generated)
        self.assertIn("startRadius:compact?Math.min(190,80+count*14):340", generated)
        self.assertIn('cy.fit(cy.elements("node.main,edge"),metrics.padding);', generated)
        self.assertNotIn("minimumZoom", generated)
        self.assertIn('window.addEventListener("resize"', generated)
        self.assertIn("fitGraph();", generated)

    def test_complex_examples_are_current_and_dense(self) -> None:
        checked = subprocess.run(
            [sys.executable, str(GENERATE_COMPLEX_EXAMPLES), "--root", str(REPOSITORY), "--check"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        expectations = {
            "complex-task-portfolio": (50, 45),
            "architecture-knowledge-base": (57, 55),
            "combined-delivery-architecture": (108, 100),
        }
        for name, (minimum_records, minimum_edges) in expectations.items():
            source = REPOSITORY / "examples" / name
            records = visualize_bundle.read_records(source)
            graph = visualize_bundle.build_graph(records, visualize_bundle.read_documents(source, records))
            with self.subTest(name=name):
                self.assertGreaterEqual(len(records), minimum_records)
                self.assertGreaterEqual(len(graph["edges"]), minimum_edges)

    def test_local_documentation_generator_builds_all_workspace_pages(self) -> None:
        output = self.root / "local-docs"
        completed = subprocess.run(
            [sys.executable, str(GENERATE_LOCAL_DOCS), "--output-dir", str(output), "--mermaid"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        for name in (
            "okf-tasks-visualization.html",
            "okf-tasks-complex-task-portfolio.html",
            "okf-tasks-architecture-knowledge-base.html",
            "okf-tasks-combined-workspace.html",
            "okf-tasks-examples.html",
            "okf-tasks-relationships.html",
        ):
            generated = (output / name).read_text(encoding="utf-8")
            self.assertIn('data-view="graph"', generated)
            self.assertIn('data-view="board"', generated)
            self.assertIn('data-view="reader"', generated)
            self.assertNotIn("__GRAPH__", generated)
        for name in (
            "okf-tasks-visualization.mermaid.md",
            "okf-tasks-complex-task-portfolio.mermaid.md",
            "okf-tasks-architecture-knowledge-base.mermaid.md",
            "okf-tasks-combined-workspace.mermaid.md",
            "okf-tasks-examples.mermaid.md",
        ):
            generated = (output / name).read_text(encoding="utf-8")
            self.assertIn("## Connected-area overview", generated)
            self.assertIn(chr(96) * 3 + "mermaid", generated)
        checked = subprocess.run(
            [sys.executable, str(GENERATE_LOCAL_DOCS), "--output-dir", str(output), "--mermaid", "--check"],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, checked.returncode, checked.stderr)

    def test_packaged_renderer_matches_reviewed_producer_bytes(self) -> None:
        import hashlib
        manifest = json.loads((REPOSITORY / "OKF_UPSTREAM.json").read_text(encoding="utf-8"))
        for name in ("visualize_bundle.py", "generate_complex_examples.py", "visualizer_template.html",
                     "vendor/mermaid-11.10.1.min.js", "vendor/mermaid-11.10.1.LICENSE"):
            key = "scripts/" + name
            with self.subTest(resource=key):
                actual = hashlib.sha256((REPOSITORY / key).read_bytes()).hexdigest()
                self.assertEqual(manifest["resources"][key]["source_sha256"], actual)


if __name__ == "__main__":
    unittest.main()
