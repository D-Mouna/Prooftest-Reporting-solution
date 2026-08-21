"""Application ports. Adapters live outside Domain."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from layers.domain.device import Device
from layers.domain.merger import OpcObservation, SilworxIdentity


@runtime_checkable
class AlarmPort(Protocol):
    def raise_alarm(
        self,
        step: str,
        action: str,
        message: str,
        *,
        device_tag: Optional[str] = None,
        severity: str = "Error",
    ) -> None: ...

    def last_error(self) -> Optional[dict]: ...


@runtime_checkable
class SilworxPort(Protocol):
    def is_attached(self) -> bool: ...

    def attach(self) -> bool: ...

    def detach(self) -> None: ...

    def list_identities(self, known_types: set[str]) -> list[SilworxIdentity]: ...

    def has_open_project(self) -> bool: ...


@runtime_checkable
class OpcPort(Protocol):
    def discover_servers(self) -> list[str]: ...

    def list_tags(self, server: str) -> list[str]: ...

    def find_running_path(self, server: str, device_tag: str) -> Optional[str]: ...

    def read_running(
        self, server: str, item_id: str
    ) -> tuple[Optional[bool], str]: ...

    def discover_opc_only(
        self,
        known_types: set[str],
        *,
        last_types_by_tag: Optional[dict[str, str]] = None,
    ) -> list[OpcObservation]: ...


@runtime_checkable
class StorePort(Protocol):
    def ensure_folders(self) -> None: ...

    def connect(self) -> str: ...

    def upsert_device(self, device: Device) -> None: ...

    def list_devices(self, view: str = "all") -> list[dict]: ...

    def reconcile(self, active_ids: list[str]) -> None: ...

    def mark_inactive(self, device_id: str) -> None: ...

    def insert_snapshot(self, device_tag: str, results_type: str, snapshot: dict) -> int: ...

    def update_report_path(self, table: str, record_id: int, report_path: str) -> None: ...

    def snapshots_for(self, device_tag: str) -> list[dict]: ...

    def start_test(self, device_tag: str, results_type: str) -> None: ...

    def finish_test(self, device_tag: str, outcome: str) -> None: ...


@runtime_checkable
class ReportPort(Protocol):
    def write(
        self,
        device_tag: str,
        results_type: str,
        snapshot: dict,
        *,
        quality_notes: Optional[list[str]] = None,
        project: str = "",
        snapshot_table: Optional[str] = None,
        record_id: Optional[int] = None,
    ) -> Optional[str]: ...

    def list_for_device(
        self,
        device_tag: str,
        results_type: Optional[str] = None,
        *,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list[dict]: ...

    def resolve_open_path(self, path: str) -> Optional[str]: ...


@runtime_checkable
class ArchivePort(Protocol):
    """List archive / keep-OPC use cases — Application must not import annex_list_archive."""

    def list_archives(self) -> list[dict]: ...

    def create_archive(self) -> dict: ...

    def restore_archive(self, archive_id: str) -> dict: ...

    def restore_archive_upload(self, path: object, filename: str) -> dict: ...

    def clear_keep_opc_only(self, *, archive_first: bool = True) -> dict: ...

    def keep_opc_only_enabled(self) -> bool: ...
