from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from pandoc_convert import executable_filter_args


def test_executable_filter_arguments_are_detected() -> None:
    assert executable_filter_args(["--toc", "--filter", "evil", "--lua-filter=bad.lua", "-Ftool"]) == [
        "--filter",
        "--lua-filter=bad.lua",
        "-Ftool",
    ]


def test_ordinary_passthrough_arguments_remain_allowed() -> None:
    assert executable_filter_args(["--toc", "--number-sections", "--metadata", "title=Guide"]) == []
