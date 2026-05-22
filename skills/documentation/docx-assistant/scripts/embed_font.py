#!/usr/bin/env python3
"""
Embed a configured display font into a generated .docx file and normalize
the branded heading styles in the package.

Usage:
    python scripts/embed_font.py input.docx [output.docx]

If output is omitted, the input file is overwritten.

The font file is read from DOCX_THEME_PRIMARY_FONT_TTF when present. Before
packaging, the embed is rewritten to use a Word-style subset-family alias for
nameID=1 and nameID=4 while keeping the typographic family name (nameID=16)
as the configured display font name. This matches the package structure that
has proven most stable in Word for the web.

Rules (from theme-system.md):
- Register under the configured display-font name in fontTable.xml
- Obfuscate the payload into `.odttf` using a real GUID-backed `fontKey`
- Add altName directly as the configured fallback font for the heading fallback metadata
- Normalize the packaged `Title`, `Heading1`, and `Heading2` style definitions so
  the final DOCX has one canonical branded style for each heading
- Store the embedded font payload on the Word-style path `word/fonts/font1.odttf`
  and wire it through `rId1`
- Finish embedding before upload/share when Word for the web or Microsoft's online
  PDF conversion must preserve the custom font
"""

import os
import sys
import struct
import uuid
from pathlib import Path

from lxml import etree

from docx_ooxml import (
    CONTENT_TYPES_PART,
    DocxArchive,
    NS,
    new_relationships_root,
    qn,
    resolve_relationship_target,
)

FONT_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.obfuscatedFont"
FONT_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"

FONT_NAME = os.environ.get("DOCX_THEME_DISPLAY_FONT_NAME", "Aptos Serif")
FALLBACK_FONT_NAME = os.environ.get("DOCX_THEME_FALLBACK_FONT_NAME", "Georgia")
FONT_FILENAME = "font1.odttf"
LEGACY_FONT_FILENAMES = ("font1.odttf",)
REL_ID = "rId1"
WORD_SUBSET_PREFIX = "___WRD_EMBED_SUB_"
TITLE_BORDER = {"color": "FF4500", "size": "12", "space": "0"}
INVISIBLE_HEADING_BORDER = {"color": "FFFFFF", "size": "2", "space": "0"}

BRANDED_STYLES = (
    {
        "style_id": "Title",
        "type": "paragraph",
        "name": "Title",
        "link": "TitleChar",
        "based_on": "Normal",
        "next": "Normal",
        "font": FONT_NAME,
        "size": "56",
        "color": "222222",
        "before": "0",
        "after": "120",
        "border": TITLE_BORDER,
        "keep_next": False,
        "outline_level": None,
    },
    {
        "style_id": "TitleChar",
        "type": "character",
        "name": "Title Char",
        "link": "Title",
        "based_on": "DefaultParagraphFont",
        "font": FONT_NAME,
        "size": "56",
        "color": "222222",
    },
    {
        "style_id": "Heading1",
        "type": "paragraph",
        "name": "Heading 1",
        "link": "Heading1Char",
        "based_on": "Normal",
        "next": "Normal",
        "font": FONT_NAME,
        "size": "38",
        "color": "222222",
        "before": "160",
        "after": "80",
        "border": INVISIBLE_HEADING_BORDER,
        "keep_next": True,
        "outline_level": "0",
    },
    {
        "style_id": "Heading1Char",
        "type": "character",
        "name": "Heading 1 Char",
        "link": "Heading1",
        "based_on": "DefaultParagraphFont",
        "font": FONT_NAME,
        "size": "38",
        "color": "222222",
    },
    {
        "style_id": "Heading2",
        "type": "paragraph",
        "name": "Heading 2",
        "link": "Heading2Char",
        "based_on": "Normal",
        "next": "Normal",
        "font": FONT_NAME,
        "size": "30",
        "color": "222222",
        "before": "100",
        "after": "60",
        "border": INVISIBLE_HEADING_BORDER,
        "keep_next": True,
        "outline_level": "1",
    },
    {
        "style_id": "Heading2Char",
        "type": "character",
        "name": "Heading 2 Char",
        "link": "Heading2",
        "based_on": "DefaultParagraphFont",
        "font": FONT_NAME,
        "size": "30",
        "color": "222222",
    },
    {
        "style_id": "DocxKicker",
        "type": "paragraph",
        "name": "DOCX Kicker",
        "link": "DocxKickerChar",
        "based_on": "Normal",
        "next": "Normal",
        "custom_style": True,
        "font": FONT_NAME,
        "size": "28",
        "color": "3424FF",
        "before": "0",
        "after": "40",
        "border": INVISIBLE_HEADING_BORDER,
        "keep_next": True,
        "outline_level": None,
    },
    {
        "style_id": "DocxKickerChar",
        "type": "character",
        "name": "DOCX Kicker Char",
        "link": "DocxKicker",
        "based_on": "DefaultParagraphFont",
        "custom_style": True,
        "font": FONT_NAME,
        "size": "28",
        "color": "3424FF",
    },
)


