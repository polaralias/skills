from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"


class OkfAdapterCliTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def start(self, root: Path) -> None:
        result = self.run_cli(root, "start")
        self.assertEqual(result.returncode, 0, result.stderr)

    def fake_okf(self, root: Path) -> Path:
        script = root / "fake_okf.py"
        script.write_text(
            "import pathlib, sys\n"
            "marker = pathlib.Path(__file__).with_name('okf-invoked.txt')\n"
            "marker.write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n"
            "if '--version' in sys.argv:\n"
            "    print('okf-tasks 0.1.0')\n"
            "elif 'validate' in sys.argv:\n"
            "    print('OKF Tasks bundle is valid: 1 task, 0 workstreams, 2 links; 0 warnings.')\n"
            "else:\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        return script

    def test_none_mode_check_is_an_explicit_noop_without_cli_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.start(root)

            result = self.run_cli(root, "task", "check", "--cli", str(root / "missing.py"))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "task-tracking-disabled")
            self.assertFalse(payload["executed"])
            self.assertEqual(payload["plan"]["mode"], "none")

    def test_lightweight_mode_records_a_reference_and_validates_through_okf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.start(root)
            (root / "tasks" / "example").mkdir(parents=True)
            (root / "tasks" / "example" / "task.md").write_text("# Example\n", encoding="utf-8")
            fake = self.fake_okf(root)

            configured = self.run_cli(
                root,
                "task",
                "configure",
                "--mode",
                "lightweight",
                "--task-ref",
                "tasks/example/task.md",
            )
            self.assertEqual(configured.returncode, 0, configured.stderr)
            configured_payload = json.loads(configured.stdout)
            self.assertEqual(configured_payload["state"]["task_tracking"]["mode"], "lightweight")
            self.assertIn("task-lifecycle", configured_payload["state"]["active_capabilities"])
            self.assertIn("task-reconciliation", configured_payload["state"]["outstanding_gates"])
            self.assertNotIn("time", configured_payload["plan"]["optionalCapabilities"])
            self.assertNotIn("tracker-sync", configured_payload["plan"]["optionalCapabilities"])

            checked = self.run_cli(root, "task", "check", "--cli", str(fake))

            self.assertEqual(checked.returncode, 0, checked.stderr)
            payload = json.loads(checked.stdout)
            self.assertEqual(payload["result"], "task-bundle-valid")
            self.assertEqual(payload["adapter"]["version"], "0.1.0")
            self.assertIn("validate", payload["command"])
            self.assertIn("--strict", payload["command"])

    def test_full_mode_exposes_optional_features_without_activating_them(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.start(root)

            result = self.run_cli(root, "task", "configure", "--mode", "full")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(
                payload["plan"]["optionalCapabilities"],
                ["workstreams", "effort", "estimates", "tracker-sync", "visualisation", "commit-backfill"],
            )
            self.assertEqual(payload["state"]["active_capabilities"], ["task-lifecycle"])

    def test_task_paths_cannot_escape_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.start(root)

            result = self.run_cli(
                root,
                "task",
                "configure",
                "--mode",
                "lightweight",
                "--task-ref",
                "../outside/task.md",
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["error"]["code"], "task_path_escape")

    def test_reconfiguration_preserves_a_task_reference_and_refuses_silent_reduction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.start(root)
            (root / "tasks" / "example").mkdir(parents=True)
            (root / "tasks" / "example" / "task.md").write_text("# Example\n", encoding="utf-8")
            first = self.run_cli(
                root,
                "task",
                "configure",
                "--mode",
                "lightweight",
                "--task-ref",
                "tasks/example/task.md",
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            expanded = self.run_cli(root, "task", "configure", "--mode", "full")
            self.assertEqual(expanded.returncode, 0, expanded.stderr)
            self.assertEqual(
                json.loads(expanded.stdout)["state"]["task_tracking"]["task_ref"],
                "tasks/example/task.md",
            )

            reduced = self.run_cli(root, "task", "configure", "--mode", "none")
            self.assertEqual(reduced.returncode, 2)
            self.assertEqual(
                json.loads(reduced.stdout)["error"]["code"],
                "task_mode_reduction_requires_force",
            )


if __name__ == "__main__":
    unittest.main()
