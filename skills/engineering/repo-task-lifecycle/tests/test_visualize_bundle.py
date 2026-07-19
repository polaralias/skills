from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "visualize_bundle.py"
SPEC = importlib.util.spec_from_file_location("repo_task_visualize_bundle", SCRIPT)
assert SPEC and SPEC.loader
visualize_bundle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = visualize_bundle
SPEC.loader.exec_module(visualize_bundle)


class VisualizationPackageTests(unittest.TestCase):
    def test_bundled_viewer_exposes_light_first_graph_and_document_views(self) -> None:
        generated = visualize_bundle.generate_html(
            {
                "nodes": [],
                "edges": [],
                "bodies": {},
                "sources": {},
                "frontmatters": {},
                "documents": [],
                "types": [],
                "palette": {},
            },
            "Example",
        )
        self.assertIn('document.documentElement.dataset.theme=savedTheme||"light"', generated)
        self.assertIn('id="graph-tab"', generated)
        self.assertIn('id="documents-tab"', generated)
        self.assertIn('id="document-reader"', generated)
        self.assertIn('id="reader-tree"', generated)
        self.assertIn("function labelButtons()", generated)
        self.assertIn("function showReaderDocument(path)", generated)
        self.assertIn('id="record-last-updated"', generated)
        self.assertIn('Last meaningful change', generated)
        self.assertIn('setRecordTime("record-last-updated",d.frontmatter?.timestamp)', generated)
        self.assertIn('<option value="grid" selected>Grid</option>', generated)
        self.assertIn('<option value="timeline">Timeline</option>', generated)
        self.assertIn('id="time-range"', generated)
        self.assertIn('id="drift-review"', generated)
        self.assertIn('edge.possible-drift', generated)
        self.assertNotIn('.selector(\'node[type = "Time Entry"]\')', generated)

    def test_bundled_viewer_exposes_relationship_focused_rendering(self) -> None:
        graph = {
            "nodes": [
                {
                    "data": {
                        "id": "example/tasks/ship/task",
                        "label": "Ship",
                        "type": "Task",
                        "status": "ready",
                        "description": "Ship the work.",
                        "tags": [],
                        "frontmatter": {},
                        "color": "#2563eb",
                    }
                }
            ],
            "edges": [],
            "bodies": {},
            "sources": {},
            "frontmatters": {},
            "documents": [],
            "types": ["Task"],
            "palette": {},
        }
        generated = visualize_bundle.generate_relationship_html(graph, "Relationships")
        self.assertIn('OKF Tasks · relationship map', generated)
        self.assertIn('<option value="relationship" selected>Relationship layout</option>', generated)
        self.assertIn('node[virtual]', generated)
        self.assertIn('Bundle lane', generated)
        self.assertIn('"relationshipPosition":', generated)


if __name__ == "__main__":
    unittest.main()
