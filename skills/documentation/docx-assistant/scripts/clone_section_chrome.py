#!/usr/bin/env python3
"""
Clone section headers, footers, and optional page setup from one section to others.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import DocxArchive, clone_section_chrome


def parse_sections(raw: str) -> list[int]:
    values: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        values.append(int(token))
    if not values:
        raise argparse.ArgumentTypeError("At least one target section is required")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone section chrome from one DOCX section to others.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument("--source_section", required=True, type=int, help="1-based source section index")
    parser.add_argument("--target_sections", required=True, type=parse_sections, help="Comma-separated 1-based target section indexes")
    parser.add_argument("--headers_only", action="store_true", help="Clone headers/footers only and leave page setup intact")
    parser.add_argument("--clone_break_type", action="store_true", help="Also clone the source section break type")
    parser.add_argument("--reuse_internal_targets", action="store_true", help="Reuse existing related parts instead of cloning internal header/footer assets")
    args = parser.parse_args()

    input_path = Path(args.input_docx).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    archive = DocxArchive.load(input_path)
    stats = clone_section_chrome(
        archive,
        args.source_section,
        args.target_sections,
        clone_page_setup=not args.headers_only,
        clone_break_type=args.clone_break_type,
        clone_internal_targets=not args.reuse_internal_targets,
    )
    archive.write(output_path)
    print(output_path)
    print(stats)


if __name__ == "__main__":
    main()
