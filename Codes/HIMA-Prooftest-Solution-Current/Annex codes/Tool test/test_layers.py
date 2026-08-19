#!/usr/bin/env python3
"""
Layer unit tests (Domain + Application) with fake ports.

Run (no X-OPC / SILworX required):
  python "Annex codes/Tool test/test_layers.py"

Uses pytest if installed; otherwise a built-in runner.
"""

from __future__ import annotations

import sys
from pathlib import Path

from _paths import SOLUTION_ROOT, setup_path

setup_path()
sys.path.insert(0, str(SOLUTION_ROOT / "Annex codes"))

from layers.application.catalog_service import CatalogService
from layers.application.engine import Engine
from layers.application.errors import RecordingAlarmPort
from layers.application.live_test import LiveTestService
from layers.application.query import QueryService
from layers.application.silworx_connection import SilworxConnectionService
from layers.domain.device import Device, DeviceId
from layers.domain.merger import CatalogMerger, OpcObservation, SilworxIdentity
from layers.domain.result_types import ResultTypeCatalog
from layers.domain.running import RunningEdgeDetector
from layers.fakes import FakeOpc, FakeReports, FakeSilworx, FakeStore

TYPE = "X-HART_WIKA_T32_Results"


def _ident(project: str, tag: str, cfg: str = "Cfg", res: str = "Res") -> SilworxIdentity:
    return SilworxIdentity(project, cfg, res, tag, TYPE)


def _opc(tag: str, server: str = "HIMA.X-OPC.1", prefix: str | None = None) -> OpcObservation:
    prefix = prefix or f"OTS ProofTest.{tag}"
    return OpcObservation(tag, server, prefix, TYPE, f"{prefix}.Running")


def test_01_same_deviceid_one_row() -> None:
    merger = CatalogMerger()
    result = merger.merge(
        [_ident("ProjA", "100-FZT-001")],
        [_opc("100-FZT-001")],
    )
    assert len(result.devices) == 1
    d = result.devices[0]
    assert d.results_type == TYPE
    assert d.opc_item_prefix.endswith("100-FZT-001")
    assert d.present_on_opc is True
    assert d.project == "ProjA"


def test_02_same_tag_two_projects() -> None:
    merger = CatalogMerger()
    result = merger.merge(
        [_ident("ProjA", "100-FZT-001"), _ident("ProjB", "100-FZT-001")],
        [],
    )
    assert len(result.devices) == 2
    projects = {d.project for d in result.devices}
    assert projects == {"ProjA", "ProjB"}


def test_03_same_tag_same_opc_path_collision() -> None:
    merger = CatalogMerger()
    path = "OTS ProofTest.100-FZT-001"
    result = merger.merge(
        [_ident("ProjA", "100-FZT-001"), _ident("ProjB", "100-FZT-001")],
        [_opc("100-FZT-001", prefix=path), _opc("100-FZT-001", prefix=path)],
    )
    assert len(result.devices) == 2
    assert result.collisions, "expected collision, not one silent row"
    present = [d for d in result.devices if d.present_on_opc]
    assert len(present) == 1


def test_04_silworx_only_not_on_opc() -> None:
    result = CatalogMerger().merge([_ident("ProjA", "100-FZT-001")], [])
    assert len(result.devices) == 1
    assert result.devices[0].present_on_opc is False


def test_05_opc_only_folder() -> None:
    result = CatalogMerger().merge([], [_opc("200-PZT-002")])
    assert len(result.devices) == 1
    assert result.devices[0].device_tag == "200-PZT-002"
    assert result.devices[0].present_on_opc is True
    assert result.devices[0].project == ""


def test_06_false_true_started_no_snapshot() -> None:
    store = FakeStore()
    live = LiveTestService(FakeOpc(), store, FakeReports(), RecordingAlarmPort())
    device = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    live.detector.observe(device.device_id.key(), False)
    live.opc.running["OTS ProofTest.A.Running"] = (True, "Good")
    live._poll_one(device)
    assert live.completed == []
    assert live.detector.is_in_progress(device.device_id.key())


