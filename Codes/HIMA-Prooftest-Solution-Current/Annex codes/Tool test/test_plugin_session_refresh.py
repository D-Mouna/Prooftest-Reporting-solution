#!/usr/bin/env python3
"""Unit checks: plugin session cache is dropped and re-register is requested."""

from __future__ import annotations

from _paths import CONFIG_INI, setup_path

setup_path()

from prooftest.annex_api_connexion import is_unusable_gui_session_error
from prooftest.annex_plugin_monitor import PluginPortMonitor
from prooftest.config import AppConfig


def main() -> int:
    cfg = AppConfig.load(CONFIG_INI)
    monitor = PluginPortMonitor(cfg)
    monitor._ensure_port_state(51710, 8400)
    with monitor._lock:
        monitor._ports[8400].session_id = "stale-token"

    monitor.request_fresh_session(8400)
    if monitor.get_session_id(8400):
        print("FAIL cache still held stale session after request_fresh_session")
        return 1
    if not monitor._should_reregister(8400):
        print("FAIL re-register flag not set")
        return 1
    if monitor._should_reregister(8400):
        print("FAIL re-register flag not consumed")
        return 1

    if not is_unusable_gui_session_error(RuntimeError("The session ID is not valid.")):
        print("FAIL stale-session error not detected")
        return 1
    if not is_unusable_gui_session_error(RuntimeError("No project opened.")):
        print("FAIL no-project error not detected")
        return 1
    if is_unusable_gui_session_error(RuntimeError("connection refused")):
        print("FAIL unrelated error treated as stale session")
        return 1

    print("OK  plugin session refresh helpers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
