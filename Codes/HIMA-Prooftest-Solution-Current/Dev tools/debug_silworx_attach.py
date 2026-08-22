#!/usr/bin/env python3
"""One-shot SILworX API attach diagnosis (dev)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "Annex codes"))
sys.path.insert(0, str(_ROOT / "Tool Steps"))

from prooftest.annex_api_connexion import (  # noqa: E402
    build_client_for_port,
    discover_available_instances,
    resolve_api_server_cert,
    resolve_gui_session_id,
)
from prooftest.config import AppConfig  # noqa: E402
from prooftest.step07_triggers import SilworxSyncTriggers  # noqa: E402


def main() -> int:
    cfg = AppConfig.load(_ROOT / "solution.ini")
    print("configured projects", cfg.silworx_projects)
    print("api_cert cfg", cfg.silworx_api_cert)
    try:
        cert = resolve_api_server_cert(cfg.silworx_programdata, cfg.silworx_api_cert)
        print("resolved cert", cert, "exists", cert.is_file())
    except Exception as exc:
        print("cert resolve FAIL", exc)

    for p in sorted(Path(cfg.silworx_programdata).glob("SILworX_v*")):
        c = p / "settings" / "api_cert.pem"
        print(" install", p.name, "cert", c.is_file())

    instances = discover_available_instances(cfg)
    print(
        "instances",
        [(i.label, i.silworx_version, i.product_name) for i in instances],
    )

    sync = SilworxSyncTriggers(config=cfg)
    sync.prepare_for_engine_start()
    sync.start_monitor()
    time.sleep(4)
    sessions = sync.refresh_open_sessions()
    print(
        "open_sessions",
        [(s.project_name, s.session_id, s.silworx_version) for s in sessions],
    )
    print(
        "active",
        sync.active_session.project_name if sync.active_session else None,
    )
    print("plugin summary", sync.plugin_monitor_summary())

    for inst in instances:
        sid = resolve_gui_session_id(
            cfg,
            inst.api_port,
            plugin_monitor=sync._plugin_monitor,
            timeout_sec=12,
        )
        print(
            "session_id port",
            inst.api_port,
            "->",
            (sid[:24] + "...") if sid else None,
        )
        if not sid:
            continue
        client = build_client_for_port(cfg, inst.api_port)
        client.set_session_id(sid)
        try:
            tree = client.get_structuretree()
            print(
                "structuretree OK",
                list(tree)[:8] if isinstance(tree, dict) else type(tree),
            )
            ok = sync._try_attach_gui_session_on_port(inst.api_port)
            print(
                "try_attach",
                ok,
                "attached_map",
                dict(sync._attached_project_names_by_api),
            )
        except Exception as exc:
            print("structuretree/attach FAIL", type(exc).__name__, exc)

    try:
        sync.shutdown()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
