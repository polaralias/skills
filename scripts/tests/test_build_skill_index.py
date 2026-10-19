from __future__ import annotations

import pytest

from scripts import build_skill_index


def test_routing_families_follow_current_family_and_path() -> None:
    entries = [
        ("delivery", "skills/delivery/example/SKILL.md", "EXA", 9),
        ("media", "skills/media/moved-skill/SKILL.md", "MOV", 9),
    ]

    rendered = build_skill_index.build_routing_families(entries)

    assert "polaralias-skill-routing:family:delivery:start" in rendered
    assert "`example` (EXA)" in rendered
    assert "polaralias-skill-routing:family:media:start" in rendered
    assert "`moved-skill` (MOV)" in rendered
    assert "description:" not in rendered
    assert "](./skills/" not in rendered


def test_engineering_family_routes_material_work_through_single_entrypoint() -> None:
    entries = [
        ("engineering", "skills/engineering/engineering-workflow/SKILL.md", "EWF", 9),
        ("engineering", "skills/engineering/repo-setup/SKILL.md", "RST", 9),
    ]

    rendered = build_skill_index.build_routing_families(entries)

    assert "invoke `engineering-workflow` as the normal skill entry point" in rendered
    assert "read-only explanations of repository code, implementation behaviour, or diffs" in rendered
    assert "code explanations use comprehension without creating workflow state" in rendered
    assert "EWF owns engineering methodology and works without RKE" in rendered
    assert "optional continuity support" in rendered
    assert "separate `rke` skill" in rendered
    assert "does not create another lifecycle" in rendered
    assert "OKF Tasks remains the independent execution-record primitive" in rendered
    assert "Historical package crosswalks remain source-side audit material outside EWF" in rendered
    assert "without adding aliases or orchestration peers to the installed methodology" in rendered
    assert "Primary skill: `engineering-workflow` (EWF)" in rendered
    assert "Separate pre-workflow package: `repo-setup` (RST)" in rendered
    assert "legacy-specialist" not in rendered
    assert "invoke every clearly matching skill" not in rendered


def test_replace_generated_routing_preserves_surrounding_readme() -> None:
    original = (
        "before\n"
        f"{build_skill_index.ROUTING_FAMILIES_START}\n"
        "stale\n"
        f"{build_skill_index.ROUTING_FAMILIES_END}\n"
        "after\n"
    )

    updated = build_skill_index.replace_generated_routing(original, "fresh\n")

    assert updated == (
        "before\n"
        f"{build_skill_index.ROUTING_FAMILIES_START}\n"
        "fresh\n"
        f"{build_skill_index.ROUTING_FAMILIES_END}\n"
        "after\n"
    )


@pytest.mark.parametrize(
    "readme",
    [
        "no markers",
        f"{build_skill_index.ROUTING_FAMILIES_START}\nmissing end",
        (
            f"{build_skill_index.ROUTING_FAMILIES_START}\n"
            f"{build_skill_index.ROUTING_FAMILIES_START}\n"
            f"{build_skill_index.ROUTING_FAMILIES_END}\n"
        ),
        (
            f"{build_skill_index.ROUTING_FAMILIES_END}\n"
            f"{build_skill_index.ROUTING_FAMILIES_START}\n"
        ),
    ],
)
def test_replace_generated_routing_rejects_malformed_markers(readme: str) -> None:
    with pytest.raises(ValueError):
        build_skill_index.replace_generated_routing(readme, "fresh\n")
