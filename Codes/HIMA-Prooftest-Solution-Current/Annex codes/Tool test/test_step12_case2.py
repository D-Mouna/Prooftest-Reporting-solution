#!/usr/bin/env python3
"""
Gate 12 — OPC device-list path (unified mode; former Case 2).

Verifies:
  1. detect_deployment_case always returns 1 (unified mode).
  2. sync_schema_case2 creates ProofTest_* tables from Results Structure CSVs.
  3. sync_device_list_from_opc discovers devices from OPC tag matching (no API).
  4. service.refresh() runs API and OPC together; when API returns None the merged source is opc_fallback.
  5. Background sync still polls the device list while SILworX/API is down (same parallel function; API no-ops).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch

from _paths import CONFIG_INI, SYNC_MARKERS, TEST_DATA, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.results_csv import RESULTS_TYPE_FILES, load_all_structures, structure_to_sql_table
from prooftest.service import ProoftestService
from prooftest.step01_setup import detect_deployment_case
from prooftest.step03_device_list import ApiDiscoveredDevice, sync_device_list_case1_via_api, sync_device_list_from_opc
from prooftest.step07_triggers import Case1SyncTriggers, run_background_sync_iteration

TEST_DEVICE = "GATE12-HMI-DEVICE"
TEST_TYPE = "X-HART_WIKA_T32_Results"
MOCK_SERVER = "Mock.X_OPC.Server"


def _open_gate_database(config: AppConfig) -> Database:
    config.sqlite_path = TEST_DATA / "gate12_case2.db"
    config.fallback_sqlite = True
    alarms = AlarmManager()
    db = Database(config, alarms)
    db._try_sql_server = lambda: False  # type: ignore[method-assign]
    db.connect()
    return db


class MockOpcUnified:
    """Minimal OPC stub for OPC device discovery."""

    prooftest_branches = ["OTS ProofTest", "OPC ProofTest"]

    def __init__(self, structure_members: List[str], device_tag: str = TEST_DEVICE) -> None:
        self._prefix = f"OTS ProofTest.{device_tag}"
        self._tags = [f"{self._prefix}.Running"]
        for member in structure_members:
            short = member.split(".")[-1]
            if short.lower() != "running":
                self._tags.append(f"{self._prefix}.{short}")

    def discover_servers(self) -> List[str]:
        return [MOCK_SERVER]

    def list_tags_all_servers(self, servers: List[str]) -> Dict[str, List[str]]:
        return {MOCK_SERVER: self._tags}

    def invalidate_cache(self) -> None:
        return


def test_unified_case_always_one() -> int:
    with patch("prooftest.step01_setup.is_silworx_installed", return_value=False):
        case = detect_deployment_case(Path(r"C:\ProgramData"))
    if case != 1:
        print(f"FAIL detect_deployment_case expected 1 (unified), got {case}")
        return 1
    print("OK  Unified mode (deployment_case=1) even when SILworX is not installed")
    return 0


def test_sync_schema_from_structures() -> int:
    config = AppConfig.load(CONFIG_INI)
    config.deployment_case = 1
    db = _open_gate_database(config)
    structures = load_all_structures(config.results_structures)

    db.sync_schema_case2(config.sql_templates, structures)

    missing = [
        structure_to_sql_table(name)
        for name in RESULTS_TYPE_FILES
        if not db._table_exists(structure_to_sql_table(name))
    ]
    if missing:
        print(f"FAIL sync_schema_case2 missing tables: {missing}")
        return 1
    print(f"OK  sync_schema_case2 created {len(RESULTS_TYPE_FILES)} ProofTest_* tables")
    return 0


def test_opc_device_list() -> int:
    config = AppConfig.load(CONFIG_INI)
    config.deployment_case = 1
    db = _open_gate_database(config)
    all_structures = load_all_structures(config.results_structures)
    structure = all_structures[TEST_TYPE]
    structures = {TEST_TYPE: structure}
    opc = MockOpcUnified(structure.member_short_names())

    active = sync_device_list_from_opc(config, db, opc, structures)
    if TEST_DEVICE not in active:
        print(f"FAIL sync_device_list_from_opc did not discover {TEST_DEVICE}")
        return 1

    devices = db.list_active_devices()
    row = next(d for d in devices if d["device_tag"] == TEST_DEVICE)
    if row["results_type"] != TEST_TYPE:
        print(f"FAIL results_type={row['results_type']!r}")
        return 1
    if row.get("configuration") or row.get("resource"):
        print("FAIL OPC path must not set Configuration/Resource from API")
        return 1
    if not row.get("opc_server") or not row.get("opc_item_prefix"):
        print("FAIL OPC_Server / OPC_ItemPrefix not populated")
        return 1
    if row.get("source_kind") != "opc" or row.get("source_name") != MOCK_SERVER:
        print(f"FAIL OPC source={row.get('source_kind')!r}/{row.get('source_name')!r}")
        return 1

    empty_opc = MockOpcUnified([], device_tag="unused")
    sync_device_list_from_opc(config, db, empty_opc, structures)
    row2 = db.list_active_devices()
    if any(d["device_tag"] == TEST_DEVICE for d in row2):
        print("FAIL device without reports still listed after it disappeared from OPC")
        return 1

    print("OK  OPC device list add / delete-when-no-reports")
    return 0


def test_service_refresh_opc_fallback() -> int:
    config = AppConfig.load(CONFIG_INI)
    config.deployment_case = 1
    db = _open_gate_database(config)
    structures = load_all_structures(config.results_structures)
    structure = structures[TEST_TYPE]
    opc = MockOpcUnified(structure.member_short_names())

    service = ProoftestService(config)
    service.db = db
    service.structures = structures
    service.opc = opc  # type: ignore[assignment]

    with patch(
        "prooftest.step03_device_list.try_discover_devices_via_api",
        return_value=None,
    ):
        result = service.refresh(manual=True)

    if result.get("active_devices", 0) < 1:
        print(f"FAIL refresh OPC fallback active_devices={result.get('active_devices')}")
        return 1
    state = db.get_service_state()
    if state.get("deployment_case") != "1":
        print(f"FAIL deployment_case state={state.get('deployment_case')!r} (expected 1)")
        return 1
    if state.get("device_list_source") != "opc_fallback":
        print(f"FAIL expected opc_fallback, got {state.get('device_list_source')!r}")
        return 1
    print("OK  service.refresh() uses OPC contribution when API returns None; stays unified (case 1)")
    return 0


def test_parallel_api_opc_merge() -> int:
    config = AppConfig.load(CONFIG_INI)
    config.deployment_case = 1
    db = _open_gate_database(config)
    all_structures = load_all_structures(config.results_structures)
    structure = all_structures[TEST_TYPE]
    structures = {TEST_TYPE: structure}
    opc = MockOpcUnified(structure.member_short_names())
    case1_sync = Case1SyncTriggers(config, SYNC_MARKERS)
    api_only = ApiDiscoveredDevice(
        device_tag="API-ONLY-DEV",
        results_type=TEST_TYPE,
        configuration="CfgA",
        resource="ResA",
        gv_node_path="/cfg/res",
        silworx_project="DemoProject",
    )

    with patch(
        "prooftest.step03_device_list.try_discover_devices_via_api",
        return_value=[api_only],
    ):
        active, source = sync_device_list_case1_via_api(
            config, db, structures, case1_sync, opc
        )

    if source != "api+opc":
        print(f"FAIL expected api+opc, got {source!r} active={active}")
        return 1
    if TEST_DEVICE not in active or "API-ONLY-DEV" not in active:
        print(f"FAIL merge missing tags: {active}")
        return 1
    devices = db.list_active_devices()
    row_api = next(d for d in devices if d["device_tag"] == "API-ONLY-DEV")
    if row_api.get("configuration") != "CfgA" or row_api.get("resource") != "ResA":
        print("FAIL API metadata not kept on API-only device")
        return 1
    row_opc = next(d for d in devices if d["device_tag"] == TEST_DEVICE)
    if row_opc.get("configuration") or row_opc.get("resource"):
        print("FAIL OPC-only device must have NULL Configuration/Resource")
        return 1
    if not row_opc.get("opc_server"):
        print("FAIL OPC-only device missing OPC_Server")
        return 1
    if row_opc.get("source_kind") != "opc" or row_opc.get("source_name") != MOCK_SERVER:
        print(f"FAIL OPC source={row_opc.get('source_kind')!r}/{row_opc.get('source_name')!r}")
        return 1
    if row_opc.get("source_label") != f"OPC: {MOCK_SERVER}":
        print(f"FAIL OPC source_label={row_opc.get('source_label')!r}")
        return 1
    if row_api.get("source_kind") != "project" or row_api.get("source_name") != "DemoProject":
        print(f"FAIL API-only source={row_api.get('source_kind')!r}/{row_api.get('source_name')!r}")
        return 1
    if row_api.get("source_label") != "Project: DemoProject":
        print(f"FAIL API-only source_label={row_api.get('source_label')!r}")
        return 1
    print("OK  Parallel API+OPC merge (union of tags; API metadata; OPC prefix; per-device source)")
    return 0


def test_background_opc_poll_when_api_down() -> int:
    config = AppConfig.load(CONFIG_INI)
    config.deployment_case = 1
    config.device_list_poll_sec = 0.1
    config.case1_sync_poll_sec = 0.1
    db = _open_gate_database(config)
    structures = load_all_structures(config.results_structures)
    structure = structures[TEST_TYPE]
    opc = MockOpcUnified(structure.member_short_names())

    service = ProoftestService(config)
    service.db = db
    service.structures = structures
    service.opc = opc  # type: ignore[assignment]
    service._last_device_sync = 0.0
    service._last_case1_sync_check = 0.0
    service._case1_sync._silworx_api_suspended = True

    with (
        patch("prooftest.step01_setup.is_silworx_installed", return_value=True),
        patch("prooftest.annex_api_connexion.is_silworx_running", return_value=False),
        patch("prooftest.step07_triggers.is_silworx_open", return_value=False),
    ):
        run_background_sync_iteration(service, time.time())

    active = [d["device_tag"] for d in db.list_active_devices()]
    if TEST_DEVICE not in active:
        print("FAIL background sync did not OPC-scan device list while API down")
        return 1
    state = db.get_service_state()
    if state.get("device_list_source") != "opc_fallback":
        print(f"FAIL background source={state.get('device_list_source')!r}")
        return 1
    print("OK  Background OPC device poll while API unavailable")
    return 0


def main() -> int:
    TEST_DATA.mkdir(parents=True, exist_ok=True)
    gate_db = TEST_DATA / "gate12_case2.db"
    if gate_db.is_file():
        gate_db.unlink()

    tests = (
        test_unified_case_always_one,
        test_sync_schema_from_structures,
        test_opc_device_list,
        test_service_refresh_opc_fallback,
        test_parallel_api_opc_merge,
        test_background_opc_poll_when_api_down,
    )
    failed = 0
    for test in tests:
        try:
            failed += test()
        except Exception as exc:
            print(f"FAIL {test.__name__}: {exc}")
            failed += 1
    if failed:
        print(f"\nGate 12: {failed} check(s) failed")
        return 1
    print("\nGate 12: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
