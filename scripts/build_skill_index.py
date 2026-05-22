#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
INDEX_PATH = ROOT / "INDEX.md"


def frontmatter_line_count(skill_md: Path) -> int:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return 0

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def build_index() -> str:
    entries: list[tuple[str, int]] = []
    for path in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        rel = path.relative_to(ROOT).as_posix()
        entries.append((rel, frontmatter_line_count(path)))

    lines = [
        "# Skill Index",
        "",
        "This file is the canonical index of active packaged skills in this repository.",
        "",
        "For each skill, the line count tells you how many lines to read from `SKILL.md` to capture all frontmatter, including the closing `---`.",
        "",
        "## Skills",
        "",
    ]
    lines.extend(f"- `{path}`: read first `{count}` lines" for path, count in entries)
    return "\n".join(lines) + "\n"


def main() -> int:
    INDEX_PATH.write_text(build_index(), encoding="utf-8")
    print(INDEX_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
