from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "worktree_manifest.py"
SPEC = importlib.util.spec_from_file_location("worktree_manifest", MODULE_PATH)
worktree_manifest = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(worktree_manifest)


def manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "task": "delivery-slice",
        "repository_root": "repo",
        "worktree_container": "repo-worktrees",
        "base_revision": "main",
        "integration_destination": "main",
        "authority": {
            "merge": "inherited",
            "push": "inherited",
            "deploy": "inherited",
            "publish": "inherited",
        },
        "workstreams": [
            {
                "slug": "service-contract",
                "branch": "feat/service-contract",
                "worktree": "repo-worktrees/service-contract",
                "owner": "worker-a",
                "status": "planned",
                "owned_paths": ["src/service"],
                "shared_paths": ["docs/integration.md"],
                "depends_on": [],
            },
            {
                "slug": "client-adapter",
                "branch": "feat/client-adapter",
                "worktree": "repo-worktrees/client-adapter",
                "owner": "worker-b",
                "status": "planned",
                "owned_paths": ["src/client"],
                "shared_paths": ["docs/integration.md"],
                "depends_on": ["service-contract"],
            },
        ],
        "shared_path_owners": {"docs/integration.md": "client-adapter"},
        "integration_order": ["service-contract", "client-adapter"],
        "validation": {"parallel_safe": ["targeted tests"], "serial": ["full suite"]},
    }


class WorktreeManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(worktree_manifest.validate_manifest(manifest(), self.root), [])

    def test_nested_container_is_rejected(self) -> None:
        data = manifest()
        data["worktree_container"] = "repo/worktrees"

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("outside repository_root" in error for error in errors))

    def test_owned_parent_child_collision_is_rejected(self) -> None:
        data = manifest()
        data["workstreams"][0]["owned_paths"] = ["src"]

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("owned path overlap" in error for error in errors))

    def test_shared_path_requires_assigned_integration_owner(self) -> None:
        data = manifest()
        data["shared_path_owners"] = {"docs/integration.md": "unknown-worker"}

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("needs an integration owner" in error for error in errors))

    def test_dependency_must_precede_dependant(self) -> None:
        data = manifest()
        data["integration_order"] = ["client-adapter", "service-contract"]

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("must appear earlier" in error for error in errors))

    def test_manifest_cannot_grant_deploy_authority(self) -> None:
        data = manifest()
        data["authority"]["deploy"] = "granted"

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("cannot grant authority" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
