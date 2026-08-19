"""Engine: StartEngine / StopEngine / GetEngineStatus. Workers are injectable no-ops in tests."""

from __future__ import annotations

from typing import Callable, Optional

from layers.application.catalog_service import CatalogService
from layers.application.errors import STEP_S1, STEP_S2
from layers.application.live_test import LiveTestService
from layers.application.silworx_connection import SilworxConnectionService
from layers.ports import AlarmPort, OpcPort, ReportPort, SilworxPort, StorePort


class Engine:
    def __init__(
        self,
        store: StorePort,
        opc: OpcPort,
        silworx: SilworxPort,
        reports: ReportPort,
        alarms: AlarmPort,
        catalog: CatalogService,
        live: LiveTestService,
        silworx_conn: Optional[SilworxConnectionService] = None,
        *,
        start_workers: Optional[Callable[[], None]] = None,
        stop_workers: Optional[Callable[[], None]] = None,
    ) -> None:
        self.store = store
        self.opc = opc
        self.silworx = silworx
        self.reports = reports
        self.alarms = alarms
        self.catalog = catalog
        self.live = live
        self.silworx_conn = silworx_conn or SilworxConnectionService(silworx, catalog, alarms)
        self._start_workers = start_workers or (lambda: None)
        self._stop_workers = stop_workers or (lambda: None)
        self.engine_state = "stopped"
        self.workers_started = False

    def start_engine(self) -> str:
        self.engine_state = "starting"
        try:
            self.store.ensure_folders()
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S1, "StartEngine", str(exc))
            self.engine_state = "stopped"
            return self.engine_state
        try:
            self.store.connect()
        except Exception as first:
            self.alarms.raise_alarm(
                STEP_S2, "StartEngine", f"SQL Server down, trying SQLite: {first}", severity="Warning"
            )
            try:
                self.store.connect()
            except Exception as exc:
                self.alarms.raise_alarm(STEP_S2, "StartEngine", str(exc))
                self.engine_state = "stopped"
                return self.engine_state
        self.catalog.load_result_types()
        try:
            self._start_workers()
            self.workers_started = True
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S1, "StartEngine", f"workers: {exc}")
        try:
            self.catalog.refresh_catalog()
        except Exception as exc:
            self.alarms.raise_alarm("S3", "StartEngine", str(exc))
        self.engine_state = "running"
        return self.engine_state

    def stop_engine(self) -> str:
        try:
            self._stop_workers()
        except Exception:
            pass
        self.workers_started = False
        try:
            self.silworx.detach()
        except Exception:
            pass
        self.engine_state = "stopped"
        return self.engine_state

    def get_engine_status(self) -> dict:
        try:
            servers = self.opc.discover_servers()
        except Exception as exc:
            self.alarms.raise_alarm("S4", "GetEngineStatus", str(exc), severity="Warning")
            servers = []
        silworx_badge = "running" if self.silworx.is_attached() else "not connected"
        return {
            "engine": self.engine_state,
            "opc_count": len(servers),
            "device_count": len(self.catalog.devices),
            "queue_depth": self.live.queue_depth,
            "silworx": silworx_badge,
            "last_error": self.alarms.last_error(),
        }
