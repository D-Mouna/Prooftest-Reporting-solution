#!/usr/bin/env python3
"""Diagnose API device count vs catalog and OPC bind."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "Annex codes"))
sys.path.insert(0, str(_ROOT / "Tool Steps"))

from prooftest.config import AppConfig
from prooftest.results_csv import load_all_structures
from prooftest.step07_triggers import SilworxSyncTriggers


def main() -> int:
    cfg = AppConfig.load(_ROOT / "solution.ini")
    structures = load_all_structures(cfg.results_structures)
    known = set(structures.keys())
    print("known_types", len(known), sorted(known))

    markers = Path(cfg.sqlite_path).parent / "sync_markers"
    markers.mkdir(parents=True, exist_ok=True)
    sync = SilworxSyncTriggers(config=cfg, markers_dir=markers)
    sync.prepare_for_engine_start()
    sync.start_monitor()
    import time

    time.sleep(3)
    from prooftest.step03_device_list import try_discover_devices_via_api

    class Quiet:
        def raise_alarm(self, *a, **k):
            return None

    devices = try_discover_devices_via_api(sync, known, Quiet()) or []
    print("api_devices", len(devices))
    for d in devices:
        print(
            f"  {d.device_tag!r} type={d.results_type!r} cfg={d.configuration!r} res={d.resource!r}"
        )

    # OPC browse ProofTest branches on servers that have tags
    from prooftest.annex_opc import OpcManager

    opc = OpcManager(cfg.opc_server_filter)
    servers = opc.discover_servers()
    print("opc_servers", servers)
    tags_by = opc.list_tags_all_servers(servers)
    for srv, tags in tags_by.items():
        running = [t for t in tags if t.endswith(".Running") and ("ProofTest" in t)]
        print(f"  {srv}: tags={len(tags)} proofTest_Running={len(running)}")
        for t in sorted(running)[:30]:
            print(f"    {t}")

    api_tags = {d.device_tag for d in devices}
    for d in devices:
        path = None
        for srv in servers:
            path = opc.find_running_path(srv, d.device_tag)
            if path:
                print(f"BIND ok {d.device_tag} -> {srv} {path}")
                break
        if not path:
            print(f"BIND miss {d.device_tag}")

    try:
        sync.shutdown()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
