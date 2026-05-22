#!/usr/bin/env python3
"""Apply structured text edits to comments that already exist in a DOCX package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from lxml import etree

from docx_ooxml import COMMENT_PART, DocxArchive, build_comment_paragraph, comment_paragraph_metadata, qn, rebuild_comment_metadata_parts


def set_comment_text(comment: etree.Element, text: str) -> None:
    existing_metadata = [
        comment_paragraph_metadata(paragraph)
        for paragraph in comment.findall(f"./{qn('w', 'p')}")
    ]
    lines = text.splitlines() or [text]
    if not lines:
        lines = [""]
    for child in list(comment):
        comment.remove(child)
    fallback_formatting = {
        "paragraph_properties": existing_metadata[0].get("paragraph_properties") if existing_metadata else None,
        "run_properties": existing_metadata[0].get("run_properties") if existing_metadata else None,
    }
    for index, line in enumerate(lines):
        metadata = existing_metadata[index] if index < len(existing_metadata) else fallback_formatting
        paragraph, _ = build_comment_paragraph(
            line,
            para_id=metadata.get("para_id"),
            text_id=metadata.get("text_id"),
            para_rsid=metadata.get("para_rsid"),
            para_rsid_default=metadata.get("para_rsid_default"),
            run_rsid=metadata.get("run_rsid"),
            paragraph_properties=metadata.get("paragraph_properties"),
            run_properties=metadata.get("run_properties"),
        )
        comment.append(paragraph)


def apply_patch(input_docx: Path, patch_path: Path, output_docx: Path) -> None:
    archive = DocxArchive.load(input_docx)
    if not archive.has(COMMENT_PART):
        raise SystemExit("word/comments.xml not found")

    operations = json.loads(patch_path.read_text(encoding="utf-8"))
    if not isinstance(operations, list):
        raise SystemExit("Patch file must be a JSON list")

    comments_root = archive.read_xml(COMMENT_PART)
    comment_index = {
        comment.get(qn("w", "id"), ""): comment
        for comment in comments_root.findall(f"./{qn('w', 'comment')}")
    }

    for operation in operations:
        comment_id = str(operation.get("id", operation.get("comment_id", "")))
        mode = operation.get("op", "replace")
        text = str(operation.get("text", "")).strip()
        if comment_id not in comment_index:
            raise SystemExit(f"Comment {comment_id} not found")

        comment = comment_index[comment_id]
        existing_text = "\n".join(
            "".join(node.text or "" for node in paragraph.findall(f".//{qn('w', 't')}"))
            for paragraph in comment.findall(f"./{qn('w', 'p')}" )
        ).strip()

        if mode == "replace":
            new_text = text
        elif mode == "append":
            new_text = existing_text + ("\n" if existing_text and text else "") + text
        elif mode == "prepend":
            new_text = text + ("\n" if existing_text and text else "") + existing_text
        else:
            raise SystemExit(f"Unsupported op: {mode}")

        if "author" in operation:
            comment.set(qn("w", "author"), str(operation["author"]))
        if "initials" in operation:
            comment.set(qn("w", "initials"), str(operation["initials"]))

        set_comment_text(comment, new_text)

    archive.set_xml(COMMENT_PART, comments_root)
    rebuild_comment_metadata_parts(archive, comments_root)
    archive.write(output_docx)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a JSON patch file to comments already present in a DOCX.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("patch_json", help="JSON patch file")
    parser.add_argument("--out", required=True, help="Destination path for the updated DOCX")
    args = parser.parse_args()

    apply_patch(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.patch_json).expanduser().resolve(),
        Path(args.out).expanduser().resolve(),
    )
    print(Path(args.out).expanduser().resolve())


if __name__ == "__main__":
    main()
