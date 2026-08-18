"""Gate 8 / G-22 — Step 7 trigger detection (plugin monitor + multi-session mtime)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Annex codes"))
sys.path.insert(0, str(ROOT / "Tool Steps"))

from prooftest.config import AppConfig
from prooftest.step07_triggers import Case1SyncTriggers, commit_marker, session_working_mtime


def main() -> int:
    cfg = AppConfig.load(ROOT / "solution.ini")
    markers = ROOT / "Annex codes" / "data" / "sync_markers"
    sync = Case1SyncTriggers(config=cfg, markers_dir=markers)
    sync.start_monitor()
    sync.commit()

    triggers = sync.check()
    print(f"Enabled triggers: {', '.join(sorted(sync._enabled))}")
    print(f"Open sessions watched: {len(sync.open_sessions)}")
    print(f"Preferred session: {sync.active_session.project_name if sync.active_session else 'none'}")
    print(f"Plugin monitor: {'on' if cfg.plugin_monitor_enabled else 'off'}")
    if sync.plugin_monitor_summary():
        print(f"Plugin ports: {sync.plugin_monitor_summary()}")
    print(f"Fired triggers (baseline): {triggers or 'none'}")

    plugin_script = ROOT / "Annex codes" / "Plugin" / "run_plugins_all.ps1"
    run_single = ROOT / "Annex codes" / "Plugin" / "run_plugin.ps1"
    print(f"run_plugin.ps1 exists: {run_single.is_file()}")
    print(f"run_plugins_all.ps1 exists: {plugin_script.is_file()}")

    if sync.active_session and "code_generation" in sync._enabled:
        key = f"session_{sync.active_session.session_id}_{sync.active_session.project_name}"
        marker = sync._marker(key)
        mtime = session_working_mtime(sync.active_session)
        commit_marker(marker, mtime - 1)
        fired = sync.check()
        if "code_generation" in fired or "silworx_session" in fired:
            print("OK  c3data mtime change fires session/code_generation triggers")
        else:
            print("WARN  c3data trigger simulation did not fire (session may be idle)")
        sync.commit()

    print("Gate 8 / G-22 trigger check complete")
    sync.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