def find_font_asset():
    """Locate the source font file relative to this script."""
    configured = os.environ.get("DOCX_THEME_PRIMARY_FONT_TTF")
    if not configured:
        return None
    font_path = Path(configured).expanduser().resolve()
    if not font_path.exists():
        raise FileNotFoundError(f"Configured font asset not found: {font_path}")
    return font_path


def make_font_key() -> str:
    return str(uuid.uuid4()).upper()


def obfuscate_font_bytes(font_bytes: bytes, font_key: str) -> bytes:
    guid_hex = font_key.replace("-", "")
    if len(guid_hex) != 32:
        raise ValueError(f"Invalid font key GUID: {font_key}")

    key_bytes = bytes.fromhex(guid_hex)[::-1]
    payload = bytearray(font_bytes)
    for idx in range(min(32, len(payload))):
        payload[idx] ^= key_bytes[idx % len(key_bytes)]
    return bytes(payload)


def _word_subset_family_name(font_key: str) -> str:
    numeric_suffix = int(font_key.replace("-", "")[-8:], 16) % 10000
    return f"{WORD_SUBSET_PREFIX}{numeric_suffix:04d}"


def _parse_sfnt_tables(font_bytes: bytes) -> tuple[int, list[tuple[str, bytes]]]:
    sfnt_version, num_tables, _search_range, _entry_selector, _range_shift = struct.unpack(">IHHHH", font_bytes[:12])
    tables: list[tuple[str, bytes]] = []
    offset = 12
    for _ in range(num_tables):
        tag, _checksum, table_offset, length = struct.unpack(">4sIII", font_bytes[offset:offset + 16])
        tables.append((tag.decode("ascii"), font_bytes[table_offset:table_offset + length]))
        offset += 16
    return sfnt_version, tables


def _encode_name_string(platform_id: int, text: str) -> bytes:
    if platform_id == 3:
        return text.encode("utf-16-be")
    return text.encode("latin1")


def _rewrite_name_table(name_table: bytes, subset_family_name: str) -> bytes:
    table_format, count, string_offset = struct.unpack(">HHH", name_table[:6])
    new_records: list[tuple[int, int, int, int, bytes]] = []
    for index in range(count):
        record_offset = 6 + index * 12
        platform_id, encoding_id, language_id, name_id, length, offset = struct.unpack(
            ">HHHHHH",
            name_table[record_offset:record_offset + 12],
        )
        raw = name_table[string_offset + offset:string_offset + offset + length]
        if name_id in {1, 4}:
            raw = _encode_name_string(platform_id, subset_family_name)
        new_records.append((platform_id, encoding_id, language_id, name_id, raw))

    new_string_offset = 6 + count * 12
    records_blob = bytearray()
    strings_blob = bytearray()
    for platform_id, encoding_id, language_id, name_id, raw in new_records:
        records_blob.extend(
            struct.pack(
                ">HHHHHH",
                platform_id,
                encoding_id,
                language_id,
                name_id,
                len(raw),
                len(strings_blob),
            )
        )
        strings_blob.extend(raw)

    return struct.pack(">HHH", table_format, count, new_string_offset) + bytes(records_blob) + bytes(strings_blob)


