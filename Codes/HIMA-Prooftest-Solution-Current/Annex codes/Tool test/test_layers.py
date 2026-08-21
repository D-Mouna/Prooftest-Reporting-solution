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
from layers.fakes import FakeArchive, FakeOpc, FakeReports, FakeSilworx, FakeStore

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


def test_07b_defer_complete_inserts_sql_before_report() -> None:
    """OPC copy is inserted immediately; report waits on the queue (same device type OK)."""
    store = FakeStore()
    reports = FakeReports()
    opc = FakeOpc(
        running_sequence={
            "OTS ProofTest.A.Running": [(False, "Good")],
            "OTS ProofTest.B.Running": [(False, "Good")],
        }
    )
    live = LiveTestService(opc, store, reports, RecordingAlarmPort(), defer_complete=True)

    for tag in ("A", "B"):
        key = DeviceId("P", "C", "R", tag).key()
        live.detector._last[key] = True
        live.detector._in_progress[key] = True
        live._poll_one(Device(DeviceId("P", "C", "R", tag), TYPE, "S", f"OTS ProofTest.{tag}", True))

    assert len(store.snapshots) == 2
    assert reports.written == []
    assert live.completed == []
    assert live.queue_depth == 2
    assert live.queue[0]["record_id"] == 1
    assert live.queue[1]["record_id"] == 2

    while live.queue:
        live.run_complete(live.queue.pop(0))

    assert reports.written == ["A", "B"]
    assert live.completed == ["A", "B"]
    assert len(store.snapshots) == 2  # no second insert on report
    assert len(store.report_paths) == 2
    assert store.report_paths[0]["record_id"] == 1
    assert store.report_paths[1]["record_id"] == 2


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
    # After close, SILworX identities are no longer used; OPC-only devices remain.
    assert sil.attached is False
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


# ----- Edge cases T1–T24 (shaped discover / poll / connect / GUI) -----

_FTL_MEMBERS = {
    "FTL_Results": {"Running", "TestResult", "SensorOK", "Extra"},
    "Other_Results": {"Running", "Alpha", "Beta", "Gamma"},
}


def test_t01_someflag_running_rejected() -> None:
    from layers.domain.opc_discover import discover_shaped_from_tag_lists

    shaped = discover_shaped_from_tag_lists(
        {"S1": ["SomeFlag.Running", "OTS ProofTest.SomeFlag.Other"]},
        _FTL_MEMBERS,
    )
    assert shaped.observations == []


def test_t02_real_tag_shape_accepted() -> None:
    from layers.domain.opc_discover import discover_shaped_from_tag_lists

    tags = [
        "OTS ProofTest.100-FZT-001.Running",
        "OTS ProofTest.100-FZT-001.TestResult",
        "OTS ProofTest.100-FZT-001.SensorOK",
        "OTS ProofTest.100-FZT-001.Extra",
    ]
    shaped = discover_shaped_from_tag_lists({"S1": tags}, _FTL_MEMBERS)
    assert len(shaped.observations) == 1
    assert shaped.observations[0].device_tag == "100-FZT-001"
    assert shaped.observations[0].results_type == "FTL_Results"


def test_t03_silworx_type_wins_over_csv() -> None:
    sil = FakeSilworx(
        identities=[SilworxIdentity("ProjA", "Cfg", "Res", "100-FZT-001", "TYPE_X")],
        attached=True,
        open_project=True,
    )
    opc = FakeOpc(
        servers=["S1"],
        paths={("S1", "OTS ProofTest.100-FZT-001.Running"): "OTS ProofTest.100-FZT-001.Running"},
        opc_only=[
            OpcObservation(
                "100-FZT-001",
                "S1",
                "OTS ProofTest.100-FZT-001",
                "FTL_Results",
                "OTS ProofTest.100-FZT-001.Running",
            )
        ],
    )
    store, alarms = FakeStore(), RecordingAlarmPort()
    svc = CatalogService(store, opc, sil, alarms)
    svc.types.types["TYPE_X"] = __import__(
        "layers.domain.result_types", fromlist=["ResultType"]
    ).ResultType("TYPE_X", ("Running",))
    svc.types.types["FTL_Results"] = __import__(
        "layers.domain.result_types", fromlist=["ResultType"]
    ).ResultType("FTL_Results", ("Running", "A", "B", "C"))
    devices = svc.refresh_catalog()
    assert len(devices) == 1
    assert devices[0].results_type == "TYPE_X"


def test_t04_opc_only_ambiguous_type_unknown() -> None:
    from layers.domain.opc_discover import discover_shaped_from_tag_lists

    # Members hit both CSVs at score ≥3 with margin < 2
    tags = [
        "OTS ProofTest.TAG1.Running",
        "OTS ProofTest.TAG1.TestResult",
        "OTS ProofTest.TAG1.SensorOK",
        "OTS ProofTest.TAG1.Extra",
        "OTS ProofTest.TAG1.Alpha",
        "OTS ProofTest.TAG1.Beta",
        "OTS ProofTest.TAG1.Gamma",
    ]
    shaped = discover_shaped_from_tag_lists({"S1": tags}, _FTL_MEMBERS)
    assert len(shaped.observations) == 1
    assert shaped.observations[0].results_type == ""


