from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"


class KnowledgeCliTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_concept(
        self,
        path: Path,
        *,
        concept_type: str,
        title: str,
        description: str,
        body: str,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n"
            f"type: {concept_type}\n"
            f"title: {title}\n"
            f"description: {description}\n"
            "timestamp: 2026-09-17T12:00:00Z\n"
            "authority: canonical\n"
            "navigation:\n"
            "  role: foundational\n"
            "---\n\n"
            f"# {title}\n\n"
            f"{body}\n",
            encoding="utf-8",
        )

    def test_check_validates_a_connected_typed_okf_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle = root / "docs" / "knowledge"
            self.write_concept(
                bundle / "architecture.md",
                concept_type="Architecture Concept",
                title="Context architecture",
                description="Explains how repository context is retrieved.",
                body="See [Documentation workflow](documentation.md).",
            )
            self.write_concept(
                bundle / "documentation.md",
                concept_type="Product Contract",
                title="Documentation workflow",
                description="Explains when canonical documentation is updated.",
                body="Canonical documentation is maintained during closure.",
            )

            result = self.run_cli(
                root,
                "knowledge",
                "check",
                "--bundle",
                "docs/knowledge",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "knowledge-checked")
            self.assertTrue(payload["conformant"])
            self.assertEqual(payload["conceptCount"], 2)
            self.assertEqual(payload["componentCount"], 1)
            self.assertEqual(payload["orphans"], [])
            self.assertEqual(payload["errors"], [])

    def test_build_indexes_creates_query_shaped_okf_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle = root / "docs" / "knowledge"
            self.write_concept(
                bundle / "documentation.md",
                concept_type="Product Contract",
                title="Documentation workflow",
                description="Explains when canonical documentation is updated.",
                body="Canonical documentation is maintained during closure.",
            )

            result = self.run_cli(
                root,
                "knowledge",
                "build-indexes",
                "--bundle",
                "docs/knowledge",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "knowledge-indexes-built")
            self.assertEqual(payload["written"], ["docs/knowledge/index.md"])
            index = (bundle / "index.md").read_text(encoding="utf-8")
            self.assertIn('okf_version: "0.1"', index)
            self.assertIn(
                "[Documentation workflow](documentation.md) - Explains when canonical documentation is updated.",
                index,
            )
            self.assertNotIn(b"\r\n", (bundle / "index.md").read_bytes())

    def test_register_binds_a_canonical_concept_to_explicit_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            knowledge = root / "docs" / "knowledge" / "documentation.md"
            source = root / "src" / "workflow.py"
            self.write_concept(
                knowledge,
                concept_type="Product Contract",
                title="Documentation workflow",
                description="Explains when canonical documentation is updated.",
                body="Canonical documentation is maintained during closure.",
            )
            source.parent.mkdir(parents=True)
            source.write_text("DOCUMENTATION_GATE = True\n", encoding="utf-8")

            result = self.run_cli(
                root,
                "knowledge",
                "register",
                "--knowledge",
                "docs/knowledge/documentation.md",
                "--source",
                "src/**/*.py",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "knowledge-registered")
            self.assertEqual(payload["knowledgePath"], "docs/knowledge/documentation.md")
            self.assertFalse(payload["verificationInvalidated"])
            manifest = json.loads(
                (root / ".polaralias" / "repo-context.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["knowledge"],
                [
                    {
                        "path": "docs/knowledge/documentation.md",
                        "sources": ["src/**/*.py"],
                    }
                ],
            )

    def test_context_find_expands_from_a_matching_okf_concept_to_its_relationships(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bundle = root / "docs" / "knowledge"
            self.write_concept(
                bundle / "architecture.md",
                concept_type="Architecture Concept",
                title="Context architecture",
                description="Explains the quasar retrieval pipeline.",
                body="The quasar pipeline links to the [Documentation workflow](documentation.md).",
            )
            self.write_concept(
                bundle / "documentation.md",
                concept_type="Product Contract",
                title="Documentation workflow",
                description="Explains when canonical documentation is updated.",
                body="Canonical documentation is maintained during closure.",
            )

            result = self.run_cli(
                root,
                "context",
                "find",
                "quasar retrieval pipeline",
                "--limit",
                "8",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            related = next(
                item
                for item in payload["results"]
                if item["path"] == "docs/knowledge/documentation.md"
            )
            self.assertIn("knowledge-relationship", related["reasons"])
            self.assertIn(
                "linked-from:docs/knowledge/architecture.md",
                related["reasons"],
            )

    def test_context_find_prefers_canonical_foundational_knowledge_for_reader_questions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            knowledge = root / "docs" / "knowledge" / "workflow.md"
            self.write_concept(
                knowledge,
                concept_type="Architecture Concept",
                title="Engineering workflow",
                description="Explains documentation work before merge.",
                body="Documentation work is completed before merge.",
            )
            (root / "notes.md").write_text(
                "# Notes\n\nDocumentation work before merge. Documentation work before merge.\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "find",
                "documentation work before merge",
                "--limit",
                "5",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["results"][0]["path"], "docs/knowledge/workflow.md")
            self.assertIn("canonical-knowledge", payload["results"][0]["reasons"])
            self.assertIn("foundational-knowledge", payload["results"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
