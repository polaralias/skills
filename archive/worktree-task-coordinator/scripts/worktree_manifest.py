#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


REQUIRED_AUTHORITY_KEYS = {"merge", "push", "deploy", "publish"}
DELIVERY_TOPOLOGIES = {"parallel", "integration-branch", "stacked"}
WORKSTREAM_STATUSES = {
    "planned",
    "active",
    "blocked",
    "integration",
    "awaiting-merge",
    "done",
    "cancelled",
}
INTEGRATION_STATES = {"not-started", "in-progress", "awaiting-merge", "durably-integrated", "retained"}
INTEGRATION_METHODS = {"merge", "squash", "rebase", "cherry-pick", "stack", "other"}
INTEGRATION_VERIFICATIONS = {"ancestry", "exact-review-head", "recorded-rewrite-chain"}
REVIEW_STATES = {"not-published", "open", "queued", "merged", "closed"}
CLEANUP_STATES = {"not-ready", "deferred", "ready", "removed", "retained"}
WORKTREE_EVIDENCE_STATES = {"clean", "dirty", "missing", "unknown"}
REMOTE_BRANCH_STATES = {"present", "absent", "unknown"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OID_PATTERN = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


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


def valid_oid(value: object) -> bool:
    return isinstance(value, str) and OID_PATTERN.fullmatch(value) is not None


def validate_review(review: object, label: str, errors: list[str]) -> dict[str, object] | None:
    if review is None:
        return None
    if not isinstance(review, dict):
        errors.append(f"{label} must be an object")
        return None
    for field in ("provider", "repository", "id", "base_ref", "head_ref", "head_tip", "state"):
        if field not in review:
            errors.append(f"{label} missing {field}")
    for field in ("provider", "repository", "id", "base_ref", "head_ref"):
        if field in review and (not isinstance(review.get(field), str) or not str(review.get(field)).strip()):
            errors.append(f"{label}.{field} must be a non-empty string")
    if review.get("state") not in REVIEW_STATES:
        errors.append(f"{label}.state is invalid")
    if "head_tip" in review and not valid_oid(review.get("head_tip")):
        errors.append(f"{label}.head_tip must be a full Git object ID")
    return review


def validate_integration_evidence(item: dict[str, object], slug: str, errors: list[str]) -> dict[str, object] | None:
    evidence = item.get("integration")
    if evidence is None:
        return None
    label = f"{slug}.integration"
    if not isinstance(evidence, dict):
        errors.append(f"{label} must be an object")
        return None
    if evidence.get("state") not in INTEGRATION_STATES:
        errors.append(f"{label}.state is invalid")
    if evidence.get("method") not in INTEGRATION_METHODS:
        errors.append(f"{label}.method is invalid")
    if evidence.get("verification") not in INTEGRATION_VERIFICATIONS:
        errors.append(f"{label}.verification is invalid")
    if evidence.get("destination_ref") is not None and (
        not isinstance(evidence.get("destination_ref"), str) or not str(evidence.get("destination_ref")).strip()
    ):
        errors.append(f"{label}.destination_ref must be null or a non-empty string")
    for field in ("source_tip", "result_tip"):
        value = evidence.get(field)
        if value is not None and not valid_oid(value):
            errors.append(f"{label}.{field} must be null or a full Git object ID")
    review = validate_review(evidence.get("review"), f"{label}.review", errors)
    if evidence.get("state") == "durably-integrated":
        for field in ("source_tip", "destination_ref", "verified_at"):
            if not evidence.get(field):
                errors.append(f"{label}.{field} is required for durably-integrated state")
        verification = evidence.get("verification")
        if verification == "exact-review-head":
            if review is None or review.get("state") != "merged":
                errors.append(f"{label}: exact-review-head requires a merged review")
            elif review.get("head_tip") != evidence.get("source_tip"):
                errors.append(f"{label}: merged review head must equal source_tip")
            if review is not None and review.get("base_ref") != evidence.get("destination_ref"):
                errors.append(f"{label}: merged review base must equal destination_ref")
            if review is not None and review.get("head_ref") != item.get("branch"):
                errors.append(f"{label}: merged review head_ref must equal the workstream branch")
        if verification == "recorded-rewrite-chain":
            if not evidence.get("result_tip"):
                errors.append(f"{label}: recorded-rewrite-chain requires result_tip")
            if review is None or review.get("state") != "merged":
                errors.append(f"{label}: recorded-rewrite-chain requires a merged terminal review")
    return evidence


def validate_cleanup_evidence(
    item: dict[str, object],
    slug: str,
    integration: dict[str, object] | None,
    errors: list[str],
) -> None:
    cleanup = item.get("cleanup")
    if cleanup is None:
        return
    label = f"{slug}.cleanup"
    if not isinstance(cleanup, dict):
        errors.append(f"{label} must be an object")
        return
    for field in ("state", "verified_tip", "worktree", "remote_branch", "reason"):
        if field not in cleanup:
            errors.append(f"{label} missing {field}")
    if cleanup.get("state") not in CLEANUP_STATES:
        errors.append(f"{label}.state is invalid")
    if cleanup.get("worktree") not in WORKTREE_EVIDENCE_STATES:
        errors.append(f"{label}.worktree is invalid")
    if cleanup.get("remote_branch") not in REMOTE_BRANCH_STATES:
        errors.append(f"{label}.remote_branch is invalid")
    verified_tip = cleanup.get("verified_tip")
    if verified_tip is not None and not valid_oid(verified_tip):
        errors.append(f"{label}.verified_tip must be null or a full Git object ID")
    if "reason" in cleanup and (not isinstance(cleanup.get("reason"), str) or not str(cleanup.get("reason")).strip()):
        errors.append(f"{label}.reason must be a non-empty string")
    if cleanup.get("state") in {"ready", "removed"}:
        if integration is None or integration.get("state") != "durably-integrated":
            errors.append(f"{label}: ready or removed cleanup requires durably-integrated evidence")
        elif verified_tip != integration.get("source_tip"):
            errors.append(f"{label}: verified_tip must equal the integrated source_tip")
        if cleanup.get("remote_branch") != "absent":
            errors.append(f"{label}: ready or removed cleanup requires an absent remote branch")
        expected_worktree = "missing" if cleanup.get("state") == "removed" else "clean"
        if cleanup.get("worktree") != expected_worktree:
            errors.append(f"{label}: {cleanup.get('state')} cleanup requires worktree={expected_worktree}")


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

    topology = data.get("delivery_topology", "parallel")
    if topology not in DELIVERY_TOPOLOGIES:
        errors.append(f"delivery_topology must be one of {', '.join(sorted(DELIVERY_TOPOLOGIES))}")

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
    if not isinstance(workstreams, list) or not workstreams:
        errors.append("workstreams must contain at least one managed workstream")
        return errors

    slugs: set[str] = set()
    branches: set[str] = set()
    worktree_paths: set[str] = set()
    owned_by_stream: dict[str, list[str]] = {}
    shared_users: dict[str, set[str]] = {}
    dependencies: dict[str, list[str]] = {}
    workstream_items: dict[str, dict[str, object]] = {}

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
        if "base_ref" in item and (not isinstance(item.get("base_ref"), str) or not str(item.get("base_ref")).strip()):
            errors.append(f"{slug}: base_ref must be a non-empty string")
        if "stack_parent" in item and item.get("stack_parent") is not None and not isinstance(item.get("stack_parent"), str):
            errors.append(f"{slug}: stack_parent must be a string or null")
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
        workstream_items[slug] = item
        integration = validate_integration_evidence(item, slug, errors)
        validate_cleanup_evidence(item, slug, integration, errors)

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

    if topology == "stacked" and slugs:
        if len(slugs) < 2:
            errors.append("stacked topology requires at least two layers")
        roots: list[str] = []
        children: dict[str, list[str]] = {slug: [] for slug in slugs}
        published_repositories: set[tuple[str, str]] = set()
        for slug, item in workstream_items.items():
            if "base_ref" not in item or "stack_parent" not in item:
                errors.append(f"{slug}: stacked topology requires base_ref and stack_parent")
                continue
            parent = item.get("stack_parent")
            if parent is None:
                roots.append(slug)
                if item.get("base_ref") != data["integration_destination"]:
                    errors.append(f"{slug}: bottom stack layer must target integration_destination")
            else:
                parent_slug = str(parent)
                if parent_slug not in slugs:
                    errors.append(f"{slug}: unknown stack_parent {parent_slug}")
                    continue
                children[parent_slug].append(slug)
                parent_branch = workstream_items[parent_slug].get("branch")
                if item.get("base_ref") != parent_branch:
                    errors.append(f"{slug}: base_ref must equal its stack parent's branch")
                if parent_slug not in dependencies.get(slug, []):
                    errors.append(f"{slug}: stack_parent must also be a dependency")
            integration = item.get("integration")
            review = integration.get("review") if isinstance(integration, dict) else None
            if isinstance(review, dict):
                published_repositories.add((str(review.get("provider")), str(review.get("repository"))))
                if review.get("head_ref") != item.get("branch"):
                    errors.append(f"{slug}: stacked review head_ref must equal the layer branch")
                if review.get("base_ref") != item.get("base_ref"):
                    errors.append(f"{slug}: stacked review base_ref must equal the layer base_ref")
        if len(roots) != 1:
            errors.append("stacked topology must contain exactly one bottom layer")
        if any(len(values) > 1 for values in children.values()):
            errors.append("stacked topology must be a linear chain, not a branching graph")
        if len(published_repositories) > 1:
            errors.append("stacked reviews must use one provider repository")
        if len(roots) == 1 and isinstance(order, list):
            chain: list[str] = []
            current: str | None = roots[0]
            while current is not None and current not in chain:
                chain.append(current)
                next_values = children.get(current, [])
                current = next_values[0] if len(next_values) == 1 else None
            if [str(value) for value in order] != chain:
                errors.append("integration_order must run from the bottom to the top of the stack")

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
        workstream_base = str(item.get("base_ref") or base)
        commands.append({
            "workstream": item["slug"],
            "argv": ["git", "worktree", "add", "-b", str(item["branch"]), str(worktree), workstream_base],
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
