"""Archive and restore the Device Prooftest Result List and report list (CSV)."""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from prooftest.config import AppConfig

ARCHIVE_FOLDER_NAME = "List Archives"
KEEP_OPC_STATE_KEY = "device_list_keep_opc_only"
ARCHIVE_ID_RE = re.compile(r"^list-archive-\d{8}-\d{6}$")

DEVICE_CSV_FIELDS = [
    "Device_TAG",
    "Results_Type",
    "Configuration",
    "Resource",
    "OPC_Server",
    "OPC_ItemPrefix",
    "IsActive",
    "LastSeenAt",
    "LastRunning",
    "TestInProgress",
    "PresentOnOpc",
    "SilworxProject",
    "DeviceId",
]

REPORT_CSV_FIELDS = [
    "Device_TAG",
    "Results_Type",
    "FileName",
    "RelativePath",
    "SourcePath",
    "ModifiedAt",
]


class ListArchiveError(ValueError):
    """Operator-facing archive/restore/clear error."""


def archive_root(config: AppConfig) -> Path:
    return Path(config.first_run_folder) / ARCHIVE_FOLDER_NAME


def keep_opc_only_enabled(db: Any) -> bool:
    try:
        return str(db.get_service_state().get(KEEP_OPC_STATE_KEY) or "") == "1"
    except Exception:
        return False


def set_keep_opc_only(db: Any, enabled: bool) -> None:
    db.set_service_state(KEEP_OPC_STATE_KEY, "1" if enabled else "0")


