from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SCENARIO_PATH = ROOT / "scripts" / "tests" / "fixtures" / "skill-routing-scenarios.json"
SHORTHAND_RE = re.compile(r"Shorthand ([A-Z]{3})\.$")
FORBIDDEN_ROUTING_JARGON = (
    "cross-artefact",
    "definitive light-first",
    "first-class",
    "producer extensions",
    "review-bounded",
    "vertical relationship focus",
)


@dataclass(frozen=True)
class SkillDescription:
    name: str
    description: str
    path: Path


def load_skill_descriptions(skills_root: Path = SKILLS_ROOT) -> list[SkillDescription]:
    descriptions: list[SkillDescription] = []
    for path in sorted(skills_root.glob("*/*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            raise ValueError(f"{path}: missing YAML frontmatter")
        try:
            frontmatter_text = text.split("---", 2)[1]
            frontmatter = yaml.safe_load(frontmatter_text)
        except (IndexError, yaml.YAMLError) as exc:
            raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
        descriptions.append(
            SkillDescription(
                name=str(frontmatter.get("name", "")),
                description=str(frontmatter.get("description", "")),
                path=path,
            )
        )
    return descriptions


def validate_description(skill: SkillDescription) -> list[str]:
    errors: list[str] = []
    description = skill.description
    if not skill.name:
        errors.append("missing name")
    if not description.startswith("Use when "):
        errors.append("description must start with 'Use when '")
    if len(description) > 1024:
        errors.append(f"description is {len(description)} characters; maximum is 1024")
    word_count = len(description.split())
    if word_count > 120:
        errors.append(f"description is {word_count} words; target maximum is 120")
    if "\n" in description:
        errors.append("description must be a single catalogue line")
    if "http://" in description or "https://" in description:
        errors.append("description must not contain URLs")
    if not SHORTHAND_RE.search(description):
        errors.append("description must end with 'Shorthand XXX.'")
    lowered = description.lower()
    for phrase in FORBIDDEN_ROUTING_JARGON:
        if phrase in lowered:
            errors.append(f"description contains catalogue-hostile jargon: {phrase!r}")
    return errors


def load_scenarios(path: Path = SCENARIO_PATH) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_scenarios(
    scenarios: list[dict[str, object]], skills: list[SkillDescription]
) -> list[str]:
    errors: list[str] = []
    skill_names = {skill.name for skill in skills}
    ids: set[str] = set()
    coverage = {name: {"positive": 0, "boundary": 0} for name in skill_names}

    for index, scenario in enumerate(scenarios):
        prefix = f"scenario[{index}]"
        scenario_id = scenario.get("id")
        kind = scenario.get("kind")
        expected = scenario.get("expected_skill")
        prompt = scenario.get("prompt")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append(f"{prefix}: missing string id")
        elif scenario_id in ids:
            errors.append(f"{prefix}: duplicate id {scenario_id!r}")
        else:
            ids.add(scenario_id)
        if kind not in {"positive", "boundary"}:
            errors.append(f"{prefix}: kind must be 'positive' or 'boundary'")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{prefix}: missing prompt")
        if expected is not None and expected not in skill_names:
            errors.append(f"{prefix}: unknown expected_skill {expected!r}")
        if isinstance(expected, str) and kind in {"positive", "boundary"}:
            coverage[expected][kind] += 1

    for name, counts in sorted(coverage.items()):
        if counts["positive"] == 0:
            errors.append(f"{name}: no positive routing scenario")
        if counts["boundary"] == 0:
            errors.append(f"{name}: no nearest-boundary routing scenario")
    return errors


def validate_estate(
    skills_root: Path = SKILLS_ROOT, scenario_path: Path = SCENARIO_PATH
) -> list[str]:
    errors: list[str] = []
    skills = load_skill_descriptions(skills_root)
    if not skills:
        return [f"no skills found under {skills_root}"]

    seen_names: set[str] = set()
    seen_shorthands: dict[str, str] = {}
    for skill in skills:
        for message in validate_description(skill):
            errors.append(f"{skill.path.relative_to(ROOT)}: {message}")
        if skill.name in seen_names:
            errors.append(f"duplicate skill name: {skill.name}")
        seen_names.add(skill.name)
        shorthand = SHORTHAND_RE.search(skill.description)
        if shorthand:
            alias = shorthand.group(1)
            if alias in seen_shorthands:
                errors.append(
                    f"duplicate shorthand {alias}: {seen_shorthands[alias]} and {skill.name}"
                )
            seen_shorthands[alias] = skill.name

    try:
        scenarios = load_scenarios(scenario_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{scenario_path.relative_to(ROOT)}: cannot load routing corpus: {exc}")
    else:
        errors.extend(validate_scenarios(scenarios, skills))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the estate-wide skill routing-description contract."
    )
    parser.parse_args()
    errors = validate_estate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    skill_count = len(load_skill_descriptions())
    scenario_count = len(load_scenarios())
    print(f"Validated {skill_count} skill descriptions and {scenario_count} routing scenarios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
