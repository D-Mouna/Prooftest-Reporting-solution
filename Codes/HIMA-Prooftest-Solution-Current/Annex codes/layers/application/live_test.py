"""LiveTestService: PollOnce, start/end/interrupt, CompleteTest off the poll thread contract."""

from __future__ import annotations

from typing import Callable, Optional

from layers.application.errors import STEP_S4, STEP_S5, STEP_S6
from layers.domain.device import Device
from layers.domain.running import RunningEdgeDetector
from layers.ports import AlarmPort, OpcPort, ReportPort, StorePort

SnapshotFn = Callable[[Device], tuple[dict, list[str]]]


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
    ) -> None:
        self.opc = opc
        self.store = store
        self.reports = reports
        self.alarms = alarms
        self.detector = detector or RunningEdgeDetector()
        self.snapshot_fn = snapshot_fn
        self.defer_complete = defer_complete
        self.completed: list[str] = []
        self.interrupted: list[str] = []
        self.queue: list[dict] = []
        self._sequence: dict[str, int] = {}

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
        job = {
            "device": device,
            "snapshot": snapshot,
            "quality_notes": notes,
            "sequence": self._next_sequence(device.device_id.key()),
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

    def run_complete(self, job: dict) -> None:
        device: Device = job["device"]
        snapshot: dict = job.get("snapshot") or {}
        quality_notes: list[str] = list(job.get("quality_notes") or [])
        self.complete_test(
            device,
            snapshot,
            quality_notes,
            sequence=job.get("sequence"),
        )

    def complete_test(
        self,
        device: Device,
        snapshot: dict,
        quality_notes: list[str],
        *,
        report_raises: Optional[Callable[[], None]] = None,
        sequence: Optional[int] = None,
    ) -> None:
        device.test_in_progress = False
        record_id = None
        insert_kw = {
            "opc_server": device.opc_server,
            "sequence": sequence,
            "device_id": device.device_id.key(),
        }
        try:
            record_id = self.store.insert_snapshot(
                device.device_tag, device.results_type, snapshot, **insert_kw
            )
        except TypeError:
            record_id = self.store.insert_snapshot(
                device.device_tag, device.results_type, snapshot
            )
        except Exception as exc:
            self.alarms.raise_alarm(
                STEP_S5, "CompleteTest", f"SQL insert failed: {exc}", device_tag=device.device_tag
            )
            try:
                try:
                    record_id = self.store.insert_snapshot(
                        device.device_tag, device.results_type, snapshot, **insert_kw
                    )
                except TypeError:
                    record_id = self.store.insert_snapshot(
                        device.device_tag, device.results_type, snapshot
                    )
            except Exception as exc2:
                self.alarms.raise_alarm(
                    STEP_S5,
                    "CompleteTest",
                    f"SQL insert retry failed: {exc2}",
                    device_tag=device.device_tag,
                )
                return
        if quality_notes:
            self.alarms.raise_alarm(
                STEP_S5,
                "CompleteTest",
                "; ".join(quality_notes),
                device_tag=device.device_tag,
                severity="Warning",
            )
        try:
            if report_raises:
                report_raises()
            self.reports.write(
                device.device_tag,
                device.results_type,
                snapshot,
                quality_notes=quality_notes,
                project=device.project,
            )
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
        _ = record_id
        _ = sequence
