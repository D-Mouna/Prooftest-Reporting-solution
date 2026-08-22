#!/usr/bin/env python3
"""Step 6 — Device list via simultaneous SILworX API and X-OPC."""

from __future__ import annotations

import sys
from pathlib import Path

from _paths import CONFIG_INI, SYNC_MARKERS, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.step04_opc import OpcManager
from prooftest.results_csv import load_all_structures
from prooftest.step07_triggers import Case1SyncTriggers, discover_open_projects
from prooftest.step03_device_list import sync_device_list_case1_via_api


def main() -> int:
    config = AppConfig.load(CONFIG_INI)
    alarms = AlarmManager()
    db = Database(config, alarms)
    db.connect()
    structures = load_all_structures(config.results_structures)
    opc = OpcManager(config.opc_server_filter)
    case1_sync = Case1SyncTriggers(config, SYNC_MARKERS)

    open_sessions = discover_open_projects(config.silworx_programdata)
    if open_sessions:
        print(f"silworx_open_sessions={len(open_sessions)} (API attach; tool does not open projects)")
        for s in open_sessions:
            print(f"  session={s.session_id} project={s.project_name}")
    else:
        print("silworx_open_sessions=0")

    active, source = sync_device_list_case1_via_api(config, db, structures, case1_sync, opc)
    print(f"source={source} active_count={len(active)}")

    devices = db.list_active_devices()
    with_config = sum(1 for d in devices if d.get("configuration") or d.get("resource"))
    print(f"devices_with_config_or_resource={with_config}/{len(devices)}")

    for d in devices[:5]:
        print(
            f"  {d['device_tag']}: {d['results_type']} "
            f"cfg={d.get('configuration')!r} res={d.get('resource')!r} "
            f"opc={d.get('opc_server') or '-'}"
        )

    state = db.get_service_state()
    if source == "api+opc":
        if not active:
            print("FAIL API+OPC returned no devices")
            return 1
        print("OK device list from SILworX API and X-OPC together")
        return 0

    if source == "api":
        if not active:
            print("FAIL API returned no devices")
            return 1
        print("OK device list from SILworX API (OPC browse unavailable)")
        return 0

    if source == "opc_fallback":
        print("NOTE no user-open SILworX project (or API unavailable) — OPC contribution only")
        if not active:
            print("FAIL no devices from OPC either")
            return 1
        print("OK OPC-only device list")
        return 0

    print("FAIL unknown source", source)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
