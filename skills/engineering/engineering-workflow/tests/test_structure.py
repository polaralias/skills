from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"


class StructuralContextTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def repository(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "a.py").write_text(
            "def leaf(value: int) -> int:\n"
            "    return value + 1\n\n"
            "def middle(value: int) -> int:\n"
            "    return leaf(value)\n",
            encoding="utf-8",
        )
        (root / "b.py").write_text(
            "from a import middle\n\n"
            "def top(value: int) -> int:\n"
            "    return middle(value)\n",
            encoding="utf-8",
        )
        (root / "web.js").write_text(
            "export function renderCard(title) {\n"
            "  return formatTitle(title);\n"
            "}\n\n"
            "const formatTitle = (title) => title.trim();\n",
            encoding="utf-8",
        )

    def test_file_api_returns_signatures_without_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(root, "structure", "file-api", "a.py")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "file-api")
            self.assertEqual(payload["parser"], "tree-sitter")
            self.assertEqual(payload["analysisMode"], "parser")
            self.assertEqual([item["name"] for item in payload["symbols"]], ["leaf", "middle"])
            self.assertEqual(payload["symbols"][0]["signature"], "def leaf(value: int) -> int")
            self.assertNotIn("return value", json.dumps(payload))

    def test_trace_finds_transitive_callers_from_live_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(
                root, "structure", "trace", "leaf", "--direction", "in", "--depth", "2"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            traced = payload["traces"][0]
            self.assertEqual([item["name"] for item in traced["nodes"]], ["middle", "top"])

    def test_import_binding_disambiguates_duplicate_symbol_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            (root / "duplicate.py").write_text(
                "def middle(value: int) -> int:\n    return value - 1\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                root, "structure", "trace", "a.py::middle", "--direction", "in"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual([item["name"] for item in payload["traces"][0]["nodes"]], ["top"])

    def test_change_impact_reports_callers_not_a_decorative_graph(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(
                root, "structure", "impact", "--changed", "a.py", "--depth", "2"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["changedSymbolCount"], 2)
            self.assertEqual([item["name"] for item in payload["affectedCallers"]], ["top"])

    def test_repository_map_prioritises_dependency_hubs_and_supports_javascript(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(root, "structure", "map", "--limit", "10")
            js_api = self.run_cli(root, "structure", "file-api", "web.js")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["sourceFileCount"], 3)
            self.assertGreaterEqual(payload["parserCatalogCount"], 300)
            self.assertGreaterEqual(payload["resolvedEdgeCount"], 3)
            self.assertEqual(payload["hubs"][0]["name"], "middle")
            self.assertEqual(js_api.returncode, 0, js_api.stderr)
            self.assertEqual(
                [item["name"] for item in json.loads(js_api.stdout)["symbols"]],
                ["renderCard", "formatTitle"],
            )

    def test_file_api_supports_go_rust_csharp_and_tsx(self) -> None:
        fixtures = {
            "service.go": ("package service\nfunc Run(value int) int { return value }\n", "Run"),
            "service.rs": ("pub fn run(value: i32) -> i32 { value }\n", "run"),
            "Service.cs": ("public class Service { public int Run(int value) { return value; } }\n", "Service"),
            "Card.tsx": ("export const Card = ({title}: Props) => <div>{title}</div>;\n", "Card"),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name, (source, expected) in fixtures.items():
                (root / name).write_text(source, encoding="utf-8")
                result = self.run_cli(root, "structure", "file-api", name)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["parser"], "tree-sitter")
                self.assertIn(expected, [item["name"] for item in payload["symbols"]])

    def test_unknown_language_returns_bounded_agent_review_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "service.weirdcode").write_text("component Example { invoke worker }\n", encoding="utf-8")

            result = self.run_cli(root, "structure", "file-api", "service.weirdcode")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["parser"], "agent-review")
            self.assertEqual(payload["analysisMode"], "agent-review-required")
            self.assertTrue(payload["chunks"])
            self.assertIn("uncertainties", payload["reviewSchema"])
            self.assertEqual(len(payload["sourceDigest"]), 64)

    def test_agent_review_evidence_feeds_file_api_and_trace_until_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)
            target = root / "service.weirdcode"
            target.write_text("component Example { invoke leaf }\n", encoding="utf-8")
            packet = json.loads(self.run_cli(root, "structure", "review", "service.weirdcode").stdout)
            review = {
                "sourceDigest": packet["sourceDigest"],
                "symbols": [{
                    "name": "Example", "kind": "component", "startLine": 1,
                    "endLine": 1, "signature": "component Example", "confidence": "medium",
                }],
                "dependencies": [{
                    "from": "Example", "to": "leaf", "confidence": "medium", "evidenceLine": 1,
                }],
                "uncertainties": ["Invocation syntax has no installed grammar."],
            }
            (root / "review.json").write_text(json.dumps(review), encoding="utf-8")

            recorded = self.run_cli(root, "structure", "review-apply", "service.weirdcode", "--review-file", "review.json")
            api = self.run_cli(root, "structure", "file-api", "service.weirdcode")
            traced = self.run_cli(root, "structure", "trace", "leaf", "--direction", "in")

            self.assertEqual(recorded.returncode, 0, recorded.stderr)
            api_payload = json.loads(api.stdout)
            self.assertEqual(api_payload["analysisMode"], "agent-reviewed")
            self.assertEqual(api_payload["symbols"][0]["origin"], "agent-review")
            self.assertEqual(api_payload["symbols"][0]["confidence"], "medium")
            self.assertIn("Example", [item["name"] for item in json.loads(traced.stdout)["traces"][0]["nodes"]])

            target.write_text("component Changed { invoke leaf }\n", encoding="utf-8")
            stale = json.loads(self.run_cli(root, "structure", "file-api", "service.weirdcode").stdout)
            self.assertEqual(stale["analysisMode"], "agent-review-required")

    def test_agent_review_rejects_stale_or_unbounded_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "service.weirdcode").write_text("component Example {}\n", encoding="utf-8")
            review = {
                "sourceDigest": "0" * 64,
                "symbols": [],
                "dependencies": [],
                "uncertainties": [],
            }
            (root / "review.json").write_text(json.dumps(review), encoding="utf-8")

            result = self.run_cli(root, "structure", "review-apply", "service.weirdcode", "--review-file", "review.json")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "structure_review_stale")

    def test_structure_cache_reuses_unchanged_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            cold = self.run_cli(root, "structure", "map")
            warm = self.run_cli(root, "structure", "map")

            self.assertEqual(cold.returncode, 0, cold.stderr)
            self.assertEqual(warm.returncode, 0, warm.stderr)
            self.assertGreater(json.loads(cold.stdout)["cache"]["misses"], 0)
            self.assertEqual(json.loads(warm.stdout)["cache"]["misses"], 0)
            self.assertEqual(json.loads(warm.stdout)["cache"]["hits"], 3)

    def test_paths_cannot_escape_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(root, "structure", "file-api", "../outside.py")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                json.loads(result.stdout)["error"]["code"], "structure_path_escape"
            )

    def test_agent_review_cannot_read_secret_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text("TOKEN=secret\n", encoding="utf-8")

            result = self.run_cli(root, "structure", "review", ".env")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "structure_path_excluded")
            self.assertNotIn("secret", result.stdout)

    def test_checked_in_benchmark_has_full_expected_recall(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "structural-benchmark" / "repository"

        result = self.run_cli(fixture, "structure", "benchmark", "--corpus", "corpus.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "structure-benchmarked")
        self.assertEqual(payload["caseCount"], 14)
        self.assertEqual(payload["meanRecall"], 1.0)
        self.assertEqual(payload["meanPrecision"], 1.0)
        self.assertEqual(payload["fullRecallCases"], 14)
        self.assertLess(payload["outputCharacters"], 20_000)

    def test_search_groups_matches_by_symbol_and_ranks_coupled_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(root, "structure", "search", "return")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "structure-searched")
            self.assertEqual(payload["matchCount"], 4)
            self.assertEqual(payload["matches"][0]["symbol"]["name"], "middle")
            self.assertGreater(payload["matches"][0]["coupling"], 0)

    def test_search_rejects_invalid_regex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.repository(root)

            result = self.run_cli(root, "structure", "search", "[")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                json.loads(result.stdout)["error"]["code"], "structure_pattern_invalid"
            )


if __name__ == "__main__":
    unittest.main()
