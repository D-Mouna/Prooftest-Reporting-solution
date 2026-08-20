"""
First-run station setup — SPEC-001 Step 1.

On first run, create ``C:\\HIMA Prooftest Reporting Tool`` with:
1. ``Database`` — SQL database files / SQLite + tables
2. ``HIMA Automated Prooftest Reports`` — generated PDF/HTML reports (+ Report Templates)
3. ``Results Structures`` — CSV type catalogue (baseline nine; new CSV = new type)
"""

from __future__ import annotations

import json
import logging
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from prooftest import __version__
from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.results_csv import RESULTS_TYPE_FILES, list_results_type_names

log = logging.getLogger(__name__)

# Baseline nine SILworX Results structure names (SPEC §3.1). Runtime may include more CSVs.
KNOWN_RESULTS_TYPES: Tuple[str, ...] = tuple(RESULTS_TYPE_FILES.keys())

_INVALID_PATH_CHARS = re.compile(r'[<>:"/\\|?*]')


def is_silworx_installed(programdata_root: Path) -> bool:
    """True when SILworX appears installed on this station (SPEC Step 1.1)."""
    program_files = Path(r"C:\Program Files\HIMA")
    if program_files.is_dir() and any(program_files.glob("SILworX_*")):
        return True
    if programdata_root.is_dir() and any(programdata_root.glob("SILworX_v*")):
        return True
    return False


def detect_deployment_case(programdata_root: Path) -> int:
    """
    Always returns 1 (unified operating mode).

    Former Case 2 (HMI / OPC-only) is part of the same path: API and OPC
    run together on every refresh; API contributes only when a project is open.
    """
    _ = programdata_root
    return 1


def results_type_folder_name(results_type: str) -> str:
    """Filesystem-safe folder name for a Results type (`/` → `-` on Windows)."""
    return results_type.replace("/", "-")


def sanitize_device_tag_for_path(device_tag: str) -> str:
    """Remove characters invalid in Windows folder names."""
    cleaned = _INVALID_PATH_CHARS.sub("_", device_tag.strip())
    cleaned = cleaned.rstrip(". ")
    return cleaned or "device"


def _installation_marker(folder: Path) -> Path:
    return folder / "installation.json"


def _load_installation(marker: Path) -> dict:
    if not marker.is_file():
        return {}
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_installation(marker: Path, payload: dict) -> None:
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def apply_deployment_case(config: AppConfig, marker: Path) -> bool:
    """
    Force unified mode (deployment_case = 1).

    Returns True on the very first run (new installation.json).
    ``auto_detect_case`` is obsolete and ignored.
    """
    existing = _load_installation(marker)
    is_first_run = not existing
    config.deployment_case = 1
    if is_first_run or config.auto_detect_case:
        log.info(
            "Unified operating mode (deployment_case=1; SILworX installed=%s, first_run=%s)",
            is_silworx_installed(config.silworx_programdata),
            is_first_run,
        )
    return is_first_run


def create_results_type_folder_hierarchy(
    roots: Iterable[Path],
    alarms: AlarmManager,
    results_types: Optional[Sequence[str]] = None,
) -> None:
    """
    Create one subfolder per Results type under each report root (SPEC Step 1.2).

    ``results_types`` defaults to the baseline nine; pass loaded CSV types so new
    catalogue entries get folders too.

    Example: C:\\HIMA Prooftest Reporting Tool\\HIMA Automated Prooftest Reports\\X-HART_WIKA_T32_Results\\
    """
    types = tuple(results_types) if results_types is not None else KNOWN_RESULTS_TYPES
    for root in roots:
        if not root:
            continue
        try:
            root.mkdir(parents=True, exist_ok=True)
            for results_type in types:
                folder_name = results_type_folder_name(results_type)
                (root / folder_name).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            alarms.raise_alarm(
                "S1-C1",
                f"Cannot create Results-type folder under {root}",
                cause=str(exc),
                severity="Error",
                show_popup=True,
            )


def sync_results_type_folders_from_catalogue(
    config: AppConfig,
    alarms: AlarmManager,
    results_types: Optional[Sequence[str]] = None,
) -> None:
    """Ensure report roots have a folder for every Results Structure CSV type."""
    types = (
        tuple(results_types)
        if results_types is not None
        else list_results_type_names(config.results_structures)
    )
    if not types:
        types = KNOWN_RESULTS_TYPES
    create_results_type_folder_hierarchy(_report_roots(config), alarms, types)


def ensure_device_report_folders(
    config: AppConfig,
    device_tag: str,
    results_type: str,
    alarms: AlarmManager,
) -> None:
    """Create per-device subfolders under each report root (SPEC Step 1.2)."""
    safe_tag = sanitize_device_tag_for_path(device_tag)
    type_folder = results_type_folder_name(results_type)
    for root in (config.first_run_folder, config.report_output, config.report_mirror):
        if not root:
            continue
        target = root / type_folder / safe_tag
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            alarms.raise_alarm(
                "S1-C2",
                f"Cannot create device report folder for {device_tag}",
                cause=str(exc),
                severity="Warning",
                show_popup=False,
            )


def sync_device_report_folders(
    config: AppConfig,
    devices: Iterable[Tuple[str, str]],
    alarms: AlarmManager,
) -> None:
    """Ensure report subfolders exist for all active devices."""
    seen: set[Tuple[str, str]] = set()
    for device_tag, results_type in devices:
        key = (device_tag, results_type)
        if key in seen:
            continue
        seen.add(key)
        ensure_device_report_folders(config, device_tag, results_type, alarms)


