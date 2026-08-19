"""Step codes and last-error mapping at the Application boundary."""

from __future__ import annotations

from typing import Optional

STEP_S1 = "S1"
STEP_S2 = "S2"
STEP_S3 = "S3"
STEP_S4 = "S4"
STEP_S5 = "S5"
STEP_S6 = "S6"
STEP_S7 = "S7"
STEP_GUI = "GUI"


class RecordingAlarmPort:
    """In-memory AlarmPort for tests and Engine.last_error."""

    def __init__(self) -> None:
        self.alarms: list[dict] = []
        self._last: Optional[dict] = None

    def raise_alarm(
        self,
        step: str,
        action: str,
        message: str,
        *,
        device_tag: Optional[str] = None,
        severity: str = "Error",
    ) -> None:
        rec = {
            "step": step,
            "action": action,
            "message": message,
            "device_tag": device_tag,
            "severity": severity,
        }
        self.alarms.append(rec)
        self._last = {"step": step, "action": action, "message": message}

    def last_error(self) -> Optional[dict]:
        return dict(self._last) if self._last else None
