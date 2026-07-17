from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "task_lifecycle.py"


class CompatibilityEntrypointTests(unittest.TestCase):
    def test_legacy_init_and_workstream_commands_create_valid_okf_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                [
                    "python",
                    str(SCRIPT),
                    "init",
                    "--root",
                    str(root),
                    "--slug",
                    "legacy-task",
                    "--title",
                    "Legacy task",
                    "--owner",
                    "agent",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "python",
                    str(SCRIPT),
                    "add-workstream",
                    "--root",
                    str(root),
                    "--task",
                    "legacy-task",
                    "--slug",
                    "delivery",
                    "--title",
                    "Deliver result",
                    "--owner",
                    "agent",
                    "--branch",
                    "feat/legacy-delivery",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            task = (root / "tasks" / "legacy-task" / "task.md").read_text(encoding="utf-8")
            workstream = (root / "tasks" / "legacy-task" / "workstreams" / "delivery.md").read_text(encoding="utf-8")
            self.assertIn("type: Task", task)
            self.assertIn("description: Legacy task", task)
            self.assertIn("type: Workstream", workstream)
            self.assertIn("description: Deliver result", workstream)


if __name__ == "__main__":
    unittest.main()
