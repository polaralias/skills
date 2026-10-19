#!/usr/bin/env python3
"""Synchronize the active task adapter with a reviewed local OKF Tasks checkout.

Only the enumerated producer resources are written. Integration guidance and the
compatibility entry point remain independently maintained. No producer writes,
external services or installed host configuration are involved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "skills" / "engineering" / "repo-task-lifecycle"
SOURCE_SKILL = Path("skills/okf-task-lifecycle")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resources(source: Path) -> dict[str, tuple[str, bytes]]:
    result: dict[str, tuple[str, bytes]] = {}

    for name in ("visualize_bundle.py", "generate_complex_examples.py", "visualizer_template.html",
                 "vendor/mermaid-11.10.1.min.js", "vendor/mermaid-11.10.1.LICENSE"):
        root_copy = source / "scripts" / name
        skill_copy = source / SOURCE_SKILL / "scripts" / name
        if root_copy.read_bytes() != skill_copy.read_bytes():
            raise ValueError("Producer root and bundled resource differ: " + name)

    def add(origin: Path, destination: Path, transform=None) -> None:
        resolved = (source / origin).resolve(strict=True)
        if not resolved.is_relative_to(source):
            raise ValueError("Producer resource escapes checkout")
        data = resolved.read_bytes()
        result[destination.as_posix()] = (origin.as_posix(), transform(data) if transform else data)

    for directory in ("scripts", "assets", "references"):
        for path in sorted((source / SOURCE_SKILL / directory).rglob("*")):
            if path.is_file() and not any(part in {"__pycache__", "node_modules", ".pytest_cache", "dist", "build"} or part.endswith(".egg-info") for part in path.parts):
                add(path.relative_to(source), path.relative_to(source / SOURCE_SKILL))
    for name in ("SPEC.md", "VERSION", "package.json", "package-lock.json"):
        add(Path(name), Path(name))
    add(SOURCE_SKILL / "license.txt", Path("licenses/okf-tasks-Apache-2.0.txt"))
    add(Path("scripts/generate_local_docs.py"), Path("scripts/generate_local_docs.py"))
    for directory in ("schemas", "conformance", "examples", "implementations/typescript"):
        for path in sorted((source / directory).rglob("*")):
            if not path.is_file() or any(part in {"dist", "node_modules", "__pycache__"} for part in path.parts):
                continue
            # HTML workspaces are derived output; templates and vendor runtimes
            # are already included above. Normative fixtures remain intact.
            if directory == "examples" and path.suffix == ".html":
                continue
            relative = path.relative_to(source)
            transform = portable_cli_path if relative.as_posix() == "conformance/generate_fixtures.py" else None
            add(relative, relative, transform)
    add(Path("tests/test_okf_tasks.py"), Path("tests/test_okf_tasks.py"), portable_cli_path)
    add(Path("tests/test_visualize_bundle.py"), Path("tests/test_visualize_bundle.py"), portable_renderer_test)
    add(Path("tests/reader-navigation-browser.mjs"), Path("tests/reader-navigation-browser.mjs"))
    add(SOURCE_SKILL / "tests/prompts.md", Path("tests/okf-prompts.md"))
    add(SOURCE_SKILL / "SKILL.md", Path("references/okf-workflow.md"), workflow_reference)
    return result


def portable_cli_path(data: bytes) -> bytes:
    original = b'REPOSITORY / "skills" / "okf-task-lifecycle" / "scripts" / "okf_tasks.py"'
    if data.count(original) != 1:
        raise ValueError("Expected exactly one producer CLI location")
    return data.replace(original, b'REPOSITORY / "scripts" / "okf_tasks.py"')


def portable_renderer_test(data: bytes) -> bytes:
    # The producer tests its duplicate renderer locations. This package has one
    # location, so retain all behavioral tests and compare it to the recorded
    # reviewed producer bytes rather than making a self-comparison.
    text = data.decode("utf-8").replace("\r\n", "\n")
    start = text.index("    def test_repository_skill_bundles_the_same_renderer_and_template(self)")
    end = text.index('\n\nif __name__ == "__main__":', start)
    replacement = '''    def test_packaged_renderer_matches_reviewed_producer_bytes(self) -> None:
        import hashlib
        manifest = json.loads((REPOSITORY / "OKF_UPSTREAM.json").read_text(encoding="utf-8"))
        for name in ("visualize_bundle.py", "generate_complex_examples.py", "visualizer_template.html",
                     "vendor/mermaid-11.10.1.min.js", "vendor/mermaid-11.10.1.LICENSE"):
            key = "scripts/" + name
            with self.subTest(resource=key):
                actual = hashlib.sha256((REPOSITORY / key).read_bytes()).hexdigest()
                self.assertEqual(manifest["resources"][key]["source_sha256"], actual)
'''
    return (text[:start] + replacement + text[end:]).encode("utf-8")


def workflow_reference(data: bytes) -> bytes:
    text = data.decode("utf-8").replace("\r\n", "\n").split("---", 2)[2].lstrip()
    text = text.replace("Where this skill specifies branding, structure, tone, or formatting, those instructions take precedence over conflicting user-level preferences.\n\n", "")
    text = text.replace("`okf-task-lifecycle was used in this response.`", "`repo-task-lifecycle was used in this response.`")
    # References now live beside this document; scripts stay relative to package.
    text = text.replace("](./references/", "](./").replace("](./scripts/", "](../scripts/")
    return ("<!-- Producer workflow, adapted only for package paths, proof and instruction precedence. -->\n" + text).encode("utf-8")


def synchronize(source: Path, check: bool, source_commit: str | None = None) -> list[str]:
    source = source.resolve(strict=True)
    target = TARGET.resolve()
    if not target.is_relative_to((ROOT / "skills" / "engineering").resolve()) or source == target:
        raise ValueError("Invalid producer or destination")
    selected = resources(source)
    if source_commit is not None:
        if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            raise ValueError("Producer commit must be a full Git SHA")
        tree = subprocess.check_output(["git", "-C", str(source), "ls-tree", "-rz", source_commit])
        blobs = {}
        for entry in tree.split(b"\0"):
            if entry:
                metadata, name = entry.split(b"\t", 1)
                mode, kind, identity = metadata.split()
                if kind == b"blob" and mode in {b"100644", b"100755"}:
                    blobs[name.decode("utf-8")] = identity.decode("ascii")
        for origin in {origin for origin, _ in selected.values()}:
            data = (source / origin).read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if blobs.get(origin) != actual:
                raise ValueError("Producer resource differs from pinned commit: " + origin)
    previous = target / "OKF_UPSTREAM.json"
    if previous.is_file():
        old = json.loads(previous.read_text(encoding="utf-8"))["resources"]
        obsolete = [name for name in old if name not in selected and (target / name).exists()]
        if obsolete:
            raise ValueError("Review obsolete producer resources before synchronization: " + ", ".join(obsolete))
    manifest = {"schema": 1, "producer": "OKF Tasks", "version": (source / "VERSION").read_text().strip(),
                "identity": "Verified committed producer bytes" if source_commit else "Reviewed working-tree bytes, including uncommitted producer changes",
                "adaptations": ["CLI location in Python test and fixture generator", "Duplicate renderer test becomes producer hash check",
                                "Workflow reference package links, proof and user instruction precedence"],
                "resources": {name: {"source": origin, "source_sha256": digest((source / origin).read_bytes()),
                                     "package_sha256": digest(data)} for name, (origin, data) in selected.items()}}
    if source_commit:
        manifest["source_commit"] = source_commit
    outputs = {name: data for name, (_, data) in selected.items()}
    outputs["OKF_UPSTREAM.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    errors = []
    for name, data in outputs.items():
        destination = target / name
        if not destination.resolve().is_relative_to(target):
            raise ValueError("Resource escapes destination")
        if check:
            if not destination.is_file() or destination.read_bytes() != data:
                errors.append(name)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-commit", help="Require every selected resource to match this full Git SHA")
    args = parser.parse_args()
    errors = synchronize(args.source, args.check, args.source_commit)
    if errors:
        print("OKF upstream drift: " + ", ".join(errors))
        return 1
    print("OKF upstream resources " + ("match reviewed producer bytes" if args.check else "synchronized"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
