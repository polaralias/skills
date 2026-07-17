#!/usr/bin/env python3
"""
Structural and semantic validation for DOCX files, with checks for styles,
numbering, tracked changes, comments, field markup, relationships, and
section/header/footer safety.
"""

from __future__ import annotations

import argparse
import json
import posixpath
from pathlib import Path
from lxml import etree

from docx_ooxml import (
    COMMENT_PART,
    COMMENT_EXTENDED_PART,
    COMMENT_IDS_PART,
    COMMENTS_CONTENT_TYPE,
    COMMENTS_EXTENDED_CONTENT_TYPE,
    COMMENTS_IDS_CONTENT_TYPE,
    COMMENTS_REL_TYPE,
    COMMENTS_EXTENDED_REL_TYPE,
    COMMENTS_IDS_REL_TYPE,
    CONTENT_TYPES_PART,
    DocxArchive,
    NUMBERING_PART,
    NS,
    SETTINGS_PART,
    STYLES_PART,
    comment_id_set,
    defined_abstract_num_ids,
    defined_num_ids,
    defined_style_ids,
    iter_comment_anchor_ids,
    relationship_by_id,
    qn,
    referenced_num_ids,
    referenced_style_ids,
    section_properties,
    style_graph_references,
    threaded_reply_parent_map,
    tracked_change_summary,
)


REL_NS = f"{{{NS['r']}}}"
KNOWN_BUILTIN_STYLE_IDS = {
    "Normal",
    "DefaultParagraphFont",
    "CommentReference",
    "CommentText",
    "Header",
    "Footer",
    "TableNormal",
    "NoList",
    "Hyperlink",
}


def root_start_tag(raw_xml: bytes) -> bytes:
    declaration_end = raw_xml.find(b"?>")
    start = raw_xml.find(b"<", declaration_end + 2 if declaration_end >= 0 else 0)
    end = raw_xml.find(b">", start)
    if start < 0 or end <= start:
        return raw_xml
    return raw_xml[start:end]


def has_xml_declaration(raw_xml: bytes) -> bool:
    return raw_xml.lstrip().startswith(b"<?xml")


def comment_paragraph_structure_warnings(
    comment_id: str,
    paragraph_index: int,
    paragraph,
    *,
    require_annotation_reference: bool,
) -> list[str]:
    warnings: list[str] = []

    para_id = paragraph.get(qn("w14", "paraId"))
    text_id = paragraph.get(qn("w14", "textId"))
    para_rsid = paragraph.get(qn("w", "rsidR"))
    para_rsid_default = paragraph.get(qn("w", "rsidRDefault"))

    if not para_id:
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing w14:paraId")
    if not text_id:
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing w14:textId")
    if not para_rsid:
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing w:rsidR")
    if not para_rsid_default:
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing w:rsidRDefault")

    runs = paragraph.findall(f"./{qn('w', 'r')}")
    reference_run = next((run for run in runs if run.find(f"./{qn('w', 'annotationRef')}") is not None), None)
    if reference_run is None and require_annotation_reference:
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing the annotation reference run")
    elif reference_run is not None:
        style = reference_run.find(f"./{qn('w', 'rPr')}/{qn('w', 'rStyle')}")
        if style is None or style.get(qn("w", "val")) != "CommentReference":
            warnings.append(
                f"Comment {comment_id} paragraph {paragraph_index} is missing the CommentReference style on the annotation run"
            )

    content_run = next((run for run in runs if run.find(f"./{qn('w', 'annotationRef')}") is None), None)
    if content_run is not None and not content_run.get(qn("w", "rsidR")):
        warnings.append(f"Comment {comment_id} paragraph {paragraph_index} is missing w:rsidR on the text run")

    return warnings


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


def relationship_attr_values(root: etree.Element) -> set[str]:
    values: set[str] = set()
    for node in root.iter():
        for attr_name, value in node.attrib.items():
            if attr_name.startswith(REL_NS) and value:
                values.add(value)
    return values


