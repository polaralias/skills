#!/usr/bin/env python3
"""Read DOCX comments and export them with lightweight anchor context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx_ooxml import COMMENT_PART, DocxArchive, comment_text, iter_comment_anchor_ids, paragraph_text, qn


def extract_comments(path: Path) -> dict:
    archive = DocxArchive.load(path)
    comments: dict[str, dict] = {}
    anchors: dict[str, list[dict]] = {}

    if archive.has(COMMENT_PART):
        root = archive.read_xml(COMMENT_PART)
        for comment in root.findall(f"./{qn('w', 'comment')}"):
            comment_id = comment.get(qn("w", "id"), "")
            comments[comment_id] = {
                "id": comment_id,
                "author": comment.get(qn("w", "author"), ""),
                "initials": comment.get(qn("w", "initials"), ""),
                "date": comment.get(qn("w", "date"), ""),
                "text": comment_text(comment),
            }
            anchors[comment_id] = []

    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        for index, paragraph in enumerate(root.findall(f".//{qn('w', 'p')}"), start=1):
            text = paragraph_text(paragraph)
            if not text:
                continue
            for comment_id in iter_comment_anchor_ids(paragraph):
                anchors.setdefault(comment_id, []).append(
                    {
                        "story_part": story_part,
                        "paragraph_index": index,
                        "snippet": text[:220],
                    }
                )

    ordered = []
    for comment_id in sorted(comments, key=lambda value: int(value) if value.isdigit() else value):
        ordered.append({**comments[comment_id], "anchors": anchors.get(comment_id, [])})

    return {
        "path": str(path),
        "comment_count": len(ordered),
        "comments": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export comments from a DOCX package into JSON.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination JSON path")
    args = parser.parse_args()

    report = extract_comments(Path(args.input_docx).expanduser().resolve())
    output_path = Path(args.out).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
