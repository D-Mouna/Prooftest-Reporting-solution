from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Dict, Optional, Tuple

from prooftest.alarms import AlarmManager, AlarmRecord
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.step01_setup import ensure_first_run, sync_results_type_folders_from_catalogue
from prooftest.step04_opc import OpcManager
from prooftest.step05_detection import ProoftestMonitor
from prooftest.results_csv import ResultsStructure, load_all_structures
from prooftest.annex_pdf_generation import ensure_report_templates_for_structures
from prooftest.step07_triggers import (
    Case1SyncTriggers,
    run_background_sync_iteration,
    silworx_session_to_state,
)

log = logging.getLogger(__name__)

_PROCESS_EXIT_REASONS = frozenset(
    {
        "silworx_uninstall",  # explicit operator script asking for process exit
        "api_shutdown",
        "uvicorn_shutdown",
        "stop_service",
    }
)


class ProoftestService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.alarms = AlarmManager()
        self.db = Database(config, self.alarms)
        self.opc = OpcManager(config.opc_server_filter)
        self.structures: Dict[str, ResultsStructure] = {}
        self.monitor: Optional[ProoftestMonitor] = None
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._last_device_sync = 0.0
        self._last_template_sync = 0.0
        self._last_case1_sync_check = 0.0
        self._silworx_uninstall_released = False
        self._silworx_integration_released = False
        self._opc_servers: list[str] = []
        self._case1_sync = Case1SyncTriggers(
            config,
            config.sqlite_path.parent / "sync_markers",
        )
        self._engine_lock = threading.Lock()
        self._stopped = False
        self._starting = False
        self._stop_in_progress = False
        self._start_token = 0
        self._loop_generation = 0
        self._on_shutdown: Optional[Callable[[str], None]] = None
        self._cached_device_counts: Tuple[int, int] = (0, 0)
        self._cached_opc_device_counts: Dict[str, int] = {}
        self._cached_service_state: Dict[str, str] = {}
        self._health_cache: Dict[str, object] = {}
        self._health_cache_at: float = 0.0
        self._health_cache_ttl_sec: float = 2.0
        self._health_lock = threading.Lock()
        self.app = None
        self._build_application()

    def _build_application(self) -> None:
        """Wire Presentation → Application (Engine / Catalog / Query / SILworX)."""
        from layers.application.facade import ApplicationFacade

        self.app = ApplicationFacade(self)

    def set_shutdown_callback(self, callback: Callable[[str], None]) -> None:
        self._on_shutdown = callback

    @property
    def engine_running(self) -> bool:
        return not self._stopped and not self._starting

    def _start_aborted(self, token: int) -> bool:
        # Token only: `_stop` stays set until an in-flight Stop finishes, so
        # treating it as abort would cancel every Start-after-Stop.
        return token != self._start_token

    def _publish_silworx_state(self) -> None:
        from prooftest.step07_triggers import silworx_open_projects_state

        self._case1_sync.refresh_open_sessions()
        for key, value in silworx_session_to_state(self._case1_sync.active_session).items():
            self.db.set_service_state(key, value)
        for key, value in silworx_open_projects_state(self._case1_sync.open_sessions).items():
            self.db.set_service_state(key, value)
        attached = self._case1_sync._attached_project_names_by_api or {}
        if attached:
            self.db.set_service_state(
                "silworx_attached_projects",
                ";".join(
                    f"{port}:{name}" for port, name in sorted(attached.items()) if name
                ),
            )

    def start(self) -> None:
        """Start or restart the Prooftest engine (OPC/API/poll). Web host stays up."""
        with self._engine_lock:
            if self._starting:
                log.info("Prooftest engine start already in progress")
                return
            if (
                not self._stopped
                and not self._stop_in_progress
                and any(t.is_alive() for t in self._threads)
            ):
                log.info("Prooftest engine already running")
                return
            self._start_token += 1
            token = self._start_token
            self._starting = True
            self._stopped = False
            # Leave _stop_in_progress / _stop for the in-flight Stop to finish.

        if not self._wait_for_stop_before_start(token):
            return

        with self._engine_lock:
            if self._start_aborted(token):
                if token == self._start_token:
                    self._starting = False
                    self._stopped = True
                log.info("Prooftest engine start aborted by Stop")
                return
            self._stop.clear()

        start_timeout_sec = 120.0
        watchdog = threading.Timer(
            start_timeout_sec,
            lambda: self._start_watchdog_fire(token, start_timeout_sec),
        )
        watchdog.daemon = True
        watchdog.start()
        try:
            completed = self._start_engine_body(token)
        except Exception:
            log.exception("Prooftest engine start failed")
            with self._engine_lock:
                if token == self._start_token:
                    self._starting = False
                    self._stopped = True
                    self._stop.set()
            raise
        finally:
            watchdog.cancel()
        with self._engine_lock:
            if token != self._start_token:
                # A newer Start/Stop owns the flag — do not clear _starting for them.
                log.info("Prooftest engine start aborted by Stop (token superseded)")
                return
            self._starting = False
            if not completed:
                self._stopped = True
                log.info("Prooftest engine start aborted by Stop")
                return
        log.info("Prooftest engine started")

    def _start_watchdog_fire(self, token: int, timeout_sec: float) -> None:
        with self._engine_lock:
            if token != self._start_token or not self._starting:
                return
            self._starting = False
            self._stopped = True
            self._stop.set()
        log.error(
            "Engine start watchdog: still starting after %.0fs (token=%s) — clearing stuck flag",
            timeout_sec,
            token,
        )

    def _wait_for_stop_before_start(self, token: int, timeout_sec: float = 45.0) -> bool:
        """Do not run a new engine body until graceful shutdown has released OPC/DB."""
        waited = 0.0
        if self._stop_in_progress:
            log.info("Engine start waiting for in-flight Stop to finish")
        while self._stop_in_progress and waited < timeout_sec:
            if self._start_aborted(token):
                with self._engine_lock:
                    if token == self._start_token:
                        self._starting = False
                        self._stopped = True
                log.info("Prooftest engine start aborted while waiting for Stop")
                return False
            time.sleep(0.25)
            waited += 0.25
        if self._stop_in_progress:
            with self._engine_lock:
                if token == self._start_token:
                    self._starting = False
                    self._stopped = True
            log.warning("Start refused — Stop still in progress after %.0fs", waited)
            return False
        leftover = [t for t in self._threads if t.is_alive()]
        if leftover:
            log.warning(
                "Previous engine threads still alive after Stop: %s — waiting",
                ", ".join(t.name for t in leftover),
            )
            for thread in leftover:
                thread.join(timeout=15.0)
        return True

    def _start_engine_body(self, token: int) -> bool:
        """Heavy start work. Returns False if Stop cancelled this start."""
        def _stage(msg: str) -> None:
            log.info("Engine start [%s]: %s", token, msg)

        if self._start_aborted(token):
            return False
        _stage("ensure_data_dirs")
        self.config.ensure_data_dirs()
        _stage("ensure_first_run")
        ensure_first_run(self.config, self.alarms)
        if self._start_aborted(token):
            return False
        _stage("connecting database")
        self.db.connect()
        self.alarms.set_persist_callback(self._persist_alarm)
        _stage("loading Results Structures")
        self.structures = load_all_structures(self.config.results_structures)
        _stage(f"structures loaded ({len(self.structures)})")
        self._build_application()
        sync_results_type_folders_from_catalogue(
            self.config, self.alarms, list(self.structures.keys())
        )
        try:
            ensure_report_templates_for_structures(
                self.config.report_html_templates,
                self.structures,
            )
        except Exception as exc:
            log.warning("Report template ensure failed: %s", exc)
        # G-05 / Step 1.3: create DB under station Database folder and all
        # ProofTest_* tables from Results Structure CSVs (baseline nine + any new types).
        try:
            _stage("sync_schema_case2")
            self.db.sync_schema_case2(self.config.sql_templates, self.structures)
            _stage("sync_schema_case2 done")
        except Exception as exc:
            log.exception("Initial SQL schema sync failed: %s", exc)
            self.alarms.raise_alarm(
                "S2",
                "Cannot create HIMA Automated Prooftest database tables",
                cause=str(exc),
                severity="Error",
                show_popup=True,
            )
        if self._start_aborted(token):
            return False
        if self.monitor is not None:
            try:
                self.monitor.shutdown()
            except Exception:
                pass
        _stage("create ProoftestMonitor")
        self.monitor = ProoftestMonitor(
            self.config,
            self.db,
            self.opc,
            self.structures,
            live_service=getattr(self.app, "live", None) if self.app else None,
        )
        if self._start_aborted(token):
            return False
        # Always start plugin monitor when possible — no-ops harmlessly if SILworX absent.
        # Skip when operator released SILworX for uninstall (until Re-integrate).
        _stage("starting plugin monitor")
        if self.is_silworx_integration_released():
            log.info("SILworX integration released — skipping plugin monitor on engine start")
            try:
                self._case1_sync._silworx_api_suspended = True
            except Exception:
                pass
        else:
            self._case1_sync.prepare_for_engine_start()
            self._case1_sync.start_monitor()
        if self._start_aborted(token):
            try:
                self._case1_sync.shutdown()
            except Exception:
                pass
            return False
        self._loop_generation += 1
        generation = self._loop_generation
        self._threads = [
            threading.Thread(
                target=self._poll_loop, args=(generation,), name="poll-loop", daemon=True
            ),
            threading.Thread(
                target=self._background_sync_loop,
                args=(generation,),
                name="sync-loop",
                daemon=True,
            ),
        ]
        for t in self._threads:
            t.start()
        try:
            self.db.set_service_state("engine", "starting")
        except Exception:
            pass
        if self._start_aborted(token):
            return False
        # Become "running" before the first OPC/API refresh so Stop→Start cannot
        # leave the UI stuck on "starting" while COM browse runs.
        try:
            self._case1_sync.commit()
        except Exception as exc:
            log.warning("Engine start marker commit failed: %s", exc)
        try:
            self.db.set_service_state("started_at", time.strftime("%Y-%m-%d %H:%M:%S"))
            self.db.set_service_state("engine", "running")
            self.db.set_service_state("stop_reason", "")
        except Exception:
            pass
        _stage("loops up — scheduling initial device-list refresh")
        threading.Thread(
            target=self._initial_refresh_async,
            args=(token,),
            name="initial-refresh",
            daemon=True,
        ).start()
        return not self._start_aborted(token)

    def _initial_refresh_async(self, token: int) -> None:
        if self._start_aborted(token):
            return
        try:
            # First catalog build — keep live OPC clients; no full invalidate.
            self.refresh(manual=False)
            log.info("Initial device-list refresh finished")
        except Exception:
            log.exception("Initial device-list refresh failed")

    def _persist_alarm(self, record: AlarmRecord) -> None:
        self.db.log_alarm(
            record.step,
            record.severity,
            record.message,
            record.solution_hint,
            record.device_tag,
        )

    @staticmethod
    def _should_exit_process(reason: str, exit_process: Optional[bool]) -> bool:
        if exit_process is not None:
            return bool(exit_process)
        if reason in _PROCESS_EXIT_REASONS:
            return True
        if reason.startswith("signal_"):
            return True
        return False

    def is_silworx_integration_released(self) -> bool:
        """True when operator released SILworX for uninstall (until Re-integrate)."""
        if getattr(self, "_silworx_integration_released", False):
            return True
        try:
            state = self.db.get_service_state() or {}
            mode = str(state.get("silworx_integration") or "").strip().lower()
            if mode == "released":
                self._silworx_integration_released = True
                return True
            # Legacy uninstall marker from G-11 auto-release.
            if str(state.get("silworx_mode") or "") == "opc_after_uninstall" and mode != "integrated":
                # Only treat as released if explicit integration key says so, or
                # operator flag was set this process.
                pass
        except Exception:
            pass
        return False

    def release_silworx_for_uninstall(self) -> Dict[str, object]:
        """
        Operator Release SILworX — drop API/plugin/c3 locks so SILworX can be uninstalled.

        Report tool keeps running on OPC-only until Re-integrate SILworX.
        """
        log.warning("Operator Release SILworX — dropping API/plugin/c3 for uninstall")
        self._silworx_integration_released = True
        self._silworx_uninstall_released = True
        try:
            self._case1_sync.detach_tool_clients()
        except Exception as exc:
            log.warning("Detach during Release SILworX failed: %s", exc)
        try:
            self._case1_sync.shutdown()
        except Exception as exc:
            log.warning("SILworX shutdown during Release failed: %s", exc)
        killed = 0
        try:
            from prooftest.annex_silworx_cleanup import kill_leftover_c3_after_close, list_c3_processes

            if list_c3_processes():
                cleanup = kill_leftover_c3_after_close(self.config, force=True)
                killed = len(getattr(cleanup, "killed", []) or [])
        except Exception as exc:
            log.warning("c3.exe cleanup during Release SILworX failed: %s", exc)
        try:
            self.db.set_service_state("silworx_integration", "released")
            self.db.set_service_state("silworx_mode", "opc_after_uninstall")
            self.db.set_service_state("device_list_source", "opc_fallback")
            self.db.set_service_state("silworx_api_connected", "0")
            self.db.set_service_state("silworx_cleanup_killed", str(killed))
            self.db.set_service_state(
                "silworx_released_at",
                time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            pass
        try:
            self.alarms.raise_alarm(
                "G-11",
                "SILworX released for uninstall — tool continues on OPC only",
                cause="API/plugin detached; leftover c3.exe cleared when present",
                severity="Warning",
                show_popup=False,
            )
        except Exception:
            pass
        try:
            self.refresh(manual=True)
        except Exception as exc:
            log.warning("OPC refresh after Release SILworX failed: %s", exc)
        return {
            "status": "released",
            "silworx_integration": "released",
            "c3_killed": killed,
            "engine_running": bool(self.engine_running),
        }

    def reintegrate_silworx(self) -> Dict[str, object]:
        """Operator Re-integrate SILworX after reinstall — allow API/plugin again."""
        log.info("Operator Re-integrate SILworX — restoring API/plugin integration")
        self._silworx_integration_released = False
        self._silworx_uninstall_released = False
        try:
            self.db.set_service_state("silworx_integration", "integrated")
            self.db.set_service_state("silworx_mode", "")
            self.db.set_service_state(
                "silworx_reintegrated_at",
                time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            pass
        try:
            self._case1_sync.prepare_for_engine_start()
            if self.engine_running:
                self._case1_sync.start_monitor()
        except Exception as exc:
            log.warning("Re-integrate SILworX monitor start failed: %s", exc)
            return {
                "status": "reintegrate_partial",
                "silworx_integration": "integrated",
                "error": str(exc),
                "engine_running": bool(self.engine_running),
            }
        # Attach if a project is already open (same as Connect).
        result: Dict[str, object] = {
            "status": "integrated",
            "silworx_integration": "integrated",
            "engine_running": bool(self.engine_running),
        }
        if self.engine_running and self.app is not None:
            try:
                attach = self.app.resume_silworx_connection()
                result.update(attach)
                result["status"] = "integrated"
                result["silworx_integration"] = "integrated"
            except Exception as exc:
                log.warning("Re-integrate attach attempt: %s", exc)
                result["attach_error"] = str(exc)
        return result

    def release_silworx_engines_keep_running(self) -> None:
        """
        G-11 — SILworX removed / uninstall in progress:

        - Release SILworX API + plugin monitors (resources that block uninstall)
        - Kill leftover ``c3.exe`` engines that hold SILworX install locks
        - Keep this Report Solution process running
        - Continue device-list updates via OPC scan (same unified path as when API is down)
        """
        # Same durable release state as the operator button.
        self.release_silworx_for_uninstall()

    # Backward-compatible name used by older call sites / docs.
    switch_to_opc_after_silworx_uninstall = release_silworx_engines_keep_running

    def request_shutdown(self, reason: str, *, exit_process: Optional[bool] = None) -> None:
        do_exit = self._should_exit_process(reason, exit_process)
        if do_exit and self._on_shutdown:
            self._on_shutdown(reason)
        self.stop(reason)

    def request_stop_flags(self, reason: str = "") -> None:
        """
        Mark the engine stopped immediately (HTTP-safe).

        Invalidates any in-flight Start so it cannot recreate plugin/OPC after Stop.
        """
        with self._engine_lock:
            self._start_token += 1
            self._loop_generation += 1
            self._starting = False
            self._stopped = True
            self._stop_in_progress = True
            self._stop.set()
        log.info("Engine stop requested (%s) — in-flight Start invalidated", reason or "no reason")

    def stop(self, reason: str = "") -> None:
        """Stop OPC/API/plugin/workers; keep the web host process alive unless exit was requested."""
        with self._engine_lock:
            already_stopped = self._stopped and not self._starting and self._stop.is_set()
            self._start_token += 1
            self._loop_generation += 1
            self._starting = False
            self._stopped = True
            self._stop_in_progress = True
            self._stop.set()
        if already_stopped and not any(t.is_alive() for t in self._threads):
            log.info("Prooftest engine already stopped (%s)", reason or "no reason")
            return
        from prooftest.annex_stop_service import perform_graceful_shutdown

        perform_graceful_shutdown(self, reason)

    def refresh(self, manual: bool = False) -> Dict[str, object]:
        """WorkerHost entry — delegates RefreshCatalog to Application CatalogService."""
        if self.app is not None:
            return self.app.catalog.run_station_refresh(self, manual=manual)
        return {}

    def _poll_loop(self, generation: int) -> None:
        while not self._stop.is_set() and generation == self._loop_generation:
            if self._starting:
                self._stop.wait(0.5)
                continue
            try:
                if self.monitor:
                    self.monitor.poll_devices()
                self.db.set_service_state("last_poll", time.strftime("%Y-%m-%d %H:%M:%S"))
                self._sync_health_caches_from_db()
            except Exception as exc:
                log.exception("Poll loop error: %s", exc)
            self._stop.wait(self.config.poll_interval_sec)

    def _background_sync_loop(self, generation: int) -> None:
        while not self._stop.is_set() and generation == self._loop_generation:
            if self._starting:
                self._stop.wait(0.5)
                continue
            now = time.time()
            try:
                run_background_sync_iteration(self, now)
            except Exception as exc:
                log.warning("Background sync error: %s", exc)
            self._stop.wait(0.5)

    def list_devices(self, view: str = "all") -> list:
        if self._stopped and not self._starting:
            return []
        if self.app is not None:
            try:
                return self.app.query.list_devices(view)
            except Exception as exc:
                log.exception("ListDevices failed: %s", exc)
                return []
        try:
            from layers.domain.device import sort_device_dicts

            return sort_device_dicts(self.db.list_devices(view))
        except Exception as exc:
            log.exception("ListDevices failed: %s", exc)
            return []

    def list_reports(
        self,
        device: str,
        results_type: Optional[str] = None,
        project: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> list:
        if self.app is not None:
            return self.app.list_reports(
                device, results_type, project=project, device_id=device_id
            )
        from prooftest.annex_pdf_generation import list_reports_for_device

        return list_reports_for_device(
            self.config.report_output,
            device,
            results_type=results_type,
            project=project,
            device_id=device_id,
        )

    def close_silworx_connection(self) -> Dict[str, object]:
        """Drop this tool's API/plugin session only. Engine and OPC keep running."""
        if self.app is not None:
            return self.app.close_silworx_connection()
        already = self._case1_sync.is_api_suspended() and not self._case1_sync.is_tool_attached()
        if already:
            return {
                "silworx": "not connected",
                "status": "already_disconnected",
                "engine_running": self.engine_running,
            }
        try:
            self._case1_sync.detach_tool_clients()
        except Exception as exc:
            self.alarms.raise_alarm(
                "S7",
                "Plugin/API detach failed",
                cause=str(exc),
                action="CloseSilworXconnection",
            )
            try:
                self._case1_sync.detach_tool_clients()
            except Exception:
                pass
        try:
            self.db.set_service_state("silworx_api_connected", "0")
            self.db.set_service_state("device_list_source", "opc_fallback")
        except Exception:
            pass
        try:
            self.refresh(manual=True)
        except Exception as exc:
            self.alarms.raise_alarm("S7", str(exc), action="CloseSilworXconnection")
        return {
            "silworx": "not connected",
            "status": "disconnected",
            "engine_running": self.engine_running,
        }

    def resume_silworx_connection(self) -> Dict[str, object]:
        """Attach to an already-open SILworX project. Never opens or kills SILworX."""
        if self.app is not None:
            return self.app.resume_silworx_connection()
        try:
            self._case1_sync.resume_tool_clients()
        except Exception as exc:
            self.alarms.raise_alarm("S7", str(exc), action="ResumeSilworXconnection")
            return {
                "silworx": "not connected",
                "status": "auth_or_cert_error",
                "engine_running": self.engine_running,
            }
        try:
            self.refresh(manual=True)
        except Exception as exc:
            self.alarms.raise_alarm("S7", str(exc), action="ResumeSilworXconnection")
        attached = self._case1_sync.is_tool_attached()
        if not attached:
            self.alarms.raise_alarm(
                "S7",
                "no open project",
                action="ResumeSilworXconnection",
                severity="Warning",
            )
            return {
                "silworx": "not connected",
                "status": "no_open_project",
                "engine_running": self.engine_running,
            }
        return {
            "silworx": "running",
            "status": "attached",
            "engine_running": self.engine_running,
        }

    def _silworx_badge(self) -> str:
        return "running" if self._case1_sync.is_tool_attached() else "not connected"

    def _device_counts(self) -> Tuple[int, int]:
        try:
            return self.db.count_listed_devices(), self.db.count_opc_devices()
        except Exception:
            return 0, 0

    def _opc_device_counts_by_server(self) -> Dict[str, int]:
        """Active catalog devices grouped by OPC ProgID (for health UI)."""
        counts: Dict[str, int] = {}
        try:
            for row in self.db.list_active_devices() or []:
                srv = str((row or {}).get("opc_server") or "").strip()
                if not srv:
                    continue
                counts[srv] = counts.get(srv, 0) + 1
        except Exception:
            return {}
        return counts

    def _sync_health_caches_from_db(self) -> None:
        """Keep UI health fresh even when catalog refresh is slow/stuck."""
        try:
            self._cached_device_counts = self._device_counts()
        except Exception:
            pass
        try:
            self._cached_opc_device_counts = self._opc_device_counts_by_server()
        except Exception:
            pass
        try:
            state = self.db.get_service_state() or {}
            if state:
                self._cached_service_state = dict(state)
        except Exception:
            pass

    def _health_stub_from_caches(self) -> Dict[str, object]:
        """Fast payload when the health lock is busy — never return empty zeros if DB has data."""
        self._sync_health_caches_from_db()
        all_count, opc_count = self._cached_device_counts
        service_state = dict(self._cached_service_state)
        db_label = "sqlite" if self.db.using_sqlite else "sqlserver"
        opc_names = list(self._opc_servers or [])
        if not opc_names:
            raw = str(service_state.get("opc_server_list") or "")
            opc_names = [p for p in raw.split(";") if p]
        payload = {
            "deployment_case": self.config.deployment_case,
            "device_list_source": service_state.get("device_list_source", ""),
            "database": db_label,
            "opc_servers": [
                {
                    "name": name,
                    "connected": True,
                    "devices": int((getattr(self, "_cached_opc_device_counts", {}) or {}).get(name, 0)),
                    "tags": 0,
                    "browse_ok": True,
                }
                for name in opc_names
            ],
            "active_devices": all_count,
            "opc_devices": opc_count,
            "queue_depth": self.monitor.queue_depth if self.monitor else 0,
            "silworx": {
                k: service_state.get(k, "")
                for k in (
                    "silworx_open",
                    "silworx_project_name",
                    "silworx_project_file",
                    "project_state",
                    "project_name",
                    "session_id",
                )
                if service_state.get(k)
            },
            "api_session": {
                "project_name": service_state.get("project_name")
                or service_state.get("silworx_project_name")
                or ""
            },
            "plugin_session": {
                "name": "",
                "registered": str(service_state.get("silworx_api_connected") or "") == "1",
            },
            "silworx_api_instances": [],
            "service_state": service_state,
            "stopping": bool(getattr(self, "_stop_in_progress", False)),
            "starting": bool(self._starting),
            "engine_running": bool(self.engine_running),
            "web_host_alive": True,
            "web_auth_required": self.config.web_auth_enabled,
        }
        engine = "starting" if self._starting else ("stopped" if self._stopped else "running")
        return self._decorate_health(payload, engine)

    def _decorate_health(self, payload: Dict[str, object], engine: str) -> Dict[str, object]:
        payload["engine"] = engine
        servers = payload.get("opc_servers") or []
        payload["opc_count"] = len(servers) if isinstance(servers, list) else int(len(self._opc_servers))
        if not payload["opc_count"] and self._opc_servers:
            payload["opc_count"] = len(self._opc_servers)
        payload["device_count"] = int(payload.get("active_devices") or 0)
        payload["silworx_status"] = self._silworx_badge() if engine != "stopped" else "not connected"
        payload["silworx_integration"] = (
            "released" if self.is_silworx_integration_released() else "integrated"
        )
        payload["web_auth_required"] = bool(self.config.web_auth_enabled)
        payload["auth_bind_warning"] = bool(getattr(self.config, "auth_bind_warning", False))
        payload["web_host"] = str(self.config.web_host)
        try:
            payload["last_error"] = self.alarms.last_error()
        except Exception:
            payload["last_error"] = None
        return payload

    def health(self) -> Dict[str, object]:
        now = time.monotonic()
        if self._health_cache and now - self._health_cache_at <= self._health_cache_ttl_sec:
            return dict(self._health_cache)

        # Single-flight guard: avoid piling up slow work across request threads.
        if not self._health_lock.acquire(blocking=False):
            if self._health_cache:
                return dict(self._health_cache)
            return self._health_stub_from_caches()
        try:
            # Prefer DB-backed counts so UI stays correct while refresh/browse runs.
            if (
                not self._cached_service_state
                or self._cached_device_counts == (0, 0)
            ):
                self._sync_health_caches_from_db()
            all_count, opc_count = self._cached_device_counts
            service_state = dict(self._cached_service_state)
            db_label = "sqlite" if self.db.using_sqlite else "sqlserver"
            if self._stopped and not self._starting:
                payload = {
                    "deployment_case": self.config.deployment_case,
                    "device_list_source": service_state.get("device_list_source", ""),
                    "database": db_label,
                    "opc_servers": [],
                    "active_devices": all_count,
                    "opc_devices": opc_count,
                    "queue_depth": 0,
                    "silworx": {},
                    "api_session": {"project_name": ""},
                    "plugin_session": {"name": "", "registered": False},
                    "silworx_api_instances": [],
                    "service_state": service_state or {"engine": "stopped"},
                    "stopping": bool(getattr(self, "_stop_in_progress", False)),
                    "starting": False,
                    "engine_running": False,
                    "web_host_alive": True,
                    "web_auth_required": self.config.web_auth_enabled,
                }
                payload = self._decorate_health(payload, "stopped")
                self._health_cache = dict(payload)
                self._health_cache_at = time.monotonic()
                return payload
            if self._starting:
                payload = {
                    "deployment_case": self.config.deployment_case,
                    "device_list_source": service_state.get("device_list_source", ""),
                    "database": db_label,
                    "opc_servers": [],
                    "active_devices": all_count,
                    "opc_devices": opc_count,
                    "queue_depth": 0,
                    "silworx": {},
                    "api_session": {"project_name": ""},
                    "plugin_session": {"name": "", "registered": False},
                    "silworx_api_instances": [],
                    "service_state": service_state or {"engine": "starting"},
                    "stopping": False,
                    "starting": True,
                    "engine_running": False,
                    "web_host_alive": True,
                    "web_auth_required": self.config.web_auth_enabled,
                }
                payload = self._decorate_health(payload, "starting")
                self._health_cache = dict(payload)
                self._health_cache_at = time.monotonic()
                return payload
            servers = []
            try:
                servers = self.opc.health_snapshot()
            except Exception:
                pass
            if not servers and self._opc_servers:
                servers = [
                    type("S", (), {"prog_id": n, "connected": True, "tag_count": 0})()
                    for n in self._opc_servers
                ]
            silworx = silworx_session_to_state(self._case1_sync.active_session)
            try:
                self._case1_sync.refresh_open_sessions()
            except Exception:
                pass
            open_projects = [
                {
                    "session_id": s.session_id,
                    "project_name": s.project_name,
                    "project_file": s.project_file,
                    "src_path": str(s.src_path),
                }
                for s in (self._case1_sync.open_sessions or [])
            ]
            device_list_source = service_state.get("device_list_source", "")
            api_project = self._case1_sync.api_connected_project_name(device_list_source)
            plugin_name = self._case1_sync.registered_plugin_session_name()
            api_instances = [
                {"api_port": inst.api_port, "plugin_port": inst.plugin_port, "label": inst.label}
                for inst in self._case1_sync._available_instances
            ]
            attached_map = {
                str(port): name
                for port, name in (self._case1_sync._attached_project_names_by_api or {}).items()
                if name
            }
            device_by_server = dict(getattr(self, "_cached_opc_device_counts", {}) or {})
            try:
                # Prefer a fresh count so health matches the catalog after refresh.
                device_by_server = self._opc_device_counts_by_server() or device_by_server
                self._cached_opc_device_counts = dict(device_by_server)
            except Exception:
                pass
            payload = {
                "deployment_case": self.config.deployment_case,
                "device_list_source": device_list_source,
                "database": db_label,
                "opc_servers": [
                    {
                        "name": s.prog_id,
                        "connected": s.connected,
                        "devices": int(device_by_server.get(s.prog_id, 0)),
                        "tags": s.tag_count,
                        "browse_ok": bool(getattr(s, "browse_ok", True)),
                        "live_ok": getattr(s, "live_ok", None),
                        "live_quality": getattr(s, "live_quality", "") or "",
                    }
                    for s in servers
                ],
                "active_devices": all_count,
                "opc_devices": opc_count,
                "queue_depth": self.monitor.queue_depth if self.monitor else 0,
                "silworx": silworx,
                "open_projects": open_projects,
                "attached_projects": attached_map,
                "api_session": {"project_name": api_project},
                "plugin_session": {"name": plugin_name, "registered": bool(plugin_name)},
                "silworx_api_instances": api_instances,
                "service_state": service_state,
                "stopping": False,
                "starting": False,
                "engine_running": True,
                "web_host_alive": True,
                "web_auth_required": self.config.web_auth_enabled,
            }
            payload = self._decorate_health(payload, "running")
            payload["silworx_integration"] = (
                "released" if self.is_silworx_integration_released() else "integrated"
            )
            self._health_cache = dict(payload)
            self._health_cache_at = time.monotonic()
            return payload
        except Exception as exc:
            log.exception("GetEngineStatus error: %s", exc)
            try:
                return self._health_stub_from_caches()
            except Exception:
                return self._decorate_health(
                    {
                        "engine": "running" if self.engine_running else "stopped",
                        "opc_servers": [],
                        "active_devices": 0,
                        "opc_devices": 0,
                        "queue_depth": 0,
                        "silworx": {},
                        "engine_running": bool(self.engine_running),
                        "web_host_alive": True,
                    },
                    "running" if self.engine_running else "stopped",
                )
        finally:
            self._health_lock.release()
