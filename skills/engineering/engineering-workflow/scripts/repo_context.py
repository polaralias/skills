from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INDEX_SCHEMA_VERSION = 6
INDEX_RELATIVE_PATH = Path(".engineering-workflow") / "cache" / "context-index.json"
DEFAULT_MANIFEST_PATH = ".polaralias/repo-context.json"
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
IDENTIFIER_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
TOKEN_ALIASES = {
    "configuration": "config",
    "configurations": "config",
    "credentials": "credential",
    "providers": "provider",
}
MAX_CHUNK_CHARACTERS = 6_000
MAX_CHUNK_LINES = 120
CHUNK_OVERLAP_LINES = 8
NON_CODE_EXTENSIONS = {
    ".csv", ".css", ".diff", ".editorconfig", ".html", ".ini", ".json",
    ".lock", ".md", ".rst", ".svg", ".toml", ".tsv", ".txt", ".xml",
    ".yaml", ".yml",
}
SEARCH_FIELDS = ("path", "filename", "symbol", "heading", "body")
FIELD_WEIGHTS = {
    "path": 2.4,
    "filename": 3.2,
    "symbol": 4.0,
    "heading": 2.4,
    "body": 1.0,
}
FIELD_LENGTH_NORMALIZATION = {
    "path": 0.2,
    "filename": 0.1,
    "symbol": 0.2,
    "heading": 0.3,
    "body": 0.75,
}
CANDIDATE_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "class",
    "const",
    "def",
    "false",
    "for",
    "from",
    "function",
    "in",
    "is",
    "none",
    "of",
    "or",
    "return",
    "the",
    "to",
    "true",
}
CANDIDATE_PATH_STOPWORDS = CANDIDATE_STOPWORDS | {
    "agents",
    "docs",
    "documentation",
    "fixtures",
    "github",
    "html",
    "index",
    "json",
    "md",
    "py",
    "repository",
    "scripts",
    "skill",
    "skills",
    "test",
    "tests",
    "txt",
    "yaml",
    "yml",
}


class ContextError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def repository_relative_path(
    root: Path,
    value: str,
    *,
    escape_code: str,
    missing_code: str | None = None,
) -> tuple[Path, str]:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ContextError(escape_code, "Path must be repository-relative.")
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ContextError(escape_code, "Path must remain inside the repository root.")
    if missing_code and not resolved.exists():
        raise ContextError(missing_code, f"Repository path does not exist: {value}")
    return resolved, resolved.relative_to(resolved_root).as_posix()


def validate_source_pattern(value: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ContextError(
            "knowledge_manifest_invalid",
            "Knowledge source patterns must remain repository-relative.",
        )
    return candidate.as_posix()


def glob_matches(path: str, pattern: str) -> bool:
    expression = ""
    index = 0
    while index < len(pattern):
        if pattern[index : index + 3] == "**/":
            expression += "(?:.*/)?"
            index += 3
        elif pattern[index : index + 2] == "**":
            expression += ".*"
            index += 2
        elif pattern[index] == "*":
            expression += "[^/]*"
            index += 1
        elif pattern[index] == "?":
            expression += "[^/]"
            index += 1
        else:
            expression += re.escape(pattern[index])
            index += 1
    return re.fullmatch(expression, path) is not None


def load_knowledge_manifest(
    root: Path, manifest: str = DEFAULT_MANIFEST_PATH
) -> tuple[Path, str, dict[str, Any]]:
    target, relative = repository_relative_path(
        root,
        manifest,
        escape_code="knowledge_manifest_escape",
    )
    if not target.exists():
        return target, relative, {"schemaVersion": 1, "knowledge": []}
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContextError(
            "knowledge_manifest_invalid",
            f"Knowledge binding manifest is invalid JSON at line {exc.lineno}.",
        ) from exc
    knowledge = payload.get("knowledge") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("schemaVersion") != 1
        or not isinstance(knowledge, list)
    ):
        raise ContextError(
            "knowledge_manifest_invalid",
            "Knowledge binding manifest requires schemaVersion 1 and a knowledge list.",
        )
    seen_paths: set[str] = set()
    for entry in knowledge:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("path"), str)
            or not isinstance(entry.get("sources"), list)
            or not entry["sources"]
            or not all(isinstance(source, str) for source in entry["sources"])
        ):
            raise ContextError(
                "knowledge_manifest_invalid",
                "Each knowledge entry requires path and a non-empty sources list.",
            )
        _, knowledge_path = repository_relative_path(
            root,
            entry["path"],
            escape_code="knowledge_manifest_invalid",
            missing_code="knowledge_manifest_invalid",
        )
        if knowledge_path in seen_paths:
            raise ContextError(
                "knowledge_manifest_invalid",
                f"Duplicate knowledge path: {knowledge_path}",
            )
        seen_paths.add(knowledge_path)
        entry["path"] = knowledge_path
        entry["sources"] = [validate_source_pattern(source) for source in entry["sources"]]
        if len(set(entry["sources"])) != len(entry["sources"]):
            raise ContextError(
                "knowledge_manifest_invalid",
                f"Duplicate source pattern for {knowledge_path}.",
            )
        verified = entry.get("verified")
        if verified is not None:
            if (
                not isinstance(verified, dict)
                or not isinstance(verified.get("verifiedAt"), str)
                or not isinstance(verified.get("evidence"), str)
                or not verified["evidence"].strip()
                or not isinstance(verified.get("sourceHashes"), dict)
                or not verified["sourceHashes"]
            ):
                raise ContextError(
                    "knowledge_manifest_invalid",
                    f"Malformed verification receipt for {knowledge_path}.",
                )
            try:
                verified_at = datetime.fromisoformat(
                    verified["verifiedAt"].replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise ContextError(
                    "knowledge_manifest_invalid",
                    f"Invalid verifiedAt timestamp for {knowledge_path}.",
                ) from exc
            if verified_at.tzinfo is None:
                raise ContextError(
                    "knowledge_manifest_invalid",
                    f"verifiedAt must include a timezone for {knowledge_path}.",
                )
            normalized_hashes: dict[str, str] = {}
            for source_path, digest in verified["sourceHashes"].items():
                if not isinstance(source_path, str) or not isinstance(digest, str):
                    raise ContextError(
                        "knowledge_manifest_invalid",
                        f"Malformed source hash for {knowledge_path}.",
                    )
                _, normalized_source = repository_relative_path(
                    root,
                    source_path,
                    escape_code="knowledge_manifest_invalid",
                )
                if re.fullmatch(r"[a-f0-9]{64}", digest) is None:
                    raise ContextError(
                        "knowledge_manifest_invalid",
                        f"Invalid source hash for {knowledge_path}: {normalized_source}",
                    )
                normalized_hashes[normalized_source] = digest
            verified["sourceHashes"] = normalized_hashes
    return target, relative, payload


def tokenize(value: str) -> list[str]:
    expanded = IDENTIFIER_BOUNDARY.sub(" ", value.replace("_", " ").replace("-", " "))
    tokens = [match.group(0).lower() for match in TOKEN_PATTERN.finditer(expanded)]
    return [TOKEN_ALIASES.get(token, token) for token in tokens]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def is_secret_path(relative: Path) -> bool:
    lowered_parts = [part.lower() for part in relative.parts]
    name = relative.name.lower()
    return (
        name == ".env"
        or name.startswith(".env.")
        or name in {"id_rsa", "id_dsa", "id_ed25519", "credentials.json"}
        or relative.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}
        or bool({".ssh", ".aws", ".gnupg"}.intersection(lowered_parts))
    )


