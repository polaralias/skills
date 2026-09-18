from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"


class HostIntegrationTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_codex_recipe_uses_the_supported_mcp_cli_and_keeps_hooks_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            result = self.run_cli(root, "host", "recipe", "--host", "codex", "--base", "main")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "host-recipe")
            self.assertEqual(payload["host"], "codex")
            self.assertEqual(payload["mcp"]["installCommand"][:4], ["codex", "mcp", "add", "polaralias-engineering-workflow"])
            self.assertEqual(payload["hooks"]["status"], "explicit-git-gate")
            self.assertEqual(payload["hooks"]["base"], "main")
            self.assertEqual(payload["routing"]["path"], "AGENTS.md")

    def test_codex_install_preserves_project_instructions_and_adds_managed_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            agents = root / "AGENTS.md"
            agents.write_text("# Existing rules\n\nKeep this.\n", encoding="utf-8")

            first = self.run_cli(root, "host", "install", "--host", "codex", "--base", "main")
            second = self.run_cli(root, "host", "install", "--host", "codex", "--base", "main")

            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
            self.assertEqual(second.returncode, 0, second.stderr or second.stdout)
            content = agents.read_text(encoding="utf-8")
            self.assertIn("Keep this.", content)
            self.assertEqual(content.count("polaralias-engineering-workflow:start"), 1)
            self.assertIn("engineering.py activate", content)
            self.assertEqual(json.loads(first.stdout)["installed"]["routingInstructions"], "AGENTS.md")

    def test_claude_install_merges_project_mcp_and_installs_a_local_pre_push_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"existing": {"command": "existing"}}}) + "\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "host",
                "install",
                "--host",
                "claude",
                "--base",
                "main",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "host-installed")
            config = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            self.assertIn("existing", config["mcpServers"])
            self.assertIn("polaralias-engineering-workflow", config["mcpServers"])
            self.assertIn("POLARALIAS_EWF_HOME", json.dumps(config))
            hook = root / ".git" / "hooks" / "pre-push"
            self.assertTrue(hook.is_file())
            self.assertIn("Polaralias engineering workflow", hook.read_text(encoding="utf-8"))

    def test_install_refuses_to_replace_an_independently_owned_hook(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            hook = root / ".git" / "hooks" / "pre-push"
            hook.write_text("#!/bin/sh\necho existing\n", encoding="utf-8")

            result = self.run_cli(
                root, "host", "install", "--host", "git", "--base", "main"
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["error"]["code"], "host_hook_owned")
            self.assertEqual(hook.read_text(encoding="utf-8"), "#!/bin/sh\necho existing\n")


if __name__ == "__main__":
    unittest.main()