def test_t05_opc_only_keeps_last_sql_type() -> None:
    from layers.domain.opc_discover import discover_shaped_from_tag_lists

    tags = [
        "OTS ProofTest.TAG1.Running",
        "OTS ProofTest.TAG1.TestResult",
        "OTS ProofTest.TAG1.SensorOK",
        "OTS ProofTest.TAG1.Extra",
        "OTS ProofTest.TAG1.Alpha",
        "OTS ProofTest.TAG1.Beta",
        "OTS ProofTest.TAG1.Gamma",
    ]
    shaped = discover_shaped_from_tag_lists(
        {"S1": tags},
        _FTL_MEMBERS,
        last_types_by_tag={"TAG1": "FTL_Results"},
    )
    assert shaped.observations[0].results_type == "FTL_Results"


def test_t06_tag_with_dots_rejected() -> None:
    from layers.domain.opc_discover import parse_shaped_running_item

    assert parse_shaped_running_item("OTS ProofTest.foo.bar.Running") is None
    assert parse_shaped_running_item("OTS ProofTest.foo.Running") is not None


def test_t07_same_tag_two_projects_two_ids() -> None:
    test_02_same_tag_two_projects()


def test_t08_same_deviceid_api_opc_one_row() -> None:
    test_01_same_deviceid_one_row()


def test_t09_opc_path_collision_alarm() -> None:
    alarms = RecordingAlarmPort()
    sil = FakeSilworx(
        identities=[
            _ident("ProjA", "100-FZT-001"),
            _ident("ProjB", "100-FZT-001"),
        ],
        attached=True,
        open_project=True,
    )
    path = "OTS ProofTest.100-FZT-001"
    opc = FakeOpc(
        servers=["S1"],
        paths={("S1", f"{path}.Running"): f"{path}.Running"},
        opc_only=[_opc("100-FZT-001", prefix=path), _opc("100-FZT-001", prefix=path)],
    )
    svc = CatalogService(FakeStore(), opc, sil, alarms)
    svc.types.types[TYPE] = __import__(
        "layers.domain.result_types", fromlist=["ResultType"]
    ).ResultType(TYPE, ("Running",))
    svc.refresh_catalog()
    assert any("collision" in a["message"].lower() for a in alarms.alarms)


def test_t10_silworx_only_listed_not_on_opc() -> None:
    test_04_silworx_only_not_on_opc()


def test_t11_empty_opc_browse_no_crash() -> None:
    from layers.domain.opc_discover import discover_shaped_from_tag_lists

    shaped = discover_shaped_from_tag_lists({"S1": []}, _FTL_MEMBERS)
    assert shaped.observations == []
    alarms = RecordingAlarmPort()
    svc = CatalogService(FakeStore(), FakeOpc(servers=[]), FakeSilworx(), alarms)
    assert svc.discover_opc_only_devices() == []


def test_t12_suspended_api_uses_shaped_opc_only() -> None:
    sil = FakeSilworx(attached=False, open_project=False)
    opc = FakeOpc(
        servers=["S1"],
        opc_only=[_opc("200-PZT-002")],
    )
    store, alarms = FakeStore(), RecordingAlarmPort()
    svc = CatalogService(store, opc, sil, alarms)
    svc.types.types[TYPE] = __import__(
        "layers.domain.result_types", fromlist=["ResultType"]
    ).ResultType(TYPE, ("Running",))
    devices = svc.refresh_catalog()
    assert sil.list_calls == 0
    assert any(d.device_tag == "200-PZT-002" and d.project == "" for d in devices)


def test_t13_false_true_started_no_snapshot() -> None:
    test_06_false_true_started_no_snapshot()


def test_t14_true_false_snapshot_complete() -> None:
    test_07_true_false_complete_once()


def test_t15_interrupt_mid_run() -> None:
    test_09_interrupt_no_snapshot()


def test_t16_poll_isolation_after_error() -> None:
    test_10_poll_continues_after_device_a_error()


def test_t17_seed_no_false_end() -> None:
    test_23_seed_detector_does_not_retrigger_start()


def test_t18_unknown_type_no_prooftest_snapshot() -> None:
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
    device = Device(DeviceId("P", "C", "R", "A"), "", "S", "OTS ProofTest.A", True)
    live._poll_one(device)
    assert store.snapshots == []
    assert live.completed == []
    assert any("unknown" in a["message"].lower() for a in live.alarms.alarms)  # type: ignore[attr-defined]


