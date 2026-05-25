#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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
    ):
        value = getattr(args, key, None)
        if value is not None:
            context[key] = value
    context["repo_name"] = repo_path.name
    context["description"] = context.get("summary", repo_path.name)
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

    if args.write_repo_admin:
        repo_admin = {
            "repoType": context.get("repo_type", "generic"),
            "license": context["license"],
            "summary": context["summary"],
            "descriptionWip": True,
            "enforcePrs": True,
            "releaseProfile": context.get("release_profile"),
        }
        write_text(repo_path / "repo-admin.json", json.dumps(repo_admin, indent=2))
    return 0


def run_gh(*args: str) -> dict[str, object] | None:
    command = ["gh", *args]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    stdout = completed.stdout.strip()
    if not stdout:
        return None
    return json.loads(stdout)


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


def branch_protection_rule(owner: str, repo: str, branch: str) -> tuple[str, str | None]:
    query = """
    query($owner:String!, $name:String!) {
      repository(owner:$owner, name:$name) {
        id
        branchProtectionRules(first:100) {
          nodes { id pattern }
        }
      }
    }
    """
    data = run_gh(
        "api",
        "graphql",
        "-f",
        f"query={query}",
        "-F",
        f"owner={owner}",
        "-F",
        f"name={repo}",
    )
    repository = data["data"]["repository"]
    rule_id = None
    for node in repository["branchProtectionRules"]["nodes"]:
        if node["pattern"] == branch:
            rule_id = node["id"]
            break
    return repository["id"], rule_id


def set_branch_protection(args: argparse.Namespace) -> int:
    repo_id, rule_id = branch_protection_rule(args.owner, args.repo, args.branch)
    mutation_name = "updateBranchProtectionRule" if rule_id else "createBranchProtectionRule"
    rule_ref = f'ruleId:"{rule_id}", ' if rule_id else ""
    mutation = f"""
    mutation {{
      {mutation_name}(input: {{
        {rule_ref}repositoryId:"{repo_id}",
        pattern:"{args.branch}",
        requiresApprovingReviews:true,
        requiredApprovingReviewCount:0,
        dismissesStaleReviews:false,
        isAdminEnforced:true,
        requiresConversationResolution:true,
        requiresLinearHistory:true,
        allowsForcePushes:false,
        allowsDeletions:false,
        requiresStatusChecks:false,
        restrictsPushes:false,
        restrictsReviewDismissals:false
      }}) {{
        clientMutationId
      }}
    }}
    """
    run_gh("api", "graphql", "-f", f"query={mutation}")
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
