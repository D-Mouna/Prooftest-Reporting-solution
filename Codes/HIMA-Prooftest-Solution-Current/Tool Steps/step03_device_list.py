"""
SPEC Step 3 — Device Prooftest Result List (G-22 data layer).

Every device-list update/refresh queries **SILworX API and X-OPC at the same
time**. API metadata (Results_Type, Configuration, Resource) is read from
structuretree + globalvariables **only when the user has a project open**
(attach; never ``open/local``). Each device is a **global variable** whose data
type is one of the Results structures defined by CSVs under
``Results Structures\\`` (baseline nine + any new types). Operators do not
invent devices by editing CSV rows; they add a CSV only to register a **new
Results structure type**. OPC browse supplies server/prefix/PresentOnOpc and
devices that exist only on X-OPC. Realtime values are never read here — see
step05.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Set, Tuple

from prooftest.annex_api_connexion import (
    GlobalVariableRecord,
    GlobalVariablesNode,
    SilworxApiConnectionError,
    SilworxApiError,
    SilworxProjectConflictError,
    acquire_open_project_session_id,
    build_client_from_config,
)
from prooftest.annex_opc import OpcManager
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.results_csv import ResultsStructure
from prooftest.step01_setup import sync_device_report_folders
from prooftest.step07_triggers import Case1SyncTriggers

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApiDiscoveredDevice:
    """One Prooftest device row from SILworX global variables."""

    device_tag: str
    results_type: str
    configuration: str
    resource: str
    gv_node_path: str
    silworx_project: str = ""


def collect_devices_from_global_variables(
    client,
    known_types: Set[str],
) -> List[ApiDiscoveredDevice]:
    """
    Scan every Global Variables node in the open API project session.

    A device is a top-level global whose data type is one of the known `_Results`
    structures (loaded from Results Structure CSVs).
    """
    tree = client.get_structuretree()
    gv_nodes: List[GlobalVariablesNode] = client.find_all_globalvariable_nodes(tree)
    if not gv_nodes:
        log.warning("SILworX API: no Global Variables nodes in structure tree")
        return []

    found: List[ApiDiscoveredDevice] = []
    seen_tags: Set[str] = set()

    for node in gv_nodes:
        variables: List[GlobalVariableRecord] = client.list_top_level_globals(node.internal_address)
        for var in variables:
            if var.data_type not in known_types:
                continue
            if not var.name or "." in var.name:
                continue
            if var.name in seen_tags:
                log.warning(
                    "Duplicate Device_TAG %s in SILworX globals (skipped duplicate at %s)",
                    var.name,
                    node.tree_path,
                )
                continue
            seen_tags.add(var.name)
            found.append(
                ApiDiscoveredDevice(
                    device_tag=var.name,
                    results_type=var.data_type,
                    configuration=node.configuration,
                    resource=node.resource,
                    gv_node_path=node.tree_path,
                )
            )
            log.info(
                "API device %s -> %s (config=%s, resource=%s, path=%s)",
                var.name,
                var.data_type,
                node.configuration or "-",
                node.resource or "-",
                node.tree_path,
            )

    return found


def try_discover_devices_via_api(
    case1_sync: Case1SyncTriggers,
    known_types: Set[str],
    alarms,
) -> Optional[List[ApiDiscoveredDevice]]:
    """
    Attempt API-based discovery on every reachable SILworX API instance (G-21).

    Returns:
      - merged device list on success (may be empty)
      - None when this refresh has no API contribution (OPC still runs in parallel)
    """
    if case1_sync.is_api_suspended():
        log.info("SILworX API suspended — API contribution skipped; OPC still scanned")
        return None

    instances = case1_sync.discover_api_instances()
    if not instances:
        log.warning("No SILworX API instances reachable on configured port range")
        return None

    merged: Dict[str, ApiDiscoveredDevice] = {}
    any_success = False
    had_conflict = False

    for instance in instances:
        try:
            with case1_sync.api_session_for_port(
                instance.api_port,
                alarms=alarms,
                allow_open_local=False,
            ) as client:
                devices = collect_devices_from_global_variables(client, known_types)
        except SilworxProjectConflictError:
            log.info(
                "No user-open SILworX project on %s — skipping instance (OPC still scanned)",
                instance.label,
            )
            had_conflict = True
            continue
        except (SilworxApiError, SilworxApiConnectionError, TimeoutError) as exc:
            log.warning("SILworX API device discovery failed on %s: %s", instance.label, exc)
            continue

        any_success = True
        project_name = case1_sync.attached_project_name_for_port(instance.api_port)
        for device in devices:
            stamped = replace(device, silworx_project=project_name or device.silworx_project)
            merged[stamped.device_tag] = stamped
        log.info(
            "API device discovery on %s: %d device(s) (project=%s)",
            instance.label,
            len(devices),
            project_name or "-",
        )

    if not any_success:
        if had_conflict:
            log.info("No user-open SILworX project on any port — API contribution empty")
        return None
    return list(merged.values())


OpcDiscoveredDevice = Tuple[str, str, str, str]  # Device_TAG, Results_Type, OPC_Server, prefix


def _device_list_source_label(api_ok: bool, opc_ok: bool) -> str:
    if api_ok and opc_ok:
        return "api+opc"
    if api_ok:
        return "api"
    return "opc_fallback"


def _discover_opc_or_none(
    opc: OpcManager | None,
    structures: Dict[str, ResultsStructure],
) -> Optional[List[OpcDiscoveredDevice]]:
    """OPC browse for the parallel device-list update. None = browse failed / unavailable."""
    if opc is None:
        return None
    try:
        return discover_devices_from_opc(opc, structures)
    except Exception as exc:
        log.warning("OPC device discovery failed: %s", exc)
        return None


def apply_merged_device_list(
    config: AppConfig,
    db: Database,
    api_devices: Optional[List[ApiDiscoveredDevice]],
    opc_discovered: Optional[List[OpcDiscoveredDevice]],
    structures: Dict[str, ResultsStructure],
) -> Tuple[List[str], str]:
    """
    Persist the union of simultaneous API and OPC discoveries.

    API wins Results_Type / Configuration / Resource.
    OPC wins OPC_Server / OPC_ItemPrefix / PresentOnOpc.
    """
    del structures  # type catalogue used only by the discover callers
    api_ok = api_devices is not None
    opc_ok = opc_discovered is not None
    api_by_tag = {device.device_tag: device for device in (api_devices or [])}
    opc_map: Dict[str, Tuple[str, str]] = {}
    opc_type: Dict[str, str] = {}
    for device_tag, results_type, server, prefix in opc_discovered or []:
        opc_map[device_tag] = (server, prefix)
        opc_type[device_tag] = results_type

    from prooftest.annex_list_archive import keep_opc_only_enabled

    keep_opc_only = opc_ok and keep_opc_only_enabled(db)

    ordered_tags: List[str] = []
    seen: Set[str] = set()

    def _add(tag: str) -> None:
        if tag and tag not in seen:
            seen.add(tag)
            ordered_tags.append(tag)

    for tag in api_by_tag:
        if keep_opc_only and tag not in opc_map:
            continue
        _add(tag)
    for tag in opc_map:
        _add(tag)

    active: List[str] = []
    folder_pairs: List[Tuple[str, str]] = []
    for tag in ordered_tags:
        api_dev = api_by_tag.get(tag)
        server, prefix = opc_map.get(tag, (None, None))
        if api_dev is not None:
            results_type = api_dev.results_type
            configuration = api_dev.configuration or None
            resource = api_dev.resource or None
        else:
            results_type = opc_type.get(tag, "")
            configuration = None
            resource = None
        if not results_type:
            continue
        active.append(tag)
        folder_pairs.append((tag, results_type))
        db.upsert_device(
            tag,
            results_type,
            opc_server=server,
            opc_prefix=prefix,
            configuration=configuration,
            resource=resource,
            silworx_project=(api_dev.silworx_project or None) if api_dev is not None else None,
        )

    db.reconcile_device_list(active, report_output=config.report_output)
    if opc_ok:
        db.set_present_on_opc(set(opc_map.keys()))
    if folder_pairs:
        sync_device_report_folders(config, folder_pairs, db.alarms)

    source = _device_list_source_label(api_ok, opc_ok)
    if not active:
        if api_ok:
            db.alarms.raise_alarm(
                "P3-C1",
                "No Prooftest Results devices from SILworX API or X-OPC",
                severity="Warning",
                show_popup=False,
            )
        else:
            db.alarms.raise_alarm(
                "P2-C1",
                "No Prooftest devices matched in any X-OPC server (API unavailable)",
                severity="Warning",
                show_popup=False,
            )
    else:
        log.info(
            "Device list (%s): %d device(s): %s",
            source,
            len(active),
            ", ".join(active),
        )
    return active, source


def apply_api_device_list(
    config: AppConfig,
    db: Database,
    devices: List[ApiDiscoveredDevice],
    opc: OpcManager | None,
    structures: Dict[str, ResultsStructure],
) -> List[str]:
    """Persist API devices, merging a live OPC browse when the manager is available."""
    opc_discovered = _discover_opc_or_none(opc, structures)
    active, _source = apply_merged_device_list(config, db, devices, opc_discovered, structures)
    return active


def sync_device_list_case1_via_api(
    config: AppConfig,
    db: Database,
    structures: Dict[str, ResultsStructure],
    case1_sync: Case1SyncTriggers,
    opc: OpcManager | None = None,
) -> Tuple[List[str], str]:
    """
    Device list update/refresh: SILworX API and X-OPC run **at the same time**.

    API attaches only if the user has a project open (never open/local).
    Results are merged once: ``api+opc``, ``api``, or ``opc_fallback``.
    """
    known_types = set(structures.keys())

    def _api_job() -> Optional[List[ApiDiscoveredDevice]]:
        return try_discover_devices_via_api(case1_sync, known_types, db.alarms)

    def _opc_job() -> Optional[List[OpcDiscoveredDevice]]:
        return _discover_opc_or_none(opc, structures)

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="device-list") as pool:
        api_future = pool.submit(_api_job)
        opc_future = pool.submit(_opc_job)
        api_devices = api_future.result()
        opc_discovered = opc_future.result()

    return apply_merged_device_list(config, db, api_devices, opc_discovered, structures)


def sync_device_list_from_opc(
    config: AppConfig,
    db: Database,
    opc: OpcManager,
    structures: Dict[str, ResultsStructure],
) -> List[str]:
    """Update device list by scanning X-OPC (when SILworX/API is unavailable)."""
    return _sync_from_opc_discovery(
        db,
        opc,
        structures,
        config=config,
        alarm_step="P2-C1",
        empty_message="No Prooftest devices matched in any X-OPC server",
    )


# Backward-compatible alias (former separate Case 2 entry point).
sync_device_list_case2 = sync_device_list_from_opc


def _normalize_member(name: str) -> str:
    return name.replace(" ", "").lower()


def _score_structure_match(member_names: Set[str], structure: ResultsStructure) -> int:
    required = {_normalize_member(m) for m in structure.member_short_names()}
    required.discard("")
    if "running" not in required:
        return 0
    normalized = {_normalize_member(m) for m in member_names}
    return len(required.intersection(normalized))


def _member_names_under_prefix(tags: List[str], prefix: str) -> Set[str]:
    """Member names directly under a device prefix (e.g. OTS ProofTest.100-FZT-001)."""
    prefix_dot = prefix + "."
    members: Set[str] = set()
    for tag in tags:
        if tag.startswith(prefix_dot):
            remainder = tag[len(prefix_dot) :]
            top = remainder.split(".")[0]
            if top:
                members.add(top)
    return members


def _discover_on_server(
    server: str,
    tags: List[str],
    structures: Dict[str, ResultsStructure],
) -> List[Tuple[str, str, str, str]]:
    found: List[Tuple[str, str, str, str]] = []
    seen_prefixes: Set[str] = set()

    for running_tag in sorted(t for t in tags if t.endswith(".Running")):
        prefix = running_tag[: -len(".Running")]
        if not prefix or prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        device_tag = prefix.split(".")[-1]
        members = _member_names_under_prefix(tags, prefix)

        best_type = ""
        best_score = 0
        for type_name, structure in structures.items():
            score = _score_structure_match(members, structure)
            if score > best_score and score >= 3:
                best_score = score
                best_type = type_name
        if best_type:
            found.append((device_tag, best_type, server, prefix))
            log.info(
                "OPC device %s on %s -> %s (prefix=%s, score=%d)",
                device_tag,
                server,
                best_type,
                prefix,
                best_score,
            )
    return found


def discover_devices_from_opc(
    opc: OpcManager,
    structures: Dict[str, ResultsStructure],
) -> List[Tuple[str, str, str, str]]:
    servers = opc.discover_servers()
    if not servers:
        return []

    best_match: Dict[str, Tuple[int, str, str, str]] = {}
    all_tags = opc.list_tags_all_servers(servers)
    log.info("Scanning %d X-OPC server(s) on branches %s", len(servers), opc.prooftest_branches)

    for server, tags in all_tags.items():
        if not tags:
            log.warning("No tags browsed on server %s", server)
            continue
        for device_tag, results_type, srv, prefix in _discover_on_server(server, tags, structures):
            members = _member_names_under_prefix(tags, prefix)
            score = _score_structure_match(members, structures[results_type])
            current = best_match.get(device_tag)
            if current is None or score > current[0]:
                best_match[device_tag] = (score, results_type, srv, prefix)

    return [(tag, t, srv, pfx) for tag, (_, t, srv, pfx) in sorted(best_match.items())]


def _sync_from_opc_discovery(
    db: Database,
    opc: OpcManager | None,
    structures: Dict[str, ResultsStructure],
    *,
    config: AppConfig | None = None,
    alarm_step: str,
    empty_message: str,
) -> List[str]:
    if opc is None:
        db.alarms.raise_alarm(
            alarm_step,
            "OPC manager not available for device discovery",
            severity="Warning",
            show_popup=False,
        )
        return []

    discovered = discover_devices_from_opc(opc, structures)
    active: List[str] = []
    folder_pairs: List[Tuple[str, str]] = []
    for device_tag, results_type, server, prefix in discovered:
        active.append(device_tag)
        folder_pairs.append((device_tag, results_type))
        db.upsert_device(
            device_tag,
            results_type,
            opc_server=server,
            opc_prefix=prefix,
        )
    report_dir = config.report_output if config is not None else None
    db.reconcile_device_list(active, report_output=report_dir)
    db.set_present_on_opc(set(active))
    if config is not None and folder_pairs:
        sync_device_report_folders(config, folder_pairs, db.alarms)
    if not active:
        db.alarms.raise_alarm(
            alarm_step,
            empty_message,
            severity="Warning",
            show_popup=False,
        )
    else:
        log.info("Device list: %d device(s): %s", len(active), ", ".join(active))
    return active