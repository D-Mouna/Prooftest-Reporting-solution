from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from typing import List, Optional

from prooftest.config import AppConfig

log = logging.getLogger(__name__)

# Seconds to wait after SILworX close before killing leftover c3.exe.
_SILWORX_CLOSE_GRACE_SEC = 8.0


@dataclass(frozen=True)
class C3Process:
    pid: int
    name: str
    command_line: str = ""


@dataclass(frozen=True)
class CleanupResult:
    killed: List[str]
    skipped: List[str]

    @property
    def changed(self) -> bool:
        return bool(self.killed)


def close_grace_sec() -> float:
    return _SILWORX_CLOSE_GRACE_SEC


def _query_processes(name_pattern: str) -> List[dict]:
    ps_cmd = (
        "Get-CimInstance Win32_Process | "
        f"Where-Object {{ $_.Name -match '{name_pattern}' }} | "
        "Select-Object ProcessId,Name,CommandLine | "
        "ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        log.debug("Process query returned invalid JSON for pattern %s", name_pattern)
        return []

    rows = payload if isinstance(payload, list) else [payload]
    return [row for row in rows if isinstance(row, dict)]


def list_c3_processes() -> List[C3Process]:
    """Return running c3.exe processes only."""
    procs: List[C3Process] = []
    for row in _query_processes("^c3"):
        name = str(row.get("Name") or "")
        if name.lower() != "c3.exe":
            continue
        try:
            pid = int(row.get("ProcessId"))
        except (TypeError, ValueError):
            continue
        procs.append(
            C3Process(
                pid=pid,
                name=name,
                command_line=str(row.get("CommandLine") or ""),
            )
        )
    return procs


def has_olixclient() -> bool:
    """True when the SILworX GUI helper (OLixClient.exe) is running."""
    return bool(_query_processes("^OLixClient"))


def is_silworx_session_active(*, silworx_open: bool) -> bool:
    """
    True when SILworX is open or its GUI is running.

    Uses lock.ini (project open) and OLixClient.exe — not the REST API.
    During startup c3.exe may already exist while both signals are still false;
    that phase is treated as opening and must never trigger c3.exe cleanup.
    """
    return silworx_open or has_olixclient()


def should_kill_c3_after_close(
    *,
    session_was_active: bool,
    session_active: bool,
    close_detected_at: Optional[float],
    now: float,
    grace_sec: float = _SILWORX_CLOSE_GRACE_SEC,
) -> bool:
    """
    True only after a confirmed SILworX close (session was active, now inactive)
    and the grace period has elapsed.
    """
    if session_active or not session_was_active:
        return False
    if close_detected_at is None:
        return False
    if now - close_detected_at < grace_sec:
        return False
    return bool(list_c3_processes())


def kill_leftover_c3_after_close(config: AppConfig, *, force: bool = True) -> CleanupResult:
    """Terminate leftover c3.exe processes after confirmed SILworX close (G-20)."""
    del config

    killed: List[str] = []
    skipped: List[str] = []
    targets = list_c3_processes()
    if not targets:
        return CleanupResult(killed=[], skipped=[])

    log.warning(
        "SILworX closed — terminating %d leftover c3.exe process(es): %s",
        len(targets),
        ", ".join(f"c3.exe:{p.pid}" for p in targets),
    )
    for proc in targets:
        cmd = ["taskkill", "/PID", str(proc.pid), "/T"]
        if force:
            cmd.append("/F")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        proc_label = f"c3.exe:{proc.pid}"
        if result.returncode == 0:
            killed.append(proc_label)
        else:
            skipped.append(proc_label)

    if killed:
        log.warning("c3.exe cleanup complete: %s", ", ".join(killed))
    if skipped:
        log.warning("c3.exe cleanup failed for: %s", ", ".join(skipped))
    return CleanupResult(killed=killed, skipped=skipped)
