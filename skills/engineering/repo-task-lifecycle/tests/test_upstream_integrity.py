"""Check all reviewed producer bytes, including dependencies and fixtures."""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UpstreamIntegrityTests(unittest.TestCase):
    def test_all_resources_match_reviewed_snapshot_without_escaping_package(self) -> None:
        manifest = json.loads((ROOT / "OKF_UPSTREAM.json").read_text(encoding="utf-8"))
        for name, identity in manifest["resources"].items():
            with self.subTest(resource=name):
                path = (ROOT / name).resolve(strict=True)
                self.assertTrue(path.is_relative_to(ROOT.resolve()))
                self.assertEqual(identity["package_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
