#!/usr/bin/env python3
"""Estimate likely DOCX layout trouble without doing a full visual render."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from lxml import etree

from docx_ooxml import DocxArchive, qn, paragraph_text, section_properties

WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
EMU_PER_DXA = 635
DEFAULT_CONTENT_WIDTH_DXA = 9360


def _int_attr(node: etree.Element | None, attr: str, default: int = 0) -> int:
    if node is None:
        return default
    value = node.get(qn("w", attr))
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _content_widths(root: etree.Element) -> list[int]:
    widths: list[int] = []
    for sect_pr in section_properties(root):
        page_size = sect_pr.find(f"./{qn('w', 'pgSz')}")
        margins = sect_pr.find(f"./{qn('w', 'pgMar')}")
        page_width = _int_attr(page_size, "w", 12240)
        left = _int_attr(margins, "left", 1440)
        right = _int_attr(margins, "right", 1440)
        gutter = _int_attr(margins, "gutter", 0)
        widths.append(max(1, page_width - left - right - gutter))
    return widths or [DEFAULT_CONTENT_WIDTH_DXA]


def _table_width_dxa(table: etree.Element) -> int | None:
    grid_widths = [
        _int_attr(col, "w", 0)
        for col in table.findall(f"./{qn('w', 'tblGrid')}/{qn('w', 'gridCol')}")
    ]
    grid_total = sum(grid_widths)
    if grid_total:
        return grid_total
    tbl_w = table.find(f"./{qn('w', 'tblPr')}/{qn('w', 'tblW')}")
    if tbl_w is not None and tbl_w.get(qn("w", "type")) == "dxa":
        return _int_attr(tbl_w, "w", 0)
    return None


def _drawing_width_dxa(drawing: etree.Element) -> int | None:
    extent = drawing.find(f".//{{{WP_NS}}}extent")
    if extent is None:
        return None
    cx = extent.get("cx")
    if cx is None:
        return None
    try:
        return math.ceil(int(cx) / EMU_PER_DXA)
    except ValueError:
        return None


def _spec_metrics(spec: dict[str, Any] | None) -> dict[str, int]:
    metrics = {
        "block_count": 0,
        "paragraphs": 0,
        "headings": 0,
        "bullet_items": 0,
        "tables": 0,
        "table_rows": 0,
        "callouts": 0,
        "section_banners": 0,
        "page_breaks": 0,
        "raw_ooxml": 0,
    }
    if not spec:
        return metrics
    blocks = spec.get("blocks", [])
    metrics["block_count"] = len(blocks)
    for block in blocks:
        block_type = block.get("type")
        if block_type == "paragraph":
            metrics["paragraphs"] += 1
        elif block_type == "heading":
            metrics["headings"] += 1
        elif block_type == "bullets":
            metrics["bullet_items"] += len(block.get("items", []))
        elif block_type == "table":
            metrics["tables"] += 1
            metrics["table_rows"] += len(block.get("rows", []))
        elif block_type == "callout":
            metrics["callouts"] += 1
            for child in block.get("body", []):
                if child.get("type") == "paragraph":
                    metrics["paragraphs"] += 1
                elif child.get("type") == "bullets":
                    metrics["bullet_items"] += len(child.get("items", []))
        elif block_type == "section_banner":
            metrics["section_banners"] += 1
        elif block_type == "page_break":
            metrics["page_breaks"] += 1
        elif block_type == "raw_docx_xml":
            metrics["raw_ooxml"] += 1
    return metrics


def _risk_from_metrics(doc_metrics: dict[str, int], spec_metrics: dict[str, int], warnings: list[str]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    estimated_pages = max(
        doc_metrics.get("explicit_page_breaks", 0) + 1,
        math.ceil(
            (
                spec_metrics.get("paragraphs", 0) * 0.16
                + spec_metrics.get("headings", 0) * 0.12
                + spec_metrics.get("bullet_items", 0) * 0.07
                + spec_metrics.get("table_rows", 0) * 0.12
                + spec_metrics.get("callouts", 0) * 0.28
                + spec_metrics.get("section_banners", 0) * 0.18
            )
        ),
    )
    if estimated_pages >= 4:
        reasons.append(f"estimated {estimated_pages} pages")
    if spec_metrics.get("tables", 0) >= 3:
        reasons.append("multiple tables")
    if spec_metrics.get("callouts", 0) >= 4:
        reasons.append("many callouts")
    if spec_metrics.get("section_banners", 0) >= 5:
        reasons.append("many section banners")
    if doc_metrics.get("images", 0) >= 3:
        reasons.append("multiple images")
    if spec_metrics.get("raw_ooxml", 0):
        reasons.append("raw OOXML")
    if any("comma-joined lists" in warning for warning in warnings):
        reasons.append("layout warnings")
    if reasons:
        return "high", reasons
    if estimated_pages >= 2 or spec_metrics.get("tables", 0) or spec_metrics.get("callouts", 0) >= 2:
        medium_reasons = []
        if estimated_pages >= 2:
            medium_reasons.append(f"estimated {estimated_pages} pages")
        if spec_metrics.get("tables", 0):
            medium_reasons.append("contains tables")
        if spec_metrics.get("callouts", 0) >= 2:
            medium_reasons.append("several callouts")
        return "medium", medium_reasons
    return "low", ["short/simple composition"]


def lint_docx(input_path: Path, spec: dict[str, Any] | None = None) -> dict[str, Any]:
    archive = DocxArchive.load(input_path)
    root = archive.document_root()
    content_width = min(_content_widths(root))
    errors: list[str] = []
    warnings: list[str] = []

    tables = root.findall(f".//{qn('w', 'tbl')}")
    for index, table in enumerate(tables, start=1):
        width = _table_width_dxa(table)
        if width is not None and width > content_width + 120:
            errors.append(
                f"Table {index} is wider than the usable page width ({width} dxa > {content_width} dxa)"
            )

    drawings = root.findall(f".//{qn('w', 'drawing')}")
    for index, drawing in enumerate(drawings, start=1):
        width = _drawing_width_dxa(drawing)
        if width is not None and width > content_width + 120:
            errors.append(
                f"Image/drawing {index} is wider than the usable page width ({width} dxa > {content_width} dxa)"
            )

    comma_list_candidates = 0
    for paragraph in root.findall(f".//{qn('w', 'p')}"):
        if any(ancestor.tag == qn("w", "tbl") for ancestor in paragraph.iterancestors()):
            continue
        text = paragraph_text(paragraph).strip()
        if text.count(", ") >= 4 and "\n" not in text:
            comma_list_candidates += 1
    if comma_list_candidates:
        warnings.append(
            f"{comma_list_candidates} paragraph(s) look like comma-joined lists; use real bullet blocks instead"
        )

    doc_metrics = {
        "paragraphs": len(root.findall(f".//{qn('w', 'p')}")),
        "tables": len(tables),
        "images": len(drawings),
        "explicit_page_breaks": sum(
            1
            for br in root.findall(f".//{qn('w', 'br')}")
            if br.get(qn("w", "type")) == "page"
        ),
    }
    spec_metrics = _spec_metrics(spec)
    risk, risk_reasons = _risk_from_metrics(doc_metrics, spec_metrics, warnings)

    return {
        "path": str(input_path),
        "ok": not errors,
        "risk": risk,
        "risk_reasons": risk_reasons,
        "errors": errors,
        "warnings": warnings,
        "doc_metrics": doc_metrics,
        "spec_metrics": spec_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate layout risk for a DOCX package.")
    parser.add_argument("input_docx", help="Source DOCX path")
    parser.add_argument("--spec", help="Optional source spec JSON used to refine composition scoring")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of plain text")
    args = parser.parse_args()

    spec = None
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    report = lint_docx(Path(args.input_docx).expanduser().resolve(), spec)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ok: {report['ok']}")
        print(f"risk: {report['risk']} ({', '.join(report['risk_reasons'])})")
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
