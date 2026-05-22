from __future__ import annotations

import os
import sys
from pathlib import Path

from docx import Document

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = SKILL_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from build_simple_from_spec import build_document as build_simple_document
from embed_font import embed
from generate_docx import validate_spec


def test_spec_rejects_raw_ooxml_without_flag() -> None:
    spec = {
        "title": "Raw spec",
        "blocks": [{"type": "raw_docx_xml", "xml": "<w:p/>", "reason": "test"}],
    }

    try:
        validate_spec(spec, allow_raw_ooxml=False)
    except SystemExit as exc:
        assert "raw_docx_xml blocks require --allow_raw_ooxml" in str(exc)
    else:
        raise AssertionError("Expected SystemExit for raw_docx_xml without allow flag")


def test_simple_builder_creates_docx(tmp_path: Path) -> None:
    output_path = tmp_path / "simple.docx"
    spec = {
        "title": "Simple output",
        "subtitle": "Subtitle",
        "blocks": [
            {"type": "paragraph", "text": "Hello world."},
            {"type": "bullets", "items": ["One", "Two"]},
        ],
    }

    build_simple_document(spec, output_path)

    assert output_path.exists()
    document = Document(output_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Simple output" in text
    assert "Hello world." in text


def test_embed_is_noop_without_configured_font(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "output.docx"
    document = Document()
    document.add_paragraph("No custom font configured.")
    document.save(input_path)

    monkeypatch.delenv("DOCX_THEME_PRIMARY_FONT_TTF", raising=False)
    result = embed(str(input_path), str(output_path))

    assert Path(result) == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == input_path.read_bytes()