def _table_checksum(data: bytes) -> int:
    padding = (4 - (len(data) % 4)) % 4
    padded = data + (b"\0" * padding)
    total = 0
    for offset in range(0, len(padded), 4):
        total = (total + struct.unpack(">I", padded[offset:offset + 4])[0]) & 0xFFFFFFFF
    return total


def _rebuild_sfnt(sfnt_version: int, tables: list[tuple[str, bytes]]) -> bytes:
    num_tables = len(tables)
    max_power = 1 << (num_tables.bit_length() - 1)
    search_range = max_power * 16
    entry_selector = max_power.bit_length() - 1
    range_shift = (num_tables * 16) - search_range

    table_records: list[tuple[str, int, int, int, bytes]] = []
    offset = 12 + (16 * num_tables)
    for tag, data in tables:
        checksum_source = data
        if tag == "head":
            head_bytes = bytearray(data)
            head_bytes[8:12] = b"\0\0\0\0"
            checksum_source = bytes(head_bytes)
        checksum = _table_checksum(checksum_source)
        length = len(data)
        table_records.append((tag, checksum, offset, length, data))
        offset += length + ((4 - (length % 4)) % 4)

    rebuilt = bytearray(struct.pack(">IHHHH", sfnt_version, num_tables, search_range, entry_selector, range_shift))
    for tag, checksum, table_offset, length, _data in table_records:
        rebuilt.extend(struct.pack(">4sIII", tag.encode("ascii"), checksum, table_offset, length))
    for _tag, _checksum, _table_offset, _length, data in table_records:
        rebuilt.extend(data)
        rebuilt.extend(b"\0" * ((4 - (len(data) % 4)) % 4))

    head_record = next(record for record in table_records if record[0] == "head")
    total_checksum = _table_checksum(bytes(rebuilt))
    adjustment = (0xB1B0AFBA - total_checksum) & 0xFFFFFFFF
    rebuilt[head_record[2] + 8:head_record[2] + 12] = struct.pack(">I", adjustment)
    return bytes(rebuilt)


def prepare_font_bytes_for_docx(font_bytes: bytes, font_key: str) -> bytes:
    subset_family_name = _word_subset_family_name(font_key)
    sfnt_version, tables = _parse_sfnt_tables(font_bytes)
    rebuilt_tables = []
    for tag, data in tables:
        if tag == "name":
            data = _rewrite_name_table(data, subset_family_name)
        rebuilt_tables.append((tag, data))
    rebuilt_font = _rebuild_sfnt(sfnt_version, rebuilt_tables)
    return obfuscate_font_bytes(rebuilt_font, font_key)


def ensure_font_content_type(archive: DocxArchive) -> None:
    ct_root = archive.read_xml(CONTENT_TYPES_PART)
    for override in list(ct_root.findall(f"./{qn('ct', 'Override')}")):
        if "fonts/" in (override.get("PartName") or ""):
            ct_root.remove(override)

    default_odttf = None
    for default in ct_root.findall(f"./{qn('ct', 'Default')}"):
        if (default.get("Extension") or "").lower() == "odttf":
            default_odttf = default
            break

    if default_odttf is None:
        etree.SubElement(
            ct_root,
            qn("ct", "Default"),
            {
                "Extension": "odttf",
                "ContentType": FONT_CONTENT_TYPE,
            },
        )
    else:
        default_odttf.set("ContentType", FONT_CONTENT_TYPE)
    archive.set_xml(CONTENT_TYPES_PART, ct_root)


