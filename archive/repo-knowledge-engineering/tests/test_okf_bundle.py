from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "okf_bundle.py"
SPEC = importlib.util.spec_from_file_location("okf_bundle", MODULE_PATH)
okf_bundle = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = okf_bundle
SPEC.loader.exec_module(okf_bundle)


CONCEPT = """---
type: Architecture Concept
title: Request routing
description: Explains how inbound requests reach the application service.
tags: [architecture, routing]
timestamp: 2026-07-17T09:30:00Z
authority: canonical
producer_extension: preserved
---

# Request routing

See the [support boundary](/support/boundary.md).
"""


class OkfBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.bundle = Path(self.temp.name) / "knowledge"
        self.bundle.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.bundle / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_valid_bundle(self) -> None:
        self.write("architecture/routing.md", CONCEPT)
        self.write("support/boundary.md", """---
type: Support Boundary
title: Supported requests
description: Defines the currently verified request surface.
verification: verified-working
verified_at: 2026-07-17T10:00:00Z
verified_against:
  - ../../tests/request-routing.test.ts
---

# Supported requests
""")
        okf_bundle.build_indexes(self.bundle)
        self.write("log.md", """# Knowledge Update Log

## 2026-07-17

- **Creation**: Added the request routing concepts.
""")

    def test_valid_versioned_bundle_is_conformant(self) -> None:
        self.write_valid_bundle()

        report = okf_bundle.validate_bundle(self.bundle, require_version=True)

        self.assertTrue(report.conformant)
        self.assertEqual(report.declared_version, "0.1")
        self.assertEqual(report.concepts, 2)

    def test_missing_type_is_an_error(self) -> None:
        self.write("concept.md", """---
title: Missing type
description: This document cannot be routed by an OKF consumer.
---

Body.
""")

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("type must be" in finding.message for finding in report.errors))

    def test_unknown_extensions_are_tolerated(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant)

    def test_frontmatter_strings_are_plaintext_but_bare_links_are_allowed(self) -> None:
        marked_up = CONCEPT.replace(
            "producer_extension: preserved",
            "resource: https://example.test/source\nproducer_extension:\n  note: '**Bold** and [label](https://example.test)'",
        ).replace("/support/boundary.md", "https://example.test/source")
        self.write("concept.md", marked_up)

        report = okf_bundle.validate_bundle(self.bundle)

        messages = [finding.message for finding in report.errors]
        self.assertTrue(any("frontmatter string values must be plaintext" in message for message in messages))
        self.assertFalse(any("resource contains" in message for message in messages))

    def test_nested_frontmatter_html_and_block_markup_are_rejected(self) -> None:
        marked_up = CONCEPT.replace(
            "producer_extension: preserved",
            "producer_extension:\n  values:\n    - '<strong>Bold</strong>'\n    - |\n      - formatted list",
        ).replace("/support/boundary.md", "https://example.test/source")
        self.write("concept.md", marked_up)

        report = okf_bundle.validate_bundle(self.bundle)

        messages = [finding.message for finding in report.errors]
        self.assertTrue(any("producer_extension.values[0] contains HTML tag" in message for message in messages))
        self.assertTrue(any("producer_extension.values[1] contains Markdown block formatting" in message for message in messages))

    def test_navigation_extension_supports_reading_prominence(self) -> None:
        self.write("concept.md", CONCEPT.replace("producer_extension: preserved", "navigation:\n  role: entry-point\n  order: 10").replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant, report.errors)

    def test_navigation_extension_rejects_invalid_role_and_order(self) -> None:
        self.write("concept.md", CONCEPT.replace("producer_extension: preserved", "navigation:\n  role: urgent\n  order: -1").replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("navigation.role" in finding.message for finding in report.errors))
        self.assertTrue(any("navigation.order" in finding.message for finding in report.errors))

    def test_verified_claim_requires_provenance(self) -> None:
        self.write(
            "concept.md",
            CONCEPT.replace(
                "producer_extension: preserved",
                "verification: verified-working",
            ).replace("/support/boundary.md", "https://example.test/source"),
        )

        report = okf_bundle.validate_bundle(self.bundle)

        messages = [finding.message for finding in report.warnings]
        self.assertTrue(any("requires verified_at" in message for message in messages))
        self.assertTrue(any("requires verified_against" in message for message in messages))

    def test_verified_claim_accepts_concrete_provenance(self) -> None:
        self.write(
            "concept.md",
            CONCEPT.replace(
                "producer_extension: preserved",
                "verification: verified-limited\nverified_at: 2026-07-30T09:00:00Z\nverified_against:\n  - ../../tests/routing.test.ts",
            ).replace("/support/boundary.md", "https://example.test/source"),
        )

        report = okf_bundle.validate_bundle(self.bundle)

        messages = [finding.message for finding in report.warnings]
        self.assertFalse(any("requires verified_" in message for message in messages))

    def test_versioned_bundle_enforces_verified_claim_provenance(self) -> None:
        self.write(
            "concept.md",
            CONCEPT.replace(
                "producer_extension: preserved",
                "verification: verified-working",
            ).replace("/support/boundary.md", "https://example.test/source"),
        )
        okf_bundle.build_indexes(self.bundle)

        report = okf_bundle.validate_bundle(self.bundle, require_version=True)

        messages = [finding.message for finding in report.errors]
        self.assertTrue(any("requires verified_at" in message for message in messages))
        self.assertTrue(any("requires verified_against" in message for message in messages))

    def test_description_that_only_restates_title_warns(self) -> None:
        self.write(
            "concept.md",
            CONCEPT.replace(
                "description: Explains how inbound requests reach the application service.",
                "description: Request routing",
            ).replace("/support/boundary.md", "https://example.test/source"),
        )

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("query-shaped retrieval summary" in finding.message for finding in report.warnings))

    def test_partial_decision_requires_successor_and_clause_sections(self) -> None:
        self.write(
            "decision.md",
            CONCEPT.replace("type: Architecture Concept", "type: Decision")
            .replace("producer_extension: preserved", "decision_status: partially-superseded")
            .replace("/support/boundary.md", "https://example.test/source"),
        )

        report = okf_bundle.validate_bundle(self.bundle)

        messages = [finding.message for finding in report.warnings]
        self.assertTrue(any("require superseded_by" in message for message in messages))
        self.assertTrue(any("Current decision" in message for message in messages))
        self.assertTrue(any("Superseded clauses" in message for message in messages))

    def test_superseded_decision_leaves_current_navigation(self) -> None:
        self.write(
            "decision.md",
            CONCEPT.replace("type: Architecture Concept", "type: Decision")
            .replace(
                "producer_extension: preserved",
                "decision_status: superseded\nsuperseded_by:\n  - successor.md\nnavigation:\n  role: foundational\n  order: 10",
            )
            .replace("/support/boundary.md", "https://example.test/source"),
        )

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("leave the current-answer navigation path" in finding.message for finding in report.warnings))

    def test_versioned_rke_bundle_rejects_transient_handoff(self) -> None:
        self.write(
            "handoff/session.md",
            CONCEPT.replace("type: Architecture Concept", "type: Handoff")
            .replace("/support/boundary.md", "https://example.test/source"),
        )
        okf_bundle.build_indexes(self.bundle)

        report = okf_bundle.validate_bundle(self.bundle, require_version=True)

        self.assertTrue(any("handoffs must remain outside" in finding.message for finding in report.errors))

    def test_broken_internal_link_is_only_a_warning(self) -> None:
        self.write("concept.md", CONCEPT)

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant)
        self.assertTrue(any("broken internal link" in finding.message for finding in report.warnings))

    def test_disconnected_durable_concepts_are_errors(self) -> None:
        self.write("one.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        self.write("two.md", CONCEPT.replace("Request routing", "Second concept").replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("orphan concept" in finding.message for finding in report.errors))
        self.assertTrue(any("disconnected components" in finding.message for finding in report.errors))

    def test_runbooks_are_excluded_from_the_durable_graph(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        self.write("runbooks/operator.md", CONCEPT.replace("type: Architecture Concept", "type: Runbook").replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant, report.errors)

    def test_subdirectory_index_cannot_have_frontmatter(self) -> None:
        self.write("group/concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        self.write("group/index.md", """---
title: Group
---

# Concepts

- [Request routing](concept.md) - Routing details.
""")

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("only allowed on the bundle-root" in finding.message for finding in report.errors))

    def test_required_version_is_enforced_only_when_requested(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        self.write("index.md", """# Concepts

- [Request routing](concept.md) - Routing details.
""")

        permissive = okf_bundle.validate_bundle(self.bundle)
        strict_profile = okf_bundle.validate_bundle(self.bundle, require_version=True)

        self.assertTrue(permissive.conformant)
        self.assertFalse(strict_profile.conformant)

    def test_required_version_needs_root_index(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))

        report = okf_bundle.validate_bundle(self.bundle, require_version=True)

        self.assertTrue(any("bundle-root index.md" in finding.message for finding in report.errors))

    def test_log_dates_must_be_newest_first(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        self.write("log.md", """# Knowledge Update Log

## 2026-07-16
- **Creation**: Created the concept.

## 2026-07-17
- **Update**: Improved the concept.
""")

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(any("newest first" in finding.message for finding in report.errors))

    def test_index_builder_uses_concept_metadata_and_root_version(self) -> None:
        self.write("architecture/routing.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))

        written = okf_bundle.build_indexes(self.bundle)

        root_index = (self.bundle / "index.md").read_text(encoding="utf-8")
        child_index = (self.bundle / "architecture" / "index.md").read_text(encoding="utf-8")
        self.assertIn('okf_version: "0.1"', root_index)
        self.assertIn(okf_bundle.GENERATED_INDEX_MARKER, root_index)
        self.assertIn("[Request routing](routing.md)", child_index)
        self.assertEqual(len(written), 2)

    def test_index_builder_refuses_to_replace_a_manual_index(self) -> None:
        self.write("concept.md", CONCEPT.replace("/support/boundary.md", "https://example.test/source"))
        original = "# Curated navigation\n\nThis grouping is maintained by a person.\n"
        self.write("index.md", original)

        with self.assertRaisesRegex(SystemExit, "Refusing to overwrite"):
            okf_bundle.build_indexes(self.bundle)

        self.assertEqual((self.bundle / "index.md").read_text(encoding="utf-8"), original)

    def test_visualization_template_is_an_okf_concept_with_explicit_freshness(self) -> None:
        template = MODULE_PATH.parents[1] / "assets" / "okf" / "visualization.md.template"
        rendered = template.read_text(encoding="utf-8")
        for old, new in {
            "{{title}}": "Task delivery map",
            "{{description}}": "Describes the generated task delivery view.",
            "{{tags}}": "visualization, tasks",
            "{{timestamp}}": "2026-07-18T12:00:00Z",
            "{{authority}}": "derived",
            "{{verification}}": "verified-working",
            "{{source}}": "../../../tasks/index.md",
            "{{renderer}}": "okf-tasks visualize",
            "{{output}}": "../../../local-docs/tasks.html",
        }.items():
            rendered = rendered.replace(old, new)
        self.write("views/task-delivery.md", rendered)

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant, report.errors)
        metadata, _ = okf_bundle.parse_frontmatter(self.bundle / "views" / "task-delivery.md", required=True)
        self.assertEqual("Visualization", metadata["type"])
        self.assertEqual("2026-07-18T12:00:00Z", metadata["timestamp"])
        self.assertEqual("timestamp", metadata["temporal_basis"])
        self.assertEqual("current-records-only", metadata["history_model"])
        self.assertIn("review-signal", metadata["drift_policy"])

    def test_decision_template_supports_partial_supersession(self) -> None:
        template = MODULE_PATH.parents[1] / "assets" / "okf" / "decision.md.template"
        rendered = template.read_text(encoding="utf-8")
        for old, new in {
            "{{title}}": "Choose request authentication",
            "{{description}}": "Explains which authentication boundary applies to inbound service requests.",
            "{{tags}}": "decision, authentication",
            "{{timestamp}}": "2026-07-30T09:00:00Z",
            "{{decision_status}}": "partially-superseded",
            "{{superseded_by}}": "ADR-007.md#authentication-boundary",
        }.items():
            rendered = rendered.replace(old, new)
        self.write("decisions/ADR-002.md", rendered)

        report = okf_bundle.validate_bundle(self.bundle)

        self.assertTrue(report.conformant, report.errors)
        messages = [finding.message for finding in report.warnings]
        self.assertFalse(any("partially-superseded decisions require" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
