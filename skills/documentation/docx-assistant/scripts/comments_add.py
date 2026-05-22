#!/usr/bin/env python3
"""
Add comments to paragraphs matched by substring.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import (
    DocxArchive,
    append_comment_extension,
    append_comment_id_mapping,
    build_comment_element,
    ensure_comments_content_type,
    ensure_comments_relationship,
    find_paragraph_by_text,
    insert_comment_anchor,
)


def add_comments(input_docx: Path, output_docx: Path, additions: list[tuple[str, str]], *, author: str, initials: str, ignore_case: bool) -> None:
    archive = DocxArchive.load(input_docx)
    comments_root = archive.comments_root()
    comments_extended_root = archive.comments_extended_root()
    comments_ids_root = archive.comments_ids_root()
    unmatched: list[str] = []

    for needle, text in additions:
        matched_paragraph = None
        matched_story_part = None
        matched_root = None
        for story_part in archive.story_parts():
            root = archive.read_xml(story_part)
            paragraph = find_paragraph_by_text(root, needle, ignore_case=ignore_case)
            if paragraph is not None:
                matched_paragraph = paragraph
                matched_story_part = story_part
                matched_root = root
                break

        if matched_paragraph is None or matched_story_part is None or matched_root is None:
            unmatched.append(needle)
            continue

        comment_id = archive.next_comment_id()
        comment_element, para_id = build_comment_element(comment_id, text, author, initials)
        comments_root.append(comment_element)
        append_comment_extension(comments_extended_root, para_id)
        append_comment_id_mapping(comments_ids_root, para_id)
        insert_comment_anchor(matched_paragraph, comment_id)
        archive.save_comments_root(comments_root)
        archive.save_comments_extended_root(comments_extended_root)
        archive.save_comments_ids_root(comments_ids_root)
        archive.set_xml(matched_story_part, matched_root)

    if unmatched:
        raise SystemExit(f"Unmatched comment targets: {', '.join(unmatched)}")

    ensure_comments_relationship(archive)
    ensure_comments_content_type(archive)
    archive.write(output_docx)


def parse_addition(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("Each --add value must be in the form needle=comment text")
    needle, comment = raw.split("=", 1)
    needle = needle.strip()
    comment = comment.strip()
    if not needle or not comment:
        raise argparse.ArgumentTypeError("Both needle and comment text are required")
    return needle, comment


def main() -> None:
    parser = argparse.ArgumentParser(description="Add comments to DOCX paragraphs by substring match.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument("--add", action="append", type=parse_addition, required=True, help="needle=comment text")
    parser.add_argument("--author", default="Document reviewer", help="Comment author name")
    parser.add_argument("--initials", default="RV", help="Initials recorded for each comment")
    parser.add_argument("--ignore_case", action="store_true", help="Match target text case-insensitively")
    args = parser.parse_args()

    add_comments(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.out).expanduser().resolve(),
        args.add,
        author=args.author,
        initials=args.initials,
        ignore_case=args.ignore_case,
    )
    print(Path(args.out).expanduser().resolve())


if __name__ == "__main__":
    main()
