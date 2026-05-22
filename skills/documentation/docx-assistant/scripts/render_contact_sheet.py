#!/usr/bin/env python3
"""Render a DOCX to a single contact-sheet PNG for fast visual QA."""

from __future__ import annotations

import argparse
import math
import shutil
import tempfile
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from render_docx import _convert_docx_to_pdf


def render_contact_sheet(
    input_path: Path,
    output_path: Path,
    *,
    dpi: int = 90,
    columns: int = 2,
    thumb_width: int = 520,
) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"Source DOCX file not found: {input_path}")
    if input_path.suffix.lower() != ".docx":
        raise ValueError("Input file must be a .docx document.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scale = dpi / 72.0
    thumbs: list[Image.Image] = []

    with tempfile.TemporaryDirectory(prefix="docx-assistant-contact-") as temp_root:
        temp_dir = Path(temp_root)
        pdf_path = _convert_docx_to_pdf(input_path, temp_dir)
        pdf = fitz.open(pdf_path)
        try:
            for index, page in enumerate(pdf, start=1):
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ratio = thumb_width / image.width
                thumb_height = max(1, int(image.height * ratio))
                image = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (thumb_width, thumb_height + 34), "white")
                canvas.paste(image, (0, 0))
                draw = ImageDraw.Draw(canvas)
                draw.rectangle((0, thumb_height, thumb_width - 1, thumb_height + 33), fill=(245, 245, 245), outline=(205, 205, 205))
                draw.text((12, thumb_height + 9), f"Page {index}", fill=(40, 40, 40), font=ImageFont.load_default())
                thumbs.append(canvas)
        finally:
            pdf.close()

    if not thumbs:
        raise RuntimeError("No pages were rendered.")

    columns = max(1, columns)
    rows = math.ceil(len(thumbs) / columns)
    gap = 24
    cell_width = max(thumb.width for thumb in thumbs)
    cell_height = max(thumb.height for thumb in thumbs)
    sheet_width = columns * cell_width + (columns + 1) * gap
    sheet_height = rows * cell_height + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), (230, 230, 230))

    for index, thumb in enumerate(thumbs):
        row = index // columns
        column = index % columns
        x = gap + column * (cell_width + gap)
        y = gap + row * (cell_height + gap)
        sheet.paste(thumb, (x, y))

    sheet.save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a DOCX to one contact-sheet PNG.")
    parser.add_argument("input_docx", help="Path to the source .docx file")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=90, help="Raster DPI before thumbnailing")
    parser.add_argument("--columns", type=int, default=2, help="Number of contact-sheet columns")
    parser.add_argument("--thumb_width", type=int, default=520, help="Thumbnail width in pixels")
    args = parser.parse_args()

    written = render_contact_sheet(
        Path(args.input_docx).expanduser().resolve(),
        Path(args.output).expanduser().resolve(),
        dpi=args.dpi,
        columns=args.columns,
        thumb_width=args.thumb_width,
    )
    print(written)


if __name__ == "__main__":
    main()
