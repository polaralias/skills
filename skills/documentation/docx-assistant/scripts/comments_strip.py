#!/usr/bin/env python3
"""Remove comment payloads and anchors from a DOCX package."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import (
    COMMENT_PART,
    COMMENT_EXTENDED_PART,
    COMMENT_IDS_PART,
    DocxArchive,
    remove_comments_content_type,
    remove_comments_relationship,
    strip_comment_anchors,
)


def strip_comments(input_docx: Path, output_docx: Path) -> dict[str, int]:
    archive = DocxArchive.load(input_docx)
    stats = {
        "story_parts_touched": 0,
        "range_start_removed": 0,
        "range_end_removed": 0,
        "references_removed": 0,
        "comments_part_removed": 0,
    }

    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        removed = strip_comment_anchors(root)
        if any(removed.values()):
            archive.set_xml(story_part, root)
            stats["story_parts_touched"] += 1
            stats["range_start_removed"] += removed["range_start"]
            stats["range_end_removed"] += removed["range_end"]
            stats["references_removed"] += removed["reference"]

    if archive.has(COMMENT_PART):
        archive.remove(COMMENT_PART)
        stats["comments_part_removed"] = 1
    archive.remove(COMMENT_EXTENDED_PART)
    archive.remove(COMMENT_IDS_PART)

    remove_comments_relationship(archive)
    remove_comments_content_type(archive)
    archive.write(output_docx)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete comments and their anchors from a DOCX.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    args = parser.parse_args()

    stats = strip_comments(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.out).expanduser().resolve(),
    )
    print(Path(args.out).expanduser().resolve())
    print(stats)


if __name__ == "__main__":
    main()
