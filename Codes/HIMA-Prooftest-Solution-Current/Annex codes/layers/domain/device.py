"""Catalog identity: DeviceId is Project + Configuration + Resource + Device_TAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

_SEP = "\x1f"


@dataclass(frozen=True)
class DeviceId:
    project: str = ""
    configuration: str = ""
    resource: str = ""
    device_tag: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "project", (self.project or "").strip())
        object.__setattr__(self, "configuration", (self.configuration or "").strip())
        object.__setattr__(self, "resource", (self.resource or "").strip())
        object.__setattr__(self, "device_tag", (self.device_tag or "").strip())

    def key(self) -> str:
        return _SEP.join(
            [self.project, self.configuration, self.resource, self.device_tag]
        )

    @classmethod
    def from_key(cls, key: str) -> "DeviceId":
        parts = (key or "").split(_SEP)
        while len(parts) < 4:
            parts.append("")
        return cls(parts[0], parts[1], parts[2], parts[3])


@dataclass
class Device:
    device_id: DeviceId
    results_type: str = ""
    opc_server: str = ""
    opc_item_prefix: str = ""
    present_on_opc: bool = False
    test_in_progress: bool = False
    last_running: Optional[bool] = None
    is_active: bool = True
    source_kind: str = "unknown"

    @property
    def device_tag(self) -> str:
        return self.device_id.device_tag

    @property
    def project(self) -> str:
        return self.device_id.project

    @property
    def configuration(self) -> str:
        return self.device_id.configuration

    @property
    def resource(self) -> str:
        return self.device_id.resource

    def source_label(self) -> str:
        if self.present_on_opc and self.opc_server:
            return f"OPC: {self.opc_server}"
        if self.project:
            return f"Project: {self.project}"
        return "Source: unknown"


def device_from_row(row: dict) -> Device:
    """Build a Device from a Device Prooftest Result List row (SQL or API)."""
    tag = str(row.get("device_tag") or "")
    project = str(row.get("project") or row.get("silworx_project") or "")
    configuration = str(row.get("configuration") or "")
    resource = str(row.get("resource") or "")
    raw_id = str(row.get("device_id") or "")
    if raw_id:
        did = DeviceId.from_key(raw_id)
        if not did.device_tag:
            did = DeviceId(project, configuration, resource, tag)
    else:
        did = DeviceId(project, configuration, resource, tag)
    last_running = row.get("last_running")
    # Some call sites (especially gate/unit tests) may omit `present_on_opc`.
    # Treat "has OPC bindings" as present-on-OPC so the Running edge detector can run.
    opc_present = bool(str(row.get("opc_server") or "").strip()) and bool(
        str(row.get("opc_item_prefix") or "").strip()
    )
    present_val = row.get("present_on_opc")
    present_on_opc = bool(present_val) or opc_present
    return Device(
        did,
        results_type=str(row.get("results_type") or ""),
        opc_server=str(row.get("opc_server") or ""),
        opc_item_prefix=str(row.get("opc_item_prefix") or ""),
        present_on_opc=present_on_opc,
        test_in_progress=bool(row.get("test_in_progress")),
        last_running=bool(last_running) if last_running is not None else None,
        is_active=bool(row.get("is_active", True)),
        source_kind=str(row.get("source_kind") or "unknown"),
    )


def sort_devices(devices: list[Device]) -> list[Device]:
    """Device_TAG, then Project, then OPC server."""
    return sorted(
        devices,
        key=lambda d: (
            d.device_tag.lower(),
            d.project.lower(),
            (d.opc_server or "").lower(),
        ),
    )


def sort_device_dicts(rows: list[dict], *, tag_key: str = "device_tag") -> list[dict]:
    return sorted(
        rows,
        key=lambda r: (
            str(r.get(tag_key) or "").lower(),
            str(r.get("project") or r.get("silworx_project") or "").lower(),
            str(r.get("opc_server") or "").lower(),
        ),
    )
