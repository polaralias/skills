from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
CLI_PATH = REPOSITORY / "scripts" / "okf_tasks.py"
SPEC = importlib.util.spec_from_file_location("okf_tasks_cli", CLI_PATH)
assert SPEC and SPEC.loader
okf_tasks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(okf_tasks)


def arguments(**values: object) -> argparse.Namespace:
    defaults: dict[str, object] = {"root": ".", "bundle": "tasks"}
    defaults.update(values)
    return argparse.Namespace(**defaults)


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def create_task(self) -> None:
        result = okf_tasks.create_task(
            arguments(
                root=str(self.root),
                slug="first-task",
                title="First task",
                description="Produce the first observable result.",
                owner="agent",
            )
        )
        self.assertEqual(0, result)

    def test_standard_bundle_placements(self) -> None:
        for placement, expected in (("root", "tasks"), ("docs", "docs/tasks")):
            with self.subTest(placement=placement):
                okf_tasks.init_bundle(
                    arguments(
                        root=str(self.root),
                        bundle=None,
                        placement=placement,
                        force=False,
                    )
                )
                self.assertTrue((self.root / expected / "index.md").is_file())

        okf_tasks.create_task(
            arguments(
                root=str(self.root),
                bundle="docs/tasks",
                slug="project-delivery",
                title="Deliver the project",
                description="Complete the observable project outcome.",
                owner="project-team",
            )
        )
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "docs" / "tasks"))

    def test_docs_placement_and_custom_bundle_are_mutually_exclusive(self) -> None:
        with self.assertRaisesRegex(SystemExit, "either --placement docs or --bundle"):
            okf_tasks.init_bundle(
                arguments(
                    root=str(self.root),
                    bundle="project/tasks",
                    placement="docs",
                    force=False,
                )
            )

    def test_create_transition_and_validate(self) -> None:
        self.create_task()
        path = self.root / "tasks" / "first-task" / "task.md"
        metadata, _ = okf_tasks.read_document(path)
        self.assertEqual("Task", metadata["type"])
        self.assertEqual("proposed", metadata["status"])

        for status in ("ready", "in-progress", "validation", "done"):
            okf_tasks.set_status(
                arguments(
                    root=str(self.root),
                    task="first-task",
                    workstream=None,
                    status=status,
                    force=False,
                )
            )
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))

    def test_active_workstream_prevents_done(self) -> None:
        self.create_task()
        okf_tasks.add_workstream(
            arguments(
                root=str(self.root),
                task="first-task",
                slug="implementation",
                title="Implement the result",
                description="Deliver an independently validated implementation.",
                owner="agent",
                branch="task/first-task-implementation",
            )
        )
        for status in ("ready", "in-progress", "validation"):
            okf_tasks.set_status(
                arguments(
                    root=str(self.root),
                    task="first-task",
                    workstream=None,
                    status=status,
                    force=False,
                )
            )
        with self.assertRaisesRegex(SystemExit, "workstreams remain active"):
            okf_tasks.set_status(
                arguments(
                    root=str(self.root),
                    task="first-task",
                    workstream=None,
                    status="done",
                    force=False,
                )
            )

    def test_external_mapping_and_unknown_fields_survive(self) -> None:
        self.create_task()
        path = self.root / "tasks" / "first-task" / "task.md"
        metadata, body = okf_tasks.read_document(path)
        metadata["producer_extension"] = {"nested": ["one", "two"]}
        okf_tasks.write_document(path, metadata, body)

        okf_tasks.link_external(
            arguments(
                root=str(self.root),
                task="first-task",
                system="linear",
                id="ENG-1",
                url="https://linear.app/example/issue/ENG-1",
                authority="repository",
            )
        )
        updated, _ = okf_tasks.read_document(path)
        self.assertEqual({"nested": ["one", "two"]}, updated["producer_extension"])
        self.assertEqual("repository", updated["sync"]["authority"])
        self.assertEqual("ENG-1", updated["external"][0]["id"])
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))

    def test_reopening_preserves_completion_history(self) -> None:
        self.create_task()
        for status in ("ready", "in-progress", "validation", "done", "in-progress"):
            okf_tasks.set_status(arguments(root=str(self.root), task="first-task", workstream=None, status=status, force=False))
        task, _ = okf_tasks.read_document(self.root / "tasks" / "first-task" / "task.md")
        self.assertEqual("in-progress", task["status"])
        self.assertNotIn("finished", task)
        self.assertEqual(1, len(task["completion_history"]))
        self.assertTrue(okf_tasks.is_rfc3339(task["completion_history"][0]["finished"]))
        self.assertTrue(okf_tasks.is_rfc3339(task["completion_history"][0]["reopened"]))

    def test_prepare_external_artifact_is_body_only_and_pinned(self) -> None:
        self.create_task()
        guide = self.root / "docs" / "guide.md"
        guide.parent.mkdir(parents=True)
        guide.write_text("# Guide\n", encoding="utf-8")
        task_path = self.root / "tasks" / "first-task" / "task.md"
        metadata, body = okf_tasks.read_document(task_path)
        body += "\n## Related knowledge\n\nSee [the guide](../../docs/guide.md).\n"
        okf_tasks.write_document(task_path, metadata, body)
        output = self.root / "prepared.md"
        okf_tasks.prepare_external_artifact(
            arguments(
                root=str(self.root),
                source="tasks/first-task/task.md",
                remote="origin",
                remote_url="https://token@github.com/example/project.git",
                provider="github",
                ref="abc123",
                include_frontmatter=False,
                allow_remote_images=False,
                output=str(output),
                force=False,
            )
        )
        rendered = output.read_text(encoding="utf-8")
        self.assertIn("source=tasks/first-task/task.md; revision=abc123", rendered)
        self.assertIn("https://github.com/example/project/blob/abc123/docs/guide.md", rendered)
        self.assertNotIn("token@", rendered)
        self.assertNotIn("type: Task", rendered)

    def test_prepare_external_artifact_does_not_echo_a_secret(self) -> None:
        self.create_task()
        task_path = self.root / "tasks" / "first-task" / "task.md"
        metadata, body = okf_tasks.read_document(task_path)
        secret = "supersecretvalue123456"
        okf_tasks.write_document(task_path, metadata, body + f"\napi_key={secret}\n")
        with self.assertRaises(SystemExit) as caught:
            okf_tasks.prepare_external_artifact(
                arguments(
                    root=str(self.root),
                    source="tasks/first-task/task.md",
                    remote="origin",
                    remote_url="https://github.com/example/project.git",
                    provider="github",
                    ref="abc123",
                    include_frontmatter=False,
                    allow_remote_images=False,
                    output=None,
                    force=False,
                )
            )
        self.assertIn("detected assigned secret", str(caught.exception))
        self.assertNotIn(secret, str(caught.exception))

    def test_bundle_cannot_escape_repository(self) -> None:
        with self.assertRaisesRegex(SystemExit, "inside the repository"):
            okf_tasks.bundle_root(self.root, "../outside")

    def test_malformed_frontmatter_is_reported_without_crashing(self) -> None:
        task = self.root / "tasks" / "broken" / "task.md"
        task.parent.mkdir(parents=True)
        task.write_text("---\ntype: [invalid\n---\n# Broken\n", encoding="utf-8")
        (self.root / "tasks" / "index.md").write_text("# Task index\n", encoding="utf-8")
        errors = okf_tasks.validate_bundle(self.root / "tasks")
        self.assertTrue(any("Invalid YAML frontmatter" in error for error in errors))

    def test_live_tracking_adjusts_long_elapsed_window(self) -> None:
        self.create_task()
        okf_tasks.set_status(
            arguments(
                root=str(self.root),
                task="first-task",
                workstream=None,
                status="ready",
                force=False,
            )
        )
        okf_tasks.start_time(
            arguments(
                root=str(self.root),
                task="first-task",
                actor="agent",
                workstream=None,
                entry=None,
                started="2026-07-17T08:00:00Z",
                note="Implementation started.",
            )
        )
        task_path = self.root / "tasks" / "first-task" / "task.md"
        task, _ = okf_tasks.read_document(task_path)
        self.assertEqual("in-progress", task["status"])
        self.assertEqual(0, task["effort_minutes"])

        okf_tasks.stop_time(
            arguments(
                root=str(self.root),
                task="first-task",
                entry=None,
                actor="agent",
                workstream=None,
                finished="2026-07-17T20:00:00Z",
                effort_minutes=150,
                note="The interval included user review waits and unrelated work.",
            )
        )
        task, _ = okf_tasks.read_document(task_path)
        self.assertEqual(150, task["effort_minutes"])
        time_path = self.root / "tasks" / "first-task" / "time" / "20260717t080000z-agent-tracked.md"
        entry, _ = okf_tasks.read_document(time_path)
        self.assertEqual(720, entry["elapsed_minutes"])
        self.assertEqual(150, entry["effort_minutes"])
        self.assertEqual("tracked-adjusted", entry["method"])
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))

    def test_running_time_prevents_task_completion(self) -> None:
        self.create_task()
        for status in ("ready", "in-progress", "validation"):
            okf_tasks.set_status(
                arguments(
                    root=str(self.root),
                    task="first-task",
                    workstream=None,
                    status=status,
                    force=False,
                )
            )
        okf_tasks.start_time(
            arguments(
                root=str(self.root),
                task="first-task",
                actor="agent",
                workstream=None,
                entry=None,
                started="2026-07-17T08:00:00Z",
                note=None,
            )
        )
        with self.assertRaisesRegex(SystemExit, "time entries remain running"):
            okf_tasks.set_status(
                arguments(
                    root=str(self.root),
                    task="first-task",
                    workstream=None,
                    status="done",
                    force=False,
                )
            )

    def test_manual_time_entry_updates_rollup(self) -> None:
        self.create_task()
        okf_tasks.add_time(
            arguments(
                root=str(self.root),
                task="first-task",
                actor="james",
                effort_minutes=45,
                note="Manual review and acceptance checks.",
                started="2026-07-17T09:00:00Z",
                finished="2026-07-17T09:30:00Z",
                workstream=None,
                entry=None,
            )
        )
        task, _ = okf_tasks.read_document(self.root / "tasks" / "first-task" / "task.md")
        self.assertEqual(45, task["effort_minutes"])
        self.assertEqual("2026-07-17T09:00:00Z", task["started"])
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))

    def test_effort_estimate_and_sprint_points_remain_separate(self) -> None:
        self.create_task()
        okf_tasks.set_estimate(
            arguments(
                root=str(self.root),
                task="first-task",
                effort_minutes=240,
                method="agent",
                confidence="medium",
                basis="Implementation, tests, review, and documentation.",
                actor="planning-agent",
                points=3.0,
                points_scale="fibonacci",
                points_context="platform-team",
            )
        )
        task, _ = okf_tasks.read_document(self.root / "tasks" / "first-task" / "task.md")
        self.assertEqual(240, task["estimate"]["effort_minutes"])
        self.assertEqual(3.0, task["sprint_points"]["value"])
        self.assertNotIn("effort_minutes", task["sprint_points"])
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            okf_tasks.time_summary(arguments(root=str(self.root), task="first-task"))
        self.assertIn("Estimated effort: 240 minutes", output.getvalue())
        self.assertIn("Sprint points: 3.0", output.getvalue())

    def test_commit_review_clusters_sparse_work_instead_of_using_full_span(self) -> None:
        commits = [
            {"commit": "1" * 40, "time": okf_tasks.parse_datetime("2026-07-17T08:00:00Z")},
            {"commit": "2" * 40, "time": okf_tasks.parse_datetime("2026-07-17T09:00:00Z")},
            {"commit": "3" * 40, "time": okf_tasks.parse_datetime("2026-07-17T19:00:00Z")},
            {"commit": "4" * 40, "time": okf_tasks.parse_datetime("2026-07-17T20:00:00Z")},
        ]
        sessions = okf_tasks.estimate_commit_sessions(commits, 90, 30)
        self.assertEqual(2, len(sessions))
        self.assertEqual(180, sum(session["effort_minutes"] for session in sessions))
        self.assertEqual("2026-07-17T07:45:00Z", sessions[0]["started"])
        self.assertEqual("2026-07-17T20:15:00Z", sessions[-1]["finished"])

    def test_backfill_from_real_commits(self) -> None:
        self.create_task()
        subprocess.run(["git", "init", "-b", "main", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test User"], check=True)
        hashes: list[str] = []
        for index, timestamp in enumerate(
            ("2026-07-17T08:00:00Z", "2026-07-17T09:00:00Z", "2026-07-17T19:00:00Z", "2026-07-17T20:00:00Z"),
            1,
        ):
            environment = os.environ.copy()
            environment["GIT_AUTHOR_DATE"] = timestamp
            environment["GIT_COMMITTER_DATE"] = timestamp
            subprocess.run(
                ["git", "-C", str(self.root), "commit", "--allow-empty", "-m", f"first-task step {index}"],
                check=True,
                capture_output=True,
                env=environment,
            )
            hashes.append(
                subprocess.run(
                    ["git", "-C", str(self.root), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
        okf_tasks.backfill_from_commits(
            arguments(
                root=str(self.root),
                task="first-task",
                commit=hashes,
                since=None,
                until=None,
                grep=None,
                session_gap_minutes=90,
                allowance_minutes=30,
                actor="agent",
                workstream=None,
                entry=None,
                effort_minutes=None,
                confidence="medium",
                note=None,
            )
        )
        task, _ = okf_tasks.read_document(self.root / "tasks" / "first-task" / "task.md")
        self.assertEqual(180, task["effort_minutes"])
        self.assertEqual([], okf_tasks.validate_bundle(self.root / "tasks"))


if __name__ == "__main__":
    unittest.main()

