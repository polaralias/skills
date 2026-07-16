from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "repo_setup.py"
SPEC = importlib.util.spec_from_file_location("repo_setup", MODULE_PATH)
repo_setup = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(repo_setup)


class RulesetTests(unittest.TestCase):
    def test_baseline_payload_requires_review_and_blocks_destructive_updates(self) -> None:
        payload = repo_setup.build_ruleset_payload("trunk", "Protect trunk")

        self.assertEqual(payload["conditions"]["ref_name"]["include"], ["refs/heads/trunk"])
        rules = {rule["type"]: rule for rule in payload["rules"]}
        review = rules["pull_request"]["parameters"]
        self.assertEqual(review["required_approving_review_count"], 1)
        self.assertTrue(review["require_code_owner_review"])
        self.assertTrue(review["required_review_thread_resolution"])
        self.assertIn("non_fast_forward", rules)
        self.assertIn("deletion", rules)

    def test_payload_rejects_invalid_approval_count(self) -> None:
        with self.assertRaises(ValueError):
            repo_setup.build_ruleset_payload("main", "Protect", required_approvals=11)

    @patch.object(repo_setup, "run_gh")
    @patch.object(repo_setup, "repository_ruleset_id", return_value=None)
    def test_upsert_creates_when_name_is_absent(self, _lookup, run_gh) -> None:
        run_gh.return_value = {"id": 42}
        payload = repo_setup.build_ruleset_payload("main", "Protect")

        result = repo_setup.upsert_repository_ruleset("sample", "project", payload)

        self.assertEqual(result["id"], 42)
        self.assertIn("POST", run_gh.call_args.args)
        self.assertEqual(run_gh.call_args.kwargs["input_data"], payload)

    @patch.object(repo_setup, "run_gh")
    @patch.object(repo_setup, "repository_ruleset_id", return_value=73)
    def test_upsert_updates_discovered_id(self, _lookup, run_gh) -> None:
        run_gh.return_value = {"id": 73}
        payload = repo_setup.build_ruleset_payload("main", "Protect")

        repo_setup.upsert_repository_ruleset("sample", "project", payload)

        self.assertIn("PATCH", run_gh.call_args.args)
        self.assertTrue(any(str(arg).endswith("rulesets/73") for arg in run_gh.call_args.args))

    def test_verification_allows_api_enrichment(self) -> None:
        expected = repo_setup.build_ruleset_payload(
            "main",
            "Protect",
            bypass_actors=[{"actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
        )
        actual = json.loads(json.dumps(expected))
        actual["bypass_actors"][0]["actor_id"] = None
        actual["rules"][0]["parameters"]["automatic_copilot_code_review_enabled"] = False

        repo_setup.verify_ruleset(actual, expected)


class TemplateTests(unittest.TestCase):
    def test_sync_writes_codeowners_and_repeatable_admin_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                repo_path=directory,
                config=None,
                license="MIT",
                summary="Example repository",
                repo_type=None,
                release_profile=None,
                copyright_holder="Example Maintainer",
                copyright_year="2026",
                owner=None,
                repo=None,
                code_owner=["@maintainer-one", "@maintainer-two"],
                ruleset_name=None,
                required_approvals=None,
                write_repo_admin=True,
            )

            repo_setup.sync_doc_templates(args)

            root = Path(directory)
            codeowners = (root / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
            self.assertIn("@maintainer-one @maintainer-two", codeowners)
            admin = json.loads((root / "repo-admin.json").read_text(encoding="utf-8"))
            self.assertEqual(admin["codeOwners"], ["@maintainer-one", "@maintainer-two"])
            self.assertEqual(admin["requiredApprovals"], 1)


if __name__ == "__main__":
    unittest.main()
