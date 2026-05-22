#!/usr/bin/env python3
"""
Render a DOCX to per-page PNGs for visual QA.

Workflow:
1. Convert DOCX to PDF with LibreOffice.
2. Rasterize the PDF with PyMuPDF.
3. Write page-01.png, page-02.png, ... to the output directory.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import fitz
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyMuPDF is required. Install it with: python -m pip install PyMuPDF"
    ) from exc


def _find_pdf(out_dir: Path) -> Path:
    pdfs = sorted(p for p in out_dir.glob("*.pdf") if p.is_file())
    if not pdfs:
        raise FileNotFoundError("LibreOffice did not produce a PDF.")
    return pdfs[0]


def _convert_docx_to_pdf_word(input_path: Path, output_path: Path) -> Path:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise FileNotFoundError("Neither LibreOffice nor PowerShell was available.")

    input_literal = str(input_path).replace("'", "''")
    output_literal = str(output_path).replace("'", "''")
    script = """
$inputPath = '{input_path}'
$outputPath = '{output_path}'
$word = $null
$doc = $null
try {{
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($inputPath)
    $doc.ExportAsFixedFormat($outputPath, 17)
}}
finally {{
    if ($doc -ne $null) {{ $doc.Close($false) }}
    if ($word -ne $null) {{ $word.Quit() }}
}}
""".format(input_path=input_literal, output_path=output_literal)

    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not output_path.exists():
        raise RuntimeError(
            "Word PDF export failed.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return output_path


def _convert_docx_to_pdf(input_path: Path, temp_dir: Path) -> Path:
    soffice = shutil.which("soffice")
    if not soffice and sys.platform.startswith("win"):
        return _convert_docx_to_pdf_word(input_path, temp_dir / f"{input_path.stem}.pdf")

    if not soffice:
        raise FileNotFoundError(
            "No supported DOCX-to-PDF converter found. Install LibreOffice or use Windows Word."
        )

    profile_dir = temp_dir / "lo-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        soffice,
        f"-env:UserInstallation={profile_dir.as_uri()}",
        "--headless",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        str(temp_dir),
        str(input_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "LibreOffice conversion failed.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return _find_pdf(temp_dir)


def render_docx(input_path: Path, output_dir: Path, dpi: int, emit_pdf: bool) -> list[Path]:
    if not input_path.exists():
        raise FileNotFoundError(f"Source DOCX file not found: {input_path}")
    if input_path.suffix.lower() != ".docx":
        raise ValueError("Input file must be a .docx document.")

    output_dir.mkdir(parents=True, exist_ok=True)
    scale = dpi / 72.0
    written: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="docx-assistant-render-") as temp_root:
        temp_dir = Path(temp_root)
        pdf_path = _convert_docx_to_pdf(input_path, temp_dir)

        if emit_pdf:
            shutil.copy2(pdf_path, output_dir / f"{input_path.stem}.pdf")

        pdf = fitz.open(pdf_path)
        for index, page in enumerate(pdf, start=1):
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            out_path = output_dir / f"page-{index:02d}.png"
            pix.save(out_path)
            written.append(out_path)
        pdf.close()

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a DOCX to page PNGs.")
    parser.add_argument("input_docx", help="Path to the source .docx file")
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Directory to receive rendered PNG pages",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=180,
        help="Raster DPI for page images (default: 180)",
    )
    parser.add_argument(
        "--emit_pdf",
        action="store_true",
        help="Also copy the intermediate PDF to the output directory",
    )
    args = parser.parse_args()

    input_path = Path(args.input_docx).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    written = render_docx(input_path, output_dir, args.dpi, args.emit_pdf)
    print(f"Rendered {len(written)} page(s) to {output_dir}")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