def ensure_font_relationship(archive: DocxArchive) -> None:
    rels_part = "word/_rels/fontTable.xml.rels"
    if archive.has(rels_part):
        rels_root = archive.read_xml(rels_part)
    else:
        rels_root = new_relationships_root()

    for rel in list(rels_root.findall(f"./{qn('rels', 'Relationship')}")):
        target = rel.get("Target") or ""
        if rel.get("Id") == REL_ID or target in {f"fonts/{name}" for name in LEGACY_FONT_FILENAMES}:
            rels_root.remove(rel)

    etree.SubElement(
        rels_root,
        qn("rels", "Relationship"),
        {
            "Id": REL_ID,
            "Type": FONT_REL_TYPE,
            "Target": f"fonts/{FONT_FILENAME}",
        },
    )
    archive.set_xml(rels_part, rels_root)


def ensure_font_table_entry(archive: DocxArchive, font_key: str) -> None:
    font_table_part = "word/fontTable.xml"
    if archive.has(font_table_part):
        root = archive.read_xml(font_table_part)
    else:
        root = etree.Element(
            qn("w", "fonts"),
            nsmap={"w": NS["w"], "r": NS["r"]},
        )

    font_el = None
    for font in root.findall(f"./{qn('w', 'font')}"):
        if font.get(qn("w", "name")) == FONT_NAME:
            font_el = font
            break

    if font_el is None:
        font_el = etree.SubElement(root, qn("w", "font"), {qn("w", "name"): FONT_NAME})

    for tag in ("embedRegular", "embedBold", "embedItalic", "embedBoldItalic", "altName"):
        existing = font_el.find(f"./{qn('w', tag)}")
        if existing is not None:
            font_el.remove(existing)

    etree.SubElement(
        font_el,
        qn("w", "embedRegular"),
        {
            qn("r", "id"): REL_ID,
            qn("w", "fontKey"): f"{{{font_key}}}",
        },
    )
    etree.SubElement(
        font_el,
        qn("w", "altName"),
        {
            qn("w", "val"): FALLBACK_FONT_NAME,
        },
    )
    archive.set_xml(font_table_part, root)


def cleanup_orphaned_font_parts(archive: DocxArchive) -> None:
    rels_part = "word/_rels/fontTable.xml.rels"
    owner_part = "word/fontTable.xml"
    referenced = set()
    if archive.has(rels_part):
        rels_root = archive.read_xml(rels_part)
        for rel in rels_root.findall(f"./{qn('rels', 'Relationship')}"):
            if rel.get("Type") != FONT_REL_TYPE:
                continue
            target = rel.get("Target")
            if not target:
                continue
            referenced.add(resolve_relationship_target(owner_part, target))

    for name in list(archive.entries):
        if name.startswith("word/fonts/") and name not in referenced:
            archive.remove(name)


def _remove_style_ids(root: etree.Element, style_ids: set[str]) -> None:
    for style in list(root.findall(f"./{qn('w', 'style')}")):
        if style.get(qn("w", "styleId")) in style_ids:
            root.remove(style)


def _append_run_properties(parent: etree.Element, spec: dict) -> None:
    r_pr = etree.SubElement(parent, qn("w", "rPr"))
    etree.SubElement(
        r_pr,
        qn("w", "rFonts"),
        {
            qn("w", "ascii"): spec["font"],
            qn("w", "cs"): spec["font"],
            qn("w", "eastAsia"): spec["font"],
            qn("w", "hAnsi"): spec["font"],
        },
    )
    etree.SubElement(r_pr, qn("w", "b"), {qn("w", "val"): "false"})
    etree.SubElement(r_pr, qn("w", "bCs"), {qn("w", "val"): "false"})
    etree.SubElement(r_pr, qn("w", "color"), {qn("w", "val"): spec["color"]})
    etree.SubElement(r_pr, qn("w", "sz"), {qn("w", "val"): spec["size"]})
    etree.SubElement(r_pr, qn("w", "szCs"), {qn("w", "val"): spec["size"]})


