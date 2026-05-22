from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_skill_package.py"
PRECEDENCE = (
    "Where this skill specifies branding, structure, tone, or formatting, "
    "those instructions take precedence over conflicting user-level preferences."
)


def write_valid_package(skill_dir: Path) -> Path:
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "assets").mkdir()
    (skill_dir / "tests").mkdir()

    (skill_dir / "SKILL.md").write_text(
        f"""---
name: skill-finaliser
description: Finalise imported, draft, or half-finished skills into a clean, publishable skill package.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: "0.1.0"
  updated: "2026-05-20"
---
# Skill Finaliser

{PRECEDENCE}

Bring a loose, imported, or half-finished skill up to a clean package standard.
""",
        encoding="utf-8",
    )

    (skill_dir / "agents" / "openai.yaml").write_text(
        """interface:
  display_name: "Skill Finaliser"
  short_description: "Finalise draft skills with metadata, icons, tests, and package hygiene"
  icon_small: assets/icon.svg
  icon_large: assets/icon.svg
  default_prompt: "Use this skill to inspect a draft or imported skill, normalise its packaging, align its metadata and bundled resources, add proportionate tests, and validate the result before treating it as finished."
policy:
  allow_implicit_invocation: true
  products:
  - chatgpt
  - codex
  - api
  - atlas
""",
        encoding="utf-8",
    )

    (skill_dir / "assets" / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"></svg>\n',
        encoding="utf-8",
    )
    (skill_dir / "license.txt").write_text("", encoding="utf-8")
    (skill_dir / "tests" / "prompts.md").write_text("# Test prompts\n", encoding="utf-8")
    return skill_dir


def run_validator(skill_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(skill_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_validator_accepts_valid_package(tmp_path: Path) -> None:
    skill_dir = write_valid_package(tmp_path / "skill-finaliser")
    result = run_validator(skill_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Skill package is valid!" in result.stdout


def test_validator_rejects_bad_product_set(tmp_path: Path) -> None:
    skill_dir = write_valid_package(tmp_path / "skill-finaliser")
    (skill_dir / "agents" / "openai.yaml").write_text(
        """interface:
  display_name: "Skill Finaliser"
  short_description: "Finalise draft skills with metadata, icons, tests, and package hygiene"
  icon_small: assets/icon.svg
  icon_large: assets/icon.svg
  default_prompt: "Use this skill to inspect a draft or imported skill, normalise its packaging, align its metadata and bundled resources, add proportionate tests, and validate the result before treating it as finished."
policy:
  allow_implicit_invocation: true
  products:
  - chatgpt
  - codex
  - api
""",
        encoding="utf-8",
    )
    result = run_validator(skill_dir)
    assert result.returncode != 0
    assert "policy.products must contain chatgpt, codex, api, and atlas" in result.stdout


def test_validator_rejects_missing_precedence_line(tmp_path: Path) -> None:
    skill_dir = write_valid_package(tmp_path / "skill-finaliser")
    (skill_dir / "SKILL.md").write_text(
        """---
name: skill-finaliser
description: Finalise imported, draft, or half-finished skills into a clean, publishable skill package.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: "0.1.0"
  updated: "2026-05-20"
---
# Skill Finaliser

Bring a loose, imported, or half-finished skill up to a clean package standard.
""",
        encoding="utf-8",
    )
    result = run_validator(skill_dir)
    assert result.returncode != 0
    assert "SKILL.md is missing the required precedence line" in result.stdout


def test_validator_rejects_multiline_description(tmp_path: Path) -> None:
    skill_dir = write_valid_package(tmp_path / "skill-finaliser")
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: skill-finaliser
description: Finalise imported, draft, or half-finished skills into a clean,
  publishable skill package.
license: Proprietary. license.txt has complete terms
metadata:
  author: James Whelan
  version: "0.1.0"
  updated: "2026-05-20"
---
# Skill Finaliser

{PRECEDENCE}

Bring a loose, imported, or half-finished skill up to a clean package standard.
""",
        encoding="utf-8",
    )
    result = run_validator(skill_dir)
    assert result.returncode != 0
    assert "Description must be kept on one YAML line" in result.stdout