def _report_roots(config: AppConfig) -> List[Path]:
    """Unique report roots (Step 1.2) — avoid duplicate folder trees."""
    roots: List[Path] = []
    for path in (config.first_run_folder, config.report_output, config.report_mirror):
        if not path:
            continue
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved not in roots:
            roots.append(resolved)
    return roots


def persist_deployment_case(config: AppConfig, *, case: int = 1, reason: str = "") -> None:
    """Persist unified mode (always deployment_case = 1) to installation.json and solution.ini."""
    case = 1  # Case 2 removed — never persist a separate HMI mode
    config.deployment_case = case
    marker = _installation_marker(config.first_run_folder)
    payload = _load_installation(marker) or {}
    payload["deployment_case"] = case
    payload["deployment_case_reason"] = reason or "unified_mode"
    payload["deployment_case_changed_utc"] = datetime.now(timezone.utc).isoformat()
    try:
        config.first_run_folder.mkdir(parents=True, exist_ok=True)
        _write_installation(marker, payload)
    except OSError as exc:
        log.warning("Cannot write installation.json for case %s: %s", case, exc)

    ini = config.ini_path
    if not ini.is_file():
        return
    try:
        text = ini.read_text(encoding="utf-8")
        if re.search(r"(?im)^deployment_case\s*=", text):
            text = re.sub(
                r"(?im)^deployment_case\s*=\s*.*$",
                f"deployment_case = {case}",
                text,
                count=1,
            )
        elif re.search(r"(?im)^\[Service\]", text):
            text = re.sub(
                r"(?im)^(\[Service\]\s*)",
                rf"\1deployment_case = {case}\n",
                text,
                count=1,
            )
        else:
            text = f"[Service]\ndeployment_case = {case}\n\n" + text
        ini.write_text(text, encoding="utf-8", newline="\n")
        log.info("Persisted deployment_case=%s to %s (%s)", case, ini, reason or "runtime")
    except OSError as exc:
        log.warning("Cannot update solution.ini deployment_case: %s", exc)


def ensure_desktop_ui_shortcut(config: AppConfig) -> None:
    """
    Ensure a Desktop shortcut ``HIMA Prooftest Report`` that opens the web UI.

    Created on first run (and recreated if missing). Targets
    ``Dev tools/open_graphic_interface.ps1`` so the port comes from ``solution.ini``.
    """
    _ = config
    if sys.platform != "win32":
        return

    solution_root = Path(__file__).resolve().parent.parent
    open_script = solution_root / "Dev tools" / "open_graphic_interface.ps1"
    if not open_script.is_file():
        log.warning("Desktop shortcut skipped — missing %s", open_script)
        return

    desktop = Path.home() / "Desktop"
    if not desktop.is_dir():
        desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    if not desktop.is_dir():
        log.warning("Desktop shortcut skipped — Desktop folder not found")
        return

    lnk = desktop / "HIMA Prooftest Report.lnk"
    if lnk.is_file():
        return

    # JSON strings are safe inside PowerShell -Command.
    lnk_j = json.dumps(str(lnk))
    script_j = json.dumps(str(open_script))
    root_j = json.dumps(str(solution_root))
    ps = f"""
$ErrorActionPreference = 'Stop'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut({lnk_j})
$s.TargetPath = 'powershell.exe'
$s.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ' + {script_j}
$s.WorkingDirectory = {root_j}
$s.Description = 'Open HIMA Prooftest Report web UI (service must be running)'
$s.WindowStyle = 7
$s.Save()
"""
    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if lnk.is_file():
            log.info("Created Desktop shortcut: %s", lnk)
        else:
            detail = (completed.stderr or completed.stdout or "").strip()
            log.warning(
                "Desktop shortcut was not created at %s%s",
                lnk,
                f" ({detail})" if detail else "",
            )
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("Cannot create Desktop UI shortcut: %s", exc)


def ensure_first_run(config: AppConfig, alarms: AlarmManager) -> None:
    """
    First-use station setup: unified mode, marker file, folder hierarchy.

    Called once per service start; mkdir operations are idempotent.
    """
    marker = _installation_marker(config.first_run_folder)
    is_first_run = False

    try:
        config.first_run_folder.mkdir(parents=True, exist_ok=True)
        is_first_run = apply_deployment_case(config, marker)

        catalogue_types = list_results_type_names(config.results_structures) or KNOWN_RESULTS_TYPES
        report_roots = _report_roots(config)
        create_results_type_folder_hierarchy(report_roots, alarms, catalogue_types)

        payload = _load_installation(marker)
        if is_first_run or not payload:
            payload = {
                "version": __version__,
                "station": socket.gethostname(),
                "first_run_utc": datetime.now(timezone.utc).isoformat(),
                "deployment_case": 1,
                "deployment_case_auto_detected": False,
                "operating_mode": "unified",
                "results_type_folders": len(catalogue_types),
            }
            _write_installation(marker, payload)
        else:
            payload["deployment_case"] = 1
            payload["operating_mode"] = "unified"
            payload["last_start_utc"] = datetime.now(timezone.utc).isoformat()
            _write_installation(marker, payload)

        ensure_desktop_ui_shortcut(config)

        log.info(
            "First-run setup complete (unified mode, %d Results-type folders)",
            len(catalogue_types),
        )
    except OSError as exc:
        alarms.raise_alarm(
            "G-02",
            "Cannot create station folders under C:\\HIMA Prooftest Reporting Tool",
            cause=str(exc),
            severity="Error",
            show_popup=True,
        )
        # Still try to place the UI shortcut even if folder setup had issues.
        try:
            ensure_desktop_ui_shortcut(config)
        except Exception:
            pass
