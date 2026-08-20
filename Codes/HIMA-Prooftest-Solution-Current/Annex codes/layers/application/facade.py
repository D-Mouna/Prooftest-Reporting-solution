"""Application facade — the only door Presentation may call."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from layers.adapters import (
    AlarmManagerAdapter,
    AnnexReportAdapter,
    Case1SyncSilworxAdapter,
    DatabaseStoreAdapter,
    OpcManagerAdapter,
)
from layers.application.catalog_service import CatalogService
from layers.application.engine import Engine
from layers.application.live_test import LiveTestService
from layers.application.query import QueryService
from layers.application.silworx_connection import SilworxConnectionService


class ApplicationFacade:
    """Named use cases from HIMA-Prooftest-Layer-Functions.md."""

    def __init__(self, host: Any) -> None:
        self._host = host
        self.alarm_port = AlarmManagerAdapter(host.alarms)
        self.opc_port = OpcManagerAdapter(host.opc, structures_fn=lambda: getattr(host, "structures", {}) or {})
        self.store_port = DatabaseStoreAdapter(host.db, getattr(host, "structures", {}) or {})
        self.report_port = AnnexReportAdapter(host.config, host.db, self.store_port)
        self.silworx_port = Case1SyncSilworxAdapter(
            host._case1_sync,
            structures_fn=lambda: set((getattr(host, "structures", {}) or {}).keys()),
            project_name_fn=lambda: (
                getattr(host._case1_sync.active_session, "project_name", "")
                if getattr(host._case1_sync, "active_session", None)
                else ""
            ),
        )
        self.catalog = CatalogService(
            self.store_port,
            self.opc_port,
            self.silworx_port,
            self.alarm_port,
            types_folder=getattr(host.config, "results_structures", None),
        )
        self.live = LiveTestService(
            self.opc_port,
            self.store_port,
            self.report_port,
            self.alarm_port,
            defer_complete=True,
        )
        self.query = QueryService(self.store_port, self.report_port, self.alarm_port, host=host)
        self.silworx_conn = SilworxConnectionService(
            self.silworx_port,
            self.catalog,
            self.alarm_port,
            refresh_fn=lambda: host.refresh(manual=True),
        )
        self.engine = Engine(
            self.store_port,
            self.opc_port,
            self.silworx_port,
            self.report_port,
            self.alarm_port,
            self.catalog,
            self.live,
            self.silworx_conn,
            start_workers=lambda: None,
            stop_workers=lambda: None,
            status_fn=lambda: host.health(),
            start_fn=lambda: host.start(),
            stop_fn=lambda: host.request_stop_flags("application_stop"),
            refresh_fn=lambda: host.refresh(manual=True),
        )

    # --- Engine lifecycle ---

    def start_engine(self) -> None:
        self._host.start()

    def stop_engine(self, reason: str = "ui_stop") -> None:
        self._host.request_stop_flags(reason)
        from prooftest.annex_stop_service import perform_graceful_shutdown

        perform_graceful_shutdown(self._host, reason)

    def request_stop_flags(self, reason: str) -> None:
        self._host.request_stop_flags(reason)

    def request_shutdown(self, reason: str, *, exit_process: bool = True) -> None:
        self._host.request_shutdown(reason, exit_process=exit_process)

    def get_engine_status(self) -> dict:
        return self._host.health()

    def refresh_catalog(self) -> dict:
        """RefreshCatalog — Application owns the use case; WorkerHost is the data plane."""
        return self.catalog.run_station_refresh(self._host, manual=True)

    # --- SILworX connection ---

    def close_silworx_connection(self) -> dict:
        result = self.silworx_conn.close_silworx_connection()
        try:
            self._host.db.set_service_state("silworx_api_connected", "0")
            self._host.db.set_service_state("device_list_source", "opc_fallback")
        except Exception:
            pass
        result["engine_running"] = bool(self._host.engine_running)
        return result

    def resume_silworx_connection(self) -> dict:
        result = self.silworx_conn.resume_silworx_connection()
        result["engine_running"] = bool(self._host.engine_running)
        return result

    # --- Queries ---

    def list_devices(self, view: str = "all") -> list:
        if self._host._stopped and not self._host._starting:
            return []
        return self.query.list_devices(view)

    def list_reports(
        self,
        device: str,
        results_type: Optional[str] = None,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list:
        return self.query.list_reports(
            device, results_type, project=project, device_id=device_id
        )

    def open_report(self, path: str) -> tuple[int, Optional[str]]:
        roots = [
            Path(self._host.config.report_output),
            Path(self._host.config.report_mirror),
        ]
        return self.query.open_report(path, roots)

    def list_alarms(self) -> dict:
        return self.query.list_alarms_payload()

    def acknowledge_alarm(self, alarm_id: int) -> Optional[dict]:
        return self.query.acknowledge_alarm(alarm_id)

    def reset_alarms(self) -> None:
        self.query.reset_alarms()

    def list_running_tests(self) -> list:
        return self.query.list_running_tests()

    def list_test_history(self) -> list:
        return self.query.list_test_history()

    # --- List archives (Application use cases) ---

    def list_archives(self) -> list:
        return self.query.list_archives()

    def create_archive(self) -> dict:
        return self.query.create_archive()

    def restore_archive(self, archive_id: str) -> dict:
        return self.query.restore_archive(archive_id)

    def restore_archive_upload(self, path: Path, filename: str) -> dict:
        return self.query.restore_archive_upload(path, filename)

    def clear_keep_opc_only(self, *, archive_first: bool = True) -> dict:
        return self.query.clear_keep_opc_only(archive_first=archive_first)

    @property
    def config(self) -> Any:
        return self._host.config

    @property
    def alarms(self) -> Any:
        return self._host.alarms

    @property
    def engine_running(self) -> bool:
        return bool(self._host.engine_running)

    @property
    def _stopped(self) -> bool:
        return bool(self._host._stopped)

    @property
    def _starting(self) -> bool:
        return bool(self._host._starting)