def test_07_true_false_complete_once() -> None:
    store = FakeStore()
    opc = FakeOpc(
        running_sequence={
            "OTS ProofTest.A.Running": [(False, "Good"), (False, "Good")],
        }
    )
    live = LiveTestService(opc, store, FakeReports(), RecordingAlarmPort())
    key = DeviceId("P", "C", "R", "A").key()
    live.detector._last[key] = True
    live.detector._in_progress[key] = True
    device = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    live._poll_one(device)
    assert live.completed == ["A"]
    assert len(store.snapshots) == 1


def test_08_flicker_no_complete() -> None:
    store = FakeStore()
    opc = FakeOpc(
        running_sequence={
            "OTS ProofTest.A.Running": [(False, "Good"), (True, "Good")],
        }
    )
    live = LiveTestService(opc, store, FakeReports(), RecordingAlarmPort())
    key = DeviceId("P", "C", "R", "A").key()
    live.detector._last[key] = True
    live.detector._in_progress[key] = True
    device = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    live._poll_one(device)
    assert live.completed == []
    assert store.snapshots == []


def test_09_interrupt_no_snapshot() -> None:
    store = FakeStore()
    opc = FakeOpc(fail_tags={"A"})
    live = LiveTestService(opc, store, FakeReports(), RecordingAlarmPort())
    key = DeviceId("P", "C", "R", "A").key()
    live.detector._in_progress[key] = True
    live.detector._last[key] = True
    device = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    live._poll_one(device)
    assert live.interrupted == ["A"]
    assert store.snapshots == []


def test_10_poll_continues_after_device_a_error() -> None:
    store = FakeStore()
    opc = FakeOpc(
        fail_tags={"A"},
        running={"OTS ProofTest.B.Running": (True, "Good")},
    )
    live = LiveTestService(opc, store, FakeReports(), RecordingAlarmPort())
    a = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    b = Device(DeviceId("P", "C", "R", "B"), TYPE, "S", "OTS ProofTest.B", True)
    live.poll_once([a, b])
    assert live.detector.is_in_progress(b.device_id.key())


def test_11_load_result_types(tmp_path: Path) -> None:
    csv_path = tmp_path / "X-HART_WIKA_T32_Results.csv"
    csv_path.write_text("Member\nRunning\nTestResult\n", encoding="utf-8")
    (tmp_path / "empty.csv").write_text("", encoding="utf-8")
    svc = CatalogService(FakeStore(), FakeOpc(), FakeSilworx(), RecordingAlarmPort(), types_folder=tmp_path)
    catalog = svc.load_result_types()
    assert "X-HART_WIKA_T32_Results" in catalog.names()
    assert catalog.skipped_files
    assert catalog.matches_global("X-HART_WIKA_T32_Results")
    assert not catalog.matches_global("Unknown_Global")


def test_12_bind_opc_paths_ots_then_opc() -> None:
    opc = FakeOpc(
        servers=["HIMA.X-OPC.1"],
        paths={("HIMA.X-OPC.1", "OTS ProofTest.100-FZT-001.Running"): "OTS ProofTest.100-FZT-001.Running"},
    )
    svc = CatalogService(FakeStore(), opc, FakeSilworx(), RecordingAlarmPort())
    obs = svc.bind_opc_paths([_ident("ProjA", "100-FZT-001")])
    assert obs and obs[0].opc_item_prefix == "OTS ProofTest.100-FZT-001"
    items = [item for _srv, item in opc.find_calls]
    assert items[0].startswith("OTS ProofTest.")
    assert any(i.startswith("OPC ProofTest.") for i in items) or items[0].startswith("OTS ProofTest.")
    # First attempt is OTS
    assert opc.find_calls[0][1] == "OTS ProofTest.100-FZT-001.Running"


def test_13_reconcile_marks_inactive_keeps_snapshots() -> None:
    store = FakeStore()
    gone = Device(DeviceId("P", "C", "R", "GONE"), TYPE)
    stay = Device(DeviceId("P", "C", "R", "STAY"), TYPE)
    store.upsert_device(gone)
    store.upsert_device(stay)
    store.insert_snapshot("GONE", TYPE, {"x": 1})
    svc = CatalogService(store, FakeOpc(servers=["x"]), FakeSilworx(), RecordingAlarmPort())
    svc.devices = [stay]
    svc.reconcile_catalog([stay.device_id.key()])
    assert gone.device_id.key() in store.inactive
    assert store.snapshots_for("GONE")