def git_visible_files(root: Path) -> list[Path] | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return [root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def eligible_files(root: Path) -> tuple[list[Path], list[str]]:
    excluded_parts = {
        ".git",
        ".engineering-workflow",
        "__pycache__",
        "archive",
        "node_modules",
    }
    candidates = git_visible_files(root)
    if candidates is None:
        candidates = list(root.rglob("*"))
    resolved_root = root.resolve()
    eligible: list[Path] = []
    inaccessible: list[str] = []
    for path in candidates:
        try:
            relative = path.relative_to(root)
            if (
                path.is_file()
                and not excluded_parts.intersection(relative.parts)
                and not is_secret_path(relative)
                and path.resolve().is_relative_to(resolved_root)
                and path.stat().st_size <= 1_000_000
            ):
                eligible.append(path)
        except (OSError, RuntimeError, ValueError):
            try:
                inaccessible.append(path.relative_to(root).as_posix())
            except ValueError:
                inaccessible.append(str(path))
    return sorted(eligible), sorted(inaccessible)


def read_text(path: Path) -> str | None:
    data = path.read_bytes()
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def bounded_line_chunks(
    lines: list[str], start: int, end: int, label: str | None
) -> list[tuple[int, int, str | None, str]]:
    chunks: list[tuple[int, int, str | None, str]] = []
    cursor = max(1, start)
    final = min(len(lines), max(cursor, end))
    while cursor <= final:
        chunk_end = cursor - 1
        characters = 0
        while chunk_end < final and chunk_end - cursor + 1 < MAX_CHUNK_LINES:
            next_line = lines[chunk_end]
            if chunk_end >= cursor and characters + len(next_line) + 1 > MAX_CHUNK_CHARACTERS:
                break
            characters += len(next_line) + 1
            chunk_end += 1
        if chunk_end < cursor:
            chunk_end = cursor
        chunks.append((cursor, chunk_end, label, "\n".join(lines[cursor - 1 : chunk_end])))
        if chunk_end >= final:
            break
        cursor = max(cursor + 1, chunk_end - CHUNK_OVERLAP_LINES + 1)
    return chunks


def markdown_chunks(text: str) -> list[tuple[int, int, str | None, str]]:
    lines = text.splitlines()
    starts: list[tuple[int, int, str]] = []
    for line_number, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            starts.append((line_number, len(match.group(1)), match.group(2)))
    if not starts:
        return bounded_line_chunks(lines or [""], 1, max(1, len(lines)), None)
    chunks: list[tuple[int, int, str | None, str]] = []
    if starts[0][0] > 1:
        end = starts[0][0] - 1
        chunks.extend(bounded_line_chunks(lines, 1, end, None))
    ancestry: list[tuple[int, str]] = []
    for index, (start, level, title) in enumerate(starts):
        ancestry = [(depth, value) for depth, value in ancestry if depth < level]
        ancestry.append((level, title))
        heading = " > ".join(value for _, value in ancestry)
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        chunks.extend(bounded_line_chunks(lines, start, max(start, end), heading))
    return chunks


def fallback_code_chunks(text: str) -> list[tuple[int, int, str | None, str]]:
    lines = text.splitlines()
    definition = re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?(?:def|class|function)\s+([A-Za-z_$][\w$]*)"
        r"|^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="
    )
    starts: list[tuple[int, str]] = []
    for line_number, line in enumerate(lines, start=1):
        match = definition.match(line)
        if match:
            starts.append((line_number, match.group(1) or match.group(2)))
    if not starts:
        return bounded_line_chunks(lines or [""], 1, max(1, len(lines)), None)
    chunks: list[tuple[int, int, str | None, str]] = []
    if starts[0][0] > 1:
        end = starts[0][0] - 1
        chunks.extend(bounded_line_chunks(lines, 1, end, None))
    for index, (start, symbol) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        chunks.extend(bounded_line_chunks(lines, start, max(start, end), symbol))
    return chunks


