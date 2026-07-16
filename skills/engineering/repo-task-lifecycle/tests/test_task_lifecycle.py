from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "task_lifecycle.py"
SPEC = importlib.util.spec_from_file_location("task_lifecycle", MODULE_PATH)
task_lifecycle = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(task_lifecycle)


class TaskLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def init_task(self, slug: str = "improve-search") -> None:
        task_lifecycle.init_task(argparse.Namespace(
            root=str(self.root),
            slug=slug,
            title="Improve search behavior",
            owner="maintainer",
        ))

    def add_workstream(self, slug: str, branch: str) -> None:
        task_lifecycle.add_workstream(argparse.Namespace(
            root=str(self.root),
            task="improve-search",
            slug=slug,
            title=f"Deliver {slug}",
            owner=f"owner-{slug}",
            branch=branch,
        ))

    def test_init_creates_task_and_generated_index(self) -> None:
        self.init_task()

        record = task_lifecycle.parse_frontmatter(self.root / "tasks" / "improve-search" / "task.md")
        self.assertEqual(record["status"], "proposed")
        self.assertIn("Improve search behavior", (self.root / "tasks" / "index.md").read_text(encoding="utf-8"))
        self.assertEqual(task_lifecycle.validate(self.root), [])

    def test_invalid_slug_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            task_lifecycle.valid_slug("External-104")

    def test_duplicate_active_branch_is_invalid(self) -> None:
        self.init_task()
        self.add_workstream("query-layer", "feat/search")
        self.add_workstream("result-view", "feat/search")

        errors = task_lifecycle.validate(self.root)

        self.assertTrue(any("active branch also used" in error for error in errors))

    def test_invalid_transition_requires_explicit_force(self) -> None:
        self.init_task()
        path = self.root / "tasks" / "improve-search" / "task.md"

        with self.assertRaises(SystemExit):
            task_lifecycle.transition(path, "done", force=False)

    def test_task_cannot_finish_with_active_workstream(self) -> None:
        self.init_task()
        self.add_workstream("query-layer", "feat/search-query")
        task_path = self.root / "tasks" / "improve-search" / "task.md"
        task_lifecycle.replace_field(task_path, "status", "validation")

        with self.assertRaises(SystemExit):
            task_lifecycle.set_status(argparse.Namespace(
                root=str(self.root),
                task="improve-search",
                workstream=None,
                status="done",
                force=False,
            ))

    def test_stale_index_is_detected_and_rebuilt(self) -> None:
        self.init_task()
        index = self.root / "tasks" / "index.md"
        index.write_text("stale\n", encoding="utf-8")
        self.assertTrue(any("stale" in error for error in task_lifecycle.validate(self.root)))

        task_lifecycle.build_index(self.root)

        self.assertEqual(task_lifecycle.validate(self.root), [])


if __name__ == "__main__":
    unittest.main()
