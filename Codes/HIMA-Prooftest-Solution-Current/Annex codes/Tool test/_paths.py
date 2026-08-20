"""Shared paths for Tool test scripts (solution root is two levels above Tool test)."""

from __future__ import annotations

import sys
from pathlib import Path

SOLUTION_ROOT = Path(__file__).resolve().parent.parent.parent
TOOL_TEST_ROOT = Path(__file__).resolve().parent
CONFIG_INI = SOLUTION_ROOT / "solution.ini"
# Gate tests use a fixture dir under Tool test (not production station markers).
SYNC_MARKERS = TOOL_TEST_ROOT / "data" / "sync_markers"
TEST_DATA = TOOL_TEST_ROOT / "data"


def setup_path() -> Path:
    root = str(SOLUTION_ROOT)
    annex = str(SOLUTION_ROOT / "Annex codes")
    if root not in sys.path:
        sys.path.insert(0, root)
    if annex not in sys.path:
        sys.path.insert(0, annex)
    return SOLUTION_ROOT


setup_path()