def _csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _collect_reports(config: AppConfig, devices: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    from prooftest.annex_pdf_generation import list_reports_for_device

    output = Path(config.report_output)
    rows: List[Dict[str, str]] = []
    seen: set[str] = set()
    for device in devices:
        tag = str(device.get("device_tag") or "")
        results_type = str(device.get("results_type") or "") or None
        if not tag:
            continue
        reports = list_reports_for_device(output, tag, results_type=results_type)
        if not reports and results_type:
            reports = list_reports_for_device(output, tag)
        for report in reports:
            path = Path(report["path"])
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            try:
                relative = str(path.resolve().relative_to(output.resolve()))
            except Exception:
                relative = path.name
            rows.append(
                {
                    "Device_TAG": tag,
                    "Results_Type": results_type or "",
                    "FileName": report.get("name") or path.name,
                    "RelativePath": relative.replace("\\", "/"),
                    "SourcePath": str(path),
                    "ModifiedAt": report.get("modified") or "",
                }
            )
    rows.sort(key=lambda row: (row["Device_TAG"], row["FileName"]))
    return rows


def create_list_archive(db: Any, config: AppConfig) -> Dict[str, Any]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_id = f"list-archive-{stamp}"
    folder = archive_root(config) / archive_id
    folder.mkdir(parents=True, exist_ok=True)
    reports_dir = folder / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    devices = db.export_device_rows()
    report_rows = _collect_reports(config, devices)

    devices_csv = folder / "devices.csv"
    with devices_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DEVICE_CSV_FIELDS)
        writer.writeheader()
        for device in devices:
            writer.writerow(
                {
                    "Device_TAG": _csv_cell(device.get("device_tag")),
                    "Results_Type": _csv_cell(device.get("results_type")),
                    "Configuration": _csv_cell(device.get("configuration")),
                    "Resource": _csv_cell(device.get("resource")),
                    "OPC_Server": _csv_cell(device.get("opc_server")),
                    "OPC_ItemPrefix": _csv_cell(device.get("opc_item_prefix")),
                    "IsActive": _csv_cell(device.get("is_active", 1)),
                    "LastSeenAt": _csv_cell(device.get("last_seen_at")),
                    "LastRunning": _csv_cell(device.get("last_running")),
                    "TestInProgress": _csv_cell(device.get("test_in_progress")),
                    "PresentOnOpc": _csv_cell(device.get("present_on_opc")),
                    "SilworxProject": _csv_cell(device.get("silworx_project")),
                    "DeviceId": _csv_cell(device.get("device_id")),
                }
            )

    reports_csv = folder / "reports.csv"
    copied = 0
    with reports_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_CSV_FIELDS)
        writer.writeheader()
        for row in report_rows:
            writer.writerow(row)
            source = Path(row["SourcePath"])
            if not source.is_file():
                continue
            dest = reports_dir / Path(row["RelativePath"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            copied += 1

    manifest = {
        "archive_id": archive_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "device_count": len(devices),
        "report_count": len(report_rows),
        "report_files_copied": copied,
        "path": str(folder),
    }
    (folder / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def zip_archive_folder(folder: Path) -> bytes:
    """Pack an on-disk list archive folder into a restore-compatible zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, path.relative_to(folder).as_posix())
    return buf.getvalue()


def export_list_archive(db: Any, config: AppConfig) -> tuple[Dict[str, Any], bytes]:
    """Create a list archive and return manifest plus zip bytes for export."""
    manifest = create_list_archive(db, config)
    folder = Path(manifest["path"])
    zip_bytes = zip_archive_folder(folder)
    manifest["export_name"] = f"{manifest['archive_id']}.zip"
    return manifest, zip_bytes


def list_list_archives(config: AppConfig) -> List[Dict[str, Any]]:
    root = archive_root(config)
    if not root.is_dir():
        return []
    archives: List[Dict[str, Any]] = []
    for folder in sorted(root.iterdir(), reverse=True):
        if not folder.is_dir() or not ARCHIVE_ID_RE.match(folder.name):
            continue
        manifest_path = folder / "manifest.json"
        item: Dict[str, Any] = {
            "archive_id": folder.name,
            "path": str(folder),
            "created_at": "",
            "device_count": 0,
            "report_count": 0,
        }
        if manifest_path.is_file():
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    item.update(
                        {
                            "created_at": payload.get("created_at") or "",
                            "device_count": int(payload.get("device_count") or 0),
                            "report_count": int(payload.get("report_count") or 0),
                            "path": payload.get("path") or str(folder),
                        }
                    )
            except Exception:
                pass
        if not item["created_at"]:
            item["created_at"] = datetime.fromtimestamp(folder.stat().st_mtime).isoformat(
                timespec="seconds"
            )
        archives.append(item)
    return archives


def _archive_folder(config: AppConfig, archive_id: str) -> Path:
    if not ARCHIVE_ID_RE.match(archive_id or ""):
        raise ListArchiveError("Invalid archive id")
    folder = archive_root(config) / archive_id
    if not folder.is_dir():
        raise ListArchiveError(f"Archive not found: {archive_id}")
    return folder


def _safe_extract_zip(archive: zipfile.ZipFile, dest: Path) -> None:
    dest = dest.resolve()
    for info in archive.infolist():
        target = (dest / info.filename).resolve()
        if dest not in target.parents and target != dest:
            raise ListArchiveError("Zip archive contains an unsafe path")
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as src, target.open("wb") as out:
            shutil.copyfileobj(src, out)


def restore_from_folder(
    db: Any,
    config: AppConfig,
    folder: Path,
    *,
    archive_id: str = "",
) -> Dict[str, Any]:
    devices_csv = folder / "devices.csv"
    if not devices_csv.is_file():
        found = [path for path in folder.rglob("devices.csv") if path.is_file()]
        if not found:
            raise ListArchiveError("Archive is missing devices.csv")
        devices_csv = found[0]
        folder = devices_csv.parent

    restored_devices = 0
    with devices_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            tag = (row.get("Device_TAG") or "").strip()
            results_type = (row.get("Results_Type") or "").strip()
            if not tag or not results_type:
                continue
            db.upsert_device(
                tag,
                results_type,
                opc_server=(row.get("OPC_Server") or "").strip() or None,
                opc_prefix=(row.get("OPC_ItemPrefix") or "").strip() or None,
                configuration=(row.get("Configuration") or "").strip() or None,
                resource=(row.get("Resource") or "").strip() or None,
                silworx_project=(row.get("SilworxProject") or "").strip() or None,
                device_id=(row.get("DeviceId") or "").strip() or None,
            )
            present = (row.get("PresentOnOpc") or "").strip() in ("1", "true", "True")
            db.set_device_present_on_opc(tag, present)
            restored_devices += 1

    if restored_devices < 1:
        raise ListArchiveError("No device rows found in the restore file")

    restored_reports = 0
    reports_dir = folder / "reports"
    reports_csv = folder / "reports.csv"
    output = Path(config.report_output)
    if reports_csv.is_file():
        with reports_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                relative = (row.get("RelativePath") or "").replace("\\", "/").lstrip("/")
                if not relative or ".." in Path(relative).parts:
                    continue
                source = reports_dir / relative
                if not source.is_file():
                    continue
                dest = output / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    continue
                shutil.copy2(source, dest)
                restored_reports += 1

    set_keep_opc_only(db, False)
    return {
        "archive_id": archive_id or folder.name,
        "restored_devices": restored_devices,
        "restored_reports": restored_reports,
        "path": str(folder),
    }


def restore_list_archive(db: Any, config: AppConfig, archive_id: str) -> Dict[str, Any]:
    folder = _archive_folder(config, archive_id)
    return restore_from_folder(db, config, folder, archive_id=archive_id)


def restore_from_uploaded_file(
    db: Any,
    config: AppConfig,
    uploaded_path: Path,
    original_name: str = "",
) -> Dict[str, Any]:
    """Restore devices (and reports if present) from an uploaded csv or zip."""
    name = (original_name or uploaded_path.name).lower()
    work = Path(tempfile.mkdtemp(prefix="list_restore_"))
    try:
        if name.endswith(".csv"):
            shutil.copy2(uploaded_path, work / "devices.csv")
            return restore_from_folder(
                db, config, work, archive_id=Path(original_name or uploaded_path.name).stem
            )
        if name.endswith(".zip"):
            with zipfile.ZipFile(uploaded_path, "r") as archive:
                _safe_extract_zip(archive, work)
            return restore_from_folder(
                db, config, work, archive_id=Path(original_name or uploaded_path.name).stem
            )
        raise ListArchiveError("Restore file must be devices.csv or a zip archive")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def clear_keep_opc_only(
    db: Any,
    config: AppConfig,
    *,
    archive_first: bool = True,
) -> Dict[str, Any]:
    opc_count = db.count_opc_devices()
    if opc_count < 1:
        raise ListArchiveError(
            "No devices are flagged as present on OPC. Refresh the service first, then try again."
        )
    archive_info: Optional[Dict[str, Any]] = None
    if archive_first:
        archive_info = create_list_archive(db, config)
    removed = db.delete_devices_not_on_opc()
    set_keep_opc_only(db, True)
    return {
        "removed": removed,
        "removed_count": len(removed),
        "opc_devices": db.count_opc_devices(),
        "listed_devices": db.count_listed_devices(),
        "archive": archive_info,
        "keep_opc_only": True,
    }
