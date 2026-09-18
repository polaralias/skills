from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


VERSION_PATTERN = re.compile(r"^okf-tasks\s+([0-9]+(?:\.[0-9]+){2})$")


class OkfAdapterError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def normalise_relative(root: Path, value: str, *, must_exist: bool = False) -> str:
    candidate = Path(value)
    if candidate.is_absolute():
        raise OkfAdapterError("task_path_escape", "Task paths must be repository-relative.")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise OkfAdapterError("task_path_escape", "Task paths must remain inside the repository root.")
    if must_exist and not resolved.exists():
        raise OkfAdapterError("task_path_missing", f"Task path does not exist: {value}")
    return resolved.relative_to(resolved_root).as_posix()


def plan(mode: str) -> dict[str, Any]:
    if mode == "none":
        return {
            "mode": "none",
            "durable": False,
            "requiredFields": [],
            "operations": [],
            "optionalCapabilities": [],
        }
    base = {
        "mode": mode,
        "durable": True,
        "requiredFields": ["outcome", "acceptance", "status", "relatedKnowledge", "evidence"],
        "operations": ["init-bundle", "create", "set-status", "build-index", "validate"],
        "optionalCapabilities": [],
    }
    if mode == "full":
        base["operations"] += [
            "add-workstream",
            "set-estimate",
            "start-time",
            "stop-time",
            "tracker",
            "review-commits",
            "backfill-from-commits",
        ]
        base["optionalCapabilities"] = [
            "workstreams",
            "effort",
            "estimates",
            "tracker-sync",
            "visualisation",
            "commit-backfill",
        ]
    return base


def executable_command(cli: str | None) -> list[str]:
    selected = cli or shutil.which("okf-tasks")
    if not selected:
        raise OkfAdapterError(
            "okf_tasks_unavailable",
            "The authoritative okf-tasks CLI is unavailable; install it or pass a trusted --cli path.",
        )
    path = Path(selected)
    if cli and not path.exists():
        raise OkfAdapterError("okf_tasks_unavailable", f"OKF Tasks CLI does not exist: {cli}")
    return [sys.executable, str(path)] if path.suffix.lower() == ".py" else [selected]


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OkfAdapterError("okf_tasks_execution_failed", str(exc)) from exc


def check_bundle(root: Path, *, bundle: str, cli: str | None = None) -> tuple[dict[str, Any], int]:
    normalized_bundle = normalise_relative(root, bundle)
    executable = executable_command(cli)
    version_result = run_checked(executable + ["--version"])
    version_match = VERSION_PATTERN.fullmatch(version_result.stdout.strip())
    if version_result.returncode != 0 or not version_match:
        raise OkfAdapterError(
            "okf_tasks_incompatible",
            "The configured executable did not identify itself as a versioned okf-tasks CLI.",
        )
    command = executable + [
        "validate",
        "--root",
        str(root.resolve()),
        "--bundle",
        normalized_bundle,
        "--strict",
    ]
    result = run_checked(command)
    payload = {
        "result": "task-bundle-valid" if result.returncode == 0 else "task-bundle-invalid",
        "executed": True,
        "adapter": {"name": "okf-tasks", "version": version_match.group(1)},
        "command": command,
        "bundle": normalized_bundle,
        "validation": {
            "valid": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        },
    }
    return payload, 0 if result.returncode == 0 else 3
