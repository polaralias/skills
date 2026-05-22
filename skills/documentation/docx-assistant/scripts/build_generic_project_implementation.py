#!/usr/bin/env python3
"""Small Python wrapper around the sample implementation-plan JS builder."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from embed_font import embed as embed_cover_font

ROOT = Path(__file__).resolve().parent.parent
JS_BUILDER = ROOT / "scripts" / "build_generic_project_implementation.js"
DEFAULT_OUTPUT = ROOT / "output" / "generic-project-implementation.docx"


def build_document(output_path: Path, customer: str, *, embed_font_enabled: bool = True) -> Path:
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js is required for the JS-first DOCX builder.")

    result = subprocess.run(
        [
            node,
            str(JS_BUILDER),
            "--output",
            str(output_path),
            "--customer",
            customer,
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    if result.returncode != 0:
        bootstrap_note = ""
        if "Cannot find module 'docx'" in result.stderr:
            bootstrap_note = (
                f"\nNode dependency resolution failed from skill root: {ROOT}\n"
                "Run these commands from the skill root before using the JS-first builders:\n"
                "  npm ci\n"
                "  python -m pip install PyMuPDF lxml\n"
                "Then verify with:\n"
                "  node -e \"require('docx'); console.log('docx ok')\"\n"
                "  python scripts/preflight.py\n"
                "If you launched a custom JS file outside the packaged skill, move it into "
                "`scripts/` or run it with the skill root as cwd."
            )
        raise SystemExit(
            "JS builder failed.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
            f"{bootstrap_note}"
        )
    if embed_font_enabled:
        embed_cover_font(str(output_path), str(output_path))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the sample implementation-plan document through the JS builder.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Destination DOCX file")
    parser.add_argument(
        "--customer",
        "--customer_name",
        dest="customer",
        default="Example customer",
        help="Customer name to place on the cover",
    )
    parser.add_argument(
        "--skip_embed_font",
        action="store_true",
        help="Skip the custom font embed step after the JS builder runs",
    )
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    built = build_document(output_path, args.customer, embed_font_enabled=not args.skip_embed_font)
    print(built)


if __name__ == "__main__":
    main()
