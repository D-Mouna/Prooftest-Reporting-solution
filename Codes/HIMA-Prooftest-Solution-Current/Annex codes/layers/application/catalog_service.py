"""CatalogService: LoadResultTypes, RefreshCatalog, BindOpcPaths, DiscoverOpcOnly, ReconcileCatalog."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from layers.application.errors import STEP_S3, STEP_S4
from layers.domain.device import Device, DeviceId, sort_devices
from layers.domain.merger import CatalogMerger, OpcObservation, SilworxIdentity
from layers.domain.result_types import ResultTypeCatalog
from layers.ports import AlarmPort, OpcPort, SilworxPort, StorePort

OTS_BRANCH = "OTS ProofTest"
OPC_BRANCH = "OPC ProofTest"


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
    ) -> None:
        self.store = store
        self.opc = opc
        self.silworx = silworx
        self.alarms = alarms
        self.types_folder = types_folder
        self.merger = merger or CatalogMerger()
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

    def bind_opc_paths(self, identities: list[SilworxIdentity]) -> list[OpcObservation]:
        """Construct OTS ProofTest.{TAG}.Running then OPC ProofTest.{TAG}.Running — do not CSV-score."""
        observations: list[OpcObservation] = []
        servers = self.opc.discover_servers()
        if not servers:
            self.alarms.raise_alarm(
                STEP_S4, "BindOpcPaths", "No X-OPC server", severity="Warning"
            )
            return observations
        for ident in identities:
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

    def discover_opc_only_devices(self) -> list[OpcObservation]:
        servers = self.opc.discover_servers()
        if not servers:
            self.alarms.raise_alarm(
                STEP_S4, "DiscoverOpcOnlyDevices", "No X-OPC server", severity="Warning"
            )
            return []
        return self.opc.discover_opc_only(self.types.names())

    def refresh_catalog(self) -> list[Device]:
        try:
            silworx_rows: list[SilworxIdentity] = []
            if self.silworx.is_attached():
                try:
                    silworx_rows = self.silworx.list_identities(self.types.names())
                except Exception as exc:
                    self.alarms.raise_alarm(
                        "S7",
                        "RefreshCatalog",
                        f"SILworX unreachable: {exc}",
                        severity="Error",
                    )
                    return list(self.devices)

            opc_bound = self.bind_opc_paths(silworx_rows) if silworx_rows else []
            opc_only = self.discover_opc_only_devices()
            opc_obs = opc_bound + opc_only
            existing = {d.device_id.key(): d for d in self.devices}
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
            for device in result.devices:
                try:
                    self.store.upsert_device(device)
                except Exception as exc:
                    self.alarms.raise_alarm(
                        STEP_S3,
                        "RefreshCatalog",
                        f"Store upsert failed: {exc}",
                        device_tag=device.device_tag,
                    )
                    continue
            self.devices = sort_devices(result.devices)
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
        Production RefreshCatalog use case (SILworX API + OPC merge, schema, markers).

        Presentation must call ApplicationFacade.refresh_catalog() only.
        WorkerHost may call this through the facade / ``host.refresh`` delegate.
        """
        import logging

        from prooftest.step03_device_list import sync_device_list_case1_via_api

        log = logging.getLogger(__name__)
        stop = getattr(host, "_stop", None)
        if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
            return {}
        if manual:
            try:
                host.alarms.clear_shown_on_refresh()
            except Exception:
                pass

        try:
            host._opc_servers = host.opc.discover_servers()
            if manual:
                host.opc.invalidate_cache()
            if not host._opc_servers:
                host.alarms.raise_alarm(
                    "S4", "No X-OPC server detected on host", action="RefreshCatalog"
                )
        except Exception as exc:
            host.alarms.raise_alarm("P3", "OPC discovery failed", cause=str(exc))

        if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
            return {}

        active_types, device_source = sync_device_list_case1_via_api(
            host.config,
            host.db,
            host.structures,
            host._case1_sync,
            host.opc,
        )
        if getattr(host, "_stopped", False) or (stop is not None and stop.is_set()):
            return {}
        host.db.set_service_state("device_list_source", device_source)
        host.db.sync_schema_case1(
            host.structures, active_types or list(host.structures.keys())
        )

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
        # Do NOT call self.refresh_catalog() here — that would dual-write via a second
        # merge path (domain CatalogMerger) after step03 already updated the store.
        return result
