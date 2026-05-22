#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MIN_SHORT_DESCRIPTION_LENGTH = 20
MAX_SHORT_DESCRIPTION_LENGTH = 120
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "metadata"}
REQUIRED_PRODUCTS = {"chatgpt", "codex", "api", "atlas"}
ALLOWED_ICON_PATHS = {"assets/icon.svg", "./assets/icon.svg"}
REQUIRED_PRECEDENCE_LINE = (
    "Where this skill specifies branding, structure, tone, or formatting, "
    "those instructions take precedence over conflicting user-level preferences."
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(skill_md: Path) -> tuple[dict | None, str | None]:
    content = read_text(skill_md)
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", content, re.DOTALL)
    if not match:
        return None, "No YAML frontmatter found in SKILL.md"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"Invalid YAML in frontmatter: {exc}"
    if not isinstance(data, dict):
        return None, "Frontmatter must be a YAML mapping"
    return data, None


def validate_skill_directory(skill_dir: Path) -> list[str]:
    errors: list[str] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"]

    frontmatter, error = parse_frontmatter(skill_md)
    if error:
        return [error]

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(
            "Unexpected SKILL.md frontmatter keys: "
            + ", ".join(sorted(unexpected))
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("Missing or invalid 'name' in frontmatter")
    else:
        name = name.strip()
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append("Frontmatter name must be hyphen-case")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append("Frontmatter name cannot start/end with hyphen or contain consecutive hyphens")
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"Frontmatter name exceeds {MAX_NAME_LENGTH} characters")
        if name != skill_dir.name:
            errors.append(f"Frontmatter name '{name}' does not match folder name '{skill_dir.name}'")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("Missing or invalid 'description' in frontmatter")
    elif len(description.strip()) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"Description exceeds {MAX_DESCRIPTION_LENGTH} characters")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("Missing or invalid 'metadata' mapping")
    else:
        for field in ("author", "version", "updated"):
            value = metadata.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"metadata.{field} is missing or invalid")

    skill_body = read_text(skill_md)
    if REQUIRED_PRECEDENCE_LINE not in skill_body:
        errors.append("SKILL.md is missing the required precedence line")

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        errors.append("agents/openai.yaml not found")
    else:
        try:
            openai = yaml.safe_load(read_text(openai_yaml))
        except yaml.YAMLError as exc:
            errors.append(f"Invalid YAML in agents/openai.yaml: {exc}")
            openai = None

        if not isinstance(openai, dict):
            errors.append("agents/openai.yaml must be a YAML mapping")
        else:
            interface = openai.get("interface")
            policy = openai.get("policy")
            if not isinstance(interface, dict):
                errors.append("agents/openai.yaml must contain an interface mapping")
            else:
                display_name = interface.get("display_name")
                short_description = interface.get("short_description")
                default_prompt = interface.get("default_prompt")
                icon_small = interface.get("icon_small")
                icon_large = interface.get("icon_large")

                if not isinstance(display_name, str) or not display_name.strip():
                    errors.append("interface.display_name is missing or invalid")
                if not isinstance(short_description, str) or not short_description.strip():
                    errors.append("interface.short_description is missing or invalid")
                elif not (MIN_SHORT_DESCRIPTION_LENGTH <= len(short_description.strip()) <= MAX_SHORT_DESCRIPTION_LENGTH):
                    errors.append(
                        f"interface.short_description must be {MIN_SHORT_DESCRIPTION_LENGTH}-{MAX_SHORT_DESCRIPTION_LENGTH} characters"
                    )
                if not isinstance(default_prompt, str) or not default_prompt.strip():
                    errors.append("interface.default_prompt is missing or invalid")
                for field_name, value in (("interface.icon_small", icon_small), ("interface.icon_large", icon_large)):
                    if not isinstance(value, str) or value.strip() not in ALLOWED_ICON_PATHS:
                        errors.append(f"{field_name} must point to assets/icon.svg")

            if not isinstance(policy, dict):
                errors.append("agents/openai.yaml must contain a policy mapping")
            else:
                if policy.get("allow_implicit_invocation") is not True:
                    errors.append("policy.allow_implicit_invocation must be true")
                products = policy.get("products")
                if not isinstance(products, list) or set(products) != REQUIRED_PRODUCTS:
                    errors.append("policy.products must contain chatgpt, codex, api, and atlas")

    icon_path = skill_dir / "assets" / "icon.svg"
    if not icon_path.exists():
        errors.append("assets/icon.svg not found")
    else:
        try:
            ET.fromstring(read_text(icon_path))
        except ET.ParseError as exc:
            errors.append(f"assets/icon.svg is not valid SVG/XML: {exc}")

    license_path = skill_dir / "license.txt"
    if not license_path.exists():
        errors.append("license.txt not found")

    prompts_path = skill_dir / "tests" / "prompts.md"
    if not prompts_path.exists():
        errors.append("tests/prompts.md not found")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill package")
    parser.add_argument("skill_directory", help="Path to the skill folder")
    args = parser.parse_args()

    skill_dir = Path(args.skill_directory).resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"Skill directory not found: {skill_dir}")
        return 1

    errors = validate_skill_directory(skill_dir)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("Skill package is valid!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
