from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "visualize_bundle.py"
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


if __name__ == "__main__":
    unittest.main()