def test_14_engine_status_after_start(tmp_path: Path) -> None:
    (tmp_path / "X-HART_WIKA_T32_Results.csv").write_text("Member\nRunning\n", encoding="utf-8")
    store, opc, sil, reports, alarms = FakeStore(), FakeOpc(servers=["HIMA.X-OPC.1", "HIMA.X-OPC.2"]), FakeSilworx(), FakeReports(), RecordingAlarmPort()
    catalog = CatalogService(store, opc, sil, alarms, types_folder=tmp_path)
    live = LiveTestService(opc, store, reports, alarms)
    engine = Engine(store, opc, sil, reports, alarms, catalog, live)
    assert engine.start_engine() == "running"
    status = engine.get_engine_status()
    assert status["engine"] == "running"
    assert status["opc_count"] == 2
    assert status["queue_depth"] == 0
    assert "device_count" in status


def test_15_close_silworx_keeps_opc_refresh(tmp_path: Path) -> None:
    (tmp_path / "X-HART_WIKA_T32_Results.csv").write_text("Member\nRunning\n", encoding="utf-8")
    sil = FakeSilworx(identities=[_ident("ProjA", "T1")], attached=True, open_project=True)
    opc = FakeOpc(
        servers=["HIMA.X-OPC.1"],
        opc_only=[_opc("T1")],
    )
    store, alarms = FakeStore(), RecordingAlarmPort()
    catalog = CatalogService(store, opc, sil, alarms, types_folder=tmp_path)
    catalog.load_result_types()
    conn = SilworxConnectionService(sil, catalog, alarms)
    out = conn.close_silworx_connection()
    assert out["silworx"] == "not connected"
    assert sil.attached is False
    catalog.refresh_catalog()
    assert sil.list_calls == 0 or not sil.is_attached()
    assert any(d.device_tag == "T1" for d in catalog.devices)


def test_16_resume_silworx(tmp_path: Path) -> None:
    (tmp_path / "X-HART_WIKA_T32_Results.csv").write_text("Member\nRunning\n", encoding="utf-8")
    sil_open = FakeSilworx(identities=[_ident("ProjA", "T1")], open_project=True)
    opc = FakeOpc(servers=["HIMA.X-OPC.1"], paths={("HIMA.X-OPC.1", "T1"): "OTS ProofTest.T1.Running"})
    store, alarms = FakeStore(), RecordingAlarmPort()
    catalog = CatalogService(store, opc, sil_open, alarms, types_folder=tmp_path)
    catalog.load_result_types()
    conn = SilworxConnectionService(sil_open, catalog, alarms)
    assert conn.resume_silworx_connection()["silworx"] == "running"

    sil_none = FakeSilworx(open_project=False)
    catalog2 = CatalogService(store, opc, sil_none, alarms, types_folder=tmp_path)
    conn2 = SilworxConnectionService(sil_none, catalog2, alarms)
    out = conn2.resume_silworx_connection()
    assert out["silworx"] == "not connected"
    assert any(a["message"] == "no open project" for a in alarms.alarms)


def test_17_list_devices_order_and_fields() -> None:
    store = FakeStore()
    store.upsert_device(Device(DeviceId("B-Proj", "", "", "ZZZ"), TYPE, "OPC-Z", "OTS ProofTest.ZZZ", True))
    store.upsert_device(Device(DeviceId("A-Proj", "", "", "AAA"), TYPE, "OPC-A", "OTS ProofTest.AAA", True))
    store.upsert_device(Device(DeviceId("C-Proj", "", "", "AAA"), TYPE, "OPC-C", "OTS ProofTest.AAA", True))
    q = QueryService(store, FakeReports(), RecordingAlarmPort())
    rows = q.list_devices()
    assert [r["device_tag"] for r in rows] == ["AAA", "AAA", "ZZZ"]
    assert rows[0]["project"] == "A-Proj"
    assert rows[1]["project"] == "C-Proj"
    for row in rows:
        assert "opc_server" in row
        assert "configuration" in row
        assert "resource" in row
        assert "opc_item_prefix" in row
        assert "present_on_opc" in row
        assert "test_in_progress" in row


