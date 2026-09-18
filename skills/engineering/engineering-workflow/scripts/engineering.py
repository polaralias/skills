from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from documentation import (
    DocumentationError,
    documentation_closure_evidence,
)
from host_integration import (
    HOSTS,
    HostIntegrationError,
    host_recipe,
    install_host,
)
from knowledge import KnowledgeError
from okf_adapter import OkfAdapterError, check_bundle, normalise_relative, plan
from operations import OperationError, invoke_operation
from repo_context import (
    ContextError,
    benchmark_context,
    repository_relative_path,
)


SCHEMA_VERSION = 1
STATE_DIRECTORY = ".engineering-workflow"
STATE_FILENAME = "state.json"
PHASES = ("understand", "design", "deliver", "close", "pause", "resume")
TASK_MODES = ("none", "lightweight", "full")
JOURNEYS: dict[str, dict[str, Any]] = {
    "understand": {
        "name": "understand",
        "reference": "references/journeys/understand.md",
        "capabilities": ["context-retrieval"],
        "gates": [],
        "operations": [
            "repository-orientation",
            "bounded-evidence-retrieval",
            "runtime-verification",
            "ambiguity-resolution",
            "knowledge-impact-classification",
        ],
    },
    "design": {
        "name": "design",
        "reference": "references/journeys/design.md",
        "capabilities": [],
        "gates": ["acceptance-defined"],
        "operations": [
            "truth-and-assumption-separation",
            "bounded-feature-contract",
            "scenario-pressure-test",
            "public-behaviour-acceptance",
            "traceable-work-package-readiness",
        ],
    },
    "close": {
        "name": "close",
        "reference": "references/journeys/close.md",
        "capabilities": [],
        "gates": [],
        "operations": [
            "bound-change-explanation",
            "independent-lane-assessment",
            "task-and-knowledge-reconciliation",
            "final-validation",
            "explicit-closure",
        ],
    },
}
CAPABILITIES: dict[str, dict[str, Any]] = {
    "parallel-delivery": {
        "name": "parallel-delivery",
        "reference": "references/extensions/parallel-delivery.md",
        "gates": ["integrated-tree-validation", "worktree-cleanup"],
    },
    "qa-planning": {
        "name": "qa-planning",
        "reference": "references/extensions/qa-planning.md",
        "gates": ["qa-coverage"],
    },
    "tracker-sync": {
        "name": "tracker-sync",
        "reference": "references/extensions/tracker-sync.md",
        "gates": ["tracker-reconciliation"],
    },
    "publication": {
        "name": "publication",
        "reference": "references/extensions/publication.md",
        "gates": ["publication-safety"],
    },
}
LEGACY_ROUTES: dict[str, dict[str, Any]] = {
    "EWO": {"name": "engineering-workflow-orchestrator", "destination": "lifecycle", "command": ["start"]},
    "RDS": {"name": "repo-dissection", "destination": "understand", "command": ["journey", "enter", "understand"]},
    "QTK": {"name": "query-to-knowledge", "destination": "understand", "command": ["journey", "enter", "understand"]},
    "RKE": {"name": "repo-knowledge-engineering", "destination": "understand", "command": ["journey", "enter", "understand"]},
    "DDD": {"name": "doc-driven-development", "destination": "design", "command": ["journey", "enter", "design"]},
    "RTL": {"name": "repo-task-lifecycle", "destination": "tasks", "command": ["task", "configure"]},
    "WTC": {"name": "worktree-task-coordinator", "destination": "parallel-delivery", "command": ["capability", "enable", "parallel-delivery"]},
    "RCC": {"name": "repo-change-comprehension", "destination": "close", "command": ["journey", "enter", "close"]},
    "RSA": {"name": "repo-session-alignment", "destination": "close", "command": ["journey", "enter", "close"]},
    "LHO": {"name": "local-handoff", "destination": "checkpoint", "command": ["checkpoint"]},
    "LPK": {"name": "local-pickup", "destination": "resume", "command": ["resume"]},
    "RPF": {"name": "repo-publish-finaliser", "destination": "publication", "command": ["capability", "enable", "publication"]},
    "TPU": {"name": "tracker-publisher", "destination": "tracker-sync", "command": ["capability", "enable", "tracker-sync"]},
    "TPW": {"name": "test-plan-writer", "destination": "qa-planning", "command": ["capability", "enable", "qa-planning"]},
    "RST": {"name": "repo-setup", "destination": "repository-setup", "command": ["use-separate-bootstrap-capability"], "separate": True},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def state_path(root: Path) -> Path:
    return root / STATE_DIRECTORY / STATE_FILENAME


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_state(root: Path) -> tuple[Path, dict[str, Any]]:
    target = state_path(root)
    if not target.exists():
        raise FileNotFoundError(f"workflow state not found: {target}")
    return target, json.loads(target.read_text(encoding="utf-8"))


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def start(
    root: Path,
    *,
    phase: str,
    capabilities: list[str],
    gates: list[str],
    task_mode: str,
    new_cycle: bool = False,
) -> dict[str, Any]:
    target = state_path(root)
    if target.exists():
        state = json.loads(target.read_text(encoding="utf-8"))
        if new_cycle and state.get("status") == "closed":
            now = utc_now()
            previous_cycle = {
                "created_at": state.get("created_at"),
                "closed_at": state.get("closed_at"),
                "primary_phase": state.get("primary_phase"),
                "gate_receipt_count": len(state.get("gate_receipts", [])),
            }
            state = {
                "schema_version": SCHEMA_VERSION,
                "status": "active",
                "primary_phase": phase,
                "active_capabilities": unique(capabilities),
                "outstanding_gates": unique(gates),
                "task_tracking": {"mode": task_mode, "task_ref": None},
                "continuity": {"checkpoint": None, "previous_cycle": previous_cycle},
                "created_at": now,
                "updated_at": now,
            }
            write_json(target, state)
            return {"result": "new-cycle-started", "state_path": str(target), "state": state}
        return {
            "result": "resumed-existing",
            "state_path": str(target),
            "state": state,
        }
    now = utc_now()
    state: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "active",
        "primary_phase": phase,
        "active_capabilities": unique(capabilities),
        "outstanding_gates": unique(gates),
        "task_tracking": {"mode": task_mode, "task_ref": None},
        "continuity": {"checkpoint": None},
        "created_at": now,
        "updated_at": now,
    }
    write_json(target, state)
    return {
        "result": "started",
        "state_path": str(target),
        "state": state,
    }


