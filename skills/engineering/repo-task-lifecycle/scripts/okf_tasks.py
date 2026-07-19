#!/usr/bin/env python3
"""Reference CLI for OKF Tasks v0.5 bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError as error:  # pragma: no cover - exercised by installation environments
    raise SystemExit("PyYAML is required. Install it with: python -m pip install PyYAML") from error


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
STATUSES = (
    "proposed",
    "ready",
    "in-progress",
    "blocked",
    "validation",
    "done",
    "superseded",
    "deferred",
)
TERMINAL_WORKSTREAM_STATUSES = {"done", "superseded", "deferred"}
TRANSITIONS = {
    "proposed": {"ready", "deferred", "superseded"},
    "ready": {"in-progress", "deferred", "superseded"},
    "in-progress": {"blocked", "validation", "deferred", "superseded"},
    "blocked": {"in-progress", "deferred", "superseded"},
    "validation": {"in-progress", "blocked", "done"},
    "done": {"in-progress", "superseded"},
    "deferred": {"ready", "superseded"},
    "superseded": set(),
}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TASK_HEADINGS = ("Outcome", "Scope", "Acceptance", "Evidence")
WORKSTREAM_HEADINGS = ("Assigned outcome", "Acceptance and validation", "Evidence", "Handoff")
SYNC_AUTHORITIES = {"repository", "tracker", "manual"}
SYNC_MODES = {"push", "pull", "bidirectional", "manual"}
TRACKER_SYSTEMS = {"github", "gitlab", "linear", "clickup"}
LABEL_STRATEGIES = {"replace", "managed-subset", "read-only", "ignore"}
PORTABLE_FIELD_TYPES = {"text", "number", "date", "boolean", "single-select", "multi-select", "user", "url"}
TIME_STATUSES = {"running", "closed"}
TIME_METHODS = {"tracked", "tracked-adjusted", "manual", "estimated-commit-review"}
TIME_ACTIVITIES = {
    "implementation",
    "review",
    "validation",
    "knowledge-maintenance",
    "research",
    "planning",
    "coordination",
    "other",
}
ESTIMATE_CONFIDENCE = {"low", "medium", "high"}
ESTIMATE_METHODS = {"agent", "manual", "historical"}
LIVE_TIME_STATUSES = {"ready", "in-progress", "blocked", "validation"}
PROFILE_VERSION = "0.5"
PROFILE_URL = "https://github.com/polaralias/okf-tasks/blob/v0.5.0/SPEC.md"
CLI_VERSION = "0.5.0"
BUNDLE_PLACEMENTS = {"root": "tasks", "docs": "docs/tasks"}
MARKDOWN_LINK_PATTERN = re.compile(r"(?P<image>!)?(?P<label>\[[^\]\n]*\])\((?P<target>[^)\s]+)(?P<suffix>[^)]*)\)")
LINK_GRAPH_EXCLUDED_TYPES = {"tracker profile", "log"}
LINK_GRAPH_EXCLUDED_TYPE_MARKERS = {"runbook", "handoff", "session", "temporary", "scratch"}
LINK_GRAPH_EXCLUDED_DIRECTORIES = {
    ".git", ".venv", "build", "dist", "generated", "node_modules", "runbooks", "scratch", "temp", "temporary", "vendor"
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "assigned secret": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{12,}"
    ),
}
MACHINE_PATH_PATTERNS = {
    "file URI": re.compile(r"(?i)\bfile://"),
    "Windows absolute path": re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\)[^\s<>'\"]+"),
    "POSIX machine path": re.compile(r"(?<![A-Za-z0-9])/(?:home|Users|tmp|var/tmp|etc|opt|srv|root|mnt|Volumes)/[^\s<>'\"]+"),
    "home-relative path": re.compile(r"(?<![A-Za-z0-9])~[\\/][^\s<>'\"]+"),
}


class FrontmatterLoader(yaml.SafeLoader):
    """Load timestamps as strings so round-trips keep their source representation."""


FrontmatterLoader.yaml_implicit_resolvers = {
    key: list(value) for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for resolver_key, resolvers in list(FrontmatterLoader.yaml_implicit_resolvers.items()):
    FrontmatterLoader.yaml_implicit_resolvers[resolver_key] = [
        resolver for resolver in resolvers if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]


def fail(message: str) -> None:
    raise SystemExit(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def valid_slug(value: str) -> str:
    if not SLUG_PATTERN.fullmatch(value):
        fail(f"Invalid slug {value!r}; use lowercase kebab-case.")
    return value


def repository_root(value: str) -> Path:
    return Path(value).resolve()


def bundle_root(root: Path, bundle: str) -> Path:
    if Path(bundle).is_absolute():
        fail("Bundle path must be repository-relative.")
    candidate = (root / bundle).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        fail("Bundle path must remain inside the repository root.")
    return candidate


def task_path(bundle: Path, slug: str) -> Path:
    return bundle / slug / "task.md"


def workstream_path(bundle: Path, task: str, slug: str) -> Path:
    return bundle / task / "workstreams" / f"{slug}.md"


def parse_datetime(value: str, label: str = "timestamp") -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"Invalid {label} {value!r}; use an RFC 3339 datetime with timezone.")
    if parsed.tzinfo is None:
        fail(f"Invalid {label} {value!r}; a timezone is required.")
    return parsed


def format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def duration_minutes(started: str, finished: str) -> int:
    seconds = (parse_datetime(finished, "finished") - parse_datetime(started, "started")).total_seconds()
    if seconds < 0:
        fail("Finished time cannot be earlier than started time.")
    return max(0, int(round(seconds / 60)))


def entry_fragment(value: str) -> str:
    fragment = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return fragment or "actor"


def default_entry_id(started: str, actor: str) -> str:
    stamp = parse_datetime(started, "started").astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return valid_slug(f"{stamp.lower()}-{entry_fragment(actor)}")


def load_body_template(name: str, values: dict[str, str]) -> str:
    text = (ASSETS_DIR / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text.rstrip() + "\n"


def read_document(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail(f"Missing YAML frontmatter in {path}")
    closing = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if closing is None:
        fail(f"Unclosed YAML frontmatter in {path}")
    source = "".join(lines[1:closing])
    try:
        metadata = yaml.load(source, Loader=FrontmatterLoader)
    except yaml.YAMLError as error:
        fail(f"Invalid YAML frontmatter in {path}: {error}")
    if not isinstance(metadata, dict):
        fail(f"Frontmatter must be a mapping in {path}")
    body = "".join(lines[closing + 1 :]).lstrip("\r\n")
    return metadata, body


def write_document(path: Path, metadata: dict[str, Any], body: str) -> None:
    frontmatter = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    content = f"---\n{frontmatter}\n---\n\n{body.rstrip()}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_new_document(path: Path, metadata: dict[str, Any], body: str) -> None:
    if path.exists():
        fail(f"Refusing to overwrite existing record: {path}")
    write_document(path, metadata, body)


def git_value(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        fail(f"Git could not resolve {' '.join(arguments)} for external artifact preparation.")
    return result.stdout.strip()


def repository_web_base(remote_url: str, provider: str | None = None) -> tuple[str, str]:
    """Return provider and credential-free repository web base for common Git remotes."""
    value = remote_url.strip()
    scp = re.fullmatch(r"(?:[^@/]+@)?([^:]+):(.+)", value) if "://" not in value else None
    if scp:
        host, repository_path = scp.groups()
    else:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
            fail("Unsupported repository remote; use a GitHub or GitLab HTTPS/SSH remote.")
        host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        repository_path = parsed.path.lstrip("/")
    repository_path = repository_path.removesuffix(".git").strip("/")
    if not repository_path or repository_path.startswith("../"):
        fail("Repository remote does not contain a safe project path.")
    detected = provider
    host_name = host.split(":", 1)[0].lower()
    if detected is None:
        if host_name == "github.com" or host_name.endswith(".github.com"):
            detected = "github"
        elif "gitlab" in host_name:
            detected = "gitlab"
    if detected not in {"github", "gitlab"}:
        fail("Repository provider is not identifiable; pass --provider github or --provider gitlab.")
    encoded_path = "/".join(quote(unquote(part), safe="-._~") for part in repository_path.split("/"))
    return detected, f"https://{host}/{encoded_path}"


def egress_findings(text: str, root: Path) -> list[str]:
    """Report finding classes and line numbers without reproducing sensitive values."""
    findings: list[str] = []
    root_forms = {str(root.resolve()), str(root.resolve()).replace("\\", "/")}
    for line_number, line in enumerate(text.splitlines(), 1):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append(f"line {line_number}: detected {name}")
        for name, pattern in MACHINE_PATH_PATTERNS.items():
            if pattern.search(line):
                findings.append(f"line {line_number}: detected {name}")
        if any(value and value.lower() in line.lower() for value in root_forms):
            findings.append(f"line {line_number}: detected repository-local absolute path")
    return list(dict.fromkeys(findings))


def resolve_repository_links(
    text: str,
    root: Path,
    source: Path,
    remote_url: str,
    ref: str,
    provider: str | None = None,
    allow_remote_images: bool = False,
) -> str:
    root = root.resolve()
    source = source.resolve()
    try:
        source.relative_to(root)
    except ValueError:
        fail("Source document must remain inside the repository root.")
    detected_provider, web_base = repository_web_base(remote_url, provider)
    encoded_ref = quote(ref, safe="-._~")

    def replace(match: re.Match[str]) -> str:
        target = match.group("target").strip("<>")
        is_image = bool(match.group("image"))
        if target.startswith("#"):
            return match.group(0)
        parsed = urlsplit(target)
        if parsed.scheme:
            if parsed.scheme != "https":
                fail("External artifact contains a non-HTTPS or machine-local link.")
            if is_image and not allow_remote_images:
                fail("External artifact contains a remote image without an explicit allow policy.")
            return match.group(0)
        if target.startswith("//") or re.match(r"^[A-Za-z]:[\\/]", target):
            fail("External artifact contains a machine-local absolute link.")
        if parsed.query:
            fail("Repository-local links with query strings are not portable.")
        local_path = unquote(parsed.path).replace("\\", "/")
        candidate = (root / local_path.lstrip("/")) if local_path.startswith("/") else (source.parent / local_path)
        candidate = candidate.resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            fail("External artifact contains a repository link outside the declared root.")
        if not candidate.exists():
            fail("External artifact contains an unresolved repository-local link.")
        view = "tree" if candidate.is_dir() else "blob"
        encoded_path = quote(relative.as_posix(), safe="/-._~")
        fragment = f"#{quote(unquote(parsed.fragment), safe='-._~')}" if parsed.fragment else ""
        resolved = f"{web_base}/{'-/' if detected_provider == 'gitlab' else ''}{view}/{encoded_ref}/{encoded_path}{fragment}"
        return f"{'!' if is_image else ''}{match.group('label')}({resolved}{match.group('suffix')})"

    return MARKDOWN_LINK_PATTERN.sub(replace, text)


def prepare_external_artifact(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    source = (root / args.source).resolve()
    try:
        source.relative_to(root)
    except ValueError:
        fail("Source document must remain inside the repository root.")
    if not source.is_file():
        fail(f"Source document does not exist: {args.source}")
    metadata, body = read_document(source)
    payload = source.read_text(encoding="utf-8") if args.include_frontmatter else body
    initial_findings = egress_findings(payload, root)
    if initial_findings:
        fail("External artifact failed egress inspection:\n" + "\n".join(initial_findings))
    remote_url = args.remote_url or git_value(root, "remote", "get-url", args.remote)
    ref = args.ref or git_value(root, "rev-parse", "HEAD")
    rendered = resolve_repository_links(
        payload,
        root,
        source,
        remote_url,
        ref,
        args.provider,
        args.allow_remote_images,
    )
    provenance = f"<!-- OKF Tasks export: source={source.relative_to(root).as_posix()}; revision={ref} -->\n\n"
    output = provenance + rendered.rstrip() + "\n"
    final_findings = egress_findings(output, root)
    if final_findings:
        fail("Rendered external artifact failed egress inspection:\n" + "\n".join(final_findings))
    if args.output:
        destination = Path(args.output).resolve()
        if destination.exists() and not args.force:
            fail(f"Refusing to overwrite external artifact: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
        print(f"Prepared external artifact at {destination}")
    else:
        print(output, end="")
    return 0


def task_records(bundle: Path) -> list[tuple[Path, dict[str, Any], str]]:
    records: list[tuple[Path, dict[str, Any], str]] = []
    if not bundle.exists():
        return records
    for path in sorted(bundle.glob("*/task.md")):
        metadata, body = read_document(path)
        records.append((path, metadata, body))
    return records


def time_entries(metadata: dict[str, Any], path: Path | None = None) -> list[dict[str, Any]]:
    value = metadata.get("time", [])
    label = f" in {path}" if path else ""
    if value is None:
        return []
    if not isinstance(value, list):
        fail(f"Field 'time' must be a list{label}")
    if not all(isinstance(entry, dict) for entry in value):
        fail(f"Every time entry must be a mapping{label}")
    return value


def time_reference(task_record_id: str, entry_id: str) -> str:
    return f"{task_record_id}#time:{entry_id}"


def update_time_rollup(metadata: dict[str, Any]) -> None:
    entries = time_entries(metadata)
    starts = [str(entry["started"]) for entry in entries if entry.get("started")]
    closed_effort = [
        int(entry["effort_minutes"])
        for entry in entries
        if entry.get("status") == "closed" and isinstance(entry.get("effort_minutes"), int)
    ]
    if starts:
        metadata["started"] = min(starts, key=lambda value: parse_datetime(value, "started"))
        metadata["effort_minutes"] = sum(closed_effort)


def update_task_time_rollup(bundle: Path, task: str, completion_time: str | None = None) -> None:
    path = task_path(bundle, task)
    metadata, body = read_document(path)
    update_time_rollup(metadata)
    if completion_time is not None:
        metadata["finished"] = completion_time
    metadata["timestamp"] = utc_now()
    write_document(path, metadata, body)


def ensure_workstream(bundle: Path, task: str, workstream: str | None) -> None:
    if workstream and not workstream_path(bundle, task, valid_slug(workstream)).exists():
        fail(f"Workstream does not exist: {task}/{workstream}")


def append_time_entry(
    bundle: Path,
    task: str,
    entry: dict[str, Any],
) -> Path:
    path = task_path(bundle, task)
    metadata, body = read_document(path)
    entries = time_entries(metadata, path)
    entry_id = valid_slug(str(entry["id"]))
    if any(item.get("id") == entry_id for item in entries):
        fail(f"Time entry already exists: {time_reference(path.with_suffix('').as_posix(), entry_id)}")
    entries.append(entry)
    metadata["time"] = entries
    update_time_rollup(metadata)
    metadata["timestamp"] = utc_now()
    write_document(path, metadata, body)
    return path


def generated_index(bundle: Path) -> str:
    groups: dict[str, list[str]] = {status: [] for status in STATUSES}
    for path, metadata, _ in task_records(bundle):
        status = str(metadata.get("status", "unknown"))
        if status not in groups:
            groups[status] = []
        title = str(metadata.get("title") or path.parent.name)
        description = str(metadata.get("description") or "No description provided.")
        relative = f"./{path.parent.name}/task.md"
        groups[status].append(f"- [{title}]({relative}) — {description}")

    sections: list[str] = []
    for status in list(STATUSES) + sorted(set(groups) - set(STATUSES)):
        entries = groups[status]
        if entries:
            sections.append(f"## {status}\n\n" + "\n".join(entries))
    if not sections:
        sections.append("_No tasks._")
    return (
        "---\n"
        'okf_version: "0.1"\n'
        f'okf_tasks_version: "{PROFILE_VERSION}"\n'
        f'okf_tasks_profile: {PROFILE_URL}\n'
        "---\n\n"
        "<!-- Generated by okf-task-lifecycle. Do not edit by hand. -->\n"
        "# Task index\n\n"
        + "\n\n".join(sections)
        + "\n"
    )


def build_index(bundle: Path) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "index.md").write_text(generated_index(bundle), encoding="utf-8")


def init_bundle(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    if args.placement == "docs" and args.bundle:
        fail("Use either --placement docs or --bundle, not both.")
    selected_bundle = args.bundle or BUNDLE_PLACEMENTS[args.placement]
    bundle = bundle_root(root, selected_bundle)
    bundle.mkdir(parents=True, exist_ok=True)
    index = bundle / "index.md"
    if index.exists() and not args.force:
        fail(f"Index already exists: {index}. Use --force to rebuild it.")
    build_index(bundle)
    print(f"Initialized OKF Tasks bundle at {bundle}")
    return 0


def discovery_fingerprint(discovery: dict[str, Any]) -> str:
    encoded = json.dumps(discovery, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def load_discovery(path_value: str) -> dict[str, Any]:
    path = Path(path_value).resolve()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"Cannot read tracker discovery document {path}: {error}")
    if not isinstance(value, dict):
        fail("Tracker discovery document must be a JSON object.")
    required = ("system", "host", "resource", "scope", "statuses", "fields", "capabilities")
    missing = [key for key in required if value.get(key) is None]
    if missing:
        fail("Tracker discovery document is missing: " + ", ".join(missing))
    return value


def request_json(url: str, headers: dict[str, str], payload: dict[str, Any] | None = None, method: str | None = None) -> Any:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    content_headers = {"Content-Type": "application/json"} if data is not None else {}
    request = Request(url, data=data, headers={"Accept": "application/json", **content_headers, **headers}, method=method or ("POST" if data else "GET"))
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        fail(f"Tracker discovery request failed with HTTP {error.code} for configured host.")
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        fail(f"Tracker discovery request failed for configured host: {error}")


def discover_provider(
    system: str,
    scope_key: str,
    token: str,
    api_base: str | None = None,
    requester: Any = request_json,
) -> dict[str, Any]:
    if not token:
        fail("Tracker discovery requires a runtime credential.")
    if system == "github":
        base = (api_base or "https://api.github.com").rstrip("/")
        headers = {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2026-03-10"}
        repository = requester(f"{base}/repos/{scope_key}", headers)
        if not isinstance(repository, dict) or not repository.get("id"):
            fail("GitHub repository discovery returned an invalid response.")
        fields: list[Any] = []
        if repository.get("owner", {}).get("type") == "Organization":
            organization = str(repository.get("owner", {}).get("login") or scope_key.split("/", 1)[0])
            try:
                discovered_fields = requester(f"{base}/orgs/{organization}/issue-fields", headers)
                if isinstance(discovered_fields, list):
                    fields = discovered_fields
            except SystemExit:
                fields = []
        return {
            "system": "github", "host": f"https://{urlsplit(str(repository.get('html_url'))).netloc}", "resource": "issue",
            "scope": {"kind": "repository", "id": repository["id"], "key": repository.get("full_name", scope_key), "name": repository.get("name")},
            "statuses": [{"id": "open", "name": "Open", "category": "open", "position": 0}, {"id": "closed", "name": "Closed", "category": "closed", "position": 0}],
            "fields": fields, "capabilities": {"webhooks": True, "issue_fields": bool(fields), "project_fields": False},
        }
    if system == "gitlab":
        base = (api_base or "https://gitlab.com/api/v4").rstrip("/")
        project = requester(f"{base}/projects/{quote(scope_key, safe='')}", {"PRIVATE-TOKEN": token})
        if not isinstance(project, dict) or not project.get("id"):
            fail("GitLab project discovery returned an invalid response.")
        return {
            "system": "gitlab", "host": f"{urlsplit(str(project.get('web_url') or base)).scheme}://{urlsplit(str(project.get('web_url') or base)).netloc}", "resource": "issue",
            "scope": {"kind": "project", "id": project["id"], "key": project.get("path_with_namespace", scope_key), "name": project.get("name")},
            "statuses": [{"id": "opened", "name": "Open", "category": "open", "position": 0}, {"id": "closed", "name": "Closed", "category": "closed", "position": 0}],
            "fields": [], "capabilities": {"webhooks": True, "work_items": True, "custom_fields": "discover-at-runtime"},
        }
    if system == "linear":
        base = (api_base or "https://api.linear.app/graphql").rstrip("/")
        query = "query OkfTrackerDiscovery { teams { nodes { id key name states { nodes { id name type position } } } } }"
        response = requester(base, {"Authorization": token, "Content-Type": "application/json"}, {"query": query})
        teams = response.get("data", {}).get("teams", {}).get("nodes", []) if isinstance(response, dict) else []
        team = next((item for item in teams if str(item.get("id")) == scope_key or str(item.get("key", "")).lower() == scope_key.lower()), None)
        if not isinstance(team, dict):
            fail(f"Linear team {scope_key!r} was not found.")
        statuses = [{"id": item["id"], "name": item["name"], "category": str(item["type"]).lower(), "position": item.get("position", 0)} for item in team.get("states", {}).get("nodes", [])]
        return {
            "system": "linear", "host": "https://api.linear.app", "resource": "issue",
            "scope": {"kind": "team", "id": team["id"], "key": team["key"], "name": team.get("name")},
            "statuses": statuses, "fields": [], "capabilities": {"webhooks": True, "arbitrary_fields": False},
        }
    if system == "clickup":
        base = (api_base or "https://api.clickup.com/api/v2").rstrip("/")
        headers = {"Authorization": token}
        list_value = requester(f"{base}/list/{scope_key}", headers)
        fields_value = requester(f"{base}/list/{scope_key}/field", headers)
        if not isinstance(list_value, dict) or not list_value.get("id"):
            fail("ClickUp List discovery returned an invalid response.")
        statuses = []
        for position, item in enumerate(list_value.get("statuses", [])):
            raw_type = str(item.get("type", "custom")).lower()
            category = "closed" if raw_type in {"closed", "done"} else "open"
            statuses.append({"id": item.get("id") or item.get("status"), "name": item.get("status"), "category": category, "position": position})
        return {
            "system": "clickup", "host": "https://app.clickup.com", "resource": "task",
            "scope": {"kind": "list", "id": list_value["id"], "key": str(list_value["id"]), "name": list_value.get("name"), "workspace_id": list_value.get("space", {}).get("id")},
            "statuses": statuses, "fields": fields_value.get("fields", []) if isinstance(fields_value, dict) else [],
            "capabilities": {"webhooks": True, "custom_fields": True, "required_field_check": True, "custom_task_types": True},
        }
    fail(f"Unsupported tracker system: {system}")


def choose_status(statuses: list[dict[str, Any]], category: str, preferred: tuple[str, ...] = ()) -> str:
    candidates = [item for item in statuses if str(item.get("category", "")).lower() == category]
    candidates.sort(key=lambda item: (int(item.get("position", 0)), str(item.get("name", ""))))
    for needle in preferred:
        for item in candidates:
            if needle in str(item.get("name", "")).lower():
                return str(item["id"])
    if candidates:
        return str(candidates[0]["id"])
    fail(f"Tracker discovery has no status in required category {category!r}.")


def suggested_status_map(system: str, statuses_value: Any) -> dict[str, str]:
    if not isinstance(statuses_value, list) or not all(isinstance(item, dict) and item.get("id") for item in statuses_value):
        fail("Tracker discovery statuses must be a list of objects with stable IDs.")
    statuses: list[dict[str, Any]] = statuses_value
    if system == "linear":
        started = choose_status(statuses, "started")
        canceled = choose_status(statuses, "canceled")
        return {
            "proposed": choose_status(statuses, "backlog"),
            "ready": choose_status(statuses, "unstarted"),
            "in-progress": started,
            "blocked": choose_status(statuses, "started", ("blocked", "waiting")),
            "validation": choose_status(statuses, "started", ("review", "validat", "verify")),
            "done": choose_status(statuses, "completed"),
            "superseded": choose_status(statuses, "canceled", ("duplicate", "supersed", "won't", "wont")) if any(str(item.get("category", "")).lower() == "canceled" for item in statuses) else canceled,
            "deferred": canceled,
        }
    open_status = choose_status(statuses, "open")
    closed_status = choose_status(statuses, "closed")
    mapping = {status: open_status for status in STATUSES}
    mapping.update({"done": closed_status, "superseded": closed_status, "deferred": closed_status})
    for local, needles in (("ready", ("ready", "todo", "to do")), ("in-progress", ("progress", "doing")), ("blocked", ("blocked", "waiting")), ("validation", ("review", "validat", "verify"))):
        for item in statuses:
            name = str(item.get("name", "")).lower()
            if any(needle in name for needle in needles):
                mapping[local] = str(item["id"])
                break
    return mapping


def tracker_profile_documents(bundle: Path) -> list[tuple[Path, dict[str, Any], str]]:
    documents: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(bundle.joinpath("trackers").glob("*.md")):
        metadata, body = read_document(path)
        if metadata.get("type") == "Tracker Profile" and metadata.get("tracker"):
            documents.append((path, metadata, body))
    return documents


def resolve_tracker_slug(bundle: Path, requested: str | None) -> str:
    if requested:
        slug = valid_slug(requested)
        if not bundle.joinpath("trackers", f"{slug}.md").exists():
            fail(f"Tracker Profile does not exist: {bundle / 'trackers' / f'{slug}.md'}")
        return slug
    profiles = tracker_profile_documents(bundle)
    defaults = [str(metadata["tracker"]) for _, metadata, _ in profiles if metadata.get("default") is True]
    if len(defaults) == 1:
        return defaults[0]
    if len(defaults) > 1:
        fail("Multiple default Tracker Profiles are configured; run tracker set-default --tracker <profile> to choose one.")
    if len(profiles) == 1:
        return str(profiles[0][1]["tracker"])
    choices = ", ".join(str(metadata["tracker"]) for _, metadata, _ in profiles) or "none"
    fail(f"No default Tracker Profile is configured. Available profiles: {choices}. Run tracker set-default --tracker <profile> after choosing the project scope.")


def tracker_set_default(args: argparse.Namespace) -> int:
    bundle = bundle_root(repository_root(args.root), args.bundle)
    selected = valid_slug(args.tracker)
    selected_path = bundle / "trackers" / f"{selected}.md"
    if not selected_path.exists():
        fail(f"Tracker Profile does not exist: {selected_path}")
    for path, metadata, body in tracker_profile_documents(bundle):
        if str(metadata["tracker"]) == selected:
            metadata["default"] = True
        else:
            metadata.pop("default", None)
        write_document(path, metadata, body)
    print(f"Saved {selected!r} as the project default Tracker Profile.")
    return 0


def tracker_init(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    tracker = valid_slug(args.tracker)
    if getattr(args, "discovery_file", None):
        discovery = load_discovery(args.discovery_file)
    else:
        if not getattr(args, "scope", None):
            fail("Live tracker initialization requires --scope.")
        token_env = getattr(args, "token_env", None) or {"github": "GITHUB_TOKEN", "gitlab": "GITLAB_TOKEN", "linear": "LINEAR_API_KEY", "clickup": "CLICKUP_API_TOKEN"}[args.system]
        discovery = discover_provider(args.system, args.scope, os.environ.get(token_env, ""), getattr(args, "api_base", None))
    system = str(discovery["system"])
    if system != args.system or system not in TRACKER_SYSTEMS:
        fail("Requested tracker system does not match the discovery document.")
    profile_path = bundle / "trackers" / f"{tracker}.md"
    if profile_path.exists() and not args.force:
        fail(f"Tracker Profile already exists: {profile_path}. Use --force to replace it.")
    status_map = suggested_status_map(system, discovery["statuses"])
    statuses_by_id = {str(item["id"]): item for item in discovery["statuses"]}
    statuses_by_name = {str(item.get("name", "")).lower(): str(item["id"]) for item in discovery["statuses"]}
    for override in args.status_map or []:
        if "=" not in override:
            fail(f"Invalid --status-map {override!r}; use local=remote-id-or-name.")
        local, remote = override.split("=", 1)
        if local not in STATUSES:
            fail(f"Unknown local status in --status-map: {local}")
        resolved = remote if remote in statuses_by_id else statuses_by_name.get(remote.lower())
        if not resolved:
            fail(f"Unknown remote status in --status-map: {remote}")
        status_map[local] = resolved
    now = utc_now()
    metadata: dict[str, Any] = {
        "type": "Tracker Profile",
        "tracker": tracker,
        "system": system,
        "host": discovery["host"],
        "resource": discovery["resource"],
        "scope": discovery["scope"],
        "sync": {"mode": args.mode, "authority": args.authority},
        "status_map": status_map,
        "field_map": {
            "title": {"remote": "title"},
            "description": {"remote": "description"},
            "assignees": {"remote": "assignees"},
            "priority": {"remote": "priority"},
            "tags": {"remote": "labels", "strategy": "managed-subset", "managed_prefix": "okf:"},
        },
        "discovery": {
            "observed_at": now,
            "fingerprint": discovery_fingerprint(discovery),
            "capabilities": discovery["capabilities"],
            "statuses": discovery["statuses"],
            "fields": discovery["fields"],
        },
    }
    title = str(discovery["scope"].get("name") or discovery["scope"].get("key") or tracker)
    scope = discovery["scope"]
    profile_body = (
        f"# {title}\n\n"
        "## Setup evidence\n\n"
        f"- Provider system: `{system}`.\n"
        f"- Resource: `{discovery['resource']}`.\n"
        f"- Selected {scope.get('kind', 'scope')}: `{scope.get('key')}` (stable ID `{scope.get('id')}`).\n"
        f"- Discovery observed: `{now}` with fingerprint `{metadata['discovery']['fingerprint']}`.\n"
        "- Authentication was read from the runtime environment; no credential or credential reference is stored here.\n"
        f"- Project default selected: `{'yes' if getattr(args, 'default', False) else 'no'}`.\n\n"
        "## Mapping review\n\n"
        "Status and field mappings were proposed from provider discovery. Review lossy mappings before enabling tracker-authoritative pull synchronization.\n"
    )
    write_document(profile_path, metadata, profile_body)
    if getattr(args, "default", False):
        tracker_set_default(argparse.Namespace(root=str(root), bundle=args.bundle, tracker=tracker))
    print(f"Initialized Tracker Profile {tracker!r} at {profile_path}")
    return 0


def tracker_inspect(args: argparse.Namespace) -> int:
    bundle = bundle_root(repository_root(args.root), args.bundle)
    path = bundle / "trackers" / f"{valid_slug(args.tracker)}.md"
    if not path.exists():
        fail(f"Tracker Profile does not exist: {path}")
    profile, _ = read_document(path)
    print(json.dumps(profile, indent=2, sort_keys=True))
    return 0


def tracker_validate_command(args: argparse.Namespace) -> int:
    bundle = bundle_root(repository_root(args.root), args.bundle)
    path = bundle / "trackers" / f"{valid_slug(args.tracker)}.md"
    if not path.exists():
        fail(f"Tracker Profile does not exist: {path}")
    profile, _ = read_document(path)
    errors: list[str] = []
    validate_tracker_profile(path, profile, errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Tracker Profile {args.tracker!r} is valid.")
    return 0


def tracker_refresh(args: argparse.Namespace) -> int:
    bundle = bundle_root(repository_root(args.root), args.bundle)
    path = bundle / "trackers" / f"{valid_slug(args.tracker)}.md"
    if not path.exists():
        fail(f"Tracker Profile does not exist: {path}")
    profile, body = read_document(path)
    if getattr(args, "discovery_file", None):
        discovery = load_discovery(args.discovery_file)
    else:
        system = str(profile.get("system"))
        scope = profile.get("scope") if isinstance(profile.get("scope"), dict) else {}
        token_env = getattr(args, "token_env", None) or {"github": "GITHUB_TOKEN", "gitlab": "GITLAB_TOKEN", "linear": "LINEAR_API_KEY", "clickup": "CLICKUP_API_TOKEN"}[system]
        discovery = discover_provider(system, str(scope.get("key")), os.environ.get(token_env, ""), getattr(args, "api_base", None))
    if discovery.get("system") != profile.get("system") or discovery.get("scope", {}).get("id") != profile.get("scope", {}).get("id"):
        fail("Refreshed discovery must describe the same provider system and stable scope ID.")
    old = profile.get("discovery") if isinstance(profile.get("discovery"), dict) else {}
    new_fingerprint = discovery_fingerprint(discovery)
    if old.get("fingerprint") == new_fingerprint:
        print(f"Tracker Profile {args.tracker!r} discovery is current.")
        return 0
    old_status_ids = {str(item.get("id")) for item in old.get("statuses", []) if isinstance(item, dict)}
    new_status_ids = {str(item.get("id")) for item in discovery["statuses"] if isinstance(item, dict)}
    mapped_ids = {str(value) for value in profile.get("status_map", {}).values()}
    missing_mappings = sorted(mapped_ids - new_status_ids)
    print(f"Discovery drift for {args.tracker!r}: statuses +{len(new_status_ids - old_status_ids)} -{len(old_status_ids - new_status_ids)}")
    if missing_mappings:
        print("Mapped status IDs no longer available: " + ", ".join(missing_mappings), file=sys.stderr)
    if not args.accept:
        return 1
    if missing_mappings:
        fail("Cannot accept discovery while mapped statuses are unavailable; update mappings explicitly.")
    profile["discovery"] = {
        "observed_at": utc_now(), "fingerprint": new_fingerprint,
        "capabilities": discovery["capabilities"], "statuses": discovery["statuses"], "fields": discovery["fields"],
    }
    write_document(path, profile, body)
    print("Accepted refreshed discovery without changing mappings.")
    return 0


def provider_api_base(profile: dict[str, Any], override: str | None = None) -> str:
    if override:
        return override.rstrip("/")
    system, host = profile["system"], str(profile["host"]).rstrip("/")
    if system == "github":
        return "https://api.github.com" if host == "https://github.com" else host + "/api/v3"
    if system == "gitlab":
        return host + "/api/v4"
    if system == "linear":
        return "https://api.linear.app/graphql"
    return "https://api.clickup.com/api/v2"


def mapped_custom_values(profile: dict[str, Any], task: dict[str, Any]) -> list[dict[str, Any]]:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    field_map = profile.get("field_map") if isinstance(profile.get("field_map"), dict) else {}
    result: list[dict[str, Any]] = []
    for local_name, field in fields.items():
        mapping = field_map.get(f"fields.{local_name}")
        if not isinstance(mapping, dict):
            continue
        remote = mapping.get("remote")
        remote_id = remote.get("id") if isinstance(remote, dict) else remote
        if remote_id in (None, ""):
            fail(f"Mapped custom field fields.{local_name} does not identify a stable remote field ID.")
        result.append({"field_id": remote_id, "value": field["value"]})
    return result


def outbound_tags(profile: dict[str, Any], task: dict[str, Any], current: list[str] | None = None) -> list[str]:
    mapping = profile.get("field_map", {}).get("tags", {}) if isinstance(profile.get("field_map"), dict) else {}
    strategy = mapping.get("strategy", "ignore") if isinstance(mapping, dict) else "ignore"
    local = [str(value) for value in task.get("tags", [])] if isinstance(task.get("tags"), list) else []
    existing = [str(value) for value in current or []]
    if strategy == "replace": return list(dict.fromkeys(local))
    if strategy in {"read-only", "ignore"}: return existing
    prefix = str(mapping.get("managed_prefix", "")); managed_values = {str(value) for value in mapping.get("managed_values", [])}
    owns = lambda value: (bool(prefix) and value.startswith(prefix)) or value in managed_values
    return list(dict.fromkeys([value for value in existing if not owns(value)] + [value for value in local if owns(value)]))


def create_remote_record(
    profile: dict[str, Any], task: dict[str, Any], body: str, token: str,
    api_base: str | None = None, requester: Any = request_json,
) -> dict[str, Any]:
    if not token:
        fail("Remote creation requires a runtime credential.")
    system = str(profile["system"]); base = provider_api_base(profile, api_base); scope = profile["scope"]
    remote_status = profile["status_map"][task["status"]]
    tags = outbound_tags(profile, task)
    custom_values = mapped_custom_values(profile, task)
    if system == "github":
        headers = {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2026-03-10"}
        payload: dict[str, Any] = {"title": task["title"], "body": body, "labels": tags}
        if custom_values: payload["issue_field_values"] = custom_values
        response = requester(f"{base}/repos/{scope['key']}/issues", headers, payload)
        if not isinstance(response, dict) or response.get("pull_request") or not response.get("number"):
            fail("GitHub issue creation returned an invalid record.")
        if str(remote_status) == "closed":
            requester(f"{base}/repos/{scope['key']}/issues/{response['number']}", headers, {"state": "closed"}, "PATCH")
        verified = requester(f"{base}/repos/{scope['key']}/issues/{response['number']}", headers)
        remote_id, key, url = verified.get("node_id") or verified.get("id"), verified.get("number"), verified.get("html_url")
        revision = verified.get("updated_at")
    elif system == "gitlab":
        if custom_values: fail("This GitLab installation did not expose a writable custom-field transport during discovery.")
        headers = {"PRIVATE-TOKEN": token}
        payload = {"title": task["title"], "description": body, "labels": ",".join(tags)}
        response = requester(f"{base}/projects/{quote(str(scope['id']), safe='')}/issues", headers, payload)
        if not isinstance(response, dict) or not response.get("iid"): fail("GitLab issue creation returned an invalid record.")
        if str(remote_status) == "closed":
            requester(f"{base}/projects/{quote(str(scope['id']), safe='')}/issues/{response['iid']}", headers, {"state_event": "close"}, "PUT")
        verified = requester(f"{base}/projects/{quote(str(scope['id']), safe='')}/issues/{response['iid']}", headers)
        remote_id, key, url, revision = verified.get("id"), verified.get("iid"), verified.get("web_url"), verified.get("updated_at")
    elif system == "linear":
        if custom_values: fail("Linear does not expose arbitrary issue custom fields for this profile.")
        headers = {"Authorization": token, "Content-Type": "application/json"}
        mutation = "mutation OkfIssueCreate($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier url title updatedAt } } }"
        response = requester(base, headers, {"query": mutation, "variables": {"input": {"teamId": scope["id"], "title": task["title"], "description": body, "stateId": remote_status}}})
        issue = response.get("data", {}).get("issueCreate", {}).get("issue") if isinstance(response, dict) else None
        if not isinstance(issue, dict) or not issue.get("id"): fail("Linear issue creation returned an invalid record.")
        query = "query OkfIssue($id: String!) { issue(id: $id) { id identifier url title updatedAt } }"
        checked = requester(base, headers, {"query": query, "variables": {"id": issue["id"]}})
        verified = checked.get("data", {}).get("issue") if isinstance(checked, dict) else None
        if not isinstance(verified, dict): fail("Linear issue read-back verification failed.")
        remote_id, key, url, revision = verified.get("id"), verified.get("identifier"), verified.get("url"), verified.get("updatedAt")
    else:
        headers = {"Authorization": token}
        status_item = next((item for item in profile.get("discovery", {}).get("statuses", []) if str(item.get("id")) == str(remote_status)), {})
        payload = {"name": task["title"], "markdown_content": body, "status": status_item.get("name", remote_status), "tags": tags, "check_required_custom_fields": True, "custom_fields": [{"id": item["field_id"], "value": item["value"]} for item in custom_values]}
        response = requester(f"{base}/list/{scope['id']}/task", headers, payload)
        if not isinstance(response, dict) or not response.get("id"): fail("ClickUp task creation returned an invalid record.")
        verified = requester(f"{base}/task/{response['id']}", headers)
        remote_id, key, url, revision = verified.get("id"), verified.get("custom_id") or verified.get("id"), verified.get("url"), verified.get("date_updated")
    if not remote_id or not key or not url or str(verified.get("title") or verified.get("name")) != str(task["title"]):
        fail(f"{system} read-back verification did not preserve the required title and identity.")
    return {"id": remote_id, "key": key, "url": url, "remote_revision": revision or discovery_fingerprint(verified)}


def tracker_create_remote(args: argparse.Namespace) -> int:
    root = repository_root(args.root); bundle = bundle_root(root, args.bundle)
    tracker = resolve_tracker_slug(bundle, getattr(args, "tracker", None))
    task_file = task_path(bundle, valid_slug(args.task)); profile_file = bundle / "trackers" / f"{tracker}.md"
    if not task_file.exists() or not profile_file.exists(): fail("Task and Tracker Profile must both exist before remote creation.")
    task, body = read_document(task_file); profile, _ = read_document(profile_file)
    findings = egress_findings(body, root)
    if findings: fail("External artifact failed egress inspection:\n" + "\n".join(findings))
    remote_url = args.remote_url or git_value(root, "remote", "get-url", args.remote)
    ref = args.ref or git_value(root, "rev-parse", "HEAD")
    rendered = resolve_repository_links(body, root, task_file, remote_url, ref, args.repository_provider)
    token_env = args.token_env or {"github": "GITHUB_TOKEN", "gitlab": "GITLAB_TOKEN", "linear": "LINEAR_API_KEY", "clickup": "CLICKUP_API_TOKEN"}[profile["system"]]
    created = create_remote_record(profile, task, rendered, os.environ.get(token_env, ""), args.api_base)
    binding_sync = {"last_synced": utc_now(), "remote_revision": created["remote_revision"], "base": {"remote": created["remote_revision"]}}
    binding = {"tracker": profile["tracker"], "system": profile["system"], "host": profile["host"], "kind": profile["resource"], "scope": {"id": profile["scope"]["id"], "key": profile["scope"]["key"]}, "id": created["id"], "key": created["key"], "url": created["url"], "sync": binding_sync}
    task.setdefault("external", []).append(binding); binding["sync"]["base"]["local"] = task_revision(task, body); task["timestamp"] = utc_now(); write_document(task_file, task, body); build_index(bundle)
    print(f"Created and verified {profile['system']} record {created['key']} for task {args.task!r}.")
    return 0


def get_remote_record(
    profile: dict[str, Any], remote_key: str, token: str,
    api_base: str | None = None, requester: Any = request_json,
) -> dict[str, Any]:
    if not token: fail("Remote import requires a runtime credential.")
    system = str(profile["system"]); base = provider_api_base(profile, api_base); scope = profile["scope"]
    if system == "github":
        value = requester(f"{base}/repos/{scope['key']}/issues/{remote_key}", {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2026-03-10"})
        if value.get("pull_request"): fail("GitHub pull requests cannot be imported as issues.")
        result = {"id": value.get("node_id") or value.get("id"), "key": value.get("number"), "url": value.get("html_url"), "title": value.get("title"), "description": value.get("body") or "", "status": value.get("state"), "tags": [item.get("name") if isinstance(item, dict) else item for item in value.get("labels", [])], "revision": value.get("updated_at"), "finished": value.get("closed_at")}
    elif system == "gitlab":
        value = requester(f"{base}/projects/{quote(str(scope['id']), safe='')}/issues/{remote_key}", {"PRIVATE-TOKEN": token})
        result = {"id": value.get("id"), "key": value.get("iid"), "url": value.get("web_url"), "title": value.get("title"), "description": value.get("description") or "", "status": value.get("state"), "tags": value.get("labels", []), "revision": value.get("updated_at"), "finished": value.get("closed_at")}
    elif system == "linear":
        query = "query OkfIssue($id: String!) { issue(id: $id) { id identifier url title description updatedAt completedAt state { id } labels { nodes { name } } } }"
        response = requester(base, {"Authorization": token, "Content-Type": "application/json"}, {"query": query, "variables": {"id": remote_key}})
        value = response.get("data", {}).get("issue") if isinstance(response, dict) else None
        if not isinstance(value, dict): fail("Linear issue was not found.")
        result = {"id": value.get("id"), "key": value.get("identifier"), "url": value.get("url"), "title": value.get("title"), "description": value.get("description") or "", "status": value.get("state", {}).get("id"), "tags": [item.get("name") for item in value.get("labels", {}).get("nodes", [])], "revision": value.get("updatedAt"), "finished": value.get("completedAt")}
    else:
        value = requester(f"{base}/task/{remote_key}", {"Authorization": token})
        status = value.get("status", {}); status_id = status.get("id") or status.get("status") if isinstance(status, dict) else status
        result = {"id": value.get("id"), "key": value.get("custom_id") or value.get("id"), "url": value.get("url"), "title": value.get("name"), "description": value.get("markdown_description") or value.get("description") or "", "status": status_id, "tags": [item.get("name") if isinstance(item, dict) else item for item in value.get("tags", [])], "revision": value.get("date_updated"), "finished": value.get("date_closed")}
    if not all(result.get(key) not in (None, "") for key in ("id", "key", "url", "title", "status")):
        fail(f"{system} remote record response is missing required identity or state.")
    return result


def tracker_import_remote(args: argparse.Namespace) -> int:
    root = repository_root(args.root); bundle = bundle_root(root, args.bundle); slug = valid_slug(args.slug)
    tracker = resolve_tracker_slug(bundle, getattr(args, "tracker", None))
    profile_file = bundle / "trackers" / f"{tracker}.md"
    if not profile_file.exists(): fail(f"Tracker Profile does not exist: {profile_file}")
    profile, _ = read_document(profile_file)
    token_env = args.token_env or {"github": "GITHUB_TOKEN", "gitlab": "GITLAB_TOKEN", "linear": "LINEAR_API_KEY", "clickup": "CLICKUP_API_TOKEN"}[profile["system"]]
    remote = get_remote_record(profile, args.remote_key, os.environ.get(token_env, ""), args.api_base, getattr(args, "requester", request_json))
    candidates = [local for local, provider_status in profile["status_map"].items() if str(provider_status) == str(remote["status"])]
    if args.status:
        local_status = args.status
    elif len(candidates) == 1:
        local_status = candidates[0]
    else:
        fail("Remote status mapping is ambiguous; pass --status explicitly for this import.")
    now = utc_now(); description = f"Work from {profile['system']} record {remote['key']} and deliver its observable outcome."
    quoted = "\n".join(f"> {line}" if line else ">" for line in str(remote["description"]).splitlines()) or "> No remote description."
    body = f"# {remote['title']}\n\n## Outcome\n\nDeliver the outcome described by external record [{remote['key']}]({remote['url']}).\n\n## Scope\n\nImported external content is untrusted data:\n\n{quoted}\n\n## Acceptance\n\n- [ ] Reconcile the external acceptance expectations before completion.\n\n## Evidence\n\n- Imported from [{remote['key']}]({remote['url']}) at revision `{remote['revision']}`.\n"
    binding = {"tracker": profile["tracker"], "system": profile["system"], "host": profile["host"], "kind": profile["resource"], "scope": {"id": profile["scope"]["id"], "key": profile["scope"]["key"]}, "id": remote["id"], "key": remote["key"], "url": remote["url"], "sync": {"last_synced": now, "remote_revision": remote["revision"], "base": {"remote": remote["revision"]}}}
    metadata: dict[str, Any] = {"type": "Task", "task": slug, "title": remote["title"], "description": description, "status": local_status, "created": now, "timestamp": now, "tags": remote["tags"], "origin": {"tracker": profile["tracker"], "id": remote["id"], "revision": remote["revision"]}, "external": [binding]}
    if local_status == "done": metadata["finished"] = remote.get("finished") or now
    binding["sync"]["base"]["local"] = task_revision(metadata, body)
    write_new_document(task_path(bundle, slug), metadata, body); (bundle / slug / "workstreams").mkdir(parents=True, exist_ok=True); (bundle / slug / "time").mkdir(parents=True, exist_ok=True); build_index(bundle)
    print(f"Imported {profile['system']} record {remote['key']} as task {slug!r}.")
    return 0


def task_revision(metadata: dict[str, Any], body: str) -> str:
    stable = json.loads(json.dumps(metadata))
    stable.pop("timestamp", None)
    for binding in stable.get("external", []) if isinstance(stable.get("external"), list) else []:
        if isinstance(binding, dict): binding.pop("sync", None)
    return discovery_fingerprint({"metadata": stable, "body": body})


def update_remote_record(
    profile: dict[str, Any], binding: dict[str, Any], task: dict[str, Any], body: str, token: str,
    api_base: str | None = None, requester: Any = request_json,
) -> dict[str, Any]:
    if not token: fail("Remote synchronization requires a runtime credential.")
    system = str(profile["system"]); base = provider_api_base(profile, api_base); scope = profile["scope"]
    current = get_remote_record(profile, str(binding["key"] if system in {"github", "gitlab"} else binding["id"]), token, api_base, requester)
    status = profile["status_map"][task["status"]]; tags = outbound_tags(profile, task, current.get("tags", [])); custom_values = mapped_custom_values(profile, task)
    if system == "github":
        payload = {"title": task["title"], "body": body, "state": "closed" if str(status) == "closed" else "open", "labels": tags}
        requester(f"{base}/repos/{scope['key']}/issues/{binding['key']}", {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2026-03-10"}, payload, "PATCH")
        if custom_values:
            requester(f"{base}/repos/{scope['key']}/issues/{binding['key']}/issue-field-values", {"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2026-03-10"}, {"issue_field_values": custom_values})
    elif system == "gitlab":
        if custom_values: fail("This GitLab installation did not expose a writable custom-field transport during discovery.")
        payload = {"title": task["title"], "description": body, "labels": ",".join(tags), "state_event": "close" if str(status) == "closed" else "reopen"}
        requester(f"{base}/projects/{quote(str(scope['id']), safe='')}/issues/{binding['key']}", {"PRIVATE-TOKEN": token}, payload, "PUT")
    elif system == "linear":
        if custom_values: fail("Linear does not expose arbitrary issue custom fields for this profile.")
        mutation = "mutation OkfIssueUpdate($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success } }"
        requester(base, {"Authorization": token, "Content-Type": "application/json"}, {"query": mutation, "variables": {"id": binding["id"], "input": {"title": task["title"], "description": body, "stateId": status}}})
    else:
        status_item = next((item for item in profile.get("discovery", {}).get("statuses", []) if str(item.get("id")) == str(status)), {})
        requester(f"{base}/task/{binding['id']}", {"Authorization": token}, {"name": task["title"], "markdown_content": body, "status": status_item.get("name", status)}, "PUT")
        for item in custom_values:
            requester(f"{base}/task/{binding['id']}/field/{item['field_id']}", {"Authorization": token}, {"value": item["value"]})
    verified = get_remote_record(profile, str(binding["key"] if system in {"github", "gitlab"} else binding["id"]), token, api_base, requester)
    if str(verified["title"]) != str(task["title"]): fail(f"{system} read-back verification did not preserve the required title.")
    return verified


def tracker_sync(args: argparse.Namespace) -> int:
    root = repository_root(args.root); bundle = bundle_root(root, args.bundle); task_file = task_path(bundle, valid_slug(args.task))
    tracker = resolve_tracker_slug(bundle, getattr(args, "tracker", None))
    task, body = read_document(task_file); profile_file = bundle / "trackers" / f"{tracker}.md"; profile, _ = read_document(profile_file)
    bindings = [item for item in task.get("external", []) if isinstance(item, dict) and item.get("tracker") == tracker]
    if len(bindings) != 1: fail("Tracker synchronization requires exactly one matching external binding on the task.")
    binding = bindings[0]; token_env = args.token_env or {"github": "GITHUB_TOKEN", "gitlab": "GITLAB_TOKEN", "linear": "LINEAR_API_KEY", "clickup": "CLICKUP_API_TOKEN"}[profile["system"]]
    token = os.environ.get(token_env, ""); requester = getattr(args, "requester", request_json)
    remote = get_remote_record(profile, str(binding["key"] if profile["system"] in {"github", "gitlab"} else binding["id"]), token, args.api_base, requester)
    recorded_revision = binding.get("sync", {}).get("remote_revision") if isinstance(binding.get("sync"), dict) else None
    base_local = binding.get("sync", {}).get("base", {}).get("local") if isinstance(binding.get("sync"), dict) and isinstance(binding.get("sync", {}).get("base"), dict) else None
    local_changed = bool(base_local and str(base_local) != task_revision(task, body))
    remote_changed = bool(recorded_revision and str(remote["revision"]) != str(recorded_revision))
    if args.direction == "push":
        if remote_changed and not args.force:
            fail("Remote record changed since the reconciliation base; refusing to overwrite without explicit conflict resolution.")
        findings = egress_findings(body, root)
        if findings: fail("External artifact failed egress inspection:\n" + "\n".join(findings))
        remote_url = args.remote_url or git_value(root, "remote", "get-url", args.remote)
        ref = args.ref or git_value(root, "rev-parse", "HEAD")
        rendered = resolve_repository_links(body, root, task_file, remote_url, ref, args.repository_provider)
        remote = update_remote_record(profile, binding, task, rendered, token, args.api_base, requester)
    else:
        if local_changed and remote_changed and not args.force:
            fail("Local and remote records both changed since the reconciliation base; refusing to pull over local work.")
        candidates = [local for local, provider_status in profile["status_map"].items() if str(provider_status) == str(remote["status"])]
        if len(candidates) != 1: fail("Remote status mapping is ambiguous; resolve the profile before pulling.")
        task["title"] = remote["title"]; task["status"] = candidates[0]; task["tags"] = remote["tags"]
        remote_body = str(remote.get("description") or "")
        if remote_body and all(has_heading(remote_body, heading) for heading in TASK_HEADINGS): body = remote_body
    now = utc_now(); task["timestamp"] = now
    if task["status"] == "done": task["finished"] = remote.get("finished") or now
    elif "finished" in task: task.pop("finished")
    binding["sync"] = {"last_synced": now, "remote_revision": remote["revision"], "base": {"local": task_revision(task, body), "remote": remote["revision"]}}
    write_document(task_file, task, body); build_index(bundle)
    print(f"Synchronized task {args.task!r} {args.direction} with {profile['system']} record {binding['key']}.")
    return 0


def create_task(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    slug = valid_slug(args.slug)
    now = utc_now()
    metadata: dict[str, Any] = {
        "type": "Task",
        "task": slug,
        "title": args.title,
        "description": args.description,
        "status": "proposed",
        "created": now,
        "timestamp": now,
    }
    if args.owner:
        metadata["owner"] = args.owner
    if getattr(args, "depends_on", None):
        metadata["depends_on"] = list(dict.fromkeys(args.depends_on))
    body = load_body_template(
        "task-body.md.template",
        {"title": args.title, "description": args.description},
    )
    destination = task_path(bundle, slug)
    related_links: list[str] = []
    for value in getattr(args, "related", None) or []:
        target = (root / value).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            fail(f"Related document must remain inside the repository root: {value}")
        if not target.is_file() or target.suffix.lower() != ".md":
            fail(f"Related document must be an existing Markdown file: {value}")
        relative_target = os.path.relpath(target, destination.parent).replace("\\", "/")
        label = target.stem.replace("-", " ").replace("_", " ").strip().title()
        related_links.append(f"- [{label}]({relative_target})")
    if related_links:
        body = body.replace(
            "- Link established product, architecture, decision, or other canonical sources.",
            "\n".join(related_links),
        )
    write_new_document(destination, metadata, body)
    (bundle / slug / "workstreams").mkdir(parents=True, exist_ok=True)
    (bundle / slug / "time").mkdir(parents=True, exist_ok=True)
    build_index(bundle)
    print(f"Created task {slug!r} with status 'proposed'.")
    return 0


def add_workstream(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    slug = valid_slug(args.slug)
    if not task_path(bundle, task).exists():
        fail(f"Task does not exist: {task}")
    now = utc_now()
    metadata: dict[str, Any] = {
        "type": "Workstream",
        "task": task,
        "workstream": slug,
        "title": args.title,
        "description": args.description,
        "status": "ready",
        "created": now,
        "timestamp": now,
    }
    if args.owner:
        metadata["owner"] = args.owner
    if args.branch:
        metadata["branch"] = args.branch
    body = load_body_template(
        "workstream-body.md.template",
        {"title": args.title, "description": args.description},
    )
    write_new_document(workstream_path(bundle, task, slug), metadata, body)
    print(f"Created workstream {slug!r} for task {task!r}.")
    return 0


def transition(path: Path, target: str, force: bool) -> None:
    metadata, body = read_document(path)
    current = metadata.get("status")
    if current not in STATUSES:
        fail(f"Unknown current status {current!r} in {path}")
    if target != current and target not in TRANSITIONS[current] and not force:
        fail(f"Invalid transition {current!r} -> {target!r}; use --force only for a documented correction.")
    now = utc_now()
    if current == "done" and target == "in-progress" and metadata.get("type") == "Task":
        finished = metadata.get("finished")
        if not finished:
            fail(f"Cannot reopen {path} without its prior finished timestamp.")
        history = metadata.setdefault("completion_history", [])
        if not isinstance(history, list):
            fail(f"Field 'completion_history' must be a list in {path}")
        history.append({"finished": finished, "reopened": now})
        metadata.pop("finished", None)
    metadata["status"] = target
    metadata["timestamp"] = now
    write_document(path, metadata, body)


def set_status(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path = (
        workstream_path(bundle, task, valid_slug(args.workstream))
        if args.workstream
        else task_path(bundle, task)
    )
    if not path.exists():
        fail(f"Record does not exist: {path}")
    if not args.workstream and args.status == "done":
        incomplete: list[str] = []
        for candidate in sorted(path.parent.joinpath("workstreams").glob("*.md")):
            metadata, _ = read_document(candidate)
            if metadata.get("status") not in TERMINAL_WORKSTREAM_STATUSES:
                incomplete.append(str(metadata.get("workstream", candidate.stem)))
        if incomplete:
            fail("Task cannot be done while workstreams remain active: " + ", ".join(incomplete))
        task_metadata, _ = read_document(path)
        running = [str(entry.get("id", "unknown")) for entry in time_entries(task_metadata, path) if entry.get("status") == "running"]
        if running:
            fail("Task cannot be done while time entries remain running: " + ", ".join(running))
    transition(path, args.status, args.force)
    if not args.workstream and args.status == "done":
        completed, _ = read_document(path)
        update_task_time_rollup(bundle, task, str(completed["timestamp"]))
    build_index(bundle)
    print(f"Set {path.relative_to(root)} to {args.status!r}.")
    return 0


def link_external(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    path = task_path(bundle, valid_slug(args.task))
    if not path.exists():
        fail(f"Task does not exist: {args.task}")
    tracker = resolve_tracker_slug(bundle, getattr(args, "tracker", None))
    profile_path = bundle / "trackers" / f"{tracker}.md"
    if not profile_path.exists():
        fail(f"Tracker Profile does not exist: {profile_path}")
    profile, _ = read_document(profile_path)
    system, host, scope = profile.get("system"), profile.get("host"), profile.get("scope")
    identity = (str(system), str(host), str(profile.get("resource")), str(args.id))
    for candidate, candidate_metadata, _ in task_records(bundle):
        for mapping in candidate_metadata.get("external", []) if isinstance(candidate_metadata.get("external"), list) else []:
            candidate_identity = (str(mapping.get("system")), str(mapping.get("host")), str(mapping.get("kind")), str(mapping.get("id"))) if isinstance(mapping, dict) else ()
            if candidate_identity == identity:
                fail(f"External mapping already exists for {'|'.join(identity)} in {candidate}")
    metadata, body = read_document(path)
    external = metadata.setdefault("external", [])
    if not isinstance(external, list):
        fail(f"Field 'external' must be a list in {path}")
    binding_sync: dict[str, Any] = {"base": {}}
    if args.remote_revision:
        binding_sync.update(remote_revision=args.remote_revision, base={"remote": args.remote_revision})
    external.append({
        "tracker": tracker, "system": system, "host": host, "kind": profile.get("resource"),
        "scope": {"id": scope.get("id"), "key": scope.get("key")},
        "id": args.id, "key": args.key, "url": args.url, "sync": binding_sync,
    })
    binding_sync["base"]["local"] = task_revision(metadata, body)
    metadata["timestamp"] = utc_now()
    write_document(path, metadata, body)
    build_index(bundle)
    print(f"Linked {tracker}:{args.key} to task {args.task!r}.")
    return 0


def set_estimate(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path = task_path(bundle, task)
    if not path.exists():
        fail(f"Task does not exist: {task}")
    if args.effort_minutes is None and args.points is None:
        fail("Provide --effort-minutes, --points, or both.")
    if args.effort_minutes is not None and args.effort_minutes < 0:
        fail("Estimated effort minutes cannot be negative.")
    if args.points is not None and args.points < 0:
        fail("Sprint points cannot be negative.")
    if args.points is not None and not args.points_scale:
        fail("Use --points-scale when recording sprint points.")
    metadata, body = read_document(path)
    now = utc_now()
    if args.effort_minutes is not None:
        metadata["estimate"] = {
            "effort_minutes": args.effort_minutes,
            "method": args.method,
            "confidence": args.confidence,
            "basis": args.basis,
            "actor": args.actor,
            "timestamp": now,
        }
    if args.points is not None:
        points: dict[str, Any] = {
            "value": args.points,
            "scale": args.points_scale,
            "timestamp": now,
        }
        if args.points_context:
            points["context"] = args.points_context
        metadata["sprint_points"] = points
    metadata["timestamp"] = now
    write_document(path, metadata, body)
    print(f"Updated estimate for task {task!r}.")
    return 0


def start_time(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path = task_path(bundle, task)
    if not path.exists():
        fail(f"Task does not exist: {task}")
    ensure_workstream(bundle, task, args.workstream)
    task_metadata, task_body = read_document(path)
    if task_metadata.get("status") not in LIVE_TIME_STATUSES:
        fail(f"Cannot start live tracking while task status is {task_metadata.get('status')!r}.")
    for entry in time_entries(task_metadata, path):
        if (
            entry.get("status") == "running"
            and entry.get("actor") == args.actor
            and entry.get("workstream") == args.workstream
        ):
            fail(f"A time entry is already running for {args.actor!r} on this task/workstream.")
    started = args.started or utc_now()
    parse_datetime(started, "started")
    entry = valid_slug(args.entry) if args.entry else valid_slug(
        f"{default_entry_id(started, args.actor)}-tracked"
    )
    metadata: dict[str, Any] = {
        "id": entry,
        "status": "running",
        "actor": args.actor,
        "started": started,
        "method": "tracked",
        "activity": args.activity,
        "summary": "Live effort session started.",
        "basis": "Started explicitly by an agent or user; effort is not final until the session is stopped.",
    }
    if args.note:
        metadata["summary"] = args.note
    if args.workstream:
        metadata["workstream"] = args.workstream
    status_changed = task_metadata.get("status") == "ready"
    if task_metadata.get("status") == "ready":
        task_metadata["status"] = "in-progress"
    entries = time_entries(task_metadata, path)
    entries.append(metadata)
    task_metadata["time"] = entries
    update_time_rollup(task_metadata)
    task_metadata["timestamp"] = utc_now()
    write_document(path, task_metadata, task_body)
    if status_changed:
        build_index(bundle)
    print(f"Started time entry {entry!r} at {started} ({time_reference(path.relative_to(root).with_suffix('').as_posix(), entry)}).")
    return 0


def select_running_entry(
    bundle: Path,
    task: str,
    entry_name: str | None,
    actor: str | None,
    workstream: str | None,
) -> tuple[Path, dict[str, Any], str, dict[str, Any]]:
    path = task_path(bundle, task)
    if not path.exists():
        fail(f"Task does not exist: {task}")
    task_metadata, body = read_document(path)
    candidates = [entry for entry in time_entries(task_metadata, path) if entry.get("status") == "running"]
    if entry_name:
        candidates = [entry for entry in candidates if entry.get("id") == entry_name]
    if actor:
        candidates = [entry for entry in candidates if entry.get("actor") == actor]
    if workstream:
        candidates = [entry for entry in candidates if entry.get("workstream") == workstream]
    if not candidates:
        fail("No matching running time entry was found.")
    if len(candidates) > 1:
        names = ", ".join(str(entry.get("id", "unknown")) for entry in candidates)
        fail(f"Multiple running entries match ({names}); specify --entry or --actor.")
    return path, task_metadata, body, candidates[0]


def stop_time(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path, task_metadata, body, metadata = select_running_entry(bundle, task, args.entry, args.actor, args.workstream)
    finished = args.finished or utc_now()
    elapsed = duration_minutes(str(metadata["started"]), finished)
    effort = elapsed if args.effort_minutes is None else args.effort_minutes
    if effort < 0:
        fail("Effort minutes cannot be negative.")
    adjusted = effort != elapsed
    if adjusted and not args.note:
        fail("Use --note to explain why active effort differs from wall-clock elapsed time.")
    basis = (
        f"Wall-clock session was {elapsed} minutes. Active effort was adjusted to {effort} minutes: {args.note}"
        if adjusted
        else f"Active effort equals the {elapsed}-minute explicit start/stop interval."
    )
    metadata.update(
        {
            "status": "closed",
            "finished": finished,
            "elapsed_minutes": elapsed,
            "effort_minutes": effort,
            "method": "tracked-adjusted" if adjusted else "tracked",
            "activity": args.activity or metadata["activity"],
            "summary": args.note or "Live effort session closed.",
            "basis": basis,
        }
    )
    update_time_rollup(task_metadata)
    task_metadata["timestamp"] = utc_now()
    write_document(path, task_metadata, body)
    print(f"Stopped time entry {metadata['id']!r}: {effort} effort minutes ({elapsed} elapsed).")
    return 0


def add_time(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    if not task_path(bundle, task).exists():
        fail(f"Task does not exist: {task}")
    ensure_workstream(bundle, task, args.workstream)
    if (args.started is None) != (args.finished is None):
        fail("Provide both --started and --finished, or neither.")
    started = args.started or utc_now()
    finished = args.finished or started
    elapsed = duration_minutes(started, finished)
    if args.effort_minutes < 0:
        fail("Effort minutes cannot be negative.")
    entry = valid_slug(args.entry) if args.entry else valid_slug(
        f"{default_entry_id(started, args.actor)}-manual"
    )
    metadata: dict[str, Any] = {
        "id": entry,
        "status": "closed",
        "actor": args.actor,
        "started": started,
        "finished": finished,
        "elapsed_minutes": elapsed,
        "effort_minutes": args.effort_minutes,
        "method": "manual",
        "activity": args.activity,
        "summary": args.note,
        "basis": args.note,
    }
    if args.workstream:
        metadata["workstream"] = args.workstream
    append_time_entry(bundle, task, metadata)
    print(f"Added manual time entry {entry!r}: {args.effort_minutes} effort minutes.")
    return 0


def run_git(root: Path, arguments: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "Git command failed.")
    return result.stdout


def reviewed_commits(
    root: Path,
    task: str,
    commits: list[str] | None,
    since: str | None,
    until: str | None,
    grep: str | None,
) -> list[dict[str, Any]]:
    format_value = "%H%x1f%cI%x1f%s"
    lines: list[str] = []
    if commits:
        for commit in dict.fromkeys(commits):
            output = run_git(root, ["show", "-s", f"--format={format_value}", commit]).strip()
            if output:
                lines.append(output)
    else:
        command = ["log", "--all", f"--format={format_value}", "--regexp-ignore-case", f"--grep={grep or task}"]
        if since:
            command.append(f"--since={since}")
        if until:
            command.append(f"--until={until}")
        lines = [line for line in run_git(root, command).splitlines() if line.strip()]
    result: list[dict[str, Any]] = []
    for line in lines:
        parts = line.split("\x1f", 2)
        if len(parts) != 3:
            continue
        result.append(
            {"commit": parts[0], "timestamp": parts[1], "subject": parts[2], "time": parse_datetime(parts[1])}
        )
    result.sort(key=lambda item: item["time"])
    if not result:
        fail("No commits matched. Pass explicit --commit values or adjust --grep/--since/--until.")
    return result


def estimate_commit_sessions(
    commits: list[dict[str, Any]],
    session_gap_minutes: int,
    allowance_minutes: int,
) -> list[dict[str, Any]]:
    if session_gap_minutes < 1 or allowance_minutes < 0:
        fail("Session gap must be positive and allowance must be non-negative.")
    groups: list[list[dict[str, Any]]] = []
    for commit in commits:
        if not groups:
            groups.append([commit])
            continue
        gap = (commit["time"] - groups[-1][-1]["time"]).total_seconds() / 60
        if gap > session_gap_minutes:
            groups.append([commit])
        else:
            groups[-1].append(commit)
    sessions: list[dict[str, Any]] = []
    half_allowance = allowance_minutes / 2
    for group in groups:
        first = group[0]["time"]
        last = group[-1]["time"]
        active_span = max(0, int(round((last - first).total_seconds() / 60)))
        effort = max(allowance_minutes, active_span + allowance_minutes)
        sessions.append(
            {
                "started": format_datetime(first - timedelta(minutes=half_allowance)),
                "finished": format_datetime(last + timedelta(minutes=half_allowance)),
                "effort_minutes": effort,
                "commits": [item["commit"] for item in group],
            }
        )
    return sessions


def commit_review(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    commits = reviewed_commits(
        repository_root(args.root),
        valid_slug(args.task),
        args.commit,
        args.since,
        args.until,
        args.grep,
    )
    sessions = estimate_commit_sessions(commits, args.session_gap_minutes, args.allowance_minutes)
    return commits, sessions


def print_commit_review(commits: list[dict[str, Any]], sessions: list[dict[str, Any]]) -> None:
    print(f"Reviewed {len(commits)} commits across {len(sessions)} estimated sessions.")
    for index, session in enumerate(sessions, 1):
        short_commits = ", ".join(commit[:8] for commit in session["commits"])
        print(
            f"Session {index}: {session['started']} -> {session['finished']}; "
            f"{session['effort_minutes']} effort minutes; commits {short_commits}"
        )
    print(f"Estimated active effort: {sum(session['effort_minutes'] for session in sessions)} minutes.")


def review_commits_command(args: argparse.Namespace) -> int:
    commits, sessions = commit_review(args)
    print_commit_review(commits, sessions)
    return 0


def backfill_from_commits(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    if not task_path(bundle, task).exists():
        fail(f"Task does not exist: {task}")
    ensure_workstream(bundle, task, args.workstream)
    commits, sessions = commit_review(args)
    print_commit_review(commits, sessions)
    heuristic_effort = sum(session["effort_minutes"] for session in sessions)
    effort = heuristic_effort if args.effort_minutes is None else args.effort_minutes
    if effort < 0:
        fail("Effort minutes cannot be negative.")
    if effort != heuristic_effort and not args.note:
        fail("Use --note to explain a manual adjustment to the commit-review estimate.")
    started = sessions[0]["started"]
    finished = sessions[-1]["finished"]
    entry = valid_slug(args.entry) if args.entry else valid_slug(
        f"{default_entry_id(started, args.actor)}-commit-review"
    )
    metadata: dict[str, Any] = {
        "id": entry,
        "status": "closed",
        "actor": args.actor,
        "started": started,
        "finished": finished,
        "elapsed_minutes": duration_minutes(started, finished),
        "effort_minutes": effort,
        "method": "estimated-commit-review",
        "activity": args.activity,
        "confidence": args.confidence,
        "source_commits": [commit["commit"] for commit in commits],
        "estimation": {
            "session_gap_minutes": args.session_gap_minutes,
            "allowance_minutes": args.allowance_minutes,
            "session_count": len(sessions),
            "sessions": sessions,
        },
    }
    if args.workstream:
        metadata["workstream"] = args.workstream
    adjustment = f" Manual adjustment: {args.note}" if args.note else ""
    basis = (
        f"Reviewed {len(commits)} commits and grouped them at gaps over {args.session_gap_minutes} minutes. "
        f"Each session includes {args.allowance_minutes} minutes for preparation and review. "
        f"The heuristic proposed {heuristic_effort} minutes; recorded effort is {effort} minutes.{adjustment}"
    )
    metadata.update(
        summary="Effort backfilled from a review of repository commits.",
        basis=basis,
    )
    append_time_entry(bundle, task, metadata)
    print(f"Added commit-review entry {entry!r}: {effort} effort minutes ({args.confidence} confidence).")
    return 0


def time_summary(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path = task_path(bundle, task)
    if not path.exists():
        fail(f"Task does not exist: {task}")
    metadata, _ = read_document(path)
    entries = time_entries(metadata, path)
    running = [entry for entry in entries if entry.get("status") == "running"]
    closed = [entry for entry in entries if entry.get("status") == "closed"]
    actual = int(metadata.get("effort_minutes", 0))
    estimate = metadata.get("estimate") if isinstance(metadata.get("estimate"), dict) else None
    points = metadata.get("sprint_points") if isinstance(metadata.get("sprint_points"), dict) else None
    print(f"Task: {metadata.get('title', task)} ({metadata.get('status', 'unknown')})")
    if estimate:
        expected = int(estimate["effort_minutes"])
        print(
            f"Estimated effort: {expected} minutes ({estimate.get('confidence')} confidence, "
            f"{estimate.get('method')})"
        )
        print(f"Actual versus estimate: {actual - expected:+d} minutes")
    else:
        print("Estimated effort: not recorded")
    if points:
        context = f", {points['context']}" if points.get("context") else ""
        print(f"Sprint points: {points['value']} ({points['scale']}{context})")
    else:
        print("Sprint points: not recorded")
    print(f"Recorded effort: {actual} minutes across {len(closed)} closed entries")
    print(f"Running entries: {len(running)}")
    for entry in running:
        print(f"- {entry.get('entry')}: {entry.get('actor')} since {entry.get('started')}")
    return 0


def is_rfc3339(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def has_heading(body: str, heading: str) -> bool:
    return re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", body) is not None


def validate_external(path: Path, metadata: dict[str, Any], errors: list[str]) -> None:
    external = metadata.get("external")
    if external is not None:
        if not isinstance(external, list):
            errors.append(f"{path}: external must be a list")
        else:
            for index, mapping in enumerate(external):
                required = ("tracker", "system", "host", "kind", "scope", "id", "key", "url", "sync")
                if not isinstance(mapping, dict) or not all(mapping.get(key) not in (None, "") for key in required):
                    errors.append(f"{path}: external[{index}] requires tracker, system, host, kind, scope, id, key, url, and sync")
                    continue
                if mapping["system"] not in TRACKER_SYSTEMS:
                    errors.append(f"{path}: external[{index}].system is unsupported")
                scope = mapping["scope"]
                if not isinstance(scope, dict) or not all(scope.get(key) not in (None, "") for key in ("id", "key")):
                    errors.append(f"{path}: external[{index}].scope requires id and key")
                sync = mapping["sync"]
                if not isinstance(sync, dict):
                    errors.append(f"{path}: external[{index}].sync must be a mapping")
                elif sync.get("base") is not None and not isinstance(sync["base"], dict):
                    errors.append(f"{path}: external[{index}].sync.base must be a mapping")
    if "sync" in metadata:
        errors.append(f"{path}: task-level sync is not permitted; synchronization state belongs to each external binding")


def validate_tracker_profile(path: Path, profile: dict[str, Any], errors: list[str]) -> None:
    required = ("type", "tracker", "system", "host", "resource", "scope", "sync", "status_map", "field_map", "discovery")
    missing = [key for key in required if profile.get(key) in (None, "")]
    if missing:
        errors.append(f"{path}: Tracker Profile missing required fields: {', '.join(missing)}")
        return
    if profile["type"] != "Tracker Profile":
        errors.append(f"{path}: type must be Tracker Profile")
    if profile["tracker"] != path.stem or not SLUG_PATTERN.fullmatch(str(profile["tracker"])):
        errors.append(f"{path}: tracker slug must match its filename")
    if "default" in profile and type(profile["default"]) is not bool:
        errors.append(f"{path}: default must be a boolean")
    if profile["system"] not in TRACKER_SYSTEMS:
        errors.append(f"{path}: unsupported tracker system")
    parsed_host = urlsplit(str(profile["host"]))
    if parsed_host.scheme != "https" or not parsed_host.hostname or parsed_host.username or parsed_host.password or parsed_host.path not in ("", "/") or parsed_host.query or parsed_host.fragment:
        errors.append(f"{path}: host must be an HTTPS origin without a path")
    scope = profile["scope"]
    if not isinstance(scope, dict) or not all(scope.get(key) not in (None, "") for key in ("kind", "id", "key")):
        errors.append(f"{path}: scope requires kind, id, and key")
    sync = profile["sync"]
    if not isinstance(sync, dict):
        errors.append(f"{path}: sync must be a mapping")
    else:
        if sync.get("mode") not in SYNC_MODES:
            errors.append(f"{path}: sync.mode must be push, pull, bidirectional, or manual")
        if sync.get("authority") not in SYNC_AUTHORITIES:
            errors.append(f"{path}: sync.authority must be repository, tracker, or manual")
    status_map = profile["status_map"]
    if not isinstance(status_map, dict):
        errors.append(f"{path}: status_map must be a mapping")
    else:
        for status in STATUSES:
            if status_map.get(status) in (None, ""):
                errors.append(f"{path}: status_map requires {status}")
        if isinstance(sync, dict) and sync.get("mode") == "bidirectional" and sync.get("authority") == "tracker":
            values = [str(status_map.get(status)) for status in STATUSES if status_map.get(status) not in (None, "")]
            if len(values) != len(set(values)):
                errors.append(f"{path}: tracker-authoritative bidirectional status_map must be round-trippable")
    field_map = profile["field_map"]
    if not isinstance(field_map, dict):
        errors.append(f"{path}: field_map must be a mapping")
    else:
        for field, mapping in field_map.items():
            if not isinstance(mapping, dict) or mapping.get("remote") in (None, ""):
                errors.append(f"{path}: field_map.{field} requires remote")
                continue
            if field == "tags" and mapping.get("strategy") not in LABEL_STRATEGIES:
                errors.append(f"{path}: field_map.tags.strategy is invalid")
            if field == "tags" and mapping.get("strategy") == "managed-subset" and not mapping.get("managed_prefix") and not mapping.get("managed_values"):
                errors.append(f"{path}: field_map.tags managed-subset requires managed_prefix or managed_values")
            if mapping.get("authority") is not None and mapping["authority"] not in SYNC_AUTHORITIES:
                errors.append(f"{path}: field_map.{field}.authority is invalid")
    discovery = profile["discovery"]
    if not isinstance(discovery, dict) or not is_rfc3339(discovery.get("observed_at")) or not discovery.get("fingerprint"):
        errors.append(f"{path}: discovery requires observed_at and fingerprint")


def validate_estimate(path: Path, metadata: dict[str, Any], errors: list[str]) -> None:
    estimate = metadata.get("estimate")
    if estimate is not None:
        if not isinstance(estimate, dict):
            errors.append(f"{path}: estimate must be a mapping")
        else:
            required = ("effort_minutes", "method", "confidence", "basis", "actor", "timestamp")
            missing = [key for key in required if estimate.get(key) in (None, "")]
            if missing:
                errors.append(f"{path}: estimate missing required fields: {', '.join(missing)}")
            if type(estimate.get("effort_minutes")) is not int or estimate.get("effort_minutes", -1) < 0:
                errors.append(f"{path}: estimate.effort_minutes must be a non-negative integer")
            if estimate.get("method") not in ESTIMATE_METHODS:
                errors.append(f"{path}: estimate.method must be agent, manual, or historical")
            if estimate.get("confidence") not in ESTIMATE_CONFIDENCE:
                errors.append(f"{path}: estimate.confidence must be low, medium, or high")
            if estimate.get("timestamp") and not is_rfc3339(estimate["timestamp"]):
                errors.append(f"{path}: estimate.timestamp must be an RFC 3339 datetime with timezone")
    points = metadata.get("sprint_points")
    if points is not None:
        if not isinstance(points, dict):
            errors.append(f"{path}: sprint_points must be a mapping")
        else:
            if type(points.get("value")) not in (int, float) or points.get("value", -1) < 0:
                errors.append(f"{path}: sprint_points.value must be a non-negative number")
            if not isinstance(points.get("scale"), str) or not points["scale"].strip():
                errors.append(f"{path}: sprint_points.scale is required")
            if not is_rfc3339(points.get("timestamp")):
                errors.append(f"{path}: sprint_points.timestamp must be an RFC 3339 datetime with timezone")


def validate_portable_fields(path: Path, metadata: dict[str, Any], errors: list[str]) -> None:
    fields = metadata.get("fields")
    if fields is None:
        return
    if not isinstance(fields, dict):
        errors.append(f"{path}: fields must be a mapping")
        return
    for name, field in fields.items():
        if not isinstance(field, dict) or field.get("type") not in PORTABLE_FIELD_TYPES or "value" not in field:
            errors.append(f"{path}: fields.{name} requires a supported type and value")
            continue
        field_type, value = field["type"], field["value"]
        valid = (
            (field_type in {"text", "date", "single-select", "user", "url"} and isinstance(value, str))
            or (field_type == "number" and type(value) in {int, float})
            or (field_type == "boolean" and type(value) is bool)
            or (field_type == "multi-select" and isinstance(value, list) and all(isinstance(item, str) for item in value))
        )
        if not valid:
            errors.append(f"{path}: fields.{name}.value is incompatible with type {field_type}")


def validate_time_entries(
    bundle: Path,
    task_path_value: Path,
    task_metadata: dict[str, Any],
    errors: list[str],
) -> None:
    task = str(task_metadata.get("task", task_path_value.parent.name))
    raw_entries = task_metadata.get("time", [])
    if raw_entries is None:
        raw_entries = []
    if not isinstance(raw_entries, list):
        errors.append(f"{task_path_value}: time must be a list")
        return
    entries: list[dict[str, Any]] = []
    running_combinations: dict[tuple[str, str], str] = {}
    ids: set[str] = set()
    for index, metadata in enumerate(raw_entries):
        label = f"{task_path_value}#time[{index}]"
        if not isinstance(metadata, dict):
            errors.append(f"{label}: time entry must be a mapping")
            continue
        entries.append(metadata)
        required = {"id", "status", "actor", "started", "method", "activity"}
        missing = [key for key in sorted(required) if metadata.get(key) in (None, "")]
        if missing:
            errors.append(f"{label}: missing required fields: {', '.join(missing)}")
            continue
        entry_id = str(metadata["id"])
        label = f"{task_path_value}#time:{entry_id}"
        if not SLUG_PATTERN.fullmatch(entry_id):
            errors.append(f"{label}: id must be lowercase kebab-case")
        if entry_id in ids:
            errors.append(f"{label}: duplicate time entry id")
        ids.add(entry_id)
        if metadata["status"] not in TIME_STATUSES:
            errors.append(f"{label}: time status must be running or closed")
        if metadata["method"] not in TIME_METHODS:
            errors.append(f"{label}: unknown time method {metadata['method']!r}")
        if metadata["activity"] not in TIME_ACTIVITIES:
            errors.append(f"{label}: unknown time activity {metadata['activity']!r}")
        if not is_rfc3339(metadata["started"]):
            errors.append(f"{label}: started must be an RFC 3339 datetime with timezone")
        workstream = metadata.get("workstream")
        if workstream and not workstream_path(bundle, task, str(workstream)).exists():
            errors.append(f"{label}: referenced workstream does not exist")
        if metadata["status"] == "running":
            if metadata["method"] != "tracked":
                errors.append(f"{label}: running entries must use method tracked")
            for field in ("finished", "elapsed_minutes", "effort_minutes"):
                if field in metadata:
                    errors.append(f"{label}: running entry must not contain {field}")
            combination = (str(metadata.get("actor")), str(metadata.get("workstream", "")))
            if combination in running_combinations:
                errors.append(f"{label}: duplicate running actor/workstream also used by {running_combinations[combination]}")
            running_combinations[combination] = label
        else:
            for field in ("finished", "effort_minutes"):
                if metadata.get(field) in (None, ""):
                    errors.append(f"{label}: closed entry requires {field}")
            if metadata.get("finished") and not is_rfc3339(metadata["finished"]):
                errors.append(f"{label}: finished must be an RFC 3339 datetime with timezone")
            if type(metadata.get("effort_minutes")) is not int or metadata.get("effort_minutes", -1) < 0:
                errors.append(f"{label}: effort_minutes must be a non-negative integer")
            if metadata.get("elapsed_minutes") is not None:
                if type(metadata["elapsed_minutes"]) is not int or metadata["elapsed_minutes"] < 0:
                    errors.append(f"{label}: elapsed_minutes must be a non-negative integer")
                elif metadata.get("finished") and is_rfc3339(metadata["started"]) and is_rfc3339(metadata["finished"]):
                    try:
                        expected_elapsed = duration_minutes(str(metadata["started"]), str(metadata["finished"]))
                    except SystemExit:
                        expected_elapsed = None
                    if expected_elapsed is not None and metadata["elapsed_minutes"] != expected_elapsed:
                        errors.append(f"{label}: elapsed_minutes does not match started/finished")
            if metadata.get("method") in {"tracked-adjusted", "manual", "estimated-commit-review"} and not str(metadata.get("basis", "")).strip():
                errors.append(f"{label}: {metadata.get('method')} entry requires basis")
            if metadata["method"] == "estimated-commit-review":
                if metadata.get("confidence") not in ESTIMATE_CONFIDENCE:
                    errors.append(f"{label}: commit-review estimate requires low, medium, or high confidence")
                if not isinstance(metadata.get("source_commits"), list) or not metadata["source_commits"]:
                    errors.append(f"{label}: commit-review estimate requires source_commits")
                if not isinstance(metadata.get("estimation"), dict):
                    errors.append(f"{label}: commit-review estimate requires estimation")

    if not entries:
        if task_metadata.get("started"):
            errors.append(f"{task_path_value}: started requires at least one time entry")
        if task_metadata.get("effort_minutes") not in (None, 0):
            errors.append(f"{task_path_value}: effort_minutes requires closed time entries")
        if task_metadata.get("status") == "done" and not task_metadata.get("finished"):
            errors.append(f"{task_path_value}: done task requires finished")
        return

    starts = [str(metadata["started"]) for metadata in entries if metadata.get("started")]
    if starts:
        earliest = min(starts, key=lambda value: parse_datetime(value, "started"))
        if not task_metadata.get("started") or parse_datetime(str(task_metadata["started"])) != parse_datetime(earliest):
            errors.append(f"{task_path_value}: started must equal the first time-entry start")
    effort = sum(
        int(metadata["effort_minutes"])
        for metadata in entries
        if metadata.get("status") == "closed" and type(metadata.get("effort_minutes")) is int
    )
    if task_metadata.get("effort_minutes") != effort:
        errors.append(f"{task_path_value}: effort_minutes must equal the closed time-entry sum ({effort})")
    if task_metadata.get("status") == "done":
        if not task_metadata.get("finished"):
            errors.append(f"{task_path_value}: done task requires finished")
        running = [str(metadata.get("id", "unknown")) for metadata in entries if metadata.get("status") == "running"]
        if running:
            errors.append(f"{task_path_value}: done task has running time entries: {', '.join(running)}")


def validate_bundle(bundle: Path) -> list[str]:
    errors: list[str] = []
    if not bundle.exists():
        return [f"{bundle}: bundle does not exist"]

    for path in sorted(bundle.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        try:
            metadata, _ = read_document(path)
        except SystemExit as error:
            errors.append(str(error))
            continue
        if not metadata.get("type"):
            errors.append(f"{path}: non-reserved Markdown concept requires a non-empty type")

    tracker_profiles: dict[str, dict[str, Any]] = {}
    default_tracker_profiles: list[str] = []
    for path in sorted(bundle.joinpath("trackers").glob("*.md")):
        try:
            profile, _ = read_document(path)
        except SystemExit:
            continue
        validate_tracker_profile(path, profile, errors)
        if profile.get("tracker"):
            tracker_profiles[str(profile["tracker"])] = profile
            if profile.get("default") is True:
                default_tracker_profiles.append(str(profile["tracker"]))
    if len(default_tracker_profiles) > 1:
        errors.append(
            f"{bundle / 'trackers'}: only one default Tracker Profile is allowed; found {', '.join(default_tracker_profiles)}"
        )

    parsed_tasks: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(bundle.glob("*/task.md")):
        try:
            metadata, body = read_document(path)
        except SystemExit:
            continue
        parsed_tasks.append((path, metadata, body))

    active_branches: dict[str, Path] = {}
    external_mappings: dict[tuple[str, str, str, str], Path] = {}
    for path, metadata, body in parsed_tasks:
        required = {"type", "task", "title", "description", "status", "created", "timestamp"}
        missing = [key for key in sorted(required) if metadata.get(key) in (None, "")]
        if missing:
            errors.append(f"{path}: missing required fields: {', '.join(missing)}")
            continue
        if metadata["type"] != "Task":
            errors.append(f"{path}: type must be Task")
        if metadata["task"] != path.parent.name or not SLUG_PATTERN.fullmatch(str(metadata["task"])):
            errors.append(f"{path}: task slug must match its directory")
        if metadata["status"] not in STATUSES:
            errors.append(f"{path}: unknown status {metadata['status']!r}")
        for field in ("created", "timestamp"):
            if not is_rfc3339(metadata[field]):
                errors.append(f"{path}: {field} must be an RFC 3339 datetime with timezone")
        for field in ("started", "finished"):
            if metadata.get(field) and not is_rfc3339(metadata[field]):
                errors.append(f"{path}: {field} must be an RFC 3339 datetime with timezone")
        completion_history = metadata.get("completion_history")
        if completion_history is not None:
            if not isinstance(completion_history, list):
                errors.append(f"{path}: completion_history must be a list")
            else:
                for index, event in enumerate(completion_history):
                    if not isinstance(event, dict) or not all(is_rfc3339(event.get(field)) for field in ("finished", "reopened")):
                        errors.append(f"{path}: completion_history[{index}] requires finished and reopened RFC 3339 datetimes")
        if metadata.get("effort_minutes") is not None and (
            type(metadata["effort_minutes"]) is not int or metadata["effort_minutes"] < 0
        ):
            errors.append(f"{path}: effort_minutes must be a non-negative integer")
        for heading in TASK_HEADINGS:
            if not has_heading(body, heading):
                errors.append(f"{path}: missing required heading '## {heading}'")
        validate_external(path, metadata, errors)
        external = metadata.get("external")
        if isinstance(external, list):
            for mapping in external:
                if not isinstance(mapping, dict) or not all(mapping.get(key) not in (None, "") for key in ("system", "host", "kind", "id")):
                    continue
                identity = (str(mapping["system"]), str(mapping["host"]), str(mapping["kind"]), str(mapping["id"]))
                if identity in external_mappings:
                    errors.append(f"{path}: external mapping {'|'.join(identity)} also used by {external_mappings[identity]}")
                else:
                    external_mappings[identity] = path
                tracker = tracker_profiles.get(str(mapping.get("tracker", "")))
                if tracker is None:
                    errors.append(f"{path}: external tracker profile {mapping.get('tracker')!r} does not exist")
                else:
                    if mapping.get("system") != tracker.get("system") or mapping.get("host") != tracker.get("host"):
                        errors.append(f"{path}: external binding system and host must match its Tracker Profile")
                    binding_scope = mapping.get("scope")
                    profile_scope = tracker.get("scope")
                    if isinstance(binding_scope, dict) and isinstance(profile_scope, dict) and binding_scope.get("id") != profile_scope.get("id"):
                        errors.append(f"{path}: external binding scope must match its Tracker Profile")
        validate_estimate(path, metadata, errors)
        validate_portable_fields(path, metadata, errors)
        validate_time_entries(bundle, path, metadata, errors)

        workstreams = sorted(path.parent.joinpath("workstreams").glob("*.md"))
        for candidate in workstreams:
            try:
                workstream, workstream_body = read_document(candidate)
            except SystemExit:
                continue
            required_workstream = {"type", "task", "workstream", "title", "description", "status", "created", "timestamp"}
            missing_workstream = [
                key for key in sorted(required_workstream) if workstream.get(key) in (None, "")
            ]
            if missing_workstream:
                errors.append(f"{candidate}: missing required fields: {', '.join(missing_workstream)}")
                continue
            if workstream["type"] != "Workstream":
                errors.append(f"{candidate}: type must be Workstream")
            if workstream["task"] != metadata["task"]:
                errors.append(f"{candidate}: parent task mismatch")
            if workstream["workstream"] != candidate.stem or not SLUG_PATTERN.fullmatch(str(workstream["workstream"])):
                errors.append(f"{candidate}: workstream slug must match its filename")
            if workstream["status"] not in STATUSES:
                errors.append(f"{candidate}: unknown status {workstream['status']!r}")
            for field in ("created", "timestamp"):
                if not is_rfc3339(workstream[field]):
                    errors.append(f"{candidate}: {field} must be an RFC 3339 datetime with timezone")
            for heading in WORKSTREAM_HEADINGS:
                if not has_heading(workstream_body, heading):
                    errors.append(f"{candidate}: missing required heading '## {heading}'")
            branch = workstream.get("branch")
            if branch and workstream["status"] not in TERMINAL_WORKSTREAM_STATUSES:
                if branch in active_branches:
                    errors.append(f"{candidate}: active branch also used by {active_branches[branch]}")
                active_branches[str(branch)] = candidate

        if metadata["status"] == "done":
            active = []
            for candidate in workstreams:
                try:
                    workstream, _ = read_document(candidate)
                except SystemExit:
                    continue
                if workstream.get("status") not in TERMINAL_WORKSTREAM_STATUSES:
                    active.append(candidate.name)
            if active:
                errors.append(f"{path}: done task has active workstreams: {', '.join(active)}")

    index = bundle / "index.md"
    if not index.exists():
        errors.append(f"{index}: generated index is missing")
    else:
        try:
            expected_index = generated_index(bundle)
        except SystemExit:
            expected_index = None
        if expected_index is not None and index.read_text(encoding="utf-8") != expected_index:
            errors.append(f"{index}: generated index is stale")
    errors.extend(durable_link_graph_errors(bundle))
    return errors


def bundle_warnings(bundle: Path) -> list[str]:
    """Return non-fatal relationship diagnostics for a structurally valid partial bundle."""
    warnings: list[str] = []
    for path, metadata, _ in task_records(bundle):
        relationships: list[tuple[str, str]] = []
        if isinstance(metadata.get("parent"), str):
            relationships.append(("parent", metadata["parent"]))
        if isinstance(metadata.get("depends_on"), list):
            relationships.extend(("depends_on", str(value)) for value in metadata["depends_on"])
        for field, target in relationships:
            if re.match(r"^[a-z][a-z0-9+.-]*://", target, re.IGNORECASE):
                continue
            clean = target.split("#", 1)[0].strip()
            if not clean:
                continue
            candidate = bundle / clean.lstrip("./")
            if candidate.suffix != ".md":
                candidate = candidate.with_suffix(".md")
            try:
                candidate.resolve().relative_to(bundle.resolve())
            except ValueError:
                continue
            if not candidate.exists():
                warnings.append(f"{path}: unresolved {field} target {target!r}")
    return warnings


def link_graph_root(bundle: Path) -> Path:
    """Infer the repository scope used by the CLI's strict durable-link audit."""
    resolved = bundle.resolve()
    if resolved.name == "tasks" and resolved.parent.name == "docs":
        return resolved.parent.parent
    return resolved.parent


