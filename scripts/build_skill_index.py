#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
INDEX_PATH = ROOT / "INDEX.md"
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


def build_index() -> str:
    entries: list[tuple[str, str, int]] = []
    for path in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        rel = path.relative_to(ROOT).as_posix()
        name = skill_name(path)
        acronym = SKILL_ACRONYMS.get(name)
        if not acronym:
            raise ValueError(f"Missing acronym mapping for {name}")
        entries.append((rel, acronym, frontmatter_line_count(path)))

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
        for path, acronym, count in entries
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    INDEX_PATH.write_text(build_index(), encoding="utf-8")
    print(INDEX_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