def checkpoint(root: Path, *, summary: str, next_action: str) -> dict[str, Any]:
    target, state = load_state(root)
    now = utc_now()
    state["continuity"]["checkpoint"] = {
        "at": now,
        "summary": summary,
        "next_action": next_action,
    }
    state["updated_at"] = now
    write_json(target, state)
    return {
        "result": "checkpointed",
        "state_path": str(target),
        "state": state,
    }


def validate_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    if state.get("status") not in {"active", "closed"}:
        errors.append("status must be active or closed")
    if state.get("primary_phase") not in PHASES:
        errors.append("primary_phase is not recognised")
    if not isinstance(state.get("active_capabilities"), list):
        errors.append("active_capabilities must be a list")
    if not isinstance(state.get("outstanding_gates"), list):
        errors.append("outstanding_gates must be a list")
    task_tracking = state.get("task_tracking")
    if not isinstance(task_tracking, dict) or task_tracking.get("mode") not in TASK_MODES:
        errors.append("task_tracking.mode is not recognised")
    return errors


def resume(root: Path) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    payload = {
        "result": "resumed" if not errors else "invalid-state",
        "state_path": str(target),
        "verification": {"valid": not errors, "errors": errors},
        "state": state,
    }
    return payload, 0 if not errors else 2


def activation_git_baseline(root: Path) -> dict[str, Any]:
    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    head = git("rev-parse", "HEAD")
    changed = git("diff", "--name-only", "HEAD")
    untracked = git("ls-files", "--others", "--exclude-standard")
    if head.returncode or changed.returncode or untracked.returncode:
        return {"gitRepository": False, "head": None, "dirtyPaths": []}
    dirty_paths = sorted(
        set(changed.stdout.splitlines()) | set(untracked.stdout.splitlines())
    )
    return {
        "gitRepository": True,
        "head": head.stdout.strip(),
        "dirtyPaths": dirty_paths[:500],
        "dirtyPathCount": len(dirty_paths),
        "dirtyPathsTruncated": len(dirty_paths) > 500,
    }


