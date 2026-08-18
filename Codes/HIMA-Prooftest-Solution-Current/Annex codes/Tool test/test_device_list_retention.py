#!/usr/bin/env python3
"""Device list retention: add new, delete if no reports, keep if reports exist."""

from __future__ import annotations

from pathlib import Path

from _paths import CONFIG_INI, TEST_DATA, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.annex_database import Database

KEEP_TAG = "KEEP-WITH-REPORT"
DROP_TAG = "DROP-NO-REPORT"
NEW_TAG = "NEW-DETECTED"
TYPE_NAME = "X-HART_WIKA_T32_Results"
TABLE = "ProofTest_WIKA_T32_Results"


def _open_db() -> Database:
    config = AppConfig.load(CONFIG_INI)
    config.sqlite_path = TEST_DATA / "device_list_retention.db"
    config.fallback_sqlite = True
    if config.sqlite_path.exists():
        config.sqlite_path.unlink()
    alarms = AlarmManager()
    db = Database(config, alarms)
    db._try_sql_server = lambda: False  # type: ignore[method-assign]
    db.connect()
    with db.cursor() as cur:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS [{TABLE}] (ID INTEGER PRIMARY KEY, Device_TAG TEXT, ReportPath TEXT)"
        )
    return db


def main() -> int:
    db = _open_db()
    reports = TEST_DATA / "retention_reports"
    reports.mkdir(parents=True, exist_ok=True)

    db.upsert_device(KEEP_TAG, TYPE_NAME)
    db.upsert_device(DROP_TAG, TYPE_NAME)
    with db.cursor() as cur:
        cur.execute(f"INSERT INTO [{TABLE}] (Device_TAG) VALUES (?)", (KEEP_TAG,))

    db.upsert_device(NEW_TAG, TYPE_NAME)
    db.reconcile_device_list([NEW_TAG, KEEP_TAG], report_output=reports)

    tags = {d["device_tag"] for d in db.list_active_devices()}
    if NEW_TAG not in tags:
        print("FAIL new detected device not in list")
        return 1
    if DROP_TAG in tags:
        print("FAIL device without reports was not deleted")
        return 1
    if KEEP_TAG not in tags:
        print("FAIL device with a SQL snapshot was removed from the list")
        return 1

    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM DeviceProoftestResultList WHERE Device_TAG=?", (DROP_TAG,))
        if int(cur.fetchone()[0]) != 0:
            print("FAIL dropped device row still exists")
            return 1

    db.set_present_on_opc({NEW_TAG})
    opc_only = {d["device_tag"] for d in db.list_devices("opc")}
    if opc_only != {NEW_TAG}:
        print(f"FAIL OPC view expected only {NEW_TAG}, got {opc_only}")
        return 1
    all_view = {d["device_tag"] for d in db.list_devices("all")}
    if all_view != {NEW_TAG, KEEP_TAG}:
        print(f"FAIL all view expected both kept and new, got {all_view}")
        return 1
    if db.count_listed_devices() != 2 or db.count_opc_devices() != 1:
        print("FAIL ALL ACTIVE / OPC counts")
        return 1

    print("OK  add new / delete no-report / keep with report / OPC view")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
