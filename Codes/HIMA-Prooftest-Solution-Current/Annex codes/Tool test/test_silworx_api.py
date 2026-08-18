#!/usr/bin/env python3
"""
Live verification for SPEC Step 3 — SILworX SAPI client (attach only).

Run with 32-bit Python while SILworX v16 is running **and the user has a project open**.
The report tool never opens a project; this script attaches the same way.
"""

from __future__ import annotations

from _paths import CONFIG_INI, SYNC_MARKERS, setup_path

setup_path()

from prooftest.config import AppConfig
from prooftest.step07_triggers import Case1SyncTriggers
from prooftest.annex_api_connexion import (
    SilworxApiConnectionError,
    SilworxApiError,
    SilworxProjectConflictError,
)


def main() -> int:
    config = AppConfig.load(CONFIG_INI)
    triggers = Case1SyncTriggers(config=config, markers_dir=SYNC_MARKERS)
    client = triggers.get_api_client()

    try:
        info = client.get_silworx_info()
    except SilworxApiConnectionError as exc:
        print(f"SKIP: SILworX API not reachable on {config.silworx_api_host}:{config.silworx_api_port}")
        print(f"  ({exc})")
        print("  Start SILworX v16 and open a project, then rerun.")
        return 2

    print("OK silworx/info:", str(info)[:200])

    try:
        with triggers.api_session() as session:
            tree = session.get_structuretree()
            nodes = session.find_all_globalvariable_nodes(tree)
            print(f"OK structuretree: {len(nodes)} Global Variables node(s)")
            for node in nodes[:5]:
                print(f"  - {node.tree_path} @ {node.internal_address}")
                globals_list = session.list_top_level_globals(node.internal_address)
                print(f"    variables: {len(globals_list)}")
    except SilworxProjectConflictError as exc:
        print("NO_USER_PROJECT (open a project in SILworX GUI to use API):", exc)
        return 0
    except SilworxApiError as exc:
        print("FAIL:", exc)
        return 1

    print("OK attached to user-open project (tool did not open/close the project)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
