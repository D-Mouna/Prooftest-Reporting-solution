"""Fake ports for unit tests — no OPC COM, no SILworX HTTP, no pyodbc."""

from __future__ import annotations

from typing import Optional

from layers.domain.device import Device, DeviceId, sort_device_dicts
from layers.domain.merger import OpcObservation, SilworxIdentity
from layers.ports import AlarmPort, OpcPort, ReportPort, SilworxPort, StorePort


class FakeSilworx:
    def __init__(
        self,
        identities: Optional[list[SilworxIdentity]] = None,
        *,
        attached: bool = False,
        open_project: bool = False,
        attach_error: Optional[Exception] = None,
        list_error: Optional[Exception] = None,
    ) -> None:
        self.identities = identities or []
        self.attached = attached
        self.open_project = open_project
        self.attach_error = attach_error
        self.list_error = list_error
        self.list_calls = 0
        self.detach_calls = 0

    def is_attached(self) -> bool:
        return self.attached

    def has_open_project(self) -> bool:
        return self.open_project

    def attach(self) -> bool:
        if self.attach_error:
            raise self.attach_error
        if not self.open_project:
            self.attached = False
            return False
        self.attached = True
        return True

    def detach(self) -> None:
        self.detach_calls += 1
        self.attached = False

    def list_identities(self, known_types: set[str]) -> list[SilworxIdentity]:
        self.list_calls += 1
        if self.list_error:
            raise self.list_error
        # Mirror production: discovery only contributes while this tool is attached
        # (or immediately during attach). After Disconnect, stay silent.
        if not self.attached:
            return []
        return [i for i in self.identities if i.results_type in known_types or not known_types]


class FakeOpc:
    def __init__(
        self,
        servers: Optional[list[str]] = None,
        paths: Optional[dict[tuple[str, str], str]] = None,
        opc_only: Optional[list[OpcObservation]] = None,
        running: Optional[dict[str, tuple[Optional[bool], str]]] = None,
        running_sequence: Optional[dict[str, list[tuple[Optional[bool], str]]]] = None,
        fail_tags: Optional[set[str]] = None,
    ) -> None:
        self.servers = servers or []
        self.paths = paths or {}
        self.opc_only = opc_only or []
        self.running = running or {}
        self.running_sequence = running_sequence or {}
        self.fail_tags = fail_tags or set()
        self.find_calls: list[tuple[str, str]] = []
        self.read_calls: list[str] = []

    def discover_servers(self) -> list[str]:
        return list(self.servers)

    def list_tags(self, server: str) -> list[str]:
        return []

    def find_running_path(self, server: str, device_tag: str) -> Optional[str]:
        for branch in ("OTS ProofTest", "OPC ProofTest"):
            item = f"{branch}.{device_tag}.Running"
            self.find_calls.append((server, item))
            if (server, item) in self.paths:
                return self.paths[(server, item)]
            if (server, device_tag) in self.paths:
                found = self.paths[(server, device_tag)]
                if found.startswith(branch) or branch in found:
                    return found
        return None

    def read_running(self, server: str, item_id: str) -> tuple[Optional[bool], str]:
        self.read_calls.append(item_id)
        tag = item_id.rsplit(".", 2)[-2] if "." in item_id else item_id
        if tag in self.fail_tags or item_id in self.fail_tags:
            raise RuntimeError(f"COM error {item_id}")
        seq = self.running_sequence.get(item_id) or self.running_sequence.get(tag)
        if seq:
            return seq.pop(0)
        if item_id in self.running:
            return self.running[item_id]
        return self.running.get(tag, (False, "Good"))

    def discover_opc_only(
        self,
        known_types: set[str],
        *,
        last_types_by_tag: Optional[dict[str, str]] = None,
    ) -> list[OpcObservation]:
        del known_types, last_types_by_tag
        return list(self.opc_only)


