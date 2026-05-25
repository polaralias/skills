from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def parse_semver(raw: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(raw.strip())
    if not match:
        raise ValueError(f"invalid semver: {raw!r}")
    return tuple(int(part) for part in match.groups())


def classify_bump(old: tuple[int, int, int], new: tuple[int, int, int]) -> str:
    if new[0] != old[0]:
        return "major"
    if new[1] != old[1]:
        return "minor"
    if new[2] != old[2]:
        return "patch"
    return "none"


def skill_root(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if len(parts) >= 3 and parts[0] == "skills":
        return "/".join(parts[:3])
    return None


def latest_previous_tag(current_tag: str) -> str | None:
    tags = [tag for tag in run_git("tag", "--sort=-v:refname").splitlines() if tag]
    for tag in tags:
        if tag != current_tag:
            return tag
    return None


def read_current_skill_version(skill_dir: str) -> str:
    text = Path(skill_dir, "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^  version:\s*\"?([0-9]+\.[0-9]+\.[0-9]+)\"?\s*$", text)
    if not match:
        raise ValueError(f"missing metadata.version in {skill_dir}/SKILL.md")
    return match.group(1)


def read_tagged_skill_version(tag: str, skill_dir: str) -> str | None:
    skill_path = f"{skill_dir}/SKILL.md"
    try:
        text = run_git("show", f"{tag}:{skill_path}")
    except subprocess.CalledProcessError:
        return None
    match = re.search(r"(?m)^  version:\s*\"?([0-9]+\.[0-9]+\.[0-9]+)\"?\s*$", text)
    if not match:
        raise ValueError(f"missing metadata.version in {skill_path} at {tag}")
    return match.group(1)


def diff_entries(previous_tag: str) -> list[tuple[str, list[str]]]:
    output = run_git("diff", "--name-status", f"{previous_tag}..HEAD", "--")
    entries: list[tuple[str, list[str]]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        entries.append((parts[0], parts[1:]))
    return entries


def validate_repo_version(current_tag: str | None) -> dict[str, object]:
    version_text = Path("VERSION").read_text(encoding="utf-8").strip()
    current_version = parse_semver(version_text)
    previous_tag = latest_previous_tag(current_tag or "")

    if not previous_tag:
        return {
            "version": version_text,
            "previous_tag": None,
            "required_bump": "initial",
            "changed_skills": [],
            "notes": ["No previous tag found; initial repo release."],
        }

    previous_version = parse_semver(previous_tag.removeprefix("v"))
    repo_bump = classify_bump(previous_version, current_version)
    if repo_bump == "none":
        raise ValueError(f"VERSION {version_text} must advance beyond {previous_tag}")

    entries = diff_entries(previous_tag)
    changed_skill_dirs: set[str] = set()
    rename_or_surface_change = False
    notes: list[str] = []

    for status, paths in entries:
        if status.startswith("R"):
            old_root = skill_root(paths[0])
            new_root = skill_root(paths[1])
            if old_root or new_root:
                rename_or_surface_change = True
                if old_root:
                    changed_skill_dirs.add(old_root)
                if new_root:
                    changed_skill_dirs.add(new_root)
        else:
            for path in paths:
                root = skill_root(path)
                if root:
                    changed_skill_dirs.add(root)

    required_bump = "patch"
    changed_skills_summary: list[dict[str, str]] = []

    if rename_or_surface_change:
        required_bump = "major"
        notes.append("One or more skill paths were renamed.")

    for skill_dir in sorted(changed_skill_dirs):
        previous_skill_version = read_tagged_skill_version(previous_tag, skill_dir)
        current_skill_file = Path(skill_dir, "SKILL.md")
        current_skill_version = read_current_skill_version(skill_dir) if current_skill_file.exists() else None

        if previous_skill_version is None or current_skill_version is None:
            required_bump = "major"
            notes.append(f"{skill_dir} was added or removed.")
            changed_skills_summary.append(
                {
                    "skill": skill_dir,
                    "previous": previous_skill_version or "missing",
                    "current": current_skill_version or "missing",
                    "bump": "major",
                }
            )
            continue

        skill_bump = classify_bump(parse_semver(previous_skill_version), parse_semver(current_skill_version))
        if skill_bump == "none":
            raise ValueError(
                f"{skill_dir} changed since {previous_tag} but metadata.version stayed at {current_skill_version}"
            )

        changed_skills_summary.append(
            {
                "skill": skill_dir,
                "previous": previous_skill_version,
                "current": current_skill_version,
                "bump": skill_bump,
            }
        )

        if skill_bump == "major":
            required_bump = "major"
        elif skill_bump == "minor" and required_bump != "major":
            required_bump = "minor"

    if len(changed_skills_summary) > 1 and required_bump == "patch":
        required_bump = "minor"
        notes.append("Multiple existing skills changed in one release.")

    if repo_bump != required_bump:
        raise ValueError(
            f"VERSION {version_text} is a {repo_bump} bump from {previous_tag}, but the changed skills require {required_bump}"
        )

    return {
        "version": version_text,
        "previous_tag": previous_tag,
        "required_bump": required_bump,
        "changed_skills": changed_skills_summary,
        "notes": notes,
    }


def main() -> int:
    current_tag = sys.argv[1] if len(sys.argv) > 1 else None
    result = validate_repo_version(current_tag)
    Path("version-metadata.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