def link_graph_concept(path: Path, metadata: dict[str, Any], root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    if path.name in {"index.md", "log.md"}:
        return False
    if any(part.lower() in LINK_GRAPH_EXCLUDED_DIRECTORIES for part in relative.parts[:-1]):
        return False
    concept_type = str(metadata.get("type", "")).strip().lower()
    return (
        bool(concept_type)
        and concept_type not in LINK_GRAPH_EXCLUDED_TYPES
        and not any(marker in concept_type for marker in LINK_GRAPH_EXCLUDED_TYPE_MARKERS)
    )


def durable_link_graph_errors(bundle: Path, root: Path | None = None) -> list[str]:
    """Require durable typed concepts to form one resolved local relationship graph."""
    root = (root or link_graph_root(bundle)).resolve()
    concepts: dict[Path, tuple[dict[str, Any], str]] = {}
    for path in sorted(root.rglob("*.md")):
        try:
            metadata, body = read_document(path)
        except SystemExit:
            continue
        if link_graph_concept(path, metadata, root):
            concepts[path.resolve()] = (metadata, body)
    if len(concepts) < 2:
        return []

    adjacency: dict[Path, set[Path]] = {path: set() for path in concepts}

    def connect(source: Path, candidate: Path) -> None:
        target = candidate.resolve()
        if target in concepts and target != source:
            adjacency[source].add(target)
            adjacency[target].add(source)

    for source, (metadata, body) in concepts.items():
        for match in MARKDOWN_LINK_PATTERN.finditer(body):
            if match.group("image"):
                continue
            target = match.group("target").strip("<>")
            if target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            local = unquote(target.split("#", 1)[0].split("?", 1)[0]).replace("\\", "/")
            if not local:
                continue
            connect(source, root / local.lstrip("/") if local.startswith("/") else source.parent / local)

        concept_type = str(metadata.get("type", ""))
        if concept_type == "Task":
            structured: list[str] = []
            if isinstance(metadata.get("parent"), str):
                structured.append(str(metadata["parent"]))
            if isinstance(metadata.get("depends_on"), list):
                structured.extend(str(value) for value in metadata["depends_on"])
            for target in structured:
                clean = target.split("#", 1)[0].strip().lstrip("./")
                if not clean or re.match(r"^[a-z][a-z0-9+.-]*:", clean, re.IGNORECASE):
                    continue
                candidate = bundle / clean
                connect(source, candidate if candidate.suffix == ".md" else candidate.with_suffix(".md"))
        elif concept_type == "Workstream" and metadata.get("task"):
            connect(source, bundle / str(metadata["task"]) / "task.md")

    orphans = sorted(path.relative_to(root).as_posix() for path, links in adjacency.items() if not links)
    errors = [f"{root}: durable link graph contains orphan concept {path}" for path in orphans]
    remaining = set(adjacency)
    components: list[set[Path]] = []
    while remaining:
        pending = [next(iter(remaining))]
        component: set[Path] = set()
        while pending:
            current = pending.pop()
            if current in component:
                continue
            component.add(current)
            pending.extend(adjacency[current] - component)
        remaining -= component
        components.append(component)
    if len(components) > 1:
        summaries = [", ".join(sorted(path.relative_to(root).as_posix() for path in component)[:3]) for component in components]
        errors.append(f"{root}: durable link graph has {len(components)} disconnected components: {' | '.join(summaries)}")
    return errors


def validate_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    errors = validate_bundle(bundle)
    inferred_root = link_graph_root(bundle)
    if inferred_root != root.resolve():
        errors = [error for error in errors if "durable link graph" not in error]
        errors.extend(durable_link_graph_errors(bundle, root))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    warnings = bundle_warnings(bundle)
    if warnings:
        print("\n".join(f"WARNING: {warning}" for warning in warnings), file=sys.stderr)
    print("OKF Tasks bundle is valid.")
    return 0


def build_index_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    build_index(bundle_root(root, args.bundle))
    print("Rebuilt task index.")
    return 0


def add_location_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument("--bundle", default="tasks", help="Repository-relative bundle path (default: tasks)")


def add_commit_review_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--task", required=True)
    parser.add_argument("--commit", action="append", help="Explicit commit hash; repeat for multiple commits")
    parser.add_argument("--grep", help="Commit-message pattern (defaults to the task slug)")
    parser.add_argument("--since", help="Git-compatible lower date bound")
    parser.add_argument("--until", help="Git-compatible upper date bound")
    parser.add_argument("--session-gap-minutes", type=int, default=90)
    parser.add_argument("--allowance-minutes", type=int, default=30)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain OKF Tasks v0.5 bundles.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {CLI_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    initialize = subparsers.add_parser("init-bundle", help="Initialize a generated task index")
    initialize.add_argument("--root", required=True, help="Repository root")
    initialize.add_argument("--bundle", help="Custom repository-relative bundle path")
    initialize.add_argument(
        "--placement",
        choices=tuple(BUNDLE_PLACEMENTS),
        default="root",
        help="Standard placement: root creates tasks/; docs creates docs/tasks/ (default: root)",
    )
    initialize.add_argument("--force", action="store_true", help="Rebuild an existing index")
    initialize.set_defaults(func=init_bundle)

    tracker = subparsers.add_parser("tracker", help="Initialize and maintain Tracker Profiles")
    tracker_commands = tracker.add_subparsers(dest="tracker_command", required=True)
    tracker_initialize = tracker_commands.add_parser("init", help="Create a profile from provider discovery")
    add_location_arguments(tracker_initialize)
    tracker_initialize.add_argument("--tracker", required=True)
    tracker_initialize.add_argument("--system", choices=sorted(TRACKER_SYSTEMS), required=True)
    tracker_initialize.add_argument("--discovery-file", help="Use normalized provider discovery JSON instead of the live API")
    tracker_initialize.add_argument("--scope", help="Repository, project, team, or List identifier for live discovery")
    tracker_initialize.add_argument("--api-base", help="Override the provider API base, primarily for enterprise hosts")
    tracker_initialize.add_argument("--token-env", help="Environment variable containing the runtime credential")
    tracker_initialize.add_argument("--mode", choices=sorted(SYNC_MODES), default="manual")
    tracker_initialize.add_argument("--authority", choices=sorted(SYNC_AUTHORITIES), default="manual")
    tracker_initialize.add_argument("--status-map", action="append", help="Override with local=remote-id-or-name")
    tracker_initialize.add_argument("--default", action="store_true", help="Save this profile as the project default")
    tracker_initialize.add_argument("--force", action="store_true")
    tracker_initialize.set_defaults(func=tracker_init)
    tracker_default_parser = tracker_commands.add_parser("set-default", help="Save the project default Tracker Profile")
    add_location_arguments(tracker_default_parser)
    tracker_default_parser.add_argument("--tracker", required=True)
    tracker_default_parser.set_defaults(func=tracker_set_default)
    for name, function, help_text in (
        ("inspect", tracker_inspect, "Print a resolved profile as JSON"),
        ("validate", tracker_validate_command, "Validate one Tracker Profile"),
    ):
        command = tracker_commands.add_parser(name, help=help_text)
        add_location_arguments(command)
        command.add_argument("--tracker", required=True)
        command.set_defaults(func=function)
    tracker_refresh_parser = tracker_commands.add_parser("refresh", help="Detect and optionally accept provider discovery drift")
    add_location_arguments(tracker_refresh_parser)
    tracker_refresh_parser.add_argument("--tracker", required=True)
    tracker_refresh_parser.add_argument("--discovery-file", help="Use normalized provider discovery JSON instead of the live API")
    tracker_refresh_parser.add_argument("--api-base")
    tracker_refresh_parser.add_argument("--token-env")
    tracker_refresh_parser.add_argument("--accept", action="store_true")
    tracker_refresh_parser.set_defaults(func=tracker_refresh)
    tracker_create_parser = tracker_commands.add_parser("create", help="Create, verify, and bind a remote record from a task")
    add_location_arguments(tracker_create_parser)
    tracker_create_parser.add_argument("--tracker", help="Profile slug; defaults to the saved or sole project profile")
    tracker_create_parser.add_argument("--task", required=True)
    tracker_create_parser.add_argument("--api-base")
    tracker_create_parser.add_argument("--token-env")
    tracker_create_parser.add_argument("--remote", default="origin", help="Git remote used to resolve repository links")
    tracker_create_parser.add_argument("--remote-url")
    tracker_create_parser.add_argument("--ref")
    tracker_create_parser.add_argument("--repository-provider", choices=("github", "gitlab"))
    tracker_create_parser.set_defaults(func=tracker_create_remote)
    tracker_import_parser = tracker_commands.add_parser("import", help="Import a remote record as a conformant local task")
    add_location_arguments(tracker_import_parser)
    tracker_import_parser.add_argument("--tracker", help="Profile slug; defaults to the saved or sole project profile")
    tracker_import_parser.add_argument("--remote-key", required=True, help="Issue number, IID, identifier, or task ID")
    tracker_import_parser.add_argument("--slug", required=True)
    tracker_import_parser.add_argument("--status", choices=STATUSES, help="Required when the remote mapping is lossy")
    tracker_import_parser.add_argument("--api-base")
    tracker_import_parser.add_argument("--token-env")
    tracker_import_parser.set_defaults(func=tracker_import_remote)
    tracker_sync_parser = tracker_commands.add_parser("sync", help="Push or pull one bound task with conflict-safe reconciliation")
    add_location_arguments(tracker_sync_parser)
    tracker_sync_parser.add_argument("--tracker", help="Profile slug; defaults to the saved or sole project profile")
    tracker_sync_parser.add_argument("--task", required=True)
    tracker_sync_parser.add_argument("--direction", choices=("push", "pull"), required=True)
    tracker_sync_parser.add_argument("--api-base")
    tracker_sync_parser.add_argument("--token-env")
    tracker_sync_parser.add_argument("--remote", default="origin")
    tracker_sync_parser.add_argument("--remote-url")
    tracker_sync_parser.add_argument("--ref")
    tracker_sync_parser.add_argument("--repository-provider", choices=("github", "gitlab"))
    tracker_sync_parser.add_argument("--force", action="store_true", help="Acknowledge a detected remote revision change for push")
    tracker_sync_parser.set_defaults(func=tracker_sync)

    create = subparsers.add_parser("create", help="Create a proposed task")
    add_location_arguments(create)
    create.add_argument("--slug", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--owner")
    create.add_argument("--depends-on", action="append", help="Resolved task concept path such as other-task/task; repeatable")
    create.add_argument("--related", action="append", help="Existing repository-relative Markdown document to link; repeatable")
    create.set_defaults(func=create_task)

    workstream = subparsers.add_parser("add-workstream", help="Add a ready workstream")
    add_location_arguments(workstream)
    workstream.add_argument("--task", required=True)
    workstream.add_argument("--slug", required=True)
    workstream.add_argument("--title", required=True)
    workstream.add_argument("--description", required=True)
    workstream.add_argument("--owner")
    workstream.add_argument("--branch")
    workstream.set_defaults(func=add_workstream)

    status = subparsers.add_parser("set-status", help="Transition a task or workstream")
    add_location_arguments(status)
    status.add_argument("--task", required=True)
    status.add_argument("--workstream")
    status.add_argument("--status", choices=STATUSES, required=True)
    status.add_argument("--force", action="store_true")
    status.set_defaults(func=set_status)

    external = subparsers.add_parser("link-external", help="Add an external tracker mapping")
    add_location_arguments(external)
    external.add_argument("--task", required=True)
    external.add_argument("--tracker", help="Profile slug; defaults to the saved or sole project profile")
    external.add_argument("--id", required=True)
    external.add_argument("--key", required=True)
    external.add_argument("--url", required=True)
    external.add_argument("--remote-revision")
    external.set_defaults(func=link_external)

    export = subparsers.add_parser(
        "prepare-export",
        help="Prepare a repository artifact for safe publication to an external system",
    )
    export.add_argument("--root", required=True, help="Repository root")
    export.add_argument("--source", required=True, help="Repository-relative Markdown source")
    export.add_argument("--remote", default="origin", help="Git remote name (default: origin)")
    export.add_argument("--remote-url", help="Explicit GitHub or GitLab remote URL")
    export.add_argument("--provider", choices=("github", "gitlab"))
    export.add_argument("--ref", help="Publication ref (default: current commit SHA)")
    export.add_argument("--include-frontmatter", action="store_true", help="Export frontmatter as well as body")
    export.add_argument("--allow-remote-images", action="store_true", help="Allow HTTPS images under an explicit policy")
    export.add_argument("--output", help="Write the prepared artifact instead of stdout")
    export.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    export.set_defaults(func=prepare_external_artifact)

    estimate = subparsers.add_parser("set-estimate", help="Record expected effort and optional sprint points")
    add_location_arguments(estimate)
    estimate.add_argument("--task", required=True)
    estimate.add_argument("--effort-minutes", type=int)
    estimate.add_argument("--method", choices=sorted(ESTIMATE_METHODS), default="agent")
    estimate.add_argument("--confidence", choices=sorted(ESTIMATE_CONFIDENCE), default="medium")
    estimate.add_argument("--basis", required=True)
    estimate.add_argument("--actor", required=True)
    estimate.add_argument("--points", type=float)
    estimate.add_argument("--points-scale")
    estimate.add_argument("--points-context")
    estimate.set_defaults(func=set_estimate)

    start = subparsers.add_parser("start-time", help="Start a live effort session")
    add_location_arguments(start)
    start.add_argument("--task", required=True)
    start.add_argument("--actor", required=True)
    start.add_argument("--workstream")
    start.add_argument("--entry")
    start.add_argument("--started", help="RFC 3339 override, primarily for recovery and testing")
    start.add_argument("--activity", choices=sorted(TIME_ACTIVITIES), default="implementation")
    start.add_argument("--note")
    start.set_defaults(func=start_time)

    stop = subparsers.add_parser("stop-time", help="Close a live effort session")
    add_location_arguments(stop)
    stop.add_argument("--task", required=True)
    stop.add_argument("--entry")
    stop.add_argument("--actor")
    stop.add_argument("--workstream")
    stop.add_argument("--finished", help="RFC 3339 override, primarily for recovery and testing")
    stop.add_argument("--effort-minutes", type=int)
    stop.add_argument("--activity", choices=sorted(TIME_ACTIVITIES), help="Override the activity selected at start")
    stop.add_argument("--note")
    stop.set_defaults(func=stop_time)

    manual = subparsers.add_parser("add-time", help="Add a closed manual effort entry")
    add_location_arguments(manual)
    manual.add_argument("--task", required=True)
    manual.add_argument("--actor", required=True)
    manual.add_argument("--effort-minutes", type=int, required=True)
    manual.add_argument("--note", required=True)
    manual.add_argument("--started")
    manual.add_argument("--finished")
    manual.add_argument("--workstream")
    manual.add_argument("--entry")
    manual.add_argument("--activity", choices=sorted(TIME_ACTIVITIES), default="implementation")
    manual.set_defaults(func=add_time)

    review = subparsers.add_parser("review-commits", help="Estimate effort sessions from commit evidence")
    add_location_arguments(review)
    add_commit_review_arguments(review)
    review.set_defaults(func=review_commits_command)

    backfill = subparsers.add_parser("backfill-from-commits", help="Write an estimated time entry from commit evidence")
    add_location_arguments(backfill)
    add_commit_review_arguments(backfill)
    backfill.add_argument("--actor", required=True)
    backfill.add_argument("--workstream")
    backfill.add_argument("--entry")
    backfill.add_argument("--effort-minutes", type=int, help="Override the transparent heuristic")
    backfill.add_argument("--confidence", choices=sorted(ESTIMATE_CONFIDENCE), default="medium")
    backfill.add_argument("--activity", choices=sorted(TIME_ACTIVITIES), default="implementation")
    backfill.add_argument("--note")
    backfill.set_defaults(func=backfill_from_commits)

    summary = subparsers.add_parser("time-summary", help="Compare estimated and recorded task effort")
    add_location_arguments(summary)
    summary.add_argument("--task", required=True)
    summary.set_defaults(func=time_summary)

    index = subparsers.add_parser("build-index", help="Rebuild generated navigation")
    add_location_arguments(index)
    index.set_defaults(func=build_index_command)

    validation = subparsers.add_parser("validate", help="Validate OKF and profile conformance")
    add_location_arguments(validation)
    validation.set_defaults(func=validate_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
