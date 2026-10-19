from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "sync_okf_task_skill.py"
SPEC = importlib.util.spec_from_file_location("sync_okf_task_skill", SCRIPT)
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


class UpstreamSynchronizationTests(unittest.TestCase):
    def test_pinned_commit_rejects_changed_bytes_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "producer"
            source.mkdir()
            subprocess.run(["git", "init", str(source)], check=True, capture_output=True)
            (source / "VERSION").write_bytes(b"0.1.0\n")
            origin = source / "runtime.py"
            origin.write_bytes(b"committed runtime\n")
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "fixture"], check=True, capture_output=True)
            commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
            target = root / "skills/engineering/repo-task-lifecycle"
            def selected(producer):
                return {"runtime.py": ("runtime.py", origin.read_bytes())}
            with patch.object(sync, "ROOT", root), patch.object(sync, "TARGET", target), patch.object(sync, "resources", selected):
                self.assertEqual([], sync.synchronize(source, False, commit))
                manifest_path = target / "OKF_UPSTREAM.json"
                before = manifest_path.read_bytes()
                self.assertEqual(commit, json.loads(before)["source_commit"])
                origin.write_bytes(b"uncommitted replacement\n")
                with self.assertRaisesRegex(ValueError, "differs from pinned commit"):
                    sync.synchronize(source, False, commit)
                self.assertEqual(before, manifest_path.read_bytes())
                self.assertEqual(b"committed runtime\n", (target / "runtime.py").read_bytes())

    def test_check_detects_both_producer_changes_and_local_drift_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "producer"
            source.mkdir()
            (source / "VERSION").write_text("0.1.0\n")
            origin = source / "runtime.py"
            origin.write_bytes(b"current runtime\n")
            target = root / "skills/engineering/repo-task-lifecycle"
            def selected(producer):
                return {"scripts/okf_tasks.py": ("runtime.py", (producer / "runtime.py").read_bytes())}
            with patch.object(sync, "ROOT", root), patch.object(sync, "TARGET", target), patch.object(sync, "resources", selected):
                self.assertEqual([], sync.synchronize(source, False))
                self.assertEqual([], sync.synchronize(source, True))
                manifest = (target / "OKF_UPSTREAM.json").read_bytes()
                resource = target / "scripts/okf_tasks.py"
                resource.write_bytes(b"obsolete installed runtime\n")
                self.assertEqual(["scripts/okf_tasks.py"], sync.synchronize(source, True))
                self.assertEqual(b"obsolete installed runtime\n", resource.read_bytes())
                resource.write_bytes(origin.read_bytes())
                origin.write_bytes(b"same version, changed producer\n")
                self.assertEqual({"scripts/okf_tasks.py", "OKF_UPSTREAM.json"}, set(sync.synchronize(source, True)))
                self.assertEqual(manifest, (target / "OKF_UPSTREAM.json").read_bytes())
                self.assertEqual([], sync.synchronize(source, False))
                self.assertEqual(origin.read_bytes(), resource.read_bytes())

    def test_obsolete_producer_resources_require_review_and_preserve_integration_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "producer"
            source.mkdir()
            (source / "VERSION").write_text("0.1.0\n")
            (source / "runtime.py").write_bytes(b"runtime\n")
            target = root / "skills/engineering/repo-task-lifecycle"
            with patch.object(sync, "ROOT", root), patch.object(sync, "TARGET", target), patch.object(sync, "resources", return_value={"runtime.py": ("runtime.py", b"runtime\n")}):
                self.assertEqual([], sync.synchronize(source, False))
                guidance = target / "SKILL.md"
                guidance.write_bytes(b"independently authored integration\n")
                old = target / "obsolete.py"
                old.write_bytes(b"obsolete runtime\n")
                manifest_path = target / "OKF_UPSTREAM.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["resources"]["obsolete.py"] = {}
                manifest_path.write_text(json.dumps(manifest))
                before = manifest_path.read_bytes()
                with self.assertRaisesRegex(ValueError, "obsolete producer resources"):
                    sync.synchronize(source, False)
                self.assertEqual(before, manifest_path.read_bytes())
                self.assertEqual(b"obsolete runtime\n", old.read_bytes())
                self.assertEqual(b"independently authored integration\n", guidance.read_bytes())


if __name__ == "__main__":
    unittest.main()
