from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from documentation import DocumentationError
from knowledge import KnowledgeError
from operations import OperationError, invoke_operation, mcp_tools
from repo_context import ContextError


LEGACY_PROTOCOL_VERSION = "2025-11-25"
MODERN_PROTOCOL_VERSION = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = [MODERN_PROTOCOL_VERSION, LEGACY_PROTOCOL_VERSION]
SERVER_INFO = {"name": "polaralias-engineering-workflow", "version": "1.3.0"}
SERVER_INFO_KEY = "io.modelcontextprotocol/serverInfo"
PROTOCOL_VERSION_KEY = "io.modelcontextprotocol/protocolVersion"
CLIENT_CAPABILITIES_KEY = "io.modelcontextprotocol/clientCapabilities"
MAX_MESSAGE_BYTES = 4 * 1024 * 1024
TOOLS = mcp_tools()


def protocol_error(
    identifier: Any,
    code: int,
    message: str,
    *,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": identifier,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        payload["error"]["data"] = data
    return payload


def modern_result(payload: dict[str, Any], *, cacheable: bool = False) -> dict[str, Any]:
    result = dict(payload)
    result["resultType"] = "complete"
    result["_meta"] = {SERVER_INFO_KEY: SERVER_INFO}
    if cacheable:
        result["ttlMs"] = 0
        result["cacheScope"] = "private"
    return result


def tool_result(
    payload: dict[str, Any], *, is_error: bool = False, modern: bool = False
) -> dict[str, Any]:
    result = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
        "isError": is_error,
    }
    return modern_result(result) if modern else result


def modern_request_error(request: dict[str, Any]) -> dict[str, Any] | None:
    params = request.get("params")
    meta = params.get("_meta") if isinstance(params, dict) else None
    version = meta.get(PROTOCOL_VERSION_KEY) if isinstance(meta, dict) else None
    if request.get("method") == "server/discover" or version is not None:
        if version != MODERN_PROTOCOL_VERSION:
            return protocol_error(
                request.get("id"),
                -32022,
                "Unsupported protocol version",
                data={"supported": SUPPORTED_PROTOCOL_VERSIONS, "requested": version},
            )
        if not isinstance(meta.get(CLIENT_CAPABILITIES_KEY), dict):
            return protocol_error(
                request.get("id"),
                -32602,
                "Modern requests require client capabilities in params._meta.",
            )
    return None


def domain_error(
    identifier: Any,
    exc: ContextError | KnowledgeError | DocumentationError | OperationError,
    *,
    modern: bool,
) -> dict[str, Any]:
    payload = {"code": exc.code, "message": exc.message}
    return {
        "jsonrpc": "2.0",
        "id": identifier,
        "result": tool_result(payload, is_error=True, modern=modern),
    }


def dispatch(root: Path, request: dict[str, Any]) -> dict[str, Any] | None:
    identifier = request.get("id")
    if request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        return protocol_error(identifier, -32600, "Invalid Request")
    if "id" not in request:
        return None
    method = request["method"]
    modern_error = modern_request_error(request)
    if modern_error is not None:
        return modern_error
    params = request.get("params")
    meta = params.get("_meta") if isinstance(params, dict) else None
    modern = isinstance(meta, dict) and meta.get(PROTOCOL_VERSION_KEY) == MODERN_PROTOCOL_VERSION
    if method == "server/discover":
        return {
            "jsonrpc": "2.0",
            "id": identifier,
            "result": modern_result(
                {
                    "supportedVersions": SUPPORTED_PROTOCOL_VERSIONS,
                    "capabilities": {"tools": {}},
                    "instructions": "Use shared engineering operations for bounded repository evidence and governed maintenance.",
                },
                cacheable=True,
            ),
        }
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": identifier,
            "result": {
                "protocolVersion": LEGACY_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": identifier,
            "result": modern_result({}) if modern else {},
        }
    if method == "tools/list":
        listed = {"tools": TOOLS}
        return {
            "jsonrpc": "2.0",
            "id": identifier,
            "result": modern_result(listed, cacheable=True) if modern else listed,
        }
    if method != "tools/call":
        return protocol_error(identifier, -32601, "Method not found")
    if not isinstance(params, dict) or not isinstance(params.get("name"), str):
        return protocol_error(identifier, -32602, "Invalid tools/call parameters")
    try:
        payload, _ = invoke_operation(root, params["name"], params.get("arguments", {}))
    except KeyError:
        return protocol_error(identifier, -32602, f"Unknown tool: {params['name']}")
    except (ContextError, KnowledgeError, DocumentationError, OperationError) as exc:
        return domain_error(identifier, exc, modern=modern)
    return {
        "jsonrpc": "2.0",
        "id": identifier,
        "result": tool_result(payload, modern=modern),
    }


def run(root: Path) -> int:
    for raw_line in sys.stdin.buffer:
        if len(raw_line) > MAX_MESSAGE_BYTES:
            response = protocol_error(None, -32600, "Message exceeds maximum size")
        else:
            try:
                request = json.loads(raw_line.decode("utf-8"))
                response = (
                    dispatch(root, request)
                    if isinstance(request, dict)
                    else protocol_error(None, -32600, "Invalid Request")
                )
            except (UnicodeDecodeError, json.JSONDecodeError):
                response = protocol_error(None, -32700, "Parse error")
        if response is not None:
            sys.stdout.write(
                json.dumps(response, separators=(",", ":"), ensure_ascii=False) + "\n"
            )
            sys.stdout.flush()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Expose shared engineering workflow operations over MCP stdio."
    )
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    return run(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