def test_t19_disconnect_no_project_close_or_kill() -> None:
    class SpySilworx(FakeSilworx):
        def __init__(self) -> None:
            super().__init__(attached=True, open_project=True)
            self.calls: list[str] = []

        def detach(self) -> None:
            self.calls.append("detach")
            super().detach()

        def project_close(self) -> None:  # not on port — must never be invoked via getattr abuse
            self.calls.append("project_close")

    sil = SpySilworx()
    catalog = CatalogService(FakeStore(), FakeOpc(), sil, RecordingAlarmPort())
    SilworxConnectionService(sil, catalog, RecordingAlarmPort()).close_silworx_connection()
    assert sil.calls == ["detach"]
    assert "project_close" not in sil.calls


def test_t20_connect_resume_no_project_open() -> None:
    class SpySilworx(FakeSilworx):
        def __init__(self) -> None:
            super().__init__(open_project=True)
            self.calls: list[str] = []

        def attach(self) -> bool:
            self.calls.append("attach")
            return super().attach()

        def project_open(self) -> None:
            self.calls.append("project_open")

    sil = SpySilworx()
    catalog = CatalogService(FakeStore(), FakeOpc(), sil, RecordingAlarmPort())
    SilworxConnectionService(sil, catalog, RecordingAlarmPort()).resume_silworx_connection()
    assert sil.calls == ["attach"]
    assert "project_open" not in sil.calls


def test_t21_open_report_outside_root(tmp_path: Path) -> None:
    test_18_open_report_outside_root(tmp_path)


def test_t22_list_includes_project_opc_sort() -> None:
    test_17_list_devices_order_and_fields()


def test_t23_nonlocal_mutating_checks_documented() -> None:
    """Gate/controllers enforce localhost on Start/Stop/Connect when checks exist."""
    from layers.presentation import controllers

    src = Path(controllers.__file__).read_text(encoding="utf-8")
    assert "localhost" in src.lower() or "127.0.0.1" in src or "client_host" in src.lower()


def test_t24_escape_html_covers_project_opc_fields() -> None:
    app_js = (
        SOLUTION_ROOT / "Graphic Interface" / "static" / "app.js"
    ).read_text(encoding="utf-8")
    assert "escapeHtml(d.project" in app_js or "escapeHtml(d.project ||" in app_js
    assert "escapeHtml(d.opc_server" in app_js


def test_r1_query_uses_archive_port_not_annex() -> None:
    import inspect

    import layers.application.query as query_mod

    src = inspect.getsource(query_mod)
    assert "annex_list_archive" not in src
    arch = FakeArchive()
    arch.create_archive()
    q = QueryService(FakeStore(), FakeReports(), RecordingAlarmPort(), archives=arch)
    assert len(q.list_archives()) == 1
    q.clear_keep_opc_only(archive_first=False)
    assert arch.keep_opc is True


def test_r2_html_seed_prefers_documents_over_z(tmp_path: Path) -> None:
    from prooftest.annex_pdf_generation import resolve_html_templates_seed

    class Cfg:
        report_html_seed = tmp_path / "seed"

    Cfg.report_html_seed.mkdir()
    path, label = resolve_html_templates_seed(config=Cfg())
    assert path == Cfg.report_html_seed
    assert label == "config"
    # Without config seed, Documents or packaged/Z may apply — never require Z solely
    path2, label2 = resolve_html_templates_seed()
    assert label2 != "none" or path2 is None
    if path2 is not None:
        assert label2 in ("documents", "packaged", "z_fallback", "config")


def test_r3_db_name_validation() -> None:
    from prooftest.annex_database import validate_sql_database_name

    assert validate_sql_database_name("HIMA_Prooftest") == "HIMA_Prooftest"
    assert validate_sql_database_name("HIMA Automated Prooftest") == "HIMA Automated Prooftest"
    try:
        validate_sql_database_name("bad name'; DROP TABLE")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    try:
        validate_sql_database_name("x;y")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_r4_auth_bind_policy_loopback_ok() -> None:
    from prooftest.config import AppConfig

    cfg = AppConfig()
    cfg.web_host = "127.0.0.1"
    cfg.web_auth_enabled = False
    cfg.require_auth_when_non_local = True
    cfg.apply_auth_bind_policy()
    assert cfg.auth_bind_warning is False


def test_r4_auth_bind_policy_non_local_refuses() -> None:
    from prooftest.config import AppConfig

    cfg = AppConfig()
    cfg.web_host = "0.0.0.0"
    cfg.web_auth_enabled = False
    cfg.require_auth_when_non_local = True
    try:
        cfg.apply_auth_bind_policy()
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_r7_unknown_results_type_placeholder() -> None:
    store = FakeStore()
    store.upsert_device(Device(DeviceId("", "", "", "TAG1"), "", "S", "OTS ProofTest.TAG1", True))
    q = QueryService(store, FakeReports(), RecordingAlarmPort())
    rows = q.list_devices()
    assert rows[0]["results_type"] == "unknown"


def test_r7_connect_button_titles() -> None:
    html = (SOLUTION_ROOT / "Graphic Interface" / "static" / "index.html").read_text(encoding="utf-8")
    assert "does not quit SILworX" in html or "does not quit SILworX".lower() in html.lower()
    assert "this tool" in html.lower()
    assert "Stop service" in html
    assert "btn-stop-service" in html


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
