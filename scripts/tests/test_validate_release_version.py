from pathlib import Path
import json
import subprocess
import sys


def test_changed_skill_and_its_zip_have_one_minor_release_owner(tmp_path):
    script = Path(__file__).resolve().parents[1] / "validate_release_version.py"

    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init")
    git("config", "user.name", "Release fixture")
    git("config", "user.email", "release@example.invalid")
    skill = tmp_path / "skills" / "engineering" / "fixture-skill"
    skill.mkdir(parents=True)
    metadata = skill / "SKILL.md"
    metadata.write_text("---\nmetadata:\n  version: 1.0.0\n---\n")
    archive = skill.with_suffix(".zip")
    archive.write_bytes(b"initial archive")
    (tmp_path / "VERSION").write_text("1.0.0\n")
    git("add", ".")
    git("commit", "-m", "Initial fixture")
    git("tag", "v1.0.0")
    metadata.write_text("---\nmetadata:\n  version: 1.1.0\n---\n")
    archive.write_bytes(b"updated archive")
    (tmp_path / "VERSION").write_text("1.1.0\n")
    git("add", ".")
    git("commit", "-m", "Update skill and its archive")
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["required_bump"] == "minor"
    assert report["changed_skills"] == [{"skill": "skills/engineering/fixture-skill", "previous": "1.0.0", "current": "1.1.0", "bump": "minor"}]
