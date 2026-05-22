#!/usr/bin/env python3
"""
Copy numbering definitions from one DOCX package into another and optionally
remap selected story parts to the imported numbering ids.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import DocxArchive, merge_numbering_packages


def parse_story_parts(raw: str) -> list[str]:
    parts = [token.strip() for token in raw.split(",") if token.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("At least one story part is required")
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description="Import numbering definitions from one DOCX into another.")
    parser.add_argument("target_docx", help="Target DOCX to update")
    parser.add_argument("--source", required=True, help="Source DOCX that provides the numbering definitions")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument(
        "--story_parts",
        type=parse_story_parts,
        help="Comma-separated target story parts that should be remapped to the imported numbering ids",
    )
    parser.add_argument(
        "--all_story_parts",
        action="store_true",
        help="Remap every story part in the target DOCX to the imported numbering ids",
    )
    args = parser.parse_args()

    target_path = Path(args.target_docx).expanduser().resolve()
    source_path = Path(args.source).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()

    target_archive = DocxArchive.load(target_path)
    source_archive = DocxArchive.load(source_path)

    if args.story_parts and args.all_story_parts:
        raise SystemExit("Use either --story_parts or --all_story_parts, not both.")

    remap_story_parts = None
    if args.all_story_parts:
        remap_story_parts = target_archive.story_parts()
    elif args.story_parts:
        remap_story_parts = args.story_parts

    stats = merge_numbering_packages(
        source_archive,
        target_archive,
        remap_story_parts=remap_story_parts,
    )
    target_archive.write(output_path)
    print(output_path)
    print(stats)


if __name__ == "__main__":
    main()
