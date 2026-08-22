"""SilworxConnectionService — this tool's API/plugin session only. Never quit SILworX."""

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

from layers.application.catalog_service import CatalogService
from layers.application.errors import STEP_S7
from layers.ports import AlarmPort, SilworxPort

log = logging.getLogger(__name__)


class SilworxConnectionService:
    def __init__(
        self,
        silworx: SilworxPort,
        catalog: CatalogService,
        alarms: AlarmPort,
        *,
        refresh_fn: Optional[Callable[[], None]] = None,
        mark_refresh_busy: Optional[Callable[[], None]] = None,
    ) -> None:
        self.silworx = silworx
        self.catalog = catalog
        self.alarms = alarms
        self._refresh = refresh_fn or (lambda: self.catalog.refresh_catalog())
        self._mark_refresh_busy = mark_refresh_busy

    def close_silworx_connection(self) -> dict:
        if not self.silworx.is_attached():
            return {"silworx": "not connected", "status": "already_disconnected"}
        try:
            self.silworx.detach()
        except Exception as exc:
            try:
                self.silworx.detach()
            except Exception:
                pass
            self.alarms.raise_alarm(STEP_S7, "CloseSilworXconnection", str(exc))
        self._start_refresh_async("CloseSilworXconnection")
        return {"silworx": "not connected", "status": "disconnected", "refresh": "started"}

    def resume_silworx_connection(self) -> dict:
        try:
            self.silworx.attach()
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S7, "ResumeSilworXconnection", str(exc))
            return {"silworx": "not connected", "status": "auth_or_cert_error"}
        if not self.silworx.has_open_project():
            self.alarms.raise_alarm(
                STEP_S7,
                "ResumeSilworXconnection",
                "no open project",
                severity="Warning",
            )
            return {"silworx": "not connected", "status": "no_open_project"}
        # Catalog refresh can take a long time (OPC browse). Do not block Connect HTTP.
        self._start_refresh_async("ResumeSilworXconnection")
        if not self.silworx.is_attached():
            self.alarms.raise_alarm(
                STEP_S7,
                "ResumeSilworXconnection",
                "SILworX project is open but API/plugin attach failed",
                severity="Warning",
            )
            return {
                "silworx": "not connected",
                "status": "attach_failed",
                "refresh": "started",
            }
        return {"silworx": "running", "status": "attached", "refresh": "started"}

    def _start_refresh_async(self, action: str) -> None:
        if self._mark_refresh_busy is not None:
            try:
                self._mark_refresh_busy()
            except Exception:
                pass

        def _run() -> None:
            try:
                self._refresh()
            except Exception as exc:
                log.warning("%s background refresh failed: %s", action, exc)
                try:
                    self.alarms.raise_alarm(STEP_S7, action, str(exc))
                except Exception:
                    pass

        threading.Thread(
            target=_run, daemon=True, name=f"silworx-{action.lower()}-refresh"
        ).start()
