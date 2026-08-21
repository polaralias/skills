from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
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
        "delivery_topology": "parallel",
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


def stacked_manifest() -> dict[str, object]:
    data = manifest()
    data["delivery_topology"] = "stacked"
    data["workstreams"][0]["base_ref"] = "main"
    data["workstreams"][0]["stack_parent"] = None
    data["workstreams"][1]["base_ref"] = "feat/service-contract"
    data["workstreams"][1]["stack_parent"] = "service-contract"
    return data


def exact_review_integration(
    branch: str,
    base_ref: str,
    source_tip: str = "a" * 40,
    repository: str = "example/service",
    state: str = "merged",
) -> dict[str, object]:
    return {
        "state": "durably-integrated",
        "source_tip": source_tip,
        "method": "squash",
        "destination_ref": base_ref,
        "result_tip": "b" * 40,
        "verification": "exact-review-head",
        "verified_at": "2026-08-21T12:00:00Z",
        "review": {
            "provider": "github",
            "repository": repository,
            "id": "42",
            "base_ref": base_ref,
            "head_ref": branch,
            "head_tip": source_tip,
            "state": state,
        },
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

    def test_legacy_manifest_without_topology_remains_valid(self) -> None:
        data = manifest()
        del data["delivery_topology"]

        self.assertEqual(worktree_manifest.validate_manifest(data, self.root), [])

    def test_valid_stacked_manifest_passes(self) -> None:
        self.assertEqual(worktree_manifest.validate_manifest(stacked_manifest(), self.root), [])

    def test_single_managed_workstream_can_be_reconciled(self) -> None:
        data = manifest()
        data["workstreams"] = data["workstreams"][:1]
        data["shared_path_owners"] = {}
        data["integration_order"] = ["service-contract"]

        self.assertEqual(worktree_manifest.validate_manifest(data, self.root), [])

    def test_single_layer_is_not_a_stack(self) -> None:
        data = stacked_manifest()
        data["workstreams"] = data["workstreams"][:1]
        data["shared_path_owners"] = {}
        data["integration_order"] = ["service-contract"]

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("at least two layers" in error for error in errors))

    def test_stack_layer_must_target_parent_branch(self) -> None:
        data = stacked_manifest()
        data["workstreams"][1]["base_ref"] = "main"

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("base_ref must equal" in error for error in errors))

    def test_stack_must_be_linear(self) -> None:
        data = stacked_manifest()
        data["workstreams"].append(
            {
                "slug": "admin-adapter",
                "branch": "feat/admin-adapter",
                "worktree": "repo-worktrees/admin-adapter",
                "owner": "worker-c",
                "status": "planned",
                "base_ref": "feat/service-contract",
                "stack_parent": "service-contract",
                "owned_paths": ["src/admin"],
                "shared_paths": [],
                "depends_on": ["service-contract"],
            }
        )
        data["integration_order"] = ["service-contract", "client-adapter", "admin-adapter"]

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("linear chain" in error for error in errors))

    def test_cleanup_ready_requires_durable_exact_tip_evidence(self) -> None:
        data = manifest()
        source_tip = "a" * 40
        data["workstreams"][0]["integration"] = exact_review_integration("feat/service-contract", "main")
        data["workstreams"][0]["cleanup"] = {
            "state": "ready",
            "verified_tip": "c" * 40,
            "worktree": "clean",
            "remote_branch": "absent",
            "reason": "merged review verified",
        }

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("verified_tip must equal" in error for error in errors))

    def test_cleanup_ready_accepts_matching_durable_evidence(self) -> None:
        data = manifest()
        source_tip = "a" * 40
        data["workstreams"][0]["integration"] = exact_review_integration("feat/service-contract", "main")
        data["workstreams"][0]["cleanup"] = {
            "state": "ready",
            "verified_tip": source_tip,
            "worktree": "clean",
            "remote_branch": "absent",
            "reason": "exact merged review head verified",
        }

        self.assertEqual(worktree_manifest.validate_manifest(data, self.root), [])

    def test_closed_review_cannot_prove_exact_integration(self) -> None:
        data = manifest()
        data["workstreams"][0]["integration"] = exact_review_integration(
            "feat/service-contract", "main", state="closed"
        )

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("requires a merged review" in error for error in errors))

    def test_stacked_reviews_must_use_one_repository(self) -> None:
        data = stacked_manifest()
        data["workstreams"][0]["integration"] = exact_review_integration("feat/service-contract", "main")
        data["workstreams"][1]["integration"] = exact_review_integration(
            "feat/client-adapter", "feat/service-contract", repository="other/service"
        )

        errors = worktree_manifest.validate_manifest(data, self.root)

        self.assertTrue(any("one provider repository" in error for error in errors))

    def test_plan_uses_each_stack_layers_direct_base(self) -> None:
        data = stacked_manifest()
        path = self.root / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = worktree_manifest.plan_command(argparse.Namespace(manifest=str(path)))
        commands = json.loads(output.getvalue())

        self.assertEqual(result, 0)
        self.assertEqual([command["argv"][-1] for command in commands], ["main", "feat/service-contract"])


if __name__ == "__main__":
    unittest.main()
