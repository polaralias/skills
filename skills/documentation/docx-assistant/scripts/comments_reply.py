#!/usr/bin/env python3
"""Add threaded replies to existing DOCX comments while preserving visible anchors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx_ooxml import (
    COMMENT_PART,
    DocxArchive,
    append_comment_extension,
    append_comment_id_mapping,
    build_comment_element,
    comment_first_para_id,
    ensure_comments_content_type,
    ensure_comments_relationship,
    insert_reply_anchor,
    qn,
    rebuild_comment_metadata_parts,
)


def add_replies(input_docx: Path, response_map: dict[str, str], output_docx: Path, *, author: str, initials: str) -> None:
    archive = DocxArchive.load(input_docx)
    if not archive.has(COMMENT_PART):
        raise SystemExit("word/comments.xml not found")

    comments_root = archive.comments_root()
    comments_extended_root = archive.comments_extended_root()
    comments_ids_root = archive.comments_ids_root()

    comment_index = {
        comment.get(qn("w", "id"), ""): comment
        for comment in comments_root.findall(f"./{qn('w', 'comment')}")
    }
    story_roots = {
        story_part: archive.read_xml(story_part)
        for story_part in archive.story_parts()
    }
    changed_story_parts: set[str] = set()

    next_comment_id = archive.next_comment_id()

    for comment_id, response in response_map.items():
        reply_text = str(response).strip()
        if not reply_text:
            continue
        parent = comment_index.get(str(comment_id))
        if parent is None:
            raise SystemExit(f"Comment {comment_id} not found")
        parent_para_id = comment_first_para_id(parent)
        if not parent_para_id:
            raise SystemExit(f"Comment {comment_id} has no paragraph id to thread replies against")

        reply_comment, reply_para_id = build_comment_element(next_comment_id, reply_text, author, initials)
        anchored = False
        for story_part, story_root in story_roots.items():
            if insert_reply_anchor(story_root, comment_id, next_comment_id):
                changed_story_parts.add(story_part)
                anchored = True
                break
        if not anchored:
            raise SystemExit(f"Comment {comment_id} has no visible anchor in the document story")
        next_comment_id += 1
        comments_root.append(reply_comment)
        append_comment_extension(comments_extended_root, reply_para_id, parent_para_id=parent_para_id, done="0")
        append_comment_id_mapping(comments_ids_root, reply_para_id)

    archive.save_comments_root(comments_root)
    archive.save_comments_extended_root(comments_extended_root)
    archive.save_comments_ids_root(comments_ids_root)
    for story_part in changed_story_parts:
        archive.set_xml(story_part, story_roots[story_part])
    rebuild_comment_metadata_parts(archive, comments_root)
    ensure_comments_relationship(archive)
    ensure_comments_content_type(archive)
    archive.write(output_docx)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append threaded replies to comments already present in a DOCX.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("responses_json", help="JSON object mapping comment ids to reply text")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    parser.add_argument("--author", default="Document reviewer", help="Display name recorded for each reply")
    parser.add_argument("--initials", default="RV", help="Initials recorded for each reply")
    args = parser.parse_args()

    response_map = json.loads(Path(args.responses_json).expanduser().resolve().read_text(encoding="utf-8"))
    if not isinstance(response_map, dict):
        raise SystemExit("responses_json must be a JSON object mapping comment ids to reply text")

    add_replies(
        Path(args.input_docx).expanduser().resolve(),
        response_map,
        Path(args.out).expanduser().resolve(),
        author=args.author,
        initials=args.initials,
    )
    print(Path(args.out).expanduser().resolve())


if __name__ == "__main__":
    main()