def record_activation(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    target = state_path(root)
    state = payload["state"]
    state["activation"] = {
        "activatedAt": utc_now(),
        **activation_git_baseline(root),
    }
    state["updated_at"] = state["activation"]["activatedAt"]
    write_json(target, state)
    payload["state"] = state
    payload["activation"] = state["activation"]
    return payload


def activate(root: Path, *, phase: str, task_mode: str) -> tuple[dict[str, Any], int]:
    """Create, validate, or reopen lifecycle state through one idempotent entrypoint."""
    target = state_path(root)
    if not target.exists():
        return (
            record_activation(root, start(
                root,
                phase=phase,
                capabilities=[],
                gates=[],
                task_mode=task_mode,
            )),
            0,
        )
    resumed, exit_code = resume(root)
    if exit_code:
        return resumed, exit_code
    if resumed["state"].get("status") == "closed":
        return (
            record_activation(root, start(
                root,
                phase=phase,
                capabilities=[],
                gates=[],
                task_mode=task_mode,
                new_cycle=True,
            )),
            0,
        )
    resumed["result"] = "activated-existing"
    return record_activation(root, resumed), 0


def close(root: Path, *, base: str | None = None) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    outstanding_gates = state["outstanding_gates"]
    if outstanding_gates:
        return (
            {
                "result": "closure-blocked",
                "state_path": str(target),
                "outstanding_gates": outstanding_gates,
                "state": state,
            },
            3,
        )
    documentation = (
        documentation_closure_evidence(root, base=base) if base is not None else None
    )
    if documentation is not None and not documentation["ready"]:
        return (
            {
                "result": "closure-blocked",
                "state_path": str(target),
                "outstanding_gates": [],
                "documentation": documentation,
                "state": state,
            },
            3,
        )
    now = utc_now()
    state["status"] = "closed"
    state["primary_phase"] = "close"
    state["closed_at"] = now
    state["updated_at"] = now
    write_json(target, state)
    return (
        {
            "result": "closed",
            "state_path": str(target),
            "outstanding_gates": [],
            "documentation": documentation,
            "state": state,
        },
        0,
    )


def resolve_gate(root: Path, *, gate: str, evidence: str) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    if gate not in state["outstanding_gates"]:
        return (
            {
                "result": "gate-not-outstanding",
                "state_path": str(target),
                "gate": gate,
                "state": state,
            },
            3,
        )
    now = utc_now()
    state["outstanding_gates"] = [
        outstanding for outstanding in state["outstanding_gates"] if outstanding != gate
    ]
    state.setdefault("gate_receipts", []).append(
        {"gate": gate, "evidence": evidence, "resolved_at": now}
    )
    state["updated_at"] = now
    write_json(target, state)
    return (
        {
            "result": "gate-resolved",
            "state_path": str(target),
            "gate": gate,
            "state": state,
        },
        0,
    )


def add_gates(root: Path, *, gates: list[str]) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    existing = state["outstanding_gates"]
    added = [gate for gate in unique(gates) if gate not in existing]
    state["outstanding_gates"] = existing + added
    state["updated_at"] = utc_now()
    write_json(target, state)
    return (
        {
            "result": "gates-added",
            "state_path": str(target),
            "added": added,
            "state": state,
        },
        0,
    )


def enter_journey(root: Path, *, journey: str) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    if state["status"] == "closed":
        return (
            {
                "result": "workflow-closed",
                "state_path": str(target),
                "state": state,
            },
            3,
        )
    specification = JOURNEYS[journey]
    previous_phase = state["primary_phase"]
    now = utc_now()
    state["primary_phase"] = journey
    state["active_capabilities"] = unique(
        state["active_capabilities"] + specification["capabilities"]
    )
    state["outstanding_gates"] = unique(
        state["outstanding_gates"] + specification["gates"]
    )
    state.setdefault("phase_history", []).append(
        {"from": previous_phase, "to": journey, "entered_at": now}
    )
    state["updated_at"] = now
    write_json(target, state)
    return (
        {
            "result": "journey-entered",
            "state_path": str(target),
            "journey": specification,
            "state": state,
        },
        0,
    )


def configure_tasks(
    root: Path,
    *,
    mode: str,
    task_ref: str | None,
    bundle: str,
    force: bool,
) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    if state["status"] == "closed":
        return ({"result": "workflow-closed", "state_path": str(target), "state": state}, 3)
    existing_tracking = state["task_tracking"]
    existing_mode = existing_tracking["mode"]
    mode_rank = {"none": 0, "lightweight": 1, "full": 2}
    if mode_rank[mode] < mode_rank[existing_mode] and not force:
        raise OkfAdapterError(
            "task_mode_reduction_requires_force",
            "Reducing durable task tracking requires explicit --force and does not resolve existing task gates.",
        )
    if mode == "none" and task_ref is not None:
        raise OkfAdapterError("task_mode_invalid", "Task mode none cannot retain a task reference.")
    normalized_bundle = normalise_relative(root, bundle)
    if task_ref is not None:
        normalized_ref = normalise_relative(root, task_ref, must_exist=True)
    elif mode != "none":
        normalized_ref = existing_tracking.get("task_ref")
    else:
        normalized_ref = None
    state["task_tracking"] = {
        "mode": mode,
        "task_ref": normalized_ref,
        "bundle": normalized_bundle,
    }
    if mode != "none":
        state["active_capabilities"] = unique(state["active_capabilities"] + ["task-lifecycle"])
        state["outstanding_gates"] = unique(state["outstanding_gates"] + ["task-reconciliation"])
    elif force:
        state["active_capabilities"] = [
            capability
            for capability in state["active_capabilities"]
            if capability != "task-lifecycle"
        ]
    state["updated_at"] = utc_now()
    write_json(target, state)
    return (
        {
            "result": "task-tracking-configured",
            "state_path": str(target),
            "plan": plan(mode),
            "state": state,
        },
        0,
    )


def check_tasks(root: Path, *, cli: str | None) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    tracking = state["task_tracking"]
    mode = tracking["mode"]
    if mode == "none":
        return (
            {
                "result": "task-tracking-disabled",
                "executed": False,
                "plan": plan("none"),
                "state": state,
            },
            0,
        )
    payload, exit_code = check_bundle(
        root,
        bundle=tracking.get("bundle", "tasks"),
        cli=cli,
    )
    payload["plan"] = plan(mode)
    payload["taskRef"] = tracking.get("task_ref")
    return payload, exit_code


def enable_capability(root: Path, *, capability: str) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    if state["status"] == "closed":
        return ({"result": "workflow-closed", "state_path": str(target), "state": state}, 3)
    specification = CAPABILITIES[capability]
    state["active_capabilities"] = unique(state["active_capabilities"] + [capability])
    state["outstanding_gates"] = unique(
        state["outstanding_gates"] + specification["gates"]
    )
    state["updated_at"] = utc_now()
    write_json(target, state)
    return (
        {
            "result": "capability-enabled",
            "state_path": str(target),
            "capability": specification,
            "state": state,
        },
        0,
    )


def closure_assessment(root: Path, *, base: str | None = None) -> tuple[dict[str, Any], int]:
    target, state = load_state(root)
    errors = validate_state(state)
    if errors:
        return (
            {
                "result": "invalid-state",
                "state_path": str(target),
                "verification": {"valid": False, "errors": errors},
                "state": state,
            },
            2,
        )
    outstanding = state["outstanding_gates"]

    def lane(gates: set[str], clear_status: str = "state-clear") -> dict[str, Any]:
        pending = [gate for gate in outstanding if gate in gates]
        return {"status": "pending" if pending else clear_status, "pendingGates": pending}

    capabilities = set(state["active_capabilities"])
    task_mode = state["task_tracking"]["mode"]
    lanes = {
        "change": lane({"change-explanation"}),
        "validation": lane(
            {"implementation-validation", "integrated-tree-validation", "qa-coverage"}
        ),
        "tasks": lane(
            {"task-reconciliation"},
            "not-applicable" if task_mode == "none" else "state-clear",
        ),
        "knowledge": lane({"knowledge-impact-review", "knowledge-promotion"}),
        "coordination": lane(
            {"integrated-tree-validation", "worktree-cleanup"},
            "not-enabled" if "parallel-delivery" not in capabilities else "state-clear",
        ),
        "tracker": lane(
            {"tracker-reconciliation"},
            "not-enabled" if "tracker-sync" not in capabilities else "state-clear",
        ),
        "publication": lane(
            {"publication-safety"},
            "not-enabled" if "publication" not in capabilities else "state-clear",
        ),
    }
    recognised = {
        gate
        for details in lanes.values()
        for gate in details["pendingGates"]
    }
    residual = [gate for gate in outstanding if gate not in recognised]
    lanes["other"] = {
        "status": "pending" if residual else "state-clear",
        "pendingGates": residual,
    }
    documentation = None
    if base is not None:
        documentation = documentation_closure_evidence(root, base=base)
        lanes["change"] = {
            **lanes["change"],
            **documentation["change"],
        }
        lanes["knowledge"] = {
            **lanes["knowledge"],
            **documentation["knowledge"],
        }
    ready = (
        not outstanding
        and state["status"] in {"active", "closed"}
        and (documentation is None or documentation["ready"])
    )
    return (
        {
            "result": "closure-ready" if ready else "closure-blocked",
            "ready": ready,
            "state_path": str(target),
            "lanes": lanes,
            "outstandingGates": outstanding,
            "documentation": documentation,
            "state": state,
        },
        0 if ready else 3,
    )


def route_legacy(value: str) -> tuple[dict[str, Any], int]:
    normalized = value.strip().lower()
    alias = next(
        (
            candidate
            for candidate, route in LEGACY_ROUTES.items()
            if normalized in {candidate.lower(), route["name"].lower()}
        ),
        None,
    )
    if alias is None:
        return (
            {
                "result": "legacy-route-unknown",
                "requested": value,
                "knownAliases": sorted(LEGACY_ROUTES),
            },
            2,
        )
    route = LEGACY_ROUTES[alias]
    return (
        {
            "result": "legacy-route",
            "alias": alias,
            "legacyName": route["name"],
            "destination": route["destination"],
            "command": route["command"],
            "deprecatedPeer": not route.get("separate", False),
            "separateCapability": route.get("separate", False),
        },
        0,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engineering",
        description="Manage the local Polaralias engineering workflow lifecycle.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    activate_parser = subparsers.add_parser(
        "activate", help="Idempotently create, validate, or reopen workflow state."
    )
    activate_parser.add_argument("--root", type=Path, default=Path.cwd())
    activate_parser.add_argument("--phase", choices=PHASES, default="deliver")
    activate_parser.add_argument("--task-mode", choices=TASK_MODES, default="none")
    start_parser = subparsers.add_parser("start", help="Start a workflow session.")
    start_parser.add_argument("--root", type=Path, default=Path.cwd())
    start_parser.add_argument("--phase", choices=PHASES, default="understand")
    start_parser.add_argument("--task-mode", choices=TASK_MODES, default="none")
    start_parser.add_argument("--capability", action="append", default=[])
    start_parser.add_argument("--gate", action="append", default=[])
    start_parser.add_argument(
        "--new-cycle",
        action="store_true",
        help="Start a fresh cycle only when the saved workflow is closed.",
    )
    checkpoint_parser = subparsers.add_parser(
        "checkpoint", help="Persist compact restart context."
    )
    checkpoint_parser.add_argument("--root", type=Path, default=Path.cwd())
    checkpoint_parser.add_argument("--summary", required=True)
    checkpoint_parser.add_argument("--next-action", required=True)
    resume_parser = subparsers.add_parser(
        "resume", help="Validate and return saved workflow state."
    )
    resume_parser.add_argument("--root", type=Path, default=Path.cwd())
    close_parser = subparsers.add_parser(
        "close", help="Close only when required gates are resolved."
    )
    close_parser.add_argument("--root", type=Path, default=Path.cwd())
    close_parser.add_argument("--base")
    gate_parser = subparsers.add_parser(
        "gate", help="Resolve workflow obligations from explicit evidence."
    )
    gate_subparsers = gate_parser.add_subparsers(dest="gate_command", required=True)
    add_parser = gate_subparsers.add_parser(
        "add", help="Register one or more obligations on an active workflow."
    )
    add_parser.add_argument("--root", type=Path, default=Path.cwd())
    add_parser.add_argument("--gate", action="append", required=True)
    resolve_parser = gate_subparsers.add_parser(
        "resolve", help="Resolve one outstanding gate with an evidence receipt."
    )
    resolve_parser.add_argument("--root", type=Path, default=Path.cwd())
    resolve_parser.add_argument("--gate", required=True)
    resolve_parser.add_argument("--evidence", required=True)
    journey_parser = subparsers.add_parser(
        "journey", help="Enter a selectively loaded workflow journey."
    )
    journey_subparsers = journey_parser.add_subparsers(
        dest="journey_command", required=True
    )
    enter_parser = journey_subparsers.add_parser(
        "enter", help="Enter the understand or design journey."
    )
    enter_parser.add_argument("journey", choices=tuple(JOURNEYS))
    enter_parser.add_argument("--root", type=Path, default=Path.cwd())
    task_parser = subparsers.add_parser(
        "task", help="Configure and validate proportional OKF Tasks tracking."
    )
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    configure_parser = task_subparsers.add_parser(
        "configure", help="Select none, lightweight, or full durable task tracking."
    )
    configure_parser.add_argument("--root", type=Path, default=Path.cwd())
    configure_parser.add_argument("--mode", choices=TASK_MODES, required=True)
    configure_parser.add_argument("--task-ref")
    configure_parser.add_argument("--bundle", default="tasks")
    configure_parser.add_argument(
        "--force",
        action="store_true",
        help="Explicitly reduce task mode without resolving existing reconciliation gates.",
    )
    task_check_parser = task_subparsers.add_parser(
        "check", help="Run strict validation through the authoritative OKF Tasks CLI."
    )
    task_check_parser.add_argument("--root", type=Path, default=Path.cwd())
    task_check_parser.add_argument("--cli")
    capability_parser = subparsers.add_parser(
        "capability", help="Activate a bounded optional workflow capability."
    )
    capability_subparsers = capability_parser.add_subparsers(
        dest="capability_command", required=True
    )
    enable_parser = capability_subparsers.add_parser(
        "enable", help="Enable one capability and register its evidence gates."
    )
    enable_parser.add_argument("capability", choices=tuple(CAPABILITIES))
    enable_parser.add_argument("--root", type=Path, default=Path.cwd())
    closure_parser = subparsers.add_parser(
        "closure", help="Assess independent material-work closure lanes."
    )
    closure_subparsers = closure_parser.add_subparsers(
        dest="closure_command", required=True
    )
    assess_parser = closure_subparsers.add_parser(
        "assess", help="Report whether every registered closure obligation is clear."
    )
    assess_parser.add_argument("--root", type=Path, default=Path.cwd())
    assess_parser.add_argument("--base")
    legacy_parser = subparsers.add_parser(
        "legacy", help="Resolve a legacy engineering name to the replacement surface."
    )
    legacy_subparsers = legacy_parser.add_subparsers(
        dest="legacy_command", required=True
    )
    route_parser = legacy_subparsers.add_parser(
        "route", help="Return one deterministic compatibility destination."
    )
    route_parser.add_argument("legacy_name")
    route_parser.add_argument("--root", type=Path, default=Path.cwd())
    context_parser = subparsers.add_parser(
        "context", help="Build and query disposable repository context."
    )
    context_subparsers = context_parser.add_subparsers(
        dest="context_command", required=True
    )
    find_parser = context_subparsers.add_parser(
        "find", help="Retrieve ranked repository evidence for a question."
    )
    find_parser.add_argument("query")
    find_parser.add_argument("--root", type=Path, default=Path.cwd())
    find_parser.add_argument("--limit", type=int, default=8)
    find_parser.add_argument("--scope")
    check_parser = context_subparsers.add_parser(
        "check", help="Refresh and report generated context trust signals."
    )
    check_parser.add_argument("--root", type=Path, default=Path.cwd())
    check_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    benchmark_parser = context_subparsers.add_parser(
        "benchmark", help="Measure retrieval against a versioned query corpus."
    )
    benchmark_parser.add_argument("--root", type=Path, default=Path.cwd())
    benchmark_parser.add_argument("--corpus", required=True)
    impact_parser = context_subparsers.add_parser(
        "impact", help="Classify canonical-knowledge impact for changed paths."
    )
    impact_parser.add_argument("--root", type=Path, default=Path.cwd())
    impact_parser.add_argument("--changed", action="append", required=True)
    impact_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    verify_parser = context_subparsers.add_parser(
        "verify", help="Record a review receipt for one bound knowledge document."
    )
    verify_parser.add_argument("--root", type=Path, default=Path.cwd())
    verify_parser.add_argument("--knowledge", required=True)
    verify_parser.add_argument("--evidence", required=True)
    verify_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    structure_parser = subparsers.add_parser(
        "structure", help="Inspect live source APIs, dependencies, and blast radius."
    )
    structure_subparsers = structure_parser.add_subparsers(
        dest="structure_command", required=True
    )
    structure_api_parser = structure_subparsers.add_parser(
        "file-api", help="Return signatures from one source file without function bodies."
    )
    structure_api_parser.add_argument("path")
    structure_api_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_review_parser = structure_subparsers.add_parser(
        "review", help="Prepare bounded source slices for agent review when parsing is unavailable."
    )
    structure_review_parser.add_argument("path")
    structure_review_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_review_apply_parser = structure_subparsers.add_parser(
        "review-apply", help="Validate and record source-bound agent structural evidence."
    )
    structure_review_apply_parser.add_argument("path")
    structure_review_apply_parser.add_argument("--review-file", required=True)
    structure_review_apply_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_trace_parser = structure_subparsers.add_parser(
        "trace", help="Trace incoming callers, outgoing calls, or both."
    )
    structure_trace_parser.add_argument("symbol")
    structure_trace_parser.add_argument(
        "--direction", choices=("in", "out", "both"), default="in"
    )
    structure_trace_parser.add_argument("--depth", type=int, default=2)
    structure_trace_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_map_parser = structure_subparsers.add_parser(
        "map", help="Return source clusters and dependency hubs without rendering."
    )
    structure_map_parser.add_argument("--limit", type=int, default=20)
    structure_map_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_impact_parser = structure_subparsers.add_parser(
        "impact", help="Trace callers affected by changed source files."
    )
    structure_impact_parser.add_argument("--changed", action="append", required=True)
    structure_impact_parser.add_argument("--depth", type=int, default=2)
    structure_impact_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_benchmark_parser = structure_subparsers.add_parser(
        "benchmark", help="Measure structural recall and output size on a corpus."
    )
    structure_benchmark_parser.add_argument("--corpus", required=True)
    structure_benchmark_parser.add_argument("--root", type=Path, default=Path.cwd())
    structure_search_parser = structure_subparsers.add_parser(
        "search", help="Find regex hits grouped by enclosing symbol and coupling."
    )
    structure_search_parser.add_argument("pattern")
    structure_search_parser.add_argument("--limit", type=int, default=50)
    structure_search_parser.add_argument("--root", type=Path, default=Path.cwd())
    knowledge_parser = subparsers.add_parser(
        "knowledge", help="Validate and maintain canonical OKF knowledge."
    )
    knowledge_subparsers = knowledge_parser.add_subparsers(
        dest="knowledge_command", required=True
    )
    knowledge_check_parser = knowledge_subparsers.add_parser(
        "check", help="Validate typed concepts and their durable relationship graph."
    )
    knowledge_check_parser.add_argument("--root", type=Path, default=Path.cwd())
    knowledge_check_parser.add_argument("--bundle", required=True)
    knowledge_build_parser = knowledge_subparsers.add_parser(
        "build-indexes", help="Build deterministic progressive-disclosure indexes."
    )
    knowledge_build_parser.add_argument("--root", type=Path, default=Path.cwd())
    knowledge_build_parser.add_argument("--bundle", required=True)
    knowledge_build_parser.add_argument("--force", action="store_true")
    knowledge_register_parser = knowledge_subparsers.add_parser(
        "register", help="Bind one typed canonical concept to explicit source patterns."
    )
    knowledge_register_parser.add_argument("--root", type=Path, default=Path.cwd())
    knowledge_register_parser.add_argument("--knowledge", required=True)
    knowledge_register_parser.add_argument("--source", action="append", required=True)
    knowledge_register_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    documentation_parser = subparsers.add_parser(
        "documentation", help="Assess and complete event-driven documentation work."
    )
    documentation_subparsers = documentation_parser.add_subparsers(
        dest="documentation_command", required=True
    )
    documentation_assess_parser = documentation_subparsers.add_parser(
        "assess", help="Classify documentation impact from a Git base."
    )
    documentation_assess_parser.add_argument("--root", type=Path, default=Path.cwd())
    documentation_assess_parser.add_argument("--base", required=True)
    documentation_assess_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    documentation_apply_parser = documentation_subparsers.add_parser(
        "apply", help="Validate authored documentation, reader retrieval, and freshness."
    )
    documentation_apply_parser.add_argument("--root", type=Path, default=Path.cwd())
    documentation_apply_parser.add_argument("--base", required=True)
    documentation_apply_parser.add_argument("--bundle", required=True)
    documentation_apply_parser.add_argument("--knowledge", action="append", required=True)
    documentation_apply_parser.add_argument("--evidence", required=True)
    documentation_apply_parser.add_argument("--reader-query", action="append", required=True)
    documentation_apply_parser.add_argument(
        "--manifest", default=".polaralias/repo-context.json"
    )
    change_parser = subparsers.add_parser(
        "change", help="Record bounded causal change comprehension."
    )
    change_subparsers = change_parser.add_subparsers(
        dest="change_command", required=True
    )
    change_explain_parser = change_subparsers.add_parser(
        "explain", help="Record an RCC-compatible explanation receipt for a Git delta."
    )
    change_explain_parser.add_argument("--root", type=Path, default=Path.cwd())
    change_explain_parser.add_argument("--base", required=True)
    change_explain_parser.add_argument("--summary", required=True)
    host_parser = subparsers.add_parser(
        "host", help="Describe or install bounded host integration."
    )
    host_subparsers = host_parser.add_subparsers(dest="host_command", required=True)
    host_recipe_parser = host_subparsers.add_parser(
        "recipe", help="Return MCP and Git-gate setup without changing host configuration."
    )
    host_recipe_parser.add_argument("--root", type=Path, default=Path.cwd())
    host_recipe_parser.add_argument("--host", choices=HOSTS, required=True)
    host_recipe_parser.add_argument("--base", required=True)
    host_install_parser = host_subparsers.add_parser(
        "install", help="Install a local pre-push gate and supported project MCP config."
    )
    host_install_parser.add_argument("--root", type=Path, default=Path.cwd())
    host_install_parser.add_argument("--host", choices=HOSTS, required=True)
    host_install_parser.add_argument("--base", required=True)
    host_install_parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    try:
        if args.command == "activate":
            payload, exit_code = activate(root, phase=args.phase, task_mode=args.task_mode)
        elif args.command == "start":
            payload = start(
                root,
                phase=args.phase,
                capabilities=args.capability,
                gates=args.gate,
                task_mode=args.task_mode,
                new_cycle=args.new_cycle,
            )
            exit_code = 0
        elif args.command == "checkpoint":
            payload = checkpoint(
                root,
                summary=args.summary,
                next_action=args.next_action,
            )
            exit_code = 0
        elif args.command == "resume":
            payload, exit_code = resume(root)
        elif args.command == "close":
            payload, exit_code = close(root, base=args.base)
        elif args.command == "gate" and args.gate_command == "resolve":
            payload, exit_code = resolve_gate(
                root,
                gate=args.gate,
                evidence=args.evidence,
            )
        elif args.command == "gate" and args.gate_command == "add":
            payload, exit_code = add_gates(root, gates=args.gate)
        elif args.command == "journey" and args.journey_command == "enter":
            payload, exit_code = enter_journey(root, journey=args.journey)
        elif args.command == "task" and args.task_command == "configure":
            payload, exit_code = configure_tasks(
                root,
                mode=args.mode,
                task_ref=args.task_ref,
                bundle=args.bundle,
                force=args.force,
            )
        elif args.command == "task" and args.task_command == "check":
            payload, exit_code = check_tasks(root, cli=args.cli)
        elif args.command == "capability" and args.capability_command == "enable":
            payload, exit_code = enable_capability(root, capability=args.capability)
        elif args.command == "closure" and args.closure_command == "assess":
            payload, exit_code = closure_assessment(root, base=args.base)
        elif args.command == "legacy" and args.legacy_command == "route":
            payload, exit_code = route_legacy(args.legacy_name)
        elif args.command == "context" and args.context_command == "find":
            payload, exit_code = invoke_operation(
                root,
                "repo_find_context",
                {"query": args.query, "limit": args.limit, "scope": args.scope},
            )
        elif args.command == "context" and args.context_command == "check":
            payload, exit_code = invoke_operation(
                root, "repo_context_check", {"manifest": args.manifest}
            )
        elif args.command == "context" and args.context_command == "benchmark":
            payload = benchmark_context(root, args.corpus)
            exit_code = 0
        elif args.command == "context" and args.context_command == "impact":
            payload, exit_code = invoke_operation(
                root,
                "repo_knowledge_impact",
                {"changedPaths": args.changed, "manifest": args.manifest},
            )
        elif args.command == "context" and args.context_command == "verify":
            payload, exit_code = invoke_operation(
                root,
                "repo_knowledge_verify",
                {
                    "knowledge": args.knowledge,
                    "evidence": args.evidence,
                    "manifest": args.manifest,
                },
            )
        elif args.command == "structure" and args.structure_command == "file-api":
            payload, exit_code = invoke_operation(
                root, "repo_file_api", {"path": args.path}
            )
        elif args.command == "structure" and args.structure_command == "review":
            payload, exit_code = invoke_operation(
                root, "repo_prepare_code_review", {"path": args.path}
            )
        elif args.command == "structure" and args.structure_command == "review-apply":
            review_path, _ = repository_relative_path(
                root,
                args.review_file,
                escape_code="structure_review_file_escape",
                missing_code="structure_review_file_missing",
            )
            try:
                review = json.loads(review_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ContextError("structure_review_invalid", f"Review evidence is invalid JSON at line {exc.lineno}.") from exc
            payload, exit_code = invoke_operation(
                root, "repo_record_code_review", {"path": args.path, "review": review}
            )
        elif args.command == "structure" and args.structure_command == "trace":
            payload, exit_code = invoke_operation(
                root,
                "repo_trace_symbol",
                {
                    "symbol": args.symbol,
                    "direction": args.direction,
                    "depth": args.depth,
                },
            )
        elif args.command == "structure" and args.structure_command == "map":
            payload, exit_code = invoke_operation(
                root, "repo_structure_map", {"limit": args.limit}
            )
        elif args.command == "structure" and args.structure_command == "impact":
            payload, exit_code = invoke_operation(
                root,
                "repo_change_impact",
                {"changedPaths": args.changed, "depth": args.depth},
            )
        elif args.command == "structure" and args.structure_command == "benchmark":
            payload, exit_code = invoke_operation(
                root, "repo_structure_benchmark", {"corpus": args.corpus}
            )
        elif args.command == "structure" and args.structure_command == "search":
            payload, exit_code = invoke_operation(
                root,
                "repo_find_all",
                {"pattern": args.pattern, "limit": args.limit},
            )
        elif args.command == "knowledge" and args.knowledge_command == "check":
            payload, exit_code = invoke_operation(
                root, "repo_knowledge_bundle_check", {"bundle": args.bundle}
            )
        elif args.command == "knowledge" and args.knowledge_command == "build-indexes":
            payload, exit_code = invoke_operation(
                root,
                "repo_knowledge_build_indexes",
                {"bundle": args.bundle, "force": args.force},
            )
        elif args.command == "knowledge" and args.knowledge_command == "register":
            payload, exit_code = invoke_operation(
                root,
                "repo_knowledge_register",
                {
                    "knowledge": args.knowledge,
                    "sources": args.source,
                    "manifest": args.manifest,
                },
            )
        elif args.command == "documentation" and args.documentation_command == "assess":
            payload, exit_code = invoke_operation(
                root,
                "repo_documentation_assess",
                {"base": args.base, "manifest": args.manifest},
            )
        elif args.command == "documentation" and args.documentation_command == "apply":
            payload, exit_code = invoke_operation(
                root,
                "repo_documentation_apply",
                {
                    "base": args.base,
                    "bundle": args.bundle,
                    "knowledgePaths": args.knowledge,
                    "evidence": args.evidence,
                    "readerQueries": args.reader_query,
                    "manifest": args.manifest,
                },
            )
        elif args.command == "change" and args.change_command == "explain":
            payload, exit_code = invoke_operation(
                root,
                "repo_change_explain",
                {"base": args.base, "summary": args.summary},
            )
        elif args.command == "host" and args.host_command == "recipe":
            payload = host_recipe(root, host=args.host, base=args.base)
            exit_code = 0
        elif args.command == "host" and args.host_command == "install":
            payload = install_host(
                root, host=args.host, base=args.base, force=args.force
            )
            exit_code = 0
        else:  # pragma: no cover - argparse owns command validation.
            raise AssertionError(f"unsupported command: {args.command}")
    except FileNotFoundError:
        payload = {
            "result": "missing-state",
            "state_path": str(state_path(root)),
            "error": {
                "code": "workflow_state_missing",
                "message": "Run engineering start before this lifecycle operation.",
            },
        }
        exit_code = 2
    except json.JSONDecodeError as exc:
        payload = {
            "result": "invalid-state",
            "state_path": str(state_path(root)),
            "error": {
                "code": "workflow_state_invalid_json",
                "message": f"Workflow state is not valid JSON at line {exc.lineno}.",
            },
        }
        exit_code = 2
    except ContextError as exc:
        payload = {
            "result": "context-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    except OkfAdapterError as exc:
        payload = {
            "result": "task-adapter-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    except KnowledgeError as exc:
        payload = {
            "result": "knowledge-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    except DocumentationError as exc:
        payload = {
            "result": "documentation-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    except HostIntegrationError as exc:
        payload = {
            "result": "host-integration-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    except OperationError as exc:
        payload = {
            "result": "operation-error",
            "error": {"code": exc.code, "message": exc.message},
        }
        exit_code = 2
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
