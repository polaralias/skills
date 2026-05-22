#!/usr/bin/env python3
"""
Pack an unpacked DOCX directory back into a .docx file.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

from validate_docx import validate_docx


def pack_docx(input_dir: Path, output_docx: Path, *, validate: bool = True) -> None:
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(input_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(input_dir).as_posix())

    if validate:
        report = validate_docx(output_docx)
        if not report["ok"]:
            joined = "\n".join(report["errors"])
            raise SystemExit(f"Packed DOCX failed validation:\n{joined}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pack an unpacked DOCX directory.")
    parser.add_argument("input_dir", help="Unpacked DOCX directory")
    parser.add_argument("output_docx", help="Destination DOCX file")
    parser.add_argument("--validate", choices=["true", "false"], default="true", help="Validate after packing")
    args = parser.parse_args()

    pack_docx(
        Path(args.input_dir).expanduser().resolve(),
        Path(args.output_docx).expanduser().resolve(),
        validate=args.validate == "true",
    )


if __name__ == "__main__":
    main()
