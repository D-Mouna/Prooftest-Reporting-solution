from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

ACTIVE_WINDOW_SEC = 60.0


DIAGNOSTICS: Dict[str, Dict[str, str]] = {
    "G-02": {
        "step": "G-02",
        "title": "Cannot create first-run folder",
        "solution": "Grant write access to C:\\; free disk space; check antivirus.",
    },
    "G-11": {
        "step": "G-11",
        "title": "SILworX uninstall — continuing with OPC device list",
        "solution": "Report Solution keeps running and updates the device list via X-OPC. After reinstalling SILworX, restart the engine (or wait for API health) to resume API discovery.",
    },
    "P1": {
        "step": "P1",
        "title": "Database creation or connection failed",
        "solution": "Start SQL Server; verify solution.ini server name and login.",
    },
    "P1-C1": {
        "step": "P1-C1",
        "title": "SILworX project not available",
        "solution": "Update project path; close SILworX lock; complete code generation.",
    },
    "P1-C2": {
        "step": "P1-C2",
        "title": "SQL template folder missing",
        "solution": "Ensure CSVs exist under C:\\HIMA Prooftest Reporting Tool\\Results Structures (seeded from package; set results_structures in solution.ini).",
    },
    "P2-C1": {
        "step": "P2-C1",
        "title": "Device list sync failed",
        "solution": "Open the SILworX project in the GUI to use API discovery, or leave it closed — the tool will scan X-OPC for devices. The report tool never opens a SILworX project itself.",
    },
    "P3-C1": {
        "step": "P3-C1",
        "title": "No Prooftest Results globals in SILworX API",
        "solution": "Add globals typed with *_Results structures; run code generation; Save project.",
    },
    "P2-C2": {
        "step": "P2-C2",
        "title": "No devices matched in OPC",
        "solution": "Verify X-OPC service; confirm tags deployed; check branch filter.",
    },
    "S2-C1": {
        "step": "S2-C1",
        "title": "SILworX API — no user-open project",
        "solution": "Open the project in the SILworX GUI to update the device list via API. If no project is open, the tool scans X-OPC instead. The report tool never opens a SILworX project.",
    },
    "S2-C2": {
        "step": "S2-C2",
        "title": "SILworX API connection or session failed",
        "solution": "Ensure SILworX is running; verify api_port and api_cert.pem in solution.ini match the active SILworX instance.",
    },
    "S1-C1": {
        "step": "S1-C1",
        "title": "Cannot create Results-type report folder",
        "solution": "Grant write access on C:\\ and Z:\\ report paths; free disk space.",
    },
    "S1-C2": {
        "step": "S1-C2",
        "title": "Cannot create device report subfolder",
        "solution": "Sanitize Device_TAG for invalid path characters; check permissions.",
    },
    "P3": {
        "step": "P3",
        "title": "OPC server or read error",
        "solution": "Start X-OPC service; use 32-bit Python; register OPCDAAuto.dll.",
    },
    "P4": {
        "step": "P4",
        "title": "Snapshot or INSERT failed",
        "solution": "Re-run schema sync; verify CSV/template column mapping.",
    },
    "P4.4": {
        "step": "P4.4",
        "title": "Parallel report staging failed",
        "solution": "Free disk space; solution will process results sequentially.",
    },
    "P5": {
        "step": "P5",
        "title": "Report generation failed",
        "solution": "Check report output path permissions; validate HTML template.",
    },
    "P6": {
        "step": "P6",
        "title": "Web server error",
        "solution": "Change web port in solution.ini; ensure service is running.",
    },
}


@dataclass
class AlarmRecord:
    timestamp: datetime
    severity: str
    step: str
    device_tag: Optional[str]
    message: str
    solution_hint: str
    error_key: str
    acknowledged: bool = False


def alarm_error_key(step: str, message: Optional[str]) -> str:
    return f"{step}|{(message or '')[:120]}"


class AlarmManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._alarms: List[AlarmRecord] = []
        self._shown_keys: Set[str] = set()
        self._pending_popups: List[Dict[str, Any]] = []
        self._last_seen: Dict[str, float] = {}
        self._persist_callback: Optional[Callable[[AlarmRecord], None]] = None

    def set_persist_callback(self, callback: Callable[[AlarmRecord], None]) -> None:
        self._persist_callback = callback

    def raise_alarm(
        self,
        step: str,
        message: str,
        *,
        severity: str = "Error",
        device_tag: Optional[str] = None,
        cause: Optional[str] = None,
        show_popup: bool = True,
    ) -> None:
        diag = DIAGNOSTICS.get(step, {})
        solution = diag.get("solution", "See specification troubleshooting catalog.")
        if cause:
            message = f"{message} — {cause}"
        error_key = alarm_error_key(step, message)
        record = AlarmRecord(
            timestamp=datetime.now(),
            severity=severity,
            step=step,
            device_tag=device_tag,
            message=message,
            solution_hint=solution,
            error_key=error_key,
        )
        with self._lock:
            self._alarms.append(record)
            self._last_seen[error_key] = time.monotonic()
            if show_popup and error_key not in self._shown_keys:
                self._shown_keys.add(error_key)
                self._pending_popups.append(
                    {
                        "step": step,
                        "title": diag.get("title", step),
                        "message": message,
                        "solution": solution,
                        "device_tag": device_tag,
                        "timestamp": record.timestamp.isoformat(),
                    }
                )

        if self._persist_callback is not None:
            try:
                self._persist_callback(record)
            except Exception:
                pass

    def clear_shown_on_refresh(self) -> None:
        with self._lock:
            self._shown_keys.clear()

    def pop_pending_popups(self) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._pending_popups)
            self._pending_popups.clear()
            return items

    def recent_alarms(self, limit: int = 50) -> List[Dict[str, Any]]:
        active_keys = self.active_error_keys()
        with self._lock:
            rows = self._alarms[-limit:]
        return [
            {
                "timestamp": a.timestamp.isoformat(),
                "severity": a.severity,
                "step": a.step,
                "device_tag": a.device_tag,
                "message": a.message,
                "solution_hint": a.solution_hint,
                "error_key": a.error_key,
                "acknowledged": a.acknowledged,
                "active": a.error_key in active_keys,
            }
            for a in reversed(rows)
        ]

    def active_error_keys(self) -> Set[str]:
        now = time.monotonic()
        with self._lock:
            return {
                key
                for key, seen in self._last_seen.items()
                if now - seen <= ACTIVE_WINDOW_SEC
            }

    def acknowledge_error_key(self, error_key: str) -> None:
        with self._lock:
            for alarm in self._alarms:
                if alarm.error_key == error_key:
                    alarm.acknowledged = True

    def reset_all(self) -> None:
        with self._lock:
            for alarm in self._alarms:
                alarm.acknowledged = True
            self._last_seen.clear()
            self._shown_keys.clear()
            self._pending_popups.clear()
