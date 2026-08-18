from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.step04_opc import OpcManager
from prooftest.step06_reports import write_reports
from prooftest.results_csv import ResultsStructure, member_to_column, structure_to_sql_table

log = logging.getLogger(__name__)


@dataclass
class CompletionEvent:
    device_tag: str
    results_type: str
    opc_server: str
    opc_prefix: str
    snapshot: Dict[str, Any]
    sequence: int
    quality_notes: List[str]


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
        self._queue: queue.Queue[CompletionEvent] = queue.Queue()
        self._report_lock = threading.Lock()
        self._sequence_counters: Dict[str, int] = {}
        self._stop = threading.Event()
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
        for device in devices:
            if device.get("test_in_progress") and not device.get("present_on_opc"):
                self._interrupt_test(device, "device no longer on OPC")
                continue
            if not device.get("present_on_opc"):
                continue
            try:
                self._poll_one(device)
            except Exception as exc:
                self.db.alarms.raise_alarm(
                    "P3",
                    f"OPC read failed for {device['device_tag']}",
                    device_tag=device["device_tag"],
                    cause=str(exc),
                    show_popup=False,
                )

    def _poll_one(self, device: Dict[str, Any]) -> None:
        structure = self.structures.get(device["results_type"])
        if not structure:
            return
        binding = self.opc.resolve_device_binding(
            device["device_tag"],
            device.get("opc_item_prefix"),
        )
        if not binding or not binding.running_item_id:
            return
        server = binding.server
        prefix = binding.item_prefix
        tags = binding.tags
        running_id = binding.running_item_id
        if device.get("opc_server") != server or device.get("opc_item_prefix") != prefix:
            self.db.upsert_device(
                device["device_tag"],
                device["results_type"],
                opc_server=server,
                opc_prefix=prefix,
            )
        read_map = self.opc.read_values(server, [running_id])
        value, quality = read_map.get(running_id, (None, "Bad"))
        running = bool(value) if value is not None else False
        prev = device.get("last_running")
        if prev is None:
            prev = False

        if (prev or device.get("test_in_progress")) and value is None and str(quality).lower() != "good":
            self._interrupt_test(device, f"OPC Running quality {quality}")
            return

        if prev is False and running:
            self.db.upsert_device(
                device["device_tag"],
                device["results_type"],
                last_running=True,
                test_in_progress=True,
            )
            try:
                self.db.start_test_history(device["device_tag"], device["results_type"])
            except Exception as exc:
                log.warning("Could not record test start history for %s: %s", device["device_tag"], exc)
            log.info("Prooftest started: %s", device["device_tag"])

        if prev is True and not running:
            snapshot, notes = self._read_snapshot(server, tags, prefix, structure)
            if snapshot.get("_running_still_true"):
                return
            seq = self._next_sequence(device["device_tag"])
            self._queue.put(
                CompletionEvent(
                    device_tag=device["device_tag"],
                    results_type=device["results_type"],
                    opc_server=server,
                    opc_prefix=prefix,
                    snapshot=snapshot,
                    sequence=seq,
                    quality_notes=notes,
                )
            )
            result = self._result_from_snapshot(snapshot)
            try:
                self.db.finish_open_test_history(device["device_tag"], "completed", result)
            except Exception as exc:
                log.warning("Could not record test completion history for %s: %s", device["device_tag"], exc)
            self.db.upsert_device(
                device["device_tag"],
                device["results_type"],
                last_running=False,
                test_in_progress=False,
            )
            log.info("Prooftest completed: %s (queued seq %s)", device["device_tag"], seq)
        else:
            self.db.upsert_device(
                device["device_tag"],
                device["results_type"],
                last_running=running,
            )

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

    def _next_sequence(self, device_tag: str) -> int:
        self._sequence_counters[device_tag] = self._sequence_counters.get(device_tag, 0) + 1
        return self._sequence_counters[device_tag]

    def _interrupt_test(self, device: Dict[str, Any], reason: str) -> None:
        tag = device.get("device_tag") or ""
        if not tag:
            return
        try:
            self.db.finish_open_test_history(tag, "interrupted", "unknown")
        except Exception as exc:
            log.warning("Could not record interrupted test for %s: %s", tag, exc)
        try:
            self.db.upsert_device(
                tag,
                device.get("results_type") or "",
                last_running=False,
                test_in_progress=False,
            )
        except Exception as exc:
            log.warning("Could not clear in-progress flag for %s: %s", tag, exc)
        log.info("Prooftest interrupted: %s (%s)", tag, reason)

    @staticmethod
    def _result_from_snapshot(snapshot: Dict[str, Any]) -> str:
        from prooftest.annex_pdf_generation import result_line_text

        text = result_line_text(snapshot or {})
        if "Unsuccessful" in text or text == "Not done":
            return "unsuccessful"
        return "successful"

    def _report_worker(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue
            if event is None:
                break
            try:
                self._process_completion(event)
            except Exception as exc:
                self.db.alarms.raise_alarm(
                    "P5",
                    f"Report generation failed for {event.device_tag}",
                    device_tag=event.device_tag,
                    cause=str(exc),
                )
            finally:
                self._queue.task_done()

    def _process_completion(self, event: CompletionEvent) -> None:
        table = structure_to_sql_table(event.results_type)
        with self._report_lock:
            record_id = self.db.insert_snapshot(
                table,
                event.device_tag,
                event.snapshot,
                opc_server=event.opc_server,
                sequence=event.sequence,
            )
            paths = write_reports(
                self.config,
                event.device_tag,
                event.results_type,
                event.snapshot,
                quality_notes=event.quality_notes,
            )
            if paths:
                self.db.update_report_path(table, record_id, paths[0])

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize()
