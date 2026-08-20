"""Runtime adapters: OpcManager / Database / write_reports / AlarmManager / Case1 → ports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from layers.domain.device import Device
from layers.domain.merger import OpcObservation, SilworxIdentity
from layers.ports import AlarmPort, OpcPort, ReportPort, SilworxPort, StorePort, ArchivePort


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

    def discover_opc_only(
        self,
        known_types: set[str],
        *,
        last_types_by_tag: Optional[dict[str, str]] = None,
    ) -> list[OpcObservation]:
        """Shaped OPC-only discover (CSV shape gate / clear type). Invent scorer is dead."""
        del known_types
        structures = self._structures_fn() or {}
        if not structures:
            return []
        try:
            from layers.domain.opc_discover import (
                discover_shaped_from_tag_lists,
                type_members_from_structures,
            )

            servers = self.discover_servers()
            if not servers:
                return []
            tags_by_server: dict[str, list[str]] = {}
            if hasattr(self._opc, "list_tags_all_servers"):
                tags_by_server = {
                    str(srv): list(tags or [])
                    for srv, tags in (self._opc.list_tags_all_servers(servers) or {}).items()
                }
            else:
                for server in servers:
                    tags_by_server[server] = self.list_tags(server)
            shaped = discover_shaped_from_tag_lists(
                tags_by_server,
                type_members_from_structures(structures),
                last_types_by_tag=last_types_by_tag or {},
            )
            return list(shaped.observations)
        except Exception:
            return []


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
            device.results_type or "",
            opc_server=device.opc_server or None,
            opc_prefix=device.opc_item_prefix or None,
            configuration=device.configuration or None,
            resource=device.resource or None,
            last_running=device.last_running,
            test_in_progress=device.test_in_progress,
            silworx_project=device.project or None,
            device_id=device.device_id.key(),
        )
        setter = getattr(self._db, "set_device_present_on_opc_by_id", None)
        if callable(setter):
            try:
                setter(device.device_id.key(), bool(device.present_on_opc))
            except Exception:
                pass

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


class AnnexListArchiveAdapter:
    """ArchivePort over annex_list_archive — keeps Application free of annex imports."""

    def __init__(self, host: Any) -> None:
        self._host = host

    def list_archives(self) -> list[dict]:
        from prooftest.annex_list_archive import list_list_archives

        try:
            return list(list_list_archives(self._host.config) or [])
        except Exception:
            return []

    def create_archive(self) -> dict:
        from prooftest.annex_list_archive import create_list_archive

        return create_list_archive(self._host.db, self._host.config)

    def restore_archive(self, archive_id: str) -> dict:
        from prooftest.annex_list_archive import restore_list_archive

        return restore_list_archive(self._host.db, self._host.config, archive_id)

    def restore_archive_upload(self, path: object, filename: str) -> dict:
        from pathlib import Path

        from prooftest.annex_list_archive import restore_from_uploaded_file

        return restore_from_uploaded_file(self._host.db, self._host.config, Path(path), filename)

    def clear_keep_opc_only(self, *, archive_first: bool = True) -> dict:
        from prooftest.annex_list_archive import clear_keep_opc_only

        return clear_keep_opc_only(self._host.db, self._host.config, archive_first=archive_first)

    def keep_opc_only_enabled(self) -> bool:
        from prooftest.annex_list_archive import keep_opc_only_enabled

        try:
            return bool(keep_opc_only_enabled(self._host.db))
        except Exception:
            return False


class Case1SyncSilworxAdapter:
    """SilworxPort over SilworxSyncTriggers / Case1SyncTriggers — this tool's session only."""

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
        """Clear suspend, ensure plugin monitor, and attach to a user-open GUI session."""
        self._case1.resume_tool_clients()
        if self._case1.is_tool_attached():
            return True
        try:
            for instance in self._case1.discover_api_instances(force=True) or []:
                api_port = getattr(instance, "api_port", None)
                if api_port is None:
                    continue
                if self._case1._try_attach_gui_session_on_port(int(api_port)):
                    return True
        except Exception:
            pass
        return bool(self._case1.is_tool_attached())

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
_ = (AlarmPort, OpcPort, ReportPort, StorePort, SilworxPort, ArchivePort)
