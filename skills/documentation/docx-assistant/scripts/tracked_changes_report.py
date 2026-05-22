#!/usr/bin/env python3
"""
Report tracked-change activity across a DOCX.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx_ooxml import DocxArchive, tracked_change_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Report tracked changes across DOCX story parts.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    archive = DocxArchive.load(Path(args.input_docx).expanduser().resolve())
    report = {
        "path": str(Path(args.input_docx).expanduser().resolve()),
        "story_parts": {},
        "total_changes": 0,
        "authors": set(),
        "dates": set(),
    }
    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        summary = tracked_change_summary(root)
        report["story_parts"][story_part] = summary
        report["total_changes"] += summary["counts"]["total"]
        report["authors"].update(summary["authors"])
        report["dates"].update(summary["dates"])

    report["authors"] = sorted(report["authors"])
    report["dates"] = sorted(report["dates"])

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"path: {report['path']}")
    print(f"total_changes: {report['total_changes']}")
    if report["authors"]:
        print(f"authors: {', '.join(report['authors'])}")
    for story_part, summary in report["story_parts"].items():
        if summary["counts"]["total"] == 0:
            continue
        print(f"{story_part}: {summary['counts']}")


if __name__ == "__main__":
    main()
