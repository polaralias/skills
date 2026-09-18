from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from host_integration import install_codex_routing


def _load_cases(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != 1 or not isinstance(value.get("cases"), list):
        raise ValueError("Evaluation corpus must use schema 1 and contain cases.")
    return value["cases"]


def _grade(case: dict[str, Any], root: Path, final: str, returncode: int) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    check("agent-exit", returncode == 0, f"exit code {returncode}")
    try:
        state_path = root / ".engineering-workflow" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
        activated = bool(state.get("activation", {}).get("activatedAt"))
        state_detail = f"activation receipt exists={activated}, expected={bool(case.get('expectWorkflowState'))}"
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        state = {}
        activated = None
        state_detail = f"state could not be inspected: {type(exc).__name__}: {exc}"
    expected_state = bool(case.get("expectWorkflowState"))
    check("workflow-activation", activated == expected_state, state_detail)
    if case.get("mustActivateBefore"):
        try:
            activation = state.get("activation", {})
            dirty_at_activation = set(activation.get("dirtyPaths", []))
            required_clean = set(case["mustActivateBefore"])
            passed = bool(activation.get("activatedAt")) and not required_clean.intersection(dirty_at_activation)
            detail = f"dirty at activation={sorted(dirty_at_activation)}"
        except (OSError, json.JSONDecodeError, AttributeError, TypeError) as exc:
            passed = False
            detail = f"activation evidence unavailable: {type(exc).__name__}: {exc}"
        check("workflow-activated-before-mutation", passed, detail)
    for text in case.get("finalContains", []):
        check(f"final-contains:{text}", text in final, "required final-response marker")
    for text in case.get("finalExcludes", []):
        check(f"final-excludes:{text}", text not in final, "forbidden final-response marker")
    for relative, text in case.get("filesContain", {}).items():
        path = root / relative
        try:
            content = path.read_text(encoding="utf-8") if path.is_file() else ""
            detail = f"required text: {text}"
        except OSError as exc:
            content = ""
            detail = f"artefact could not be read: {type(exc).__name__}: {exc}"
        check(f"file-contains:{relative}", text in content, detail)
    for relative in case.get("forbiddenPaths", []):
        check(f"path-absent:{relative}", not (root / relative).exists(), "forbidden artefact")
    return {
        "id": case["id"],
        "category": case["category"],
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
        "finalResponse": final,
    }


def _bounded_diagnostics(stdout: str, stderr: str) -> dict[str, str]:
    return {"stdoutTail": stdout[-4_000:], "stderrTail": stderr[-4_000:]}


def _run_case(case: dict[str, Any], codex: str, model: str | None, timeout: int) -> dict[str, Any]:
    root = Path(tempfile.mkdtemp(prefix="ewf-agent-eval-"))
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "eval@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "EWF Eval"], cwd=root, check=True)
        for relative, content in case.get("setup", {}).items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        if case.get("installCodexRouting"):
            install_codex_routing(root)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "evaluation fixture"], cwd=root, check=True)
        # Seed an evaluator-owned, deliberately unactivated state file. Windows
        # sandbox-created files can receive ACLs the parent cannot read. Activation
        # overwrites this existing file and adds the receipt that the grader checks;
        # mere file existence never counts as activation.
        control = root / ".engineering-workflow"
        control.mkdir()
        (control / "state.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "closed",
                    "primary_phase": "close",
                    "active_capabilities": [],
                    "outstanding_gates": [],
                    "task_tracking": {"mode": "none", "task_ref": None},
                    "continuity": {"checkpoint": None},
                    "created_at": "2000-01-01T00:00:00Z",
                    "updated_at": "2000-01-01T00:00:00Z",
                    "closed_at": "2000-01-01T00:00:00Z",
                    "gate_receipts": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        final_path = root / ".agent-final.txt"
        command = [codex, "exec", "--ephemeral", "--sandbox", "workspace-write", "--color", "never", "--cd", str(root), "--output-last-message", str(final_path)]
        if model:
            command.extend(["--model", model])
        command.append(case["prompt"])
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags, start_new_session=os.name != "nt")
        try:
            stdout, _ = process.communicate(timeout=timeout)
            try:
                final = final_path.read_text(encoding="utf-8") if final_path.is_file() else stdout
            except OSError:
                final = stdout
            return _grade(case, root, final, process.returncode)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False)
            else:
                os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            report = _grade(case, root, "", 124)
            report["runnerDiagnostics"] = _bounded_diagnostics(stdout, stderr)
            return report
    finally:
        # Windows may retain short-lived handles after a terminated Codex process.
        # Evaluation evidence must not be replaced by cleanup failure.
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded end-to-end agent behaviour evaluations for engineering-workflow.")
    parser.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "tests" / "evals" / "agent-behaviour.json")
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--codex", default=shutil.which("codex") or "codex")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    cases = _load_cases(args.corpus.resolve())
    if args.case_ids:
        cases = [case for case in cases if case.get("id") in set(args.case_ids)]
    if not cases:
        raise SystemExit("No evaluation cases selected.")
    reports = [_run_case(case, args.codex, args.model, args.timeout) for case in cases]
    output = {
        "result": "agent-behaviour-evaluated",
        "caseCount": len(reports),
        "passedCount": sum(item["passed"] for item in reports),
        "failedCount": sum(not item["passed"] for item in reports),
        "cases": reports,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output["failedCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
