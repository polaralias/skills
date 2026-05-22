#!/usr/bin/env python3
"""
Clean-room OOXML helpers for DOCX validation, comment workflows, numbering
repair, section chrome cloning, tracked-change cleanup, and low-level package
surgery.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import posixpath
import random
import re
import zipfile
from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16du": "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16sdtfl": "http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rels": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
}

for prefix, uri in NS.items():
    etree.register_namespace(prefix, uri)

COMMENTS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
COMMENTS_EXTENDED_REL_TYPE = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"
COMMENTS_IDS_REL_TYPE = "http://schemas.microsoft.com/office/2016/09/relationships/commentsIds"
COMMENTS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
COMMENTS_EXTENDED_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"
COMMENTS_IDS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml"
COMMENT_PART = "word/comments.xml"
COMMENT_EXTENDED_PART = "word/commentsExtended.xml"
COMMENT_IDS_PART = "word/commentsIds.xml"
DOCUMENT_RELS_PART = "word/_rels/document.xml.rels"
CONTENT_TYPES_PART = "[Content_Types].xml"
NUMBERING_PART = "word/numbering.xml"
STYLES_PART = "word/styles.xml"
SETTINGS_PART = "word/settings.xml"
HEADER_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
FOOTER_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
HEADER_FOOTER_REL_TYPES = {HEADER_REL_TYPE, FOOTER_REL_TYPE}
CONTENT_TYPE_STYLE = "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"
CONTENT_TYPE_NUMBERING = "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"


def qn(prefix: str, local: str) -> str:
    return f"{{{NS[prefix]}}}{local}"


TRACKED_CHANGE_CONTAINER_TAGS = {
    qn("w", "ins"),
    qn("w", "del"),
    qn("w", "moveFrom"),
    qn("w", "moveTo"),
}
TRACKED_CHANGE_PROPERTY_TAGS = {
    qn("w", "pPrChange"),
    qn("w", "rPrChange"),
    qn("w", "tblPrChange"),
    qn("w", "trPrChange"),
    qn("w", "tcPrChange"),
    qn("w", "sectPrChange"),
    qn("w", "numPrChange"),
    qn("w", "tblGridChange"),
}
STYLE_REFERENCE_TAGS = ("pStyle", "rStyle", "tblStyle")
STYLE_GRAPH_TAGS = ("basedOn", "next", "link", "numStyleLink", "styleLink")


def rebuild_root_with_nsmap(root: etree.Element, nsmap: dict[str | None, str]) -> etree.Element:
    new_root = etree.Element(root.tag, nsmap=nsmap)
    for attr_name, value in root.attrib.items():
        new_root.set(attr_name, value)
    new_root.text = root.text
    new_root.tail = root.tail
    for child in list(root):
        new_root.append(child)
    return new_root


def normalised_root_for_serialization(root: etree.Element) -> etree.Element:
    nsmap: dict[str | None, str] = {prefix: uri for prefix, uri in root.nsmap.items() if uri}

    if root.tag == qn("ct", "Types"):
        nsmap[None] = NS["ct"]
        nsmap.pop("ct", None)
    elif root.tag == qn("rels", "Relationships"):
        nsmap[None] = NS["rels"]
        nsmap.pop("rels", None)

    for prefix in root.get(qn("mc", "Ignorable"), "").split():
        uri = NS.get(prefix)
        if uri:
            nsmap.setdefault(prefix, uri)

    if nsmap == {prefix: uri for prefix, uri in root.nsmap.items() if uri}:
        return root

    return rebuild_root_with_nsmap(clone_element(root), nsmap)


def xml_bytes(root: etree.Element) -> bytes:
    return etree.tostring(normalised_root_for_serialization(root), encoding="utf-8", xml_declaration=True)


def clone_element(node: etree.Element) -> etree.Element:
    return etree.fromstring(etree.tostring(node, encoding="utf-8"))


def new_relationships_root() -> etree.Element:
    return etree.Element(qn("rels", "Relationships"), nsmap={None: NS["rels"]})


def part_relationship_name(part_name: str) -> str:
    directory, _, filename = part_name.rpartition("/")
    rel_dir = f"{directory}/_rels" if directory else "_rels"
    return f"{rel_dir}/{filename}.rels"


def relationship_source_part(rels_name: str) -> str | None:
    if rels_name == "_rels/.rels":
        return ""
    if "/_rels/" not in rels_name or not rels_name.endswith(".rels"):
        return None
    directory, _, tail = rels_name.partition("/_rels/")
    return f"{directory}/{tail[:-5]}"


def resolve_relationship_target(source_part: str, target: str) -> str:
    target_path = target.split("#", 1)[0]
    if not target_path:
        return ""
    if target_path.startswith("/"):
        return target_path.lstrip("/")
    base_dir = posixpath.dirname(source_part) if source_part else ""
    return posixpath.normpath(posixpath.join(base_dir, target_path))


def relative_relationship_target(source_part: str, target_part: str) -> str:
    base_dir = posixpath.dirname(source_part)
    return posixpath.relpath(target_part, base_dir or ".")


def next_relationship_id(rels_root: etree.Element) -> str:
    used_ids = {
        rel.get("Id")
        for rel in rels_root.findall(f"./{qn('rels', 'Relationship')}")
        if rel.get("Id")
    }
    next_id = 1
    while f"rId{next_id}" in used_ids:
        next_id += 1
    return f"rId{next_id}"


def relationship_by_id(rels_root: etree.Element, rel_id: str) -> etree.Element | None:
    for rel in rels_root.findall(f"./{qn('rels', 'Relationship')}"):
        if rel.get("Id") == rel_id:
            return rel
    return None


def ensure_relationships_root(archive: "DocxArchive", rels_name: str) -> etree.Element:
    if archive.has(rels_name):
        return archive.read_xml(rels_name)
    return new_relationships_root()


def build_content_type_maps(content_types_root: etree.Element) -> tuple[dict[str, str], dict[str, str]]:
    defaults: dict[str, str] = {}
    overrides: dict[str, str] = {}
    for default in content_types_root.findall(f"./{qn('ct', 'Default')}"):
        extension = (default.get("Extension") or "").lower()
        content_type = default.get("ContentType") or ""
        if extension and extension not in defaults:
            defaults[extension] = content_type
    for override in content_types_root.findall(f"./{qn('ct', 'Override')}"):
        part_name = (override.get("PartName") or "").lstrip("/")
        content_type = override.get("ContentType") or ""
        if part_name and part_name not in overrides:
            overrides[part_name] = content_type
    return defaults, overrides


def ensure_content_type_override(archive: "DocxArchive", part_name: str, content_type: str) -> None:
    root = archive.read_xml(CONTENT_TYPES_PART)
    target_part = f"/{part_name.lstrip('/')}"
    for override in root.findall(f"./{qn('ct', 'Override')}"):
        if override.get("PartName") == target_part:
            override.set("ContentType", content_type)
            archive.set_xml(CONTENT_TYPES_PART, root)
            return
    etree.SubElement(
        root,
        qn("ct", "Override"),
        {
            "PartName": target_part,
            "ContentType": content_type,
        },
    )
    archive.set_xml(CONTENT_TYPES_PART, root)


def next_similar_part_name(existing_names: Iterable[str], source_part: str) -> str:
    directory, filename = posixpath.split(source_part)
    stem, ext = posixpath.splitext(filename)
    match = re.match(r"^(.*?)(\d+)?$", stem)
    base = match.group(1) if match else stem
    index = 1
    existing = set(existing_names)
    while True:
        candidate = posixpath.join(directory, f"{base}{index}{ext}") if directory else f"{base}{index}{ext}"
        if candidate not in existing:
            return candidate
        index += 1


def body_root(document_root: etree.Element) -> etree.Element:
    body = document_root.find(f"./{qn('w', 'body')}")
    if body is None:
        raise ValueError("word/document.xml is missing w:body")
    return body


def section_properties(document_root: etree.Element) -> list[etree.Element]:
    body = body_root(document_root)
    sections: list[etree.Element] = []
    for paragraph in body.findall(f"./{qn('w', 'p')}"):
        sect = paragraph.find(f"./{qn('w', 'pPr')}/{qn('w', 'sectPr')}")
        if sect is not None:
            sections.append(sect)
    final = body.find(f"./{qn('w', 'sectPr')}")
    if final is not None:
        sections.append(final)
    return sections


def section_reference_elements(sect_pr: etree.Element) -> list[etree.Element]:
    refs = []
    refs.extend(list(sect_pr.findall(f"./{qn('w', 'headerReference')}")))
    refs.extend(list(sect_pr.findall(f"./{qn('w', 'footerReference')}")))
    return refs


def first_paragraph_id(comment: etree.Element) -> str | None:
    paragraph = comment.find(f"./{qn('w', 'p')}")
    if paragraph is None:
        return None
    return paragraph.get(qn("w14", "paraId"))


def ensure_ignorable_prefixes(root: etree.Element, *prefixes: str) -> etree.Element:
    current = root.get(qn("mc", "Ignorable"), "").split()
    for prefix in prefixes:
        if prefix not in current:
            current.append(prefix)
    if current:
        root.set(qn("mc", "Ignorable"), " ".join(current))
    return root


def story_part_names(names: Iterable[str]) -> list[str]:
    ordered = []
    for name in sorted(names):
        if name == "word/document.xml":
            ordered.insert(0, name)
        elif name.startswith("word/header") and name.endswith(".xml"):
            ordered.append(name)
        elif name.startswith("word/footer") and name.endswith(".xml"):
            ordered.append(name)
        elif name in {"word/footnotes.xml", "word/endnotes.xml"}:
            ordered.append(name)
    return ordered


def paragraph_text(paragraph: etree.Element, *, include_deleted: bool = False) -> str:
    tags = {qn("w", "t")}
    if include_deleted:
        tags.add(qn("w", "delText"))

    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag in tags and node.text:
            parts.append(node.text)
    return "".join(parts).strip()


def comment_text(comment: etree.Element) -> str:
    chunks: list[str] = []
    for paragraph in comment.findall(f"./{qn('w', 'p')}"):
        text = paragraph_text(paragraph)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


def random_word_id() -> str:
    return f"{random.randint(0, 0x7FFFFFFE):08X}"


def build_comment_paragraph(
    text: str,
    *,
    para_id: str | None = None,
    text_id: str | None = None,
    para_rsid: str | None = None,
    para_rsid_default: str | None = None,
    run_rsid: str | None = None,
    paragraph_properties: etree.Element | None = None,
    run_properties: etree.Element | None = None,
) -> tuple[etree.Element, str]:
    para_id = para_id or random_word_id()
    text_id = text_id or random_word_id()
    para_rsid = para_rsid or random_word_id()
    para_rsid_default = para_rsid_default or para_rsid
    run_rsid = run_rsid or random_word_id()
    paragraph = etree.Element(
        qn("w", "p"),
        {
            qn("w14", "paraId"): para_id,
            qn("w14", "textId"): text_id,
            qn("w", "rsidR"): para_rsid,
            qn("w", "rsidRDefault"): para_rsid_default,
        },
    )
    if paragraph_properties is None:
        paragraph_properties = etree.Element(qn("w", "pPr"))
    else:
        paragraph_properties = etree.fromstring(etree.tostring(paragraph_properties, encoding="utf-8"))
    style = paragraph_properties.find(f"./{qn('w', 'pStyle')}")
    if style is None:
        paragraph_properties.insert(0, etree.Element(qn("w", "pStyle"), {qn("w", "val"): "CommentText"}))
    paragraph.append(paragraph_properties)
    ref_run = etree.SubElement(paragraph, qn("w", "r"))
    ref_props = etree.SubElement(ref_run, qn("w", "rPr"))
    etree.SubElement(ref_props, qn("w", "rStyle"), {qn("w", "val"): "CommentReference"})
    etree.SubElement(ref_run, qn("w", "annotationRef"))
    run = etree.SubElement(paragraph, qn("w", "r"), {qn("w", "rsidR"): run_rsid})
    if run_properties is not None:
        run.append(etree.fromstring(etree.tostring(run_properties, encoding="utf-8")))
    text_node = etree.SubElement(run, qn("w", "t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    text_node.text = text
    return paragraph, para_id


def clone_paragraph_properties(paragraph: etree.Element) -> etree.Element | None:
    properties = paragraph.find(f"./{qn('w', 'pPr')}")
    if properties is None:
        return None
    return etree.fromstring(etree.tostring(properties, encoding="utf-8"))


def clone_run_properties(run: etree.Element) -> etree.Element | None:
    properties = run.find(f"./{qn('w', 'rPr')}")
    if properties is None:
        return None
    return etree.fromstring(etree.tostring(properties, encoding="utf-8"))


def comment_paragraph_metadata(paragraph: etree.Element) -> dict[str, object]:
    metadata: dict[str, object] = {}
    paragraph_properties = clone_paragraph_properties(paragraph)
    if paragraph_properties is not None:
        metadata["paragraph_properties"] = paragraph_properties
    for key, attr in (
        ("para_id", qn("w14", "paraId")),
        ("text_id", qn("w14", "textId")),
        ("para_rsid", qn("w", "rsidR")),
        ("para_rsid_default", qn("w", "rsidRDefault")),
    ):
        value = paragraph.get(attr)
        if value:
            metadata[key] = value

    for run in paragraph.findall(f"./{qn('w', 'r')}"):
        if run.find(f"./{qn('w', 'annotationRef')}") is not None:
            continue
        run_rsid = run.get(qn("w", "rsidR"))
        if run_rsid:
            metadata["run_rsid"] = run_rsid
        run_properties = clone_run_properties(run)
        if run_properties is not None:
            metadata["run_properties"] = run_properties
        break

    return metadata


def build_comment_element(comment_id: int, text: str, author: str, initials: str) -> tuple[etree.Element, str]:
    para_rsid = random_word_id()
    run_rsid = random_word_id()
    first_para_id = ""
    comment = etree.Element(
        qn("w", "comment"),
        {
            qn("w", "id"): str(comment_id),
            qn("w", "author"): author,
            qn("w", "initials"): initials,
            qn("w", "date"): datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
    )
    for line in [segment for segment in text.splitlines() if segment.strip()] or [text]:
        paragraph, para_id = build_comment_paragraph(
            line,
            para_rsid=para_rsid,
            para_rsid_default=para_rsid,
            run_rsid=run_rsid,
        )
        if not first_para_id:
            first_para_id = para_id
        comment.append(paragraph)
    return comment, first_para_id


def create_comment_reference_run(comment_id: int) -> etree.Element:
    run = etree.Element(qn("w", "r"))
    run_props = etree.SubElement(run, qn("w", "rPr"))
    etree.SubElement(run_props, qn("w", "rStyle"), {qn("w", "val"): "CommentReference"})
    etree.SubElement(run, qn("w", "commentReference"), {qn("w", "id"): str(comment_id)})
    return run


def iter_comment_anchor_ids(paragraph: etree.Element) -> set[str]:
    ids: set[str] = set()
    for tag in ("commentRangeStart", "commentRangeEnd", "commentReference"):
        for node in paragraph.findall(f".//{qn('w', tag)}"):
            value = node.get(qn("w", "id"))
            if value:
                ids.add(value)
    return ids


@dataclass
class DocxArchive:
    input_path: Path
    entries: dict[str, bytes]

    @classmethod
    def load(cls, input_path: Path) -> "DocxArchive":
        with zipfile.ZipFile(input_path, "r") as archive:
            entries = {name: archive.read(name) for name in archive.namelist()}
        return cls(input_path=input_path, entries=entries)

    def has(self, name: str) -> bool:
        return name in self.entries

    def read_xml(self, name: str) -> etree.Element:
        return etree.fromstring(self.entries[name])

    def set_xml(self, name: str, root: etree.Element) -> None:
        self.entries[name] = xml_bytes(root)

    def remove(self, name: str) -> None:
        self.entries.pop(name, None)

    def write(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(self.entries):
                archive.writestr(name, self.entries[name])

    def story_parts(self) -> list[str]:
        return story_part_names(self.entries.keys())

    def document_root(self) -> etree.Element:
        return self.read_xml("word/document.xml")

    def save_document_root(self, root: etree.Element) -> None:
        self.set_xml("word/document.xml", root)

    def content_types_root(self) -> etree.Element:
        return self.read_xml(CONTENT_TYPES_PART)

    def save_content_types_root(self, root: etree.Element) -> None:
        self.set_xml(CONTENT_TYPES_PART, root)

    def styles_root(self) -> etree.Element | None:
        if not self.has(STYLES_PART):
            return None
        return self.read_xml(STYLES_PART)

    def save_styles_root(self, root: etree.Element) -> None:
        self.set_xml(STYLES_PART, root)

    def numbering_root(self) -> etree.Element:
        if self.has(NUMBERING_PART):
            return self.read_xml(NUMBERING_PART)
        return etree.Element(qn("w", "numbering"))

    def save_numbering_root(self, root: etree.Element) -> None:
        self.set_xml(NUMBERING_PART, root)
        ensure_content_type_override(self, NUMBERING_PART, CONTENT_TYPE_NUMBERING)

    def settings_root(self) -> etree.Element | None:
        if not self.has(SETTINGS_PART):
            return None
        return self.read_xml(SETTINGS_PART)

    def save_settings_root(self, root: etree.Element) -> None:
        self.set_xml(SETTINGS_PART, root)

    def relationships_root(self, part_name: str) -> etree.Element:
        return ensure_relationships_root(self, part_relationship_name(part_name))

    def save_relationships_root(self, part_name: str, root: etree.Element) -> None:
        self.set_xml(part_relationship_name(part_name), root)

    def comments_root(self) -> etree.Element:
        if self.has(COMMENT_PART):
            root = self.read_xml(COMMENT_PART)
        else:
            root = etree.Element(qn("w", "comments"))
        return ensure_ignorable_prefixes(root, "w14")

    def save_comments_root(self, root: etree.Element) -> None:
        self.set_xml(COMMENT_PART, root)

    def next_comment_id(self) -> int:
        root = self.comments_root()
        ids = []
        for comment in root.findall(f"./{qn('w', 'comment')}"):
            value = comment.get(qn("w", "id"))
            if value and value.isdigit():
                ids.append(int(value))
        return max(ids, default=-1) + 1

    def comments_extended_root(self) -> etree.Element:
        if self.has(COMMENT_EXTENDED_PART):
            root = self.read_xml(COMMENT_EXTENDED_PART)
        else:
            root = etree.Element(qn("w15", "commentsEx"))
        return ensure_ignorable_prefixes(root, "w15")

    def save_comments_extended_root(self, root: etree.Element) -> None:
        self.set_xml(COMMENT_EXTENDED_PART, root)

    def comments_ids_root(self) -> etree.Element:
        if self.has(COMMENT_IDS_PART):
            root = self.read_xml(COMMENT_IDS_PART)
        else:
            root = etree.Element(qn("w16cid", "commentsIds"))
        return ensure_ignorable_prefixes(root, "w16cid")

    def save_comments_ids_root(self, root: etree.Element) -> None:
        self.set_xml(COMMENT_IDS_PART, root)


def defined_style_ids(styles_root: etree.Element | None) -> set[str]:
    if styles_root is None:
        return set()
    return {
        style.get(qn("w", "styleId"))
        for style in styles_root.findall(f"./{qn('w', 'style')}")
        if style.get(qn("w", "styleId"))
    }


def referenced_style_ids(root: etree.Element) -> set[str]:
    refs: set[str] = set()
    for tag in STYLE_REFERENCE_TAGS:
        for node in root.findall(f".//{qn('w', tag)}"):
            value = node.get(qn("w", "val"))
            if value:
                refs.add(value)
    return refs


def style_graph_references(styles_root: etree.Element | None) -> set[str]:
    if styles_root is None:
        return set()
    refs: set[str] = set()
    for tag in STYLE_GRAPH_TAGS:
        for node in styles_root.findall(f".//{qn('w', tag)}"):
            value = node.get(qn("w", "val"))
            if value:
                refs.add(value)
    return refs


def style_nodes_by_id(styles_root: etree.Element | None) -> dict[str, etree.Element]:
    if styles_root is None:
        return {}
    nodes: dict[str, etree.Element] = {}
    for style in styles_root.findall(f"./{qn('w', 'style')}"):
        style_id = style.get(qn("w", "styleId"))
        if style_id and style_id not in nodes:
            nodes[style_id] = style
    return nodes


def resolve_chained_mapping(mapping: dict[str, str], *, kind: str) -> dict[str, str]:
    resolved: dict[str, str] = {}

    def resolve(key: str, trail: list[str]) -> str:
        if key in resolved:
            return resolved[key]
        target = mapping.get(key)
        if target is None:
            return key
        if not target:
            raise ValueError(f"{kind} entry for {key} has an empty target")
        if key in trail:
            cycle = trail[trail.index(key):] + [key]
            raise ValueError(f"{kind} contains a cycle: {' -> '.join(cycle)}")
        final = resolve(target, trail + [key]) if target in mapping else target
        resolved[key] = final
        return final

    for key in mapping:
        resolve(key, [])
    return resolved


def remap_story_style_references(root: etree.Element, mapping: dict[str, str]) -> int:
    updated = 0
    for tag in STYLE_REFERENCE_TAGS:
        for node in root.findall(f".//{qn('w', tag)}"):
            value = node.get(qn("w", "val"))
            if value in mapping:
                node.set(qn("w", "val"), mapping[value])
                updated += 1
    return updated


def remap_style_graph_references(styles_root: etree.Element, mapping: dict[str, str]) -> int:
    updated = 0
    for tag in STYLE_GRAPH_TAGS:
        for node in styles_root.findall(f".//{qn('w', tag)}"):
            value = node.get(qn("w", "val"))
            if value in mapping:
                node.set(qn("w", "val"), mapping[value])
                updated += 1
    return updated


def drop_missing_style_graph_references(styles_root: etree.Element) -> int:
    removed = 0
    valid_ids = defined_style_ids(styles_root)
    for tag in STYLE_GRAPH_TAGS:
        for node in list(styles_root.findall(f".//{qn('w', tag)}")):
            value = node.get(qn("w", "val"))
            if value and value not in valid_ids:
                parent = node.getparent()
                if parent is not None:
                    parent.remove(node)
                    removed += 1
    return removed


def rewrite_styles(
    archive: "DocxArchive",
    style_mapping: dict[str, str] | None = None,
    *,
    drop_missing_graph_links: bool = False,
) -> dict[str, object]:
    styles_root = archive.styles_root()
    stats: dict[str, object] = {
        "styles_renamed": 0,
        "styles_removed": 0,
        "story_references_updated": 0,
        "graph_references_updated": 0,
        "graph_links_removed": 0,
        "missing_source_styles": [],
        "unresolved_targets": [],
        "effective_map": {},
    }
    if styles_root is None:
        return stats

    raw_map = {old: new for old, new in (style_mapping or {}).items() if old}
    resolved_map = resolve_chained_mapping(raw_map, kind="style mapping") if raw_map else {}

    ordered_style_ids = [
        style.get(qn("w", "styleId"))
        for style in styles_root.findall(f"./{qn('w', 'style')}")
        if style.get(qn("w", "styleId"))
    ]
    styles_by_id = style_nodes_by_id(styles_root)
    missing_source_styles = sorted(style_id for style_id in resolved_map if style_id not in styles_by_id)

    final_style_ids_by_source = {
        style_id: resolved_map.get(style_id, style_id)
        for style_id in ordered_style_ids
        if style_id in styles_by_id
    }
    owner_by_final_id: dict[str, str] = {}
    for style_id in ordered_style_ids:
        if style_id not in final_style_ids_by_source:
            continue
        final_id = final_style_ids_by_source[style_id]
        if final_id in owner_by_final_id:
            continue
        if final_id in styles_by_id and final_style_ids_by_source.get(final_id, final_id) == final_id:
            owner_by_final_id[final_id] = final_id
        else:
            owner_by_final_id[final_id] = style_id

    for style_id in ordered_style_ids:
        node = styles_by_id.get(style_id)
        if node is None:
            continue
        final_id = final_style_ids_by_source.get(style_id, style_id)
        owner_id = owner_by_final_id.get(final_id, style_id)
        if owner_id == style_id:
            if style_id != final_id:
                node.set(qn("w", "styleId"), final_id)
                stats["styles_renamed"] += 1
        else:
            styles_root.remove(node)
            stats["styles_removed"] += 1

    final_defined_ids = defined_style_ids(styles_root)
    effective_map = {
        old: target
        for old, target in resolved_map.items()
        if old != target and target in final_defined_ids
    }
    unresolved_targets = sorted({
        target
        for old, target in resolved_map.items()
        if old != target and target not in final_defined_ids
    })

    if effective_map:
        stats["graph_references_updated"] += remap_style_graph_references(styles_root, effective_map)
        for story_part in archive.story_parts():
            root = archive.read_xml(story_part)
            updated = remap_story_style_references(root, effective_map)
            if updated:
                archive.set_xml(story_part, root)
                stats["story_references_updated"] += updated

    if drop_missing_graph_links:
        stats["graph_links_removed"] += drop_missing_style_graph_references(styles_root)

    archive.save_styles_root(styles_root)
    stats["missing_source_styles"] = missing_source_styles
    stats["unresolved_targets"] = unresolved_targets
    stats["effective_map"] = effective_map
    return stats


def defined_abstract_num_ids(numbering_root: etree.Element) -> set[str]:
    return {
        node.get(qn("w", "abstractNumId"))
        for node in numbering_root.findall(f"./{qn('w', 'abstractNum')}")
        if node.get(qn("w", "abstractNumId"))
    }


def defined_num_ids(numbering_root: etree.Element) -> set[str]:
    return {
        node.get(qn("w", "numId"))
        for node in numbering_root.findall(f"./{qn('w', 'num')}")
        if node.get(qn("w", "numId"))
    }


def referenced_num_ids(root: etree.Element) -> set[str]:
    refs: set[str] = set()
    for node in root.findall(f".//{qn('w', 'numPr')}/{qn('w', 'numId')}"):
        value = node.get(qn("w", "val"))
        if value:
            refs.add(value)
    return refs


def next_abstract_num_id(numbering_root: etree.Element) -> int:
    ids = []
    for node in numbering_root.findall(f"./{qn('w', 'abstractNum')}"):
        value = node.get(qn("w", "abstractNumId"))
        if value and value.isdigit():
            ids.append(int(value))
    return max(ids, default=-1) + 1


def next_num_id(numbering_root: etree.Element) -> int:
    ids = []
    for node in numbering_root.findall(f"./{qn('w', 'num')}"):
        value = node.get(qn("w", "numId"))
        if value and value.isdigit():
            ids.append(int(value))
    return max(ids, default=0) + 1


def remap_numbering_references(root: etree.Element, mapping: dict[str, str]) -> int:
    updated = 0
    for node in root.findall(f".//{qn('w', 'numPr')}/{qn('w', 'numId')}"):
        value = node.get(qn("w", "val"))
        if value in mapping:
            node.set(qn("w", "val"), mapping[value])
            updated += 1
    return updated


def normalize_numbering_ids(archive: DocxArchive, *, drop_unused: bool = False) -> dict[str, object]:
    numbering_root = archive.numbering_root()
    abstract_map: dict[str, str] = {}
    num_map: dict[str, str] = {}
    stats = {
        "abstract_nums_renumbered": 0,
        "nums_renumbered": 0,
        "story_references_updated": 0,
        "unused_nums_removed": 0,
    }

    abstract_nodes = numbering_root.findall(f"./{qn('w', 'abstractNum')}")
    for new_id, node in enumerate(abstract_nodes):
        old_id = node.get(qn("w", "abstractNumId"))
        if old_id is None:
            continue
        new_id_str = str(new_id)
        abstract_map[old_id] = new_id_str
        if old_id != new_id_str:
            node.set(qn("w", "abstractNumId"), new_id_str)
            stats["abstract_nums_renumbered"] += 1

    num_nodes = numbering_root.findall(f"./{qn('w', 'num')}")
    next_id = 1
    for node in num_nodes:
        old_id = node.get(qn("w", "numId"))
        if old_id is None:
            continue
        new_id_str = str(next_id)
        next_id += 1
        num_map[old_id] = new_id_str
        if old_id != new_id_str:
            node.set(qn("w", "numId"), new_id_str)
            stats["nums_renumbered"] += 1
        abstract_ref = node.find(f"./{qn('w', 'abstractNumId')}")
        if abstract_ref is not None:
            old_abstract = abstract_ref.get(qn("w", "val"))
            if old_abstract in abstract_map:
                abstract_ref.set(qn("w", "val"), abstract_map[old_abstract])

    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        updated = remap_numbering_references(root, num_map)
        if updated:
            archive.set_xml(story_part, root)
            stats["story_references_updated"] += updated

    if drop_unused:
        used_num_ids = set()
        for story_part in archive.story_parts():
            used_num_ids.update(referenced_num_ids(archive.read_xml(story_part)))
        for node in list(numbering_root.findall(f"./{qn('w', 'num')}")):
            num_id = node.get(qn("w", "numId"))
            if num_id and num_id not in used_num_ids:
                numbering_root.remove(node)
                stats["unused_nums_removed"] += 1

    archive.save_numbering_root(numbering_root)
    return stats | {"num_map": num_map, "abstract_map": abstract_map}


def import_numbering_definitions(source_archive: DocxArchive, target_archive: DocxArchive) -> dict[str, dict[str, str]]:
    if not source_archive.has(NUMBERING_PART):
        return {"num_map": {}, "abstract_map": {}}

    source_root = source_archive.numbering_root()
    target_root = target_archive.numbering_root()
    abstract_map: dict[str, str] = {}
    num_map: dict[str, str] = {}

    next_abstract = next_abstract_num_id(target_root)
    for abstract_node in source_root.findall(f"./{qn('w', 'abstractNum')}"):
        old_id = abstract_node.get(qn("w", "abstractNumId"))
        if old_id is None:
            continue
        new_id = str(next_abstract)
        next_abstract += 1
        clone = clone_element(abstract_node)
        clone.set(qn("w", "abstractNumId"), new_id)
        abstract_map[old_id] = new_id
        target_root.append(clone)

    next_num = next_num_id(target_root)
    for num_node in source_root.findall(f"./{qn('w', 'num')}"):
        old_id = num_node.get(qn("w", "numId"))
        if old_id is None:
            continue
        new_id = str(next_num)
        next_num += 1
        clone = clone_element(num_node)
        clone.set(qn("w", "numId"), new_id)
        abstract_ref = clone.find(f"./{qn('w', 'abstractNumId')}")
        if abstract_ref is not None:
            old_abstract = abstract_ref.get(qn("w", "val"))
            if old_abstract in abstract_map:
                abstract_ref.set(qn("w", "val"), abstract_map[old_abstract])
        num_map[old_id] = new_id
        target_root.append(clone)

    target_archive.save_numbering_root(target_root)
    return {"num_map": num_map, "abstract_map": abstract_map}


def merge_numbering_packages(
    source_archive: "DocxArchive",
    target_archive: "DocxArchive",
    *,
    remap_story_parts: Iterable[str] | None = None,
) -> dict[str, object]:
    mapping = import_numbering_definitions(source_archive, target_archive)
    stats: dict[str, object] = {
        "imported_abstract_nums": len(mapping["abstract_map"]),
        "imported_nums": len(mapping["num_map"]),
        "story_parts_touched": 0,
        "story_references_updated": {},
        "num_map": mapping["num_map"],
        "abstract_map": mapping["abstract_map"],
    }
    if not remap_story_parts:
        return stats

    valid_story_parts = set(target_archive.story_parts())
    for story_part in remap_story_parts:
        if story_part not in valid_story_parts:
            raise ValueError(f"Story part not found in target DOCX: {story_part}")
        root = target_archive.read_xml(story_part)
        updated = remap_numbering_references(root, mapping["num_map"])
        if updated:
            target_archive.set_xml(story_part, root)
            stats["story_parts_touched"] += 1
        stats["story_references_updated"][story_part] = updated
    return stats


def tracked_change_summary(root: etree.Element) -> dict[str, object]:
    counts = {
        "insertions": len(root.findall(f".//{qn('w', 'ins')}")),
        "deletions": len(root.findall(f".//{qn('w', 'del')}")),
        "move_from": len(root.findall(f".//{qn('w', 'moveFrom')}")),
        "move_to": len(root.findall(f".//{qn('w', 'moveTo')}")),
        "property_changes": sum(len(root.findall(f".//{tag}")) for tag in TRACKED_CHANGE_PROPERTY_TAGS),
    }
    authors = sorted({
        node.get(qn("w", "author"))
        for node in root.iter()
        if node.tag in TRACKED_CHANGE_CONTAINER_TAGS | TRACKED_CHANGE_PROPERTY_TAGS and node.get(qn("w", "author"))
    })
    dates = sorted({
        node.get(qn("w", "date"))
        for node in root.iter()
        if node.tag in TRACKED_CHANGE_CONTAINER_TAGS | TRACKED_CHANGE_PROPERTY_TAGS and node.get(qn("w", "date"))
    })
    counts["total"] = sum(value for key, value in counts.items() if key != "total")
    return {"counts": counts, "authors": authors, "dates": dates}


def accept_tracked_changes_in_root(root: etree.Element) -> dict[str, int]:
    stats = {
        "insertions_unwrapped": 0,
        "deletions_removed": 0,
        "moves_removed": 0,
        "property_changes_removed": 0,
        "del_text_runs_removed": 0,
    }

    for tag in TRACKED_CHANGE_PROPERTY_TAGS:
        for node in list(root.findall(f".//{tag}")):
            parent = node.getparent()
            if parent is None:
                continue
            parent.remove(node)
            stats["property_changes_removed"] += 1

    for tag, stat_key in ((qn("w", "moveFrom"), "moves_removed"), (qn("w", "del"), "deletions_removed")):
        for node in list(root.findall(f".//{tag}")):
            parent = node.getparent()
            if parent is None:
                continue
            parent.remove(node)
            stats[stat_key] += 1

    for node in list(root.findall(f".//{qn('w', 'moveTo')}")):
        parent = node.getparent()
        if parent is None:
            continue
        insert_at = parent.index(node)
        for child in list(node):
            node.remove(child)
            parent.insert(insert_at, child)
            insert_at += 1
        parent.remove(node)
        stats["insertions_unwrapped"] += 1

    for node in list(root.findall(f".//{qn('w', 'ins')}")):
        parent = node.getparent()
        if parent is None:
            continue
        insert_at = parent.index(node)
        for child in list(node):
            node.remove(child)
            parent.insert(insert_at, child)
            insert_at += 1
        parent.remove(node)
        stats["insertions_unwrapped"] += 1

    for del_text in list(root.findall(f".//{qn('w', 'delText')}")):
        run = del_text.getparent()
        if run is None:
            continue
        parent = run.getparent()
        if parent is None:
            continue
        parent.remove(run)
        stats["del_text_runs_removed"] += 1

    return stats


def ensure_tracking_disabled(archive: DocxArchive) -> None:
    settings_root = archive.settings_root()
    if settings_root is None:
        return
    for tag in ("trackRevisions", "doNotTrackMoves", "doNotTrackFormatting"):
        node = settings_root.find(f"./{qn('w', tag)}")
        if node is not None:
            settings_root.remove(node)
    archive.save_settings_root(settings_root)

def ensure_comments_relationship(archive: DocxArchive) -> None:
    if archive.has(DOCUMENT_RELS_PART):
        rels = archive.read_xml(DOCUMENT_RELS_PART)
    else:
        rels = new_relationships_root()

    defs = [
        (COMMENTS_REL_TYPE, "comments.xml"),
        (COMMENTS_EXTENDED_REL_TYPE, "commentsExtended.xml"),
        (COMMENTS_IDS_REL_TYPE, "commentsIds.xml"),
    ]
    existing_rels = list(rels.findall(f"./{qn('rels', 'Relationship')}"))
    existing_keys = {(rel.get("Type"), rel.get("Target")) for rel in existing_rels}
    existing_ids = {rel.get("Id", "") for rel in existing_rels}
    next_id = 1

    for rel_type, target in defs:
        if (rel_type, target) in existing_keys:
            continue
        while f"rId{next_id}" in existing_ids:
            next_id += 1
        rel = etree.SubElement(
            rels,
            qn("rels", "Relationship"),
            {
                "Id": f"rId{next_id}",
                "Type": rel_type,
                "Target": target,
            },
        )
        existing_ids.add(rel.get("Id", ""))
    archive.set_xml(DOCUMENT_RELS_PART, rels)


def ensure_comments_content_type(archive: DocxArchive) -> None:
    root = archive.read_xml(CONTENT_TYPES_PART)
    defs = [
        (f"/{COMMENT_PART}", COMMENTS_CONTENT_TYPE),
        (f"/{COMMENT_EXTENDED_PART}", COMMENTS_EXTENDED_CONTENT_TYPE),
        (f"/{COMMENT_IDS_PART}", COMMENTS_IDS_CONTENT_TYPE),
    ]
    existing = {
        override.get("PartName")
        for override in root.findall(f"./{qn('ct', 'Override')}")
    }
    for part_name, content_type in defs:
        if part_name in existing:
            continue
        etree.SubElement(
            root,
            qn("ct", "Override"),
            {
                "PartName": part_name,
                "ContentType": content_type,
            },
        )
    archive.set_xml(CONTENT_TYPES_PART, root)


def remove_comments_relationship(archive: DocxArchive) -> None:
    if not archive.has(DOCUMENT_RELS_PART):
        return
    rels = archive.read_xml(DOCUMENT_RELS_PART)
    changed = False
    for rel in list(rels.findall(f"./{qn('rels', 'Relationship')}")):
        if rel.get("Type") in {COMMENTS_REL_TYPE, COMMENTS_EXTENDED_REL_TYPE, COMMENTS_IDS_REL_TYPE}:
            rels.remove(rel)
            changed = True
    if changed:
        archive.set_xml(DOCUMENT_RELS_PART, rels)


def remove_comments_content_type(archive: DocxArchive) -> None:
    root = archive.read_xml(CONTENT_TYPES_PART)
    changed = False
    for override in list(root.findall(f"./{qn('ct', 'Override')}")):
        if override.get("PartName") in {f"/{COMMENT_PART}", f"/{COMMENT_EXTENDED_PART}", f"/{COMMENT_IDS_PART}"}:
            root.remove(override)
            changed = True
    if changed:
        archive.set_xml(CONTENT_TYPES_PART, root)


def clone_part_subtree(
    archive: DocxArchive,
    source_part: str,
    *,
    clone_internal_targets: bool = True,
    clone_memo: dict[str, str] | None = None,
) -> str:
    clone_memo = clone_memo or {}
    if source_part in clone_memo:
        return clone_memo[source_part]

    new_part = next_similar_part_name(archive.entries.keys(), source_part)
    archive.entries[new_part] = archive.entries[source_part]
    clone_memo[source_part] = new_part
    content_types_root = archive.read_xml(CONTENT_TYPES_PART)
    source_override = next(
        (
            override
            for override in content_types_root.findall(f"./{qn('ct', 'Override')}")
            if override.get("PartName") == f"/{source_part}"
        ),
        None,
    )
    if source_override is not None:
        ensure_content_type_override(
            archive,
            new_part,
            source_override.get("ContentType") or "application/xml",
        )

    rels_name = part_relationship_name(source_part)
    if archive.has(rels_name):
        rels_root = archive.read_xml(rels_name)
        new_rels_root = clone_element(rels_root)
        for rel in new_rels_root.findall(f"./{qn('rels', 'Relationship')}"):
            target = rel.get("Target") or ""
            if not target or rel.get("TargetMode") == "External":
                continue
            resolved = resolve_relationship_target(source_part, target)
            if not resolved or resolved not in archive.entries:
                continue
            if clone_internal_targets and resolved.startswith(("word/media/", "word/embeddings/", "word/charts/", "word/diagrams/", "word/drawings/")):
                cloned_target = clone_part_subtree(
                    archive,
                    resolved,
                    clone_internal_targets=clone_internal_targets,
                    clone_memo=clone_memo,
                )
                rel.set("Target", relative_relationship_target(new_part, cloned_target))
        archive.set_xml(part_relationship_name(new_part), new_rels_root)

    return new_part


def section_reference_type(rel_type: str) -> str:
    if rel_type == HEADER_REL_TYPE:
        return "headerReference"
    if rel_type == FOOTER_REL_TYPE:
        return "footerReference"
    raise ValueError(f"Unsupported section relationship type: {rel_type}")


def clone_section_chrome(
    archive: DocxArchive,
    source_section_index: int,
    target_section_indexes: list[int],
    *,
    clone_page_setup: bool = True,
    clone_break_type: bool = False,
    clone_internal_targets: bool = True,
) -> dict[str, int]:
    document_root = archive.document_root()
    document_rels = archive.read_xml(DOCUMENT_RELS_PART)
    sections = section_properties(document_root)
    if source_section_index < 1 or source_section_index > len(sections):
        raise ValueError(f"Section {source_section_index} is out of range")

    source_sect = sections[source_section_index - 1]
    source_refs = list(section_reference_elements(source_sect))
    clone_memo: dict[str, str] = {}
    stats = {
        "target_sections_updated": 0,
        "header_footer_parts_cloned": 0,
        "document_relationships_added": 0,
    }
    layout_tags = {
        qn("w", "pgSz"),
        qn("w", "pgMar"),
        qn("w", "cols"),
        qn("w", "titlePg"),
        qn("w", "docGrid"),
        qn("w", "vAlign"),
        qn("w", "textDirection"),
        qn("w", "paperSrc"),
        qn("w", "pgNumType"),
        qn("w", "formProt"),
    }
    if clone_break_type:
        layout_tags.add(qn("w", "type"))

    for target_index in target_section_indexes:
        if target_index < 1 or target_index > len(sections):
            raise ValueError(f"Section {target_index} is out of range")
        if target_index == source_section_index:
            continue
        target_sect = sections[target_index - 1]
        for ref in list(section_reference_elements(target_sect)):
            target_sect.remove(ref)
        if clone_page_setup:
            for child in list(target_sect):
                if child.tag in layout_tags:
                    target_sect.remove(child)
            insert_at = 0
            for child in source_sect:
                if child.tag in layout_tags:
                    target_sect.insert(insert_at, clone_element(child))
                    insert_at += 1

        for source_ref in source_refs:
            rel_id = source_ref.get(qn("r", "id"))
            if not rel_id:
                continue
            rel = relationship_by_id(document_rels, rel_id)
            if rel is None:
                continue
            source_part = resolve_relationship_target("word/document.xml", rel.get("Target") or "")
            if not source_part or source_part not in archive.entries:
                continue
            cloned_part = clone_part_subtree(
                archive,
                source_part,
                clone_internal_targets=clone_internal_targets,
                clone_memo=clone_memo,
            )
            new_rel_id = next_relationship_id(document_rels)
            etree_rel = etree.SubElement(
                document_rels,
                qn("rels", "Relationship"),
                {
                    "Id": new_rel_id,
                    "Type": rel.get("Type") or "",
                    "Target": relative_relationship_target("word/document.xml", cloned_part),
                },
            )
            target_sect.append(
                etree.Element(
                    qn("w", section_reference_type(rel.get("Type") or "")),
                    {
                        qn("w", "type"): source_ref.get(qn("w", "type"), "default"),
                        qn("r", "id"): new_rel_id,
                    },
                )
            )
            stats["document_relationships_added"] += 1
            stats["header_footer_parts_cloned"] += 1
        stats["target_sections_updated"] += 1

    archive.save_document_root(document_root)
    archive.set_xml(DOCUMENT_RELS_PART, document_rels)
    return stats


def find_paragraph_by_text(root: etree.Element, needle: str, *, ignore_case: bool = False) -> etree.Element | None:
    candidate = needle.lower() if ignore_case else needle
    for paragraph in root.findall(f".//{qn('w', 'p')}"):
        text = paragraph_text(paragraph)
        haystack = text.lower() if ignore_case else text
        if candidate and candidate in haystack:
            return paragraph
    return None


def insert_comment_anchor(paragraph: etree.Element, comment_id: int) -> None:
    start = etree.Element(qn("w", "commentRangeStart"), {qn("w", "id"): str(comment_id)})
    end = etree.Element(qn("w", "commentRangeEnd"), {qn("w", "id"): str(comment_id)})
    insert_at = 0
    if len(paragraph) and paragraph[0].tag == qn("w", "pPr"):
        insert_at = 1
    paragraph.insert(insert_at, start)
    paragraph.append(end)
    paragraph.append(create_comment_reference_run(comment_id))


def insert_reply_anchor(root: etree.Element, parent_comment_id: int | str, reply_comment_id: int) -> bool:
    parent_id = str(parent_comment_id)
    parent_map = {child: parent for parent in root.iter() for child in parent}

    start_node = None
    end_node = None
    reference_node = None
    for node in root.iter():
        if start_node is None and node.tag == qn("w", "commentRangeStart") and node.get(qn("w", "id")) == parent_id:
            start_node = node
        elif end_node is None and node.tag == qn("w", "commentRangeEnd") and node.get(qn("w", "id")) == parent_id:
            end_node = node
        elif reference_node is None and node.tag == qn("w", "commentReference") and node.get(qn("w", "id")) == parent_id:
            reference_node = node
        if start_node is not None and end_node is not None and reference_node is not None:
            break

    if start_node is None or end_node is None:
        return False

    start_parent = parent_map.get(start_node)
    end_parent = parent_map.get(end_node)
    if start_parent is None or end_parent is None:
        return False

    start_index = list(start_parent).index(start_node) + 1
    start_parent.insert(start_index, etree.Element(qn("w", "commentRangeStart"), {qn("w", "id"): str(reply_comment_id)}))

    if reference_node is not None:
        reference_run = parent_map.get(reference_node)
        reference_parent = parent_map.get(reference_run) if reference_run is not None else None
        if reference_run is not None and reference_parent is not None and reference_run.tag == qn("w", "r"):
            reference_index = list(reference_parent).index(reference_run) + 1
            reference_parent.insert(
                reference_index,
                etree.Element(qn("w", "commentRangeEnd"), {qn("w", "id"): str(reply_comment_id)}),
            )
            reference_parent.insert(reference_index + 1, create_comment_reference_run(reply_comment_id))
            return True

    end_index = list(end_parent).index(end_node) + 1
    end_parent.insert(end_index, etree.Element(qn("w", "commentRangeEnd"), {qn("w", "id"): str(reply_comment_id)}))
    end_parent.insert(end_index + 1, create_comment_reference_run(reply_comment_id))
    return True


def strip_comment_anchors(root: etree.Element) -> dict[str, int]:
    removed = {"range_start": 0, "range_end": 0, "reference": 0}
    parent_map = {child: parent for parent in root.iter() for child in parent}
    for node in list(root.iter()):
        if node.tag == qn("w", "commentRangeStart"):
            parent_map[node].remove(node)
            removed["range_start"] += 1
        elif node.tag == qn("w", "commentRangeEnd"):
            parent_map[node].remove(node)
            removed["range_end"] += 1
        elif node.tag == qn("w", "commentReference"):
            parent = parent_map[node]
            run_parent = parent_map.get(parent)
            if run_parent is not None and parent.tag == qn("w", "r"):
                run_parent.remove(parent)
            else:
                parent.remove(node)
            removed["reference"] += 1
    return removed


def comment_id_set(root: etree.Element) -> set[str]:
    ids: set[str] = set()
    for comment in root.findall(f"./{qn('w', 'comment')}"):
        value = comment.get(qn("w", "id"))
        if value:
            ids.add(value)
    return ids




def comment_first_para_id(comment: etree.Element) -> str | None:
    paragraph = comment.find(f"./{qn('w', 'p')}")
    if paragraph is None:
        return None
    return paragraph.get(qn("w14", "paraId"))


def existing_comment_extension_map(comments_extended_root: etree.Element) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for node in comments_extended_root.findall(f"./{qn('w15', 'commentEx')}"):
        para_id = node.get(qn("w15", "paraId"))
        if not para_id:
            continue
        payload = {
            "done": node.get(qn("w15", "done"), "0"),
        }
        parent = node.get(qn("w15", "paraIdParent"))
        if parent:
            payload["paraIdParent"] = parent
        mapping[para_id] = payload
    return mapping


def existing_comment_id_map(comments_ids_root: etree.Element) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for node in comments_ids_root.findall(f"./{qn('w16cid', 'commentId')}"):
        para_id = node.get(qn("w16cid", "paraId"))
        durable_id = node.get(qn("w16cid", "durableId"))
        if para_id and durable_id:
            mapping[para_id] = durable_id
    return mapping


def append_comment_extension(comments_extended_root: etree.Element, para_id: str, *, parent_para_id: str | None = None, done: str = "0") -> None:
    attrs = {
        qn("w15", "paraId"): para_id,
        qn("w15", "done"): done,
    }
    if parent_para_id:
        attrs[qn("w15", "paraIdParent")] = parent_para_id
    etree.SubElement(comments_extended_root, qn("w15", "commentEx"), attrs)


def append_comment_id_mapping(comments_ids_root: etree.Element, para_id: str, durable_id: str | None = None) -> str:
    durable_id = durable_id or random_word_id()
    etree.SubElement(
        comments_ids_root,
        qn("w16cid", "commentId"),
        {
            qn("w16cid", "paraId"): para_id,
            qn("w16cid", "durableId"): durable_id,
        },
    )
    return durable_id


def ensure_comment_reference_paragraph(paragraph: etree.Element) -> None:
    runs = paragraph.findall(f"./{qn('w', 'r')}")
    reference_run = next((run for run in runs if run.find(f"./{qn('w', 'annotationRef')}") is not None), None)
    if reference_run is None:
        paragraph.insert(0, create_comment_reference_run(0))
        reference_run = paragraph.find(f"./{qn('w', 'r')}")
        comment_ref = reference_run.find(f"./{qn('w', 'commentReference')}")
        if comment_ref is not None:
            reference_run.remove(comment_ref)
            etree.SubElement(reference_run, qn("w", "annotationRef"))
    run_props = reference_run.find(f"./{qn('w', 'rPr')}")
    if run_props is None:
        run_props = etree.SubElement(reference_run, qn("w", "rPr"))
    style = run_props.find(f"./{qn('w', 'rStyle')}")
    if style is None:
        style = etree.SubElement(run_props, qn("w", "rStyle"))
    style.set(qn("w", "val"), "CommentReference")


def normalise_comment_paragraph(paragraph: etree.Element, *, used_para_ids: set[str] | None = None, used_text_ids: set[str] | None = None) -> str:
    para_id = paragraph.get(qn("w14", "paraId"))
    while not para_id or (used_para_ids is not None and para_id in used_para_ids):
        para_id = random_word_id()
    paragraph.set(qn("w14", "paraId"), para_id)
    if used_para_ids is not None:
        used_para_ids.add(para_id)

    text_id = paragraph.get(qn("w14", "textId"))
    while not text_id or (used_text_ids is not None and text_id in used_text_ids):
        text_id = random_word_id()
    paragraph.set(qn("w14", "textId"), text_id)
    if used_text_ids is not None:
        used_text_ids.add(text_id)

    if not paragraph.get(qn("w", "rsidR")):
        paragraph.set(qn("w", "rsidR"), random_word_id())
    if not paragraph.get(qn("w", "rsidRDefault")):
        paragraph.set(qn("w", "rsidRDefault"), paragraph.get(qn("w", "rsidR"), random_word_id()))
    ensure_comment_reference_paragraph(paragraph)

    content_run = None
    for run in paragraph.findall(f"./{qn('w', 'r')}"):
        if run.find(f"./{qn('w', 'annotationRef')}") is not None:
            continue
        if not run.get(qn("w", "rsidR")):
            run.set(qn("w", "rsidR"), random_word_id())
        content_run = run
        break
    if content_run is None:
        content_run = etree.SubElement(paragraph, qn("w", "r"), {qn("w", "rsidR"): random_word_id()})
        etree.SubElement(content_run, qn("w", "t")).text = ""

    return para_id


def rebuild_comment_metadata_parts(archive: DocxArchive, comments_root: etree.Element) -> None:
    existing_extensions = existing_comment_extension_map(archive.comments_extended_root())
    existing_ids = existing_comment_id_map(archive.comments_ids_root())

    comments_extended_root = archive.comments_extended_root()
    for child in list(comments_extended_root):
        comments_extended_root.remove(child)
    comments_ids_root = archive.comments_ids_root()
    for child in list(comments_ids_root):
        comments_ids_root.remove(child)

    para_ids_seen: set[str] = set()
    text_ids_seen: set[str] = set()
    for comment in comments_root.findall(f"./{qn('w', 'comment')}"):
        first_para_id = None
        for paragraph in comment.findall(f"./{qn('w', 'p')}"):
            para_id = normalise_comment_paragraph(paragraph, used_para_ids=para_ids_seen, used_text_ids=text_ids_seen)
            if not first_para_id:
                first_para_id = para_id
        if not first_para_id:
            paragraph, first_para_id = build_comment_paragraph(
                comment_text(comment) or "Reply",
                para_rsid=random_word_id(),
                para_rsid_default=random_word_id(),
                run_rsid=random_word_id(),
            )
            comment.append(paragraph)
        ext = existing_extensions.get(first_para_id or "", {})
        append_comment_extension(
            comments_extended_root,
            first_para_id or "",
            parent_para_id=ext.get("paraIdParent"),
            done=ext.get("done", "0"),
        )
        append_comment_id_mapping(comments_ids_root, first_para_id or "", existing_ids.get(first_para_id or ""))

    archive.save_comments_extended_root(comments_extended_root)
    archive.save_comments_ids_root(comments_ids_root)
    archive.save_comments_root(comments_root)
    ensure_comments_relationship(archive)
    ensure_comments_content_type(archive)


def threaded_reply_parent_map(archive: DocxArchive) -> dict[str, str]:
    mapping: dict[str, str] = {}
    comments_root = archive.comments_root()
    para_to_comment_id = {}
    for comment in comments_root.findall(f"./{qn('w', 'comment')}"):
        comment_id = comment.get(qn("w", "id"))
        para_id = first_paragraph_id(comment)
        if comment_id and para_id:
            para_to_comment_id[para_id] = comment_id

    comments_extended_root = archive.comments_extended_root()
    for node in comments_extended_root.findall(f"./{qn('w15', 'commentEx')}"):
        para_id = node.get(qn("w15", "paraId"))
        parent_para_id = node.get(qn("w15", "paraIdParent"))
        if not para_id or not parent_para_id:
            continue
        child_comment_id = para_to_comment_id.get(para_id)
        parent_comment_id = para_to_comment_id.get(parent_para_id)
        if child_comment_id and parent_comment_id:
            mapping[child_comment_id] = parent_comment_id
    return mapping


def anchored_comment_ids(root: etree.Element) -> set[str]:
    ids: set[str] = set()
    for paragraph in root.findall(f".//{qn('w', 'p')}"):
        ids.update(iter_comment_anchor_ids(paragraph))
    return ids


def rebuild_threaded_reply_anchors(archive: DocxArchive) -> dict[str, int]:
    comments_root = archive.comments_root()
    comment_ids = comment_id_set(comments_root)
    if not comment_ids:
        return {"reply_anchors_added": 0, "story_parts_touched": 0}

    reply_parent = threaded_reply_parent_map(archive)
    anchored: set[str] = set()
    story_roots: dict[str, etree.Element] = {}
    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        story_roots[story_part] = root
        anchored.update(anchored_comment_ids(root))

    stats = {"reply_anchors_added": 0, "story_parts_touched": 0}
    touched_parts: set[str] = set()
    for reply_id, parent_id in reply_parent.items():
        if reply_id in anchored:
            continue
        for story_part, root in story_roots.items():
            if insert_reply_anchor(root, parent_id, int(reply_id)):
                anchored.add(reply_id)
                touched_parts.add(story_part)
                stats["reply_anchors_added"] += 1
                break

    for story_part in touched_parts:
        archive.set_xml(story_part, story_roots[story_part])
    stats["story_parts_touched"] = len(touched_parts)
    return stats
