from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


HOSTS = ("codex", "claude", "git")
HOOK_MARKER = "# Polaralias engineering workflow"
ROUTING_START = "<!-- polaralias-engineering-workflow:start -->"
ROUTING_END = "<!-- polaralias-engineering-workflow:end -->"
CODEX_ROUTING_BLOCK = f"""{ROUTING_START}
## Engineering workflow activation

For every material repository implementation, fix, refactor, test, documentation change, or review that may lead to edits, invoke the installed `engineering-workflow` skill before the first task action. After reading its complete `SKILL.md`, run its single `engineering.py activate --phase deliver --task-mode none --root <repository>` entrypoint before broad inspection or mutation. Let repository evidence adjust phase, task mode, capabilities, and gates afterward. Do not activate it for explanation-only questions or trivial read-only inspection. Never claim workflow use unless activation succeeded.
{ROUTING_END}
"""


class HostIntegrationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def host_recipe(root: Path, *, host: str, base: str) -> dict[str, Any]:
    scripts = Path(__file__).resolve().parent
    mcp_command = [
        sys.executable,
        str(scripts / "repo_context_mcp.py"),
        "--root",
        str(root.resolve()),
    ]
    pre_merge_command = [
        sys.executable,
        str(scripts / "hooks" / "pre_merge.py"),
        "--root",
        str(root.resolve()),
        "--base",
        base,
    ]
    if host == "codex":
        mcp = {
            "status": "manual-user-activation",
            "installCommand": [
                "codex",
                "mcp",
                "add",
                "polaralias-engineering-workflow",
                "--",
                *mcp_command,
            ],
            "reason": "The installed Codex CLI exposes user-level `codex mcp add`; no project-scoped hook schema is assumed.",
        }
    elif host == "claude":
        mcp = {
            "status": "project-config-supported",
            "path": ".mcp.json",
            "entry": {
                "command": mcp_command[0],
                "args": mcp_command[1:],
                "env": {},
            },
        }
    else:
        mcp = {"status": "not-applicable"}
    return {
        "result": "host-recipe",
        "host": host,
        "mcp": mcp,
        "hooks": {
            "status": "explicit-git-gate",
            "base": base,
            "path": ".githooks/pre-push",
            "command": pre_merge_command,
            "activationCommand": ["git", "config", "core.hooksPath", ".githooks"],
        },
        "routing": {
            "status": "project-instructions-supported" if host == "codex" else "not-applicable",
            "path": "AGENTS.md" if host == "codex" else None,
            "managedMarkers": [ROUTING_START, ROUTING_END] if host == "codex" else [],
        },
    }


def git_hooks_directory(root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise HostIntegrationError(
            "host_git_repository_required",
            result.stderr.strip() or "Host hook installation requires a Git repository.",
        )
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (root / value).resolve()


def install_pre_push(root: Path, *, base: str, force: bool) -> str:
    hooks = git_hooks_directory(root)
    target = hooks / "pre-push"
    if target.exists():
        existing = target.read_text(encoding="utf-8", errors="replace")
        if HOOK_MARKER not in existing and not force:
            raise HostIntegrationError(
                "host_hook_owned",
                "Refusing to replace an existing pre-push hook without --force.",
            )
    script = Path(__file__).resolve().parent / "hooks" / "pre_merge.py"
    command = " ".join(
        shlex.quote(value)
        for value in [
            Path(sys.executable).as_posix(),
            script.as_posix(),
            "--root",
            root.resolve().as_posix(),
            "--base",
            base,
        ]
    )
    write_text_lf(
        target,
        f"#!/bin/sh\n{HOOK_MARKER}\nexec {command}\n",
    )
    try:
        os.chmod(target, 0o755)
    except OSError:
        pass
    return str(target)


def install_claude_mcp(root: Path, *, force: bool) -> str:
    target = root / ".mcp.json"
    if target.exists():
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise HostIntegrationError(
                "host_mcp_config_invalid",
                f".mcp.json is invalid JSON at line {error.lineno}.",
            ) from error
        if not isinstance(payload, dict):
            raise HostIntegrationError(
                "host_mcp_config_invalid", ".mcp.json must contain an object."
            )
    else:
        payload = {}
    servers = payload.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise HostIntegrationError(
            "host_mcp_config_invalid", ".mcp.json mcpServers must be an object."
        )
    name = "polaralias-engineering-workflow"
    if name in servers and not force:
        raise HostIntegrationError(
            "host_mcp_entry_owned",
            "Refusing to replace the existing polaralias-engineering-workflow MCP entry without --force.",
        )
    servers[name] = {
        "command": "${POLARALIAS_PYTHON:-python}",
        "args": [
            "${POLARALIAS_EWF_HOME}/scripts/repo_context_mcp.py",
            "--root",
            "${CLAUDE_PROJECT_DIR}",
        ],
        "env": {},
    }
    write_text_lf(target, json.dumps(payload, indent=2) + "\n")
    return target.relative_to(root).as_posix()


def install_codex_routing(root: Path) -> str:
    target = root / "AGENTS.md"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    has_start = ROUTING_START in existing
    has_end = ROUTING_END in existing
    if has_start != has_end:
        raise HostIntegrationError(
            "host_routing_markers_invalid",
            "AGENTS.md contains only one engineering-workflow routing marker.",
        )
    if has_start:
        prefix, remainder = existing.split(ROUTING_START, 1)
        _, suffix = remainder.split(ROUTING_END, 1)
        content = prefix.rstrip() + "\n\n" + CODEX_ROUTING_BLOCK.rstrip() + suffix
    else:
        content = existing.rstrip()
        if content:
            content += "\n\n"
        content += CODEX_ROUTING_BLOCK.rstrip()
    write_text_lf(target, content.rstrip() + "\n")
    return target.relative_to(root).as_posix()


def install_host(root: Path, *, host: str, base: str, force: bool = False) -> dict[str, Any]:
    recipe = host_recipe(root, host=host, base=base)
    installed = {"gitHook": install_pre_push(root, base=base, force=force)}
    if host == "claude":
        installed["mcpConfig"] = install_claude_mcp(root, force=force)
    elif host == "codex":
        installed["routingInstructions"] = install_codex_routing(root)
    return {
        "result": "host-installed",
        "host": host,
        "installed": installed,
        "mcp": recipe["mcp"],
        "base": base,
    }
