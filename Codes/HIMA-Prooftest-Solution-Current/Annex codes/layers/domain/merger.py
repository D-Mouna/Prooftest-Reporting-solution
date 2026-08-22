"""Merge SILworX identities with OPC observations. Device_TAG is not globally unique."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from layers.domain.device import Device, DeviceId


@dataclass(frozen=True)
class SilworxIdentity:
    project: str
    configuration: str
    resource: str
    device_tag: str
    results_type: str


@dataclass(frozen=True)
class OpcObservation:
    device_tag: str
    opc_server: str
    opc_item_prefix: str
    results_type: str = ""
    running_item: str = ""


@dataclass
class MergeCollision:
    device_tag: str
    opc_path: str
    device_ids: list[str]


@dataclass
class MergeResult:
    devices: list[Device]
    collisions: list[MergeCollision] = field(default_factory=list)
    skipped_duplicates: list[str] = field(default_factory=list)


class CatalogMerger:
    """Build catalog rows from SILworX + OPC. Never invent type by CSV score when SILworX typed the DeviceId."""

    @staticmethod
    def _tag_lookup_keys(tag: str) -> list[str]:
        """SILworX TAG may use '/'; HIMA X-OPC often publishes the same leaf with '_'."""
        text = str(tag or "")
        keys = [text]
        underscored = text.replace("/", "_")
        if underscored != text:
            keys.append(underscored)
        return keys

    @staticmethod
    def _tags_equivalent(a: str, b: str) -> bool:
        left, right = str(a or ""), str(b or "")
        return left == right or left.replace("/", "_") == right.replace("/", "_")

    def _opc_matches_for_tag(
        self, tag: str, opc_by_tag: dict[str, list[OpcObservation]]
    ) -> list[OpcObservation]:
        matches: list[OpcObservation] = []
        seen: set[int] = set()
        for key in self._tag_lookup_keys(tag):
            for obs in opc_by_tag.get(key) or []:
                oid = id(obs)
                if oid in seen:
                    continue
                seen.add(oid)
                matches.append(obs)
        return matches

    def merge(
        self,
        silworx: list[SilworxIdentity],
        opc: list[OpcObservation],
        *,
        existing: Optional[dict[str, Device]] = None,
    ) -> MergeResult:
        existing = existing or {}
        devices: dict[str, Device] = {}
        skipped: list[str] = []
        seen_silworx: set[str] = set()

        for ident in silworx:
            did = DeviceId(
                ident.project, ident.configuration, ident.resource, ident.device_tag
            )
            key = did.key()
            if key in seen_silworx:
                skipped.append(key)
                continue
            seen_silworx.add(key)
            devices[key] = Device(
                device_id=did,
                results_type=ident.results_type,
                present_on_opc=False,
                source_kind="project",
            )

        opc_by_tag: dict[str, list[OpcObservation]] = {}
        for obs in opc:
            opc_by_tag.setdefault(obs.device_tag, []).append(obs)

        path_owners: dict[tuple[str, str], list[str]] = {}
        bound_obs: set[int] = set()

        for key, device in list(devices.items()):
            matches = self._opc_matches_for_tag(device.device_tag, opc_by_tag)
            chosen = self._choose_opc_for_device(device, matches)
            if chosen is None:
                continue
            bound_obs.add(id(chosen))
            device.opc_server = chosen.opc_server
            device.opc_item_prefix = chosen.opc_item_prefix
            device.present_on_opc = True
            device.source_kind = "opc"
            path_owners.setdefault(
                (chosen.opc_server, chosen.opc_item_prefix), []
            ).append(key)

        collisions: list[MergeCollision] = []
        for (server, prefix), owners in path_owners.items():
            if len(owners) > 1:
                collisions.append(
                    MergeCollision(
                        device_tag=devices[owners[0]].device_tag,
                        opc_path=f"{server}|{prefix}",
                        device_ids=owners,
                    )
                )
                keep = owners[0]
                for extra in owners[1:]:
                    extra_dev = devices[extra]
                    extra_dev.opc_server = ""
                    extra_dev.opc_item_prefix = ""
                    extra_dev.present_on_opc = False
                    extra_dev.source_kind = "project"

        used_tags_with_silworx = {devices[k].device_tag for k in devices}
        for obs in opc:
            if id(obs) in bound_obs:
                continue
            # OPC-only when this tool is not attached, or TAG not in SILworX.
            if any(
                self._tags_equivalent(obs.device_tag, sil_tag)
                and any(
                    self._tags_equivalent(d.device_tag, obs.device_tag) and d.present_on_opc
                    for d in devices.values()
                )
                for sil_tag in used_tags_with_silworx
            ):
                continue
            did = DeviceId("", "", "", obs.device_tag)
            key = did.key()
            prev = existing.get(key)
            results_type = obs.results_type or (prev.results_type if prev else "")
            if key in devices:
                # Same empty-project DeviceId already from another OPC folder.
                existing_dev = devices[key]
                same_path = (
                    existing_dev.opc_server == obs.opc_server
                    and existing_dev.opc_item_prefix == obs.opc_item_prefix
                )
                if not same_path and existing_dev.present_on_opc:
                    collisions.append(
                        MergeCollision(
                            device_tag=obs.device_tag,
                            opc_path=f"{obs.opc_server}|{obs.opc_item_prefix}",
                            device_ids=[key],
                        )
                    )
                continue
            devices[key] = Device(
                device_id=did,
                results_type=results_type,
                opc_server=obs.opc_server,
                opc_item_prefix=obs.opc_item_prefix,
                present_on_opc=True,
                source_kind="opc",
            )

        # Keep SILworX/project devices across cycles when the API is down or
        # the project was closed — do not drop them just because silworx_rows is empty.
        for key, prev in existing.items():
            if key in devices:
                continue
            if not str(prev.device_id.project or "").strip():
                continue
            carried = Device(
                device_id=prev.device_id,
                results_type=prev.results_type,
                opc_server=prev.opc_server,
                opc_item_prefix=prev.opc_item_prefix,
                present_on_opc=bool(prev.present_on_opc),
                test_in_progress=bool(prev.test_in_progress),
                last_running=prev.last_running,
                is_active=True,
                source_kind=prev.source_kind if prev.source_kind not in ("", "unknown", "opc") else "project",
            )
            matches = self._opc_matches_for_tag(carried.device_tag, opc_by_tag)
            chosen = self._choose_opc_for_device(carried, matches)
            if chosen is not None:
                carried.opc_server = chosen.opc_server
                carried.opc_item_prefix = chosen.opc_item_prefix
                carried.present_on_opc = True
            devices[key] = carried

        # Prefer project-scoped rows over OPC-only (empty project) for the same TAG
        # (including '/' vs '_' HIMA export aliases).
        project_tags = {
            d.device_tag
            for d in devices.values()
            if str(d.device_id.project or "").strip()
        }
        if project_tags:
            devices = {
                key: device
                for key, device in devices.items()
                if str(device.device_id.project or "").strip()
                or not any(
                    self._tags_equivalent(device.device_tag, pt) for pt in project_tags
                )
            }

        return MergeResult(
            devices=list(devices.values()),
            collisions=collisions,
            skipped_duplicates=skipped,
        )

    @staticmethod
    def _choose_opc_for_device(
        device: Device, matches: list[OpcObservation]
    ) -> Optional[OpcObservation]:
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        # Prefer paths whose prefix ends with the device TAG (user folder names vary).
        for obs in matches:
            for tag in CatalogMerger._tag_lookup_keys(device.device_tag):
                ending = "." + tag
                if obs.opc_item_prefix == tag or obs.opc_item_prefix.endswith(ending):
                    return obs
        return matches[0]
