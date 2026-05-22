#!/usr/bin/env python3
"""
Rewrite style ids and repair broken style-graph links in a DOCX.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import DocxArchive, rewrite_styles


def parse_style_maps(values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(f"Invalid style mapping '{value}'. Use OLD=NEW.")
        old, new = value.split("=", 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            raise argparse.ArgumentTypeError(f"Invalid style mapping '{value}'. Use OLD=NEW.")
        mapping[old] = new
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(description="Rewrite style ids and repair style graph links in a DOCX.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument(
        "--map",
        dest="style_maps",
        action="append",
        default=[],
        help="Style remap in OLD=NEW form. Can be repeated.",
    )
    parser.add_argument(
        "--drop_missing_links",
        action="store_true",
        help="Remove style graph links that point to undefined styles after remapping",
    )
    args = parser.parse_args()

    input_path = Path(args.input_docx).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    archive = DocxArchive.load(input_path)
    stats = rewrite_styles(
        archive,
        parse_style_maps(args.style_maps),
        drop_missing_graph_links=args.drop_missing_links,
    )
    archive.write(output_path)
    print(output_path)
    print(stats)


if __name__ == "__main__":
    main()
