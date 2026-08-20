"""Runtime adapters: OpcManager / Database / write_reports / AlarmManager / Case1 → ports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from layers.domain.device import Device
from layers.domain.merger import OpcObservation, SilworxIdentity
from layers.ports import AlarmPort, OpcPort, ReportPort, SilworxPort, StorePort


def _structure_to_sql_table(results_type: str) -> str:
    from prooftest.results_csv import structure_to_sql_table

    return structure_to_sql_table(results_type)


class AlarmManagerAdapter:
    def __init__(self, alarms: Any) -> None:
        self._alarms = alarms

    def raise_alarm(
        self,
        step: str,
        action: str,
        message: str,
        *,
        device_tag: Optional[str] = None,
        severity: str = "Error",
    ) -> None:
        self._alarms.raise_alarm(
            step,
            message,
            device_tag=device_tag,
            action=action,
            severity=severity,
        )

    def last_error(self) -> Optional[dict]:
        fn = getattr(self._alarms, "last_error", None)
        return fn() if callable(fn) else None


class OpcManagerAdapter:
    def __init__(
        self,
        opc: Any,
        *,
        structures_fn: Optional[Callable[[], dict]] = None,
    ) -> None:
        self._opc = opc
        self._structures_fn = structures_fn or (lambda: {})

    def discover_servers(self) -> list[str]:
        return list(self._opc.discover_servers()) if hasattr(self._opc, "discover_servers") else []

    def list_tags(self, server: str) -> list[str]:
        if hasattr(self._opc, "list_all_tags"):
            return list(self._opc.list_all_tags(server) or [])
        return []

    def find_running_path(self, server: str, device_tag: str) -> Optional[str]:
        if hasattr(self._opc, "find_running_path"):
            return self._opc.find_running_path(server, device_tag)
        return None

    def read_running(self, server: str, item_id: str) -> tuple[Optional[bool], str]:
        read_map = self._opc.read_values(server, [item_id])
        value, quality = read_map.get(item_id, (None, "Bad"))
        if str(quality).lower() != "good":
            return None, str(quality)
        if value is None:
            return None, str(quality)
        return bool(value), str(quality)

    def discover_opc_only(self, known_types: set[str]) -> list[OpcObservation]:
        del known_types
        structures = self._structures_fn() or {}
        if not structures:
            return []
        try:
            from prooftest.step03_device_list import discover_devices_from_opc

            found = discover_devices_from_opc(self._opc, structures)
        except Exception:
            return []
        return [
            OpcObservation(
                device_tag=device_tag,
                opc_server=server,
                opc_item_prefix=prefix,
                results_type=results_type,
                running_item=f"{prefix}.Running",
            )
            for device_tag, results_type, server, prefix in found
        ]


class DatabaseStoreAdapter:
    def __init__(self, db: Any, structures: dict) -> None:
        self._db = db
        self._structures = structures
        self.last_table: Optional[str] = None
        self.last_record_id: Optional[int] = None

    def ensure_folders(self) -> None:
        return None

    def connect(self) -> str:
        return "sqlite" if getattr(self._db, "using_sqlite", True) else "sqlserver"

    def upsert_device(self, device: Device) -> None:
        self._db.upsert_device(
            device.device_tag,
            device.results_type,
            opc_server=device.opc_server or None,
            opc_prefix=device.opc_item_prefix or None,
            configuration=device.configuration or None,
            resource=device.resource or None,
            last_running=device.last_running,
            test_in_progress=device.test_in_progress,
            silworx_project=device.project or None,
            device_id=device.device_id.key(),
        )

    def list_devices(self, view: str = "all") -> list[dict]:
        return self._db.list_devices(view)

    def reconcile(self, active_ids: list[str]) -> None:
        self._db.reconcile_device_list(active_ids)

    def mark_inactive(self, device_id: str) -> None:
        self._db.reconcile_device_list([])

    def insert_snapshot(self, device_tag: str, results_type: str, snapshot: dict, **kwargs) -> int:
        table = _structure_to_sql_table(results_type)
        record_id = self._db.insert_snapshot(
            table,
            device_tag,
            snapshot,
            opc_server=kwargs.get("opc_server"),
            sequence=kwargs.get("sequence"),
        )
        self.last_table = table
        self.last_record_id = record_id
        return record_id

    def snapshots_for(self, device_tag: str) -> list[dict]:
        return []

    def start_test(self, device_tag: str, results_type: str) -> None:
        self._db.start_test_history(device_tag, results_type)

    def finish_test(self, device_tag: str, outcome: str, result: str = "") -> None:
        self._db.finish_open_test_history(device_tag, outcome, result or None)

    def list_running_tests(self) -> list[dict]:
        return list(self._db.list_running_tests() or [])

    def list_test_history(self) -> list[dict]:
        return list(self._db.list_test_history() or [])

    def list_recent_alarms(self) -> list[dict]:
        return list(self._db.list_recent_alarms() or [])

    def acknowledge_alarm(self, alarm_id: int) -> Optional[dict]:
        return self._db.acknowledge_alarm(alarm_id)

    def reset_alarms(self) -> None:
        self._db.reset_alarms()


class AnnexReportAdapter:
    def __init__(self, config: Any, db: Any, store: DatabaseStoreAdapter) -> None:
        self._config = config
        self._db = db
        self._store = store

    def write(
        self,
        device_tag: str,
        results_type: str,
        snapshot: dict,
        *,
        quality_notes: Optional[list[str]] = None,
        project: str = "",
    ) -> Optional[str]:
        from prooftest.annex_pdf_generation import write_reports

        paths = write_reports(
            self._config,
            device_tag,
            results_type,
            snapshot,
            quality_notes=quality_notes,
            project=project or "",
        )
        if paths and self._store.last_table is not None and self._store.last_record_id:
            try:
                self._db.update_report_path(
                    self._store.last_table, self._store.last_record_id, paths[0]
                )
            except Exception:
                pass
        return paths[0] if paths else None

    def list_for_device(
        self,
        device_tag: str,
        results_type: Optional[str] = None,
        *,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list[dict]:
        from prooftest.annex_pdf_generation import list_reports_for_device

        return list_reports_for_device(
            Path(self._config.report_output),
            device_tag,
            results_type=results_type,
            project=project,
            device_id=device_id,
        )

    def resolve_open_path(self, path: str) -> Optional[str]:
        return path


class Case1SyncSilworxAdapter:
    """SilworxPort over Case1SyncTriggers — this tool's session only."""

    def __init__(
        self,
        case1: Any,
        *,
        structures_fn: Optional[Callable[[], set[str]]] = None,
        project_name_fn: Optional[Callable[[], str]] = None,
    ) -> None:
        self._case1 = case1
        self._structures_fn = structures_fn or (lambda: set())
        self._project_name_fn = project_name_fn or (lambda: "")

    def is_attached(self) -> bool:
        return bool(self._case1.is_tool_attached())

    def attach(self) -> bool:
        self._case1.resume_tool_clients()
        return bool(self._case1.is_tool_attached()) or not self._case1.is_api_suspended()

    def detach(self) -> None:
        self._case1.detach_tool_clients()

    def has_open_project(self) -> bool:
        if self._case1.is_tool_attached():
            return True
        try:
            sessions = self._case1.refresh_open_sessions()
            return bool(sessions)
        except Exception:
            return False

    def list_identities(self, known_types: set[str]) -> list[SilworxIdentity]:
        types = known_types or self._structures_fn()
        if not types:
            return []
        try:
            from prooftest.step03_device_list import try_discover_devices_via_api

            class _Quiet:
                def raise_alarm(self, *args, **kwargs):
                    return None

            devices = try_discover_devices_via_api(self._case1, set(types), _Quiet())
        except Exception:
            devices = None
        if not devices:
            return []
        project = self._project_name_fn() or ""
        rows: list[SilworxIdentity] = []
        for d in devices:
            rows.append(
                SilworxIdentity(
                    project=d.silworx_project or project,
                    configuration=d.configuration or "",
                    resource=d.resource or "",
                    device_tag=d.device_tag,
                    results_type=d.results_type,
                )
            )
        return rows


# Protocol checks for static analysis / tests
_ = (AlarmPort, OpcPort, ReportPort, StorePort, SilworxPort)
