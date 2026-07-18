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


if __name__ == "__main__":
    unittest.main()
