"""In-memory .Running edge detection. SQL is not updated every poll cycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class EdgeEvent:
    kind: str  # started | ended | flicker | interrupted | none
    device_id: str
    running: bool = False


class RunningEdgeDetector:
    def __init__(self) -> None:
        self._last: dict[str, bool] = {}
        self._in_progress: dict[str, bool] = {}

    def observe(
        self,
        device_id: str,
        running: Optional[bool],
        *,
        quality_good: bool = True,
        present_on_opc: bool = True,
    ) -> EdgeEvent:
        in_progress = self._in_progress.get(device_id, False)
        if in_progress and (not present_on_opc or running is None or not quality_good):
            self._in_progress[device_id] = False
            self._last[device_id] = False
            return EdgeEvent("interrupted", device_id, False)

        if running is None:
            return EdgeEvent("none", device_id, False)

        prev = self._last.get(device_id, False)
        if not prev and running:
            self._last[device_id] = True
            self._in_progress[device_id] = True
            return EdgeEvent("started", device_id, True)
        if prev and not running:
            return EdgeEvent("ended", device_id, False)
        self._last[device_id] = bool(running)
        return EdgeEvent("none", device_id, bool(running))

    def confirm_ended(self, device_id: str, still_running: bool) -> EdgeEvent:
        if still_running:
            self._last[device_id] = True
            self._in_progress[device_id] = True
            return EdgeEvent("flicker", device_id, True)
        self._last[device_id] = False
        self._in_progress[device_id] = False
        return EdgeEvent("ended", device_id, False)

    def is_in_progress(self, device_id: str) -> bool:
        return bool(self._in_progress.get(device_id))

    def prime(
        self,
        device_id: str,
        last_running: Optional[bool],
        in_progress: bool = False,
    ) -> None:
        """Seed from SQL on restart. Does not overwrite an already-observed DeviceId."""
        if device_id in self._last:
            return
        self._last[device_id] = bool(last_running)
        self._in_progress[device_id] = bool(in_progress)
