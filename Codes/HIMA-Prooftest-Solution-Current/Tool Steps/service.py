from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Dict, Optional, Tuple

from prooftest.alarms import AlarmManager, AlarmRecord
from prooftest.config import AppConfig
from prooftest.annex_database import Database
from prooftest.step01_setup import ensure_first_run, sync_results_type_folders_from_catalogue
from prooftest.step03_device_list import (
    sync_device_list_case1_via_api,
    sync_device_list_from_opc,
)
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
        self.opc = OpcManager(
            config.opc_server_filter,
            config.opc_default_branch,
            config.opc_prooftest_branches,
        )
        self.structures: Dict[str, ResultsStructure] = {}
        self.monitor: Optional[ProoftestMonitor] = None
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._last_device_sync = 0.0
        self._last_template_sync = 0.0
        self._last_case1_sync_check = 0.0
        self._silworx_uninstall_released = False
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
        self._cached_service_state: Dict[str, str] = {}
        self._health_cache: Dict[str, object] = {}
        self._health_cache_at: float = 0.0
        self._health_cache_ttl_sec: float = 2.0
        self._health_lock = threading.Lock()

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
        for key, value in silworx_session_to_state(self._case1_sync.active_session).items():
            self.db.set_service_state(key, value)

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
        with self._engine_lock:
            if token != self._start_token:
                log.info("Prooftest engine start aborted by Stop (token superseded)")
                return
            self._starting = False
            if not completed:
                self._stopped = True
                log.info("Prooftest engine start aborted by Stop")
                return
        log.info("Prooftest engine started")

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
        if self._start_aborted(token):
            return False
        self.config.ensure_data_dirs()
        ensure_first_run(self.config, self.alarms)
        if self._start_aborted(token):
            return False
        log.info("Engine start: connecting database")
        self.db.connect()
        self.alarms.set_persist_callback(self._persist_alarm)
        log.info("Engine start: loading Results Structures")
        self.structures = load_all_structures(self.config.results_structures)
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
            self.db.sync_schema_case2(self.config.sql_templates, self.structures)
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
        self.monitor = ProoftestMonitor(self.config, self.db, self.opc, self.structures)
        if self._start_aborted(token):
            return False
        # Always start plugin monitor when possible — no-ops harmlessly if SILworX absent.
        log.info("Engine start: starting plugin monitor")
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
        log.info("Prooftest engine loops started — refreshing device list in background")
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
            self.refresh(manual=True)
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

    def release_silworx_engines_keep_running(self) -> None:
        """
        G-11 — SILworX removed / uninstall in progress:

        - Release SILworX API + plugin monitors (resources that block uninstall)
        - Kill leftover ``c3.exe`` engines that hold SILworX install locks
        - Keep this Report Solution process running
        - Continue device-list updates via OPC scan (same unified path as when API is down)
        """
        log.warning(
            "SILworX no longer installed — releasing SILworX engines; "
            "Report Solution stays running and uses OPC for device list (G-11)"
        )

        try:
            self._case1_sync.shutdown()
        except Exception as exc:
            log.warning("SILworX API/plugin release during uninstall failed: %s", exc)

        try:
            from prooftest.annex_silworx_cleanup import kill_leftover_c3_after_close, list_c3_processes

            if list_c3_processes():
                cleanup = kill_leftover_c3_after_close(self.config, force=True)
                try:
                    self.db.set_service_state(
                        "silworx_cleanup_killed",
                        str(len(cleanup.killed)),
                    )
                except Exception:
                    pass
        except Exception as exc:
            log.warning("c3.exe cleanup during uninstall failed: %s", exc)

        try:
            self.db.set_service_state("device_list_source", "opc_fallback")
            self.db.set_service_state("silworx_api_connected", "0")
            self.db.set_service_state("silworx_mode", "opc_after_uninstall")
            self.db.set_service_state(
                "silworx_released_at",
                time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            pass

        try:
            self.alarms.raise_alarm(
                "G-11",
                "SILworX uninstalled/removed — continuing with OPC device list",
                cause="Released SILworX API/plugin/c3 locks; Report Solution continues running",
                severity="Warning",
                show_popup=False,
            )
        except Exception:
            pass

        try:
            self.refresh(manual=True)
        except Exception as exc:
            log.warning("OPC refresh after SILworX release failed: %s", exc)

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
        if self._stop.is_set() or self._stopped:
            return {}
        if manual:
            self.alarms.clear_shown_on_refresh()
        try:
            self._opc_servers = self.opc.discover_servers()
            if manual:
                self.opc.invalidate_cache()
            if not self._opc_servers:
                self.alarms.raise_alarm("P3", "No X-OPC server detected on host")
        except Exception as exc:
            self.alarms.raise_alarm("P3", "OPC discovery failed", cause=str(exc))

        if self._stop.is_set() or self._stopped:
            return {}

        active_types: list[str] = []
        device_source = ""
        # Unified path: SILworX API and X-OPC run together; merge into one list.
        active_types, device_source = sync_device_list_case1_via_api(
            self.config,
            self.db,
            self.structures,
            self._case1_sync,
            self.opc,
        )
        if self._stop.is_set() or self._stopped:
            return {}
        self.db.set_service_state("device_list_source", device_source)
        self.db.sync_schema_case1(self.structures, active_types or list(self.structures.keys()))

        if self._stop.is_set() or self._stopped:
            return {}
        self._case1_sync.commit()
        self._publish_silworx_state()
        self.db.set_service_state("deployment_case", "1")
        self.db.set_service_state("opc_servers", str(len(self._opc_servers)))
        self.db.set_service_state("opc_server_list", ";".join(self._opc_servers))
        self.db.set_service_state("active_devices", str(len(self.db.list_active_devices())))
        self.db.set_service_state("opc_devices", str(self.db.count_opc_devices()))
        result = {
            "opc_servers": len(self._opc_servers),
            "active_devices": len(self.db.list_active_devices()),
            "opc_devices": self.db.count_opc_devices(),
            "structures_loaded": len(self.structures),
            "device_list_source": device_source,
        }
        self._cached_device_counts = (int(result["active_devices"]), int(result["opc_devices"]))
        try:
            self._cached_service_state = self.db.get_service_state()
        except Exception:
            pass
        return result

    def _poll_loop(self, generation: int) -> None:
        while not self._stop.is_set() and generation == self._loop_generation:
            if self._starting:
                self._stop.wait(0.5)
                continue
            try:
                if self.monitor:
                    self.monitor.poll_devices()
                self.db.set_service_state("last_poll", time.strftime("%Y-%m-%d %H:%M:%S"))
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

    def _device_counts(self) -> Tuple[int, int]:
        try:
            return self.db.count_listed_devices(), self.db.count_opc_devices()
        except Exception:
            return 0, 0

    def health(self) -> Dict[str, object]:
        now = time.monotonic()
        if self._health_cache and now - self._health_cache_at <= self._health_cache_ttl_sec:
            return dict(self._health_cache)

        # Single-flight guard: avoid piling up slow OPC/DB work across request threads.
        if not self._health_lock.acquire(blocking=False):
            if self._health_cache:
                return dict(self._health_cache)
            return {
                "deployment_case": self.config.deployment_case,
                "device_list_source": "",
                "database": "sqlserver" if not self.db.using_sqlite else "sqlite",
                "opc_servers": [],
                "active_devices": 0,
                "opc_devices": 0,
                "queue_depth": 0,
                "silworx": {},
                "api_session": {"project_name": ""},
                "plugin_session": {"name": "", "registered": False},
                "silworx_api_instances": [],
                "service_state": {},
                "stopping": bool(getattr(self, "_stop_in_progress", False)),
                "starting": bool(self._starting),
                "engine_running": bool(self.engine_running),
                "web_host_alive": True,
                "web_auth_required": self.config.web_auth_enabled,
            }
        try:
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
                self._health_cache = dict(payload)
                self._health_cache_at = time.monotonic()
                return payload
            servers = []
            try:
                servers = self.opc.health_snapshot()
            except Exception:
                pass
            silworx = silworx_session_to_state(self._case1_sync.active_session)
            device_list_source = service_state.get("device_list_source", "")
            api_project = self._case1_sync.api_connected_project_name(device_list_source)
            plugin_name = self._case1_sync.registered_plugin_session_name()
            api_instances = [
                {"api_port": inst.api_port, "plugin_port": inst.plugin_port, "label": inst.label}
                for inst in self._case1_sync._available_instances
            ]
            payload = {
                "deployment_case": self.config.deployment_case,
                "device_list_source": device_list_source,
                "database": db_label,
                "opc_servers": [
                    {"name": s.prog_id, "connected": s.connected, "tags": s.tag_count} for s in servers
                ],
                "active_devices": all_count,
                "opc_devices": opc_count,
                "queue_depth": self.monitor.queue_depth if self.monitor else 0,
                "silworx": silworx,
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
            self._health_cache = dict(payload)
            self._health_cache_at = time.monotonic()
            return payload
        finally:
            self._health_lock.release()
