from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "visualize_bundle.py"
GENERATE_COMPLEX_EXAMPLES = SKILL / "scripts" / "generate_complex_examples.py"
SPEC = importlib.util.spec_from_file_location("repo_task_visualize_bundle", SCRIPT)
assert SPEC and SPEC.loader
visualize_bundle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = visualize_bundle
SPEC.loader.exec_module(visualize_bundle)


class VisualizationPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        task = self.root / "tasks" / "ship-viewer" / "task.md"
        task.parent.mkdir(parents=True)
        task.write_text(
            """---
type: Task
task: ship-viewer
title: Ship viewer
description: Render the definitive workspace.
status: in-progress
created: 2026-07-17T20:00:00Z
timestamp: 2026-07-17T21:00:00Z
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

Review the [recorded session](./task.md#time:session).
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def generated(self) -> str:
        records = visualize_bundle.read_records(self.root)
        documents = visualize_bundle.read_documents(self.root, records)
        return visualize_bundle.generate_html(
            visualize_bundle.build_graph(records, documents), "Example"
        )

    def payload(self, generated: str) -> dict[str, object]:
        match = re.search(
            r'<script type="application/json" id="okf-bundle">(.*?)</script>',
            generated,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_bundles_the_definitive_light_first_graph_board_reader_workspace(self) -> None:
        generated = self.generated()
        self.assertIn('<html lang="en" data-theme="light">', generated)
        self.assertIn('<button class="view-tab" data-view="graph"', generated)
        self.assertIn('<button class="view-tab" data-view="board"', generated)
        self.assertIn('<button class="view-tab" data-view="reader"', generated)
        self.assertIn('class="wordmark"', generated)
        self.assertIn('--serif:Charter,"Bitstream Charter"', generated)
        self.assertIn('--accent:#2b4bc4', generated)

    def test_embedded_time_is_task_evidence(self) -> None:
        generated = self.generated()
        payload = self.payload(generated)
        node = payload["nodes"][0]["data"]
        self.assertEqual("session", node["frontmatter"]["time"][0]["id"])
        self.assertIn("times:Array.isArray(t.frontmatter?.time)", generated)
        self.assertIn("Time is canonical Task frontmatter data", generated)

    def test_relationship_graph_board_and_reader_behaviour_remains_available(self) -> None:
        generated = self.generated()
        self.assertIn("function buildGraph()", generated)
        self.assertIn("function applyGraphFocus()", generated)
        self.assertIn('"label":"data(elabel)"', generated)
        self.assertIn("function buildKanban()", generated)
        self.assertIn("function buildRows()", generated)
        self.assertIn("function buildTree()", generated)
        self.assertIn("function openReader(path)", generated)
        self.assertIn('id="reading-filter"', generated)
        self.assertIn('decision:"ADR / decision"', generated)
        self.assertIn("function applyGraphFilters()", generated)
        self.assertIn('selector:".filterdim"', generated)

    def test_dense_overview_is_semantic_and_selected_neighbourhood_reflows(self) -> None:
        generated = self.generated()
        self.assertIn("function updateGraphOverviewDetail()", generated)
        self.assertIn('node.toggleClass("overview-compact",compact&&!prominent)', generated)
        self.assertIn('node.data("deg")>=4', generated)
        self.assertIn("function focusGraphNeighborhood(path)", generated)
        self.assertIn('name:"concentric"', generated)
        self.assertIn("minNodeSpacing:10,spacingFactor:.44", generated)
        self.assertIn("graphViewportFor(focus.union(crumbs),44,1.6)", generated)
        self.assertIn("separateOverlappingNodes(focusNodes", generated)
        template = SCRIPT.with_name("visualizer_template.html").read_text(encoding="utf-8")
        graph_config = template.split("cy=cytoscape({", 1)[1].split("// layout runs", 1)[0]
        self.assertNotIn("wheelSensitivity", graph_config)

    def test_standalone_workspace_bundles_runtimes_for_offline_review(self) -> None:
        generated = self.generated()
        self.assertNotIn('src="http://', generated)
        self.assertNotIn('src="https://', generated)
        self.assertNotIn("cdn.jsdelivr.net/npm/mermaid", generated)
        self.assertNotIn("__MERMAID_RUNTIME__", generated)
        self.assertTrue((SCRIPT.parent / "vendor" / "mermaid-11.10.1.min.js").is_file())
        self.assertTrue((SCRIPT.parent / "vendor" / "mermaid-11.10.1.LICENSE").is_file())

    def test_graph_uses_a_compact_vertical_relationship_focus_panel(self) -> None:
        generated = self.generated()
        self.assertIn("function renderGraphFocus(host)", generated)
        self.assertIn('className="graph-focus-flow"', generated)
        self.assertIn('graphFocusLane("Incoming",incoming,"incoming")', generated)
        self.assertIn('graphFocusLane("Outgoing",outgoing,"outgoing")', generated)
        self.assertIn('if(state.view==="graph"){renderGraphFocus(host)', generated)
        focus = generated.split("function renderGraphFocus(host)", 1)[1].split(
            "function renderRecordDetail", 1
        )[0]
        self.assertNotIn("renderMd(", focus)
        self.assertIn("Open in Reader", focus)
        self.assertIn('function centerGraphFocus(host,anchor)', generated)
        self.assertIn('graphScrollCue("up",incoming.length,incomingLane)', generated)
        self.assertIn('graphScrollCue("down",outgoing.length,outgoingLane)', generated)

    def test_temporal_drift_markdown_and_theme_controls_are_preserved(self) -> None:
        generated = self.generated()
        self.assertIn('id="temporal-field"', generated)
        self.assertIn('id="drift-btn"', generated)
        self.assertIn('selector:"edge.drift"', generated)
        self.assertIn("possible timestamp-order signal", generated)
        self.assertIn("review semantics before calling content stale", generated)
        self.assertIn("marked.parse(text||\"\")", generated)
        self.assertIn("code.language-mermaid", generated)
        self.assertIn('securityLevel:"strict"', generated)
        self.assertIn("DOMPurify.sanitize", generated)
        self.assertIn('localStorage.getItem("okf-proto-theme")', generated)

    def test_scalable_mermaid_and_dynamic_small_graph_framing_are_preserved(self) -> None:
        records = visualize_bundle.read_records(self.root)
        graph = visualize_bundle.build_graph(records)
        graph["nodes"].append({"data": {"id": "docs/guide", "label": "Guide", "type": "Architecture", "status": ""}})
        graph["edges"].append({"data": {"id": "e-guide", "source": "tasks/ship-viewer/task", "target": "docs/guide", "relationship": "links"}})
        markdown = visualize_bundle.generate_markdown(graph, "Example", "tasks")
        self.assertIn("## Connected-area overview", markdown)
        self.assertIn("## Connected component 1", markdown)
        self.assertIn("function graphLayoutMetrics(count)", self.generated())
        self.assertIn("startRadius:compact?Math.min(190,80+count*14):340", self.generated())
        self.assertIn("cy.fit(cy.elements(),metrics.padding);", self.generated())
        self.assertNotIn("minimumZoom", self.generated())
        self.assertIn('window.addEventListener("resize"', self.generated())

    def test_relationship_renderer_uses_the_same_workspace(self) -> None:
        records = visualize_bundle.read_records(self.root)
        graph = visualize_bundle.build_graph(records)
        generated = visualize_bundle.generate_relationship_html(graph, "Relationships")
        self.assertIn('data-view="graph"', generated)
        self.assertIn('data-view="board"', generated)
        self.assertIn('data-view="reader"', generated)
        self.assertEqual("relationship", self.payload(generated)["default_layout"])

    def test_bundled_viewer_keeps_its_external_template(self) -> None:
        self.assertTrue(SCRIPT.with_name("visualizer_template.html").is_file())

    def test_explicit_exclusions_and_typed_readmes_remain_available(self) -> None:
        readme = self.root / "README.md"
        readme.write_text(
            "---\ntype: Knowledge Document\ntitle: Guide\ntimestamp: 2026-07-19T12:00:00Z\n"
            "navigation:\n  role: entry-point\n  order: 10\n---\n# Guide\n\n"
            "Read the [task](./tasks/ship-viewer/task.md).\n",
            encoding="utf-8",
        )
        scratch = self.root / "notes" / "scratch.md"
        scratch.parent.mkdir()
        scratch.write_text("# Temporary note\n", encoding="utf-8")
        (self.root / visualize_bundle.DEFAULT_EXCLUSION_FILE).write_text(
            "notes/**\n", encoding="utf-8"
        )
        exclusions = visualize_bundle.load_exclusions(self.root)
        records = visualize_bundle.read_records(self.root, exclusions)
        documents = visualize_bundle.read_documents(self.root, records, exclusions)
        graph = visualize_bundle.build_graph(records, documents)
        self.assertIn("README", {node["data"]["id"] for node in graph["nodes"]})
        self.assertNotIn("notes/scratch.md", {document["path"] for document in documents})

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
        (self.root / visualize_bundle.DEFAULT_EXCLUSION_FILE).write_text(
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

    def test_bundled_complex_examples_generator_creates_dense_workspaces(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(GENERATE_COMPLEX_EXAMPLES), "--root", str(self.root)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        checked = subprocess.run(
            [sys.executable, str(GENERATE_COMPLEX_EXAMPLES), "--root", str(self.root), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        expectations = {
            "complex-task-portfolio": 50,
            "architecture-knowledge-base": 57,
            "combined-delivery-architecture": 108,
        }
        for name, minimum_records in expectations.items():
            records = visualize_bundle.read_records(self.root / "examples" / name)
            with self.subTest(name=name):
                self.assertGreaterEqual(len(records), minimum_records)


if __name__ == "__main__":
    unittest.main()
