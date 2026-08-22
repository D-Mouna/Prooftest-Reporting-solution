"""LiveTestService: PollOnce, start/end/interrupt, CompleteTest off the poll thread contract."""

from __future__ import annotations

import logging
import time
from typing import Callable, Optional

from layers.application.errors import STEP_S4, STEP_S5, STEP_S6
from layers.domain.device import Device
from layers.domain.running import RunningEdgeDetector
from layers.ports import AlarmPort, OpcPort, ReportPort, StorePort

SnapshotFn = Callable[[Device], tuple[dict, list[str]]]
log = logging.getLogger(__name__)

# How often to probe a Bad-quality .Running item so monitoring can resume.
LIVE_RECHECK_SEC = 5.0


class LiveTestService:
    def __init__(
        self,
        opc: OpcPort,
        store: StorePort,
        reports: ReportPort,
        alarms: AlarmPort,
        *,
        detector: Optional[RunningEdgeDetector] = None,
        snapshot_fn: Optional[SnapshotFn] = None,
        defer_complete: bool = False,
        live_recheck_sec: float = LIVE_RECHECK_SEC,
    ) -> None:
        self.opc = opc
        self.store = store
        self.reports = reports
        self.alarms = alarms
        self.detector = detector or RunningEdgeDetector()
        self.snapshot_fn = snapshot_fn
        self.defer_complete = defer_complete
        self.live_recheck_sec = max(0.01, float(live_recheck_sec))
        self.completed: list[str] = []
        self.interrupted: list[str] = []
        self.queue: list[dict] = []
        self._sequence: dict[str, int] = {}
        # Per Running item (not whole ProgID) — one Bad tag must not block others.
        self._item_live_ok: dict[str, bool] = {}
        self._item_recheck_at: dict[str, float] = {}
        self._skip_logged: set[str] = set()

    @property
    def queue_depth(self) -> int:
        return len(self.queue)

    def seed_device(self, device: Device) -> None:
        self.detector.prime(
            device.device_id.key(),
            device.last_running,
            device.test_in_progress,
        )

    def poll_once(self, devices: list[Device]) -> None:
        for device in devices:
            try:
                self.seed_device(device)
                self._poll_one(device)
            except Exception as exc:
                self.alarms.raise_alarm(
                    STEP_S4,
                    "PollOnce",
                    str(exc),
                    device_tag=device.device_tag,
                )

    def _server_live_ok(self, server: str) -> Optional[bool]:
        fn = getattr(self.opc, "server_live_ok", None)
        if not callable(fn):
            return None
        try:
            return fn(server)
        except Exception:
            return None

    def _mark_item_live(self, running_id: str, ok: bool, quality: str = "") -> None:
        self._item_live_ok[running_id] = bool(ok)
        if ok:
            self._skip_logged.discard(running_id)

    def _maybe_recheck_item(self, server: str, running_id: str) -> Optional[bool]:
        """Return True when this item is Good again; False still Bad; None if wait window."""
        now = time.monotonic()
        if running_id not in self._item_recheck_at:
            self._item_recheck_at[running_id] = now
            return None
        if now - self._item_recheck_at[running_id] < self.live_recheck_sec:
            return None
        self._item_recheck_at[running_id] = now
        fn = getattr(self.opc, "recheck_server_live", None)
        try:
            if callable(fn):
                ok = fn(server, running_id)
            else:
                running, quality = self.opc.read_running(server, running_id)
                ok = running is not None and str(quality).lower() == "good"
            self._mark_item_live(running_id, bool(ok))
            if ok:
                log.info(
                    "OPC item live quality Good again — resuming .Running monitoring: %s",
                    running_id,
                )
            return bool(ok)
        except Exception as exc:
            log.debug("OPC live recheck failed on %s: %s", running_id, exc)
            self._mark_item_live(running_id, False)
            return False

    def _should_skip_live_poll(self, server: str, running_id: str) -> bool:
        """Skip only when this item (or, if unknown, the server sample) is known Bad."""
        item_ok = self._item_live_ok.get(running_id)
        if item_ok is False:
            return True
        if item_ok is True:
            return False
        server_ok = self._server_live_ok(server) if server else None
        return server_ok is False

    def _poll_one(self, device: Device) -> None:
        key = device.device_id.key()
        if self.detector.is_in_progress(key) and not device.present_on_opc:
            self.on_test_interrupted(device, "present_on_opc false")
            return
        if not device.present_on_opc or not device.opc_item_prefix:
            return
        running_id = (
            device.opc_item_prefix
            if device.opc_item_prefix.endswith(".Running")
            else f"{device.opc_item_prefix}.Running"
        )
        server = str(device.opc_server or "")
        if self._should_skip_live_poll(server, running_id):
            if self.detector.is_in_progress(key):
                self.on_test_interrupted(device, "OPC live quality Bad — monitoring skipped")
                return
            if running_id not in self._skip_logged:
                self._skip_logged.add(running_id)
                log.info(
                    "Skipping .Running monitoring for %s (live quality Bad); recheck every %.0fs",
                    running_id,
                    self.live_recheck_sec,
                )
            resumed = self._maybe_recheck_item(server, running_id)
            if resumed is not True:
                return
            # Quality restored — fall through and read in this same poll cycle.

        try:
            running, quality = self.opc.read_running(device.opc_server, running_id)
        except Exception as exc:
            if self.detector.is_in_progress(key):
                self.on_test_interrupted(device, str(exc))
            else:
                self.alarms.raise_alarm(
                    STEP_S4, "PollOnce", str(exc), device_tag=device.device_tag
                )
            return
        quality_good = str(quality).lower() == "good"
        self._mark_item_live(running_id, quality_good, str(quality or ""))
        mark = getattr(self.opc, "mark_live_quality", None)
        if callable(mark) and server:
            try:
                mark(server, quality_good, str(quality or ""))
            except Exception:
                pass
        if not quality_good and not self.detector.is_in_progress(key):
            self._maybe_recheck_item(server, running_id)
            return
        event = self.detector.observe(
            key,
            running,
            quality_good=quality_good,
            present_on_opc=device.present_on_opc,
        )
        if event.kind == "started":
            self.on_test_started(device)
        elif event.kind == "ended":
            self.on_test_ended(device, running_id)
        elif event.kind == "interrupted":
            self.on_test_interrupted(device, f"OPC quality {quality}")

    def on_test_started(self, device: Device) -> None:
        device.test_in_progress = True
        device.last_running = True
        try:
            self.store.upsert_device(device)
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S5, "OnTestStarted", str(exc), device_tag=device.device_tag
            )
        try:
            self.store.start_test(device.device_tag, device.results_type)
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S5, "OnTestStarted", str(exc), device_tag=device.device_tag
            )

    def on_test_ended(self, device: Device, running_id: str) -> None:
        # T18: unknown / empty Results type — no ProofTest_* snapshot write.
        if not (device.results_type or "").strip():
            device.test_in_progress = False
            device.last_running = False
            try:
                self.store.upsert_device(device)
            except Exception:
                pass
            try:
                self.store.finish_test(device.device_tag, "skipped_unknown_type")
            except Exception:
                pass
            self.alarms.raise_alarm(
                STEP_S5,
                "OnTestEnded",
                "Skipped ProofTest snapshot — Results type unknown",
                device_tag=device.device_tag,
                severity="Warning",
            )
            self.detector.confirm_ended(device.device_id.key(), False)
            return

        snapshot: dict
        notes: list[str]
        if self.snapshot_fn is not None:
            snapshot, notes = self.snapshot_fn(device)
            if snapshot.get("_running_still_true"):
                return
            self.detector.confirm_ended(device.device_id.key(), False)
        else:
            try:
                still, quality = self.opc.read_running(device.opc_server, running_id)
            except Exception as exc:
                self.on_test_interrupted(device, str(exc))
                return
            confirmed = self.detector.confirm_ended(
                device.device_id.key(), bool(still) and str(quality).lower() == "good"
            )
            if confirmed.kind == "flicker":
                return
            snapshot, notes = {"Running": False}, []

        device.test_in_progress = False
        device.last_running = False
        try:
            self.store.upsert_device(device)
        except Exception:
            pass
        try:
            self.store.finish_test(device.device_tag, "completed")
        except Exception:
            pass

        sequence = self._next_sequence(device.device_id.key())
        # Durable freeze: copy OPC-read values into SQL before report queue waits.
        # OPC is read-only — this never writes back to the server.
        record_id, snapshot_table = self._persist_snapshot(device, snapshot, sequence=sequence)
        job = {
            "device": device,
            "snapshot": snapshot,
            "quality_notes": notes,
            "sequence": sequence,
            "record_id": record_id,
            "snapshot_table": snapshot_table,
        }
        if self.defer_complete:
            self.queue.append(job)
            return
        self.run_complete(job)

    def on_test_interrupted(self, device: Device, reason: str) -> None:
        device.test_in_progress = False
        device.last_running = False
        self.interrupted.append(device.device_tag)
        try:
            self.store.upsert_device(device)
        except Exception:
            pass
        try:
            self.store.finish_test(device.device_tag, "interrupted")
        except Exception:
            pass
        self.alarms.raise_alarm(
            STEP_S5,
            "OnTestInterrupted",
            reason,
            device_tag=device.device_tag,
            severity="Warning",
        )

    def _next_sequence(self, device_id: str) -> int:
        self._sequence[device_id] = self._sequence.get(device_id, 0) + 1
        return self._sequence[device_id]

    def _snapshot_table_name(self, results_type: str) -> str:
        fn = getattr(self.store, "snapshot_table_for", None)
        if callable(fn):
            try:
                return str(fn(results_type) or "")
            except Exception:
                pass
        return ""

    def _persist_snapshot(
        self,
        device: Device,
        snapshot: dict,
        *,
        sequence: Optional[int] = None,
    ) -> tuple[Optional[int], str]:
        """INSERT the frozen OPC copy into ProofTest_* immediately (read-only OPC)."""
        insert_kw = {
            "opc_server": device.opc_server,
            "sequence": sequence,
            "device_id": device.device_id.key(),
        }
        table = self._snapshot_table_name(device.results_type)
        try:
            record_id = self.store.insert_snapshot(
                device.device_tag, device.results_type, snapshot, **insert_kw
            )
        except TypeError:
            try:
                record_id = self.store.insert_snapshot(
                    device.device_tag, device.results_type, snapshot
                )
            except Exception as exc:
                self.alarms.raise_alarm(
                    STEP_S5,
                    "OnTestEnded",
                    f"SQL insert failed: {exc}",
                    device_tag=device.device_tag,
                )
                return None, table
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S5,
                "OnTestEnded",
                f"SQL insert failed: {exc}",
                device_tag=device.device_tag,
            )
            try:
                record_id = self.store.insert_snapshot(
                    device.device_tag, device.results_type, snapshot, **insert_kw
                )
            except TypeError:
                try:
                    record_id = self.store.insert_snapshot(
                        device.device_tag, device.results_type, snapshot
                    )
                except Exception as exc2:
                    self.alarms.raise_alarm(
                        STEP_S5,
                        "OnTestEnded",
                        f"SQL insert retry failed: {exc2}",
                        device_tag=device.device_tag,
                    )
                    return None, table
            except Exception as exc2:
                self.alarms.raise_alarm(
                    STEP_S5,
                    "OnTestEnded",
                    f"SQL insert retry failed: {exc2}",
                    device_tag=device.device_tag,
                )
                return None, table
        if not table:
            table = str(getattr(self.store, "last_table", None) or "") or self._snapshot_table_name(
                device.results_type
            )
        return record_id, table

    def run_complete(self, job: dict) -> None:
        device: Device = job["device"]
        snapshot: dict = job.get("snapshot") or {}
        quality_notes: list[str] = list(job.get("quality_notes") or [])
        self.complete_test(
            device,
            snapshot,
            quality_notes,
            sequence=job.get("sequence"),
            record_id=job.get("record_id"),
            snapshot_table=job.get("snapshot_table") or "",
        )

    def complete_test(
        self,
        device: Device,
        snapshot: dict,
        quality_notes: list[str],
        *,
        report_raises: Optional[Callable[[], None]] = None,
        sequence: Optional[int] = None,
        record_id: Optional[int] = None,
        snapshot_table: str = "",
    ) -> None:
        """Write report from the frozen snapshot. SQL insert already done on test end when possible."""
        device.test_in_progress = False
        table = snapshot_table or self._snapshot_table_name(device.results_type)

        # Direct callers (unit tests) may skip on_test_ended — insert once here.
        if record_id is None:
            record_id, table = self._persist_snapshot(device, snapshot, sequence=sequence)

        if quality_notes:
            self.alarms.raise_alarm(
                STEP_S5,
                "CompleteTest",
                "; ".join(quality_notes),
                device_tag=device.device_tag,
                severity="Warning",
            )
        report_path: Optional[str] = None
        try:
            if report_raises:
                report_raises()
            write_kw = {
                "quality_notes": quality_notes,
                "project": device.project,
                "snapshot_table": table or None,
                "record_id": record_id,
            }
            try:
                report_path = self.reports.write(
                    device.device_tag,
                    device.results_type,
                    snapshot,
                    **write_kw,
                )
            except TypeError:
                report_path = self.reports.write(
                    device.device_tag,
                    device.results_type,
                    snapshot,
                    quality_notes=quality_notes,
                    project=device.project,
                )
            if report_path and table and record_id is not None:
                updater = getattr(self.store, "update_report_path", None)
                if callable(updater):
                    try:
                        updater(table, int(record_id), report_path)
                    except Exception:
                        pass
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S6,
                "CompleteTest",
                f"Report failed: {exc}",
                device_tag=device.device_tag,
            )
        self.completed.append(device.device_tag)
        try:
            self.store.finish_test(device.device_tag, "completed")
        except Exception:
            pass
        _ = sequence
        _ = report_path
