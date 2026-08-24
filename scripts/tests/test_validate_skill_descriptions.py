from pathlib import Path

from scripts import validate_skill_descriptions


def test_active_estate_satisfies_description_contract() -> None:
    assert validate_skill_descriptions.validate_estate() == []


def test_rejects_capability_first_description() -> None:
    skill = validate_skill_descriptions.SkillDescription(
        name="example-skill",
        description="Build useful things. Use when the user asks. Shorthand EXS.",
        path=Path("skills/example/SKILL.md"),
    )

    assert "description must start with 'Use when '" in (
        validate_skill_descriptions.validate_description(skill)
    )


def test_rejects_catalogue_jargon() -> None:
    skill = validate_skill_descriptions.SkillDescription(
        name="example-skill",
        description=(
            "Use when the user asks for review-bounded output. Produces a result. "
            "Shorthand EXS."
        ),
        path=Path("skills/example/SKILL.md"),
    )

    assert any(
        "catalogue-hostile jargon" in error
        for error in validate_skill_descriptions.validate_description(skill)
    )


def test_scenario_corpus_covers_every_skill_on_both_axes() -> None:
    skills = validate_skill_descriptions.load_skill_descriptions()
    scenarios = validate_skill_descriptions.load_scenarios()

    assert validate_skill_descriptions.validate_scenarios(scenarios, skills) == []
