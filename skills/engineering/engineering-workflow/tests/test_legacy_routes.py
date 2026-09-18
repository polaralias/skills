from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"


class LegacyRouteTests(unittest.TestCase):
    EXPECTED = {
        "EWO": "lifecycle",
        "RDS": "understand",
        "QTK": "understand",
        "RKE": "understand",
        "DDD": "design",
        "RTL": "tasks",
        "WTC": "parallel-delivery",
        "RCC": "close",
        "RSA": "close",
        "LHO": "checkpoint",
        "LPK": "resume",
        "RPF": "publication",
        "TPU": "tracker-sync",
        "TPW": "qa-planning",
        "RST": "repository-setup",
    }

    def test_every_legacy_alias_has_one_deterministic_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for alias, destination in self.EXPECTED.items():
                with self.subTest(alias=alias):
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT),
                            "legacy",
                            "route",
                            alias,
                            "--root",
                            str(root),
                        ],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["result"], "legacy-route")
                    self.assertEqual(payload["alias"], alias)
                    self.assertEqual(payload["destination"], destination)
                    self.assertNotIn(alias, payload["command"])

    def test_legacy_full_name_routes_case_insensitively(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "legacy",
                    "route",
                    "Repo-Dissection",
                    "--root",
                    temp_dir,
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["alias"], "RDS")
            self.assertEqual(payload["destination"], "understand")

    def test_unknown_legacy_name_is_rejected_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "legacy",
                    "route",
                    "made-up-skill",
                    "--root",
                    temp_dir,
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "legacy-route-unknown")


if __name__ == "__main__":
    unittest.main()
