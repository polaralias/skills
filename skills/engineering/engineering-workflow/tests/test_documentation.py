from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"
PRE_MERGE = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "pre_merge.py"


class DocumentationLifecycleTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def run_pre_merge(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PRE_MERGE), "--root", str(root), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def git(self, root: Path, *args: str) -> None:
        result = subprocess.run(
            ["git", *args], cwd=root, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def repository(self, root: Path, *, bound: bool = True) -> None:
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "tests@example.test")
        self.git(root, "config", "user.name", "Workflow Tests")
        source = root / "src" / "workflow.py"
        source.parent.mkdir(parents=True)
        source.write_text("MODE = 'before'\n", encoding="utf-8")
        (root / "AGENTS.md").write_text(
            "# Repository rules\n\nCanonical documentation must be updated with material behavior.\n",
            encoding="utf-8",
        )
        concept = root / "docs" / "knowledge" / "workflow.md"
        concept.parent.mkdir(parents=True)
        concept.write_text(
            "---\n"
            "type: Architecture Concept\n"
            "title: Documentation lifecycle\n"
            "description: Explains how documentation is assessed before merge.\n"
            "authority: canonical\n"
            "navigation:\n"
            "  role: foundational\n"
            "---\n\n"
            "# Documentation lifecycle\n\n"
            "Documentation is assessed before merge.\n",
            encoding="utf-8",
        )
        manifest = root / ".polaralias" / "repo-context.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "knowledge": [
                        {
                            "path": "docs/knowledge/workflow.md",
                            "sources": ["src/**/*.py"],
                        }
                    ]
                    if bound
                    else [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "baseline")

    def test_assess_classifies_bound_material_changes_as_documentation_updates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(root, "documentation", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "documentation-assessed")
            self.assertEqual(payload["outcome"], "update")
            self.assertEqual(payload["changedPaths"], ["src/workflow.py"])
            self.assertEqual(
                payload["affectedKnowledge"], ["docs/knowledge/workflow.md"]
            )
            self.assertEqual(payload["generationContext"]["rulePaths"], ["AGENTS.md"])
            self.assertIn(
                "follow-applicable-repository-rules",
                payload["generationContext"]["constraints"],
            )
            self.assertTrue(payload["assessmentId"])

    def test_assess_discovers_nested_repository_rules_for_changed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            nested_rules = root / "src" / "AGENTS.md"
            nested_rules.write_text(
                "# Source rules\n\nDocument public source behavior in the canonical concept.\n",
                encoding="utf-8",
            )
            self.git(root, "add", "src/AGENTS.md")
            self.git(root, "commit", "-qm", "add nested rules")
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(root, "documentation", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(
                payload["generationContext"]["rulePaths"],
                ["AGENTS.md", "src/AGENTS.md"],
            )

    def test_assess_is_a_noop_for_generated_navigation_without_material_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "docs" / "knowledge" / "index.md").write_text(
                "<!-- Generated by engineering-workflow OKF knowledge index builder. -->\n",
                encoding="utf-8",
            )

            result = self.run_cli(root, "documentation", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["outcome"], "no-op")
            self.assertEqual(payload["changedPaths"], [])

    def test_assess_keeps_unmapped_material_changes_as_a_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root, bound=False)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(root, "documentation", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["outcome"], "decision-required")
            self.assertEqual(
                payload["impact"]["unmappedChanges"][0]["changedPath"],
                "src/workflow.py",
            )

    def test_assess_bounds_large_detail_payloads_without_losing_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root, bound=False)
            generated = root / "generated"
            generated.mkdir()
            for index in range(55):
                (generated / f"change-{index:02d}.txt").write_text(
                    f"material change {index}\n", encoding="utf-8"
                )

            result = self.run_cli(root, "documentation", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["changedPathCount"], 55)
            self.assertEqual(len(payload["changedPaths"]), 20)
            self.assertTrue(payload["detailsTruncated"])
            self.assertEqual(payload["impactCounts"]["unmappedChanges"], 55)
            self.assertEqual(len(payload["impact"]["unmappedChanges"]), 20)

    def test_change_explain_records_a_causal_receipt_for_the_current_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(
                root,
                "change",
                "explain",
                "--base",
                "HEAD",
                "--summary",
                "The workflow now enters after mode through the existing source path.",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "change-explained")
            self.assertEqual(payload["changedPaths"], ["src/workflow.py"])
            receipt = json.loads(
                (root / ".engineering-workflow" / "change-explanation.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["deltaFingerprint"], payload["deltaFingerprint"])
            self.assertIn("after mode", receipt["summary"])

    def test_apply_validates_reader_retrieval_and_records_a_fresh_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )
            concept = root / "docs" / "knowledge" / "workflow.md"
            concept.write_text(
                concept.read_text(encoding="utf-8").replace(
                    "Documentation is assessed before merge.",
                    "Documentation impact is assessed and verified before merge.",
                ),
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "documentation",
                "apply",
                "--base",
                "HEAD",
                "--bundle",
                "docs/knowledge",
                "--knowledge",
                "docs/knowledge/workflow.md",
                "--evidence",
                "Reviewed the workflow source and canonical lifecycle concept.",
                "--reader-query",
                "how is documentation assessed before merge",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "documentation-applied")
            self.assertEqual(payload["knowledgeFreshness"], "fresh")
            self.assertEqual(payload["readerChecks"][0]["status"], "passed")
            receipt = json.loads(
                (root / ".engineering-workflow" / "documentation-receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(receipt["deltaFingerprint"], payload["deltaFingerprint"])
            self.assertEqual(receipt["generationContext"]["rulePaths"], ["AGENTS.md"])
            manifest = json.loads(
                (root / ".polaralias" / "repo-context.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("verified", manifest["knowledge"][0])

    def test_closure_assessment_requires_current_explanation_and_documentation_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            self.assertEqual(self.run_cli(root, "start", "--phase", "deliver").returncode, 0)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(root, "closure", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["lanes"]["change"]["status"], "pending")
            self.assertEqual(payload["lanes"]["knowledge"]["status"], "pending")
            self.assertIn("change-explanation-missing", payload["lanes"]["change"]["issues"])
            self.assertIn(
                "documentation-receipt-missing", payload["lanes"]["knowledge"]["issues"]
            )
            closed = self.run_cli(root, "close", "--base", "HEAD")
            self.assertEqual(closed.returncode, 3, closed.stderr or closed.stdout)
            self.assertEqual(json.loads(closed.stdout)["result"], "closure-blocked")

    def test_current_explanation_and_documentation_receipts_clear_closure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            self.assertEqual(self.run_cli(root, "start", "--phase", "deliver").returncode, 0)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )
            concept = root / "docs" / "knowledge" / "workflow.md"
            concept.write_text(
                concept.read_text(encoding="utf-8").replace(
                    "Documentation is assessed before merge.",
                    "Documentation impact is assessed and verified before merge.",
                ),
                encoding="utf-8",
            )
            explained = self.run_cli(
                root,
                "change",
                "explain",
                "--base",
                "HEAD",
                "--summary",
                "The workflow source and its canonical lifecycle now use after mode.",
            )
            self.assertEqual(explained.returncode, 0, explained.stderr or explained.stdout)
            applied = self.run_cli(
                root,
                "documentation",
                "apply",
                "--base",
                "HEAD",
                "--bundle",
                "docs/knowledge",
                "--knowledge",
                "docs/knowledge/workflow.md",
                "--evidence",
                "Reviewed source and concept together.",
                "--reader-query",
                "how is documentation assessed before merge",
            )
            self.assertEqual(applied.returncode, 0, applied.stderr or applied.stdout)

            result = self.run_cli(root, "closure", "assess", "--base", "HEAD")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["lanes"]["change"]["status"], "receipt-current")
            self.assertEqual(payload["lanes"]["knowledge"]["status"], "receipt-current")

            (root / "AGENTS.md").write_text(
                "# Repository rules\n\nCanonical documentation now requires a new review rule.\n",
                encoding="utf-8",
            )
            stale = self.run_cli(root, "closure", "assess", "--base", "HEAD")
            self.assertEqual(stale.returncode, 3, stale.stderr or stale.stdout)
            stale_payload = json.loads(stale.stdout)
            self.assertIn(
                "change-explanation-stale", stale_payload["lanes"]["change"]["issues"]
            )
            self.assertIn(
                "documentation-receipt-stale",
                stale_payload["lanes"]["knowledge"]["issues"],
            )

    def test_apply_refuses_authored_knowledge_that_reader_queries_cannot_find(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_cli(
                root,
                "documentation",
                "apply",
                "--base",
                "HEAD",
                "--bundle",
                "docs/knowledge",
                "--knowledge",
                "docs/knowledge/workflow.md",
                "--evidence",
                "Reviewed source and concept together.",
                "--reader-query",
                "quantum bananas orbital fermentation",
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(
                payload["error"]["code"], "documentation_reader_check_failed"
            )
            self.assertFalse(
                (root / ".engineering-workflow" / "documentation-receipt.json").exists()
            )

    def test_pre_merge_uses_the_documentation_gate_when_a_base_is_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            self.assertEqual(self.run_cli(root, "start", "--phase", "deliver").returncode, 0)
            (root / "src" / "workflow.py").write_text(
                "MODE = 'after'\n", encoding="utf-8"
            )

            result = self.run_pre_merge(root, "--base", "HEAD")

            self.assertEqual(result.returncode, 3, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertIn("documentation", payload)
            self.assertFalse(payload["documentation"]["ready"])


if __name__ == "__main__":
    unittest.main()
