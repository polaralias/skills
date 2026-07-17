#!/usr/bin/env python3
"""Reference CLI for OKF Tasks v0.3 bundles."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlsplit

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
TIME_STATUSES = {"running", "closed"}
TIME_METHODS = {"tracked", "tracked-adjusted", "manual", "estimated-commit-review"}
ESTIMATE_CONFIDENCE = {"low", "medium", "high"}
ESTIMATE_METHODS = {"agent", "manual", "historical"}
LIVE_TIME_STATUSES = {"ready", "in-progress", "blocked", "validation"}
PROFILE_VERSION = "0.3"
PROFILE_URL = "https://github.com/polaralias/okf-tasks/blob/v0.3.0/SPEC.md"
BUNDLE_PLACEMENTS = {"root": "tasks", "docs": "docs/tasks"}
MARKDOWN_LINK_PATTERN = re.compile(r"(?P<image>!)?(?P<label>\[[^\]\n]*\])\((?P<target>[^)\s]+)(?P<suffix>[^)]*)\)")
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


def time_entry_path(bundle: Path, task: str, entry: str) -> Path:
    return bundle / task / "time" / f"{entry}.md"


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


def time_records(bundle: Path, task: str) -> list[tuple[Path, dict[str, Any], str]]:
    records: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted((bundle / task / "time").glob("*.md")):
        metadata, body = read_document(path)
        records.append((path, metadata, body))
    return records


def render_time_body(summary: str, basis: str, activity: str) -> str:
    return load_body_template(
        "time-entry-body.md.template",
        {"summary": summary, "basis": basis, "activity": activity},
    )


def update_task_time_rollup(bundle: Path, task: str, completion_time: str | None = None) -> None:
    path = task_path(bundle, task)
    metadata, body = read_document(path)
    entries = time_records(bundle, task)
    starts = [str(entry["started"]) for _, entry, _ in entries if entry.get("started")]
    closed_effort = [
        int(entry["effort_minutes"])
        for _, entry, _ in entries
        if entry.get("status") == "closed" and isinstance(entry.get("effort_minutes"), int)
    ]
    if starts:
        metadata["started"] = min(starts, key=lambda value: parse_datetime(value, "started"))
        metadata["effort_minutes"] = sum(closed_effort)
    if completion_time is not None:
        metadata["finished"] = completion_time
    metadata["timestamp"] = utc_now()
    write_document(path, metadata, body)


def ensure_workstream(bundle: Path, task: str, workstream: str | None) -> None:
    if workstream and not workstream_path(bundle, task, valid_slug(workstream)).exists():
        fail(f"Workstream does not exist: {task}/{workstream}")


def write_time_entry(
    bundle: Path,
    task: str,
    metadata: dict[str, Any],
    summary: str,
    basis: str,
    activity: str,
) -> Path:
    entry = valid_slug(str(metadata["entry"]))
    path = time_entry_path(bundle, task, entry)
    write_new_document(path, metadata, render_time_body(summary, basis, activity))
    update_task_time_rollup(bundle, task)
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
    body = load_body_template(
        "task-body.md.template",
        {"title": args.title, "description": args.description},
    )
    write_new_document(task_path(bundle, slug), metadata, body)
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
        running = [
            str(metadata.get("entry", candidate.stem))
            for candidate, metadata, _ in time_records(bundle, task)
            if metadata.get("status") == "running"
        ]
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
    for candidate, candidate_metadata, _ in task_records(bundle):
        for mapping in candidate_metadata.get("external", []) if isinstance(candidate_metadata.get("external"), list) else []:
            if isinstance(mapping, dict) and mapping.get("system") == args.system and str(mapping.get("id")) == args.id:
                fail(f"External mapping already exists for {args.system}:{args.id} in {candidate}")
    metadata, body = read_document(path)
    external = metadata.setdefault("external", [])
    if not isinstance(external, list):
        fail(f"Field 'external' must be a list in {path}")
    if any(isinstance(item, dict) and item.get("system") == args.system and str(item.get("id")) == args.id for item in external):
        fail(f"External mapping already exists for {args.system}:{args.id}")
    external.append({"system": args.system, "id": args.id, "url": args.url})
    sync = metadata.setdefault("sync", {})
    if not isinstance(sync, dict):
        fail(f"Field 'sync' must be a mapping in {path}")
    sync["authority"] = args.authority
    metadata["timestamp"] = utc_now()
    write_document(path, metadata, body)
    build_index(bundle)
    print(f"Linked {args.system}:{args.id} to task {args.task!r}.")
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
    task_metadata, _ = read_document(path)
    if task_metadata.get("status") not in LIVE_TIME_STATUSES:
        fail(f"Cannot start live tracking while task status is {task_metadata.get('status')!r}.")
    for _, entry, _ in time_records(bundle, task):
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
        "type": "Time Entry",
        "task": task,
        "entry": entry,
        "status": "running",
        "actor": args.actor,
        "started": started,
        "method": "tracked",
        "timestamp": started,
    }
    if args.workstream:
        metadata["workstream"] = args.workstream
    created = write_time_entry(
        bundle,
        task,
        metadata,
        "Live effort session started.",
        "Started explicitly by an agent or user; effort is not final until the session is stopped.",
        args.note or "Work is active.",
    )
    if task_metadata.get("status") == "ready":
        transition(path, "in-progress", False)
        update_task_time_rollup(bundle, task)
        build_index(bundle)
    print(f"Started time entry {entry!r} at {started} ({created.relative_to(root)}).")
    return 0


def select_running_entry(
    bundle: Path,
    task: str,
    entry_name: str | None,
    actor: str | None,
    workstream: str | None,
) -> tuple[Path, dict[str, Any], str]:
    candidates = [record for record in time_records(bundle, task) if record[1].get("status") == "running"]
    if entry_name:
        candidates = [record for record in candidates if record[1].get("entry") == entry_name]
    if actor:
        candidates = [record for record in candidates if record[1].get("actor") == actor]
    if workstream:
        candidates = [record for record in candidates if record[1].get("workstream") == workstream]
    if not candidates:
        fail("No matching running time entry was found.")
    if len(candidates) > 1:
        names = ", ".join(str(record[1].get("entry", record[0].stem)) for record in candidates)
        fail(f"Multiple running entries match ({names}); specify --entry or --actor.")
    return candidates[0]


def stop_time(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    task = valid_slug(args.task)
    path, metadata, _ = select_running_entry(bundle, task, args.entry, args.actor, args.workstream)
    finished = args.finished or utc_now()
    elapsed = duration_minutes(str(metadata["started"]), finished)
    effort = elapsed if args.effort_minutes is None else args.effort_minutes
    if effort < 0:
        fail("Effort minutes cannot be negative.")
    adjusted = effort != elapsed
    if adjusted and not args.note:
        fail("Use --note to explain why active effort differs from wall-clock elapsed time.")
    metadata.update(
        {
            "status": "closed",
            "finished": finished,
            "elapsed_minutes": elapsed,
            "effort_minutes": effort,
            "method": "tracked-adjusted" if adjusted else "tracked",
            "timestamp": finished,
        }
    )
    basis = (
        f"Wall-clock session was {elapsed} minutes. Active effort was adjusted to {effort} minutes: {args.note}"
        if adjusted
        else f"Active effort equals the {elapsed}-minute explicit start/stop interval."
    )
    write_document(
        path,
        metadata,
        render_time_body("Live effort session closed.", basis, args.note or "Session completed."),
    )
    update_task_time_rollup(bundle, task)
    print(f"Stopped time entry {metadata['entry']!r}: {effort} effort minutes ({elapsed} elapsed).")
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
        "type": "Time Entry",
        "task": task,
        "entry": entry,
        "status": "closed",
        "actor": args.actor,
        "started": started,
        "finished": finished,
        "elapsed_minutes": elapsed,
        "effort_minutes": args.effort_minutes,
        "method": "manual",
        "timestamp": utc_now(),
    }
    if args.workstream:
        metadata["workstream"] = args.workstream
    write_time_entry(
        bundle,
        task,
        metadata,
        "Manual effort entry added.",
        args.note,
        f"Recorded {args.effort_minutes} effort minutes manually.",
    )
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
        "type": "Time Entry",
        "task": task,
        "entry": entry,
        "status": "closed",
        "actor": args.actor,
        "started": started,
        "finished": finished,
        "elapsed_minutes": duration_minutes(started, finished),
        "effort_minutes": effort,
        "method": "estimated-commit-review",
        "confidence": args.confidence,
        "source_commits": [commit["commit"] for commit in commits],
        "estimation": {
            "session_gap_minutes": args.session_gap_minutes,
            "allowance_minutes": args.allowance_minutes,
            "session_count": len(sessions),
            "sessions": sessions,
        },
        "timestamp": utc_now(),
    }
    if args.workstream:
        metadata["workstream"] = args.workstream
    activity = "\n".join(
        f"- `{commit['commit'][:12]}` {commit['timestamp']} — {commit['subject']}" for commit in commits
    )
    adjustment = f" Manual adjustment: {args.note}" if args.note else ""
    basis = (
        f"Reviewed {len(commits)} commits and grouped them at gaps over {args.session_gap_minutes} minutes. "
        f"Each session includes {args.allowance_minutes} minutes for preparation and review. "
        f"The heuristic proposed {heuristic_effort} minutes; recorded effort is {effort} minutes.{adjustment}"
    )
    write_time_entry(
        bundle,
        task,
        metadata,
        "Effort backfilled from a review of repository commits.",
        basis,
        activity,
    )
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
    entries = time_records(bundle, task)
    running = [entry for _, entry, _ in entries if entry.get("status") == "running"]
    closed = [entry for _, entry, _ in entries if entry.get("status") == "closed"]
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
                if not isinstance(mapping, dict) or not all(mapping.get(key) for key in ("system", "id", "url")):
                    errors.append(f"{path}: external[{index}] requires system, id, and url")
    sync = metadata.get("sync")
    if sync is not None:
        if not isinstance(sync, dict):
            errors.append(f"{path}: sync must be a mapping")
        else:
            if sync.get("authority") not in SYNC_AUTHORITIES:
                errors.append(f"{path}: sync.authority must be repository, tracker, or manual")
            field_authority = sync.get("field_authority")
            if field_authority is not None:
                if not isinstance(field_authority, dict):
                    errors.append(f"{path}: sync.field_authority must be a mapping")
                else:
                    for field, authority in field_authority.items():
                        if authority not in SYNC_AUTHORITIES:
                            errors.append(f"{path}: sync.field_authority.{field} must be repository, tracker, or manual")
            if sync.get("base") is not None and not isinstance(sync["base"], dict):
                errors.append(f"{path}: sync.base must be a mapping")


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


def validate_time_entries(
    bundle: Path,
    task_path_value: Path,
    task_metadata: dict[str, Any],
    errors: list[str],
) -> None:
    task = str(task_metadata.get("task", task_path_value.parent.name))
    entries: list[tuple[Path, dict[str, Any], str]] = []
    running_combinations: dict[tuple[str, str], Path] = {}
    for path in sorted(task_path_value.parent.joinpath("time").glob("*.md")):
        try:
            metadata, body = read_document(path)
        except SystemExit:
            continue
        entries.append((path, metadata, body))
        required = {"type", "task", "entry", "status", "actor", "started", "method", "timestamp"}
        missing = [key for key in sorted(required) if metadata.get(key) in (None, "")]
        if missing:
            errors.append(f"{path}: missing required fields: {', '.join(missing)}")
            continue
        if metadata["type"] != "Time Entry":
            errors.append(f"{path}: type must be Time Entry")
        if metadata["task"] != task:
            errors.append(f"{path}: parent task mismatch")
        if metadata["entry"] != path.stem or not SLUG_PATTERN.fullmatch(str(metadata["entry"])):
            errors.append(f"{path}: entry slug must match its filename")
        if metadata["status"] not in TIME_STATUSES:
            errors.append(f"{path}: time status must be running or closed")
        if metadata["method"] not in TIME_METHODS:
            errors.append(f"{path}: unknown time method {metadata['method']!r}")
        for field in ("started", "timestamp"):
            if not is_rfc3339(metadata[field]):
                errors.append(f"{path}: {field} must be an RFC 3339 datetime with timezone")
        for heading in ("Summary", "Basis", "Activity"):
            if not has_heading(body, heading):
                errors.append(f"{path}: missing required heading '## {heading}'")
        workstream = metadata.get("workstream")
        if workstream and not workstream_path(bundle, task, str(workstream)).exists():
            errors.append(f"{path}: referenced workstream does not exist")
        if metadata["status"] == "running":
            if metadata["method"] != "tracked":
                errors.append(f"{path}: running entries must use method tracked")
            for field in ("finished", "elapsed_minutes", "effort_minutes"):
                if field in metadata:
                    errors.append(f"{path}: running entry must not contain {field}")
            combination = (str(metadata.get("actor")), str(metadata.get("workstream", "")))
            if combination in running_combinations:
                errors.append(f"{path}: duplicate running actor/workstream also used by {running_combinations[combination]}")
            running_combinations[combination] = path
        else:
            for field in ("finished", "effort_minutes"):
                if metadata.get(field) in (None, ""):
                    errors.append(f"{path}: closed entry requires {field}")
            if metadata.get("finished") and not is_rfc3339(metadata["finished"]):
                errors.append(f"{path}: finished must be an RFC 3339 datetime with timezone")
            if type(metadata.get("effort_minutes")) is not int or metadata.get("effort_minutes", -1) < 0:
                errors.append(f"{path}: effort_minutes must be a non-negative integer")
            if metadata.get("elapsed_minutes") is not None:
                if type(metadata["elapsed_minutes"]) is not int or metadata["elapsed_minutes"] < 0:
                    errors.append(f"{path}: elapsed_minutes must be a non-negative integer")
                elif metadata.get("finished") and is_rfc3339(metadata["started"]) and is_rfc3339(metadata["finished"]):
                    try:
                        expected_elapsed = duration_minutes(str(metadata["started"]), str(metadata["finished"]))
                    except SystemExit:
                        expected_elapsed = None
                    if expected_elapsed is not None and metadata["elapsed_minutes"] != expected_elapsed:
                        errors.append(f"{path}: elapsed_minutes does not match started/finished")
            if metadata["method"] == "estimated-commit-review":
                if metadata.get("confidence") not in ESTIMATE_CONFIDENCE:
                    errors.append(f"{path}: commit-review estimate requires low, medium, or high confidence")
                if not isinstance(metadata.get("source_commits"), list) or not metadata["source_commits"]:
                    errors.append(f"{path}: commit-review estimate requires source_commits")

    if not entries:
        if task_metadata.get("started"):
            errors.append(f"{task_path_value}: started requires at least one time entry")
        if task_metadata.get("effort_minutes") not in (None, 0):
            errors.append(f"{task_path_value}: effort_minutes requires closed time entries")
        if task_metadata.get("status") == "done" and not task_metadata.get("finished"):
            errors.append(f"{task_path_value}: done task requires finished")
        return

    starts = [str(metadata["started"]) for _, metadata, _ in entries if metadata.get("started")]
    if starts:
        earliest = min(starts, key=lambda value: parse_datetime(value, "started"))
        if not task_metadata.get("started") or parse_datetime(str(task_metadata["started"])) != parse_datetime(earliest):
            errors.append(f"{task_path_value}: started must equal the first time-entry start")
    effort = sum(
        int(metadata["effort_minutes"])
        for _, metadata, _ in entries
        if metadata.get("status") == "closed" and type(metadata.get("effort_minutes")) is int
    )
    if task_metadata.get("effort_minutes") != effort:
        errors.append(f"{task_path_value}: effort_minutes must equal the closed time-entry sum ({effort})")
    if task_metadata.get("status") == "done":
        if not task_metadata.get("finished"):
            errors.append(f"{task_path_value}: done task requires finished")
        running = [str(metadata.get("entry", path.stem)) for path, metadata, _ in entries if metadata.get("status") == "running"]
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

    parsed_tasks: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(bundle.glob("*/task.md")):
        try:
            metadata, body = read_document(path)
        except SystemExit:
            continue
        parsed_tasks.append((path, metadata, body))

    active_branches: dict[str, Path] = {}
    external_mappings: dict[tuple[str, str], Path] = {}
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
                if not isinstance(mapping, dict) or not mapping.get("system") or mapping.get("id") in (None, ""):
                    continue
                identity = (str(mapping["system"]), str(mapping["id"]))
                if identity in external_mappings:
                    errors.append(f"{path}: external mapping {identity[0]}:{identity[1]} also used by {external_mappings[identity]}")
                else:
                    external_mappings[identity] = path
        validate_estimate(path, metadata, errors)
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


def validate_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    bundle = bundle_root(root, args.bundle)
    errors = validate_bundle(bundle)
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
    parser = argparse.ArgumentParser(description="Maintain OKF Tasks v0.3 bundles.")
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

    create = subparsers.add_parser("create", help="Create a proposed task")
    add_location_arguments(create)
    create.add_argument("--slug", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--owner")
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
    external.add_argument("--system", required=True)
    external.add_argument("--id", required=True)
    external.add_argument("--url", required=True)
    external.add_argument("--authority", choices=sorted(SYNC_AUTHORITIES), required=True)
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
