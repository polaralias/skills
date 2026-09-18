from __future__ import annotations

import argparse
import json
from pathlib import Path

from repo_context import ContextError, repository_relative_path
from structure import NON_CODE_LANGUAGES, build_structure, detect_language, retrieval_symbol_spans


def main() -> int:
    parser = argparse.ArgumentParser(description="Isolated Tree-sitter span extraction worker.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--path", action="append", required=True)
    parser.add_argument("--graph", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.graph:
            graph = build_structure(root, include_paths=set(args.path))
            print(
                json.dumps(
                    {
                        "symbols": [symbol.public() for symbol in graph["symbols"]],
                        "incoming": {key: sorted(value) for key, value in graph["incoming"].items()},
                        "outgoing": {key: sorted(value) for key, value in graph["outgoing"].items()},
                        "parseWarnings": graph["parseWarnings"],
                    }
                )
            )
            return 0
        target, relative = repository_relative_path(
            root,
            args.path[0],
            escape_code="structure_path_escape",
            missing_code="structure_path_missing",
        )
        language = detect_language(target)
        symbols = (
            retrieval_symbol_spans(root, target)
            if language and language not in NON_CODE_LANGUAGES
            else []
        )
        print(json.dumps({"path": relative, "language": language, "symbols": symbols}))
        return 0
    except (ContextError, OSError, RuntimeError) as exc:
        print(json.dumps({"path": args.path[0], "symbols": [], "warning": type(exc).__name__}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
