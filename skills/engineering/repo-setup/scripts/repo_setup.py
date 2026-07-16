#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
RELEASE_PROFILES_DIR = ASSETS_DIR / "release-profiles"
AGENTS_MARKER_START = "<!-- repo-setup:shared-governance:start -->"
AGENTS_MARKER_END = "<!-- repo-setup:shared-governance:end -->"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")


def render_template(name: str, context: dict[str, object]) -> str:
    text = read_text(TEMPLATES_DIR / name)
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def render_profile(profile: str, name: str, context: dict[str, object]) -> str:
    text = read_text(RELEASE_PROFILES_DIR / profile / name)
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def load_defaults() -> dict[str, object]:
    return json.loads(read_text(ASSETS_DIR / "polaralias-defaults.json"))


def load_config(repo_path: Path, explicit_config: str | None) -> dict[str, object]:
    if explicit_config:
        return json.loads(Path(explicit_config).read_text(encoding="utf-8"))
    config_path = repo_path / "repo-admin.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def repo_context(repo_path: Path, args: argparse.Namespace) -> dict[str, object]:
    defaults = load_defaults()
    config = load_config(repo_path, args.config)
    context = {**defaults, **config}
    aliases = {
        "repoType": "repo_type",
        "releaseProfile": "release_profile",
        "codeOwners": "code_owners",
        "rulesetName": "ruleset_name",
        "requiredApprovals": "required_approvals",
        "requireCodeOwnerReview": "require_code_owner_review",
        "requireReviewThreadResolution": "require_review_thread_resolution",
        "organizationAdminBypass": "organization_admin_bypass",
    }
    for source, target in aliases.items():
        if source in context:
            context[target] = context[source]
    for key in (
        "license",
        "summary",
        "repo_type",
        "release_profile",
        "copyright_holder",
        "copyright_year",
        "owner",
        "repo",
        "artifact_name",
        "artifact_basename",
        "application_id",
        "version_source_path",
        "package_name",
        "manifest_path",
        "integration_slug",
        "ruleset_name",
        "required_approvals",
    ):
        value = getattr(args, key, None)
        if value is not None:
            context[key] = value
    context["repo_name"] = repo_path.name
    context["description"] = context.get("summary", repo_path.name)
    code_owners = getattr(args, "code_owner", None) or context.get("code_owners", [])
    if isinstance(code_owners, str):
        code_owners = [code_owners]
    context["code_owners"] = list(code_owners)
    context["code_owners_line"] = " ".join(str(owner) for owner in code_owners)
    return context


def merge_agents(existing: str, shared_block: str) -> str:
    block = f"{AGENTS_MARKER_START}\n{shared_block.rstrip()}\n{AGENTS_MARKER_END}"
    if not existing.strip():
        return "# AGENTS\n\n" + block + "\n"
    if AGENTS_MARKER_START in existing and AGENTS_MARKER_END in existing:
        start = existing.index(AGENTS_MARKER_START)
        end = existing.index(AGENTS_MARKER_END) + len(AGENTS_MARKER_END)
        return existing[:start].rstrip() + "\n\n" + block + "\n" + existing[end:].lstrip("\n")
    return existing.rstrip() + "\n\n" + block + "\n"


def license_template_name(license_name: str) -> str:
    mapping = {
        "Apache-2.0": "license-apache-2.0.txt",
        "MIT": "license-mit.txt",
    }
    if license_name not in mapping:
        raise SystemExit(f"Unsupported local license template: {license_name}")
    return mapping[license_name]


def sync_doc_templates(args: argparse.Namespace) -> int:
    repo_path = Path(args.repo_path).resolve()
    context = repo_context(repo_path, args)

    write_text(repo_path / "LICENSE", render_template(license_template_name(str(context["license"])), context))
    write_text(repo_path / "NOTICE", render_template("notice.txt", context))
    write_text(repo_path / "CONTRIBUTING.md", render_template("contributing.md", context))

    agents_path = repo_path / "AGENTS.md"
    existing_agents = read_text(agents_path) if agents_path.exists() else ""
    shared_agents = render_template("agents-block.md", context)
    write_text(agents_path, merge_agents(existing_agents, shared_agents))

    write_text(repo_path / ".github" / "release-drafter.yml", render_template("release-drafter-config.yml", context))
    write_text(repo_path / ".github" / "workflows" / "release-drafter.yml", render_template("release-drafter-workflow.yml", context))
    if context["code_owners"]:
        write_text(repo_path / ".github" / "CODEOWNERS", render_template("codeowners", context))

    if args.write_repo_admin:
        repo_admin = {
            "repoType": context.get("repo_type", "generic"),
            "license": context["license"],
            "summary": context["summary"],
            "descriptionWip": True,
            "enforcePrs": True,
            "releaseProfile": context.get("release_profile"),
            "codeOwners": context.get("code_owners", []),
            "rulesetName": context.get("ruleset_name", "Protect default branch"),
            "requiredApprovals": int(context.get("required_approvals", 1)),
            "requireCodeOwnerReview": bool(context.get("require_code_owner_review", True)),
            "requireReviewThreadResolution": bool(context.get("require_review_thread_resolution", True)),
            "organizationAdminBypass": bool(context.get("organization_admin_bypass", False)),
        }
        write_text(repo_path / "repo-admin.json", json.dumps(repo_admin, indent=2))
    return 0


