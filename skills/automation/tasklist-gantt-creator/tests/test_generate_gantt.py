from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_gantt import safe_excel_text


def test_formula_like_imported_values_are_forced_to_text() -> None:
    for value in ("=WEBSERVICE(\"https://example.invalid\")", "+cmd", "-cmd", "@SUM(A1:A2)", "\tformula"):
        assert safe_excel_text(value).startswith("'")


def test_ordinary_labels_are_unchanged() -> None:
    assert safe_excel_text("Implementation") == "Implementation"