def _append_paragraph_style(root: etree.Element, spec: dict) -> None:
    attrs = {qn("w", "type"): "paragraph", qn("w", "styleId"): spec["style_id"]}
    if spec.get("custom_style"):
        attrs[qn("w", "customStyle")] = "1"
    style = etree.SubElement(
        root,
        qn("w", "style"),
        attrs,
    )
    etree.SubElement(style, qn("w", "name"), {qn("w", "val"): spec["name"]})
    etree.SubElement(style, qn("w", "basedOn"), {qn("w", "val"): spec["based_on"]})
    etree.SubElement(style, qn("w", "next"), {qn("w", "val"): spec["next"]})
    etree.SubElement(style, qn("w", "link"), {qn("w", "val"): spec["link"]})
    etree.SubElement(style, qn("w", "qFormat"))

    p_pr = etree.SubElement(style, qn("w", "pPr"))
    if spec["keep_next"]:
        etree.SubElement(p_pr, qn("w", "keepNext"))
    p_bdr = etree.SubElement(p_pr, qn("w", "pBdr"))
    etree.SubElement(
        p_bdr,
        qn("w", "bottom"),
        {
            qn("w", "val"): "single",
            qn("w", "color"): spec["border"]["color"],
            qn("w", "sz"): spec["border"]["size"],
            qn("w", "space"): spec["border"]["space"],
        },
    )
    etree.SubElement(
        p_pr,
        qn("w", "spacing"),
        {qn("w", "after"): spec["after"], qn("w", "before"): spec["before"]},
    )
    if spec["outline_level"] is not None:
        etree.SubElement(p_pr, qn("w", "outlineLvl"), {qn("w", "val"): spec["outline_level"]})

    _append_run_properties(style, spec)


def _append_character_style(root: etree.Element, spec: dict) -> None:
    attrs = {qn("w", "type"): "character", qn("w", "styleId"): spec["style_id"]}
    if spec.get("custom_style"):
        attrs[qn("w", "customStyle")] = "1"
    style = etree.SubElement(
        root,
        qn("w", "style"),
        attrs,
    )
    etree.SubElement(style, qn("w", "name"), {qn("w", "val"): spec["name"]})
    etree.SubElement(style, qn("w", "basedOn"), {qn("w", "val"): spec["based_on"]})
    etree.SubElement(style, qn("w", "link"), {qn("w", "val"): spec["link"]})
    etree.SubElement(style, qn("w", "qFormat"))
    _append_run_properties(style, spec)


def ensure_branded_heading_styles(archive: DocxArchive) -> None:
    styles_part = "word/styles.xml"
    if archive.has(styles_part):
        root = archive.read_xml(styles_part)
    else:
        root = etree.Element(
            qn("w", "styles"),
            nsmap={"w": NS["w"], "r": NS["r"]},
        )

    target_style_ids = {spec["style_id"] for spec in BRANDED_STYLES}
    _remove_style_ids(root, target_style_ids)

    for spec in BRANDED_STYLES:
        if spec["type"] == "paragraph":
            _append_paragraph_style(root, spec)
        else:
            _append_character_style(root, spec)

    archive.set_xml(styles_part, root)


def _story_part_names(archive: DocxArchive) -> list[str]:
    names: list[str] = []
    for name in archive.entries:
        if name == "word/document.xml":
            names.append(name)
            continue
        if name in {"word/footnotes.xml", "word/endnotes.xml"}:
            names.append(name)
            continue
        if name.startswith("word/header") and name.endswith(".xml"):
            names.append(name)
            continue
        if name.startswith("word/footer") and name.endswith(".xml"):
            names.append(name)
    return names


def _paragraph_text(paragraph: etree.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(f".//{qn('w', 't')}"))


