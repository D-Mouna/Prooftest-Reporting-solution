"""
Bootstrap package for the HIMA Prooftest solution (SPEC-001 v1.23).

Maps ``prooftest.*`` imports to ``Tool Steps/``, annex modules to ``Annex codes/``,
and the web app to ``Graphic Interface/``.
"""

from __future__ import annotations

import importlib.abc
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

__version__ = "1.64.0"

_SOLUTION_ROOT = Path(__file__).resolve().parent.parent.parent
_TOOL_STEPS = _SOLUTION_ROOT / "Tool Steps"
_ANNEX_BASE = _SOLUTION_ROOT / "Annex codes"

_ANNEX_MODULES: dict[str, tuple[str, str]] = {
    "annex_database": ("Database", "annex_database.py"),
    "annex_api_connexion": ("API connexion", "annex_api_connexion.py"),
    "annex_opc": ("OPC", "annex_opc.py"),
    "annex_pdf_generation": ("PDF generation", "annex_pdf_generation.py"),
    "annex_list_archive": ("Database", "annex_list_archive.py"),
    "annex_stop_service": ("Stop service", "annex_stop_service.py"),
    "annex_start_service": ("Stop service", "annex_start_service.py"),
    "annex_silworx_cleanup": ("Stop service", "annex_silworx_cleanup.py"),
    "annex_plugin_monitor": ("Plugin", "annex_plugin_monitor.py"),
}


def _load_module(qualified_name: str, file_path: Path) -> ModuleType:
    if qualified_name in sys.modules:
        return sys.modules[qualified_name]
    spec = importlib.util.spec_from_file_location(qualified_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {qualified_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module


class _ProoftestFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path, target=None):
        if not fullname.startswith("prooftest."):
            return None
        parts = fullname.split(".")
        if len(parts) == 2:
            py = _TOOL_STEPS / f"{parts[1]}.py"
            if py.is_file():
                return importlib.util.spec_from_file_location(fullname, py)
        if fullname == "prooftest.web.app":
            app_path = _SOLUTION_ROOT / "Graphic Interface" / "app.py"
            return importlib.util.spec_from_file_location(fullname, app_path)
        return None


def _bootstrap() -> None:
    annex = str(_ANNEX_BASE)
    if annex not in sys.path:
        sys.path.insert(0, annex)
    if not any(isinstance(finder, _ProoftestFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, _ProoftestFinder())

    for modname, (folder, filename) in _ANNEX_MODULES.items():
        qualified = f"prooftest.{modname}"
        path = _ANNEX_BASE / folder / filename
        _load_module(qualified, path)

    web_pkg = ModuleType("prooftest.web")
    web_pkg.__path__ = []  # type: ignore[attr-defined]
    web_pkg.__package__ = "prooftest.web"
    sys.modules["prooftest.web"] = web_pkg

    app_path = _SOLUTION_ROOT / "Graphic Interface" / "app.py"
    app_mod = _load_module("prooftest.web.app", app_path)
    setattr(web_pkg, "app", app_mod)


_bootstrap()