def build_content_type_maps(content_types_root: etree.Element) -> tuple[dict[str, str], dict[str, str], list[str]]:
    defaults: dict[str, str] = {}
    overrides: dict[str, str] = {}
    errors: list[str] = []

    for default in content_types_root.findall(f"./{qn('ct', 'Default')}"):
        extension = (default.get("Extension") or "").lower()
        content_type = default.get("ContentType") or ""
        if not extension:
            errors.append("[Content_Types].xml contains a Default entry without an Extension")
            continue
        if extension in defaults:
            errors.append(f"[Content_Types].xml contains duplicate Default entries for .{extension}")
            continue
        defaults[extension] = content_type

    for override in content_types_root.findall(f"./{qn('ct', 'Override')}"):
        part_name = (override.get("PartName") or "").lstrip("/")
        content_type = override.get("ContentType") or ""
        if not part_name:
            errors.append("[Content_Types].xml contains an Override entry without a PartName")
            continue
        if part_name in overrides:
            errors.append(f"[Content_Types].xml contains duplicate Override entries for /{part_name}")
            continue
        overrides[part_name] = content_type

    return defaults, overrides, errors


def part_has_content_type(part_name: str, *, defaults: dict[str, str], overrides: dict[str, str]) -> bool:
    if part_name in overrides:
        return True
    _, _, extension = part_name.rpartition(".")
    return bool(extension and extension.lower() in defaults)


def validate_story_part_fields(part_name: str, root: etree.Element) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field_index, fld_simple in enumerate(root.findall(f".//{qn('w', 'fldSimple')}"), start=1):
        if fld_simple.find(f".//{qn('w', 'fldChar')}") is not None:
            errors.append(
                f"{part_name} contains a w:fldSimple field #{field_index} with nested w:fldChar markup; "
                "use simple or complex field syntax, not both"
            )

    complex_fields: list[dict[str, bool]] = []
    for node in root.iter():
        if node.tag != qn("w", "fldChar"):
            continue
        field_type = node.get(qn("w", "fldCharType")) or node.get("fldCharType") or ""
        if field_type == "begin":
            complex_fields.append({"separate_seen": False})
        elif field_type == "separate":
            if not complex_fields:
                errors.append(f"{part_name} contains w:fldCharType=\"separate\" without a matching begin")
            elif complex_fields[-1]["separate_seen"]:
                errors.append(f"{part_name} contains a complex field with multiple separate markers")
            else:
                complex_fields[-1]["separate_seen"] = True
        elif field_type == "end":
            if not complex_fields:
                errors.append(f"{part_name} contains w:fldCharType=\"end\" without a matching begin")
            else:
                field_state = complex_fields.pop()
                if not field_state["separate_seen"]:
                    warnings.append(
                        f"{part_name} contains a complex field without w:fldCharType=\"separate\"; "
                        "Word may still open it, but the field result markup is incomplete"
                    )
        elif field_type:
            warnings.append(f"{part_name} contains w:fldChar with unexpected fldCharType=\"{field_type}\"")
        else:
            warnings.append(f"{part_name} contains w:fldChar without a fldCharType")

    if complex_fields:
        errors.append(f"{part_name} contains {len(complex_fields)} unterminated complex field(s)")

    return errors, warnings


