from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from documentation import apply_documentation, assess_documentation, explain_change
from knowledge import build_indexes, inspect_bundle, register_knowledge
from repo_context import (
    check_context,
    find_context,
    impact_context,
    verify_knowledge,
)
from structure import (
    benchmark_structure,
    change_impact,
    file_api,
    prepare_agent_review,
    record_agent_review,
    repository_map,
    search_structure,
    trace_symbol,
)


DEFAULT_MANIFEST = ".polaralias/repo-context.json"
OperationHandler = Callable[[Path, dict[str, Any]], tuple[dict[str, Any], int]]


class OperationError(Exception):
    def __init__(self, message: str, *, code: str = "invalid_operation_arguments") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Operation:
    name: str
    title: str
    description: str
    input_schema: dict[str, Any]
    read_only: bool
    idempotent: bool
    handler: OperationHandler

    def mcp_tool(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": {
                "readOnlyHint": self.read_only,
                "idempotentHint": self.idempotent,
            },
        }


def string(arguments: dict[str, Any], name: str, *, default: str | None = None) -> str:
    value = arguments.get(name, default)
    if not isinstance(value, str) or not value.strip():
        raise OperationError(f"Argument '{name}' must be a non-empty string.")
    return value


def optional_string(arguments: dict[str, Any], name: str) -> str | None:
    value = arguments.get(name)
    if value is not None and not isinstance(value, str):
        raise OperationError(f"Argument '{name}' must be a string.")
    return value


def integer(arguments: dict[str, Any], name: str, *, default: int) -> int:
    value = arguments.get(name, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise OperationError(f"Argument '{name}' must be an integer.")
    return value


def boolean(arguments: dict[str, Any], name: str, *, default: bool = False) -> bool:
    value = arguments.get(name, default)
    if not isinstance(value, bool):
        raise OperationError(f"Argument '{name}' must be a boolean.")
    return value


def strings(arguments: dict[str, Any], name: str) -> list[str]:
    value = arguments.get(name)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        raise OperationError(f"Argument '{name}' must be a non-empty string array.")
    return value


def mapping(arguments: dict[str, Any], name: str) -> dict[str, Any]:
    value = arguments.get(name)
    if not isinstance(value, dict):
        raise OperationError(f"Argument '{name}' must be an object.")
    return value


def context_find(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        find_context(
            root,
            string(arguments, "query"),
            limit=integer(arguments, "limit", default=8),
            scope=optional_string(arguments, "scope"),
        ),
        0,
    )


def context_check(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return check_context(root, manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST)), 0


def knowledge_impact(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        impact_context(
            root,
            strings(arguments, "changedPaths"),
            manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST),
        ),
        0,
    )


def knowledge_verify(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        verify_knowledge(
            root,
            string(arguments, "knowledge"),
            string(arguments, "evidence"),
            manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST),
        ),
        0,
    )


def knowledge_check(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return inspect_bundle(root, string(arguments, "bundle"))


def knowledge_build(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        build_indexes(
            root,
            string(arguments, "bundle"),
            force=boolean(arguments, "force"),
        ),
        0,
    )


def knowledge_register(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        register_knowledge(
            root,
            string(arguments, "knowledge"),
            strings(arguments, "sources"),
            manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST),
        ),
        0,
    )


def documentation_assess(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return assess_documentation(
        root,
        base=string(arguments, "base"),
        manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST),
    )


def documentation_apply(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        apply_documentation(
            root,
            base=string(arguments, "base"),
            bundle=string(arguments, "bundle"),
            knowledge_paths=strings(arguments, "knowledgePaths"),
            evidence=string(arguments, "evidence"),
            reader_queries=strings(arguments, "readerQueries"),
            manifest=string(arguments, "manifest", default=DEFAULT_MANIFEST),
        ),
        0,
    )


def change_explain(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        explain_change(
            root,
            base=string(arguments, "base"),
            summary=string(arguments, "summary"),
        ),
        0,
    )


