"""SilworxConnectionService — this tool's API/plugin session only. Never quit SILworX."""

from __future__ import annotations

from layers.application.catalog_service import CatalogService
from layers.application.errors import STEP_S7
from layers.ports import AlarmPort, SilworxPort


class SilworxConnectionService:
    def __init__(
        self,
        silworx: SilworxPort,
        catalog: CatalogService,
        alarms: AlarmPort,
    ) -> None:
        self.silworx = silworx
        self.catalog = catalog
        self.alarms = alarms

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
        self.catalog.refresh_catalog()
        return {"silworx": "not connected", "status": "disconnected"}

    def resume_silworx_connection(self) -> dict:
        try:
            attached = self.silworx.attach()
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S7, "ResumeSilworXconnection", str(exc))
            return {"silworx": "not connected", "status": "auth_or_cert_error"}
        if not attached or not self.silworx.has_open_project():
            self.alarms.raise_alarm(
                STEP_S7,
                "ResumeSilworXconnection",
                "no open project",
                severity="Warning",
            )
            return {"silworx": "not connected", "status": "no_open_project"}
        self.catalog.refresh_catalog()
        return {"silworx": "running", "status": "attached"}
