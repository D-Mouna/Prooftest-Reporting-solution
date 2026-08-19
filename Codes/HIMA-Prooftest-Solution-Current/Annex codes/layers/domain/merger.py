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
            matches = opc_by_tag.get(device.device_tag) or []
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
            if obs.device_tag in used_tags_with_silworx and any(
                d.device_tag == obs.device_tag and d.present_on_opc for d in devices.values()
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
        # Prefer constructed OTS then OPC ProofTest prefixes ending with the TAG.
        tag = device.device_tag
        for branch in ("OTS ProofTest", "OPC ProofTest"):
            want = f"{branch}.{tag}"
            for obs in matches:
                if obs.opc_item_prefix == want or obs.opc_item_prefix.endswith("." + tag):
                    if obs.opc_item_prefix.startswith(branch) or obs.opc_item_prefix == want:
                        return obs
        return matches[0]
