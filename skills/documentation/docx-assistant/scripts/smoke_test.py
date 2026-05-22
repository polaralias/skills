#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMPLE_OUT = ROOT / "output" / "smoke-test-simple.docx"
BRANDED_OUT = ROOT / "output" / "smoke-test-branded.docx"
CONTACT_SHEET = ROOT / "output" / "smoke-test-branded-contact.png"


def run(cmd: list[str]) -> None:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"Command failed: {' '.join(cmd)}\n\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def main() -> None:
    run([sys.executable, "scripts/preflight.py"])
    run(
        [
            sys.executable,
            "scripts/generate_docx.py",
            "--mode",
            "simple",
            "--input",
            "references/spec-examples/simple-sop.json",
            "--output",
            str(SIMPLE_OUT),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/generate_docx.py",
            "--mode",
            "branded",
            "--input",
            "references/spec-examples/branded-proposal.json",
            "--output",
            str(BRANDED_OUT),
        ]
    )
    run([sys.executable, "scripts/render_contact_sheet.py", str(BRANDED_OUT), "--output", str(CONTACT_SHEET)])
    print(SIMPLE_OUT)
    print(BRANDED_OUT)
    print(CONTACT_SHEET)


if __name__ == "__main__":
    main()
