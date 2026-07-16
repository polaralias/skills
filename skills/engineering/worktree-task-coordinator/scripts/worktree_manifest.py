#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


REQUIRED_AUTHORITY_KEYS = {"merge", "push", "deploy", "publish"}
WORKSTREAM_STATUSES = {"planned", "active", "blocked", "integration", "done", "cancelled"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalize_repo_path(value: str) -> str:
    return value.replace("\\", "/").strip("/").casefold()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def paths_overlap(left: str, right: str) -> bool:
    left_parts = Path(normalize_repo_path(left)).parts
    right_parts = Path(normalize_repo_path(right)).parts
    length = min(len(left_parts), len(right_parts))
    return left_parts[:length] == right_parts[:length]


def validate_manifest(data: dict[str, object], manifest_dir: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "task",
        "repository_root",
        "worktree_container",
        "base_revision",
        "integration_destination",
        "authority",
        "workstreams",
        "shared_path_owners",
        "integration_order",
        "validation",
    }
    missing = required - data.keys()
    if missing:
        return ["missing fields: " + ", ".join(sorted(missing))]
    if data["schema_version"] != 1:
        errors.append("schema_version must be 1")

    repo_root = (manifest_dir / str(data["repository_root"])).resolve()
    container = (manifest_dir / str(data["worktree_container"])).resolve()
    if is_within(container, repo_root):
        errors.append("worktree_container must be outside repository_root")

    authority = data["authority"]
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        missing_authority = REQUIRED_AUTHORITY_KEYS - authority.keys()
        if missing_authority:
            errors.append("authority missing: " + ", ".join(sorted(missing_authority)))
        for key, value in authority.items():
            if key in REQUIRED_AUTHORITY_KEYS and value != "inherited":
                errors.append(f"authority.{key} must be 'inherited'; the manifest cannot grant authority")

    workstreams = data["workstreams"]
    if not isinstance(workstreams, list) or len(workstreams) < 2:
        errors.append("workstreams must contain at least two parallel workstreams")
        return errors

    slugs: set[str] = set()
    branches: set[str] = set()
    worktree_paths: set[str] = set()
    owned_by_stream: dict[str, list[str]] = {}
    shared_users: dict[str, set[str]] = {}
    dependencies: dict[str, list[str]] = {}

    for index, item in enumerate(workstreams):
        label = f"workstreams[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        for field in ("slug", "branch", "worktree", "owner", "status", "owned_paths", "shared_paths", "depends_on"):
            if field not in item:
                errors.append(f"{label} missing {field}")
        if any(field not in item for field in ("slug", "branch", "worktree")):
            continue
        slug = str(item["slug"])
        branch = str(item["branch"])
        worktree = (manifest_dir / str(item["worktree"])).resolve()
        if slug in slugs:
            errors.append(f"duplicate workstream slug: {slug}")
        if not SLUG_PATTERN.fullmatch(slug):
            errors.append(f"{slug!r}: workstream slug must use lowercase kebab-case")
        slugs.add(slug)
        if not branch.strip():
            errors.append(f"{slug}: branch must not be empty")
        branch_key = branch.casefold()
        if branch_key in branches:
            errors.append(f"duplicate branch: {branch}")
        branches.add(branch_key)
        folded_worktree = os.path.normcase(str(worktree))
        if folded_worktree in worktree_paths:
            errors.append(f"duplicate worktree path: {worktree}")
        worktree_paths.add(folded_worktree)
        if not is_within(worktree, container):
            errors.append(f"{slug}: worktree must be inside worktree_container")
        if is_within(worktree, repo_root):
            errors.append(f"{slug}: worktree must not be inside repository_root")
        if item.get("status") not in WORKSTREAM_STATUSES:
            errors.append(f"{slug}: invalid status {item.get('status')!r}")
        owned_raw = item.get("owned_paths", [])
        shared_raw = item.get("shared_paths", [])
        dependencies_raw = item.get("depends_on", [])
        if not isinstance(owned_raw, list) or not isinstance(shared_raw, list) or not isinstance(dependencies_raw, list):
            errors.append(f"{slug}: owned_paths, shared_paths, and depends_on must be arrays")
            owned_raw, shared_raw, dependencies_raw = [], [], []
        owned = [normalize_repo_path(str(path)) for path in owned_raw]
        shared = [normalize_repo_path(str(path)) for path in shared_raw]
        if set(owned) & set(shared):
            errors.append(f"{slug}: a path cannot be both owned and shared")
        owned_by_stream[slug] = owned
        for path in shared:
            shared_users.setdefault(path, set()).add(slug)
        dependencies[slug] = [str(value) for value in dependencies_raw]

    stream_items = list(owned_by_stream.items())
    for left_index, (left_slug, left_paths) in enumerate(stream_items):
        for right_slug, right_paths in stream_items[left_index + 1:]:
            for left in left_paths:
                for right in right_paths:
                    if paths_overlap(left, right):
                        errors.append(f"owned path overlap: {left_slug}:{left} and {right_slug}:{right}")

    shared_path_owners_raw = data["shared_path_owners"]
    if not isinstance(shared_path_owners_raw, dict):
        errors.append("shared_path_owners must be an object")
        shared_path_owners_raw = {}
    shared_path_owners = {
        normalize_repo_path(str(path)): str(owner)
        for path, owner in shared_path_owners_raw.items()
    }
    for path, users in shared_users.items():
        owner = shared_path_owners.get(path)
        if len(users) > 1 and owner not in users:
            errors.append(f"shared path {path!r} needs an integration owner from its assigned workstreams")
    for path, owner in shared_path_owners.items():
        if path not in shared_users:
            errors.append(f"shared_path_owners includes unused path {path!r}")
        elif owner not in shared_users[path]:
            errors.append(f"shared path owner {owner!r} is not assigned {path!r}")

    order = data["integration_order"]
    if not isinstance(order, list) or len(order) != len(slugs) or set(str(value) for value in order) != slugs:
        errors.append("integration_order must contain every workstream exactly once")
    else:
        positions = {str(slug): index for index, slug in enumerate(order)}
        for slug, required_slugs in dependencies.items():
            for dependency in required_slugs:
                if dependency not in slugs:
                    errors.append(f"{slug}: unknown dependency {dependency}")
                elif positions[dependency] >= positions[slug]:
                    errors.append(f"{slug}: dependency {dependency} must appear earlier in integration_order")

    validation = data["validation"]
    if not isinstance(validation, dict) or not isinstance(validation.get("parallel_safe"), list) or not isinstance(validation.get("serial"), list):
        errors.append("validation must contain parallel_safe and serial command lists")
    return errors


def load_manifest(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Cannot read manifest {path}: {error}")
    if not isinstance(data, dict):
        raise SystemExit("Manifest root must be an object.")
    return data


def validated_manifest(path: Path) -> dict[str, object]:
    data = load_manifest(path)
    errors = validate_manifest(data, path.parent.resolve())
    if errors:
        raise SystemExit("\n".join(errors))
    return data


def validate_command(args: argparse.Namespace) -> int:
    validated_manifest(Path(args.manifest).resolve())
    print("Worktree coordination manifest is valid.")
    return 0


def plan_command(args: argparse.Namespace) -> int:
    path = Path(args.manifest).resolve()
    data = validated_manifest(path)
    base = str(data["base_revision"])
    commands = []
    for item in data["workstreams"]:
        worktree = (path.parent / str(item["worktree"])).resolve()
        commands.append({
            "workstream": item["slug"],
            "argv": ["git", "worktree", "add", "-b", str(item["branch"]), str(worktree), base],
        })
    print(json.dumps(commands, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and plan explicit Git worktree coordination.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validation = subparsers.add_parser("validate")
    validation.add_argument("--manifest", required=True)
    validation.set_defaults(func=validate_command)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--manifest", required=True)
    plan.set_defaults(func=plan_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
