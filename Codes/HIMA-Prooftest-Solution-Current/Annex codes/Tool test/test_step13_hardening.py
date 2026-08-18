#!/usr/bin/env python3
"""
Gate 13 / SPEC hardening — non-blocking health, web auth, template column mapping.

Verifies:
  1. service.health() uses OpcManager.health_snapshot() (no blocking OPC browse).
  2. Optional web auth: 401 without token; 200 with X-Prooftest-Token when enabled.
  3. verify_template_placeholder_mapping — all twelve HIMA templates resolve placeholders.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

from _paths import CONFIG_INI, TEST_DATA, setup_path

setup_path()

from prooftest.annex_opc import OpcServerInfo
from prooftest.config import AppConfig
from prooftest.annex_pdf_generation import verify_template_placeholder_mapping
from prooftest.results_csv import load_all_structures
from prooftest.service import ProoftestService
from prooftest.web.app import create_app

AUTH_TOKEN = "gate13-test-token"


def test_health_non_blocking() -> int:
    opc = MagicMock()
    opc.health_snapshot.return_value = [
        OpcServerInfo(prog_id="Mock.X_OPC.Server", connected=True, tag_count=12)
    ]

    config = AppConfig.load(CONFIG_INI)
    service = ProoftestService(config)
    service.opc = opc  # type: ignore[assignment]
    service.db = MagicMock()
    service.db.list_active_devices.return_value = []
    service.db.count_listed_devices.return_value = 0
    service.db.count_opc_devices.return_value = 0
    service.db.get_service_state.return_value = {}
    service.db.using_sqlite = True
    service.monitor = None
    service._case1_sync.active_session = None
    service._case1_sync._available_instances = []

    start = time.perf_counter()
    health = service.health()
    elapsed = time.perf_counter() - start

    if elapsed > 0.5:
        print(f"FAIL health() took {elapsed:.2f}s — expected non-blocking snapshot")
        return 1
    if not opc.health_snapshot.called:
        print("FAIL health() did not call opc.health_snapshot()")
        return 1
    if opc.server_status.called:
        print("FAIL health() must not call blocking opc.server_status()")
        return 1
    if not health.get("opc_servers"):
        print("FAIL health payload missing opc_servers")
        return 1
    print("OK  /api/health uses non-blocking OPC snapshot")
    return 0


def test_web_auth() -> int:
    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        print(f"FAIL TestClient unavailable: {exc}")
        return 1

    service = MagicMock()
    service.config.web_auth_enabled = True
    service.config.web_auth_token = AUTH_TOKEN
    service.config.web_localhost_bypass = False
    service.config.report_output = MagicMock()
    service.config.report_mirror = MagicMock()
    service.health.return_value = {
        "deployment_case": 1,
        "database": "sqlite",
        "opc_servers": [],
        "active_devices": 0,
        "queue_depth": 0,
        "silworx": {},
        "silworx_api_instances": [],
        "service_state": {},
        "stopping": False,
        "web_auth_required": True,
    }
    service.db.list_active_devices.return_value = []
    service.db.list_devices.return_value = []
    service.db.list_recent_alarms.return_value = []
    service.alarms.pop_pending_popups.return_value = []
    service.alarms.recent_alarms.return_value = []
    service._stopped = False

    client = TestClient(create_app(service))

    denied = client.get("/api/health")
    if denied.status_code != 401:
        print(f"FAIL expected 401 without token, got {denied.status_code}")
        return 1

    allowed = client.get("/api/health", headers={"X-Prooftest-Token": AUTH_TOKEN})
    if allowed.status_code != 200:
        print(f"FAIL expected 200 with token, got {allowed.status_code}")
        return 1

    query = client.get(f"/api/health?token={AUTH_TOKEN}")
    if query.status_code != 200:
        print(f"FAIL expected 200 with ?token=, got {query.status_code}")
        return 1

    print("OK  web auth token gate (401 / X-Prooftest-Token / ?token=)")
    return 0


def test_auth_disabled_without_token() -> int:
    TEST_DATA.mkdir(parents=True, exist_ok=True)
    lines = []
    for line in CONFIG_INI.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("auth_enabled"):
            lines.append("auth_enabled = true")
        elif stripped.startswith("auth_token"):
            lines.append("auth_token =")
        else:
            lines.append(line)
    tmp_ini = TEST_DATA / "gate13_auth_no_token.ini"
    tmp_ini.write_text("\n".join(lines) + "\n", encoding="utf-8")
    config = AppConfig.load(tmp_ini)
    if config.web_auth_enabled:
        print("FAIL auth must not stay enabled with empty token")
        return 1
    print("OK  auth disabled when token is empty")
    return 0


def test_template_placeholder_mapping() -> int:
    config = AppConfig.load(CONFIG_INI)
    structures = load_all_structures(config.results_structures)
    failures = verify_template_placeholder_mapping(config.report_html_templates, structures)
    if failures:
        print(f"FAIL unresolved template placeholders ({len(failures)}):")
        for item in failures[:20]:
            print(f"  {item}")
        return 1
    print("OK  all HIMA report templates resolve snapshot placeholders")
    return 0


def test_auto_start_config() -> int:
    config = AppConfig.load(CONFIG_INI)
    if not config.auto_start:
        print("FAIL auto_start should default to true in solution.ini")
        return 1
    if config.auto_start_delay_sec < 1:
        print("FAIL auto_start_delay_sec must be positive")
        return 1
    if config.auto_start_trigger not in ("logon", "startup"):
        print(f"FAIL auto_start_trigger must be logon or startup (got {config.auto_start_trigger!r})")
        return 1
    if config.health_check_wait_sec < 30:
        print("FAIL health_check_wait_sec must be at least 30")
        return 1
    root = CONFIG_INI.resolve().parent
    for name in ("install_auto_start.ps1", "uninstall_auto_start.ps1"):
        if not (root / name).is_file():
            print(f"FAIL missing {name}")
            return 1
    annex = root / "Annex codes" / "Stop service" / "annex_windows_auto_start.ps1"
    if not annex.is_file():
        print("FAIL missing annex_windows_auto_start.ps1")
        return 1
    print("OK  auto_start config and Windows auto-start scripts present")
    return 0


def main() -> int:
    tests = (
        test_health_non_blocking,
        test_web_auth,
        test_auth_disabled_without_token,
        test_template_placeholder_mapping,
        test_auto_start_config,
    )
    failed = 0
    for test in tests:
        try:
            failed += test()
        except Exception as exc:
            print(f"FAIL {test.__name__}: {exc}")
            failed += 1
    if failed:
        print(f"\nGate 13: {failed} check(s) failed")
        return 1
    print("\nGate 13: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
