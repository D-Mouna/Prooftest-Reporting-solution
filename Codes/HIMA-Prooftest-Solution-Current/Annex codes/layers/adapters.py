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
        shape_gate_ratio: float = 0.5,
        shape_gate_floor: int = 3,
    ) -> None:
        self._opc = opc
        self._structures_fn = structures_fn or (lambda: {})
        self._shape_gate_ratio = float(shape_gate_ratio)
        self._shape_gate_floor = int(shape_gate_floor)

    def discover_servers(self) -> list[str]:
        return list(self._opc.discover_servers()) if hasattr(self._opc, "discover_servers") else []

    def list_tags(self, server: str) -> list[str]:
        if hasattr(self._opc, "list_all_tags"):
            return list(self._opc.list_all_tags(server) or [])
        return []

    def list_tags_all_servers(self, servers: Optional[list[str]] = None) -> dict[str, list[str]]:
        """Browse ProofTest tags into cache for every server (used by bind_opc_paths)."""
        if hasattr(self._opc, "list_tags_all_servers"):
            raw = self._opc.list_tags_all_servers(servers)
            return {str(srv): list(tags or []) for srv, tags in (raw or {}).items()}
        out: dict[str, list[str]] = {}
        for server in servers or self.discover_servers():
            out[str(server)] = self.list_tags(str(server))
        return out

    def invalidate_tag_cache(self) -> None:
        inval = getattr(self._opc, "invalidate_tag_cache", None)
        if callable(inval):
            inval()
            return
        if hasattr(self._opc, "invalidate_cache"):
            self._opc.invalidate_cache()

    def find_running_path(self, server: str, device_tag: str) -> Optional[str]:
        if hasattr(self._opc, "find_running_path"):
            return self._opc.find_running_path(server, device_tag)
        return None

    def read_running(self, server: str, item_id: str) -> tuple[Optional[bool], str]:
        read_map = self._opc.read_values(server, [item_id])
        value, quality = read_map.get(item_id, (None, "Bad"))
        quality_text = str(quality or "Bad")
        ok = quality_text.lower() == "good"
        mark = getattr(self._opc, "mark_live_quality", None)
        if callable(mark):
            try:
                mark(server, ok, quality_text)
            except Exception:
                pass
        if not ok:
            return None, quality_text
        if value is None:
            return None, quality_text
        return bool(value), quality_text

    def server_live_ok(self, server: str) -> Optional[bool]:
        fn = getattr(self._opc, "server_live_ok", None)
        if callable(fn):
            return fn(server)
        return None

    def recheck_server_live(
        self, server: str, running_item: Optional[str] = None
    ) -> Optional[bool]:
        fn = getattr(self._opc, "recheck_server_live", None)
        if callable(fn):
            return fn(server, running_item)
        return self.server_live_ok(server)

    def mark_live_quality(self, server: str, ok: bool, quality: str = "") -> None:
        fn = getattr(self._opc, "mark_live_quality", None)
        if callable(fn):
            fn(server, ok, quality)

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
                gate_n=self._shape_gate_floor,
                gate_ratio=self._shape_gate_ratio,
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
        structure = (self._structures or {}).get(results_type)
        filtered = {k: v for k, v in snapshot.items() if not str(k).startswith("_")}
        if structure is not None:
            from prooftest.results_csv import member_to_column

            allowed = {
                member_to_column(f"{structure.type_name}.{name}", structure.type_name)
                for name in structure.member_short_names()
            }
            allowed.update(
                {
                    "Device_TAG",
                    "OPC_Server",
                    "CollectedAt",
                    "SequenceInBatch",
                    "ReportPath",
                    "Error_code",
                    "Error_Code",
                    "Installation_direction",
                    "Assigned_current_output",
                    "Current_span",
                    "Output_mode",
                    "value_4_mA",
                    "value_20_mA",
                    "Damping",
                    "Failure_mode",
                    "Medium",
                    "Gas_type",
                    "Reference_sound_velocity",
                    "Temperature_coefficient",
                    "Partially_filled_pipe_detection",
                    "Low_value_partial_filled_pipe_detection",
                    "High_value_partial_filled_pipe_detection",
                    "Maximum_damping_partial_filled_pipe_detection",
                    "Assigned_low_flow_cutoff",
                    "Off_value_low_flow_cutoff",
                    "On_value_low_flow_cutoff",
                    "Pressure_shock_suppression",
                    "Pressure_compensation",
                    "Pressure_value",
                    "Zero_point",
                    "Serial_number",
                    "Device_tag",
                    "Device_tag_long",
                    "HIMA_system_tag",
                    "Test_starttime",
                    "Test_endtime",
                    "Alarm_selection",
                    "Transfer_function",
                    "Lower_range_value",
                    "Upper_range_value",
                    "Damping_value",
                    "Transmitter_units_code",
                    "HBSI_value",
                    "HBSI_result",
                    "Heartbeat_verif_result",
                    "Device_status",
                    "Device_type_extended",
                }
            )
            filtered = {k: v for k, v in filtered.items() if k in allowed}
        try:
            record_id = self._db.insert_snapshot(
                table,
                device_tag,
                filtered,
                opc_server=kwargs.get("opc_server"),
                sequence=kwargs.get("sequence"),
            )
        except Exception:
            # CSV-only tables may lack HIMA flattened columns — retry with Results members only.
            if structure is not None:
                from prooftest.results_csv import member_to_column

                member_cols = {
                    member_to_column(f"{structure.type_name}.{name}", structure.type_name)
                    for name in structure.member_short_names()
                }
                member_cols.update({"Device_TAG", "OPC_Server", "CollectedAt", "SequenceInBatch", "ReportPath"})
                slim = {k: v for k, v in filtered.items() if k in member_cols}
                record_id = self._db.insert_snapshot(
                    table,
                    device_tag,
                    slim,
                    opc_server=kwargs.get("opc_server"),
                    sequence=kwargs.get("sequence"),
                )
            else:
                raise
        self.last_table = table
        self.last_record_id = record_id
        return record_id

    def snapshot_table_for(self, results_type: str) -> str:
        return _structure_to_sql_table(results_type)

    def update_report_path(self, table: str, record_id: int, report_path: str) -> None:
        self._db.update_report_path(table, record_id, report_path)

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
        snapshot_table: Optional[str] = None,
        record_id: Optional[int] = None,
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
        table = snapshot_table or self._store.last_table
        rid = record_id if record_id is not None else self._store.last_record_id
        if paths and table is not None and rid:
            try:
                self._db.update_report_path(table, int(rid), paths[0])
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
        """Clear suspend, ensure plugin monitor, and attach every reachable GUI session."""
        self._case1.resume_tool_clients()
        attached_any = bool(self._case1.is_tool_attached())
        try:
            for instance in self._case1.discover_api_instances(force=True) or []:
                api_port = getattr(instance, "api_port", None)
                if api_port is None:
                    continue
                # Skip ports whose plugin already has no listener after a short probe.
                try:
                    if self._case1._try_attach_gui_session_on_port(int(api_port)):
                        attached_any = True
                except Exception as exc:
                    log = __import__("logging").getLogger(__name__)
                    log.warning("Attach on API %s failed: %s", api_port, exc)
        except Exception:
            pass
        return attached_any or bool(self._case1.is_tool_attached())

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