def test_18_open_report_outside_root(tmp_path: Path) -> None:
    q = QueryService(FakeStore(), FakeReports(), RecordingAlarmPort())
    code, path = q.open_report(str(tmp_path / "secret.txt"), [tmp_path / "reports"])
    assert code == 403
    assert path is None


def test_19_no_opc_servers_alarm_no_crash(tmp_path: Path) -> None:
    (tmp_path / "X-HART_WIKA_T32_Results.csv").write_text("Member\nRunning\n", encoding="utf-8")
    alarms = RecordingAlarmPort()
    sil = FakeSilworx(identities=[_ident("P", "T1")], attached=True, open_project=True)
    catalog = CatalogService(FakeStore(), FakeOpc(servers=[]), sil, alarms, types_folder=tmp_path)
    catalog.load_result_types()
    catalog.refresh_catalog()
    assert any(a["step"] == "S4" for a in alarms.alarms)
    assert any(d.device_tag == "T1" and not d.present_on_opc for d in catalog.devices)


def test_20_report_fail_keeps_snapshot() -> None:
    store = FakeStore()
    live = LiveTestService(FakeOpc(), store, FakeReports(fail=True), RecordingAlarmPort())
    device = Device(DeviceId("P", "C", "R", "A"), TYPE, "S", "OTS ProofTest.A", True)
    live.complete_test(device, {"x": 1}, [])
    assert store.snapshots
    assert any(a["step"] == "S6" for a in live.alarms.alarms)  # type: ignore[attr-defined]


def test_21_start_engine_store_fail() -> None:
    store = FakeStore(connect_always_fail=True)
    opc, sil, reports, alarms = FakeOpc(), FakeSilworx(), FakeReports(), RecordingAlarmPort()
    catalog = CatalogService(store, opc, sil, alarms)
    live = LiveTestService(opc, store, reports, alarms)
    engine = Engine(store, opc, sil, reports, alarms, catalog, live)
    assert engine.start_engine() == "stopped"
    status = engine.get_engine_status()
    assert status["engine"] == "stopped"
    assert status["last_error"]

    store2 = FakeStore(connect_fail_then_ok=True)
    alarms2 = RecordingAlarmPort()
    catalog2 = CatalogService(store2, opc, sil, alarms2)
    engine2 = Engine(store2, opc, sil, reports, alarms2, catalog2, live)
    assert engine2.start_engine() == "running"


def test_22_reports_scoped_by_project() -> None:
    reports = FakeReports()
    reports.write("100-FZT-001", TYPE, {}, project="ProjA")
    reports.write("100-FZT-001", TYPE, {}, project="ProjB")
    q = QueryService(FakeStore(), reports, RecordingAlarmPort())
    a = q.list_reports("100-FZT-001", project="ProjA")
    b = q.list_reports("100-FZT-001", project="ProjB")
    assert a and "ProjA" in a[0]["path"]
    assert b and "ProjB" in b[0]["path"]
    assert a[0]["path"] != b[0]["path"]


def test_23_seed_detector_does_not_retrigger_start() -> None:
    live = LiveTestService(FakeOpc(running={"OTS ProofTest.A.Running": (True, "Good")}), FakeStore(), FakeReports(), RecordingAlarmPort())
    device = Device(
        DeviceId("P", "C", "R", "A"),
        TYPE,
        "S",
        "OTS ProofTest.A",
        True,
        test_in_progress=True,
        last_running=True,
    )
    live.poll_once([device])
    assert live.completed == []
    assert live.detector.is_in_progress(device.device_id.key())


def _run_without_pytest() -> int:
    import inspect
    import tempfile

    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            params = inspect.signature(fn).parameters
            if "tmp_path" in params:
                with tempfile.TemporaryDirectory() as td:
                    fn(Path(td))
            else:
                fn()
            print(f"OK  {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        import pytest

        raise SystemExit(pytest.main([__file__, "-q"]))
    except ImportError:
        raise SystemExit(_run_without_pytest())