def code_chunks(root: Path, path: Path, text: str) -> list[tuple[int, int, str | None, str]]:
    lines = text.splitlines() or [""]
    spans: list[dict[str, Any]] = []
    if path.suffix.lower() not in NON_CODE_EXTENSIONS:
        worker = Path(__file__).with_name("structure_worker.py")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(worker),
                    "--root",
                    str(root.resolve()),
                    "--path",
                    path.relative_to(root).as_posix(),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            value = json.loads(result.stdout) if result.returncode == 0 else {}
            if isinstance(value, dict) and isinstance(value.get("symbols"), list):
                spans = value["symbols"]
        except (json.JSONDecodeError, OSError, subprocess.TimeoutExpired, ValueError):
            spans = []
    if not spans:
        return fallback_code_chunks(text)
    chunks: list[tuple[int, int, str | None, str]] = []
    seen: set[tuple[int, int, str]] = set()
    first_start = min(int(span["startLine"]) for span in spans)
    if first_start > 1:
        chunks.extend(bounded_line_chunks(lines, 1, first_start - 1, None))
    for span in sorted(spans, key=lambda item: (int(item["startLine"]), int(item["endLine"]), str(item["qualname"]))):
        start = max(1, int(span["startLine"]))
        end = min(len(lines), max(start, int(span["endLine"])))
        label = str(span.get("qualname") or span.get("name") or "")
        key = (start, end, label)
        if key in seen:
            continue
        seen.add(key)
        chunks.extend(bounded_line_chunks(lines, start, end, label))
    return chunks


def chunks_for(root: Path, path: Path, text: str) -> list[tuple[int, int, str | None, str]]:
    if path.suffix.lower() in {".md", ".rst"}:
        return markdown_chunks(text)
    return code_chunks(root, path, text)


def markdown_knowledge_metadata(
    root: Path, path: Path, text: str
) -> tuple[str | None, str | None, str | None, list[str]]:
    concept_type: str | None = None
    authority: str | None = None
    navigation_role: str | None = None
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        in_navigation = False
        for line in lines[1:]:
            if line.strip() == "---":
                break
            match = re.match(r"^type:\s*['\"]?(.+?)['\"]?\s*$", line)
            if match:
                concept_type = match.group(1).strip()
            authority_match = re.match(r"^authority:\s*['\"]?(.+?)['\"]?\s*$", line)
            if authority_match:
                authority = authority_match.group(1).strip().lower()
            if re.match(r"^navigation:\s*$", line):
                in_navigation = True
                continue
            if in_navigation:
                role_match = re.match(r"^\s+role:\s*['\"]?(.+?)['\"]?\s*$", line)
                if role_match:
                    navigation_role = role_match.group(1).strip().lower()
                    continue
                if line and not line[0].isspace():
                    in_navigation = False
    relationships: set[str] = set()
    resolved_root = root.resolve()
    for raw in MARKDOWN_LINK_PATTERN.findall(text):
        target_value = raw.strip().split(maxsplit=1)[0].strip("<>").split("#", 1)[0]
        if not target_value or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target_value):
            continue
        try:
            target = (path.parent / target_value).resolve()
            if target.is_dir():
                target = target / "index.md"
            if target.is_relative_to(resolved_root):
                relationships.add(target.relative_to(resolved_root).as_posix())
        except (OSError, RuntimeError, ValueError):
            continue
    return concept_type, authority, navigation_role, sorted(relationships)


