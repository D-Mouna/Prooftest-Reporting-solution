"""QueryService — Presentation calls this, never OPC/SILworX adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from layers.application.errors import STEP_GUI
from layers.domain.device import sort_device_dicts
from layers.ports import AlarmPort, ReportPort, StorePort


class QueryService:
    def __init__(self, store: StorePort, reports: ReportPort, alarms: AlarmPort) -> None:
        self.store = store
        self.reports = reports
        self.alarms = alarms

    def list_devices(self, view: str = "all") -> list[dict]:
        try:
            rows = self.store.list_devices(view)
        except Exception as exc:
            self.alarms.raise_alarm("S3", "ListDevices", str(exc))
            return []
        for row in rows:
            row.setdefault("project", row.get("silworx_project") or "")
            row.setdefault("opc_server", row.get("opc_server") or "")
            row.setdefault("configuration", row.get("configuration") or "")
            row.setdefault("resource", row.get("resource") or "")
            row.setdefault("opc_item_prefix", row.get("opc_item_prefix") or "")
            row.setdefault("present_on_opc", bool(row.get("present_on_opc")))
            row.setdefault("test_in_progress", bool(row.get("test_in_progress")))
        return sort_device_dicts(rows)

    def list_reports(
        self,
        device_tag: str,
        results_type: Optional[str] = None,
        *,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list[dict]:
        return self.reports.list_for_device(
            device_tag,
            results_type,
            project=project,
            device_id=device_id,
        )

    def list_alarms(self) -> list[dict]:
        rec = getattr(self.alarms, "alarms", [])
        return list(rec) if isinstance(rec, list) else []

    def open_report(self, path: str, allowed_roots: list[Path]) -> tuple[int, Optional[str]]:
        file_path = Path(path).resolve()
        if not any(str(file_path).startswith(str(root.resolve())) for root in allowed_roots):
            self.alarms.raise_alarm(
                STEP_GUI, "OpenReport", "Path outside report root", severity="Error"
            )
            return 403, None
        if not file_path.exists():
            return 404, None
        return 200, str(file_path)