class FakeStore:
    def __init__(self, *, connect_fail_then_ok: bool = False, connect_always_fail: bool = False) -> None:
        self.devices: dict[str, Device] = {}
        self.snapshots: list[dict] = []
        self.inactive: list[str] = []
        self.connect_calls = 0
        self.connect_fail_then_ok = connect_fail_then_ok
        self.connect_always_fail = connect_always_fail
        self.folder_ok = True
        self.insert_fail_once = False

    def ensure_folders(self) -> None:
        if not self.folder_ok:
            raise OSError("cannot create folders")

    def connect(self) -> str:
        self.connect_calls += 1
        if self.connect_always_fail:
            raise RuntimeError("store down")
        if self.connect_fail_then_ok and self.connect_calls == 1:
            # Caller simulates SQL then sqlite: second connect succeeds.
            raise RuntimeError("sqlserver down")
        return "sqlite"

    def upsert_device(self, device: Device) -> None:
        self.devices[device.device_id.key()] = device

    def list_devices(self, view: str = "all") -> list[dict]:
        rows = []
        for device in self.devices.values():
            if view == "opc" and not device.present_on_opc:
                continue
            rows.append(
                {
                    "device_id": device.device_id.key(),
                    "device_tag": device.device_tag,
                    "results_type": device.results_type,
                    "project": device.project,
                    "silworx_project": device.project,
                    "configuration": device.configuration,
                    "resource": device.resource,
                    "opc_server": device.opc_server,
                    "opc_item_prefix": device.opc_item_prefix,
                    "present_on_opc": device.present_on_opc,
                    "test_in_progress": device.test_in_progress,
                }
            )
        return sort_device_dicts(rows)

    def reconcile(self, active_ids: list[str]) -> None:
        active = set(active_ids)
        for key, device in list(self.devices.items()):
            if key not in active:
                device.is_active = False
                self.inactive.append(key)

    def mark_inactive(self, device_id: str) -> None:
        self.inactive.append(device_id)
        if device_id in self.devices:
            self.devices[device_id].is_active = False

    def insert_snapshot(self, device_tag: str, results_type: str, snapshot: dict, **kwargs) -> int:
        if self.insert_fail_once:
            self.insert_fail_once = False
            raise RuntimeError("insert failed")
        self.snapshots.append(
            {
                "device_tag": device_tag,
                "results_type": results_type,
                "snapshot": snapshot,
                "device_id": kwargs.get("device_id"),
            }
        )
        return len(self.snapshots)

    def snapshots_for(self, device_tag: str) -> list[dict]:
        return [s for s in self.snapshots if s["device_tag"] == device_tag]

    def start_test(self, device_tag: str, results_type: str) -> None:
        return None

    def finish_test(self, device_tag: str, outcome: str, result: str = "") -> None:
        return None


class FakeReports:
    def __init__(self, *, fail: bool = False, root: Optional[str] = None) -> None:
        self.fail = fail
        self.written: list[str] = []
        self.written_meta: list[dict] = []
        self.root = root or "/reports"

    def write(
        self,
        device_tag: str,
        results_type: str,
        snapshot: dict,
        *,
        quality_notes: Optional[list[str]] = None,
        project: str = "",
    ) -> Optional[str]:
        if self.fail:
            raise RuntimeError("template missing")
        self.written.append(device_tag)
        self.written_meta.append({"tag": device_tag, "project": project or ""})
        folder = f"{self.root}/{project}/{device_tag}" if project else f"{self.root}/{device_tag}"
        return f"{folder}.html"

    def list_for_device(
        self,
        device_tag: str,
        results_type: Optional[str] = None,
        *,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list[dict]:
        _ = results_type, device_id
        hits = []
        for meta in self.written_meta:
            if meta["tag"] != device_tag:
                continue
            if project is not None and meta["project"] != (project or ""):
                continue
            folder = (
                f"{self.root}/{meta['project']}/{device_tag}"
                if meta["project"]
                else f"{self.root}/{device_tag}"
            )
            hits.append({"path": f"{folder}.html", "project": meta["project"]})
        return hits

    def resolve_open_path(self, path: str) -> Optional[str]:
        return path


class FakeArchive:
    def __init__(self) -> None:
        self.archives: list[dict] = []
        self.created = 0
        self.keep_opc = False
        self.clear_calls = 0

    def list_archives(self) -> list[dict]:
        return list(self.archives)

    def create_archive(self) -> dict:
        self.created += 1
        item = {"archive_id": f"list-archive-20260101-{self.created:06d}", "device_count": 0}
        self.archives.insert(0, item)
        return item

    def restore_archive(self, archive_id: str) -> dict:
        self.keep_opc = False
        return {"archive_id": archive_id, "restored": True}

    def restore_archive_upload(self, path: object, filename: str) -> dict:
        return {"filename": filename, "restored": True}

    def clear_keep_opc_only(self, *, archive_first: bool = True) -> dict:
        self.clear_calls += 1
        if archive_first:
            self.create_archive()
        self.keep_opc = True
        return {"keep_opc_only": True, "archive_first": archive_first}

    def keep_opc_only_enabled(self) -> bool:
        return self.keep_opc
