#!/usr/bin/env python3
"""Normalize numbering ids in a DOCX and optionally remove unused numbering instances."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import DocxArchive, normalize_numbering_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize numbering.xml ids and story references in a DOCX package.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument("--drop_unused", action="store_true", help="Remove numbering instances that are no longer referenced")
    args = parser.parse_args()

    input_path = Path(args.input_docx).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    archive = DocxArchive.load(input_path)
    stats = normalize_numbering_ids(archive, drop_unused=args.drop_unused)
    archive.write(output_path)
    print(output_path)
    print(stats)


if __name__ == "__main__":
    main()
