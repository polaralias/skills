from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_START = ROOT / "scripts" / "hooks" / "session_start.py"
PRE_COMPACTION = ROOT / "scripts" / "hooks" / "pre_compaction.py"
PRE_MERGE = ROOT / "scripts" / "hooks" / "pre_merge.py"


class WorkflowHookTests(unittest.TestCase):
    def run_hook(self, script: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), "--root", str(root), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_session_start_is_idempotent_and_preserves_existing_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = self.run_hook(SESSION_START, root)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = root / ".engineering-workflow" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["outstanding_gates"] = ["implementation-validation"]
            state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

            second = self.run_hook(SESSION_START, root)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(second.stdout)["result"], "activated-existing")
            preserved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(preserved["outstanding_gates"], ["implementation-validation"])

    def test_pre_compaction_records_only_the_supplied_restart_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.assertEqual(self.run_hook(SESSION_START, root).returncode, 0)

            result = self.run_hook(
                PRE_COMPACTION,
                root,
                "--summary",
                "Adapter tests are green.",
                "--next-action",
                "Run package validation.",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            checkpoint = payload["state"]["continuity"]["checkpoint"]
            self.assertEqual(checkpoint["summary"], "Adapter tests are green.")
            self.assertEqual(checkpoint["next_action"], "Run package validation.")

    def test_pre_merge_blocks_when_closure_lanes_are_outstanding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            started = self.run_hook(SESSION_START, root)
            self.assertEqual(started.returncode, 0, started.stderr)
            state_path = root / ".engineering-workflow" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["outstanding_gates"] = ["implementation-validation"]
            state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

            result = self.run_hook(PRE_MERGE, root)

            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)["result"], "closure-blocked")


if __name__ == "__main__":
    unittest.main()
