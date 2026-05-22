#!/usr/bin/env python3
"""
Repair and normalize DOCX comment structures without rewriting comment text.

This utility is aimed at damaged or older DOCX files where Word reports
comment-recovery issues, missing metadata parts, or malformed comment paragraphs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import (
    COMMENT_PART,
    DocxArchive,
    rebuild_comment_metadata_parts,
    rebuild_threaded_reply_anchors,
    strip_comment_anchors,
)


def repair_comments(
    input_docx: Path,
    output_docx: Path,
    *,
    drop_orphaned_anchors: bool = False,
    rebuild_reply_anchors: bool = False,
) -> dict[str, int]:
    archive = DocxArchive.load(input_docx)
    stats = {
        "comments_present": 0,
        "story_parts_touched": 0,
        "orphaned_anchors_removed": 0,
        "reply_anchors_added": 0,
    }

    if not archive.has(COMMENT_PART):
        archive.write(output_docx)
        return stats

    comments_root = archive.comments_root()
    stats["comments_present"] = len(comments_root.findall('./{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment'))
    rebuild_comment_metadata_parts(archive, comments_root)
    if rebuild_reply_anchors:
        reply_stats = rebuild_threaded_reply_anchors(archive)
        stats["reply_anchors_added"] = reply_stats["reply_anchors_added"]
        stats["story_parts_touched"] += reply_stats["story_parts_touched"]

    if drop_orphaned_anchors:
        valid_ids = {comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id', '') for comment in comments_root.findall('./{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment')}
        for story_part in archive.story_parts():
            root = archive.read_xml(story_part)
            removed_here = 0
            # Stay conservative: if a paragraph references missing comment ids, remove that paragraph's full anchor set.
            for paragraph in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                ids = set()
                for tag in ('commentRangeStart', 'commentRangeEnd', 'commentReference'):
                    for node in paragraph.findall(f'.//{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{tag}'):
                        val = node.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                        if val:
                            ids.add(val)
                if ids and not ids.issubset(valid_ids):
                    removed = strip_comment_anchors(paragraph)
                    removed_here += sum(removed.values())
            if removed_here:
                archive.set_xml(story_part, root)
                stats["story_parts_touched"] += 1
                stats["orphaned_anchors_removed"] += removed_here

    archive.write(output_docx)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair malformed comment structures inside a DOCX package.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the repaired DOCX")
    parser.add_argument("--drop_orphaned_anchors", action="store_true", help="Remove anchors that point to missing comment ids")
    parser.add_argument("--rebuild_reply_anchors", action="store_true", help="Recreate visible reply anchors when the parent chain still exists")
    args = parser.parse_args()

    stats = repair_comments(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.out).expanduser().resolve(),
        drop_orphaned_anchors=args.drop_orphaned_anchors,
        rebuild_reply_anchors=args.rebuild_reply_anchors,
    )
    print(Path(args.out).expanduser().resolve())
    print(stats)


if __name__ == "__main__":
    main()
