#!/usr/bin/env python3
"""Resolve tracked-change markup across every story part in a DOCX package."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx_ooxml import DocxArchive, accept_tracked_changes_in_root, ensure_tracking_disabled


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve tracked changes throughout a DOCX package.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--out", required=True, help="Destination path for the rewritten DOCX")
    args = parser.parse_args()

    input_path = Path(args.input_docx).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    archive = DocxArchive.load(input_path)
    totals = {
        "story_parts_touched": 0,
        "insertions_unwrapped": 0,
        "deletions_removed": 0,
        "moves_removed": 0,
        "property_changes_removed": 0,
        "del_text_runs_removed": 0,
    }

    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        stats = accept_tracked_changes_in_root(root)
        if any(stats.values()):
            archive.set_xml(story_part, root)
            totals["story_parts_touched"] += 1
            for key in stats:
                totals[key] += stats[key]

    ensure_tracking_disabled(archive)
    archive.write(output_path)
    print(output_path)
    print(totals)


if __name__ == "__main__":
    main()
