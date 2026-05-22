#!/usr/bin/env python3
"""Validate a DOCX JSON spec and render it through the selected mode."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

from embed_font import embed as embed_cover_font
from layout_lint import lint_docx
from render_contact_sheet import render_contact_sheet
from validate_docx import validate_docx

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "references" / "spec-schema.json"
SIMPLE_RENDERER = ROOT / "scripts" / "build_simple_from_spec.py"
BRANDED_RENDERER = ROOT / "scripts" / "build_branded_from_spec.js"


def load_json(path: str) -> dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def find_raw_ooxml(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "raw_docx_xml":
            found.append(path)
        for key, child in value.items():
            found.extend(find_raw_ooxml(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_raw_ooxml(child, f"{path}[{index}]"))
    return found


def validate_spec(spec: dict[str, Any], *, allow_raw_ooxml: bool) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda error: list(error.path))
    if errors:
        lines = []
        for error in errors:
            json_path = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in error.path
            )
            lines.append(f"{json_path}: {error.message}")
        raise SystemExit("Spec validation failed:\n" + "\n".join(lines))
    raw_paths = find_raw_ooxml(spec)
    if raw_paths and not allow_raw_ooxml:
        raise SystemExit(
            "raw_docx_xml blocks require --allow_raw_ooxml:\n" + "\n".join(raw_paths)
        )


def write_temp_spec(spec: dict[str, Any]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    with temp:
        json.dump(spec, temp, indent=2)
    return Path(temp.name)


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def build_simple(spec_path: Path, output_path: Path) -> None:
    run([sys.executable, str(SIMPLE_RENDERER), "--input", str(spec_path), "--output", str(output_path)])


def build_branded(spec_path: Path, output_path: Path, *, embed_font_enabled: bool) -> None:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js is required for branded DOCX generation.")
    run([node, str(BRANDED_RENDERER), "--input", str(spec_path), "--output", str(output_path)])
    if embed_font_enabled:
        embed_cover_font(str(output_path), str(output_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a DOCX from a JSON spec.")
    parser.add_argument("--mode", choices=("simple", "branded"), default="branded")
    parser.add_argument("--input", required=True, help="Spec JSON path, or '-' for stdin")
    parser.add_argument("--output", required=True, help="Destination path for the generated DOCX")
    parser.add_argument(
        "--allow_raw_ooxml",
        action="store_true",
        help="Allow expert-only raw_docx_xml blocks through schema validation",
    )
    parser.add_argument(
        "--skip_embed_font",
        action="store_true",
        help="Skip the Word-safe custom font embed step for branded output",
    )
    parser.add_argument(
        "--skip_validate",
        action="store_true",
        help="Skip semantic DOCX validation after generation",
    )
    parser.add_argument(
        "--qa",
        choices=("fast", "thorough", "auto", "none"),
        default="fast",
        help=(
            "QA route after generation: fast=validate+layout lint, "
            "thorough=validate+layout lint+contact sheet, auto=contact sheet only for high-risk lint, none=skip QA"
        ),
    )
    parser.add_argument(
        "--contact_sheet_output",
        help="Optional contact-sheet PNG path for --qa thorough or high-risk --qa auto",
    )
    args = parser.parse_args()

    spec = load_json(args.input)
    validate_spec(spec, allow_raw_ooxml=args.allow_raw_ooxml)
    output_path = Path(args.output).expanduser().resolve()
    spec_path = write_temp_spec(spec)
    try:
        if args.mode == "simple":
            build_simple(spec_path, output_path)
        else:
            build_branded(spec_path, output_path, embed_font_enabled=not args.skip_embed_font)
    finally:
        spec_path.unlink(missing_ok=True)

    if not args.skip_validate and args.qa != "none":
        result = validate_docx(output_path)
        if not result["ok"]:
            raise SystemExit("Generated DOCX failed validation:\n" + "\n".join(result["errors"]))
    lint_result = None
    if args.qa in {"fast", "thorough", "auto"}:
        lint_result = lint_docx(output_path, spec)
        if not lint_result["ok"]:
            raise SystemExit("Generated DOCX failed layout lint:\n" + "\n".join(lint_result["errors"]))
        print(
            f"layout risk: {lint_result['risk']} ({', '.join(lint_result['risk_reasons'])})"
        )
    should_render_contact = args.qa == "thorough" or (
        args.qa == "auto" and lint_result is not None and lint_result["risk"] == "high"
    )
    if should_render_contact:
        contact_sheet = (
            Path(args.contact_sheet_output).expanduser().resolve()
            if args.contact_sheet_output
            else output_path.with_name(f"{output_path.stem}-contact-sheet.png")
        )
        render_contact_sheet(output_path, contact_sheet)
        print(f"contact sheet: {contact_sheet}")
    print(output_path)


if __name__ == "__main__":
    main()