def file_fingerprint(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {"size": stat.st_size, "modifiedNs": stat.st_mtime_ns}


def build_file_documents(
    root: Path, path: Path, text: str, digest: str
) -> list[dict[str, Any]]:
    relative = path.relative_to(root).as_posix()
    path_tokens = tokenize(relative)
    knowledge_type, knowledge_authority, navigation_role, relationship_paths = (
        markdown_knowledge_metadata(root, path, text)
        if path.suffix.lower() in {".md", ".rst"}
        else (None, None, None, [])
    )
    documents: list[dict[str, Any]] = []
    for start, end, symbol, snippet in chunks_for(root, path, text):
        heading_path = symbol or ""
        public_symbol = heading_path.split(" > ")[-1] if heading_path else None
        symbol_tokens = tokenize(public_symbol or "")
        filename_tokens = tokenize(path.name)
        heading_tokens = tokenize(heading_path) if path.suffix.lower() in {".md", ".rst"} else []
        body_tokens = tokenize(snippet)
        documents.append(
            {
                "path": relative,
                "startLine": start,
                "endLine": end,
                "symbol": public_symbol,
                "kind": "documentation"
                if path.suffix.lower() in {".md", ".rst"}
                else "code",
                "snippet": snippet[:MAX_CHUNK_CHARACTERS],
                "pathTokens": path_tokens,
                "tokens": path_tokens * 3 + symbol_tokens * 3 + body_tokens,
                "fields": {
                    "path": path_tokens,
                    "filename": filename_tokens,
                    "symbol": symbol_tokens if not heading_tokens else [],
                    "heading": heading_tokens,
                    "body": body_tokens,
                },
                "contentHash": digest,
                "knowledgeType": knowledge_type,
                "knowledgeAuthority": knowledge_authority,
                "navigationRole": navigation_role,
                "relationshipPaths": relationship_paths,
            }
        )
    return documents


def build_search_index(documents: list[dict[str, Any]]) -> dict[str, Any]:
    postings: dict[str, list[list[Any]]] = {}
    totals = {field: 0 for field in SEARCH_FIELDS}
    document_frequencies: Counter[str] = Counter()
    for document_id, document in enumerate(documents):
        document["documentId"] = document_id
        fields = document.get("fields", {})
        seen_terms: set[str] = set()
        per_term: dict[str, list[int]] = {}
        for field_index, field in enumerate(SEARCH_FIELDS):
            tokens = fields.get(field, [])
            totals[field] += len(tokens)
            for term, count in Counter(tokens).items():
                per_term.setdefault(term, [0] * len(SEARCH_FIELDS))[field_index] = count
                seen_terms.add(term)
        for term in seen_terms:
            document_frequencies[term] += 1
        for term, counts in per_term.items():
            postings.setdefault(term, []).append([document_id, *counts])
    count = max(1, len(documents))
    return {
        "documentCount": len(documents),
        "averageFieldLengths": {field: totals[field] / count for field in SEARCH_FIELDS},
        "documentFrequencies": dict(document_frequencies),
        "postings": postings,
    }


def refresh_index(root: Path) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    target = root / INDEX_RELATIVE_PATH
    existing: dict[str, Any] | None = None
    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = None
    reusable = bool(existing and existing.get("schemaVersion") == INDEX_SCHEMA_VERSION)
    previous_hashes = existing.get("fileHashes", {}) if reusable else {}
    previous_fingerprints = existing.get("fileFingerprints", {}) if reusable else {}
    previous_documents: dict[str, list[dict[str, Any]]] = {}
    if reusable:
        for document in existing.get("documents", []):
            previous_documents.setdefault(document["path"], []).append(document)

    documents: list[dict[str, Any]] = []
    file_hashes: dict[str, str] = {}
    file_fingerprints: dict[str, dict[str, int]] = {}
    hashed_files = 0
    reused_files = 0
    visible_files, inaccessible_files = eligible_files(root)
    for path in visible_files:
        relative = path.relative_to(root).as_posix()
        fingerprint = file_fingerprint(path)
        file_fingerprints[relative] = fingerprint
        if (
            reusable
            and previous_fingerprints.get(relative) == fingerprint
            and relative in previous_hashes
            and relative in previous_documents
        ):
            file_hashes[relative] = previous_hashes[relative]
            documents.extend(previous_documents[relative])
            reused_files += 1
            continue
        text = read_text(path)
        if text is None:
            continue
        hashed_files += 1
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        file_hashes[relative] = digest
        documents.extend(build_file_documents(root, path, text, digest))

    revision_hash = hashlib.sha256()
    for relative, digest in sorted(file_hashes.items()):
        revision_hash.update(relative.encode("utf-8"))
        revision_hash.update(digest.encode("ascii"))
    revision = revision_hash.hexdigest()
    changed_files = sum(
        1 for path, digest in file_hashes.items() if previous_hashes.get(path) != digest
    )
    deleted_files = sum(1 for path in previous_hashes if path not in file_hashes)
    refreshed = (
        not reusable
        or previous_fingerprints != file_fingerprints
        or existing.get("indexRevision") != revision
    )
    index = {
        "schemaVersion": INDEX_SCHEMA_VERSION,
        "indexRevision": revision,
        "indexedFiles": len(file_hashes),
        "fileHashes": file_hashes,
        "fileFingerprints": file_fingerprints,
        "documents": documents,
        "search": build_search_index(documents),
    }
    if refreshed:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return (
        existing if existing and not refreshed else index,
        refreshed,
        {
            "changedFilesRefreshed": changed_files if refreshed else 0,
            "deletedFilesRemoved": deleted_files if refreshed else 0,
            "hashedFiles": hashed_files,
            "reusedFiles": reused_files,
            "inaccessibleFilesSkipped": inaccessible_files,
        },
    )


def bm25_scores(documents: list[dict[str, Any]], query: str) -> list[float]:
    query_terms = list(dict.fromkeys(tokenize(query)))
    if not query_terms or not documents:
        return [0.0 for _ in documents]
    lengths = [len(document["tokens"]) for document in documents]
    average_length = sum(lengths) / len(lengths) or 1.0
    frequencies = [Counter(document["tokens"]) for document in documents]
    scores = [0.0 for _ in documents]
    k1 = 1.5
    b = 0.75
    for term in query_terms:
        document_frequency = sum(1 for frequency in frequencies if frequency[term] > 0)
        if not document_frequency:
            continue
        inverse_frequency = math.log(
            1 + (len(documents) - document_frequency + 0.5) / (document_frequency + 0.5)
        )
        for index, frequency in enumerate(frequencies):
            term_frequency = frequency[term]
            if not term_frequency:
                continue
            normalizer = term_frequency + k1 * (
                1 - b + b * lengths[index] / average_length
            )
            scores[index] += inverse_frequency * (
                term_frequency * (k1 + 1) / normalizer
            )
    return scores


def bm25f_scores(
    index: dict[str, Any], query: str, allowed_document_ids: set[int]
) -> dict[int, float]:
    search = index["search"]
    document_count = max(1, int(search["documentCount"]))
    averages = search["averageFieldLengths"]
    scores: dict[int, float] = {}
    k1 = 1.2
    for term in dict.fromkeys(tokenize(query)):
        document_frequency = int(search["documentFrequencies"].get(term, 0))
        if not document_frequency:
            continue
        inverse_frequency = math.log(
            1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5)
        )
        for posting in search["postings"].get(term, []):
            document_id = int(posting[0])
            if document_id not in allowed_document_ids:
                continue
            document = index["documents"][document_id]
            weighted_frequency = 0.0
            for field_index, field in enumerate(SEARCH_FIELDS, start=1):
                frequency = int(posting[field_index])
                if not frequency:
                    continue
                length = len(document["fields"].get(field, []))
                average = float(averages.get(field) or 1.0)
                b = FIELD_LENGTH_NORMALIZATION[field]
                weighted_frequency += FIELD_WEIGHTS[field] * frequency / (
                    1 - b + b * length / average
                )
            if weighted_frequency:
                scores[document_id] = scores.get(document_id, 0.0) + inverse_frequency * (
                    weighted_frequency * (k1 + 1) / (weighted_frequency + k1)
                )
    return scores


