#!/usr/bin/env python3
"""
Unpack a DOCX into a directory and pretty-print XML parts.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import zipfile
from lxml import etree

from docx_ooxml import xml_bytes


def unpack_docx(input_docx: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_docx, "r") as archive:
        archive.extractall(output_dir)

    for xml_path in output_dir.rglob("*.xml"):
        raw_xml = xml_path.read_bytes()
        for _event, namespace in etree.iterparse(io.BytesIO(raw_xml), events=("start-ns",)):
            prefix, uri = namespace
            if prefix:
                etree.register_namespace(prefix, uri)
        root = etree.fromstring(raw_xml)
        etree.indent(root, space="  ")
        xml_path.write_bytes(xml_bytes(root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Unpack a DOCX into an editable directory.")
    parser.add_argument("input_docx", help="Source DOCX file")
    parser.add_argument("output_dir", help="Directory to write the unpacked content")
    args = parser.parse_args()

    unpack_docx(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.output_dir).expanduser().resolve(),
    )


if __name__ == "__main__":
    main()
