"""CatalogService: LoadResultTypes, RefreshCatalog, BindOpcPaths, DiscoverOpcOnly, ReconcileCatalog."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from layers.application.errors import STEP_S3, STEP_S4
from layers.domain.device import Device, device_from_row, sort_devices
from layers.domain.merger import CatalogMerger, OpcObservation, SilworxIdentity
from layers.domain.opc_discover import type_members_from_structures
from layers.domain.result_types import ResultType, ResultTypeCatalog
from layers.ports import AlarmPort, ArchivePort, OpcPort, SilworxPort, StorePort

OTS_BRANCH = "OTS ProofTest"
OPC_BRANCH = "OPC ProofTest"

log = logging.getLogger(__name__)


class CatalogService:
    def __init__(
        self,
        store: StorePort,
        opc: OpcPort,
        silworx: SilworxPort,
        alarms: AlarmPort,
        *,
        types_folder: Optional[Path] = None,
        merger: Optional[CatalogMerger] = None,
        archive: Optional[ArchivePort] = None,
    ) -> None:
        self.store = store
        self.opc = opc
        self.silworx = silworx
        self.alarms = alarms
        self.types_folder = types_folder
        self.merger = merger or CatalogMerger()
        self.archive = archive
        self.types = ResultTypeCatalog()
        self.devices: list[Device] = []

    def load_result_types(self, folder: Optional[Path] = None) -> ResultTypeCatalog:
        path = folder or self.types_folder
        if path is None:
            self.types = ResultTypeCatalog()
            self.alarms.raise_alarm(STEP_S3, "LoadResultTypes", "No Results Structures folder", severity="Warning")
            return self.types
        self.types = ResultTypeCatalog.from_csv_folder(path)
        for skipped in self.types.skipped_files:
            self.alarms.raise_alarm(
                STEP_S3, "LoadResultTypes", f"Skipped invalid CSV {skipped}", severity="Warning"
            )
        if not self.types.types:
            self.alarms.raise_alarm(
                STEP_S3,
                "LoadResultTypes",
                "Zero valid Results types — catalog cannot match globals",
                severity="Error",
            )
        return self.types

    def sync_types_from_structures(self, structures: dict) -> None:
        """Mirror production ResultsStructure dict into ResultTypeCatalog (shape gate)."""
        catalog = ResultTypeCatalog()
        for name, members in type_members_from_structures(structures).items():
            catalog.types[name] = ResultType(name=name, members=tuple(sorted(members)))
        self.types = catalog

    def bind_opc_paths(self, identities: list[SilworxIdentity]) -> list[OpcObservation]:
        """Construct OTS ProofTest.{TAG}.Running then OPC ProofTest.{TAG}.Running — do not CSV-score."""
        observations: list[OpcObservation] = []
        servers = self.opc.discover_servers()
        if not servers:
            self.alarms.raise_alarm(
                STEP_S4, "BindOpcPaths", "No X-OPC server", severity="Warning"
            )
            return observations
        # Browse ProofTest branches into cache BEFORE path lookup (find_running_path
        # only searches the tag cache — without this, API mode never binds OPC).
        try:
            if hasattr(self.opc, "list_tags_all_servers"):
                self.opc.list_tags_all_servers(servers)
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S4,
                "BindOpcPaths",
                f"OPC browse failed: {exc}",
                severity="Warning",
            )
        for ident in identities:
            if not ident.device_tag or "." in ident.device_tag:
                continue
            bound = None
            for server in servers:
                path = self.opc.find_running_path(server, ident.device_tag)
                if path:
                    prefix = path[: -len(".Running")] if path.endswith(".Running") else path
                    bound = OpcObservation(
                        device_tag=ident.device_tag,
                        opc_server=server,
                        opc_item_prefix=prefix,
                        results_type=ident.results_type,
                        running_item=path if path.endswith(".Running") else f"{prefix}.Running",
                    )
                    break
            if bound:
                observations.append(bound)
        return observations

    def _last_types_by_tag(self) -> dict[str, str]:
        last: dict[str, str] = {}
        try:
            rows = self.store.list_devices("all")
        except Exception:
            rows = []
        for row in rows or []:
            tag = str(row.get("device_tag") or "")
            rtype = str(row.get("results_type") or "").strip()
            if tag and rtype:
                last.setdefault(tag, rtype)
        for device in self.devices:
            if device.device_tag and device.results_type:
                last.setdefault(device.device_tag, device.results_type)
        return last

    def discover_opc_only_devices(self) -> list[OpcObservation]:
        servers = self.opc.discover_servers()
        if not servers:
            self.alarms.raise_alarm(
                STEP_S4, "DiscoverOpcOnlyDevices", "No X-OPC server", severity="Warning"
            )
            return []
        return self.opc.discover_opc_only(
            self.types.names(),
            last_types_by_tag=self._last_types_by_tag(),
        )

    def refresh_catalog(self) -> list[Device]:
        try:
            silworx_rows: list[SilworxIdentity] = []
            # Always attempt API discovery when SILworX may be reachable.
            # Attach happens inside list_identities / try_discover_devices_via_api —
            # requiring is_attached() first created a permanent OPC-only deadlock.
            try:
                if self.silworx.has_open_project() or self.silworx.is_attached():
                    silworx_rows = self.silworx.list_identities(self.types.names())
            except Exception as exc:
                self.alarms.raise_alarm(
                    "S7",
                    "RefreshCatalog",
                    f"SILworX unreachable: {exc}",
                    severity="Error",
                )
                # Keep prior in-memory devices when API fails mid-flight; OPC-only still runs.
                silworx_rows = []

            # A1: SILworX identities present → bind constructed paths (type from API).
            # A2: otherwise / extra OPC folders → shaped OPC-only (shape gate, no invent).
            opc_bound = self.bind_opc_paths(silworx_rows) if silworx_rows else []
            opc_only = self.discover_opc_only_devices()
            if silworx_rows:
                # When SILworX typed the TAG, discard OPC invent/type from opc_only for that TAG;
                # keep opc_only rows only for TAGs not in SILworX (true OPC-only devices).
                api_tags = {i.device_tag for i in silworx_rows}
                opc_only = [o for o in opc_only if o.device_tag not in api_tags]
                # Bound observations already carry SILworX results_type.
                for obs in opc_bound:
                    # Ensure type remains SILworX (never CSV).
                    for ident in silworx_rows:
                        if ident.device_tag == obs.device_tag:
                            # OpcObservation is frozen — replace via new instance in list rebuild
                            break
                opc_bound = [
                    OpcObservation(
                        device_tag=o.device_tag,
                        opc_server=o.opc_server,
                        opc_item_prefix=o.opc_item_prefix,
                        results_type=next(
                            (i.results_type for i in silworx_rows if i.device_tag == o.device_tag),
                            o.results_type,
                        ),
                        running_item=o.running_item,
                    )
                    for o in opc_bound
                ]
            opc_obs = opc_bound + opc_only
            existing = {d.device_id.key(): d for d in self.devices}
            try:
                for row in self.store.list_devices("all") or []:
                    try:
                        device = device_from_row(row)
                        existing.setdefault(device.device_id.key(), device)
                    except Exception:
                        continue
            except Exception:
                pass
            result = self.merger.merge(silworx_rows, opc_obs, existing=existing)
            for collision in result.collisions:
                self.alarms.raise_alarm(
                    STEP_S3,
                    "RefreshCatalog",
                    f"OPC path collision for {collision.device_tag} at {collision.opc_path}",
                    device_tag=collision.device_tag,
                    severity="Error",
                )
            for dup in result.skipped_duplicates:
                self.alarms.raise_alarm(
                    STEP_S3,
                    "RefreshCatalog",
                    "Duplicate TAG in same project+config+resource skipped",
                    device_tag=dup,
                    severity="Warning",
                )
            keep_opc_only = False
            if self.archive is not None:
                try:
                    keep_opc_only = bool(self.archive.keep_opc_only_enabled())
                except Exception:
                    keep_opc_only = False
            else:
                try:
                    host_db = getattr(self.store, "_db", None)
                    if host_db is not None:
                        state = host_db.get_service_state() or {}
                        keep_opc_only = str(state.get("device_list_keep_opc_only") or "") == "1"
                except Exception:
                    keep_opc_only = False

            persisted: list[Device] = []
            for device in result.devices:
                if keep_opc_only and not device.present_on_opc:
                    continue
                try:
                    self.store.upsert_device(device)
                    persisted.append(device)
                except Exception as exc:
                    self.alarms.raise_alarm(
                        STEP_S3,
                        "RefreshCatalog",
                        f"Store upsert failed: {exc}",
                        device_tag=device.device_tag,
                    )
                    continue
            self.devices = sort_devices(persisted)
            self.reconcile_catalog([d.device_id.key() for d in self.devices])
            return self.devices
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S3, "RefreshCatalog", str(exc))
            return list(self.devices)

    def reconcile_catalog(self, active_ids: list[str]) -> None:
        try:
            self.store.reconcile(active_ids)
        except Exception as exc:
            self.alarms.raise_alarm(STEP_S3, "ReconcileCatalog", str(exc))

    def run_station_refresh(self, host: object, *, manual: bool = False) -> dict:
        """
        Production RefreshCatalog — Domain/ports merge is the brain (Gap B).

        Host still owns OPC server cache, schema sync, sync markers, and service_state.
        step03 sync_device_list_case1_via_api is NOT called.
        """
        import time as _time

        stop = getattr(host, "_stop", None)
        if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
            return {}
        try:
            host.db.set_service_state("catalog_refresh", "1")
            sync_fn = getattr(host, "_sync_health_caches_from_db", None)
            if callable(sync_fn):
                sync_fn()
        except Exception:
            pass
        try:
            if manual:
                try:
                    host.alarms.clear_shown_on_refresh()
                except Exception:
                    pass

            try:
                host._opc_servers = host.opc.discover_servers()
                if manual:
                    # Re-browse tags only — do not disconnect live OPC clients (poll race).
                    inval = getattr(host.opc, "invalidate_tag_cache", None)
                    if callable(inval):
                        inval()
                    else:
                        host.opc.invalidate_cache()
                if not host._opc_servers:
                    host.alarms.raise_alarm(
                        "S4", "No X-OPC server detected on host", action="RefreshCatalog"
                    )
            except Exception as exc:
                host.alarms.raise_alarm("P3", "OPC discovery failed", cause=str(exc))

            if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
                return {}

            structures = getattr(host, "structures", {}) or {}
            self.sync_types_from_structures(structures)
            if not self.types.types and self.types_folder:
                self.load_result_types()

            devices = self.refresh_catalog()
            if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
                return {}

            api_rows = any(
                bool(getattr(d, "project", None) or getattr(d, "configuration", None))
                for d in devices
            )
            api_attached = False
            try:
                api_attached = bool(self.silworx.is_attached())
            except Exception:
                api_attached = False
            api_ok = api_attached or api_rows
            opc_ok = bool(getattr(host, "_opc_servers", None))
            if api_ok and opc_ok:
                device_source = "api+opc"
            elif api_ok:
                device_source = "api"
            else:
                device_source = "opc_fallback"

            active_types = sorted({d.results_type for d in devices if d.results_type})
            try:
                host.db.set_service_state("device_list_source", device_source)
                host.db.sync_schema_case1(
                    host.structures, active_types or list(host.structures.keys())
                )
            except Exception as exc:
                log.warning("Schema / device_list_source update failed: %s", exc)

            try:
                from prooftest.step01_setup import sync_device_report_folders

                folder_pairs = [
                    (d.device_tag, d.results_type) for d in devices if d.results_type
                ]
                if folder_pairs:
                    sync_device_report_folders(host.config, folder_pairs, host.db.alarms)
            except Exception as exc:
                log.warning("Report folder sync failed: %s", exc)

            if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
                return {}
            try:
                host._case1_sync.commit()
            except Exception as exc:
                log.warning("Sync marker commit failed: %s", exc)
            try:
                host._publish_silworx_state()
            except Exception as exc:
                log.warning("Publish SILworX state failed: %s", exc)
            host.db.set_service_state("deployment_case", "1")
            host.db.set_service_state("opc_servers", str(len(host._opc_servers)))
            host.db.set_service_state("opc_server_list", ";".join(host._opc_servers))
            host.db.set_service_state("active_devices", str(len(host.db.list_active_devices())))
            host.db.set_service_state("opc_devices", str(host.db.count_opc_devices()))
            result = {
                "opc_servers": len(host._opc_servers),
                "active_devices": len(host.db.list_active_devices()),
                "opc_devices": host.db.count_opc_devices(),
                "structures_loaded": len(host.structures),
                "device_list_source": device_source,
            }
            host._cached_device_counts = (
                int(result["active_devices"]),
                int(result["opc_devices"]),
            )
            try:
                host._cached_service_state = host.db.get_service_state()
            except Exception:
                pass
            return result
        finally:
            try:
                host.db.set_service_state("catalog_refresh", "0")
                host.db.set_service_state(
                    "last_catalog_refresh", _time.strftime("%Y-%m-%d %H:%M:%S")
                )
                sync_fn = getattr(host, "_sync_health_caches_from_db", None)
                if callable(sync_fn):
                    sync_fn()
            except Exception:
                pass