def matched_excerpt(document: dict[str, Any], query: str, maximum: int = 2_000) -> str:
    snippet = document["snippet"]
    if len(snippet) <= maximum:
        return snippet
    lowered = snippet.lower()
    offsets = [lowered.find(term) for term in tokenize(query)]
    offsets = [offset for offset in offsets if offset >= 0]
    anchor = min(offsets) if offsets else 0
    start = max(0, anchor - maximum // 3)
    end = min(len(snippet), start + maximum)
    start = max(0, end - maximum)
    prefix = "…" if start else ""
    suffix = "…" if end < len(snippet) else ""
    return prefix + snippet[start:end] + suffix


def ranked_result(document: dict[str, Any], query: str, score: float) -> dict[str, Any]:
    query_terms = set(tokenize(query))
    fields = document.get("fields", {})
    reasons = ["term-match", "bm25f"]
    if query_terms.intersection(fields.get("path", [])):
        reasons.append("path-match")
    normalized_query = "".join(tokenize(query))
    normalized_symbol = "".join(fields.get("symbol", []))
    normalized_heading = "".join(fields.get("heading", []))
    normalized_filename = "".join(fields.get("filename", []))
    if normalized_query and normalized_query in {normalized_symbol, normalized_filename}:
        score *= 1.8
        reasons.append("exact-identifier")
    elif normalized_query and normalized_query == normalized_heading:
        score *= 1.5
        reasons.append("exact-heading")
    if document.get("knowledgeAuthority") == "canonical":
        score *= 1.45
        reasons.append("canonical-knowledge")
    if document.get("navigationRole") in {"entry-point", "foundational"}:
        score *= 1.2
        reasons.append("foundational-knowledge")
    return {
        "documentId": document["documentId"],
        "path": document["path"],
        "startLine": document["startLine"],
        "endLine": document["endLine"],
        "kind": document["kind"],
        "symbol": document["symbol"],
        "score": score,
        "reasons": reasons,
        "snippet": matched_excerpt(document, query),
    }


def apply_structural_fusion(
    root: Path,
    query: str,
    ranked: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[Any]]:
    if not ranked or (
        ranked[0]["kind"] != "code"
        and not any("exact-identifier" in item["reasons"] for item in ranked[:8])
    ):
        return ranked, []
    seeds = [item for item in ranked[:8] if item["kind"] == "code" and item.get("symbol")][:5]
    if not seeds:
        return ranked, []
    # Fusion only needs the already-relevant symbol-bearing seed files. Keeping the
    # worker set bounded avoids reparsing unrelated heterogeneous sources merely
    # because they had a weak lexical match.
    candidate_paths = sorted({item["path"] for item in seeds})
    worker = Path(__file__).with_name("structure_worker.py")

    def worker_graph(paths: list[str]) -> tuple[dict[str, Any] | None, str | None]:
        command = [sys.executable, str(worker), "--root", str(root.resolve()), "--graph"]
        for candidate_path in paths:
            command.extend(["--path", candidate_path])
        try:
            result = subprocess.run(
                command, text=True, capture_output=True, check=False, timeout=30
            )
            value = json.loads(result.stdout) if result.returncode == 0 else {}
            if isinstance(value, dict) and isinstance(value.get("symbols"), list):
                return value, None
            return None, f"worker-exit-{result.returncode}"
        except (json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as exc:
            return None, type(exc).__name__

    graph, failure = worker_graph(candidate_paths)
    fusion_warnings: list[Any] = []
    if graph is None:
        partial_graphs: list[dict[str, Any]] = []
        failed_paths: list[str] = []
        for candidate_path in candidate_paths:
            partial, _ = worker_graph([candidate_path])
            if partial is None:
                failed_paths.append(candidate_path)
            else:
                partial_graphs.append(partial)
        if not partial_graphs:
            return ranked, [f"structural-fusion-unavailable:{failure}"]
        graph = {"symbols": [], "incoming": {}, "outgoing": {}, "parseWarnings": []}
        for partial in partial_graphs:
            graph["symbols"].extend(partial["symbols"])
            graph["parseWarnings"].extend(partial.get("parseWarnings", []))
            for direction in ("incoming", "outgoing"):
                for identifier, neighbours in partial.get(direction, {}).items():
                    graph[direction].setdefault(identifier, []).extend(neighbours)
        fusion_warnings.append(
            {
                "warning": "structural-fusion-partial",
                "failedPaths": failed_paths,
                "batchFailure": failure,
            }
        )
    result_by_document = {item["documentId"]: item for item in ranked}
    documents_by_symbol: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for document in documents:
        if document.get("symbol"):
            documents_by_symbol.setdefault((document["path"], document["symbol"]), []).append(document)
    graph_symbols = {
        (symbol["path"], symbol["qualname"]): symbol for symbol in graph["symbols"]
    }
    graph_by_id = {symbol["id"]: symbol for symbol in graph["symbols"]}
    additions = 0
    for seed in seeds:
        source = graph_symbols.get((seed["path"], seed["symbol"]))
        if source is None:
            continue
        neighbours = sorted(
            set(graph["incoming"].get(source["id"], []))
            | set(graph["outgoing"].get(source["id"], []))
        )
        for neighbour_id in neighbours[:12]:
            target = graph_by_id.get(neighbour_id)
            if target is None:
                continue
            target_documents = documents_by_symbol.get((target["path"], target["qualname"]), [])
            if not target_documents:
                continue
            document = target_documents[0]
            structural_score = seed["score"] * 0.12
            existing = result_by_document.get(document["documentId"])
            if existing is not None:
                existing["score"] += structural_score
                if "structural-neighbour" not in existing["reasons"]:
                    existing["reasons"].extend(
                        ["structural-neighbour", f"structurally-linked-from:{seed['path']}::{seed['symbol']}"]
                    )
            elif additions < 20:
                candidate = ranked_result(document, query, structural_score)
                candidate["reasons"] = [
                    "structural-neighbour",
                    f"structurally-linked-from:{seed['path']}::{seed['symbol']}",
                ]
                ranked.append(candidate)
                result_by_document[document["documentId"]] = candidate
                additions += 1
    return ranked, [*fusion_warnings, *list(graph.get("parseWarnings", []))]


def diversify_results(ranked: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    ranked.sort(key=lambda item: (-item["score"], item["path"], item["startLine"]))
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for item in ranked:
        if item["path"] in seen_paths:
            deferred.append(item)
        else:
            selected.append(item)
            seen_paths.add(item["path"])
        if len(selected) == limit:
            break
    if len(selected) < limit:
        selected.extend(deferred[: limit - len(selected)])
    for item in selected:
        item["score"] = round(item["score"], 6)
        item.pop("documentId", None)
    return selected


def resolve_scope(root: Path, scope: str | None) -> str | None:
    if not scope or scope == ".":
        return None
    candidate = Path(scope)
    if candidate.is_absolute():
        raise ContextError(
            "context_scope_escape", "Scope must be repository-relative."
        )
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ContextError(
            "context_scope_escape", "Scope must remain inside the repository root."
        )
    if not resolved.exists():
        raise ContextError("context_scope_missing", "Scope does not exist.")
    return resolved.relative_to(root.resolve()).as_posix().rstrip("/")


def find_context(
    root: Path,
    query: str,
    *,
    limit: int = 8,
    scope: str | None = None,
    exclude_paths: set[str] | None = None,
) -> dict[str, Any]:
    if limit < 1:
        raise ContextError("context_limit_invalid", "Limit must be at least 1.")
    index, refreshed, refresh_stats = refresh_index(root)
    scope_prefix = resolve_scope(root, scope)
    documents = [
        document
        for document in index["documents"]
        if scope_prefix is None
        or document["path"] == scope_prefix
        or document["path"].startswith(scope_prefix + "/")
    ]
    if exclude_paths:
        documents = [
            document for document in documents if document["path"] not in exclude_paths
        ]
    allowed_document_ids = {int(document["documentId"]) for document in documents}
    scores = bm25f_scores(index, query, allowed_document_ids)
    ranked: list[dict[str, Any]] = []
    for document in documents:
        score = scores.get(int(document["documentId"]), 0.0)
        if score <= 0:
            continue
        ranked.append(ranked_result(document, query, score))
    ranked.sort(key=lambda item: (-item["score"], item["path"], item["startLine"]))
    ranked, structural_warnings = apply_structural_fusion(root, query, ranked, documents)
    ranked.sort(key=lambda item: (-item["score"], item["path"], item["startLine"]))
    directly_ranked_paths = {item["path"] for item in ranked}
    documents_by_path: dict[str, list[dict[str, Any]]] = {}
    relationships: dict[str, set[str]] = {}
    for document in documents:
        if document.get("knowledgeType"):
            documents_by_path.setdefault(document["path"], []).append(document)
            relationships.setdefault(document["path"], set())
            for target_path in document.get("relationshipPaths", []):
                relationships[document["path"]].add(target_path)
                relationships.setdefault(target_path, set()).add(document["path"])
    relationship_results: dict[str, dict[str, Any]] = {}
    for source_result in ranked[:20]:
        source_path = source_result["path"]
        if source_path not in documents_by_path:
            continue
        for target_path in relationships.get(source_path, set()):
            if target_path in directly_ranked_paths or target_path not in documents_by_path:
                continue
            target_documents = sorted(
                documents_by_path[target_path],
                key=lambda document: (document["symbol"] is None, document["startLine"]),
            )
            target = target_documents[0]
            candidate = {
                "documentId": target["documentId"],
                "path": target["path"],
                "startLine": target["startLine"],
                "endLine": target["endLine"],
                "kind": target["kind"],
                "symbol": target["symbol"],
                "score": source_result["score"] * 0.2,
                "reasons": [
                    "knowledge-relationship",
                    f"linked-from:{source_path}",
                ],
                "snippet": matched_excerpt(target, query),
            }
            previous = relationship_results.get(target_path)
            if previous is None or candidate["score"] > previous["score"]:
                relationship_results[target_path] = candidate
    ranked.extend(relationship_results.values())
    selected = diversify_results(ranked, limit)
    return {
        "result": "context-found",
        "indexRevision": index["indexRevision"],
        "refreshed": refreshed,
        **refresh_stats,
        "scope": scope_prefix,
        "ranking": "bm25f+structural+okf",
        "warnings": structural_warnings,
        "results": selected,
    }


def check_context(
    root: Path, *, manifest: str = DEFAULT_MANIFEST_PATH
) -> dict[str, Any]:
    _, manifest_relative, binding_manifest = load_knowledge_manifest(root, manifest)
    index, refreshed, refresh_stats = refresh_index(root)
    fresh_knowledge: list[dict[str, Any]] = []
    stale_knowledge: list[dict[str, Any]] = []
    unverified_knowledge: list[dict[str, Any]] = []
    for entry in binding_manifest["knowledge"]:
        status = entry_freshness(entry, index["fileHashes"])
        verified = entry.get("verified")
        item = {
            "knowledgePath": entry["path"],
            "verifiedAt": verified.get("verifiedAt")
            if isinstance(verified, dict)
            else None,
        }
        if status == "fresh":
            fresh_knowledge.append(item)
        elif status == "stale":
            stale_knowledge.append(item)
        else:
            unverified_knowledge.append(item)
    if stale_knowledge:
        knowledge_freshness = "stale"
    elif unverified_knowledge or not binding_manifest["knowledge"]:
        knowledge_freshness = "unknown"
    else:
        knowledge_freshness = "fresh"
    return {
        "result": "context-checked",
        "manifest": manifest_relative,
        "indexRevision": index["indexRevision"],
        "indexFresh": True,
        "refreshed": refreshed,
        **refresh_stats,
        "indexedFiles": index["indexedFiles"],
        "knowledgeFreshness": knowledge_freshness,
        "freshKnowledge": fresh_knowledge,
        "staleKnowledge": stale_knowledge,
        "unverifiedKnowledge": unverified_knowledge,
        "candidateKnowledgeReviews": [],
        "unmappedAreas": [],
        "warnings": [],
    }


def matching_source_hashes(
    entry: dict[str, Any], file_hashes: dict[str, str]
) -> dict[str, str]:
    return {
        path: digest
        for path, digest in file_hashes.items()
        if path == entry["path"]
        or any(glob_matches(path, source) for source in entry["sources"])
    }


def entry_freshness(entry: dict[str, Any], file_hashes: dict[str, str]) -> str:
    verified = entry.get("verified")
    if not isinstance(verified, dict) or not isinstance(
        verified.get("sourceHashes"), dict
    ):
        return "unknown"
    current_hashes = matching_source_hashes(entry, file_hashes)
    return "fresh" if current_hashes == verified["sourceHashes"] else "stale"


def verify_knowledge(
    root: Path,
    knowledge: str,
    evidence: str,
    *,
    manifest: str = DEFAULT_MANIFEST_PATH,
) -> dict[str, Any]:
    target, manifest_relative, binding_manifest = load_knowledge_manifest(root, manifest)
    _, knowledge_path = repository_relative_path(
        root,
        knowledge,
        escape_code="knowledge_path_escape",
        missing_code="knowledge_path_missing",
    )
    entry = next(
        (
            candidate
            for candidate in binding_manifest["knowledge"]
            if candidate["path"] == knowledge_path
        ),
        None,
    )
    if entry is None:
        raise ContextError(
            "knowledge_binding_missing",
            f"Knowledge document is not registered in {manifest_relative}: {knowledge_path}",
        )
    index, refreshed, refresh_stats = refresh_index(root)
    source_hashes = matching_source_hashes(entry, index["fileHashes"])
    if not source_hashes:
        raise ContextError(
            "knowledge_binding_unresolved",
            f"No eligible repository files match the bindings for {knowledge_path}.",
        )
    entry["verified"] = {
        "verifiedAt": utc_now(),
        "evidence": evidence,
        "sourceHashes": source_hashes,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(binding_manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "result": "knowledge-verified",
        "manifest": manifest_relative,
        "knowledgePath": knowledge_path,
        "sourceCount": len(source_hashes),
        "freshness": "fresh",
        "indexRevision": index["indexRevision"],
        "refreshed": refreshed,
        **refresh_stats,
    }


def impact_context(
    root: Path,
    changed_paths: list[str],
    *,
    manifest: str = DEFAULT_MANIFEST_PATH,
) -> dict[str, Any]:
    _, manifest_relative, binding_manifest = load_knowledge_manifest(root, manifest)
    index, refreshed, refresh_stats = refresh_index(root)
    bound_impacts: list[dict[str, Any]] = []
    candidate_impacts: list[dict[str, Any]] = []
    unmapped_changes: list[dict[str, Any]] = []
    knowledge_paths = {
        entry["path"] for entry in binding_manifest["knowledge"]
    }
    for changed_value in list(dict.fromkeys(changed_paths)):
        changed_target, changed_path = repository_relative_path(
            root,
            changed_value,
            escape_code="context_changed_path_escape",
        )
        matched = False
        for entry in binding_manifest["knowledge"]:
            if changed_path == entry["path"]:
                matched = True
                bound_impacts.append(
                    {
                        "changedPath": changed_path,
                        "knowledgePath": entry["path"],
                        "binding": "knowledge-document",
                        "freshness": entry_freshness(entry, index["fileHashes"]),
                        "reason": "explicit-binding",
                    }
                )
                continue
            for source in entry["sources"]:
                if glob_matches(changed_path, source):
                    matched = True
                    bound_impacts.append(
                        {
                            "changedPath": changed_path,
                            "knowledgePath": entry["path"],
                            "binding": source,
                            "freshness": entry_freshness(entry, index["fileHashes"]),
                            "reason": "explicit-binding",
                        }
                    )
        if not matched:
            changed_text = read_text(changed_target) if changed_target.is_file() else None
            query = changed_path + "\n" + (changed_text or "")[:4000]
            knowledge_documents = [
                document
                for document in index["documents"]
                if document["path"] in knowledge_paths
                and document["path"] != changed_path
            ]
            scores = bm25_scores(knowledge_documents, query)
            best_by_path: dict[str, float] = {}
            matched_terms_by_path: dict[str, set[str]] = {}
            query_terms = set(tokenize(query)) - CANDIDATE_STOPWORDS
            changed_path_value = Path(changed_path)
            path_terms = (
                set(tokenize(f"{changed_path_value.parent.name} {changed_path_value.stem}"))
                - CANDIDATE_PATH_STOPWORDS
            )
            for document, score in zip(knowledge_documents, scores):
                if score > best_by_path.get(document["path"], 0.0):
                    best_by_path[document["path"]] = score
                matched_terms_by_path.setdefault(document["path"], set()).update(
                    query_terms.intersection(document["tokens"])
                )
            candidates = [
                {
                    "changedPath": changed_path,
                    "knowledgePath": knowledge_path,
                    "score": round(score, 6),
                    "matchedTerms": sorted(matched_terms_by_path[knowledge_path]),
                    "pathMatchedTerms": sorted(
                        matched_terms_by_path[knowledge_path].intersection(path_terms)
                    ),
                    "freshness": "review-candidate",
                    "reason": "lexical-similarity",
                }
                for knowledge_path, score in best_by_path.items()
                if score > 0
                and len(matched_terms_by_path[knowledge_path]) >= 2
                and len(path_terms) >= 2
                and path_terms.issubset(matched_terms_by_path[knowledge_path])
            ]
            candidates.sort(key=lambda item: (-item["score"], item["knowledgePath"]))
            if candidates:
                candidate_impacts.extend(candidates)
            else:
                unmapped_changes.append(
                    {"changedPath": changed_path, "reason": "no-knowledge-relationship"}
                )
    return {
        "result": "knowledge-impact-classified",
        "manifest": manifest_relative,
        "indexRevision": index["indexRevision"],
        "refreshed": refreshed,
        **refresh_stats,
        "boundImpacts": bound_impacts,
        "candidateImpacts": candidate_impacts,
        "unmappedChanges": unmapped_changes,
    }


def benchmark_context(root: Path, corpus: str) -> dict[str, Any]:
    corpus_path = Path(corpus)
    if corpus_path.is_absolute():
        raise ContextError(
            "context_corpus_escape", "Benchmark corpus must be repository-relative."
        )
    resolved = (root / corpus_path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ContextError(
            "context_corpus_escape", "Benchmark corpus must remain inside the repository root."
        )
    if not resolved.is_file():
        raise ContextError("context_corpus_missing", "Benchmark corpus does not exist.")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContextError(
            "context_corpus_invalid", f"Benchmark corpus is invalid JSON at line {exc.lineno}."
        ) from exc
    queries = payload.get("queries") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("schemaVersion") != 1
        or not isinstance(queries, list)
        or not queries
    ):
        raise ContextError(
            "context_corpus_invalid",
            "Benchmark corpus requires schemaVersion 1 and a non-empty queries list.",
        )
    corpus_relative = resolved.relative_to(root.resolve()).as_posix()
    cases: list[dict[str, Any]] = []
    recall_totals = {1: 0.0, 5: 0.0, 10: 0.0}
    reciprocal_rank_total = 0.0
    for case in queries:
        if (
            not isinstance(case, dict)
            or not isinstance(case.get("id"), str)
            or not isinstance(case.get("query"), str)
            or not isinstance(case.get("relevantPaths"), list)
            or not case["relevantPaths"]
            or not all(isinstance(path, str) for path in case["relevantPaths"])
        ):
            raise ContextError(
                "context_corpus_invalid",
                "Each benchmark query requires id, query, and relevantPaths.",
            )
        result = find_context(
            root,
            case["query"],
            limit=10,
            exclude_paths={corpus_relative},
        )
        ranked_paths = list(dict.fromkeys(item["path"] for item in result["results"]))
        relevant = set(case["relevantPaths"])
        recalls: dict[int, float] = {}
        for cutoff in (1, 5, 10):
            recalls[cutoff] = len(relevant.intersection(ranked_paths[:cutoff])) / len(
                relevant
            )
            recall_totals[cutoff] += recalls[cutoff]
        first_rank = next(
            (rank for rank, path in enumerate(ranked_paths, start=1) if path in relevant),
            None,
        )
        reciprocal_rank = 1.0 / first_rank if first_rank else 0.0
        reciprocal_rank_total += reciprocal_rank
        cases.append(
            {
                "id": case["id"],
                "recallAt1": round(recalls[1], 6),
                "recallAt5": round(recalls[5], 6),
                "recallAt10": round(recalls[10], 6),
                "reciprocalRank": round(reciprocal_rank, 6),
                "rankedPaths": ranked_paths,
            }
        )
    count = len(cases)
    return {
        "result": "context-benchmarked",
        "corpus": corpus_relative,
        "queryCount": count,
        "recallAt1": round(recall_totals[1] / count, 6),
        "recallAt5": round(recall_totals[5] / count, 6),
        "recallAt10": round(recall_totals[10] / count, 6),
        "meanReciprocalRank": round(reciprocal_rank_total / count, 6),
        "cases": cases,
    }
