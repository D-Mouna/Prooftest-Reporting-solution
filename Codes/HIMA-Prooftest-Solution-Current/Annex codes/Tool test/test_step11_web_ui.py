#!/usr/bin/env python3
"""
Gate 11 / SPEC Part 2 — Web UI + alarms.

Verifies:
  1. Static assets under Graphic Interface/static/.
  2. FastAPI routes with a lightweight mocked service.
  3. GET /api/reports accepts results_type for scoped folder lookup.
  4. raise_alarm persists rows to AlarmLog.
  5. Health payload includes silworx and opc_servers fields.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from _paths import CONFIG_INI, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.annex_pdf_generation import device_report_dir, write_reports
from prooftest.web.app import APP_VERSION, STATIC_DIR, create_app

TEST_TAG = "GATE11-UI-DEVICE"
RESULTS_TYPE = "X-HART_E+H_PMx7xB_Results"


def _alarms_payload(service: MagicMock) -> dict:
    try:
        keys = service.alarms.active_error_keys()
        active_keys = set(keys) if isinstance(keys, (set, list, tuple, frozenset)) else set()
    except Exception:
        active_keys = set()
    enriched = []
    for row in service.db.list_recent_alarms():
        item = dict(row)
        key = item.get("error_key") or f"{item.get('step')}|{str(item.get('message') or '')[:120]}"
        item["error_key"] = key
        item["acknowledged"] = bool(item.get("acknowledged"))
        item["active"] = key in active_keys
        enriched.append(item)
    return {
        "alarms": enriched,
        "popups": list(service.alarms.pop_pending_popups()),
    }


def _attach_application_facade(service: MagicMock) -> object:
    """Wire a plain Application facade stand-in — Presentation has no DB/annex fallbacks."""
    from prooftest.annex_pdf_generation import list_reports_for_device

    class _TestFacade:
        def __init__(self) -> None:
            self._host = service
            self.config = service.config
            self.alarms = service.alarms
            self.engine_running = bool(getattr(service, "engine_running", True))
            self._stopped = bool(getattr(service, "_stopped", False))
            self._starting = bool(getattr(service, "_starting", False))

        def get_engine_status(self):
            return service.health()

        def list_devices(self, view: str = "all"):
            try:
                return list(service.db.list_devices(view=view))
            except TypeError:
                return list(service.db.list_devices())

        def list_running_tests(self):
            return list(service.db.list_running_tests())

        def list_test_history(self):
            return list(service.db.list_test_history())

        def list_alarms(self):
            return _alarms_payload(service)

        def acknowledge_alarm(self, alarm_id: int):
            return service.db.acknowledge_alarm(alarm_id)

        def reset_alarms(self):
            return service.db.reset_alarms()

        def refresh_catalog(self):
            return service.refresh(manual=True)

        def start_engine(self):
            return service.start()

        def stop_engine(self, reason: str = "ui_stop"):
            return None

        def request_stop_flags(self, reason: str):
            return service.request_stop_flags(reason)

        def request_shutdown(self, reason: str, *, exit_process: bool = True):
            return service.request_shutdown(reason, exit_process=exit_process)

        def list_archives(self):
            return []

        def create_archive(self):
            return {"ok": True}

        def restore_archive(self, archive_id: str):
            return {"ok": True}

        def restore_archive_upload(self, path, filename: str):
            return {"ok": True}

        def clear_keep_opc_only(self, *, archive_first: bool = True):
            return {"ok": True}

        def list_reports(self, device, results_type=None, project=None, device_id=None):
            return list_reports_for_device(
                service.config.report_output,
                device,
                results_type=results_type,
                project=project,
                device_id=device_id,
            )

        def open_report(self, path: str):
            return 200, path

    facade = _TestFacade()
    service.app = facade
    return facade


def test_static_assets() -> int:
    required = ("index.html", "app.js", "style.css", "ui-paths.js")
    missing = [name for name in required if not (STATIC_DIR / name).is_file()]
    if missing:
        print(f"FAIL missing static files: {', '.join(missing)}")
        return 1
    img_dir = STATIC_DIR / "img"
    for logo in ("himalogo.png", "hart.jpg", "abb.png", "eh.png", "emerson.png", "samson.png", "wika.png", "hero-plant.jpg"):
        if not (img_dir / logo).is_file():
            print(f"FAIL missing branding image: {logo}")
            return 1
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    if "href=\"style.css" not in html or 'src="img/himalogo.png"' not in html:
        print("FAIL index.html must use relative asset paths (style.css, img/...)")
        return 1
    for marker in (
        "device-list",
        "report-list",
        "btn-refresh",
        "btn-start-service",
        "btn-stop-service",
        "btn-open",
        "modal",
        "health-grid",
        "alarm-list",
        "vendor-grid",
        "device-search",
        "report-search",
        "hero-banner",
        "scroll-panel",
        "(No device available)",
        "(No report available)",
    ):
        if marker not in html:
            print(f"FAIL index.html missing {marker!r}")
            return 1
    print("OK  static assets, branding images, and UI components")
    return 0


def test_api_routes() -> int:
    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        print(f"FAIL TestClient unavailable: {exc}")
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="gate11_api_"))
    output = tmp / "reports"
    mirror = tmp / "mirror"
    output.mkdir(parents=True)
    mirror.mkdir(parents=True)

    service = MagicMock()
    service._stopped = False
    service._starting = False
    service.engine_running = True
    service.config.web_auth_enabled = False
    service.config.web_auth_token = ""
    service.config.web_localhost_bypass = True
    service.config.web_port = 8080
    service.config.report_output = output
    service.config.report_mirror = mirror
    service.config.first_run_folder = tmp
    service.health.return_value = {
        "deployment_case": 1,
        "database": "sqlite",
        "opc_servers": [{"name": "Mock.OPC", "connected": True, "tags": 3}],
        "active_devices": 1,
        "opc_devices": 1,
        "queue_depth": 0,
        "silworx": {"session_id": "abc", "project_state": "open"},
        "silworx_api_instances": [],
        "service_state": {},
        "stopping": False,
        "engine_running": True,
        "web_host_alive": True,
    }
    service.db.list_active_devices.return_value = [
        {"device_tag": TEST_TAG, "results_type": RESULTS_TYPE, "is_active": 1, "present_on_opc": True}
    ]
    service.db.list_devices.return_value = [
        {"device_tag": TEST_TAG, "results_type": RESULTS_TYPE, "is_active": 1, "present_on_opc": True}
    ]
    service.db.list_running_tests.return_value = []
    service.db.list_test_history.return_value = []
    service.db.list_recent_alarms.return_value = [
        {
            "id": 1,
            "timestamp": "2026-06-18T12:00:00",
            "severity": "Error",
            "step": "P3",
            "device_tag": None,
            "message": "Test alarm",
            "solution_hint": "Check OPC.",
            "acknowledged": False,
            "error_key": "P3|Test alarm",
        }
    ]
    service.alarms.pop_pending_popups.return_value = []
    service.alarms.active_error_keys.return_value = {"P3|Test alarm"}
    service.db.acknowledge_alarm.return_value = {
        "id": 1,
        "error_key": "P3|Test alarm",
        "acknowledged": True,
    }
    service.refresh = MagicMock(return_value={})
    service.request_stop_flags = MagicMock()
    service.request_shutdown = MagicMock()
    service.start = MagicMock()
    _attach_application_facade(service)

    client = TestClient(create_app(service))
    page = client.get("/").text
    if "<base href=\"/static/\">" not in page:
        print("FAIL GET / must inject <base href=\"/static/\">")
        return 1
    if client.get("/static/style.css").status_code != 200:
        print("FAIL /static/style.css not served")
        return 1
    if client.get("/static/img/himalogo.png").status_code != 200:
        print("FAIL /static/img/himalogo.png not served")
        return 1
    if client.get("/").status_code != 200:
        print("FAIL GET /")
        return 1
    if "view-all-devices" not in page or "view-opc-devices" not in page:
        print("FAIL device list view options missing from GET /")
        return 1
    if "btn-archive-lists" not in page or "btn-keep-opc" not in page or "btn-browse-restore" not in page:
        print("FAIL archive / clear / browse-restore controls missing from GET /")
        return 1
    if "Keep OPC devices only" not in page:
        print("FAIL Clear device list hover notice missing from GET /")
        return 1
    if "Clear device list" not in page or "archive-status" not in page or "btn-reset-alarms" not in page:
        print("FAIL clear label / archive path / reset alarms missing from GET /")
        return 1
    if "btn-prooftest-history" not in page or "history-modal" not in page:
        print("FAIL Prooftest history button or popup missing from GET /")
        return 1
    js = client.get("/static/app.js").text
    if "ALL DEVICES" not in js or "OPC ACTIVE DEVICES" not in js or "Plugin session" not in js:
        print("FAIL health card labels missing from app.js")
        return 1
    health = client.get("/api/health").json()
    if "silworx" not in health or "opc_servers" not in health:
        print("FAIL /api/health missing silworx or opc_servers")
        return 1
    if len(client.get("/api/devices").json()) != 1:
        print("FAIL /api/devices")
        return 1
    if len(client.get("/api/devices?view=opc").json()) != 1:
        print("FAIL /api/devices?view=opc")
        return 1
    if not isinstance(client.get("/api/archives").json(), list):
        print("FAIL /api/archives")
        return 1
    alarms = client.get("/api/alarms").json()
    if not alarms.get("alarms"):
        print("FAIL /api/alarms")
        return 1
    if alarms["alarms"][0].get("active") is not True:
        print(f"FAIL /api/alarms active flag: {alarms['alarms'][0]}")
        return 1
    if not isinstance(client.get("/api/running-tests").json(), list):
        print("FAIL /api/running-tests")
        return 1
    refresh = client.post("/api/refresh").json()
    if refresh.get("status") != "refresh_started":
        print("FAIL /api/refresh")
        return 1
    from prooftest.web import app as app_mod

    with __import__("unittest.mock").mock.patch.object(app_mod, "_is_local_client", return_value=True):
        start = client.post("/api/start").json()
        stop = client.post("/api/stop?reason=ui_stop").json()
        shutdown = client.post("/api/shutdown?reason=test_exit").json()
        ack = client.post("/api/alarms/1/ack").json()
        reset = client.post("/api/alarms/reset").json()
        csv_bytes = b"Device_TAG,Results_Type\nGATE11-UI-DEVICE,X-HART_E+H_PMx7xB_Results\n"
        uploaded = client.post(
            "/api/archives/upload-restore",
            files={"file": ("devices.csv", csv_bytes, "text/csv")},
        )
    if start.get("status") != "already_running":
        print(f"FAIL /api/start expected already_running: {start}")
        return 1
    if stop.get("status") != "engine_stop_requested" or stop.get("web_host_alive") is not True:
        print(f"FAIL /api/stop: {stop}")
        return 1
    if shutdown.get("status") != "shutdown_started":
        print(f"FAIL /api/shutdown: {shutdown}")
        return 1
    if ack.get("acknowledged") is not True:
        print(f"FAIL /api/alarms/1/ack: {ack}")
        return 1
    if reset.get("reset") is not True:
        print(f"FAIL /api/alarms/reset: {reset}")
        return 1
    if uploaded.status_code >= 400:
        print(f"FAIL /api/archives/upload-restore: {uploaded.status_code} {uploaded.text}")
        return 1
    print(f"OK  API routes (app version {APP_VERSION})")
    return 0


def test_reports_results_type() -> int:
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="gate11_reports_"))
    output = tmp / "reports"
    mirror = tmp / "mirror"
    config = AppConfig.load(CONFIG_INI)
    config.report_output = output
    config.report_mirror = mirror

    write_reports(
        config,
        TEST_TAG,
        RESULTS_TYPE,
        {"Error": False, "Device_tag": TEST_TAG},
    )
    report_dir = device_report_dir(output, TEST_TAG, RESULTS_TYPE)
    if not any(report_dir.glob(f"{TEST_TAG}*")):
        print("FAIL report file not created for results_type lookup")
        return 1

    service = MagicMock()
    service.config.web_auth_enabled = False
    service.config.web_auth_token = ""
    service.config.web_localhost_bypass = True
    service.config.report_output = output
    service.config.report_mirror = mirror
    service.db.list_recent_alarms.return_value = []
    service.alarms.pop_pending_popups.return_value = []
    _attach_application_facade(service)

    client = TestClient(create_app(service))
    scoped = client.get(
        "/api/reports",
        params={"device": TEST_TAG, "results_type": RESULTS_TYPE},
    ).json()
    if not scoped:
        print("FAIL scoped /api/reports returned no files")
        return 1
    print("OK  /api/reports?results_type= scoped lookup")
    return 0


def test_alarm_persistence() -> int:
    config = AppConfig.load(CONFIG_INI)
    db_path = Path(tempfile.mkdtemp(prefix="gate11_db_")) / "gate11_alarms.db"
    config.sqlite_path = db_path
    alarms = AlarmManager()
    db = Database(config, alarms)
    db.connect()
    alarms.set_persist_callback(
        lambda record: db.log_alarm(
            record.step,
            record.severity,
            record.message,
            record.solution_hint,
            record.device_tag,
        )
    )
    alarms.raise_alarm("P3", "Gate 11 alarm persistence test", device_tag=TEST_TAG)
    rows = db.list_recent_alarms(limit=5)
    if not rows or rows[0]["step"] != "P3":
        print("FAIL AlarmLog row missing after raise_alarm")
        return 1
    if rows[0]["device_tag"] != TEST_TAG:
        print("FAIL AlarmLog device_tag not persisted")
        return 1
    if not rows[0].get("id") or rows[0].get("acknowledged"):
        print("FAIL AlarmLog id/acknowledged missing or already acknowledged")
        return 1
    acked = db.acknowledge_alarm(rows[0]["id"])
    if not acked or not acked.get("acknowledged"):
        print("FAIL acknowledge_alarm did not mark the row")
        return 1
    db.reset_alarms()
    print("OK  raise_alarm persists to AlarmLog")
    return 0


def main() -> int:
    tests = (
        test_static_assets,
        test_api_routes,
        test_reports_results_type,
        test_alarm_persistence,
    )
    failed = 0
    for test in tests:
        failed += test()
    if failed:
        print(f"\nGate 11: {failed} check(s) failed")
        return 1
    print("\nGate 11: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
