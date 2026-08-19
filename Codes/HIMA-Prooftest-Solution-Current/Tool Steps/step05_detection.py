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
from prooftest.results_csv import ResultsStructure, member_to_column
from prooftest.step04_opc import OpcManager

log = __import__("logging").getLogger(__name__)


class ProoftestMonitor:
    def __init__(
        self,
        config: AppConfig,
        db: Database,
        opc: OpcManager,
        structures: Dict[str, ResultsStructure],
    ) -> None:
        self.config = config
        self.db = db
        self.opc = opc
        self.structures = structures
        self._queue: queue.Queue = queue.Queue()
        self._report_lock = threading.Lock()
        self._stop = threading.Event()
        self._store = DatabaseStoreAdapter(db, structures)
        self._reports = AnnexReportAdapter(config, db, self._store)
        self._live = LiveTestService(
            OpcManagerAdapter(opc),
            self._store,
            self._reports,
            AlarmManagerAdapter(db.alarms),
            snapshot_fn=self._collect_snapshot,
            defer_complete=True,
        )
        self._worker = threading.Thread(target=self._report_worker, daemon=True, name="report-worker")
        self._worker.start()

    def shutdown(self, timeout: float = 30.0) -> None:
        """Stop the report worker and drain or abandon the completion queue."""
        self._stop.set()
        self._queue.put(None)
        self._worker.join(timeout=timeout)
        if self._worker.is_alive():
            log.warning("Report worker did not stop within %.0fs", timeout)

    def poll_devices(self) -> None:
        devices = self.db.list_active_devices()
        for row in devices:
            try:
                self._poll_one(row)
            except Exception as exc:
                self.db.alarms.raise_alarm(
                    "S4",
                    f"OPC read failed for {row.get('device_tag')}",
                    device_tag=row.get("device_tag"),
                    cause=str(exc),
                    show_popup=False,
                    action="PollOnce",
                )

    def _poll_one(self, device: Union[Dict[str, Any], Device]) -> None:
        if isinstance(device, dict):
            device = device_from_row(device)
        self._live.seed_device(device)
        self._live._poll_one(device)
        while self._live.queue:
            self._queue.put(self._live.queue.pop(0))

    def _collect_snapshot(self, device: Device) -> tuple[Dict[str, Any], List[str]]:
        structure = self.structures.get(device.results_type)
        if not structure:
            return {}, ["No Results structure"]
        binding = self.opc.resolve_device_binding(
            device.device_tag,
            device.opc_item_prefix,
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
        short_names = [n for n in structure.member_short_names() if n.lower() != "running"]
        item_map = self.opc.build_member_item_ids(tags, prefix, short_names)
        item_ids = list(item_map.values())
        if not item_ids:
            return {}, ["No OPC members resolved"]
        values = self.opc.read_values(server, item_ids)
        snapshot: Dict[str, Any] = {}
        notes: List[str] = []
        for member, item_id in item_map.items():
            val, quality = values.get(item_id, (None, "Bad"))
            col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
            snapshot[col] = val
            if str(quality).lower() != "good":
                notes.append(f"{member}: quality {quality}")
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