def run_gh(*args: str, input_data: object | None = None) -> Any:
    command = ["gh", *args]
    stdin = json.dumps(input_data) if input_data is not None else None
    completed = subprocess.run(command, input=stdin, capture_output=True, text=True, check=True)
    stdout = completed.stdout.strip()
    if not stdout:
        return None
    return json.loads(stdout)


def run_gh_optional(*args: str) -> Any:
    completed = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if completed.returncode == 0:
        stdout = completed.stdout.strip()
        return json.loads(stdout) if stdout else {}
    if "HTTP 404" in completed.stderr:
        return None
    raise subprocess.CalledProcessError(
        completed.returncode,
        completed.args,
        output=completed.stdout,
        stderr=completed.stderr,
    )


def set_description(args: argparse.Namespace) -> int:
    description = args.description.strip()
    if args.wip and not description.startswith("WIP: "):
        description = f"WIP: {description}"
    if args.final and description.startswith("WIP: "):
        description = description.removeprefix("WIP: ").strip()
    subprocess.run(
        ["gh", "repo", "edit", f"{args.owner}/{args.repo}", "--description", description],
        check=True,
    )
    return 0


def build_ruleset_payload(
    branch: str,
    name: str,
    required_approvals: int = 1,
    require_code_owner_review: bool = True,
    require_review_thread_resolution: bool = True,
    allowed_merge_methods: list[str] | None = None,
    bypass_actors: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    if required_approvals < 0 or required_approvals > 10:
        raise ValueError("required approvals must be between 0 and 10")
    return {
        "name": name,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": bypass_actors or [],
        "conditions": {
            "ref_name": {
                "include": [f"refs/heads/{branch}"],
                "exclude": [],
            }
        },
        "rules": [
            {
                "type": "pull_request",
                "parameters": {
                    "allowed_merge_methods": allowed_merge_methods or ["merge", "squash", "rebase"],
                    "dismiss_stale_reviews_on_push": False,
                    "require_code_owner_review": require_code_owner_review,
                    "require_last_push_approval": False,
                    "required_approving_review_count": required_approvals,
                    "required_review_thread_resolution": require_review_thread_resolution,
                },
            },
            {"type": "non_fast_forward"},
            {"type": "deletion"},
        ],
    }


def repository_ruleset_id(owner: str, repo: str, name: str) -> int | None:
    rulesets = run_gh(
        "api",
        "--method",
        "GET",
        f"repos/{owner}/{repo}/rulesets",
        "-f",
        "includes_parents=false",
    )
    matches = [
        item
        for item in rulesets
        if item.get("name") == name and item.get("source_type") == "Repository"
    ]
    if len(matches) > 1:
        raise SystemExit(f"More than one repository ruleset is named {name!r}; resolve the duplicate before retrying.")
    return int(matches[0]["id"]) if matches else None


def upsert_repository_ruleset(owner: str, repo: str, payload: dict[str, object]) -> dict[str, object]:
    ruleset_id = repository_ruleset_id(owner, repo, str(payload["name"]))
    if ruleset_id is None:
        return run_gh(
            "api",
            "--method",
            "POST",
            f"repos/{owner}/{repo}/rulesets",
            "--input",
            "-",
            input_data=payload,
        )
    return run_gh(
        "api",
        "--method",
        "PATCH",
        f"repos/{owner}/{repo}/rulesets/{ruleset_id}",
        "--input",
        "-",
        input_data=payload,
    )


def contains_expected(actual: object, expected: object) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and contains_expected(actual[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        if all(isinstance(item, dict) and "type" in item for item in expected):
            actual_by_type = {
                item.get("type"): item
                for item in actual
                if isinstance(item, dict) and "type" in item
            }
            return all(contains_expected(actual_by_type.get(item["type"]), item) for item in expected)
        return len(actual) == len(expected) and all(
            contains_expected(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected)
        )
    return actual == expected


def verify_ruleset(actual: dict[str, object], expected: dict[str, object]) -> None:
    for key in ("name", "target", "enforcement", "conditions", "rules", "bypass_actors"):
        if not contains_expected(actual.get(key), expected.get(key)):
            raise SystemExit(f"Ruleset verification failed for {key!r}.")


def set_branch_protection(args: argparse.Namespace) -> int:
    branch = run_gh_optional("api", "--method", "GET", f"repos/{args.owner}/{args.repo}/branches/{args.branch}")
    if branch is None:
        raise SystemExit(f"Branch {args.branch!r} does not exist remotely. Push an initial commit before enabling protection.")
    codeowners = run_gh_optional(
        "api",
        "--method",
        "GET",
        f"repos/{args.owner}/{args.repo}/contents/.github/CODEOWNERS",
        "-f",
        f"ref={args.branch}",
    )
    if codeowners is None and args.require_code_owner_review:
        raise SystemExit(".github/CODEOWNERS is not present on the protected branch. Commit and push it before enabling code-owner review.")

    bypass_actors: list[dict[str, object]] = []
    if args.organization_admin_bypass:
        repository = run_gh("api", "--method", "GET", f"repos/{args.owner}/{args.repo}")
        if repository.get("owner", {}).get("type") != "Organization":
            raise SystemExit("Organisation-admin bypass is only valid for organisation-owned repositories.")
        bypass_actors.append({"actor_type": "OrganizationAdmin", "bypass_mode": "always"})

    payload = build_ruleset_payload(
        branch=args.branch,
        name=args.ruleset_name,
        required_approvals=args.required_approvals,
        require_code_owner_review=args.require_code_owner_review,
        require_review_thread_resolution=args.require_review_thread_resolution,
        allowed_merge_methods=args.allowed_merge_method,
        bypass_actors=bypass_actors,
    )
    result = upsert_repository_ruleset(args.owner, args.repo, payload)
    ruleset_id = int(result["id"])
    actual = run_gh("api", "--method", "GET", f"repos/{args.owner}/{args.repo}/rulesets/{ruleset_id}")
    verify_ruleset(actual, payload)

    classic = run_gh_optional(
        "api",
        "--method",
        "GET",
        f"repos/{args.owner}/{args.repo}/branches/{args.branch}/protection",
    )
    print(json.dumps({
        "ruleset": args.ruleset_name,
        "ruleset_id": ruleset_id,
        "branch": args.branch,
        "classic_branch_protection_also_present": classic is not None,
    }, indent=2))
    return 0


def apply_release_profile(args: argparse.Namespace) -> int:
    repo_path = Path(args.repo_path).resolve()
    context = repo_context(repo_path, args)
    profile = args.profile
    files_by_profile = {
        "android": ["android-debug.yml", "publish-release.yml"],
        "mcp": ["publish-release.yml"],
        "homeassistant": ["publish-release.yml"],
        "generic": ["publish-release.yml"],
    }
    output_names = {
        "android-debug.yml": ".github/workflows/android-debug.yml",
        "publish-release.yml": ".github/workflows/publish-release.yml",
    }
    for template_name in files_by_profile[profile]:
        rendered = render_profile(profile, template_name, context)
        write_text(repo_path / output_names[template_name], rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo bootstrap and release-profile helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo-path", required=True)
    common.add_argument("--config")
    common.add_argument("--license")
    common.add_argument("--summary")
    common.add_argument("--repo-type", dest="repo_type")
    common.add_argument("--release-profile")
    common.add_argument("--copyright-holder")
    common.add_argument("--copyright-year")
    common.add_argument("--owner")
    common.add_argument("--repo")
    common.add_argument("--code-owner", action="append")

    sync = subparsers.add_parser("sync-doc-templates", parents=[common])
    sync.add_argument("--write-repo-admin", action="store_true")
    sync.set_defaults(func=sync_doc_templates)

    description = subparsers.add_parser("set-description")
    description.add_argument("--owner", required=True)
    description.add_argument("--repo", required=True)
    description.add_argument("--description", required=True)
    description.add_argument("--wip", action="store_true")
    description.add_argument("--final", action="store_true")
    description.set_defaults(func=set_description)

    protection = subparsers.add_parser("set-branch-protection")
    protection.add_argument("--owner", required=True)
    protection.add_argument("--repo", required=True)
    protection.add_argument("--branch", default="main")
    protection.add_argument("--ruleset-name", default="Protect default branch")
    protection.add_argument("--required-approvals", type=int, default=1)
    protection.add_argument("--allowed-merge-method", action="append", choices=["merge", "squash", "rebase"])
    protection.add_argument("--organization-admin-bypass", action="store_true")
    protection.add_argument("--no-code-owner-review", dest="require_code_owner_review", action="store_false")
    protection.add_argument(
        "--no-review-thread-resolution",
        dest="require_review_thread_resolution",
        action="store_false",
    )
    protection.set_defaults(require_code_owner_review=True, require_review_thread_resolution=True)
    protection.set_defaults(func=set_branch_protection)

    release = subparsers.add_parser("apply-release-profile", parents=[common])
    release.add_argument("--profile", choices=["android", "mcp", "homeassistant", "generic"], required=True)
    release.add_argument("--artifact-name")
    release.add_argument("--artifact-basename")
    release.add_argument("--application-id")
    release.add_argument("--version-source-path")
    release.add_argument("--package-name")
    release.add_argument("--manifest-path")
    release.add_argument("--integration-slug")
    release.set_defaults(func=apply_release_profile)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
