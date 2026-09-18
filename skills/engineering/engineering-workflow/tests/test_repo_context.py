from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "engineering.py"
BENCHMARK_ROOT = Path(__file__).resolve().parent / "fixtures" / "retrieval-benchmark" / "repository"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repo_context


class RepoContextCliTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_find_auto_indexes_and_ranks_relevant_repository_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "src" / "credentials.py").write_text(
                "def hydrate_github_credentials(token):\n"
                "    return {'Authorization': f'Bearer {token}'}\n",
                encoding="utf-8",
            )
            (root / "src" / "billing.py").write_text(
                "def calculate_invoice_total(items):\n"
                "    return sum(item.price for item in items)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "find",
                "where are GitHub credentials hydrated?",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "context-found")
            self.assertTrue(payload["refreshed"])
            self.assertEqual(payload["results"][0]["path"], "src/credentials.py")
            self.assertGreater(payload["results"][0]["score"], 0)
            self.assertIn("term-match", payload["results"][0]["reasons"])
            self.assertEqual(payload["results"][0]["startLine"], 1)
            self.assertGreaterEqual(payload["results"][0]["endLine"], 2)
            self.assertIn("hydrate_github_credentials", payload["results"][0]["snippet"])
            self.assertTrue(payload["indexRevision"])

    def test_find_skips_git_visible_paths_that_cannot_be_statted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readable = root / "architecture.md"
            unreadable = root / "linked-skill"
            readable.write_text(
                "# Architecture\n\nRepository knowledge is retrieved here.\n",
                encoding="utf-8",
            )
            original_is_file = Path.is_file

            def guarded_is_file(path: Path) -> bool:
                if path == unreadable:
                    raise PermissionError("simulated inaccessible reparse point")
                return original_is_file(path)

            with (
                patch.object(
                    repo_context,
                    "git_visible_files",
                    return_value=[readable, unreadable],
                ),
                patch.object(Path, "is_file", guarded_is_file),
            ):
                payload = repo_context.find_context(root, "repository knowledge")

            self.assertEqual(payload["result"], "context-found")
            self.assertEqual(payload["results"][0]["path"], "architecture.md")
            self.assertEqual(payload["inaccessibleFilesSkipped"], ["linked-skill"])

    def test_check_reports_generated_index_freshness_without_claiming_knowledge_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "# Service\n\nThe gateway hydrates GitHub credentials.\n",
                encoding="utf-8",
            )
            found = self.run_cli(root, "context", "find", "GitHub credentials")
            self.assertEqual(found.returncode, 0, found.stderr)

            result = self.run_cli(root, "context", "check")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "context-checked")
            self.assertTrue(payload["indexFresh"])
            self.assertFalse(payload["refreshed"])
            self.assertEqual(payload["indexedFiles"], 1)
            self.assertEqual(payload["knowledgeFreshness"], "unknown")
            self.assertEqual(payload["candidateKnowledgeReviews"], [])
            self.assertEqual(payload["warnings"], [])

    def test_find_excludes_git_ignored_binary_and_secret_material(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(
                ["git", "init", "--quiet", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            (root / ".gitignore").write_text("generated/\n", encoding="utf-8")
            (root / "generated").mkdir()
            (root / "generated" / "credentials.md").write_text(
                "GitHub credentials are generated here.", encoding="utf-8"
            )
            (root / ".env").write_text(
                "GITHUB_TOKEN=do-not-index-this-value\n", encoding="utf-8"
            )
            (root / "secrets.bin").write_bytes(b"github credentials\x00private")
            (root / "credentials.md").write_text(
                "GitHub credentials are hydrated by the gateway client.",
                encoding="utf-8",
            )

            result = self.run_cli(root, "context", "find", "GitHub credentials")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            paths = [item["path"] for item in payload["results"]]
            self.assertIn("credentials.md", paths)
            self.assertNotIn("generated/credentials.md", paths)
            self.assertNotIn(".env", paths)
            self.assertNotIn("secrets.bin", paths)

    def test_find_returns_the_relevant_markdown_section_not_the_whole_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "architecture.md").write_text(
                "# Platform\n\nGeneral platform overview.\n\n"
                "## Billing\n\nInvoices and payment settlement.\n\n"
                "## Credential hydration\n\n"
                "The GitHub gateway reads the token registry and hydrates request headers.\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "find",
                "where does the GitHub gateway hydrate credentials?",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            top = payload["results"][0]
            self.assertEqual(top["path"], "architecture.md")
            self.assertEqual(top["startLine"], 9)
            self.assertEqual(top["symbol"], "Credential hydration")
            self.assertNotIn("Invoices", top["snippet"])

    def test_long_markdown_sections_are_bounded_and_excerpt_the_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            filler = "\n".join(f"ordinary line {index}" for index in range(240))
            (root / "architecture.md").write_text(
                "# Platform\n\n## Runtime\n\n" + filler + "\nrarequasar handshake boundary\n",
                encoding="utf-8",
            )
            payload = repo_context.find_context(root, "rarequasar handshake")
            top = payload["results"][0]
            self.assertEqual(top["symbol"], "Runtime")
            self.assertIn("rarequasar handshake", top["snippet"])
            self.assertLessEqual(len(top["snippet"]), 2002)
            self.assertGreater(top["startLine"], 100)

    def test_tree_sitter_symbols_drive_retrieval_chunks_for_go(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "worker.go").write_text(
                "package demo\n\nfunc ReconcileLedger(entry string) string {\n    return entry\n}\n",
                encoding="utf-8",
            )
            payload = repo_context.find_context(root, "ReconcileLedger")
            self.assertEqual(payload["results"][0]["path"], "worker.go")
            self.assertEqual(payload["results"][0]["symbol"], "ReconcileLedger")
            self.assertIn("exact-identifier", payload["results"][0]["reasons"])

    def test_lexical_results_are_fused_with_one_hop_structural_neighbours(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "service.py").write_text(
                "def target_operation(value: int) -> int:\n"
                "    return value + 1\n\n"
                "def caller_operation(value: int) -> int:\n"
                "    return target_operation(value)\n",
                encoding="utf-8",
            )
            payload = repo_context.find_context(root, "target_operation", limit=4)
            caller = next(item for item in payload["results"] if item["symbol"] == "caller_operation")
            self.assertIn("structural-neighbour", caller["reasons"])
            self.assertEqual(payload["ranking"], "bm25f+structural+okf")

    def test_native_parser_failure_cannot_terminate_retrieval_fusion(self) -> None:
        ranked = [
            {
                "documentId": 0,
                "path": "unsafe.py",
                "startLine": 1,
                "endLine": 2,
                "kind": "code",
                "symbol": "unsafe",
                "score": 3.0,
                "reasons": ["term-match", "bm25f", "exact-identifier"],
                "snippet": "def unsafe(): pass",
            }
        ]
        failed = subprocess.CompletedProcess([], 3221225477, stdout="", stderr="native crash")
        with patch.object(repo_context.subprocess, "run", return_value=failed):
            results, warnings = repo_context.apply_structural_fusion(Path.cwd(), "unsafe", ranked, [])
        self.assertEqual(results[0]["path"], "unsafe.py")
        self.assertIn("structural-fusion-unavailable", warnings[0])

    def test_index_persists_fielded_postings_and_results_are_path_diverse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "one.md").write_text(
                "# First\n\nshared signal\n\n## Again\n\nshared signal repeated\n",
                encoding="utf-8",
            )
            (root / "two.md").write_text("# Second\n\nshared signal\n", encoding="utf-8")
            payload = repo_context.find_context(root, "shared signal", limit=2)
            self.assertEqual({item["path"] for item in payload["results"]}, {"one.md", "two.md"})
            index = json.loads((root / ".engineering-workflow" / "cache" / "context-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["schemaVersion"], 6)
            self.assertIn("shared", index["search"]["postings"])
            self.assertIn("averageFieldLengths", index["search"])

    def test_find_scope_narrows_results_and_rejects_repository_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / "src" / "gateway.py").write_text(
                "def hydrate_credentials():\n    return 'github token'\n",
                encoding="utf-8",
            )
            (root / "docs" / "gateway.md").write_text(
                "# Gateway\n\nGitHub credentials are hydrated here.\n",
                encoding="utf-8",
            )

            narrowed = self.run_cli(
                root,
                "context",
                "find",
                "GitHub credentials",
                "--scope",
                "src",
            )
            escaped = self.run_cli(
                root,
                "context",
                "find",
                "GitHub credentials",
                "--scope",
                "../outside",
            )

            self.assertEqual(narrowed.returncode, 0, narrowed.stderr)
            narrowed_payload = json.loads(narrowed.stdout)
            self.assertTrue(narrowed_payload["results"])
            self.assertTrue(
                all(item["path"].startswith("src/") for item in narrowed_payload["results"])
            )
            self.assertEqual(escaped.returncode, 2)
            escaped_payload = json.loads(escaped.stdout)
            self.assertEqual(escaped_payload["result"], "context-error")
            self.assertEqual(escaped_payload["error"]["code"], "context_scope_escape")

    def test_check_reports_changed_and_deleted_files_refreshed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            changed = root / "changed.py"
            deleted = root / "deleted.py"
            changed.write_text("def old_name():\n    return 1\n", encoding="utf-8")
            deleted.write_text("def removed():\n    return 2\n", encoding="utf-8")
            initial = self.run_cli(root, "context", "find", "old name")
            self.assertEqual(initial.returncode, 0, initial.stderr)

            changed.write_text(
                "def new_gateway_name():\n    return 'github'\n", encoding="utf-8"
            )
            deleted.unlink()
            result = self.run_cli(root, "context", "check")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["refreshed"])
            self.assertEqual(payload["changedFilesRefreshed"], 1)
            self.assertEqual(payload["deletedFilesRemoved"], 1)

    def test_unchanged_refresh_reuses_cached_documents_without_rehashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "gateway.py").write_text(
                "def hydrate_credentials():\n    return 'github'\n", encoding="utf-8"
            )
            initial = self.run_cli(root, "context", "find", "credentials")
            self.assertEqual(initial.returncode, 0, initial.stderr)

            result = self.run_cli(root, "context", "check")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["refreshed"])
            self.assertEqual(payload["hashedFiles"], 0)
            self.assertEqual(payload["reusedFiles"], 1)

    def test_benchmark_reports_repeatable_retrieval_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / "src" / "credential_gateway.py").write_text(
                "def hydrate_github_gateway_credentials():\n"
                "    return token_registry.get('github')\n",
                encoding="utf-8",
            )
            (root / "src" / "invoice.py").write_text(
                "def total_invoice(lines):\n    return sum(lines)\n", encoding="utf-8"
            )
            (root / "docs" / "architecture.md").write_text(
                "# Request authentication\n\n"
                "The credential gateway hydrates GitHub request headers.\n",
                encoding="utf-8",
            )
            corpus = {
                "schemaVersion": 1,
                "queries": [
                    {
                        "id": "exact-symbol",
                        "query": "hydrateGithubGatewayCredentials",
                        "relevantPaths": ["src/credential_gateway.py"],
                    },
                    {
                        "id": "architecture",
                        "query": "how are GitHub requests authenticated?",
                        "relevantPaths": ["docs/architecture.md"],
                    },
                ],
            }
            (root / "benchmark.json").write_text(
                json.dumps(corpus), encoding="utf-8"
            )

            result = self.run_cli(
                root, "context", "benchmark", "--corpus", "benchmark.json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "context-benchmarked")
            self.assertEqual(payload["queryCount"], 2)
            self.assertEqual(payload["recallAt1"], 1.0)
            self.assertEqual(payload["recallAt5"], 1.0)
            self.assertEqual(payload["recallAt10"], 1.0)
            self.assertEqual(payload["meanReciprocalRank"], 1.0)
            self.assertEqual(len(payload["cases"]), 2)

    def test_bundled_bm25_baseline_meets_initial_retrieval_floor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repository"
            shutil.copytree(BENCHMARK_ROOT, root)

            result = self.run_cli(
                root,
                "context",
                "benchmark",
                "--corpus",
                "corpus.json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertGreaterEqual(payload["recallAt1"], 0.8)
            self.assertGreaterEqual(payload["recallAt5"], 0.9)
            self.assertGreaterEqual(payload["meanReciprocalRank"], 0.7)

    def test_impact_classifies_an_explicit_binding_without_overstating_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "src" / "auth.py").write_text(
                "def authenticate_request(token):\n    return token is not None\n",
                encoding="utf-8",
            )
            (root / "docs" / "security.md").write_text(
                "# Authentication\n\nRequests require a registered token.\n",
                encoding="utf-8",
            )
            manifest = {
                "schemaVersion": 1,
                "knowledge": [
                    {
                        "path": "docs/security.md",
                        "sources": ["src/auth.py"],
                    }
                ],
            }
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            result = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "src/auth.py",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "knowledge-impact-classified")
            self.assertEqual(payload["candidateImpacts"], [])
            self.assertEqual(payload["unmappedChanges"], [])
            self.assertEqual(len(payload["boundImpacts"]), 1)
            impact = payload["boundImpacts"][0]
            self.assertEqual(impact["changedPath"], "src/auth.py")
            self.assertEqual(impact["knowledgePath"], "docs/security.md")
            self.assertEqual(impact["binding"], "src/auth.py")
            self.assertEqual(impact["freshness"], "unknown")
            self.assertEqual(impact["reason"], "explicit-binding")

    def test_verify_records_source_hashes_and_makes_bound_knowledge_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "src" / "auth.py").write_text(
                "def authenticate_request(token):\n    return bool(token)\n",
                encoding="utf-8",
            )
            (root / "docs" / "security.md").write_text(
                "# Authentication\n\nRequests require a token.\n", encoding="utf-8"
            )
            manifest_path = root / ".polaralias" / "repo-context.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/security.md",
                                "sources": ["src/*.py"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            verified = self.run_cli(
                root,
                "context",
                "verify",
                "--knowledge",
                "docs/security.md",
                "--evidence",
                "Reviewed authentication behaviour against the implementation.",
            )
            impact = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "src/auth.py",
            )

            self.assertEqual(verified.returncode, 0, verified.stderr)
            verified_payload = json.loads(verified.stdout)
            self.assertEqual(verified_payload["result"], "knowledge-verified")
            self.assertEqual(verified_payload["knowledgePath"], "docs/security.md")
            self.assertEqual(verified_payload["sourceCount"], 2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            receipt = manifest["knowledge"][0]["verified"]
            self.assertEqual(
                receipt["evidence"],
                "Reviewed authentication behaviour against the implementation.",
            )
            self.assertIn("verifiedAt", receipt)
            self.assertIn("src/auth.py", receipt["sourceHashes"])
            self.assertIn("docs/security.md", receipt["sourceHashes"])
            self.assertEqual(impact.returncode, 0, impact.stderr)
            impact_payload = json.loads(impact.stdout)
            self.assertEqual(impact_payload["boundImpacts"][0]["freshness"], "fresh")

    def test_editing_a_verified_knowledge_document_makes_its_own_receipt_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "src" / "auth.py").write_text("AUTH_REQUIRED = True\n", encoding="utf-8")
            knowledge = root / "docs" / "security.md"
            knowledge.write_text("# Authentication\n\nAuthentication is required.\n", encoding="utf-8")
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {"path": "docs/security.md", "sources": ["src/auth.py"]}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            verified = self.run_cli(
                root,
                "context",
                "verify",
                "--knowledge",
                "docs/security.md",
                "--evidence",
                "Reviewed the canonical claim against authentication implementation.",
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)

            knowledge.write_text(
                "# Authentication\n\nAuthentication is optional.\n",
                encoding="utf-8",
            )
            impact = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "docs/security.md",
            )

            self.assertEqual(impact.returncode, 0, impact.stderr)
            payload = json.loads(impact.stdout)
            self.assertEqual(payload["unmappedChanges"], [])
            self.assertEqual(payload["boundImpacts"][0]["binding"], "knowledge-document")
            self.assertEqual(payload["boundImpacts"][0]["freshness"], "stale")

    def test_impact_marks_verified_knowledge_stale_after_bound_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            source = root / "src" / "auth.py"
            source.write_text("AUTH_REQUIRED = True\n", encoding="utf-8")
            (root / "docs" / "security.md").write_text(
                "# Authentication\n\nAuthentication is required.\n", encoding="utf-8"
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/security.md",
                                "sources": ["src/auth.py"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            verified = self.run_cli(
                root,
                "context",
                "verify",
                "--knowledge",
                "docs/security.md",
                "--evidence",
                "Reviewed initial authentication behaviour.",
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)

            source.write_text("AUTH_REQUIRED = False\n", encoding="utf-8")
            result = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "src/auth.py",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["boundImpacts"][0]["freshness"], "stale")

    def test_impact_separates_lexical_candidates_from_unmapped_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "config").mkdir()
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "config" / "providers.toml").write_text(
                "[github]\ntoken_key = 'github.token'\nprovider = 'gateway'\n",
                encoding="utf-8",
            )
            (root / "src" / "orphan.py").write_text(
                "ZEBRANIUM_FLUX = 17\n", encoding="utf-8"
            )
            (root / "src" / "bound_elsewhere.py").write_text(
                "VALUE = 1\n", encoding="utf-8"
            )
            unrelated = root / "skills" / "agenda" / "SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text(
                "# Agenda skill\n\n"
                "Use repository context, documentation, tasks, evidence, and workflow rules.\n",
                encoding="utf-8",
            )
            (root / "docs" / "configuration.md").write_text(
                "# GitHub provider configuration\n\n"
                "The gateway reads the GitHub token key from provider configuration.\n",
                encoding="utf-8",
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/configuration.md",
                                "sources": ["src/bound_elsewhere.py"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "config/providers.toml",
                "--changed",
                "src/orphan.py",
                "--changed",
                "skills/agenda/SKILL.md",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["boundImpacts"], [])
            self.assertEqual(len(payload["candidateImpacts"]), 1)
            candidate = payload["candidateImpacts"][0]
            self.assertEqual(candidate["changedPath"], "config/providers.toml")
            self.assertEqual(candidate["knowledgePath"], "docs/configuration.md")
            self.assertEqual(candidate["reason"], "lexical-similarity")
            self.assertGreater(candidate["score"], 0)
            self.assertIn("gateway", candidate["matchedTerms"])
            self.assertGreaterEqual(len(candidate["matchedTerms"]), 2)
            self.assertGreaterEqual(len(candidate["pathMatchedTerms"]), 2)
            self.assertEqual(
                payload["unmappedChanges"],
                [
                    {
                        "changedPath": "src/orphan.py",
                        "reason": "no-knowledge-relationship",
                    },
                    {
                        "changedPath": "skills/agenda/SKILL.md",
                        "reason": "no-knowledge-relationship",
                    },
                ],
            )

    def test_check_reports_stale_bound_knowledge_from_verification_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            source = root / "src" / "auth.py"
            source.write_text("AUTH_REQUIRED = True\n", encoding="utf-8")
            (root / "docs" / "security.md").write_text(
                "# Authentication\n\nAuthentication is required.\n", encoding="utf-8"
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/security.md",
                                "sources": ["src/auth.py"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            verified = self.run_cli(
                root,
                "context",
                "verify",
                "--knowledge",
                "docs/security.md",
                "--evidence",
                "Reviewed required authentication.",
            )
            self.assertEqual(verified.returncode, 0, verified.stderr)
            source.write_text("AUTH_REQUIRED = False\n", encoding="utf-8")

            result = self.run_cli(root, "context", "check")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["knowledgeFreshness"], "stale")
            self.assertEqual(
                payload["staleKnowledge"],
                [
                    {
                        "knowledgePath": "docs/security.md",
                        "verifiedAt": payload["staleKnowledge"][0]["verifiedAt"],
                    }
                ],
            )
            self.assertEqual(payload["unverifiedKnowledge"], [])

    def test_double_star_binding_matches_direct_and_nested_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src" / "nested").mkdir(parents=True)
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "src" / "direct.py").write_text("DIRECT = True\n", encoding="utf-8")
            (root / "src" / "nested" / "deep.py").write_text(
                "DEEP = True\n", encoding="utf-8"
            )
            (root / "docs" / "sources.md").write_text(
                "# Sources\n\nPython source behaviour.\n", encoding="utf-8"
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/sources.md",
                                "sources": ["src/**/*.py"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "src/direct.py",
                "--changed",
                "src/nested/deep.py",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(
                [impact["changedPath"] for impact in payload["boundImpacts"]],
                ["src/direct.py", "src/nested/deep.py"],
            )

    def test_impact_rejects_binding_patterns_that_escape_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "docs" / "security.md").write_text(
                "# Security\n", encoding="utf-8"
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/security.md",
                                "sources": ["../private/**"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cli(
                root,
                "context",
                "impact",
                "--changed",
                "src/example.py",
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "context-error")
            self.assertEqual(payload["error"]["code"], "knowledge_manifest_invalid")

    def test_check_rejects_malformed_verification_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / ".polaralias").mkdir()
            (root / "src" / "auth.py").write_text("AUTH = True\n", encoding="utf-8")
            (root / "docs" / "security.md").write_text(
                "# Security\n", encoding="utf-8"
            )
            (root / ".polaralias" / "repo-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "knowledge": [
                            {
                                "path": "docs/security.md",
                                "sources": ["src/auth.py"],
                                "verified": {
                                    "verifiedAt": "not-a-date",
                                    "evidence": "claimed review",
                                    "sourceHashes": {"src/auth.py": "not-a-hash"},
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cli(root, "context", "check")

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "context-error")
            self.assertEqual(payload["error"]["code"], "knowledge_manifest_invalid")


if __name__ == "__main__":
    unittest.main()
