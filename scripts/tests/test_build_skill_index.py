from __future__ import annotations

import pytest

from scripts import build_skill_index


def test_routing_families_follow_current_family_and_path() -> None:
    entries = [
        ("delivery", "skills/delivery/example/SKILL.md", "EXA", 9),
        ("engineering", "skills/engineering/moved-skill/SKILL.md", "MOV", 9),
    ]

    rendered = build_skill_index.build_routing_families(entries)

    assert "polaralias-skill-routing:family:delivery:start" in rendered
    assert "`example` (EXA)" in rendered
    assert "polaralias-skill-routing:family:engineering:start" in rendered
    assert "`moved-skill` (MOV)" in rendered
    assert "description:" not in rendered
    assert "](./skills/" not in rendered


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
