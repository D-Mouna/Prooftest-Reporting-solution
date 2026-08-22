"""Production poll host — thin shell over Application LiveTestService (Gap C)."""

from __future__ import annotations

import queue
import threading
from typing import Any, Dict, List, Optional, Union

from layers.adapters import (
    AlarmManagerAdapter,
    AnnexReportAdapter,
    DatabaseStoreAdapter,
    OpcManagerAdapter,
)
from layers.application.live_test import LiveTestService
from layers.domain.device import Device, device_from_row
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.results_csv import ResultsStructure, member_to_column, annexes_directory, load_annex_types, member_column_dtype_map, is_ascii_type, is_parameters_type
from prooftest.step04_opc import OpcManager

log = __import__("logging").getLogger(__name__)


class ProoftestMonitor:
    """
    Thin production host for LiveTestService.

    Owns OPC snapshot collection + report worker. Edge detection / complete path
    is always ``LiveTestService`` (injected from ApplicationFacade when available).
    """

    def __init__(
        self,
        config: AppConfig,
        db: Database,
        opc: OpcManager,
        structures: Dict[str, ResultsStructure],
        *,
        live_service: Optional[LiveTestService] = None,
    ) -> None:
        self.config = config
        self.db = db
        self.opc = opc
        self.structures = structures
        self._annex_types = load_annex_types(annexes_directory(config.results_structures))
        if self._annex_types:
            log.info(
                "Loaded %d annex type(s) from %s",
                len(self._annex_types),
                annexes_directory(config.results_structures),
            )
        else:
            log.warning(
                "No annex types loaded — ASCII/Parameters OPC decode needs "
                "Results Structures/Annexes/*.csv (e.g. X-HART_ASCII_32, X-HART_*_Parameters)"
            )
        self._queue: queue.Queue = queue.Queue()
        self._report_lock = threading.Lock()
        self._stop = threading.Event()
        self._store = DatabaseStoreAdapter(db, structures)
        self._reports = AnnexReportAdapter(config, db, self._store)
        if live_service is not None:
            self._live = live_service
            self._live.snapshot_fn = self._collect_snapshot
            self._live.defer_complete = True
            # Keep ports consistent with production adapters when facade used different instances.
            self._live.opc = OpcManagerAdapter(opc, structures_fn=lambda: self.structures)
            self._live.store = self._store
            self._live.reports = self._reports
            self._live.alarms = AlarmManagerAdapter(db.alarms)
        else:
            self._live = LiveTestService(
                OpcManagerAdapter(opc, structures_fn=lambda: self.structures),
                self._store,
                self._reports,
                AlarmManagerAdapter(db.alarms),
                snapshot_fn=self._collect_snapshot,
                defer_complete=True,
            )
        self._worker = threading.Thread(target=self._report_worker, daemon=True, name="report-worker")
        self._worker.start()

    def reload_type_catalog(self) -> None:
        """Reload annex nested types after Results Structures catalogue changes."""
        self._annex_types = load_annex_types(annexes_directory(self.config.results_structures))
        log.info("Annex type catalogue reloaded: %d type(s)", len(self._annex_types))

    def shutdown(self, timeout: float = 30.0) -> None:
        """Stop the report worker and drain or abandon the completion queue."""
        self._stop.set()
        self._queue.put(None)
        self._worker.join(timeout=timeout)
        if self._worker.is_alive():
            log.warning("Report worker did not stop within %.0fs", timeout)

    def poll_devices(self) -> None:
        """Production poll entry — delegates entirely to LiveTestService.poll_once."""
        rows = self.db.list_active_devices()
        devices: List[Device] = []
        for row in rows:
            try:
                devices.append(device_from_row(row) if isinstance(row, dict) else row)
            except Exception as exc:
                self.db.alarms.raise_alarm(
                    "S4",
                    f"Device row map failed for {getattr(row, 'get', lambda *_: None)('device_tag')}",
                    device_tag=(row.get("device_tag") if isinstance(row, dict) else None),
                    cause=str(exc),
                    show_popup=False,
                    action="PollOnce",
                )
        self._live.poll_once(devices)
        while self._live.queue:
            self._queue.put(self._live.queue.pop(0))

    def _poll_one(self, device: Union[Dict[str, Any], Device]) -> None:
        """Compatibility for older callers — prefer poll_devices."""
        if isinstance(device, dict):
            device = device_from_row(device)
        self._live.seed_device(device)
        self._live._poll_one(device)
        while self._live.queue:
            self._queue.put(self._live.queue.pop(0))

    def _collect_snapshot(self, device: Device) -> tuple[Dict[str, Any], List[str]]:
        if not (device.results_type or "").strip():
            return {}, ["Results type unknown — snapshot skipped"]
        structure = self.structures.get(device.results_type)
        if not structure:
            return {}, ["No Results structure"]
        binding = self.opc.resolve_device_binding(
            device.device_tag,
            device.opc_item_prefix,
            servers=[device.opc_server] if device.opc_server else None,
        )
        if not binding or not binding.running_item_id:
            return {}, ["No OPC binding"]
        server = binding.server
        prefix = binding.item_prefix
        if device.opc_server != server or device.opc_item_prefix != prefix:
            device.opc_server = server
            device.opc_item_prefix = prefix
            self.db.upsert_device(
                device.device_tag,
                device.results_type,
                opc_server=server,
                opc_prefix=prefix,
                device_id=device.device_id.key(),
                silworx_project=device.project or None,
                configuration=device.configuration or None,
                resource=device.resource or None,
            )
        return self._read_snapshot(server, binding.tags, prefix, structure)

    def _read_snapshot(
        self,
        server: str,
        tags: List[str],
        prefix: str,
        structure: ResultsStructure,
    ) -> tuple[Dict[str, Any], List[str]]:
        from prooftest.opc_snapshot import enrich_snapshot_from_opc, value_is_empty

        short_names = [n for n in structure.member_short_names() if n.lower() != "running"]
        item_map = self.opc.build_member_item_ids(tags, prefix, short_names)
        item_ids = list(item_map.values())
        if not item_ids:
            return {}, ["No OPC members resolved"]
        values = self.opc.read_values(server, item_ids)
        snapshot: Dict[str, Any] = {}
        notes: List[str] = []
        col_dtypes = member_column_dtype_map(structure)
        member_types: Dict[str, str] = {}
        for member, item_id in item_map.items():
            val, quality = values.get(item_id, (None, "Bad"))
            col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
            snapshot[col] = val
            dtype = col_dtypes.get(col, "")
            member_types[col] = dtype
            if str(quality).lower() != "good":
                notes.append(f"{member}: quality {quality}")
            elif value_is_empty(val) and dtype and (
                is_ascii_type(dtype)
                or is_parameters_type(dtype, self._annex_types)
            ):
                notes.append(f"{member}: quality Empty")

        def _read(ids: List[str]) -> Dict[str, tuple]:
            return self.opc.read_values(server, ids)

        snapshot, notes = enrich_snapshot_from_opc(
            tags=tags,
            prefix=prefix,
            member_types=member_types,
            snapshot=snapshot,
            notes=notes,
            read_values=_read,
            type_catalog=self._annex_types,
        )
        running_items = [t for t in tags if t.endswith(".Running") and prefix in t]
        if running_items:
            rv, _ = self.opc.read_values(server, [running_items[0]]).get(running_items[0], (False, "Good"))
            if bool(rv):
                snapshot["_running_still_true"] = True
        return snapshot, notes

    def _report_worker(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue
            if event is None:
                break
            try:
                with self._report_lock:
                    self._live.run_complete(event)
            except Exception as exc:
                tag = ""
                if isinstance(event, dict):
                    device = event.get("device")
                    tag = getattr(device, "device_tag", "") or ""
                self.db.alarms.raise_alarm(
                    "S6",
                    f"Report generation failed for {tag}",
                    device_tag=tag,
                    cause=str(exc),
                    action="CompleteTest",
                )
            finally:
                self._queue.task_done()

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize() + self._live.queue_depth

    @property
    def live(self) -> LiveTestService:
        return self._live
