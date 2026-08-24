#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
INDEX_PATH = ROOT / "INDEX.md"
README_PATH = ROOT / "README.md"
ROUTING_FAMILIES_START = "<!-- polaralias-skill-routing:families:start -->"
ROUTING_FAMILIES_END = "<!-- polaralias-skill-routing:families:end -->"
SKILL_ACRONYMS = {
    "agenda-generator": "AGN",
    "ai-initiative-builder": "AIB",
    "ai-initiative-deep-dive-and-scoping": "ADS",
    "clickup-project-plan-builder": "CPP",
    "doc-driven-development": "DDD",
    "engineering-workflow-orchestrator": "EWO",
    "docx-assistant": "DXA",
    "elevenlabs-ai-voice-gen": "EAV",
    "feedback-rice-prioritiser": "FRP",
    "implementation-plan-writer": "IPW",
    "kickoff-summary-writer": "KSW",
    "knowledge-transfer-documentation-writer": "KTD",
    "linkedin-short-post-drafter": "LSP",
    "llm-instruction-fixer": "LIF",
    "llm-instruction-reviewer": "LIR",
    "local-handoff": "LHO",
    "local-pickup": "LPK",
    "long-form-post-drafter": "LFP",
    "meeting-pack-processor": "MPP",
    "mermaid-flowchart-designer": "MFD",
    "pandoc-converter": "PDC",
    "process-document-writer": "PDW",
    "project-context-builder": "PCB",
    "project-packager": "PKG",
    "project-report-writer": "PRW",
    "project-support": "PRS",
    "query-to-knowledge": "QTK",
    "release-note-writer": "RNW",
    "remotion-explainer-video-production": "REV",
    "repo-dissection": "RDS",
    "repo-change-comprehension": "RCC",
    "repo-knowledge-engineering": "RKE",
    "repo-publish-finaliser": "RPF",
    "repo-session-alignment": "RSA",
    "repo-setup": "RST",
    "repo-task-lifecycle": "RTL",
    "scheduling-assistant": "SCH",
    "setup-polaralias-skills": "SPS",
    "skill-eval-suite-writer": "SEW",
    "skill-finaliser": "SKF",
    "source-derived-design-system-builder": "SDS",
    "tasklist-gantt-creator": "TGC",
    "test-plan-writer": "TPW",
    "tracker-publisher": "TPU",
    "training-plan-writer": "TRW",
    "worktree-task-coordinator": "WTC",
}


def frontmatter_line_count(skill_md: Path) -> int:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return 0

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def skill_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^name: (.+)$", text, re.M)
    if not match:
        raise ValueError(f"Missing skill name in {skill_md}")
    return match.group(1).strip()


def skill_entries() -> list[tuple[str, str, str, int]]:
    entries: list[tuple[str, str, str, int]] = []
    for path in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        rel = path.relative_to(ROOT).as_posix()
        family = path.relative_to(SKILLS_ROOT).parts[0]
        name = skill_name(path)
        acronym = SKILL_ACRONYMS.get(name)
        if not acronym:
            raise ValueError(f"Missing acronym mapping for {name}")
        entries.append((family, rel, acronym, frontmatter_line_count(path)))
    return entries


def build_index(entries: list[tuple[str, str, str, int]]) -> str:

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
    lines.extend(
        f"- `{path}` ({acronym}): read first `{count}` lines"
        for _, path, acronym, count in entries
    )
    return "\n".join(lines) + "\n"


def build_routing_families(entries: list[tuple[str, str, str, int]]) -> str:
    families: dict[str, list[tuple[str, str, str]]] = {}
    for family, path, acronym, _ in entries:
        name = Path(path).parent.name
        families.setdefault(family, []).append((name, path, acronym))

    lines: list[str] = []
    for family, family_entries in families.items():
        lines.extend(
            [
                f"<!-- polaralias-skill-routing:family:{family}:start -->",
                f"### {family.title()}",
                "",
                f"For {family} work, inspect the current descriptions in the host's installed skill catalogue, then invoke every clearly matching skill before taking task actions. In the source repository, `README.md` and `INDEX.md` provide the canonical family and frontmatter paths.",
                "",
                "Current skills: "
                + ", ".join(
                    f"`{name}` ({acronym})"
                    for name, _path, acronym in family_entries
                )
                + ".",
                f"<!-- polaralias-skill-routing:family:{family}:end -->",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def replace_generated_routing(readme: str, generated: str) -> str:
    if readme.count(ROUTING_FAMILIES_START) != 1 or readme.count(ROUTING_FAMILIES_END) != 1:
        raise ValueError("README routing family markers must each appear exactly once")

    start = readme.index(ROUTING_FAMILIES_START) + len(ROUTING_FAMILIES_START)
    end = readme.index(ROUTING_FAMILIES_END)
    if start > end:
        raise ValueError("README routing family markers are out of order")
    return (
        readme[:start]
        + "\n"
        + generated
        + ROUTING_FAMILIES_END
        + readme[end + len(ROUTING_FAMILIES_END) :]
    )


def write_or_check(path: Path, expected: str, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == expected:
        return True
    if check:
        print(f"stale: {path}")
        return False
    path.write_text(expected, encoding="utf-8")
    print(path)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the skill index and README routing-family catalogue."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when generated surfaces are stale",
    )
    args = parser.parse_args()

    entries = skill_entries()
    expected_index = build_index(entries)
    readme = README_PATH.read_text(encoding="utf-8")
    expected_readme = replace_generated_routing(
        readme, build_routing_families(entries)
    )
    valid = write_or_check(INDEX_PATH, expected_index, args.check)
    valid = write_or_check(README_PATH, expected_readme, args.check) and valid
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
