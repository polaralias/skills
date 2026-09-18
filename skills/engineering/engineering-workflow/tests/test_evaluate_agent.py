from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_agent.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("evaluate_agent", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class AgentEvaluationTests(unittest.TestCase):
    def test_checked_in_corpus_covers_activation_non_activation_and_boundary(self) -> None:
        corpus = Path(__file__).parent / "evals" / "agent-behaviour.json"
        cases = MODULE._load_cases(corpus)
        self.assertEqual({case["category"] for case in cases}, {"activation", "non-activation", "boundary"})

    def test_grader_combines_activation_response_and_artifact_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".engineering-workflow").mkdir()
            (root / ".engineering-workflow" / "state.json").write_text(
                json.dumps({"activation": {"activatedAt": "2026-09-18T00:00:00Z", "dirtyPaths": []}}),
                encoding="utf-8",
            )
            (root / "README.md").write_text("# Demo\n\n## Scope\n", encoding="utf-8")
            case = {
                "id": "example", "category": "activation", "expectWorkflowState": True,
                "finalContains": ["proof"], "filesContain": {"README.md": "Scope"},
                "forbiddenPaths": ["secret.txt"],
            }
            report = MODULE._grade(case, root, "proof", 0)
            self.assertTrue(report["passed"])
            self.assertTrue(all(check["passed"] for check in report["checks"]))

    def test_grader_reports_missing_artifact_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            report = MODULE._grade(
                {"id": "missing", "category": "boundary", "filesContain": {"missing.md": "text"}},
                Path(temporary),
                "",
                0,
            )
            self.assertFalse(report["passed"])
            self.assertFalse(next(check for check in report["checks"] if check["name"] == "file-contains:missing.md")["passed"])

    def test_timeout_diagnostics_are_bounded(self) -> None:
        diagnostics = MODULE._bounded_diagnostics("a" * 5_000, "b" * 6_000)
        self.assertEqual(len(diagnostics["stdoutTail"]), 4_000)
        self.assertEqual(len(diagnostics["stderrTail"]), 4_000)

    def test_grader_proves_activation_preceded_named_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_dir = root / ".engineering-workflow"
            state_dir.mkdir()
            (state_dir / "state.json").write_text(
                json.dumps({"activation": {"activatedAt": "2026-09-18T00:00:00Z", "dirtyPaths": []}}),
                encoding="utf-8",
            )
            report = MODULE._grade(
                {
                    "id": "ordered",
                    "category": "activation",
                    "expectWorkflowState": True,
                    "mustActivateBefore": ["calculator.py"],
                },
                root,
                "",
                0,
            )
            self.assertTrue(report["passed"])
            self.assertTrue(next(check for check in report["checks"] if check["name"] == "workflow-activated-before-mutation")["passed"])

    def test_case_cleanup_is_best_effort_and_preserves_the_grade(self) -> None:
        case = {
            "id": "cleanup",
            "category": "non-activation",
            "prompt": "Explain the fixture.",
            "setup": {},
            "expectWorkflowState": False,
        }
        completed = type("Completed", (), {"returncode": 0, "communicate": lambda self, timeout: ("done", "")})()
        original_rmtree = MODULE.shutil.rmtree
        cleanup_calls = []

        def cleanup(path, **kwargs):
            cleanup_calls.append(kwargs)
            return original_rmtree(path, **kwargs)

        with (
            patch.object(MODULE.subprocess, "run", return_value=type("GitResult", (), {"returncode": 0})()),
            patch.object(MODULE.subprocess, "Popen", return_value=completed),
            patch.object(MODULE.shutil, "rmtree", side_effect=cleanup),
        ):
            report = MODULE._run_case(case, "codex", None, 1)
        self.assertTrue(report["passed"])
        self.assertTrue(cleanup_calls[0]["ignore_errors"])


if __name__ == "__main__":
    unittest.main()