def validate_docx(path: Path) -> dict:
    archive = DocxArchive.load(path)
    errors: list[str] = []
    warnings: list[str] = []
    document_part = archive.main_document_part()
    document_rels_part = archive.main_document_rels_part()

    required = ["_rels/.rels", CONTENT_TYPES_PART, document_part]
    for name in required:
        if not archive.has(name):
            errors.append(f"Missing required part: {name}")

    if archive.has(CONTENT_TYPES_PART) and b"<ct:Types" in archive.entries[CONTENT_TYPES_PART]:
        errors.append("[Content_Types].xml must use the default package namespace, not a ct: prefix")
    if archive.has(document_rels_part) and b"<rels:Relationships" in archive.entries[document_rels_part]:
        errors.append(f"{document_rels_part} must use the default package namespace, not a rels: prefix")

    for name, raw_xml in archive.entries.items():
        if name.endswith(".xml") and not has_xml_declaration(raw_xml):
            warnings.append(f"{name} is missing an XML declaration")

    content_types_root = archive.read_xml(CONTENT_TYPES_PART) if archive.has(CONTENT_TYPES_PART) else None
    defaults: dict[str, str] = {}
    overrides: dict[str, str] = {}
    if content_types_root is not None:
        defaults, overrides, content_type_errors = build_content_type_maps(content_types_root)
        errors.extend(content_type_errors)
        for name in sorted(archive.entries):
            if name == CONTENT_TYPES_PART or name.endswith("/"):
                continue
            if not part_has_content_type(name, defaults=defaults, overrides=overrides):
                errors.append(f"{name} is not declared in [Content_Types].xml")

    styles_root = archive.read_xml(STYLES_PART) if archive.has(STYLES_PART) else None
    style_ids = defined_style_ids(styles_root) if styles_root is not None else set()
    if styles_root is not None:
        missing_style_links = sorted(style_graph_references(styles_root) - style_ids - KNOWN_BUILTIN_STYLE_IDS)
        if missing_style_links:
            warnings.append(
                f"{STYLES_PART} contains style graph references to undefined style id(s): {', '.join(missing_style_links)}"
            )

    numbering_root = archive.read_xml(NUMBERING_PART) if archive.has(NUMBERING_PART) else None
    if numbering_root is not None:
        abstract_ids = defined_abstract_num_ids(numbering_root)
        num_ids = defined_num_ids(numbering_root)
        if len(abstract_ids) != len(numbering_root.findall(f"./{qn('w', 'abstractNum')}")):
            errors.append(f"{NUMBERING_PART} contains duplicate abstractNumId values")
        if len(num_ids) != len(numbering_root.findall(f"./{qn('w', 'num')}")):
            errors.append(f"{NUMBERING_PART} contains duplicate numId values")
        for num in numbering_root.findall(f"./{qn('w', 'num')}"):
            num_id = num.get(qn("w", "numId")) or "<missing>"
            abstract_ref = num.find(f"./{qn('w', 'abstractNumId')}")
            if abstract_ref is None:
                errors.append(f"{NUMBERING_PART} num {num_id} is missing w:abstractNumId")
                continue
            abstract_id = abstract_ref.get(qn("w", "val"))
            if not abstract_id:
                errors.append(f"{NUMBERING_PART} num {num_id} has an empty w:abstractNumId")
            elif abstract_id not in abstract_ids:
                errors.append(
                    f"{NUMBERING_PART} num {num_id} references missing abstractNumId {abstract_id}"
                )

    settings_root = archive.read_xml(SETTINGS_PART) if archive.has(SETTINGS_PART) else None
    if settings_root is not None and settings_root.find(f"./{qn('w', 'trackRevisions')}") is not None:
        warnings.append(
            f"{SETTINGS_PART} has w:trackRevisions enabled; future edits may reopen review mode"
        )

    for rels_name in sorted(name for name in archive.entries if name.endswith(".rels")):
        rels_root = archive.read_xml(rels_name)
        seen_rel_ids: set[str] = set()
        source_part = relationship_source_part(rels_name)
        for rel in rels_root.findall(f"./{qn('rels', 'Relationship')}"):
            rel_id = rel.get("Id") or ""
            target = rel.get("Target") or ""
            if not rel_id:
                errors.append(f"{rels_name} contains a Relationship without an Id")
            elif rel_id in seen_rel_ids:
                errors.append(f"{rels_name} contains duplicate relationship Id {rel_id}")
            else:
                seen_rel_ids.add(rel_id)
            if not target:
                errors.append(f"{rels_name} contains relationship {rel_id or '<missing>'} without a Target")
                continue
            if rel.get("TargetMode") == "External":
                warnings.append(
                    f"{rels_name} relationship {rel_id or '<missing>'} targets external content; "
                    "review or remove it before sharing or opening the document in a trusted environment"
                )
                continue
            if source_part is None:
                continue
            resolved = resolve_relationship_target(source_part, target)
            if not resolved:
                errors.append(
                    f"{rels_name} contains relationship {rel_id or '<missing>'} with an empty internal Target"
                )
                continue
            if not archive.has(resolved):
                errors.append(
                    f"{rels_name} relationship {rel_id or '<missing>'} targets missing part {resolved}"
                )
                continue
            if defaults or overrides:
                if not part_has_content_type(resolved, defaults=defaults, overrides=overrides):
                    errors.append(f"{resolved} is referenced by {rels_name} but missing from [Content_Types].xml")

    comments_part_present = archive.has(COMMENT_PART)
    comments_root = archive.read_xml(COMMENT_PART) if comments_part_present else None
    comment_ids = comment_id_set(comments_root) if comments_root is not None else set()
    comments_present = bool(comment_ids)
    anchor_ids: set[str] = set()
    for story_part in archive.story_parts():
        root = archive.read_xml(story_part)
        field_errors, field_warnings = validate_story_part_fields(story_part, root)
        errors.extend(field_errors)
        warnings.extend(field_warnings)
        if styles_root is None:
            missing_style_refs = sorted(referenced_style_ids(root) - KNOWN_BUILTIN_STYLE_IDS)
            if missing_style_refs:
                errors.append(
                    f"{story_part} references style id(s) but {STYLES_PART} is missing: {', '.join(missing_style_refs)}"
                )
        else:
            missing_style_refs = sorted(referenced_style_ids(root) - style_ids - KNOWN_BUILTIN_STYLE_IDS)
            if missing_style_refs:
                errors.append(
                    f"{story_part} references undefined style id(s): {', '.join(missing_style_refs)}"
                )

        story_num_refs = referenced_num_ids(root)
        if story_num_refs and numbering_root is None:
            errors.append(
                f"{story_part} references numbering ids but {NUMBERING_PART} is missing: {', '.join(sorted(story_num_refs))}"
            )
        elif numbering_root is not None:
            missing_num_refs = sorted(story_num_refs - defined_num_ids(numbering_root))
            if missing_num_refs:
                errors.append(
                    f"{story_part} references undefined numbering id(s): {', '.join(missing_num_refs)}"
                )

        tracked_summary = tracked_change_summary(root)
        if tracked_summary["counts"]["total"]:
            warnings.append(
                f"{story_part} contains tracked changes "
                f"(ins={tracked_summary['counts']['insertions']}, del={tracked_summary['counts']['deletions']}, "
                f"move={tracked_summary['counts']['move_from'] + tracked_summary['counts']['move_to']}, "
                f"prop={tracked_summary['counts']['property_changes']})"
            )
        raw_head = root_start_tag(archive.entries[story_part])
        ignorable = root.get(qn("mc", "Ignorable"), "").split()
        for prefix in ignorable:
            if f"xmlns:{prefix}=".encode("utf-8") not in raw_head:
                errors.append(f"{story_part} mc:Ignorable references an undefined prefix: {prefix}")
        for paragraph in root.findall(f".//{qn('w', 'p')}"):
            anchor_ids.update(iter_comment_anchor_ids(paragraph))
            children = list(paragraph)
            ppr_index = next((index for index, child in enumerate(children) if child.tag == qn("w", "pPr")), None)
            for index, child in enumerate(children):
                if child.tag == qn("w", "commentRangeStart") and ppr_index is not None and index < ppr_index:
                    errors.append(f"{story_part} contains a commentRangeStart before w:pPr")
                    break

    document_root = archive.read_xml(document_part) if archive.has(document_part) else None
    document_rels_root = archive.read_xml(document_rels_part) if archive.has(document_rels_part) else None
    for section_index, sect_pr in enumerate(section_properties(document_root) if document_root is not None else [], start=1):
        seen_header_types: set[str] = set()
        seen_footer_types: set[str] = set()
        for tag, expected_rel_type, seen_types in (
            ("headerReference", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header", seen_header_types),
            ("footerReference", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer", seen_footer_types),
        ):
            for ref in sect_pr.findall(f"./{qn('w', tag)}"):
                ref_type = ref.get(qn("w", "type"), "default")
                if ref_type in seen_types:
                    errors.append(f"Section {section_index} contains duplicate {tag} entries for type {ref_type}")
                else:
                    seen_types.add(ref_type)
                rel_id = ref.get(qn("r", "id"))
                if not rel_id:
                    errors.append(f"Section {section_index} {tag} is missing r:id")
                    continue
                if document_rels_root is None:
                    errors.append(f"Section {section_index} {tag} references {rel_id} but {document_rels_part} is missing")
                    continue
                rel = relationship_by_id(document_rels_root, rel_id)
                if rel is None:
                    errors.append(f"Section {section_index} {tag} references undefined relationship id {rel_id}")
                    continue
                if rel.get("Type") != expected_rel_type:
                    errors.append(
                        f"Section {section_index} {tag} uses relationship {rel_id} with wrong type {rel.get('Type')}"
                    )
                    continue
                target = resolve_relationship_target(document_part, rel.get("Target") or "")
                if not target or not archive.has(target):
                    errors.append(f"Section {section_index} {tag} relationship {rel_id} targets missing part {target or '<empty>'}")
                    continue
                if tag == "headerReference" and not target.startswith("word/header"):
                    errors.append(f"Section {section_index} headerReference {rel_id} targets non-header part {target}")
                if tag == "footerReference" and not target.startswith("word/footer"):
                    errors.append(f"Section {section_index} footerReference {rel_id} targets non-footer part {target}")

    xml_parts = [
        name
        for name in archive.entries
        if name.endswith(".xml") and name != CONTENT_TYPES_PART and not name.endswith(".rels")
    ]
    for xml_part in sorted(xml_parts):
        root = archive.read_xml(xml_part)
        referenced_rel_ids = relationship_attr_values(root)
        if not referenced_rel_ids:
            continue
        rels_name = part_relationship_name(xml_part)
        if not archive.has(rels_name):
            errors.append(f"{xml_part} references relationships but {rels_name} is missing")
            continue
        rels_root = archive.read_xml(rels_name)
        defined_rel_ids = {
            rel.get("Id")
            for rel in rels_root.findall(f"./{qn('rels', 'Relationship')}")
            if rel.get("Id")
        }
        missing_ids = sorted(referenced_rel_ids - defined_rel_ids)
        if missing_ids:
            errors.append(
                f"{xml_part} references undefined relationship id(s): {', '.join(missing_ids)}"
            )

    if comments_part_present and comments_root is not None:
        comments_head = root_start_tag(archive.entries[COMMENT_PART])
        comments_ignorable = comments_root.get(qn("mc", "Ignorable"), "").split()
        for prefix in comments_ignorable:
            if f"xmlns:{prefix}=".encode("utf-8") not in comments_head:
                errors.append(f"{COMMENT_PART} mc:Ignorable references an undefined prefix: {prefix}")
        if len(comment_ids) != len(comments_root.findall(f"./{qn('w', 'comment')}")):
            errors.append("Duplicate comment IDs found in word/comments.xml")
        if not comments_present:
            warnings.append("word/comments.xml exists but contains no comments")

        seen_para_ids: set[str] = set()
        seen_text_ids: set[str] = set()
        comment_para_ids: dict[str, str] = {}
        for comment in comments_root.findall(f"./{qn('w', 'comment')}"):
            comment_id = comment.get(qn("w", "id"), "")
            for paragraph_index, paragraph in enumerate(comment.findall(f"./{qn('w', 'p')}"), start=1):
                warnings.extend(
                    comment_paragraph_structure_warnings(
                        comment_id,
                        paragraph_index,
                        paragraph,
                        require_annotation_reference=paragraph_index == 1,
                    )
                )

                para_id = paragraph.get(qn("w14", "paraId"))
                if para_id:
                    if comment_id:
                        comment_para_ids[para_id] = comment_id
                    if para_id in seen_para_ids:
                        warnings.append(f"Duplicate w14:paraId found in comments.xml: {para_id}")
                    else:
                        seen_para_ids.add(para_id)

                text_id = paragraph.get(qn("w14", "textId"))
                if text_id:
                    if text_id in seen_text_ids:
                        warnings.append(f"Duplicate w14:textId found in comments.xml: {text_id}")
                    else:
                        seen_text_ids.add(text_id)

        if archive.has(COMMENT_EXTENDED_PART):
            comments_extended_root = archive.read_xml(COMMENT_EXTENDED_PART)
            seen_comment_ex_para_ids: set[str] = set()
            for node in comments_extended_root.findall(f"./{qn('w15', 'commentEx')}"):
                para_id = node.get(qn("w15", "paraId"))
                parent_para_id = node.get(qn("w15", "paraIdParent"))
                if not para_id:
                    errors.append(f"{COMMENT_EXTENDED_PART} contains commentEx without w15:paraId")
                    continue
                if para_id in seen_comment_ex_para_ids:
                    warnings.append(f"{COMMENT_EXTENDED_PART} contains duplicate commentEx paraId {para_id}")
                else:
                    seen_comment_ex_para_ids.add(para_id)
                if para_id not in comment_para_ids:
                    errors.append(f"{COMMENT_EXTENDED_PART} references missing comment paraId {para_id}")
                if parent_para_id and parent_para_id not in comment_para_ids:
                    errors.append(
                        f"{COMMENT_EXTENDED_PART} commentEx paraId {para_id} references missing parent paraId {parent_para_id}"
                    )

        if archive.has(COMMENT_IDS_PART):
            comments_ids_root = archive.read_xml(COMMENT_IDS_PART)
            seen_comments_ids_para_ids: set[str] = set()
            for node in comments_ids_root.findall(f"./{qn('w16cid', 'commentId')}"):
                para_id = node.get(qn("w16cid", "paraId"))
                durable_id = node.get(qn("w16cid", "durableId"))
                if not para_id:
                    errors.append(f"{COMMENT_IDS_PART} contains commentId without w16cid:paraId")
                    continue
                if para_id in seen_comments_ids_para_ids:
                    warnings.append(f"{COMMENT_IDS_PART} contains duplicate commentId paraId {para_id}")
                else:
                    seen_comments_ids_para_ids.add(para_id)
                if para_id not in comment_para_ids:
                    errors.append(f"{COMMENT_IDS_PART} references missing comment paraId {para_id}")
                if not durable_id:
                    warnings.append(f"{COMMENT_IDS_PART} paraId {para_id} is missing durableId")

        rels_root = archive.read_xml(document_rels_part) if archive.has(document_rels_part) else None
        if rels_root is None or not any(
            rel.get("Type") == COMMENTS_REL_TYPE
            and resolve_relationship_target(document_part, rel.get("Target") or "") == COMMENT_PART
            for rel in rels_root.findall("./*")
        ):
            errors.append(f"word/comments.xml exists but {document_rels_part} has no comments relationship")
        if comment_ids and (rels_root is None or not any(
            rel.get("Type") == COMMENTS_EXTENDED_REL_TYPE
            and resolve_relationship_target(document_part, rel.get("Target") or "") == COMMENT_EXTENDED_PART
            for rel in rels_root.findall("./*")
        )):
            errors.append(f"Comments exist but {document_rels_part} has no commentsExtended relationship")
        if comment_ids and (rels_root is None or not any(
            rel.get("Type") == COMMENTS_IDS_REL_TYPE
            and resolve_relationship_target(document_part, rel.get("Target") or "") == COMMENT_IDS_PART
            for rel in rels_root.findall("./*")
        )):
            errors.append(f"Comments exist but {document_rels_part} has no commentsIds relationship")

        if content_types_root is None:
            errors.append("[Content_Types].xml is missing; cannot validate comment content types")
        elif not any(
            override.get("PartName") == f"/{COMMENT_PART}" and override.get("ContentType") == COMMENTS_CONTENT_TYPE
            for override in content_types_root.findall("./*")
        ):
            errors.append("[Content_Types].xml has no comments.xml override")
        if content_types_root is not None and comment_ids and not any(
            override.get("PartName") == f"/{COMMENT_EXTENDED_PART}" and override.get("ContentType") == COMMENTS_EXTENDED_CONTENT_TYPE
            for override in content_types_root.findall("./*")
        ):
            errors.append("[Content_Types].xml has no commentsExtended.xml override")
        if content_types_root is not None and comment_ids and not any(
            override.get("PartName") == f"/{COMMENT_IDS_PART}" and override.get("ContentType") == COMMENTS_IDS_CONTENT_TYPE
            for override in content_types_root.findall("./*")
        ):
            errors.append("[Content_Types].xml has no commentsIds.xml override")
        if comment_ids and not archive.has(COMMENT_EXTENDED_PART):
            errors.append("Comments exist but word/commentsExtended.xml is missing")
        if comment_ids and not archive.has(COMMENT_IDS_PART):
            errors.append("Comments exist but word/commentsIds.xml is missing")

        orphaned_anchors = sorted(anchor_ids - comment_ids)
        threaded_reply_ids: set[str] = set()
        if archive.has(COMMENT_EXTENDED_PART):
            comments_extended_root = archive.read_xml(COMMENT_EXTENDED_PART)
            reply_para_ids = {
                node.get(qn("w15", "paraId"))
                for node in comments_extended_root.findall(f"./{qn('w15', 'commentEx')}")
                if node.get(qn("w15", "paraIdParent"))
            }
            for comment in comments_root.findall(f"./{qn('w', 'comment')}"):
                comment_id = comment.get(qn("w", "id"))
                para_ids = {
                    paragraph.get(qn("w14", "paraId"))
                    for paragraph in comment.findall(f"./{qn('w', 'p')}")
                }
                if comment_id and para_ids.intersection(reply_para_ids):
                    threaded_reply_ids.add(comment_id)
        reply_parent_map = threaded_reply_parent_map(archive) if archive.has(COMMENT_EXTENDED_PART) else {}
        missing_reply_anchors = sorted(
            reply_id for reply_id in reply_parent_map
            if reply_id not in anchor_ids and reply_parent_map[reply_id] in anchor_ids
        )
        unanchored_comments = sorted(comment_ids - anchor_ids - threaded_reply_ids)
        if orphaned_anchors:
            errors.append(f"Anchors reference missing comments: {', '.join(orphaned_anchors)}")
        if missing_reply_anchors:
            warnings.append(
                f"Threaded replies exist without visible anchors and can be rebuilt: {', '.join(missing_reply_anchors)}"
            )
        if unanchored_comments:
            warnings.append(f"Comments exist without visible anchors: {', '.join(unanchored_comments)}")
    elif anchor_ids:
        errors.append(f"Comment anchors exist but {COMMENT_PART} is missing")

    if archive.has("word/settings.xml"):
        settings_root = archive.read_xml("word/settings.xml")
        if settings_root.find(f"./{qn('w', 'updateFields')}") is not None:
            warnings.append("word/settings.xml contains w:updateFields; Word may prompt to update fields on open")

    return {
        "path": str(path),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "comments_present": comments_present,
        "comments_part_present": comments_part_present,
        "comment_count": len(comment_ids),
        "anchored_comment_ids": sorted(anchor_ids),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a DOCX structurally and semantically, including comment wiring, "
            "field markup, relationships, and header/footer safety."
        )
    )
    parser.add_argument("input_docx", help="Path to the source DOCX")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of plain text")
    args = parser.parse_args()

    report = validate_docx(Path(args.input_docx).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ok: {report['ok']}")
        for warning in report["warnings"]:
            print(f"warning: {warning}")
        for error in report["errors"]:
            print(f"error: {error}")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
