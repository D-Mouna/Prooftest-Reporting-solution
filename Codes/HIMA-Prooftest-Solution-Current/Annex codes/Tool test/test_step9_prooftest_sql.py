#!/usr/bin/env python3
"""
Gate 9 / SPEC Step 5 — Prooftest SQL insert on completion.

Verifies:
  1. insert_snapshot writes a row into the correct ProofTest_* table.
  2. Mandatory metadata columns are populated (Device_TAG, OPC_Server, CollectedAt, SequenceInBatch).
  3. ProoftestMonitor detects Running FALSE→TRUE→FALSE and queues a completion that inserts SQL.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from _paths import CONFIG_INI, TEST_DATA, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.annex_opc import DeviceOpcBinding
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.results_csv import (
    ResultsStructure,
    load_all_structures,
    member_to_column,
    structure_to_sql_table,
)
from prooftest.step04_opc import OpcManager
from prooftest.step05_detection import ProoftestMonitor

META_COLS = ("Device_TAG", "OPC_Server", "CollectedAt", "SequenceInBatch")


def _open_gate_database(config: AppConfig) -> Database:
    """Use an isolated SQLite file so the gate test never touches production SQL data."""
    config.sqlite_path = TEST_DATA / "gate9_prooftest.db"
    config.fallback_sqlite = True
    alarms = AlarmManager()
    db = Database(config, alarms)
    db._try_sql_server = lambda: False  # type: ignore[method-assign]
    db.connect()
    return db
TEST_DEVICE_TAG = "GATE9-TEST-DEVICE"
TEST_RESULTS_TYPE = "X-HART_WIKA_T32_Results"
MOCK_SERVER = "Mock.X_OPC.Server"
MOCK_PREFIX = f"OTS ProofTest.{TEST_DEVICE_TAG}"


class MockOpcManager:
    """Simulates Running edge and member reads without a live X-OPC server."""

    def __init__(self, running_sequence: List[bool], structure: ResultsStructure) -> None:
        self.running_sequence = list(running_sequence)
        self.structure = structure
        self._running_index = 0
        self.running_item_id = f"{MOCK_PREFIX}.Running"
        self.tags = [self.running_item_id]

    def _next_running(self) -> bool:
        if self._running_index < len(self.running_sequence):
            value = self.running_sequence[self._running_index]
            self._running_index += 1
            return value
        return False

    def resolve_device_binding(
        self,
        device_tag: str,
        item_prefix: Optional[str] = None,
    ) -> DeviceOpcBinding:
        return DeviceOpcBinding(
            server=MOCK_SERVER,
            item_prefix=MOCK_PREFIX,
            tags=self.tags,
            running_item_id=self.running_item_id,
        )

    def build_member_item_ids(
        self,
        tags: List[str],
        prefix: str,
        short_names: List[str],
    ) -> Dict[str, str]:
        return {name: f"{prefix}.{name}" for name in short_names}

    def read_values(self, server: str, item_ids: List[str]) -> Dict[str, tuple[Any, str]]:
        values: Dict[str, tuple[Any, str]] = {}
        for item_id in item_ids:
            if item_id.endswith(".Running"):
                values[item_id] = (self._next_running(), "Good")
                continue
            member = item_id.rsplit(".", 1)[-1]
            if member.lower() == "error":
                values[item_id] = (False, "Good")
            elif "real" in member.lower() or "value" in member.lower():
                values[item_id] = (1.23, "Good")
            else:
                values[item_id] = (0, "Good")
        return values


def _pick_structure(structures: Dict[str, ResultsStructure]) -> ResultsStructure:
    if TEST_RESULTS_TYPE in structures:
        return structures[TEST_RESULTS_TYPE]
    if structures:
        return next(iter(structures.values()))
    raise RuntimeError("No Results structures loaded — check results_structures path in solution.ini")


def _build_snapshot(structure: ResultsStructure) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {}
    for member in structure.member_short_names():
        if member.lower() == "running":
            continue
        col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
        if member.lower() == "error":
            snapshot[col] = False
        elif "real" in member.lower() or "value" in member.lower():
            snapshot[col] = 12.34
        else:
            snapshot[col] = 0
    return snapshot


def _fetch_latest_row(db: Database, table: str, device_tag: str) -> Optional[Dict[str, Any]]:
    target = f"[{table}]" if db.using_sqlite else f"[dbo].[{table}]"
    with db.cursor() as cur:
        cur.execute(
            f"SELECT * FROM {target} WHERE [Device_TAG]=? ORDER BY [ID] DESC",
            (device_tag,),
        )
        row = cur.fetchone()
        if not row:
            return None
        if db.using_sqlite:
            columns = [d[0] for d in cur.description]
            return {columns[i]: row[i] for i in range(len(columns))}
        return {desc[0]: row[i] for i, desc in enumerate(cur.description)}


def _delete_test_rows(db: Database, table: str, device_tag: str) -> None:
    target = f"[{table}]" if db.using_sqlite else f"[dbo].[{table}]"
    with db.cursor() as cur:
        cur.execute(f"DELETE FROM {target} WHERE [Device_TAG]=?", (device_tag,))


def test_insert_snapshot(db: Database, structure: ResultsStructure) -> int:
    table = structure_to_sql_table(structure.type_name)
    snapshot = _build_snapshot(structure)
    record_id = db.insert_snapshot(
        table,
        TEST_DEVICE_TAG,
        snapshot,
        opc_server=MOCK_SERVER,
        sequence=1,
    )
    row = _fetch_latest_row(db, table, TEST_DEVICE_TAG)
    if not row:
        print(f"FAIL no row found after insert_snapshot (returned id={record_id})")
        return 1
    if record_id <= 0 and not row.get("ID"):
        print(f"FAIL insert_snapshot returned id={record_id} and row has no ID")
        return 1

    missing = [col for col in META_COLS if col not in row or row[col] in (None, "")]
    if missing:
        print(f"FAIL missing metadata columns: {missing}")
        return 1

    if row["Device_TAG"] != TEST_DEVICE_TAG:
        print(f"FAIL Device_TAG mismatch: {row['Device_TAG']!r}")
        return 1
    if row["OPC_Server"] != MOCK_SERVER:
        print(f"FAIL OPC_Server mismatch: {row['OPC_Server']!r}")
        return 1
    if int(row["SequenceInBatch"]) != 1:
        print(f"FAIL SequenceInBatch mismatch: {row['SequenceInBatch']!r}")
        return 1

    print(f"OK  insert_snapshot -> {table} id={record_id}")
    print(f"    CollectedAt={row['CollectedAt']}")
    _delete_test_rows(db, table, TEST_DEVICE_TAG)
    return 0


def test_running_edge_pipeline(
    config: AppConfig,
    db: Database,
    structures: Dict[str, ResultsStructure],
) -> int:
    structure = _pick_structure(structures)
    table = structure_to_sql_table(structure.type_name)
    _delete_test_rows(db, table, TEST_DEVICE_TAG)

    db.upsert_device(
        TEST_DEVICE_TAG,
        structure.type_name,
        opc_server=MOCK_SERVER,
        opc_prefix=MOCK_PREFIX,
        last_running=False,
        test_in_progress=False,
    )

    mock_opc = MockOpcManager([False, True, False, False], structure)
    monitor = ProoftestMonitor(config, db, mock_opc, structures)  # type: ignore[arg-type]

    device = {
        "device_tag": TEST_DEVICE_TAG,
        "results_type": structure.type_name,
        "configuration": None,
        "resource": None,
        "opc_server": MOCK_SERVER,
        "opc_item_prefix": MOCK_PREFIX,
        "last_running": False,
        "test_in_progress": False,
    }
    monitor._poll_one(device)  # idle
    device.update(next(d for d in db.list_active_devices() if d["device_tag"] == TEST_DEVICE_TAG))
    monitor._poll_one(device)  # started
    device.update(next(d for d in db.list_active_devices() if d["device_tag"] == TEST_DEVICE_TAG))
    monitor._poll_one(device)  # completed -> queued

    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if monitor.queue_depth == 0:
            row = _fetch_latest_row(db, table, TEST_DEVICE_TAG)
            if row:
                break
        time.sleep(0.2)
    else:
        monitor.shutdown()
        print("FAIL completion worker did not insert SQL row within 10s")
        return 1

    missing = [col for col in META_COLS if col not in row or row[col] in (None, "")]
    monitor.shutdown()
    if missing:
        print(f"FAIL edge pipeline missing metadata: {missing}")
        _delete_test_rows(db, table, TEST_DEVICE_TAG)
        return 1

    device = db.list_active_devices()
    gate_device = next((d for d in device if d["device_tag"] == TEST_DEVICE_TAG), None)
    if gate_device and gate_device.get("test_in_progress"):
        print("FAIL TestInProgress still set after completion")
        _delete_test_rows(db, table, TEST_DEVICE_TAG)
        return 1

    print(f"OK  Running edge -> SQL row in {table} id={row.get('ID')}")
    print(f"    SequenceInBatch={row.get('SequenceInBatch')} CollectedAt={row.get('CollectedAt')}")
    _delete_test_rows(db, table, TEST_DEVICE_TAG)
    db.deactivate_missing_devices([t for t in [d["device_tag"] for d in db.list_active_devices()] if t != TEST_DEVICE_TAG])
    with db.cursor() as cur:
        cur.execute("DELETE FROM DeviceProoftestResultList WHERE Device_TAG=?", (TEST_DEVICE_TAG,))
    return 0


def test_live_opc_optional(db: Database, structures: Dict[str, ResultsStructure]) -> int:
    """Informational only — does not fail the gate when OPC is unavailable."""
    config = AppConfig.load(CONFIG_INI)
    opc = OpcManager(
        config.opc_server_filter,
        config.opc_default_branch,
        config.opc_prooftest_branches,
    )
    try:
        servers = opc.discover_servers()
    except Exception as exc:
        print(f"SKIP live OPC: {exc}")
        return 0

    if not servers:
        print("SKIP live OPC: no X-OPC servers on host")
        return 0

    devices = db.list_active_devices()
    if not devices:
        print("SKIP live OPC: no active devices in DeviceProoftestResultList")
        return 0

    print(f"NOTE live OPC: {len(servers)} server(s), {len(devices)} active device(s)")
    print("      Run a prooftest on a configured device to verify end-to-end on station.")
    return 0


def main() -> int:
    config = AppConfig.load(CONFIG_INI)
    db = _open_gate_database(config)
    print(f"Database: sqlite ({config.sqlite_path})")

    structures = load_all_structures(config.results_structures)
    if not structures:
        print("FAIL no Results structures loaded")
        return 1

    structure = _pick_structure(structures)
    db.sync_schema_case1(structures, [structure.type_name])

    rc = test_insert_snapshot(db, structure)
    if rc:
        db.close()
        return rc

    rc = test_running_edge_pipeline(config, db, structures)
    if rc:
        db.close()
        return rc

    test_live_opc_optional(db, structures)
    db.close()
    print("Gate 9 / Step 5 SQL insert check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
