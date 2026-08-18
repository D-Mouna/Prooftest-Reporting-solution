#!/usr/bin/env python3
"""Archive / restore device+report lists and keep-OPC-only clear."""

from __future__ import annotations

from pathlib import Path

from _paths import CONFIG_INI, TEST_DATA, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.annex_list_archive import (
    ListArchiveError,
    clear_keep_opc_only,
    create_list_archive,
    keep_opc_only_enabled,
    list_list_archives,
    restore_from_uploaded_file,
    restore_list_archive,
)
from prooftest.annex_pdf_generation import device_report_dir
from prooftest.config import AppConfig
from prooftest.annex_database import Database

KEEP_TAG = "KEEP-WITH-REPORT"
OPC_TAG = "OPC-DEVICE"
TYPE_NAME = "X-HART_WIKA_T32_Results"


def _open_db(station):
    config = AppConfig.load(CONFIG_INI)
    config.sqlite_path = station / "list_archive.db"
    config.fallback_sqlite = True
    config.first_run_folder = station
    config.report_output = station / "reports"
    config.report_mirror = station / "mirror"
    config.report_output.mkdir(parents=True, exist_ok=True)
    config.report_mirror.mkdir(parents=True, exist_ok=True)
    if config.sqlite_path.exists():
        config.sqlite_path.unlink()
    db = Database(config, AlarmManager())
    db._try_sql_server = lambda: False  # type: ignore[method-assign]
    db.connect()
    db.config = config
    return db


def _write_report(config, tag):
    folder = device_report_dir(config.report_output, tag, TYPE_NAME)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{tag}_sample.html"
    path.write_text("<html>archived report</html>", encoding="utf-8")
    return path


def main() -> int:
    station = TEST_DATA / "list_archive_station"
    if station.exists():
        for child in sorted(station.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
    station.mkdir(parents=True, exist_ok=True)
    db = _open_db(station)
    config = db.config

    db.upsert_device(KEEP_TAG, TYPE_NAME)
    db.upsert_device(OPC_TAG, TYPE_NAME)
    db.set_present_on_opc({OPC_TAG})
    report_path = _write_report(config, KEEP_TAG)

    archive = create_list_archive(db, config)
    listed = list_list_archives(config)
    if not listed or listed[0]["archive_id"] != archive["archive_id"]:
        print("FAIL archive not listed")
        return 1
    if archive["device_count"] != 2 or archive["report_count"] < 1:
        print(f"FAIL archive counts {archive}")
        return 1

    result = clear_keep_opc_only(db, config, archive_first=True)
    tags = {d["device_tag"] for d in db.list_active_devices()}
    if KEEP_TAG in tags or OPC_TAG not in tags:
        print(f"FAIL keep OPC only left {tags}")
        return 1
    if KEEP_TAG not in result["removed"] or result["opc_devices"] != 1:
        print(f"FAIL clear result {result}")
        return 1
    if not keep_opc_only_enabled(db):
        print("FAIL keep_opc_only flag not set")
        return 1
    if not report_path.is_file():
        print("FAIL report file was deleted by clear")
        return 1

    report_path.unlink()
    restored = restore_list_archive(db, config, archive["archive_id"])
    tags = {d["device_tag"] for d in db.list_active_devices()}
    if tags != {KEEP_TAG, OPC_TAG}:
        print(f"FAIL restore devices {tags}")
        return 1
    if not report_path.is_file():
        print("FAIL restore did not copy missing report file")
        return 1
    if keep_opc_only_enabled(db):
        print("FAIL restore must clear keep_opc_only flag")
        return 1
    if restored["restored_devices"] != 2:
        print(f"FAIL restored_devices={restored}")
        return 1

    csv_upload = restore_from_uploaded_file(
        db, config, Path(archive["path"]) / "devices.csv", "devices.csv"
    )
    if csv_upload["restored_devices"] != 2:
        print(f"FAIL csv upload restore {csv_upload}")
        return 1

    import zipfile

    zip_path = station / "list-archive-upload.zip"
    archive_dir = Path(archive["path"])
    with zipfile.ZipFile(zip_path, "w") as zf:
        for child in archive_dir.rglob("*"):
            if child.is_file():
                zf.write(child, child.relative_to(archive_dir.parent).as_posix())
    zip_upload = restore_from_uploaded_file(db, config, zip_path, zip_path.name)
    if zip_upload["restored_devices"] != 2:
        print(f"FAIL zip upload restore {zip_upload}")
        return 1

    db.set_present_on_opc(set())
    try:
        clear_keep_opc_only(db, config, archive_first=False)
        print("FAIL clear must refuse when no OPC devices are flagged")
        return 1
    except ListArchiveError:
        pass

    print("OK  archive / keep OPC only / restore / upload-restore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
