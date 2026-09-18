from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ENGINEERING = Path(__file__).resolve().parents[1] / "engineering.py"


def invoke(arguments: list[str]) -> int:
    result = subprocess.run(
        [sys.executable, str(ENGINEERING), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode
