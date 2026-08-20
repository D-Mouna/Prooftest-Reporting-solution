"""QueryService — Presentation calls this, never OPC/SILworX adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from layers.application.errors import STEP_GUI
from layers.domain.device import sort_device_dicts
from layers.ports import AlarmPort, ReportPort, StorePort


class QueryService:
    def __init__(
        self,
        store: StorePort,
        reports: ReportPort,
        alarms: AlarmPort,
        *,
        host: Any = None,
    ) -> None:
        self.store = store
        self.reports = reports
        self.alarms = alarms
        self._host = host

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

    def list_alarms_payload(self) -> dict:
        """GUI alarm list + popup queue."""
        host = self._host
        active_keys: set[str] = set()
        if host is not None:
            try:
                keys = host.alarms.active_error_keys()
                if isinstance(keys, (set, list, tuple, frozenset)):
                    active_keys = set(keys)
            except Exception:
                active_keys = set()
        try:
            alarm_rows = getattr(self.store, "list_recent_alarms", lambda: [])()
        except Exception:
            alarm_rows = []
            if host is not None:
                try:
                    alarm_rows = host.alarms.recent_alarms()
                except Exception:
                    alarm_rows = []
        enriched = []
        for row in alarm_rows:
            item = dict(row)
            key = item.get("error_key") or f"{item.get('step')}|{str(item.get('message') or '')[:120]}"
            acknowledged = bool(item.get("acknowledged"))
            item["error_key"] = key
            item["acknowledged"] = acknowledged
            item["active"] = key in active_keys
            enriched.append(item)
        popups = []
        if host is not None:
            try:
                popups = host.alarms.pop_pending_popups()
            except Exception:
                popups = []
        return {"alarms": enriched, "popups": popups}

    def acknowledge_alarm(self, alarm_id: int) -> Optional[dict]:
        fn = getattr(self.store, "acknowledge_alarm", None)
        row = fn(alarm_id) if callable(fn) else None
        if row and self._host is not None:
            try:
                self._host.alarms.acknowledge_error_key(row.get("error_key") or "")
            except Exception:
                pass
        return row

    def reset_alarms(self) -> None:
        fn = getattr(self.store, "reset_alarms", None)
        if callable(fn):
            fn()
        if self._host is not None:
            try:
                self._host.alarms.reset_all()
            except Exception:
                pass

    def list_running_tests(self) -> list[dict]:
        fn = getattr(self.store, "list_running_tests", None)
        try:
            return list(fn() or []) if callable(fn) else []
        except Exception:
            return []

    def list_test_history(self) -> list[dict]:
        fn = getattr(self.store, "list_test_history", None)
        try:
            return list(fn() or []) if callable(fn) else []
        except Exception:
            return []

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

    def list_archives(self) -> list:
        if self._host is None:
            return []
        from prooftest.annex_list_archive import list_list_archives

        try:
            return list_list_archives(self._host.config)
        except Exception:
            return []

    def create_archive(self) -> dict:
        from prooftest.annex_list_archive import create_list_archive

        return create_list_archive(self._host.db, self._host.config)

    def restore_archive(self, archive_id: str) -> dict:
        from prooftest.annex_list_archive import restore_list_archive

        return restore_list_archive(self._host.db, self._host.config, archive_id)

    def restore_archive_upload(self, path: Path, filename: str) -> dict:
        from prooftest.annex_list_archive import restore_from_uploaded_file

        return restore_from_uploaded_file(self._host.db, self._host.config, path, filename)

    def clear_keep_opc_only(self, *, archive_first: bool = True) -> dict:
        from prooftest.annex_list_archive import clear_keep_opc_only

        return clear_keep_opc_only(self._host.db, self._host.config, archive_first=archive_first)