def structure_file_api(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return file_api(root, string(arguments, "path")), 0


def structure_agent_review(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return prepare_agent_review(root, string(arguments, "path")), 0


def structure_record_agent_review(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return record_agent_review(root, string(arguments, "path"), mapping(arguments, "review")), 0


def structure_trace(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        trace_symbol(
            root,
            string(arguments, "symbol"),
            direction=string(arguments, "direction", default="in"),
            depth=integer(arguments, "depth", default=2),
        ),
        0,
    )


def structure_map(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return repository_map(root, limit=integer(arguments, "limit", default=20)), 0


def structure_change_impact(
    root: Path, arguments: dict[str, Any]
) -> tuple[dict[str, Any], int]:
    return (
        change_impact(
            root,
            strings(arguments, "changedPaths"),
            depth=integer(arguments, "depth", default=2),
        ),
        0,
    )


def structure_benchmark(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return benchmark_structure(root, string(arguments, "corpus")), 0


def structure_search(root: Path, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    return (
        search_structure(
            root,
            string(arguments, "pattern"),
            limit=integer(arguments, "limit", default=50),
        ),
        0,
    )


def object_schema(
    properties: dict[str, Any], required: list[str] | None = None
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


STRING = {"type": "string"}
STRING_ARRAY = {"type": "array", "items": STRING, "minItems": 1}


OPERATIONS = (
    Operation(
        "repo_find_context",
        "Find repository context",
        "Rank repository-local evidence for a query with the disposable BM25 index.",
        object_schema(
            {
                "query": STRING,
                "limit": {"type": "integer", "minimum": 1, "default": 8},
                "scope": STRING,
            },
            ["query"],
        ),
        True,
        True,
        context_find,
    ),
    Operation(
        "repo_context_check",
        "Check repository knowledge freshness",
        "Check indexed evidence and declared knowledge bindings without changing governed knowledge.",
        object_schema({"manifest": STRING}),
        True,
        True,
        context_check,
    ),
    Operation(
        "repo_knowledge_impact",
        "Classify knowledge impact",
        "Classify changed paths against explicit bindings and conservative lexical candidates.",
        object_schema({"changedPaths": STRING_ARRAY, "manifest": STRING}, ["changedPaths"]),
        True,
        True,
        knowledge_impact,
    ),
    Operation(
        "repo_knowledge_verify",
        "Record knowledge verification",
        "Record an evidence-backed verification receipt in the repository knowledge manifest.",
        object_schema(
            {"knowledge": STRING, "evidence": STRING, "manifest": STRING},
            ["knowledge", "evidence"],
        ),
        False,
        False,
        knowledge_verify,
    ),
    Operation(
        "repo_knowledge_bundle_check",
        "Validate an OKF knowledge bundle",
        "Validate typed concepts and the resolved durable relationship graph.",
        object_schema({"bundle": STRING}, ["bundle"]),
        True,
        True,
        knowledge_check,
    ),
    Operation(
        "repo_knowledge_build_indexes",
        "Build OKF knowledge indexes",
        "Build deterministic progressive-disclosure indexes.",
        object_schema(
            {"bundle": STRING, "force": {"type": "boolean", "default": False}},
            ["bundle"],
        ),
        False,
        True,
        knowledge_build,
    ),
    Operation(
        "repo_knowledge_register",
        "Register canonical knowledge bindings",
        "Bind one typed OKF concept to explicit repository source patterns.",
        object_schema(
            {"knowledge": STRING, "sources": STRING_ARRAY, "manifest": STRING},
            ["knowledge", "sources"],
        ),
        False,
        True,
        knowledge_register,
    ),
    Operation(
        "repo_documentation_assess",
        "Assess documentation impact",
        "Classify a material Git delta as no-op, update, or decision-required.",
        object_schema({"base": STRING, "manifest": STRING}, ["base"]),
        True,
        True,
        documentation_assess,
    ),
    Operation(
        "repo_documentation_apply",
        "Complete documentation validation",
        "Validate authored documentation, reader retrieval, graph integrity, and freshness.",
        object_schema(
            {
                "base": STRING,
                "bundle": STRING,
                "knowledgePaths": STRING_ARRAY,
                "evidence": STRING,
                "readerQueries": STRING_ARRAY,
                "manifest": STRING,
            },
            ["base", "bundle", "knowledgePaths", "evidence", "readerQueries"],
        ),
        False,
        False,
        documentation_apply,
    ),
    Operation(
        "repo_change_explain",
        "Record change explanation",
        "Record a causal explanation receipt for the current material Git delta.",
        object_schema({"base": STRING, "summary": STRING}, ["base", "summary"]),
        False,
        False,
        change_explain,
    ),
    Operation(
        "repo_file_api",
        "Read a file API surface",
        "Return signatures and line locations without function bodies.",
        object_schema({"path": STRING}, ["path"]),
        True,
        True,
        structure_file_api,
    ),
    Operation(
        "repo_prepare_code_review",
        "Prepare bounded agent code review",
        "Return bounded source slices and a strict review schema when parser evidence is unavailable.",
        object_schema({"path": STRING}, ["path"]),
        True,
        True,
        structure_agent_review,
    ),
    Operation(
        "repo_record_code_review",
        "Record bounded agent code review",
        "Validate and cache source-digest-bound structural evidence for a file without parser coverage.",
        object_schema({"path": STRING, "review": {"type": "object"}}, ["path", "review"]),
        False,
        True,
        structure_record_agent_review,
    ),
    Operation(
        "repo_trace_symbol",
        "Trace symbol dependencies",
        "Trace bounded incoming callers, outgoing calls, or both from live source.",
        object_schema(
            {
                "symbol": STRING,
                "direction": {"type": "string", "enum": ["in", "out", "both"], "default": "in"},
                "depth": {"type": "integer", "minimum": 1, "maximum": 5, "default": 2},
            },
            ["symbol"],
        ),
        True,
        True,
        structure_trace,
    ),
    Operation(
        "repo_structure_map",
        "Summarise repository structure",
        "Return source clusters and dependency hubs for orientation without rendering a graph.",
        object_schema({"limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}}),
        True,
        True,
        structure_map,
    ),
    Operation(
        "repo_change_impact",
        "Trace structural change impact",
        "Find callers transitively affected by symbols in changed source files.",
        object_schema(
            {
                "changedPaths": STRING_ARRAY,
                "depth": {"type": "integer", "minimum": 1, "maximum": 5, "default": 2},
            },
            ["changedPaths"],
        ),
        True,
        True,
        structure_change_impact,
    ),
    Operation(
        "repo_structure_benchmark",
        "Benchmark structural context",
        "Measure exact expected-symbol recall and output size on a checked-in corpus.",
        object_schema({"corpus": STRING}, ["corpus"]),
        True,
        True,
        structure_benchmark,
    ),
    Operation(
        "repo_find_all",
        "Find all structural matches",
        "Find regex matches in source, grouped by enclosing symbol and ranked by coupling.",
        object_schema(
            {
                "pattern": STRING,
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
            },
            ["pattern"],
        ),
        True,
        True,
        structure_search,
    ),
)

OPERATION_BY_NAME = {operation.name: operation for operation in OPERATIONS}


def mcp_tools() -> list[dict[str, Any]]:
    return [operation.mcp_tool() for operation in OPERATIONS]


def invoke_operation(
    root: Path, name: str, raw_arguments: Any
) -> tuple[dict[str, Any], int]:
    if not isinstance(raw_arguments, dict):
        raise OperationError("Operation arguments must be an object.")
    operation = OPERATION_BY_NAME.get(name)
    if operation is None:
        raise KeyError(name)
    return operation.handler(root, raw_arguments)
