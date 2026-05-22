#!/usr/bin/env python3
from __future__ import annotations

import importlib
import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_binary(name: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"Missing required executable: {name}")


def check_python_module(name: str) -> None:
    try:
        importlib.import_module(name)
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"Missing required Python module: {name}\n{exc}") from exc


def check_node_module(name: str) -> None:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Missing required executable: node")
    result = subprocess.run(
        [node, "-e", f"require('{name}'); console.log('{name} ok')"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"Missing required Node module: {name}\n"
            f"Run `npm ci` from the skill root: {ROOT}\n"
            f"stderr:\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Check dependencies for the DOCX assistant skill.")
    parser.add_argument("--mode", choices=("simple", "branded"), default="branded")
    parser.add_argument("--qa", choices=("fast", "thorough", "auto", "none"), default="fast")
    args = parser.parse_args()

    check_python_module("docx")
    check_python_module("jsonschema")
    check_python_module("lxml")
    if args.mode == "branded":
        check_binary("node")
        check_node_module("docx")
    if args.qa == "thorough":
        check_python_module("fitz")
        check_python_module("PIL")
    print(f"Preflight passed: {ROOT} ({args.mode}, {args.qa})")


if __name__ == "__main__":
    main()