def _ensure_kicker_paragraph_shape(paragraph: etree.Element) -> None:
    text = _paragraph_text(paragraph)

    p_pr = paragraph.find(f"./{qn('w', 'pPr')}")
    if p_pr is None:
        p_pr = etree.Element(qn("w", "pPr"))
        paragraph.insert(0, p_pr)

    p_style = p_pr.find(f"./{qn('w', 'pStyle')}")
    if p_style is None:
        p_style = etree.Element(qn("w", "pStyle"))
        p_pr.insert(0, p_style)
    p_style.set(qn("w", "val"), "DocxKicker")

    keep_next = p_pr.find(f"./{qn('w', 'keepNext')}")
    if keep_next is None:
        keep_next = etree.Element(qn("w", "keepNext"))
        insert_at = 1 if list(p_pr) and list(p_pr)[0] is p_style else 0
        p_pr.insert(insert_at, keep_next)
    keep_next.set(qn("w", "val"), "1")

    for child in list(p_pr):
        if child is p_style or child is keep_next:
            continue
        if child.tag == qn("w", "rPr"):
            continue
        p_pr.remove(child)

    p_pr_rpr = p_pr.find(f"./{qn('w', 'rPr')}")
    if p_pr_rpr is None:
        p_pr_rpr = etree.SubElement(p_pr, qn("w", "rPr"))
    else:
        for child in list(p_pr_rpr):
            p_pr_rpr.remove(child)

    etree.SubElement(
        p_pr_rpr,
        qn("w", "rFonts"),
        {
            qn("w", "ascii"): FONT_NAME,
            qn("w", "hAnsi"): FONT_NAME,
            qn("w", "eastAsia"): FONT_NAME,
            qn("w", "cs"): FONT_NAME,
        },
    )
    etree.SubElement(p_pr_rpr, qn("w", "color"), {qn("w", "val"): "3424FF"})
    etree.SubElement(p_pr_rpr, qn("w", "sz"), {qn("w", "val"): "28"})
    etree.SubElement(p_pr_rpr, qn("w", "szCs"), {qn("w", "val"): "28"})

    for child in list(paragraph):
        if child is p_pr:
            continue
        paragraph.remove(child)

    run = etree.SubElement(paragraph, qn("w", "r"))
    etree.SubElement(run, qn("w", "rPr"))
    text_node = etree.SubElement(run, qn("w", "t"))
    if text != text.strip():
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text


def normalize_kicker_paragraphs(archive: DocxArchive) -> None:
    for part_name in _story_part_names(archive):
        root = archive.read_xml(part_name)
        changed = False
        for paragraph in root.findall(f".//{qn('w', 'p')}"):
            p_style = paragraph.find(f"./{qn('w', 'pPr')}/{qn('w', 'pStyle')}")
            if p_style is None or p_style.get(qn("w", "val")) != "DocxKicker":
                continue
            _ensure_kicker_paragraph_shape(paragraph)
            changed = True
        if changed:
            archive.set_xml(part_name, root)


def embed(docx_in, docx_out=None):
    if docx_out is None:
        docx_out = docx_in

    font_path = find_font_asset()
    input_path = Path(docx_in).expanduser().resolve()
    output_path = Path(docx_out).expanduser().resolve()
    if font_path is None:
        if input_path != output_path:
            output_path.write_bytes(input_path.read_bytes())
        return str(output_path)

    archive = DocxArchive.load(input_path)
    font_key = make_font_key()
    ensure_branded_heading_styles(archive)
    normalize_kicker_paragraphs(archive)
    for legacy_name in LEGACY_FONT_FILENAMES:
        archive.remove(f"word/fonts/{legacy_name}")
    archive.entries[f"word/fonts/{FONT_FILENAME}"] = prepare_font_bytes_for_docx(font_path.read_bytes(), font_key)
    ensure_font_content_type(archive)
    ensure_font_relationship(archive)
    ensure_font_table_entry(archive, font_key)
    cleanup_orphaned_font_parts(archive)
    archive.write(output_path)
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/embed_font.py input.docx [output.docx]")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    print(embed(src, dst))
